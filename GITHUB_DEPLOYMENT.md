# GitHub Deployment Guide

This guide explains how to deploy Travel Tracker using GitHub as your source of truth.

## Overview

There are two deployment methods:

1. **Local Development** - Build from local files (use `docker-compose.yml`)
2. **GitHub Deployment** - Build from GitHub repository (use `docker-compose-github.yml`)

## Method 1: Local Development

Use this when developing locally with code changes.

```bash
# Standard local development
docker-compose up -d
```

## Method 2: GitHub Deployment

Use this for production deployments that automatically pull from GitHub.

### Initial Setup

#### 1. Push Code to GitHub

```bash
# Initialize git repository (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit"

# Add your GitHub remote
git remote add origin https://github.com/YOUR_USERNAME/travel-tracker.git

# Push to GitHub
git push -u origin main
```

#### 2. Update docker-compose-github.yml

Edit `docker-compose-github.yml` and replace `YOUR_USERNAME` with your actual GitHub username:

```yaml
build:
  context: https://github.com/YOUR_USERNAME/travel-tracker.git#main
```

Find and replace in two places:
- Line ~32 (web service)
- Line ~73 (scheduler service)

#### 3. Update deploy-github.sh

Edit `deploy-github.sh` and update the repository configuration:

```bash
GITHUB_REPO="YOUR_USERNAME/travel-tracker"
BRANCH="main"
```

#### 4. Make scripts executable

```bash
chmod +x deploy-github.sh
chmod +x start.sh
```

#### 5. Create .env file

```bash
cp .env.example .env
nano .env  # Edit with your configuration
```

#### 6. Deploy from GitHub

```bash
./deploy-github.sh
```

This will:
- Pull latest code from GitHub
- Build Docker images from the repository
- Start all services
- Run database migrations

### Updating Your Deployment

When you make changes to your code and push to GitHub:

```bash
# On your development machine
git add .
git commit -m "Description of changes"
git push origin main

# On your server
./deploy-github.sh
```

The deployment script will:
1. Stop existing containers
2. Remove old images
3. Pull latest code from GitHub
4. Rebuild containers
5. Start services
6. Run migrations

## Deployment Options

### Option A: Direct GitHub URL Build

Docker Compose can build directly from a GitHub URL:

```yaml
build:
  context: https://github.com/YOUR_USERNAME/travel-tracker.git#main
```

**Pros:**
- Always pulls latest code
- No local code needed
- Simple deployment

**Cons:**
- Requires public repository (or GitHub token)
- Slower builds (downloads each time)

### Option B: Git Clone + Local Build

Alternative approach - clone repository first:

```bash
# On your server
git clone https://github.com/YOUR_USERNAME/travel-tracker.git
cd travel-tracker

# Deploy
docker-compose up -d

# Update later
git pull origin main
docker-compose up -d --build
```

**Pros:**
- Works with private repositories
- Faster subsequent builds
- Can review changes before deploying

**Cons:**
- Requires git on server
- Extra step to pull changes

## Private Repository Setup

If using a private GitHub repository:

### Option 1: SSH Key

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Add to GitHub Settings > SSH Keys

# Use SSH URL in docker-compose-github.yml
build:
  context: git@github.com:YOUR_USERNAME/travel-tracker.git
```

### Option 2: Personal Access Token

```bash
# Create token at: https://github.com/settings/tokens
# Select: repo (full control)

# Use token in URL
build:
  context: https://YOUR_TOKEN@github.com/YOUR_USERNAME/travel-tracker.git#main
```

⚠️ **Security Note:** Never commit tokens to your repository!

### Option 3: GitHub Actions (Recommended for Private Repos)

Use GitHub Actions to build and push Docker images:

```yaml
# .github/workflows/deploy.yml
name: Build and Push

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build and push
        run: |
          docker build -t traveltracker:latest .
          docker push YOUR_REGISTRY/traveltracker:latest
```

Then pull pre-built images in docker-compose:

```yaml
web:
  image: YOUR_REGISTRY/traveltracker:latest
