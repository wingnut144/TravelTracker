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


def get_coordinates_from_address(address, google_maps_api_key):
    """Get latitude and longitude from address using Google Maps API"""
    if not google_maps_api_key:
        logger.warning("Google Maps API key not configured")
        return None, None
    
    try:
        url = 'https://maps.googleapis.com/maps/api/geocode/json'
        params = {
            'address': address,
            'key': google_maps_api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data['status'] == 'OK' and data['results']:
            location = data['results'][0]['geometry']['location']
            return location['lat'], location['lng']
        
        return None, None
    
    except Exception as e:
        logger.error(f"Error geocoding address: {str(e)}")
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


def get_immich_photos_for_trip(trip, immich_api_url, immich_api_key):
    """Get photos from Immich for a trip based on dates and location"""
    if not immich_api_url or not immich_api_key:
        logger.warning("Immich API not configured")
        return []
    
    try:
        # Query Immich for photos in date range
        headers = {
            'x-api-key': immich_api_key,
            'Content-Type': 'application/json'
        }
        
        # Search by date range
        start_date = trip.start_date.isoformat()
        end_date = trip.end_date.isoformat()
        
        search_url = f"{immich_api_url}/search/metadata"
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
                    'thumbnail_url': f"{immich_api_url}/asset/thumbnail/{asset['id']}",
                    'full_url': f"{immich_api_url}/asset/file/{asset['id']}",
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
