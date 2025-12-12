"""
Utility functions for Travel Tracking System
"""
import secrets
from datetime import datetime, timedelta
import pytz
from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user
import requests
import logging

logger = logging.getLogger(__name__)


def generate_share_token():
    """Generate a unique share token"""
    return secrets.token_urlsafe(32)


def format_datetime(dt, timezone='UTC'):
    """Format datetime with timezone"""
    if not dt:
        return ''
    
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    
    tz = pytz.timezone(timezone)
    local_dt = dt.astimezone(tz)
    
    return local_dt.strftime('%Y-%m-%d %I:%M %p %Z')


def format_date(dt):
    """Format date only"""
    if not dt:
        return ''
    return dt.strftime('%B %d, %Y')


def get_airport_name(code):
    """Get airport name from code"""
    # In production, this would query a database or API
    airport_names = {
        'JFK': 'John F. Kennedy International Airport',
        'LAX': 'Los Angeles International Airport',
        'ORD': "O'Hare International Airport",
        'DFW': 'Dallas/Fort Worth International Airport',
        'ATL': 'Hartsfield-Jackson Atlanta International Airport',
        'SFO': 'San Francisco International Airport',
        'MIA': 'Miami International Airport',
        'LAS': 'Harry Reid International Airport',
        'SEA': 'Seattle-Tacoma International Airport',
        'BOS': 'Boston Logan International Airport'
    }
    
    return airport_names.get(code, code)


def calculate_trip_duration(start_date, end_date):
    """Calculate trip duration in days"""
    if not start_date or not end_date:
        return 0
    
    delta = end_date - start_date
    return delta.days + 1


def get_trip_status(trip):
    """Get trip status string"""
    now = datetime.utcnow()
    
    if trip.end_date < now:
        return 'past'
    elif trip.start_date > now:
        return 'upcoming'
    else:
        return 'current'


def can_edit_trip(user, trip):
    """Check if user can edit trip"""
    if user.id == trip.user_id:
        return True
    
    if user.is_admin():
        return True
    
    # Check if shared with edit permissions
    from models import TripShare
    share = TripShare.query.filter_by(
        trip_id=trip.id,
        shared_with_user_id=user.id,
        can_edit=True
    ).first()
    
    return share is not None


def can_view_trip(user, trip):
    """Check if user can view trip"""
    from models import TripVisibility, TripShare
    
    # Owner can always view
    if user.id == trip.user_id:
        return True
    
    # Admin can always view
    if user.is_admin():
        return True
    
    # Public trips can be viewed by anyone
    if trip.visibility == TripVisibility.PUBLIC:
        return True
    
    # Check if shared
    if trip.visibility == TripVisibility.SHARED:
        share = TripShare.query.filter_by(
            trip_id=trip.id,
            shared_with_user_id=user.id
        ).first()
        return share is not None
    
    return False


def requires_trip_access(edit=False):
    """Decorator to check trip access"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            trip_id = kwargs.get('trip_id')
            
            if not trip_id:
                flash('Trip not found.', 'danger')
                return redirect(url_for('main.dashboard'))
            
            from models import Trip
            trip = Trip.query.get_or_404(trip_id)
            
            if edit:
                if not can_edit_trip(current_user, trip):
                    flash('You do not have permission to edit this trip.', 'danger')
                    return redirect(url_for('trips.view_trip', trip_id=trip_id))
            else:
                if not can_view_trip(current_user, trip):
                    flash('You do not have permission to view this trip.', 'danger')
                    return redirect(url_for('main.dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def get_coordinates_from_address(address, user_settings=None):
    """
    Get latitude and longitude from address using OpenStreetMap Nominatim (FREE)
    No API key required!
    
    Args:
        address: Address string to geocode
        user_settings: Not used (kept for compatibility)
    
    Returns:
        tuple: (latitude, longitude) or (None, None) if geocoding fails
    """
    import time
    
    try:
        url = 'https://nominatim.openstreetmap.org/search'
        params = {
            'q': address,
            'format': 'json',
            'limit': 1,
            'addressdetails': 1
        }
        headers = {
            'User-Agent': 'TravelTracker/1.0'  # Required by Nominatim usage policy
        }
        
        # Nominatim rate limit: 1 request per second
        time.sleep(1)
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data and len(data) > 0:
                result = data[0]
                lat = float(result['lat'])
                lng = float(result['lon'])
                logger.info(f"Successfully geocoded address: {address} -> ({lat}, {lng})")
                return lat, lng
        
        logger.warning(f"No results found for address: {address}")
        return None, None
    
    except Exception as e:
        logger.error(f"Error geocoding address with OpenStreetMap: {str(e)}")
        return None, None


def refresh_oauth_token(email_account):
    """Refresh OAuth token for email account using user's own credentials"""
    from app import app
    
    user_settings = email_account.user.user_settings
    
    try:
        if email_account.email_type == 'gmail':
            if not user_settings.has_google_oauth():
                logger.error(f"User {email_account.user_id} missing Google OAuth credentials")
                return False
            
            token_url = 'https://oauth2.googleapis.com/token'
            data = {
                'client_id': user_settings.google_client_id,
                'client_secret': user_settings.google_client_secret,
                'refresh_token': email_account.refresh_token,
                'grant_type': 'refresh_token'
            }
        
        elif email_account.email_type == 'outlook':
            if not user_settings.has_microsoft_oauth():
                logger.error(f"User {email_account.user_id} missing Microsoft OAuth credentials")
                return False
            
            token_url = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
            data = {
                'client_id': user_settings.microsoft_client_id,
                'client_secret': user_settings.microsoft_client_secret,
                'refresh_token': email_account.refresh_token,
                'grant_type': 'refresh_token'
            }
        
        else:
            return False
        
        response = requests.post(token_url, data=data, timeout=10)
        tokens = response.json()
        
        if 'access_token' in tokens:
            email_account.access_token = tokens['access_token']
            
            if 'refresh_token' in tokens:
                email_account.refresh_token = tokens['refresh_token']
            
            if 'expires_in' in tokens:
                email_account.token_expires_at = datetime.utcnow() + timedelta(
                    seconds=tokens['expires_in']
                )
            
            from models import db
            db.session.commit()
            logger.info(f"Refreshed OAuth token for email account {email_account.id}")
            return True
        
        logger.error(f"Failed to refresh token: {tokens.get('error', 'Unknown error')}")
        return False
    
    except Exception as e:
        logger.error(f"Error refreshing OAuth token: {str(e)}")
        return False


