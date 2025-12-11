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
    
    # Google Maps API - NO LONGER NEEDED (using free OpenStreetMap)
    # google_maps_api_key = db.Column(db.String(255))
    
    # Airline APIs
    united_api_key = db.Column(db.String(255))
    american_api_key = db.Column(db.String(255))
    delta_api_key = db.Column(db.String(255))
    southwest_api_key = db.Column(db.String(255))
    
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
    
    # Google Maps no longer needed - using free OpenStreetMap
    # def has_google_maps(self):
    #     """Check if user has configured Google Maps"""
    #     return bool(self.google_maps_api_key)
    
    def has_airline_api(self, airline):
        """Check if user has configured specific airline API"""
        airline_map = {
            'united': self.united_api_key,
            'american': self.american_api_key,
            'delta': self.delta_api_key,
            'southwest': self.southwest_api_key
        }
        return bool(airline_map.get(airline.lower()))
    
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
    seat_number = db.Column(db.String(10))
    gate = db.Column(db.String(10))
    terminal = db.Column(db.String(10))
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
