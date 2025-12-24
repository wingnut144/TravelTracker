"""
Database models for Travel Tracking System
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import enum

db = SQLAlchemy()

class UserRole(enum.Enum):
    """User role enumeration"""
    USER = "user"
    ADMIN = "admin"

class TripVisibility(enum.Enum):
    """Trip visibility options"""
    PRIVATE = "private"
    SHARED = "shared"
    PUBLIC = "public"

class User(UserMixin, db.Model):
    """User model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    password_hash = db.Column(db.String(255))
    role = db.Column(db.Enum(UserRole), default=UserRole.USER, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    trips = db.relationship('Trip', back_populates='user', cascade='all, delete-orphan')
    email_accounts = db.relationship('EmailAccount', back_populates='user', cascade='all, delete-orphan')
    user_settings = db.relationship('UserSettings', back_populates='user', uselist=False, cascade='all, delete-orphan')
    shared_trips_received = db.relationship('TripShare', foreign_keys='TripShare.shared_with_user_id', back_populates='shared_with_user')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role == UserRole.ADMIN
    
    def get_friends(self):
        """Get list of accepted friends"""
        friends = []
        # Friends who I sent request to
        for req in self.sent_friend_requests:
            if req.status == 'accepted':
                friends.append(req.receiver)
        # Friends who sent request to me
        for req in self.received_friend_requests:
            if req.status == 'accepted':
                friends.append(req.sender)
        return friends
    
    def get_pending_requests(self):
        """Get pending friend requests received"""
        return [req for req in self.received_friend_requests if req.status == 'pending']
    
    def is_friend_with(self, user):
        """Check if this user is friends with another user"""
        return user in self.get_friends()
    
    def has_pending_request_from(self, user):
        """Check if there's a pending request from a user"""
        for req in self.received_friend_requests:
            if req.sender_id == user.id and req.status == 'pending':
                return True
        return False
    
    def __repr__(self):
        return f'<User {self.username}>'

class UserSettings(db.Model):
    """User-specific feature settings"""
    __tablename__ = 'user_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Feature toggles (controlled by admin)
    email_integration_enabled = db.Column(db.Boolean, default=False)
    immich_integration_enabled = db.Column(db.Boolean, default=False)
    google_maps_enabled = db.Column(db.Boolean, default=True)
    
    # User preferences
    auto_scan_emails = db.Column(db.Boolean, default=True)
    default_trip_visibility = db.Column(db.Enum(TripVisibility), default=TripVisibility.PRIVATE)
    timezone = db.Column(db.String(50), default='America/New_York')
    
    # Per-user OAuth app credentials (for Gmail/Outlook integration)
    google_client_id = db.Column(db.String(255))
    google_client_secret = db.Column(db.String(255))
    microsoft_client_id = db.Column(db.String(255))
    microsoft_client_secret = db.Column(db.String(255))
    
    # Per-user API credentials
    # Immich integration
    immich_api_url = db.Column(db.String(255))
    immich_api_key = db.Column(db.String(255))
    
    # Foursquare/Swarm API (for check-in integration)
    foursquare_access_token = db.Column(db.String(500))
    foursquare_enabled = db.Column(db.Boolean, default=False)
    
    # Relationships
    user = db.relationship('User', back_populates='user_settings')
    
    def has_google_oauth(self):
        """Check if user has configured Google OAuth"""
        return bool(self.google_client_id and self.google_client_secret)
    
    def has_microsoft_oauth(self):
        """Check if user has configured Microsoft OAuth"""
        return bool(self.microsoft_client_id and self.microsoft_client_secret)
    
    def has_immich(self):
        """Check if user has configured Immich"""
        return bool(self.immich_api_url and self.immich_api_key)
    
    def __repr__(self):
        return f'<UserSettings for User {self.user_id}>'

class EmailAccount(db.Model):
    """Email account credentials for scanning"""
    __tablename__ = 'email_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    email_type = db.Column(db.String(20), nullable=False)  # 'gmail' or 'outlook'
    email_address = db.Column(db.String(120), nullable=False)
    
    # OAuth tokens (encrypted in production)
    access_token = db.Column(db.Text)
    refresh_token = db.Column(db.Text)
    token_expires_at = db.Column(db.DateTime)
    
    last_scan = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='email_accounts')
    
    def __repr__(self):
        return f'<EmailAccount {self.email_address}>'

class Trip(db.Model):
    """Trip model"""
    __tablename__ = 'trips'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    destination = db.Column(db.String(200))
    destination_latitude = db.Column(db.Float)
    destination_longitude = db.Column(db.Float)
    background_image_url = db.Column(db.String(500))
    start_date = db.Column(db.DateTime, nullable=False, index=True)
    end_date = db.Column(db.DateTime, nullable=False)
    
    visibility = db.Column(db.Enum(TripVisibility), default=TripVisibility.PRIVATE, nullable=False)
    
    # Trip metadata
    confirmation_number = db.Column(db.String(100))
    notes = db.Column(db.Text)
    
    # Auto-detection flags
    auto_detected = db.Column(db.Boolean, default=False)
    email_source = db.Column(db.String(200))  # Email ID that created this trip
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='trips')
    flights = db.relationship('Flight', back_populates='trip', cascade='all, delete-orphan')
    accommodations = db.relationship('Accommodation', back_populates='trip', cascade='all, delete-orphan')
    shares = db.relationship('TripShare', back_populates='trip', cascade='all, delete-orphan')
    photos = db.relationship('TripPhoto', back_populates='trip', cascade='all, delete-orphan')
    checkins = db.relationship('CheckIn', back_populates='trip', cascade='all, delete-orphan')
    
    def is_upcoming(self):
        """Check if trip is upcoming"""
        return self.start_date > datetime.utcnow()
    
    def is_past(self):
        """Check if trip is in the past"""
        return self.end_date < datetime.utcnow()
    
    def is_current(self):
        """Check if trip is currently ongoing"""
        now = datetime.utcnow()
        return self.start_date <= now <= self.end_date
    
    def __repr__(self):
        return f'<Trip {self.title}>'