```

## Production Deployment Checklist

Before deploying to production:

### Security
- [ ] Change `SECRET_KEY` in `.env` to a strong random value
- [ ] Use strong database passwords
- [ ] Configure HTTPS/SSL certificates
- [ ] Set `SESSION_COOKIE_SECURE=true`
- [ ] Update OAuth redirect URIs to production URLs
- [ ] Never commit `.env` file to GitHub

### Configuration
- [ ] Update `GOOGLE_REDIRECT_URI` to your domain
- [ ] Update `MICROSOFT_REDIRECT_URI` to your domain
- [ ] Set correct `TIMEZONE`
- [ ] Configure email scanning interval
- [ ] Add API keys for integrations

### Infrastructure
- [ ] Set up reverse proxy (Nginx/Caddy)
- [ ] Configure SSL certificates (Let's Encrypt)
- [ ] Set up database backups
- [ ] Configure log rotation
- [ ] Set up monitoring (Uptime checks)
- [ ] Configure firewall rules

### Testing
- [ ] Test user registration
- [ ] Test OAuth flows (Gmail/Outlook)
- [ ] Test trip creation
- [ ] Test email scanning
- [ ] Test trip sharing
- [ ] Test admin functions

## Continuous Deployment

### Manual Deployment

```bash
# After pushing changes to GitHub
./deploy-github.sh
```

### Automated Deployment

Set up a webhook or use GitHub Actions:

```bash
# On your server, create webhook endpoint
# When GitHub pushes, run:
cd /path/to/travel-tracker
./deploy-github.sh
```

Or use GitHub Actions to deploy to your server via SSH.

## Rollback

If deployment fails:

```bash
# Stop current deployment
docker-compose -f docker-compose-github.yml down

# Checkout previous version
git checkout HEAD~1

# Redeploy
./deploy-github.sh
```

Or use specific git tag:

```bash
git checkout v1.0.0
./deploy-github.sh
```

## Environment Variables

Required on deployment server:

```bash
# Database
DATABASE_URL=postgresql://user:pass@db:5432/traveltracker
SECRET_KEY=your-secret-key

# OAuth (optional but recommended)
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
MICROSOFT_CLIENT_ID=...
MICROSOFT_CLIENT_SECRET=...

# APIs (optional)
UNITED_API_KEY=...
AMERICAN_API_KEY=...
DELTA_API_KEY=...
SOUTHWEST_API_KEY=...
IMMICH_API_URL=...
IMMICH_API_KEY=...
GOOGLE_MAPS_API_KEY=...
```

## Multiple Environments

Deploy to different environments:

### Staging

```bash
# docker-compose-staging.yml
build:
  context: https://github.com/YOUR_USERNAME/travel-tracker.git#staging
```

### Production

```bash
# docker-compose-production.yml
build:
  context: https://github.com/YOUR_USERNAME/travel-tracker.git#production
```

Use Git branches or tags for version control.

## Monitoring Deployments

```bash
# Watch logs during deployment
docker-compose -f docker-compose-github.yml logs -f

# Check service status
docker-compose -f docker-compose-github.yml ps

# Check application health
curl http://localhost:5000

# View recent logs
docker-compose -f docker-compose-github.yml logs --tail=100
```

## Troubleshooting

### Build fails from GitHub

```bash
# Check GitHub URL is correct
# Verify repository is public (or token is valid)
# Check Docker has internet access
docker-compose -f docker-compose-github.yml build --no-cache
```

### Services won't start

```bash
# Check logs
docker-compose -f docker-compose-github.yml logs

# Verify .env file exists
ls -la .env

# Check database is ready
docker-compose -f docker-compose-github.yml exec db pg_isready
```

### Database migration fails

```bash
# Try manual migration
docker-compose -f docker-compose-github.yml exec web flask db upgrade

# Or initialize database
docker-compose -f docker-compose-github.yml exec web flask init-db
```

## Support

For deployment issues:
1. Check logs: `docker-compose logs`
2. Review this guide
3. Check GitHub repository settings
4. Verify .env configuration

## Next Steps

After successful deployment:
1. Create admin user: `docker-compose exec web flask create-admin`
2. Access application at your domain
3. Configure integrations in admin panel
4. Set up monitoring and backups
5. Test all functionality

---

Happy deploying! 🚀
