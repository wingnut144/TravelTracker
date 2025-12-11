# Travel Tracker System

A comprehensive travel tracking application similar to TripIt, built with Flask and Docker. Track your trips, flights, accommodations, and automatically import travel details from your email.

## Features

### Core Features
- **Multi-user support** with user authentication and role-based access
- **Trip Management**: Create, view, edit, and delete trips
- **Flight Tracking**: Add flights with confirmation numbers, track status
- **Accommodation Tracking**: Add hotels and rentals with location data
- **Trip Sharing**: Share trips with other users or via external links

### Email Integration
- **Automatic Email Scanning**: Scans Gmail and Outlook for flight confirmations
- **Auto-Trip Creation**: Automatically creates private trips from detected emails
- **Supported Airlines**: United, American, Delta, Southwest

### Airline API Integration
- Real-time flight status updates
- Gate and terminal information
- Delay and cancellation notifications

### Advanced Features
- **Immich Integration**: Link photos from your Immich server to trips
- **Google Maps Integration**: Geocoding for accommodations
- **Privacy Controls**: Private, shared, or public trip visibility
- **Admin Dashboard**: User management and feature controls

## Architecture

```
travel-tracker/
├── app.py                 # Main Flask application
├── models.py              # Database models
├── auth.py                # Authentication and OAuth
├── admin.py               # Admin functionality
├── email_scanner.py       # Email scanning service
├── airline_apis.py        # Airline API integrations
├── utils.py               # Utility functions
├── config.py              # Configuration
├── scheduler.py           # Background task scheduler
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker image configuration
├── docker-compose.yml     # Multi-container setup
└── templates/             # HTML templates (to be created)
```

## Prerequisites

- Docker and Docker Compose
- (Optional) OAuth credentials for Gmail/Outlook
- (Optional) Airline API keys
- (Optional) Immich server for photo integration
- (Optional) Google Maps API key

## Quick Start

### 1. Clone or Create Project Directory

```bash
mkdir travel-tracker
cd travel-tracker
# Copy all provided files into this directory
```

### 2. Configure Environment

```bash
cp .env.example .env
nano .env  # Edit with your API keys and settings
```

### 3. Build and Start

```bash
# Build Docker images
docker-compose build

# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f web
```

### 4. Initialize Database

```bash
# Run database migrations
docker-compose exec web flask db upgrade

# Create admin user
docker-compose exec web flask create-admin
```

### 5. Access Application

Open your browser to: `http://localhost:5000`

## Configuration

### Required Settings

- `SECRET_KEY`: Change this to a random string in production
- `DATABASE_URL`: PostgreSQL connection string (configured in docker-compose)

### Optional Integrations

#### Gmail Integration

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URI: `http://your-domain/auth/google/callback`
6. Copy Client ID and Secret to `.env`

#### Outlook Integration