class Flight(db.Model):
    """Flight information"""
    __tablename__ = 'flights'
    
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    
    airline = db.Column(db.String(100), nullable=False)
    flight_number = db.Column(db.String(20), nullable=False)
    confirmation_number = db.Column(db.String(100))
    
    departure_airport = db.Column(db.String(10), nullable=False)
    arrival_airport = db.Column(db.String(10), nullable=False)
    departure_time = db.Column(db.DateTime, nullable=False, index=True)
    arrival_time = db.Column(db.DateTime, nullable=False)
    
    # Additional details
    departure_terminal = db.Column(db.String(10))
    arrival_terminal = db.Column(db.String(10))
    departure_gate = db.Column(db.String(10))
    arrival_gate = db.Column(db.String(10))
    seat_number = db.Column(db.String(10))
    cost = db.Column(db.Float)
    notes = db.Column(db.Text)
    status = db.Column(db.String(50))  # 'scheduled', 'delayed', 'cancelled', 'boarding', 'departed', 'arrived'
    
    # API sync
    last_api_update = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    trip = db.relationship('Trip', back_populates='flights')
    
    def __repr__(self):
        return f'<Flight {self.airline} {self.flight_number}>'

class Accommodation(db.Model):
    """Hotel/accommodation information"""
    __tablename__ = 'accommodations'
    
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.Text)
    check_in = db.Column(db.DateTime, nullable=False)
    check_out = db.Column(db.DateTime, nullable=False)
    
    confirmation_number = db.Column(db.String(100))
    phone = db.Column(db.String(50))
    
    # Location
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    trip = db.relationship('Trip', back_populates='accommodations')
    
    def __repr__(self):
        return f'<Accommodation {self.name}>'

class TripShare(db.Model):
    """Trip sharing with other users"""
    __tablename__ = 'trip_shares'
    
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    shared_with_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Null for external shares
    
    # External sharing
    share_token = db.Column(db.String(100), unique=True, index=True)  # For sharing outside the system
    external_email = db.Column(db.String(120))  # Email for external shares
    
    can_edit = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)  # Optional expiration for external shares
    
    # Relationships
    trip = db.relationship('Trip', back_populates='shares')
    shared_with_user = db.relationship('User', foreign_keys=[shared_with_user_id], back_populates='shared_trips_received')
    
    def __repr__(self):
        return f'<TripShare for Trip {self.trip_id}>'

class TripPhoto(db.Model):
    """Photos associated with trips (Immich integration)"""
    __tablename__ = 'trip_photos'
    
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    
    immich_asset_id = db.Column(db.String(100), unique=True)
    photo_url = db.Column(db.String(500))
    thumbnail_url = db.Column(db.String(500))
    
    taken_at = db.Column(db.DateTime)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    trip = db.relationship('Trip', back_populates='photos')
    
    def __repr__(self):
        return f'<TripPhoto {self.id} for Trip {self.trip_id}>'

class CheckIn(db.Model):
    """Foursquare/Swarm check-ins associated with trips"""
    __tablename__ = 'checkins'
    
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Foursquare data
    foursquare_checkin_id = db.Column(db.String(100), unique=True, index=True)
    venue_name = db.Column(db.String(255))
    venue_category = db.Column(db.String(255))
    venue_address = db.Column(db.String(500))
    
    # Location data
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    # Check-in details
    checkin_time = db.Column(db.DateTime, nullable=False, index=True)
    shout = db.Column(db.Text)  # User's comment/shout
    photo_url = db.Column(db.String(500))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    trip = db.relationship('Trip', back_populates='checkins')
    user = db.relationship('User', backref='checkins')
    
    def __repr__(self):
        return f'<CheckIn {self.venue_name} at {self.checkin_time}>'

class EmailScanLog(db.Model):
    """Log of email scans for debugging"""
    __tablename__ = 'email_scan_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    email_account_id = db.Column(db.Integer, db.ForeignKey('email_accounts.id'))
    
    scan_time = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    emails_processed = db.Column(db.Integer, default=0)
    trips_created = db.Column(db.Integer, default=0)
    errors = db.Column(db.Text)
    
    def __repr__(self):
        return f'<EmailScanLog {self.scan_time}>'

class APIStatus(db.Model):
    """Track API service status"""
    __tablename__ = 'api_status'
    
    id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(50), unique=True, nullable=False)  # 'airlabs', 'unsplash', etc.
    is_active = db.Column(db.Boolean, default=False)
    last_checked = db.Column(db.DateTime, default=datetime.utcnow)
    status_message = db.Column(db.String(200))
    
    def __repr__(self):
        return f'<APIStatus {self.service_name}: {"✓" if self.is_active else "✗"}>'

class FriendRequest(db.Model):
    """Friend request model"""
    __tablename__ = 'friend_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_friend_requests')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_friend_requests')
    
    def __repr__(self):
        return f'<FriendRequest {self.sender.username} -> {self.receiver.username}>'
