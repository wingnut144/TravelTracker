"""
Email Scanner Service - Automatically scans emails for flight confirmations
"""
import re
import base64
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
import requests
from bs4 import BeautifulSoup
from models import db, EmailAccount, Trip, Flight, EmailScanLog, TripVisibility
import logging

logger = logging.getLogger(__name__)

class EmailScanner:
    """Base email scanner class"""
    
    # Airline email patterns
    AIRLINE_PATTERNS = {
        'united': [
            r'united\.com',
            r'confirmation.*united',
            r'flight.*confirmation'
        ],
        'american': [
            r'aa\.com',
            r'americanairlines\.com',
            r'confirmation.*american airlines'
        ],
        'delta': [
            r'delta\.com',
            r'confirmation.*delta',
            r'flight.*confirmation.*delta'
        ],
        'southwest': [
            r'southwest\.com',
            r'confirmation.*southwest',
            r'flight.*confirmation.*southwest'
        ]
    }
    
    # Flight number pattern
    FLIGHT_NUMBER_PATTERN = r'\b([A-Z]{2})\s*(\d{1,4})\b'
    
    # Confirmation number pattern
    CONFIRMATION_PATTERN = r'\b([A-Z0-9]{6})\b'
    
    # Airport code pattern
    AIRPORT_PATTERN = r'\b([A-Z]{3})\b'
    
    def __init__(self, email_account):
        """Initialize scanner with email account"""
        self.email_account = email_account
    
    def scan_for_flights(self):
        """Main scanning method - to be implemented by subclasses"""
        raise NotImplementedError
    
    def parse_flight_email(self, email_content, subject, from_email):
        """Parse email content to extract flight information"""
        try:
            # Clean HTML if present
            if '<html' in email_content.lower():
                soup = BeautifulSoup(email_content, 'html.parser')
                text_content = soup.get_text()
            else:
                text_content = email_content
            
            # Detect airline
            airline = self._detect_airline(from_email, subject, text_content)
            if not airline:
                return None
            
            # Extract flight information
            flight_info = self._extract_flight_info(text_content, airline)
            
            return flight_info
        
        except Exception as e:
            logger.error(f"Error parsing flight email: {str(e)}")
            return None
    
    def _detect_airline(self, from_email, subject, content):
        """Detect which airline sent the email"""
        text_to_search = f"{from_email} {subject} {content}".lower()
        
        for airline, patterns in self.AIRLINE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_to_search, re.IGNORECASE):
                    return airline
        
        return None
    
    def _extract_flight_info(self, content, airline):
        """Extract flight details from email content"""
        info = {
            'airline': airline.upper(),
            'flight_number': None,
            'confirmation_number': None,
            'departure_airport': None,
            'arrival_airport': None,
            'departure_time': None,
            'arrival_time': None
        }
        
        # Extract flight number
        flight_match = re.search(self.FLIGHT_NUMBER_PATTERN, content)
        if flight_match:
            info['flight_number'] = f"{flight_match.group(1)}{flight_match.group(2)}"
        
        # Extract confirmation number
        conf_matches = re.findall(self.CONFIRMATION_PATTERN, content)
        if conf_matches:
            # Usually the first one is the confirmation
            info['confirmation_number'] = conf_matches[0]
        
        # Extract airport codes
        airport_matches = re.findall(self.AIRPORT_PATTERN, content)
        if len(airport_matches) >= 2:
            # Filter out common false positives
            valid_airports = [code for code in airport_matches if code not in ['THE', 'AND', 'FOR', 'NOT', 'ARE']]
            if len(valid_airports) >= 2:
                info['departure_airport'] = valid_airports[0]
                info['arrival_airport'] = valid_airports[1]
        
        # Extract dates/times (simplified - would need more sophisticated parsing)
        info['departure_time'] = self._extract_datetime(content, 'departure')
        info['arrival_time'] = self._extract_datetime(content, 'arrival')
        
        # Validate we have minimum required info
        if info['flight_number'] and info['departure_airport'] and info['arrival_airport']:
            return info
        
        return None
    
    def _extract_datetime(self, content, flight_type):
        """Extract date/time from email content"""
        # This is a simplified version - in production, use more sophisticated parsing
        # Look for common date patterns
        date_patterns = [
            r'(\d{1,2})/(\d{1,2})/(\d{4})\s+(\d{1,2}):(\d{2})\s*(AM|PM)?',
            r'(\d{4})-(\d{2})-(\d{2})\s+(\d{2}):(\d{2})',
            r'([A-Za-z]+)\s+(\d{1,2}),\s+(\d{4})\s+(\d{1,2}):(\d{2})\s*(AM|PM)?'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, content)
            if match:
                try:
                    # This is simplified - would need proper date parsing
                    return datetime.now() + timedelta(days=30)  # Placeholder
                except:
                    pass
        
        return None
    
    def create_trip_from_flight(self, flight_info, email_id):
        """Create a trip and flight from parsed information"""
        try:
            user = self.email_account.user
            
            # Check if trip already exists
            existing_flight = Flight.query.filter_by(
                confirmation_number=flight_info['confirmation_number']
            ).first()
            
            if existing_flight:
                logger.info(f"Flight already exists: {flight_info['confirmation_number']}")
                return None
            
            # Create trip
            trip = Trip(
                user_id=user.id,
                title=f"{flight_info['departure_airport']} to {flight_info['arrival_airport']}",
                destination=flight_info['arrival_airport'],
                start_date=flight_info['departure_time'] or datetime.now(),
                end_date=flight_info['arrival_time'] or datetime.now() + timedelta(days=1),
                visibility=TripVisibility.PRIVATE,  # Default to private
                confirmation_number=flight_info['confirmation_number'],
                auto_detected=True,
                email_source=email_id
            )
            
            db.session.add(trip)
            db.session.flush()  # Get trip ID
            
            # Create flight
            flight = Flight(
                trip_id=trip.id,
                airline=flight_info['airline'],
                flight_number=flight_info['flight_number'],
                confirmation_number=flight_info['confirmation_number'],
                departure_airport=flight_info['departure_airport'],
                arrival_airport=flight_info['arrival_airport'],
                departure_time=flight_info['departure_time'] or datetime.now(),
                arrival_time=flight_info['arrival_time'] or datetime.now() + timedelta(hours=2),
                status='scheduled'
            )
            
            db.session.add(flight)
            db.session.commit()
            
            logger.info(f"Created trip {trip.id} from email")
            return trip
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating trip from flight: {str(e)}")
            return None


