# GitHub Upload Guide

Complete guide for uploading Travel Tracker to GitHub and setting up your repository.

## Complete File List

Here are all the files you need to upload to GitHub:

### Root Directory Files
```
travel-tracker/
├── .dockerignore               # Docker build exclusions
├── .env.example                # Environment variables template
├── .gitignore                  # Git exclusions
├── Dockerfile                  # Docker image configuration
├── docker-compose.yml          # Local development compose
├── docker-compose-github.yml   # GitHub deployment compose
├── deploy-github.sh            # GitHub deployment script (executable)
├── start.sh                    # Quick start script (executable)
├── LICENSE                     # MIT License
├── README.md                   # Main documentation
├── QUICKSTART.md              # 5-minute setup guide
├── PROJECT_STRUCTURE.md        # Project structure documentation
├── GITHUB_DEPLOYMENT.md        # GitHub deployment guide
├── requirements.txt            # Python dependencies
```

### Python Application Files
```
├── app.py                      # Main Flask application
├── models.py                   # Database models
├── auth.py                     # Authentication module
├── admin.py                    # Admin functionality
├── email_scanner.py            # Email scanning service
├── airline_apis.py             # Airline API integrations
├── utils.py                    # Utility functions
├── config.py                   # Configuration
├── scheduler.py                # Background task scheduler
```

### Templates Directory
```
├── templates/
│   ├── base.html              # Base template
│   ├── index.html             # Landing page
│   ├── dashboard.html         # User dashboard
│   │
│   ├── auth/
│   │   ├── login.html         # Login page
│   │   └── register.html      # Registration page
│   │
│   ├── trips/
│   │   ├── list.html          # Trip list
│   │   ├── view.html          # Trip details
│   │   ├── new.html           # Create trip form
│   │   ├── edit.html          # Edit trip (to be created)
│   │   ├── add_flight.html    # Add flight (to be created)
│   │   ├── add_accommodation.html  # Add accommodation (to be created)
│   │   ├── share.html         # Share trip (to be created)
│   │   └── view_shared.html   # External share view (to be created)
│   │
│   ├── settings/
│   │   ├── index.html         # Settings dashboard
│   │   ├── profile.html       # Profile settings (to be created)
│   │   └── preferences.html   # User preferences (to be created)
│   │
│   ├── admin/
│   │   ├── dashboard.html     # Admin dashboard (to be created)
│   │   ├── users.html         # User management (to be created)
│   │   └── ...                # Other admin templates (to be created)
│   │
│   └── errors/
│       ├── 404.html           # Page not found
│       └── 500.html           # Server error
```

### Directories (will be created at runtime)
```
├── migrations/                 # Database migrations (created by Flask-Migrate)
├── logs/                      # Application logs (created at runtime)
└── uploads/                   # User uploads (created at runtime)
```

## Step-by-Step GitHub Setup

### 1. Create GitHub Repository

1. Go to https://github.com
2. Click "New repository"
3. Repository name: `travel-tracker`
4. Description: "A comprehensive travel tracking application similar to TripIt"
5. Choose Public or Private
6. **Do NOT** initialize with README (we already have one)
7. Click "Create repository"

### 2. Prepare Local Repository

```bash
# Navigate to your project directory
cd travel-tracker

# Initialize git repository
git init

# Add all files
git add .

# Make initial commit
git commit -m "Initial commit: Travel Tracker application"

# Add your GitHub remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/travel-tracker.git

# Verify remote was added
git remote -v
```

### 3. Push to GitHub

```bash
# Push to GitHub
git push -u origin main

# If you get an error about 'master' vs 'main', rename your branch:
git branch -M main
git push -u origin main
```

### 4. Verify Upload

Visit your repository at: `https://github.com/YOUR_USERNAME/travel-tracker`

You should see all files uploaded.

### 5. Update GitHub-Specific Files

After uploading, you need to update two files to reference your actual GitHub username:

#### Update docker-compose-github.yml

Edit on GitHub or locally and commit:

1. Find line ~32: `context: https://github.com/YOUR_USERNAME/travel-tracker.git#main`
2. Replace `YOUR_USERNAME` with your actual GitHub username
3. Find line ~73: Same replacement
4. Commit and push changes

```bash
# Edit the file
nano docker-compose-github.yml

# Commit changes
git add docker-compose-github.yml
git commit -m "Update GitHub username in docker-compose"
git push origin main
```

#### Update deploy-github.sh

```bash
# Edit the file
nano deploy-github.sh

# Change line 10: GITHUB_REPO="YOUR_USERNAME/travel-tracker"
# Replace YOUR_USERNAME with your actual GitHub username

# Commit changes
git add deploy-github.sh
git commit -m "Update GitHub username in deployment script"
git push origin main
```

### 6. Set Up Repository Settings

