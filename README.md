# Travel Tracker v1.5 - Changed Files Only

This archive contains **only the files modified or created** during today's v1.5 update.

## 📦 Contents

**Root Files (3):**
- models.py
- app.py  
- utils.py

**Documentation (2):**
- VERSION_1.5_FEATURES.md
- LOCATION_BACKGROUNDS_FEATURE.md

**Templates (6):**
- templates/dashboard.html
- templates/settings/profile.html (NEW)
- templates/trips/new.html
- templates/trips/edit.html (NEW)
- templates/trips/list.html
- templates/trips/view.html

## 🚀 Quick Deploy

```bash
# Extract
tar -xzf travel-tracker-v1.5-changes-only.tar.gz

# Copy to project
cp -r travel-tracker-v1.5-changes-only/* ~/TravelTracker/

# Push to GitHub
cd ~/TravelTracker
git add .
git commit -m "v1.5: Date-only inputs, image thumbnails, user names"
git push origin main

# Deploy to server
cd ~/TravelTracker
git pull origin main
docker-compose build web
docker-compose up -d
```

See VERSION_1.5_FEATURES.md for complete documentation!