class GmailScanner(EmailScanner):
    """Gmail-specific scanner using Gmail API"""
    
    def __init__(self, email_account):
        super().__init__(email_account)
        self.access_token = email_account.access_token
    
    def scan_for_flights(self):
        """Scan Gmail for flight confirmations"""
        try:
            # Build query for airline emails
            query = 'subject:(flight confirmation OR itinerary OR booking confirmation) from:(united.com OR aa.com OR delta.com OR southwest.com)'
            
            # Get messages
            headers = {'Authorization': f'Bearer {self.access_token}'}
            list_url = f'https://gmail.googleapis.com/gmail/v1/users/me/messages?q={query}&maxResults=20'
            
            response = requests.get(list_url, headers=headers)
            
            if response.status_code == 401:
                # Token expired - need refresh
                logger.warning("Gmail token expired")
                return 0
            
            messages = response.json().get('messages', [])
            
            trips_created = 0
            emails_processed = 0
            
            for message in messages:
                msg_id = message['id']
                
                # Get full message
                msg_url = f'https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}'
                msg_response = requests.get(msg_url, headers=headers)
                msg_data = msg_response.json()
                
                # Extract email details
                subject = ''
                from_email = ''
                body = ''
                
                for header in msg_data.get('payload', {}).get('headers', []):
                    if header['name'] == 'Subject':
                        subject = header['value']
                    elif header['name'] == 'From':
                        from_email = header['value']
                
                # Get body
                parts = msg_data.get('payload', {}).get('parts', [])
                if parts:
                    for part in parts:
                        if part.get('mimeType') == 'text/plain':
                            body_data = part.get('body', {}).get('data', '')
                            body = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')
                            break
                
                if not body:
                    # Try to get body from payload directly
                    body_data = msg_data.get('payload', {}).get('body', {}).get('data', '')
                    if body_data:
                        body = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')
                
                # Parse email
                flight_info = self.parse_flight_email(body, subject, from_email)
                
                if flight_info:
                    trip = self.create_trip_from_flight(flight_info, msg_id)
                    if trip:
                        trips_created += 1
                
                emails_processed += 1
            
            # Update last scan
            self.email_account.last_scan = datetime.utcnow()
            db.session.commit()
            
            return trips_created
        
        except Exception as e:
            logger.error(f"Error scanning Gmail: {str(e)}")
            return 0