On GitHub:

1. Go to Settings → General
2. Add topics: `travel`, `flask`, `docker`, `trip-planning`, `travel-tracker`
3. Add a description

#### Optional: Set Up GitHub Pages (for documentation)

1. Go to Settings → Pages
2. Source: Deploy from branch
3. Branch: main
4. Folder: / (root)
5. Save

Your README will be available at: `https://YOUR_USERNAME.github.io/travel-tracker/`

### 7. Add Repository Badges (Optional)

Add these to the top of your README.md:

```markdown
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=flat&logo=flask&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/postgresql-%23316192.svg?style=flat&logo=postgresql&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green.svg)
```

## What NOT to Upload

**NEVER upload these files to GitHub:**

❌ `.env` - Contains secrets and API keys  
❌ `*.db` or `*.sqlite` - Database files  
❌ `__pycache__/` - Python cache  
❌ `logs/*.log` - Log files  
❌ `uploads/*` - User uploads  
❌ `venv/` or `env/` - Virtual environments

These are already excluded in `.gitignore`.

## Making Updates

After making changes to your code:

```bash
# Check what changed
git status

# Add changed files
git add .

# Commit with descriptive message
git commit -m "Description of changes"

# Push to GitHub
git push origin main
```

## Deploying from GitHub

Once your code is on GitHub, anyone (including you on a server) can deploy:

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/travel-tracker.git
cd travel-tracker

# Create .env file
cp .env.example .env
nano .env  # Add your configuration

# Deploy from GitHub
chmod +x deploy-github.sh
./deploy-github.sh
```

Or use Docker Compose directly:

```bash
# For GitHub deployment
docker-compose -f docker-compose-github.yml up -d
```

## Repository Structure Best Practices

### Branching Strategy

Consider using branches for development:

```bash
# Create development branch
git checkout -b develop

# Make changes...
git add .
git commit -m "New feature"

# Push to GitHub
git push origin develop

# Later, merge to main via Pull Request on GitHub
```

### Recommended Branches

- `main` - Production-ready code
- `develop` - Development/testing
- `feature/feature-name` - Feature branches
- `hotfix/issue-name` - Quick fixes

### Release Tags

Create tags for versions:

```bash
# Tag a release
git tag -a v1.0.0 -m "Version 1.0.0 - Initial release"
git push origin v1.0.0

# Deploy specific version
git checkout v1.0.0
./deploy-github.sh
```

## GitHub Actions (Optional)

Create `.github/workflows/docker-build.yml` for automated builds:

```yaml
name: Docker Build

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Build Docker image
      run: docker build -t traveltracker:latest .
    
    - name: Test Docker image
      run: |
        docker run -d --name test traveltracker:latest
        docker ps | grep test
        docker stop test
```

## Collaborating

### Adding Collaborators

1. Go to Settings → Collaborators
2. Click "Add people"
3. Enter GitHub username
4. Choose permission level

### Contributing Guidelines

Create `CONTRIBUTING.md`:

```markdown
# Contributing to Travel Tracker

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a Pull Request

Please follow the existing code style and add tests for new features.
```

## Security Best Practices

### 1. Protect Secrets

Never commit:
- API keys
- OAuth client secrets
- Database passwords
- SECRET_KEY

Use environment variables or GitHub Secrets.

### 2. Use .gitignore

Already configured, but verify:

```bash
# Check if .env is ignored
git check-ignore .env
# Should output: .env
```

### 3. Enable Branch Protection

On GitHub:
1. Settings → Branches
2. Add rule for `main`
3. Require pull request reviews
4. Require status checks

## Troubleshooting

### Git Push Rejected

```bash
# If remote has changes you don't have
git pull origin main --rebase
git push origin main
```

### Large Files

GitHub has a 100MB file limit. For large files, use Git LFS:

```bash
git lfs install
git lfs track "*.db"
git add .gitattributes
```

### Wrong Remote URL

```bash
# Check current remote
git remote -v

# Change remote URL
git remote set-url origin https://github.com/YOUR_USERNAME/travel-tracker.git
```

## Next Steps After Upload

1. ✅ Verify all files are uploaded
2. ✅ Update repository settings
3. ✅ Add description and topics
4. ✅ Update docker-compose-github.yml with your username
5. ✅ Update deploy-github.sh with your username
6. ✅ Test deployment from GitHub
7. ✅ Add badges to README
8. ✅ Create release/tag for v1.0.0
9. ✅ Share repository link

## Support

For GitHub-related issues:
- [GitHub Documentation](https://docs.github.com)
- [Git Documentation](https://git-scm.com/doc)
- Check repository's Issues tab

---

🎉 **Your Travel Tracker is now on GitHub!**

Repository URL: `https://github.com/YOUR_USERNAME/travel-tracker`

Happy coding! 🚀
