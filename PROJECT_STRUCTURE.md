# Travel Tracker - Project Structure

Complete directory structure and file descriptions.

## Directory Layout

```
travel-tracker/
├── app.py                      # Main Flask application (routes, initialization)
├── models.py                   # Database models (SQLAlchemy)
├── auth.py                     # Authentication (login, OAuth, decorators)
├── admin.py                    # Admin dashboard and user management
├── email_scanner.py            # Email scanning service (Gmail/Outlook)
├── airline_apis.py             # Airline API integrations
├── utils.py                    # Utility functions
├── config.py                   # Configuration (dev/production)
├── scheduler.py                # Background job scheduler
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker image configuration
├── docker-compose.yml          # Multi-container orchestration
├── .env.example                # Environment variables template
├── .dockerignore              # Docker build exclusions
├── .gitignore                 # Git exclusions
├── start.sh                   # Quick start script
├── README.md                  # Complete documentation
├── QUICKSTART.md              # 5-minute setup guide
├── PROJECT_STRUCTURE.md       # This file
│
├── templates/                  # HTML templates (Jinja2)
│   ├── base.html              # Base template with navbar/footer
│   ├── index.html             # Landing page
│   ├── dashboard.html         # User dashboard
│   │
│   ├── auth/                  # Authentication templates
│   │   ├── login.html
│   │   └── register.html
│   │
│   ├── trips/                 # Trip management templates
│   │   ├── list.html         # List all trips
│   │   ├── view.html         # View trip details
│   │   ├── new.html          # Create new trip
│   │   ├── edit.html         # Edit trip
│   │   ├── add_flight.html   # Add flight to trip
│   │   ├── add_accommodation.html
│   │   ├── share.html        # Share trip
│   │   └── view_shared.html  # External share view
│   │
│   ├── settings/              # User settings templates
│   │   ├── index.html        # Settings dashboard
│   │   ├── profile.html      # Profile settings
│   │   └── preferences.html  # User preferences
│   │
│   ├── admin/                 # Admin panel templates
│   │   ├── dashboard.html    # Admin dashboard
│   │   ├── users.html        # User management
│   │   ├── user_detail.html  # User details
│   │   ├── edit_user.html    # Edit user
│   │   ├── features.html     # Feature management
│   │   ├── trips.html        # All trips view
│   │   ├── email_logs.html   # Email scan logs
│   │   └── settings.html     # System settings
│   │
│   └── errors/                # Error pages
│       ├── 404.html
│       ├── 500.html
│       └── expired_share.html
│
├── static/                     # Static assets (CSS/JS/images)
│   ├── css/
│   │   └── custom.css
│   ├── js/
│   │   └── main.js
│   └── images/
│       └── logo.png
│
├── migrations/                 # Database migrations
│   ├── versions/              # Migration files
│   └── env.py                 # Migration environment
│
├── logs/                       # Application logs (created at runtime)
│   ├── traveltracker.log
│   └── scheduler.log
│
└── uploads/                    # User uploads (created at runtime)
```

## Core Python Files

### app.py
Main Flask application containing:
- Route definitions for all pages
- Flask-Login setup
- Template filters
- Error handlers
- CLI commands (init_db, create_admin, scan_emails)

Key Routes:
- `/` - Landing page
- `/dashboard` - User dashboard
- `/trips` - List trips
- `/trips/<id>` - View trip
- `/trips/new` - Create trip
- `/trips/<id>/edit` - Edit trip
- `/trips/<id>/flights/add` - Add flight
- `/settings` - User settings
- `/admin` - Admin panel

### models.py
SQLAlchemy database models:
- `User` - User accounts with authentication
- `UserSettings` - Per-user feature toggles
- `EmailAccount` - OAuth tokens for email integration
- `Trip` - Trip information and metadata
- `Flight` - Flight details and status
- `Accommodation` - Hotel/rental information
- `TripShare` - Internal and external trip sharing
- `TripPhoto` - Immich photo associations
- `EmailScanLog` - Email scanning audit trail