class OutlookScanner(EmailScanner):
    """Outlook-specific scanner using Microsoft Graph API"""
    
    def __init__(self, email_account):
        super().__init__(email_account)
        self.access_token = email_account.access_token
    
    def scan_for_flights(self):
        """Scan Outlook for flight confirmations"""
        try:
            # Build query
            query = 'subject:flight OR subject:confirmation OR subject:itinerary'
            
            # Get messages
            headers = {'Authorization': f'Bearer {self.access_token}'}
            list_url = f'https://graph.microsoft.com/v1.0/me/messages?$filter=contains(subject, \'flight\') or contains(subject, \'confirmation\')&$top=20'
            
            response = requests.get(list_url, headers=headers)
            
            if response.status_code == 401:
                # Token expired - need refresh
                logger.warning("Outlook token expired")
                return 0
            
            messages = response.json().get('value', [])
            
            trips_created = 0
            emails_processed = 0
            
            for message in messages:
                msg_id = message['id']
                subject = message.get('subject', '')
                from_email = message.get('from', {}).get('emailAddress', {}).get('address', '')
                body = message.get('body', {}).get('content', '')
                
                # Parse email
                flight_info = self.parse_flight_email(body, subject, from_email)
                
                if flight_info:
                    trip = self.create_trip_from_flight(flight_info, msg_id)
                    if trip:
                        trips_created += 1
                
                emails_processed += 1
            
            # Update last scan
            self.email_account.last_scan = datetime.utcnow()
            db.session.commit()
            
            return trips_created
        
        except Exception as e:
            logger.error(f"Error scanning Outlook: {str(e)}")
            return 0


def scan_all_email_accounts():
    """Scan all active email accounts"""
    from app import app
    
    with app.app_context():
        email_accounts = EmailAccount.query.filter_by(is_active=True).all()
        
        total_trips = 0
        
        for account in email_accounts:
            # Check if user has email integration enabled
            if not account.user.user_settings.email_integration_enabled:
                continue
            
            if not account.user.user_settings.auto_scan_emails:
                continue
            
            logger.info(f"Scanning email account: {account.email_address}")
            
            try:
                if account.email_type == 'gmail':
                    scanner = GmailScanner(account)
                elif account.email_type == 'outlook':
                    scanner = OutlookScanner(account)
                else:
                    continue
                
                trips_created = scanner.scan_for_flights()
                total_trips += trips_created
                
                # Log scan
                scan_log = EmailScanLog(
                    email_account_id=account.id,
                    trips_created=trips_created,
                    emails_processed=20  # Simplified
                )
                db.session.add(scan_log)
                db.session.commit()
                
            except Exception as e:
                logger.error(f"Error scanning account {account.id}: {str(e)}")
                
                scan_log = EmailScanLog(
                    email_account_id=account.id,
                    errors=str(e)
                )
                db.session.add(scan_log)
                db.session.commit()
        
        logger.info(f"Email scan complete. Created {total_trips} trips.")
        return total_trips