def get_immich_photos_for_trip(trip, user_settings):
    """Get photos from Immich for a trip based on dates and location using user's credentials"""
    if not user_settings or not user_settings.has_immich():
        logger.warning("User does not have Immich configured")
        return []
    
    try:
        # Query Immich for photos in date range
        headers = {
            'x-api-key': user_settings.immich_api_key,
            'Content-Type': 'application/json'
        }
        
        # Search by date range
        start_date = trip.start_date.isoformat()
        end_date = trip.end_date.isoformat()
        
        search_url = f"{user_settings.immich_api_url}/search/metadata"
        params = {
            'takenAfter': start_date,
            'takenBefore': end_date
        }
        
        response = requests.get(search_url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            assets = response.json().get('assets', [])
            
            photos = []
            for asset in assets:
                photos.append({
                    'id': asset['id'],
                    'thumbnail_url': f"{user_settings.immich_api_url}/asset/thumbnail/{asset['id']}",
                    'full_url': f"{user_settings.immich_api_url}/asset/file/{asset['id']}",
                    'taken_at': asset.get('fileCreatedAt'),
                    'latitude': asset.get('exifInfo', {}).get('latitude'),
                    'longitude': asset.get('exifInfo', {}).get('longitude')
                })
            
            return photos
        
        return []
    
    except Exception as e:
        logger.error(f"Error fetching Immich photos: {str(e)}")
        return []


def validate_email(email):
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def search_locations(query):
    """
    Search for locations worldwide using OpenStreetMap Photon
    Returns list of location suggestions for autocomplete
    
    Args:
        query: Search query string
    
    Returns:
        list: List of dicts with location data
    """
    try:
        # Use Photon for fast autocomplete-friendly search
        url = 'https://photon.komoot.io/api/'
        params = {
            'q': query,
            'limit': 10,
            'lang': 'en'
        }
        
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            locations = []
            
            for feature in data.get('features', []):
                props = feature.get('properties', {})
                coords = feature.get('geometry', {}).get('coordinates', [])
                
                # Build display name
                name_parts = []
                if props.get('name'):
                    name_parts.append(props['name'])
                if props.get('city'):
                    name_parts.append(props['city'])
                elif props.get('county'):
                    name_parts.append(props['county'])
                if props.get('state'):
                    name_parts.append(props['state'])
                if props.get('country'):
                    name_parts.append(props['country'])
                
                display_name = ', '.join(name_parts) if name_parts else 'Unknown Location'
                
                locations.append({
                    'display_name': display_name,
                    'name': props.get('name', ''),
                    'city': props.get('city', ''),
                    'state': props.get('state', ''),
                    'country': props.get('country', ''),
                    'latitude': coords[1] if len(coords) > 1 else None,
                    'longitude': coords[0] if len(coords) > 0 else None
                })
            
            return locations
        
        return []
    
    except Exception as e:
        logger.error(f"Error searching locations: {str(e)}")
        return []


def get_destination_background_image(destination):
    """
    Get a background image URL for a destination using Pexels
    Free service with curated travel images
    
    Args:
        destination: Destination name (e.g., "Paris, France")
    
    Returns:
        str: Image URL or fallback generic travel image
    """
    try:
        # Use Pexels API (free, 200 requests/hour)
        search_term = destination.replace(',', ' ').strip().lower()
        search_query = f"{search_term} landmark travel"
        
        # Pexels API endpoint
        url = "https://api.pexels.com/v1/search"
        params = {
            'query': search_query,
            'per_page': 1,
            'orientation': 'landscape'
        }
        headers = {
            # Public demo API key (limited to 200/hour)
            'Authorization': 'Bearer 563492ad6f91700001000001c5d4d7c5b9b54ac2a2b51b1e86f0964f'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('photos') and len(data['photos']) > 0:
                # Get the large size image
                return data['photos'][0]['src']['large2x']
        
        # Fallback: return a generic beautiful travel image
        return "https://images.pexels.com/photos/1285625/pexels-photo-1285625.jpeg?auto=compress&cs=tinysrgb&w=1600"
    
    except Exception as e:
        logger.error(f"Error fetching background image: {str(e)}")
        # Return generic travel image as fallback
        return "https://images.pexels.com/photos/1285625/pexels-photo-1285625.jpeg?auto=compress&cs=tinysrgb&w=1600"


def sanitize_filename(filename):
    """Sanitize filename for safe storage"""
    import re
    # Remove any non-alphanumeric characters except dots and dashes
    filename = re.sub(r'[^\w\s.-]', '', filename)
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    return filename


def get_file_extension(filename):
    """Get file extension"""
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return ''


def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed"""
    return '.' in filename and get_file_extension(filename) in allowed_extensions


def fetch_foursquare_checkins(access_token, start_date, end_date):
    """
    Fetch check-ins from Foursquare Swarm API
    
    Args:
        access_token: Foursquare OAuth access token
        start_date: Start datetime for check-ins
        end_date: End datetime for check-ins
    
    Returns:
        list: Check-in data
    """
    if not access_token:
        return []
    
    try:
        url = 'https://api.foursquare.com/v2/users/self/checkins'
        params = {
            'oauth_token': access_token,
            'v': '20231212',  # API version date
            'afterTimestamp': int(start_date.timestamp()),
            'beforeTimestamp': int(end_date.timestamp()),
            'limit': 250
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('response', {}).get('checkins', {}).get('items', [])
        else:
            logger.error(f"Foursquare API error: {response.status_code} - {response.text}")
        
        return []
    
    except Exception as e:
        logger.error(f"Error fetching Foursquare check-ins: {str(e)}")
        return []


def sync_trip_checkins(trip):
    """
    Sync check-ins for a specific trip from Foursquare
    
    Args:
        trip: Trip object
    
    Returns:
        int: Number of new check-ins added
    """
    from models import CheckIn, db
    
    user_settings = trip.user.user_settings
    
    if not user_settings or not user_settings.foursquare_enabled or not user_settings.foursquare_access_token:
        return 0
    
    checkins_data = fetch_foursquare_checkins(
        user_settings.foursquare_access_token,
        trip.start_date,
        trip.end_date
    )
    
    new_checkins = 0
    
    for checkin_data in checkins_data:
        foursquare_id = checkin_data.get('id')
        
        # Skip if already exists
        existing = CheckIn.query.filter_by(
            foursquare_checkin_id=foursquare_id
        ).first()
        
        if existing:
            continue
        
        venue = checkin_data.get('venue', {})
        location = venue.get('location', {})
        categories = venue.get('categories', [])
        photos = checkin_data.get('photos', {})
        
        # Get photo URL if available
        photo_url = None
        if photos.get('count', 0) > 0:
            items = photos.get('items', [])
            if items:
                photo = items[0]
                prefix = photo.get('prefix', '')
                suffix = photo.get('suffix', '')
                if prefix and suffix:
                    photo_url = f"{prefix}300x300{suffix}"
        
        checkin = CheckIn(
            trip_id=trip.id,
            user_id=trip.user_id,
            foursquare_checkin_id=foursquare_id,
            venue_name=venue.get('name'),
            venue_category=categories[0].get('name') if categories else None,
            venue_address=location.get('address', ''),
            latitude=location.get('lat'),
            longitude=location.get('lng'),
            checkin_time=datetime.fromtimestamp(checkin_data.get('createdAt')),
            shout=checkin_data.get('shout'),
            photo_url=photo_url
        )
        
        db.session.add(checkin)
        new_checkins += 1
    
    if new_checkins > 0:
        db.session.commit()
        logger.info(f"Added {new_checkins} check-ins to trip {trip.id}")
    
    return new_checkins

