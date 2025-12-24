"""
Main Flask Application for Travel Tracking System
"""
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
from flask_migrate import Migrate
from datetime import datetime, timedelta
import os
import requests
import logging
from logging.handlers import RotatingFileHandler

# Import modules
from config import config
from models import db, User, Trip, Flight, Accommodation, TripShare, TripPhoto, UserSettings, TripVisibility, UserRole
from auth import init_auth, admin_required
from admin import init_admin
from utils import (
    generate_share_token, format_datetime, get_trip_status, can_view_trip, 
    can_edit_trip, requires_trip_access, get_immich_photos_for_trip,
    get_coordinates_from_address
)

# Add this near the top of app.py (after imports)
from functools import lru_cache
import requests
from models import User, Trip, Flight, Accommodation, UserSettings, EmailAccount, TripShare, TripPhoto, CheckIn, APIStatus, FriendRequest

@lru_cache(maxsize=500)  # Cache up to 500 airports
def get_airport_info(iata_code):
    """Fetch airport info from AirLabs API with caching"""
    if not iata_code or len(iata_code) != 3:
        return {'city': iata_code, 'name': iata_code}
    
    try:
        airlabs_api_key = os.getenv('AIRLABS_API_KEY')
        if not airlabs_api_key:
            return {'city': iata_code, 'name': iata_code}
        
        url = 'https://airlabs.co/api/v9/airports'
        params = {
            'api_key': airlabs_api_key,
            'iata_code': iata_code
        }
        
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('response') and len(data['response']) > 0:
                airport = data['response'][0]
                return {
                    'city': airport.get('city', iata_code),
                    'name': airport.get('name', iata_code),
                    'country': airport.get('country_code', '')
                }
    except Exception as e:
        logger.error(f"Error fetching airport info for {iata_code}: {str(e)}")
    
    return {'city': iata_code, 'name': iata_code}

def get_airline_name(iata_code):
    """Convert airline IATA code to full name"""
    airlines = {
        'AA': 'American Airlines',
        'DL': 'Delta Air Lines',
        'UA': 'United Airlines',
        'WN': 'Southwest Airlines',
        'B6': 'JetBlue Airways',
        'AS': 'Alaska Airlines',
        'F9': 'Frontier Airlines',
        'NK': 'Spirit Airlines',
        'G4': 'Allegiant Air',
        'SY': 'Sun Country Airlines',
        'HA': 'Hawaiian Airlines',
        'AC': 'Air Canada',
        'BA': 'British Airways',
        'LH': 'Lufthansa',
        'AF': 'Air France',
        'KL': 'KLM',
        'EK': 'Emirates',
        'QR': 'Qatar Airways',
        'SQ': 'Singapore Airlines',
        'CX': 'Cathay Pacific',
        'QF': 'Qantas',
        'NZ': 'Air New Zealand',
    }
    return airlines.get(iata_code, iata_code)
# Create Flask app
app = Flask(__name__)

# Load configuration
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)

# Initialize auth and admin
init_auth(app)
init_admin(app)