### auth.py
Authentication module:
- Flask-Login configuration
- Login/logout routes
- User registration
- Google OAuth flow
- Microsoft OAuth flow
- Admin-required decorator
- User authorization helpers

### admin.py
Admin functionality:
- Admin dashboard with statistics
- User management (CRUD operations)
- Feature toggle management
- Email scan log viewer
- System-wide settings
- Bulk user operations

### email_scanner.py
Email scanning service:
- Base `EmailScanner` class
- `GmailScanner` - Gmail API integration
- `OutlookScanner` - Microsoft Graph API integration
- Flight email parsing (regex patterns)
- Automatic trip creation
- Airline detection
- Confirmation number extraction

### airline_apis.py
Airline API integrations:
- Base `AirlineAPI` class
- `UnitedAPI` - United Airlines
- `AmericanAPI` - American Airlines
- `DeltaAPI` - Delta Air Lines
- `SouthwestAPI` - Southwest Airlines
- `AirlineAPIManager` - Unified interface
- Flight status updates
- Booking detail retrieval

### utils.py
Utility functions:
- Share token generation
- Date/time formatting
- Airport code lookups
- Trip status calculations
- Permission checking decorators
- Google Maps geocoding
- OAuth token refresh
- Immich photo fetching

### config.py
Configuration classes:
- `Config` - Base configuration
- `DevelopmentConfig` - Development settings
- `ProductionConfig` - Production settings
- Environment variable loading
- API key configuration

### scheduler.py
Background task scheduler (APScheduler):
- Email scanning job (every 5 minutes)
- Flight status updates (every 30 minutes)
- Expired share cleanup (daily)
- Logging and error handling

## Docker Files

### Dockerfile
Multi-stage Python Docker image:
- Python 3.11 slim base
- System dependencies (PostgreSQL client)
- Python packages from requirements.txt
- Gunicorn WSGI server

### docker-compose.yml
Three-service architecture:
1. **db** - PostgreSQL 15 database
2. **web** - Flask application (Gunicorn)
3. **scheduler** - Background task runner

Features:
- Health checks
- Volume persistence
- Network isolation
- Environment variable injection

## Database Schema

### Tables

**users**
- User accounts, passwords, roles, login tracking

**user_settings**
- Feature toggles per user
- Privacy preferences
- Default settings

**email_accounts**
- OAuth tokens for Gmail/Outlook
- Token expiration tracking
- Last scan timestamp

**trips**
- Trip details, dates, destination
- Visibility settings
- Auto-detection flags

**flights**
- Flight numbers, airports, times
- Status tracking (scheduled/delayed/cancelled)
- Gate and terminal information

**accommodations**
- Hotel/rental details
- Check-in/out dates
- Location coordinates

**trip_shares**
- Internal user-to-user sharing
- External share links with tokens
- Edit permissions

**trip_photos**
- Immich asset references
- Photo metadata

**email_scan_logs**
- Scan history and statistics
- Error tracking

## Template Structure

### Base Template (base.html)
- Bootstrap 5 styling
- Navigation bar with user menu
- Flash message display
- Footer
- Common CSS/JS includes

### Page Templates
All extend base.html and use:
- Jinja2 template inheritance
- Bootstrap components
- Bootstrap Icons
- Form handling
- Dynamic content rendering

## Features Implemented

### User Features
✅ User registration and login
✅ OAuth integration (Google, Microsoft)
✅ Trip creation and management
✅ Flight tracking
✅ Accommodation tracking
✅ Trip sharing (internal and external)
✅ Privacy controls
✅ Email integration setup
✅ User preferences

### Admin Features
✅ User management dashboard
✅ Feature toggle per user
✅ Email scan log viewing
✅ System statistics
✅ Bulk user operations
✅ Trip overview

### Automation
✅ Scheduled email scanning
✅ Automatic trip creation from emails
✅ Flight status updates
✅ Token refresh
✅ Share link expiration

### Integrations
✅ Gmail API
✅ Microsoft Graph API
✅ Airline APIs (framework)
✅ Immich API (photo integration)
✅ Google Maps API (geocoding)

