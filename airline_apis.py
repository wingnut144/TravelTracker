"""
Airline API Integration Module
Interfaces with major US airline APIs for flight information
"""
import requests
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AirlineAPI:
    """Base class for airline API integration"""
    
    def __init__(self, api_key):
        """Initialize with API key"""
        self.api_key = api_key
    
    def get_flight_status(self, flight_number, date):
        """Get flight status - to be implemented by subclasses"""
        raise NotImplementedError
    
    def get_flight_details(self, confirmation_number):
        """Get flight details by confirmation - to be implemented by subclasses"""
        raise NotImplementedError


class UnitedAPI(AirlineAPI):
    """United Airlines API integration"""
    
    BASE_URL = "https://api.united.com/v1"
    
    def __init__(self, api_key):
        super().__init__(api_key)
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def get_flight_status(self, flight_number, date):
        """
        Get United flight status
        Note: This is a placeholder - actual API endpoints may differ
        """
        try:
            url = f"{self.BASE_URL}/flightstatus/{flight_number}/{date}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_flight_status(data)
            else:
                logger.error(f"United API error: {response.status_code}")
                return None
        
        except Exception as e:
            logger.error(f"Error fetching United flight status: {str(e)}")
            return None
    
    def get_flight_details(self, confirmation_number):
        """
        Get United booking details
        Note: This is a placeholder - actual API endpoints may differ
        """
        try:
            url = f"{self.BASE_URL}/booking/{confirmation_number}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_booking_details(data)
            else:
                logger.error(f"United API error: {response.status_code}")
                return None
        
        except Exception as e:
            logger.error(f"Error fetching United booking: {str(e)}")
            return None
    
    def _parse_flight_status(self, data):
        """Parse United flight status response"""
        return {
            'status': data.get('flightStatus', 'unknown'),
            'departure_gate': data.get('departureGate'),
            'arrival_gate': data.get('arrivalGate'),
            'departure_terminal': data.get('departureTerminal'),
            'scheduled_departure': data.get('scheduledDeparture'),
            'actual_departure': data.get('actualDeparture'),
            'scheduled_arrival': data.get('scheduledArrival'),
            'actual_arrival': data.get('actualArrival')
        }
    
    def _parse_booking_details(self, data):
        """Parse United booking details response"""
        return {
            'confirmation_number': data.get('confirmationNumber'),
            'passenger_name': data.get('passengerName'),
            'flights': data.get('flights', []),
            'seat_assignments': data.get('seatAssignments', [])
        }


class AmericanAPI(AirlineAPI):
    """American Airlines API integration"""
    
    BASE_URL = "https://api.aa.com/v1"
    
    def __init__(self, api_key):
        super().__init__(api_key)
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def get_flight_status(self, flight_number, date):
        """
        Get American Airlines flight status
        Note: This is a placeholder - actual API endpoints may differ
        """
        try:
            url = f"{self.BASE_URL}/flights/status/{flight_number}"
            params = {'date': date}
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_flight_status(data)
            else:
                logger.error(f"American API error: {response.status_code}")
                return None
        
        except Exception as e:
            logger.error(f"Error fetching American flight status: {str(e)}")
            return None
    
    def get_flight_details(self, confirmation_number):
        """
        Get American booking details
        Note: This is a placeholder - actual API endpoints may differ
        """
        try:
            url = f"{self.BASE_URL}/reservations/{confirmation_number}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_booking_details(data)
            else:
                logger.error(f"American API error: {response.status_code}")
                return None
        
        except Exception as e:
            logger.error(f"Error fetching American booking: {str(e)}")
            return None
    
    def _parse_flight_status(self, data):
        """Parse American flight status response"""
        flight = data.get('flight', {})
        return {
            'status': flight.get('status', 'unknown'),
            'departure_gate': flight.get('departureGate'),
            'arrival_gate': flight.get('arrivalGate'),
            'departure_terminal': flight.get('departureTerminal'),
            'scheduled_departure': flight.get('scheduledDepartureTime'),
            'actual_departure': flight.get('actualDepartureTime'),
            'scheduled_arrival': flight.get('scheduledArrivalTime'),
            'actual_arrival': flight.get('actualArrivalTime')
        }
    
    def _parse_booking_details(self, data):
        """Parse American booking details response"""
        return {
            'confirmation_number': data.get('recordLocator'),
            'passenger_name': data.get('travelers', [{}])[0].get('name'),
            'flights': data.get('segments', []),
            'seat_assignments': data.get('seats', [])
        }