# Setup logging
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = RotatingFileHandler(
        'logs/traveltracker.log',
        maxBytes=10240000,
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    
    app.logger.setLevel(logging.INFO)
    app.logger.info('Travel Tracker startup')

# Template filters
@app.template_filter('datetime')
def datetime_filter(dt, timezone='UTC'):
    """Format datetime"""
    return format_datetime(dt, timezone)

@app.template_filter('trip_status')
def trip_status_filter(trip):
    """Get trip status"""
    return get_trip_status(trip)


# Main routes
@app.route('/')
def index():
    """Landing page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    now = datetime.utcnow()
    
    # Get upcoming trips
    upcoming_trips = Trip.query.filter(
        Trip.user_id == current_user.id,
        Trip.start_date > now
    ).order_by(Trip.start_date).limit(5).all()
    
    # Get current trips
    current_trips = Trip.query.filter(
        Trip.user_id == current_user.id,
        Trip.start_date <= now,
        Trip.end_date >= now
    ).all()
    
    # Get recent trips
    past_trips = Trip.query.filter(
        Trip.user_id == current_user.id,
        Trip.end_date < now
    ).order_by(Trip.end_date.desc()).limit(5).all()
    
    # Get shared trips
    shared_trips = []
    for share in current_user.shared_trips_received:
        if can_view_trip(current_user, share.trip):
            shared_trips.append(share.trip)
    
    return render_template(
        'dashboard.html',
        upcoming_trips=upcoming_trips,
        current_trips=current_trips,
        past_trips=past_trips,
        shared_trips=shared_trips,
        now=datetime.now()
    )


@app.route('/trips')
@login_required
def trips():
    """List all user trips"""
    page = request.args.get('page', 1, type=int)
    filter_type = request.args.get('filter', 'all')
    
    query = Trip.query.filter_by(user_id=current_user.id)
    
    now = datetime.utcnow()
    
    if filter_type == 'upcoming':
        query = query.filter(Trip.start_date > now)
    elif filter_type == 'past':
        query = query.filter(Trip.end_date < now)
    elif filter_type == 'current':
        query = query.filter(Trip.start_date <= now, Trip.end_date >= now)
    
    trips = query.order_by(Trip.start_date).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('trips/list.html', trips=trips, filter_type=filter_type)


@app.route('/trips/<int:trip_id>')
@login_required
@requires_trip_access()
def view_trip(trip_id):
    """View trip details"""
    trip = Trip.query.get_or_404(trip_id)
    
    # Get photos if Immich is enabled and configured
    photos = []
    if current_user.user_settings.immich_integration_enabled and current_user.user_settings.has_immich():
        photos = get_immich_photos_for_trip(trip, current_user.user_settings)
    
    return render_template(
        'trips/view.html',
        trip=trip,
        photos=photos,
        can_edit=can_edit_trip(current_user, trip)
    )


@app.route('/trips/new', methods=['GET', 'POST'])
@login_required
def new_trip():
    """Create new trip"""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        destination = request.form.get('destination')
        destination_lat = request.form.get('destination_latitude')
        destination_lng = request.form.get('destination_longitude')
        start_date = datetime.fromisoformat(request.form.get('start_date'))
        end_date = datetime.fromisoformat(request.form.get('end_date'))
        visibility = request.form.get('visibility', 'private')
        
        # Validation
        if not title or not start_date or not end_date:
            flash('Title, start date, and end date are required.', 'danger')
            return render_template('trips/new.html')
        
        if start_date > end_date:
            flash('Start date must be before end date.', 'danger')
            return render_template('trips/new.html')
        
        # Get background image for destination
        background_url = None
        if destination:
            from utils import get_destination_background_image
            background_url = get_destination_background_image(destination)
        
        # Create trip
        trip = Trip(
            user_id=current_user.id,
            title=title,
            description=description,
            destination=destination,
            destination_latitude=float(destination_lat) if destination_lat else None,
            destination_longitude=float(destination_lng) if destination_lng else None,
            background_image_url=background_url,
            start_date=start_date,
            end_date=end_date,
            visibility=TripVisibility[visibility.upper()]
        )
        
        db.session.add(trip)
        db.session.commit()
        
        flash('Trip created successfully!', 'success')
        return redirect(url_for('view_trip', trip_id=trip.id))
    
    return render_template('trips/new.html')


@app.route('/trips/<int:trip_id>/edit', methods=['GET', 'POST'])
@login_required
@requires_trip_access(edit=True)
def edit_trip(trip_id):
    """Edit trip"""
    trip = Trip.query.get_or_404(trip_id)
    
    if request.method == 'POST':
        old_destination = trip.destination
        
        trip.title = request.form.get('title', trip.title)
        trip.description = request.form.get('description', trip.description)
        trip.destination = request.form.get('destination', trip.destination)
        
        # Update coordinates if provided
        dest_lat = request.form.get('destination_latitude')
        dest_lng = request.form.get('destination_longitude')
        if dest_lat and dest_lng:
            trip.destination_latitude = float(dest_lat)
            trip.destination_longitude = float(dest_lng)
        
        trip.start_date = datetime.fromisoformat(request.form.get('start_date'))
        trip.end_date = datetime.fromisoformat(request.form.get('end_date'))
        trip.visibility = TripVisibility[request.form.get('visibility', 'private').upper()]
        trip.notes = request.form.get('notes', trip.notes)
        
        # Update background image if destination changed
        if trip.destination and trip.destination != old_destination:
            from utils import get_destination_background_image
            background_url = get_destination_background_image(trip.destination)
            if background_url:
                trip.background_image_url = background_url
        
        db.session.commit()
        
        flash('Trip updated successfully!', 'success')
        return redirect(url_for('view_trip', trip_id=trip.id))
    
    return render_template('trips/edit.html', trip=trip)


@app.route('/trips/<int:trip_id>/delete', methods=['POST'])
@login_required
@requires_trip_access(edit=True)
def delete_trip(trip_id):
    """Delete trip"""
    trip = Trip.query.get_or_404(trip_id)
    
    db.session.delete(trip)
    db.session.commit()
    
    flash('Trip deleted successfully.', 'success')
    return redirect(url_for('trips'))


@app.route('/trips/<int:trip_id>/flights/add', methods=['GET', 'POST'])
@login_required
@requires_trip_access(edit=True)
def add_flight(trip_id):
    """Add flight to trip"""
    trip = Trip.query.get_or_404(trip_id)
    
    if request.method == 'POST':
        flight = Flight(
            trip_id=trip.id,
            airline=request.form.get('airline'),
            flight_number=request.form.get('flight_number'),
            confirmation_number=request.form.get('confirmation_number'),
            departure_airport=request.form.get('departure_airport'),
            arrival_airport=request.form.get('arrival_airport'),
            departure_time=datetime.fromisoformat(request.form.get('departure_time')),
            arrival_time=datetime.fromisoformat(request.form.get('arrival_time')),
            seat_number=request.form.get('seat_number'),
            status='scheduled'
        )
        
        db.session.add(flight)
        db.session.commit()
        
        flash('Flight added successfully!', 'success')
        return redirect(url_for('view_trip', trip_id=trip.id))
    
    return render_template('trips/add_flight.html', trip=trip)


@app.route('/trips/<int:trip_id>/accommodation/add', methods=['GET', 'POST'])
@login_required
@requires_trip_access(edit=True)
def add_accommodation(trip_id):
    """Add accommodation to trip"""
    trip = Trip.query.get_or_404(trip_id)
    
    if request.method == 'POST':
        address = request.form.get('address')
        
        # Get coordinates using OpenStreetMap (free, no API key needed)
        lat, lng = None, None
        if address:
            lat, lng = get_coordinates_from_address(address)
        
        accommodation = Accommodation(
            trip_id=trip.id,
            name=request.form.get('name'),
            address=address,
            check_in=datetime.fromisoformat(request.form.get('check_in')),
            check_out=datetime.fromisoformat(request.form.get('check_out')),
            confirmation_number=request.form.get('confirmation_number'),
            phone=request.form.get('phone'),
            latitude=lat,
            longitude=lng,
            notes=request.form.get('notes')
        )
        
        db.session.add(accommodation)
        db.session.commit()
        
        flash('Accommodation added successfully!', 'success')
        return redirect(url_for('view_trip', trip_id=trip.id))
    
    return render_template('trips/add_accommodation.html', trip=trip)


@app.route('/trips/<int:trip_id>/share', methods=['GET', 'POST'])
@login_required
def share_trip(trip_id):
    """Share trip with friends or via external link"""
    trip = Trip.query.get_or_404(trip_id)
    
    if request.method == 'POST':
        share_type = request.form.get('share_type')
        
        if share_type == 'friends':
            # Handle friend sharing with checkboxes
            selected_friends = request.form.getlist('friends[]')
            can_edit_friends = request.form.getlist('can_edit[]')
            
            # Remove all existing friend shares
            TripShare.query.filter_by(trip_id=trip.id).filter(
                TripShare.shared_with_user_id.isnot(None)
            ).delete()
            
            # Create new friend shares
            for friend_id in selected_friends:
                friend_id = int(friend_id)
                can_edit = str(friend_id) in can_edit_friends
                
                share = TripShare(
                    trip_id=trip.id,
                    shared_with_user_id=friend_id,
                    can_edit=can_edit
                )
                db.session.add(share)
            
            db.session.commit()
            
            if selected_friends:
                flash(f'Trip shared with {len(selected_friends)} friend(s)!', 'success')
            else:
                flash('All friend shares removed.', 'info')
            
            return redirect(url_for('share_trip', trip_id=trip.id))
        
        elif share_type == 'external':
            # Handle external link sharing
            external_email = request.form.get('external_email')
            expires_days = request.form.get('expires_days')
            can_edit = request.form.get('can_edit') == 'on'
            
            # Generate share token
            import secrets
            token = secrets.token_urlsafe(32)
            
            # Calculate expiration
            expires_at = None
            if expires_days:
                expires_at = datetime.utcnow() + timedelta(days=int(expires_days))
            
            share = TripShare(
                trip_id=trip.id,
                external_email=external_email if external_email else None,
                share_token=token,
                can_edit=can_edit,
                expires_at=expires_at
            )
            
            db.session.add(share)
            db.session.commit()
            
            flash('Share link created successfully!', 'success')
            return redirect(url_for('share_trip', trip_id=trip.id))
    
    # GET request - show the share form
    friends = current_user.get_friends()
    
    # Get currently shared friend IDs and their edit permissions
    shared_friend_ids = {share.shared_with_user_id: share.can_edit 
                         for share in trip.shares 
                         if share.shared_with_user_id is not None}
    
    # Get external shares (ones with share_token)
    shares = [share for share in trip.shares if share.share_token is not None]
    
    return render_template('trips/share.html',
                         trip=trip,
                         friends=friends,
                         shared_friend_ids=shared_friend_ids,
                         shares=shares)

@app.route('/shared/<token>')
def view_shared_trip(token):
    """View trip via external share link"""
    share = TripShare.query.filter_by(share_token=token).first_or_404()
    
    # Check expiration
    if share.expires_at and share.expires_at < datetime.utcnow():
        return render_template('errors/expired_share.html'), 410
    
    trip = share.trip
    
    return render_template('trips/view_shared.html', trip=trip, share=share)


@app.route('/settings/api-integrations', methods=['GET', 'POST'])
@login_required
def api_integrations():
    """Configure API integrations"""
    settings = current_user.user_settings
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'save_immich':
            settings.immich_api_url = request.form.get('immich_api_url', '').strip().rstrip('/')
            settings.immich_api_key = request.form.get('immich_api_key', '').strip()
            db.session.commit()
            flash('Immich API credentials saved!', 'success')
        
        elif action == 'save_google_maps':
            settings.google_maps_api_key = request.form.get('google_maps_api_key', '').strip()
            db.session.commit()
            flash('Google Maps API key saved!', 'success')
        
        elif action == 'delete_immich':
            settings.immich_api_url = None
            settings.immich_api_key = None
            db.session.commit()
            flash('Immich API credentials removed.', 'info')
        
        elif action == 'delete_google_maps':
            settings.google_maps_api_key = None
            db.session.commit()
            flash('Google Maps API key removed.', 'info')
        
        return redirect(url_for('api_integrations'))
    
    return render_template('settings/api_integrations.html', settings=settings)


@app.route('/api/search/locations', methods=['GET'])
@login_required
def search_locations_api():
    """Search for locations worldwide for autocomplete"""
    query = request.args.get('q', '')
    
    if not query or len(query) < 2:
        return jsonify({'locations': []})
    
    from utils import search_locations
    locations = search_locations(query)
    
    return jsonify({'locations': locations})


@app.route('/api/test/immich', methods=['POST'])
@login_required
def test_immich():
    """Test Immich API connection"""
    settings = current_user.user_settings
    
    # Use temporary values if provided, otherwise use saved
    api_url = request.form.get('immich_api_url', settings.immich_api_url)
    api_key = request.form.get('immich_api_key', settings.immich_api_key)
    
    if not api_url or not api_key:
        return jsonify({'success': False, 'message': 'API URL and Key are required'})
    
    try:
        # Test connection to Immich server
        headers = {'x-api-key': api_key}
        response = requests.get(f"{api_url}/server-info/ping", headers=headers, timeout=5)
        
        if response.status_code == 200:
            # Try to get server version
            version_response = requests.get(f"{api_url}/server-info/version", headers=headers, timeout=5)
            if version_response.status_code == 200:
                version_data = version_response.json()
                return jsonify({
                    'success': True, 
                    'message': f'Connected to Immich server successfully! Version: {version_data.get("major", "")}.{version_data.get("minor", "")}.{version_data.get("patch", "")}'
                })
            else:
                return jsonify({'success': True, 'message': 'Connected to Immich server successfully!'})
        else:
            return jsonify({'success': False, 'message': f'Connection failed: {response.status_code}'})
    
    except requests.exceptions.Timeout:
        return jsonify({'success': False, 'message': 'Connection timeout - check if server is accessible'})
    except requests.exceptions.ConnectionError:
        return jsonify({'success': False, 'message': 'Connection error - check URL and network'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})


@app.route('/settings/oauth-apps', methods=['GET', 'POST'])
@login_required
def oauth_apps():
    """Configure OAuth applications"""
    settings = current_user.user_settings
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'save_google':
            settings.google_client_id = request.form.get('google_client_id', '').strip()
            settings.google_client_secret = request.form.get('google_client_secret', '').strip()
            db.session.commit()
            flash('Google OAuth app credentials saved!', 'success')
        
        elif action == 'save_microsoft':
            settings.microsoft_client_id = request.form.get('microsoft_client_id', '').strip()
            settings.microsoft_client_secret = request.form.get('microsoft_client_secret', '').strip()
            db.session.commit()
            flash('Microsoft OAuth app credentials saved!', 'success')
        
        elif action == 'delete_google':
            settings.google_client_id = None
            settings.google_client_secret = None
            db.session.commit()
            flash('Google OAuth app credentials removed.', 'info')
        
        elif action == 'delete_microsoft':
            settings.microsoft_client_id = None
            settings.microsoft_client_secret = None
            db.session.commit()
            flash('Microsoft OAuth app credentials removed.', 'info')
        
        return redirect(url_for('oauth_apps'))
    
    return render_template('settings/oauth_apps.html', settings=settings)


@app.route('/settings/email-accounts')
@login_required
def email_accounts():
    """Manage email accounts"""
    accounts = EmailAccount.query.filter_by(user_id=current_user.id).all()
    return render_template('settings/email_accounts.html', accounts=accounts)


@app.route('/settings/email-accounts/<int:account_id>/disconnect', methods=['POST'])
@login_required
def disconnect_email_account(account_id):
    """Disconnect an email account"""
    account = EmailAccount.query.get_or_404(account_id)
    
    if account.user_id != current_user.id:
        flash('Permission denied.', 'danger')
        return redirect(url_for('email_accounts'))
    
    email_address = account.email_address
    db.session.delete(account)
    db.session.commit()
    
    flash(f'Email account {email_address} disconnected.', 'success')
    return redirect(url_for('email_accounts'))


@app.route('/settings')
@login_required
def settings():
    """User settings page"""
    from datetime import datetime
    return render_template('settings/index.html', now=datetime.utcnow)


@app.route('/settings/profile', methods=['GET', 'POST'])
@login_required
def profile_settings():
    """Update user profile"""
    if request.method == 'POST':
        # Update basic info
        current_user.first_name = request.form.get('first_name', '').strip() or None
        current_user.last_name = request.form.get('last_name', '').strip() or None
        current_user.username = request.form.get('username', current_user.username)
        current_user.email = request.form.get('email', current_user.email)
        
        # Change password if provided
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password:
            current_password = request.form.get('current_password')
            
            if not current_password:
                flash('Please enter your current password to change it.', 'danger')
                return render_template('settings/profile.html')
            
            if not current_user.check_password(current_password):
                flash('Current password is incorrect.', 'danger')
                return render_template('settings/profile.html')
            
            if new_password != confirm_password:
                flash('New passwords do not match.', 'danger')
                return render_template('settings/profile.html')
            
            current_user.set_password(new_password)
            flash('Password updated successfully.', 'success')
        
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('settings'))
    
    return render_template('settings/profile.html')


@app.route('/settings/preferences', methods=['GET', 'POST'])
@login_required
def preferences_settings():
    """Update user preferences"""
    settings = current_user.user_settings
    
    if request.method == 'POST':
        settings.auto_scan_emails = request.form.get('auto_scan_emails') == 'true'
        settings.default_trip_visibility = TripVisibility[
            request.form.get('default_visibility', 'private').upper()
        ]
        settings.timezone = request.form.get('timezone', settings.timezone)
        
        db.session.commit()
        flash('Preferences updated successfully.', 'success')
        return redirect(url_for('settings'))
    
    return render_template('settings/preferences.html', settings=settings)




# Foursquare/Swarm Integration
@app.route('/foursquare/connect')
@login_required
def connect_foursquare():
    """Initiate Foursquare OAuth flow"""
    # Foursquare OAuth configuration
    client_id = os.getenv('FOURSQUARE_CLIENT_ID')
    
    if not client_id:
        flash('Foursquare integration is not configured. Please contact your administrator.', 'danger')
        return redirect(url_for('api_integrations'))
    
    redirect_uri = url_for('foursquare_callback', _external=True)
    auth_url = f"https://foursquare.com/oauth2/authenticate?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}"
    
    return redirect(auth_url)


@app.route('/foursquare/callback')
@login_required
def foursquare_callback():
    """Handle Foursquare OAuth callback"""
    code = request.args.get('code')
    
    if not code:
        flash('Foursquare authentication failed.', 'danger')
        return redirect(url_for('api_integrations'))
    
    # Exchange code for access token
    client_id = os.getenv('FOURSQUARE_CLIENT_ID')
    client_secret = os.getenv('FOURSQUARE_CLIENT_SECRET')
    redirect_uri = url_for('foursquare_callback', _external=True)
    
    token_url = 'https://foursquare.com/oauth2/access_token'
    params = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri,
        'code': code
    }
    
    try:
        response = requests.get(token_url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            access_token = data.get('access_token')
            
            # Save token to user settings
            settings = current_user.user_settings
            if not settings:
                settings = UserSettings(user_id=current_user.id)
                db.session.add(settings)
            
            settings.foursquare_access_token = access_token
            settings.foursquare_enabled = True
            db.session.commit()
            
            flash('Foursquare connected successfully! Your check-ins will sync automatically.', 'success')
        else:
            flash('Failed to connect to Foursquare. Please try again.', 'danger')
    
    except Exception as e:
        logger.error(f"Foursquare OAuth error: {str(e)}")
        flash('An error occurred while connecting to Foursquare.', 'danger')
    
    return redirect(url_for('api_integrations'))


@app.route('/foursquare/disconnect', methods=['POST'])
@login_required
def disconnect_foursquare():
    """Disconnect Foursquare integration"""
    settings = current_user.user_settings
    
    if settings:
        settings.foursquare_access_token = None
        settings.foursquare_enabled = False
        db.session.commit()
        
        flash('Foursquare disconnected successfully.', 'info')
    
    return redirect(url_for('api_integrations'))


@app.route('/trips/<int:trip_id>/sync-checkins', methods=['POST'])
@login_required
@requires_trip_access(edit=True)
def manual_sync_checkins(trip_id):
    """Manually trigger check-in sync for a trip"""
    trip = Trip.query.get_or_404(trip_id)
    
    from utils import sync_trip_checkins
    new_checkins = sync_trip_checkins(trip)
    
    if new_checkins > 0:
        flash(f'Added {new_checkins} new check-ins to your trip!', 'success')
    else:
        flash('No new check-ins found for this trip.', 'info')
    
    return redirect(url_for('view_trip', trip_id=trip_id))

@app.route('/api/flights/lookup', methods=['GET'])
@login_required
def lookup_flight():
    """Look up flight details using AirLabs API"""
    flight_number = request.args.get('flight_number', '').upper().strip()
    flight_date = request.args.get('date')
    
    if not flight_number or not flight_date:
        return jsonify({
            'success': False, 
            'message': 'Missing flight number or date'
        })
    
    # Get admin AirLabs API key from settings
    import os
    airlabs_api_key = os.getenv('AIRLABS_API_KEY')
    if not airlabs_api_key:
        return jsonify({
            'success': False,
            'message': 'AirLabs API not configured. Please contact administrator.'
        })
    
    try:
        # Call AirLabs API
        url = 'https://airlabs.co/api/v9/schedules'
        params = {
            'api_key': airlabs_api_key,
            'flight_iata': flight_number,
            'dep_date': flight_date  # Format: YYYY-MM-DD
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            return jsonify({
                'success': False,
                'message': f'API error: {response.status_code}'
            })
        
        data = response.json()
        
        if not data.get('response') or len(data['response']) == 0:
            return jsonify({
                'success': False,
                'message': 'Flight not found. Please check flight number and date.'
            })
        
        # Get first matching flight
        flight_data = data['response'][0]
        
        # Parse and format the data
        dep_code = flight_data.get('dep_iata', '')
        arr_code = flight_data.get('arr_iata', '')
        airline_code = flight_data.get('airline_iata', '')
        
        # Fetch airport info from AirLabs
        dep_info = get_airport_info(dep_code)
        arr_info = get_airport_info(arr_code)
        
        result = {
            'success': True,
            'flight': {
                'airline': get_airline_name(airline_code),
                'flight_number': flight_number,
                'departure_airport': dep_code,
                'departure_city': dep_info['city'],
                'departure_name': dep_info['name'],
                'arrival_airport': arr_code,
                'arrival_city': arr_info['city'],
                'arrival_name': arr_info['name'],
                'departure_time': format_airlabs_time(flight_data.get('dep_time')),
                'arrival_time': format_airlabs_time(flight_data.get('arr_time')),
                'departure_terminal': flight_data.get('dep_terminal', ''),
                'arrival_terminal': flight_data.get('arr_terminal', ''),
                'departure_gate': flight_data.get('dep_gate', ''),
                'arrival_gate': flight_data.get('arr_gate', ''),
                'status': flight_data.get('status', '')
            }
        }
        
        return jsonify(result)
        
    except requests.exceptions.Timeout:
        return jsonify({
            'success': False,
            'message': 'Request timed out. Please try again.'
        })
    except requests.exceptions.RequestException as e:
        logger.error(f"AirLabs API error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error connecting to flight data service.'
        })
    except Exception as e:
        logger.error(f"Flight lookup error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while looking up flight details.'
        })

def format_airlabs_time(time_str):
    """Convert AirLabs time format to datetime-local format"""
    if not time_str:
        return ''
    
    try:
        # AirLabs format: "2024-12-25 14:30"
        from datetime import datetime
        dt = datetime.strptime(time_str, '%Y-%m-%d %H:%M')
        # Convert to HTML datetime-local format: "2024-12-25T14:30"
        return dt.strftime('%Y-%m-%dT%H:%M')
    except:
        return ''

# ============================================
# FRIEND ROUTES
# ============================================

@app.route('/friends')
@login_required
def friends():
    """View friends list and requests"""
    friends = current_user.get_friends()
    pending_requests = current_user.get_pending_requests()
    sent_requests = [req for req in current_user.sent_friend_requests if req.status == 'pending']
    
    return render_template('friends/index.html',
                         friends=friends,
                         pending_requests=pending_requests,
                         sent_requests=sent_requests)

@app.route('/friends/request', methods=['POST'])
@login_required
def send_friend_request():
    """Send a friend request"""
    email = request.form.get('email')
    
    if not email:
        flash('Please provide an email address.', 'danger')
        return redirect(url_for('friends'))
    
    receiver = User.query.filter_by(email=email).first()
    
    if not receiver:
        flash('No user found with that email address.', 'danger')
        return redirect(url_for('friends'))
    
    if receiver.id == current_user.id:
        flash('You cannot send a friend request to yourself.', 'warning')
        return redirect(url_for('friends'))
    
    if current_user.is_friend_with(receiver):
        flash('You are already friends with this user.', 'info')
        return redirect(url_for('friends'))
    
    existing = FriendRequest.query.filter(
        ((FriendRequest.sender_id == current_user.id) & (FriendRequest.receiver_id == receiver.id)) |
        ((FriendRequest.sender_id == receiver.id) & (FriendRequest.receiver_id == current_user.id))
    ).filter(FriendRequest.status == 'pending').first()
    
    if existing:
        flash('A friend request already exists.', 'info')
        return redirect(url_for('friends'))
    
    friend_request = FriendRequest(sender_id=current_user.id, receiver_id=receiver.id)
    db.session.add(friend_request)
    db.session.commit()
    
    receiver_name = f"{receiver.first_name} {receiver.last_name}".strip() if receiver.first_name or receiver.last_name else receiver.username
    flash(f'Friend request sent to {receiver_name}!', 'success')

@app.route('/friends/accept/<int:request_id>', methods=['POST'])
@login_required
def accept_friend_request(request_id):
    """Accept a friend request"""
    friend_request = FriendRequest.query.get_or_404(request_id)
    
    if friend_request.receiver_id != current_user.id:
        flash('Invalid request.', 'danger')
        return redirect(url_for('friends'))
    
    friend_request.status = 'accepted'
    db.session.commit()
    
    flash(f'You are now friends with {friend_request.sender.username}!', 'success')
    return redirect(url_for('friends'))

@app.route('/friends/reject/<int:request_id>', methods=['POST'])
@login_required
def reject_friend_request(request_id):
    """Reject a friend request"""
    friend_request = FriendRequest.query.get_or_404(request_id)
    
    if friend_request.receiver_id != current_user.id:
        flash('Invalid request.', 'danger')
        return redirect(url_for('friends'))
    
    friend_request.status = 'rejected'
    db.session.commit()
    
    flash('Friend request rejected.', 'info')
    return redirect(url_for('friends'))

@app.route('/friends/remove/<int:user_id>', methods=['POST'])
@login_required
def remove_friend(user_id):
    """Remove a friend"""
    friend_request = FriendRequest.query.filter(
        ((FriendRequest.sender_id == current_user.id) & (FriendRequest.receiver_id == user_id)) |
        ((FriendRequest.sender_id == user_id) & (FriendRequest.receiver_id == current_user.id))
    ).filter(FriendRequest.status == 'accepted').first()
    
    if friend_request:
        db.session.delete(friend_request)
        db.session.commit()
        flash('Friend removed.', 'info')
    
    return redirect(url_for('friends'))

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    """404 error handler"""
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    db.session.rollback()
    return render_template('errors/500.html'), 500


# CLI commands
@app.cli.command()
def init_db():
    """Initialize the database"""
    db.create_all()
    print('Database initialized.')


@app.cli.command()
def create_admin():
    """Create admin user"""
    username = input('Admin username: ')
    email = input('Admin email: ')
    password = input('Admin password: ')
    
    user = User(username=username, email=email, role=UserRole.ADMIN)
    user.set_password(password)
    
    settings = UserSettings(user=user)
    
    db.session.add(user)
    db.session.add(settings)
    db.session.commit()
    
    print(f'Admin user {username} created.')


@app.cli.command()
def scan_emails():
    """Manually trigger email scan"""
    from email_scanner import scan_all_email_accounts
    
    print('Starting email scan...')
    trips_created = scan_all_email_accounts()
    print(f'Email scan complete. Created {trips_created} trips.')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