## API Endpoints

### Public Routes
- `GET /` - Landing page
- `GET /auth/login` - Login page
- `POST /auth/login` - Login submission
- `GET /auth/register` - Registration page
- `POST /auth/register` - Registration submission
- `GET /shared/<token>` - View shared trip

### Authenticated Routes
- `GET /dashboard` - User dashboard
- `GET /trips` - List trips
- `GET /trips/<id>` - View trip
- `POST /trips/new` - Create trip
- `POST /trips/<id>/edit` - Edit trip
- `POST /trips/<id>/delete` - Delete trip
- `GET /settings` - User settings

### Admin Routes
- `GET /admin` - Admin dashboard
- `GET /admin/users` - User list
- `GET /admin/users/<id>` - User details
- `POST /admin/users/<id>/edit` - Edit user
- `POST /admin/features/toggle` - Toggle features

### API Routes
- `POST /api/flights/<id>/update` - Update flight status

## Environment Variables

Required:
- `SECRET_KEY` - Flask secret key
- `DATABASE_URL` - PostgreSQL connection

Optional (OAuth):
- `GOOGLE_CLIENT_ID` - Gmail integration
- `GOOGLE_CLIENT_SECRET` - Gmail integration
- `MICROSOFT_CLIENT_ID` - Outlook integration
- `MICROSOFT_CLIENT_SECRET` - Outlook integration

Optional (APIs):
- `UNITED_API_KEY` - United Airlines
- `AMERICAN_API_KEY` - American Airlines
- `DELTA_API_KEY` - Delta Air Lines
- `SOUTHWEST_API_KEY` - Southwest Airlines
- `IMMICH_API_URL` - Immich server
- `IMMICH_API_KEY` - Immich authentication
- `GOOGLE_MAPS_API_KEY` - Maps and geocoding

Configuration:
- `EMAIL_SCAN_INTERVAL` - Scan frequency (seconds)
- `TIMEZONE` - Default timezone
- `FLASK_ENV` - Environment (development/production)

## Security Features

✅ Password hashing (Werkzeug)
✅ CSRF protection (Flask-WTF)
✅ Session management (Flask-Login)
✅ OAuth 2.0 flows
✅ Permission decorators
✅ SQL injection prevention (SQLAlchemy)
✅ XSS protection (Jinja2 autoescaping)
✅ Secure cookie settings

## Performance Optimizations

✅ Database indexing (user emails, trip dates)
✅ Eager loading (SQLAlchemy relationships)
✅ Connection pooling (PostgreSQL)
✅ Gunicorn multi-worker setup
✅ Background task offloading
✅ Token caching

## Monitoring and Logging

✅ Application logs (rotating file handler)
✅ Scheduler logs
✅ Email scan audit trail
✅ Error tracking
✅ Docker Compose logs

## Development Workflow

1. Make code changes
2. Restart specific service: `docker-compose restart web`
3. View logs: `docker-compose logs -f web`
4. Test changes
5. Create database migration if needed
6. Update documentation

## Deployment Notes

### Development
```bash
docker-compose up -d
```

### Production
- Use production config (`FLASK_ENV=production`)
- Set strong SECRET_KEY
- Use HTTPS
- Configure proper OAuth redirect URIs
- Set secure cookie flags
- Use volume backups for database

## Future Enhancements

Roadmap items:
- Mobile app (React Native)
- Calendar integration (Google Calendar, iCal)
- Car rental tracking
- Activity/tour bookings
- Expense tracking
- Weather forecasts
- Currency conversion
- Real-time notifications
- Packing list management
- Document storage (passports, tickets)

## Contributing

When contributing:
1. Follow existing code structure
2. Add tests for new features
3. Update documentation
4. Create database migrations
5. Test with Docker Compose

## File Size Summary

- Python files: ~4,500 lines
- Templates: ~15 files
- Configuration: 5 files
- Documentation: 3 files
- Total project: Fully modular, production-ready

---

For more information, see:
- [README.md](README.md) - Complete documentation
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