1. Go to [Azure Portal](https://portal.azure.com)
2. Register a new application
3. Add Mail.Read permission
4. Create client secret
5. Add redirect URI: `http://your-domain/auth/microsoft/callback`
6. Copy Client ID and Secret to `.env`

#### Airline APIs

Contact each airline's developer portal:
- United: https://developer.united.com
- American: Contact AA developer support
- Delta: https://developer.delta.com
- Southwest: Contact Southwest developer support

Note: Actual API endpoints may require approval and partnership agreements.

#### Immich Integration

If you have an Immich server:
1. Get your Immich API URL (e.g., `http://immich:2283/api`)
2. Generate an API key in Immich settings
3. Add to `.env`

#### Google Maps

1. Get API key from [Google Cloud Console](https://console.cloud.google.com)
2. Enable Geocoding API
3. Add key to `.env`

## Usage

### For Users

#### Creating Trips

1. Log in to your account
2. Click "New Trip"
3. Enter trip details (title, destination, dates)
4. Set visibility (Private, Shared, or Public)
5. Add flights and accommodations

#### Email Integration

1. Go to Settings → Email Accounts
2. Click "Connect Gmail" or "Connect Outlook"
3. Authorize access
4. Enable auto-scanning

The system will scan your email every 5 minutes (configurable) for flight confirmations.

#### Sharing Trips

**Internal Sharing:**
- Go to trip details
- Click "Share"
- Enter username
- Choose edit permissions

**External Sharing:**
- Go to trip details
- Click "Share" → "External Link"
- Copy the generated link
- Send to anyone (expires in 30 days)

### For Administrators

#### Accessing Admin Panel

Navigate to `/admin` after logging in as admin.

#### Managing Users

- View all users
- Edit user settings
- Enable/disable features per user
- Activate/deactivate accounts

#### Feature Management

Enable/disable features globally or per-user:
- Email integration
- Immich integration
- Google Maps

#### Viewing Logs

- Email scan logs
- All trips overview
- System statistics

### CLI Commands

```bash
# Create admin user
docker-compose exec web flask create-admin

# Manually trigger email scan
docker-compose exec web flask scan-emails

# Initialize database
docker-compose exec web flask init-db

# Database migrations
docker-compose exec web flask db upgrade
```

## Development

### Running Locally (without Docker)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up PostgreSQL database
createdb traveltracker

# Configure environment
export DATABASE_URL=postgresql://user:pass@localhost/traveltracker
export SECRET_KEY=dev-secret-key

# Initialize database
flask db upgrade

# Run development server
flask run --debug
```

### Database Migrations

```bash
# Create new migration
docker-compose exec web flask db migrate -m "Description"

# Apply migrations
docker-compose exec web flask db upgrade

# Rollback
docker-compose exec web flask db downgrade
```

## Architecture Details

### Database Schema

- **users**: User accounts and authentication
- **user_settings**: Per-user feature toggles
- **trips**: Trip information
- **flights**: Flight details
- **accommodations**: Hotel/rental information
- **trip_shares**: Trip sharing (internal and external)
- **email_accounts**: OAuth tokens for email scanning
- **trip_photos**: Immich photo links
- **email_scan_logs**: Email scanning audit log

### Background Jobs

The scheduler service runs:

1. **Email Scanning** (every 5 minutes)
   - Scans connected email accounts
   - Detects flight confirmations
   - Creates private trips automatically

2. **Flight Status Updates** (every 30 minutes)
   - Updates flight statuses for upcoming flights (next 48 hours)
   - Fetches gate/terminal information
   - Detects delays and cancellations

3. **Share Cleanup** (daily at 2 AM)
   - Removes expired external share links

## Security Considerations

### Production Deployment

1. **Change SECRET_KEY**: Use a strong random string
2. **Use HTTPS**: Configure SSL certificates
3. **Secure Database**: Use strong passwords
4. **OAuth Secrets**: Keep credentials secure
5. **Token Encryption**: Consider encrypting OAuth tokens in database

### Privacy

- Trips are private by default
- Email scanning only processes user's own emails
- External shares expire after 30 days
- Users can disable features at any time

## Troubleshooting

### Email Scanning Not Working

1. Check OAuth tokens are valid
2. Verify email integration is enabled for user
3. Check scheduler logs: `docker-compose logs scheduler`
4. Manually trigger scan: `docker-compose exec web flask scan-emails`

### Airline API Errors

- Most airline APIs require partnership agreements
- The code includes placeholders for API endpoints
- You may need to adjust endpoints based on actual API documentation

### Database Connection Issues

```bash
# Check database is running
docker-compose ps

# Restart database
docker-compose restart db

# Check database logs
docker-compose logs db
```

### Immich Integration Issues

- Verify Immich server is accessible from Docker network
- Check API key is valid
- Ensure user has Immich integration enabled

## API Endpoints

The application includes a RESTful API:

- `POST /api/flights/<id>/update` - Update flight status from airline API
- More endpoints can be added for mobile apps or integrations

## Customization

### Adding New Airlines

1. Create new class in `airline_apis.py`
2. Inherit from `AirlineAPI`
3. Implement `get_flight_status()` and `get_flight_details()`
4. Add to `AirlineAPIManager`
5. Update email scanner patterns

### Custom Email Patterns

Edit `email_scanner.py`:
- Add patterns to `AIRLINE_PATTERNS`
- Adjust `parse_flight_email()` for your needs

### Styling

Templates use Bootstrap 5 (when created). Customize:
- Create `static/css/custom.css`
- Override Bootstrap variables
- Add custom styles

## License

[Add your license here]

## Support

For issues and questions:
1. Check logs: `docker-compose logs`
2. Review this README
3. Check airline API documentation
4. Verify OAuth credentials

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Roadmap

- [ ] Mobile app (React Native)
- [ ] Car rental tracking
- [ ] Activity/tour booking integration
- [ ] Travel expense tracking
- [ ] Calendar integration (Google Calendar, iCal)
- [ ] Weather forecasts
- [ ] Currency conversion
- [ ] Travel document storage
- [ ] Packing list management
- [ ] Real-time notifications (push, SMS)
