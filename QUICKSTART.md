# Quick Start Guide - Travel Tracker

Get up and running with Travel Tracker in 5 minutes!

## Prerequisites

- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed ([Get Docker Compose](https://docs.docker.com/compose/install/))

## Installation

### 1. Quick Setup (Recommended)

```bash
# Make the startup script executable
chmod +x start.sh

# Run the startup script
./start.sh
```

The script will:
- Check for Docker and Docker Compose
- Create `.env` file with a random SECRET_KEY
- Build Docker images
- Start all services
- Initialize the database
- Provide next steps

### 2. Manual Setup

If you prefer manual setup:

```bash
# Copy environment file
cp .env.example .env

# Edit .env and set your SECRET_KEY
nano .env

# Build and start services
docker-compose up -d

# Wait for database to start (10 seconds)
sleep 10

# Initialize database
docker-compose exec web flask db upgrade
# OR if that fails:
docker-compose exec web flask init-db

# Create admin user
docker-compose exec web flask create-admin
```

## First Steps

### 1. Create Admin User

```bash
docker-compose exec web flask create-admin
```

Follow the prompts to create your admin account.

### 2. Access the Application

Open your browser and go to: **http://localhost:5000**

### 3. Login

Use the admin credentials you just created to log in.

### 4. Configure Email Integration (Optional)

To enable automatic trip imports from email:

#### For Gmail:

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Add redirect URI: `http://localhost:5000/auth/google/callback`
6. Copy Client ID and Secret to `.env`:
   ```
   GOOGLE_CLIENT_ID=your-client-id
   GOOGLE_CLIENT_SECRET=your-client-secret
   ```
7. Restart: `docker-compose restart`
8. In app: Settings → Email Accounts → Connect Gmail

#### For Outlook:

1. Go to [Azure Portal](https://portal.azure.com)
2. Register a new application
3. Add Mail.Read permission
4. Create client secret
5. Add redirect URI: `http://localhost:5000/auth/microsoft/callback`
6. Copy Client ID and Secret to `.env`:
   ```
   MICROSOFT_CLIENT_ID=your-client-id
   MICROSOFT_CLIENT_SECRET=your-client-secret
   ```
7. Restart: `docker-compose restart`
8. In app: Settings → Email Accounts → Connect Outlook

### 5. Enable Features for Users

As admin:

1. Go to Admin Dashboard (`/admin`)
2. Click on "Users"
3. Select a user
4. Edit user settings
5. Enable:
   - Email Integration
   - Immich Integration (if you have Immich)
   - Google Maps (if you have API key)

## Basic Usage

### Creating a Trip

1. Click "New Trip" in the navigation
2. Fill in trip details:
   - Title (e.g., "Hawaii Vacation")
   - Destination
   - Start and end dates
   - Visibility (Private/Shared/Public)
3. Click "Create Trip"

### Adding Flights

1. Open a trip
2. Click "Add Flight"
3. Enter flight details:
   - Airline
   - Flight number
   - Airports (3-letter codes)
   - Departure/arrival times
   - Confirmation number
4. Click "Add Flight"

### Adding Accommodations

1. Open a trip
2. Click "Add Accommodation"
3. Enter hotel/rental details:
   - Name
   - Address
   - Check-in/out dates
   - Confirmation number
4. Click "Add Accommodation"

### Sharing Trips

#### Internal Sharing (with other users):

1. Open a trip
2. Click "Share"
3. Enter username
4. Choose edit permissions
5. Click "Share"

#### External Sharing (with anyone):

1. Open a trip
2. Click "Share" → "External Link"
3. Copy the generated link
4. Send link to anyone
5. Link expires in 30 days

## Automatic Email Scanning

Once email integration is enabled:

1. The system scans your email every 5 minutes
2. Looks for flight confirmations from:
   - United Airlines
   - American Airlines
   - Delta Air Lines
   - Southwest Airlines
3. Automatically creates private trips
4. You can review and edit them in your dashboard

## Useful Commands

### View Logs
```bash
docker-compose logs -f web
docker-compose logs -f scheduler
```

### Restart Services
```bash
docker-compose restart
```

### Stop Everything
```bash
docker-compose down
```

### Start Everything
```bash
docker-compose up -d
```

### Manually Trigger Email Scan
```bash
docker-compose exec web flask scan-emails
```

### Access Database
```bash
docker-compose exec db psql -U traveluser -d traveltracker
```

## Troubleshooting

### Services won't start
```bash
# Check logs
docker-compose logs

# Try rebuilding
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Database errors
```bash
# Reset database
docker-compose down -v
docker-compose up -d
sleep 10
docker-compose exec web flask init-db
```

### Can't connect to email
1. Check OAuth credentials in `.env`
2. Verify redirect URIs match
3. Restart services: `docker-compose restart`
4. Check admin enabled email integration for user

### Email scanning not working
```bash
# Check scheduler logs
docker-compose logs scheduler

# Manually trigger scan
docker-compose exec web flask scan-emails
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Configure additional integrations (Immich, Google Maps)
- Set up airline API keys for real-time flight updates
- Invite team members or family

## Support

For issues:
1. Check logs: `docker-compose logs`
2. Review this guide
3. Check the main README.md

## Security Note

⚠️ **Production Deployment:**

Before deploying to production:
1. Change SECRET_KEY in `.env`
2. Use strong database passwords
3. Enable HTTPS
4. Set `SESSION_COOKIE_SECURE=true`
5. Use environment-specific OAuth redirect URIs

---

Happy travels! 🌍✈️