class DeltaAPI(AirlineAPI):
    """Delta Airlines API integration"""
    
    BASE_URL = "https://api.delta.com/v1"
    
    def __init__(self, api_key):
        super().__init__(api_key)
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def get_flight_status(self, flight_number, date):
        """
        Get Delta flight status
        Note: This is a placeholder - actual API endpoints may differ
        """
        try:
            url = f"{self.BASE_URL}/flightstatus/{flight_number}/{date}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_flight_status(data)
            else:
                logger.error(f"Delta API error: {response.status_code}")
                return None
        
        except Exception as e:
            logger.error(f"Error fetching Delta flight status: {str(e)}")
            return None
    
    def get_flight_details(self, confirmation_number):
        """
        Get Delta booking details
        Note: This is a placeholder - actual API endpoints may differ
        """
        try:
            url = f"{self.BASE_URL}/trips/{confirmation_number}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_booking_details(data)
            else:
                logger.error(f"Delta API error: {response.status_code}")
                return None
        
        except Exception as e:
            logger.error(f"Error fetching Delta booking: {str(e)}")
            return None
    
    def _parse_flight_status(self, data):
        """Parse Delta flight status response"""
        return {
            'status': data.get('operationalStatus', 'unknown'),
            'departure_gate': data.get('departureGate'),
            'arrival_gate': data.get('arrivalGate'),
            'departure_terminal': data.get('departureTerminal'),
            'scheduled_departure': data.get('scheduledDepartureDateTime'),
            'actual_departure': data.get('estimatedDepartureDateTime'),
            'scheduled_arrival': data.get('scheduledArrivalDateTime'),
            'actual_arrival': data.get('estimatedArrivalDateTime')
        }
    
    def _parse_booking_details(self, data):
        """Parse Delta booking details response"""
        return {
            'confirmation_number': data.get('confirmationNumber'),
            'passenger_name': data.get('passenger', {}).get('name'),
            'flights': data.get('segments', []),
            'seat_assignments': data.get('seatAssignments', [])
        }


class SouthwestAPI(AirlineAPI):
    """Southwest Airlines API integration"""
    
    BASE_URL = "https://api.southwest.com/v1"
    
    def __init__(self, api_key):
        super().__init__(api_key)
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def get_flight_status(self, flight_number, date):
        """
        Get Southwest flight status
        Note: This is a placeholder - actual API endpoints may differ
        """
        try:
            url = f"{self.BASE_URL}/flightstatus"
            params = {
                'flightNumber': flight_number,
                'date': date
            }
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_flight_status(data)
            else:
                logger.error(f"Southwest API error: {response.status_code}")
                return None
        
        except Exception as e:
            logger.error(f"Error fetching Southwest flight status: {str(e)}")
            return None
    
    def get_flight_details(self, confirmation_number):
        """
        Get Southwest booking details
        Note: This is a placeholder - actual API endpoints may differ
        """
        try:
            url = f"{self.BASE_URL}/reservations/detail"
            params = {'confirmationNumber': confirmation_number}
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_booking_details(data)
            else:
                logger.error(f"Southwest API error: {response.status_code}")
                return None
        
        except Exception as e:
            logger.error(f"Error fetching Southwest booking: {str(e)}")
            return None
    
    def _parse_flight_status(self, data):
        """Parse Southwest flight status response"""
        flight_info = data.get('flightStatusResponse', {}).get('flight', {})
        return {
            'status': flight_info.get('status', 'unknown'),
            'departure_gate': flight_info.get('departureGate'),
            'arrival_gate': flight_info.get('arrivalGate'),
            'departure_terminal': flight_info.get('departureTerminal'),
            'scheduled_departure': flight_info.get('scheduledDepartureTime'),
            'actual_departure': flight_info.get('actualDepartureTime'),
            'scheduled_arrival': flight_info.get('scheduledArrivalTime'),
            'actual_arrival': flight_info.get('actualArrivalTime')
        }
    
    def _parse_booking_details(self, data):
        """Parse Southwest booking details response"""
        reservation = data.get('reservation', {})
        return {
            'confirmation_number': reservation.get('confirmationNumber'),
            'passenger_name': reservation.get('passengers', [{}])[0].get('name'),
            'flights': reservation.get('itinerary', {}).get('flights', []),
            'seat_assignments': []  # Southwest doesn't have assigned seats
        }


class AirlineAPIManager:
    """Manager for all airline APIs"""
    
    def __init__(self, app_config):
        """Initialize with app configuration"""
        self.apis = {}
        
        if app_config.get('UNITED_API_KEY'):
            self.apis['united'] = UnitedAPI(app_config['UNITED_API_KEY'])
        
        if app_config.get('AMERICAN_API_KEY'):
            self.apis['american'] = AmericanAPI(app_config['AMERICAN_API_KEY'])
        
        if app_config.get('DELTA_API_KEY'):
            self.apis['delta'] = DeltaAPI(app_config['DELTA_API_KEY'])
        
        if app_config.get('SOUTHWEST_API_KEY'):
            self.apis['southwest'] = SouthwestAPI(app_config['SOUTHWEST_API_KEY'])
    
    def get_api(self, airline):
        """Get API instance for airline"""
        airline_lower = airline.lower()
        return self.apis.get(airline_lower)
    
    def update_flight_status(self, flight):
        """Update flight status from airline API"""
        airline = flight.airline.lower()
        api = self.get_api(airline)
        
        if not api:
            logger.warning(f"No API configured for {airline}")
            return False
        
        try:
            # Format date for API
            date = flight.departure_time.strftime('%Y-%m-%d')
            
            # Get status
            status = api.get_flight_status(flight.flight_number, date)
            
            if status:
                # Update flight with new information
                flight.status = status.get('status', flight.status)
                flight.gate = status.get('departure_gate', flight.gate)
                flight.terminal = status.get('departure_terminal', flight.terminal)
                flight.last_api_update = datetime.utcnow()
                
                from models import db
                db.session.commit()
                
                logger.info(f"Updated flight {flight.id} status: {flight.status}")
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"Error updating flight status: {str(e)}")
            return False
    
    def get_booking_details(self, airline, confirmation_number):
        """Get booking details from airline API"""
        api = self.get_api(airline)
        
        if not api:
            logger.warning(f"No API configured for {airline}")
            return None
        
        try:
            return api.get_flight_details(confirmation_number)
        except Exception as e:
            logger.error(f"Error fetching booking details: {str(e)}")
            return None
