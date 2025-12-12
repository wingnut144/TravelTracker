# Foursquare/Swarm Integration Setup Guide

Complete guide to setting up automatic check-in syncing from Foursquare Swarm.

## 🎯 Overview

The Foursquare integration automatically imports your Swarm check-ins and displays them on your trips with:
- Venue names and categories
- Addresses and locations
- Check-in photos
- Your comments/shouts
- Timestamps

Check-ins are synced automatically every hour for active trips.

---

## 📋 Prerequisites

1. **Foursquare Developer Account**
   - Sign up at: https://foursquare.com/developers/
   - Free tier is sufficient

2. **Foursquare/Swarm App**
   - Have check-ins in your Swarm history
   - Connected to the same Foursquare account

---

## 🔧 Step 1: Create Foursquare App

### 1.1 Register Application

1. Go to https://foursquare.com/developers/apps
2. Click **"Create a New App"**
3. Fill in:
   - **App Name:** `Travel Tracker` (or your preference)
   - **Download / Welcome page url:** `https://your-domain.com` (your Travel Tracker URL)
   - **Redirect URI:** `https://your-domain.com/foursquare/callback`
     - **Important:** Must match exactly (http vs https, with/without www)
     - **Example:** `https://traveltracker.example.com/foursquare/callback`

### 1.2 Get Credentials

After creating the app:
1. Note your **Client ID**
2. Note your **Client Secret**
3. Keep these secure!

---

## 🔧 Step 2: Configure Travel Tracker

### 2.1 Add to Environment Variables

Add to your `.env` file:

```bash
# Foursquare/Swarm Integration
FOURSQUARE_CLIENT_ID=your_actual_client_id_here
FOURSQUARE_CLIENT_SECRET=your_actual_client_secret_here
```

### 2.2 Update Docker Environment

If using Docker, also update `docker-compose.yml`:

```yaml
services:
  web:
    environment:
      - FOURSQUARE_CLIENT_ID=${FOURSQUARE_CLIENT_ID}
      - FOURSQUARE_CLIENT_SECRET=${FOURSQUARE_CLIENT_SECRET}
```

### 2.3 Restart Application

```bash
docker-compose restart web
# or
docker-compose down && docker-compose up -d
```

---

## 🔧 Step 3: Connect Your Account

### 3.1 In Travel Tracker

1. Go to **Settings** → **API Integrations**
2. Find the **Foursquare / Swarm Integration** section
3. Click **"Connect Foursquare Account"**

### 3.2 Authorization Flow

1. You'll be redirected to Foursquare.com
2. Log in to your Foursquare account (if not already)
3. Review permissions (read-only access to check-ins)
4. Click **"Allow"**
5. You'll be redirected back to Travel Tracker

### 3.3 Verify Connection

You should see:
- ✅ "Connected!" message
- "Your Foursquare check-ins are syncing automatically"

---

## 🔧 Step 4: Test the Integration

### 4.1 Manual Sync

1. Go to any trip
2. If you have check-ins during that trip's dates, click **"Sync Now"**
3. Check-ins should appear within seconds

### 4.2 Check Results

Each check-in displays:
- 📍 Venue name
- 🏷️ Category (Restaurant, Bar, Airport, etc.)
- 📍 Address
- 🕐 Date and time
- 💬 Your comment (if any)
- 📸 Photo (if you added one)

---

## ⚙️ How It Works

### Automatic Syncing

The scheduler runs every hour and:
1. Finds trips ending within the last 7 days
2. For users with Foursquare enabled
3. Fetches check-ins matching trip dates
4. Imports new check-ins (avoids duplicates)
5. Attaches them to the appropriate trips

### Manual Syncing

You can trigger immediate sync:
1. View any trip
2. Click **"Sync Now"** button
3. New check-ins appear immediately

### Data Stored

For each check-in, we store:
- Foursquare check-in ID (prevents duplicates)
- Venue name, category, address
- Coordinates (latitude/longitude)
- Check-in timestamp
- Your comment/shout
- Photo URL (if available)

---

## 🔒 Security & Privacy

### What We Access

- **Read-only** access to your check-ins
- No ability to create, edit, or delete
- Only check-in data (no friends, messages, etc.)

### Data Storage

- Access token stored encrypted in database
- Only you can see your check-ins
- You can disconnect anytime

### Disconnecting

To stop syncing:
1. Go to **Settings** → **API Integrations**
2. Click **"Disconnect Foursquare"**
3. Your existing check-ins remain
4. New check-ins won't be synced

---

## 🐛 Troubleshooting

### "Foursquare integration is not configured"

**Problem:** Environment variables not set

**Solution:**
1. Check `.env` file has `FOURSQUARE_CLIENT_ID` and `FOURSQUARE_CLIENT_SECRET`
2. Restart Docker containers
3. Verify variables with: `docker-compose exec web env | grep FOURSQUARE`

### "Authentication failed"

**Problem:** Redirect URI mismatch

**Solution:**
1. Check Foursquare app settings
2. Redirect URI must exactly match: `https://your-domain.com/foursquare/callback`
3. Including http vs https, www or not, trailing slash

### "No check-ins found"

**Possible causes:**
1. No check-ins during trip dates
2. Check-in dates don't overlap with trip dates
3. Foursquare API rate limit (rare)

**Solution:**
- Verify check-ins exist in Swarm app
- Check trip dates match your actual travel
- Wait an hour for automatic sync
- Try manual "Sync Now"

### Check-ins appear on wrong trip

**Problem:** Trip dates overlap

**Solution:**
- Check-ins are matched by timestamp
- Adjust trip dates to be more accurate
- Check-ins will attach to first matching trip

---

## 📊 API Limits

### Foursquare API

- **Rate Limits:** 500 requests/hour (per user)
- **Quota:** Free tier sufficient for most users
- **Check-in History:** Full history available

### Travel Tracker Syncing

- **Automatic:** Every hour
- **Manual:** Unlimited
- **Lookback:** 7 days from trip end date
- **Per-request:** Up to 250 check-ins

---

## 🎨 Customization

### Changing Sync Frequency

Edit `scheduler.py`:

```python
# Change from hourly to every 30 minutes
scheduler.add_job(
    sync_foursquare_checkins_job,
    trigger=IntervalTrigger(minutes=30),  # Changed from hours=1
    id='sync_foursquare',
    name='Sync Foursquare check-ins',
    replace_existing=True
)
```

### Changing Lookback Period

Edit `scheduler.py`:

```python
# Change from 7 days to 30 days
seven_days_ago = now - timedelta(days=7)  # Change to days=30
```

---

## 🔄 Migration Guide

### For Existing Users

If you're adding Foursquare to an existing Travel Tracker:

1. **Database migration** (already done in v1.5):
   - `checkins` table created
   - `foursquare_enabled` and `foursquare_access_token` added to user_settings

2. **Update code:**
   - Pull latest from repository
   - Rebuild Docker containers

3. **Configure:**
   - Add Foursquare credentials to `.env`
   - Restart services

4. **Connect:**
   - Each user connects their own Foursquare account
   - Historical check-ins will sync for existing trips

---

## 📚 API Documentation

### Foursquare API v2

- **Documentation:** https://developer.foursquare.com/docs/api-reference/
- **Check-ins Endpoint:** `/users/self/checkins`
- **Required Parameters:**
  - `oauth_token` - User's access token
  - `v` - API version date (YYYYMMDD format)
  - `afterTimestamp` - Unix timestamp (start)
  - `beforeTimestamp` - Unix timestamp (end)

### Response Format

```json
{
  "response": {
    "checkins": {
      "items": [
        {
          "id": "checkin_id",
          "createdAt": 1234567890,
          "shout": "Great coffee!",
          "venue": {
            "name": "Starbucks",
            "categories": [{"name": "Coffee Shop"}],
            "location": {
              "address": "123 Main St",
              "lat": 37.7749,
              "lng": -122.4194
            }
          },
          "photos": {
            "count": 1,
            "items": [{"prefix": "...", "suffix": "..."}]
          }
        }
      ]
    }
  }
}
```

---

## ✅ Testing Checklist

After setup, verify:

- [ ] Environment variables set
- [ ] Docker containers restarted
- [ ] "Connect Foursquare" button visible
- [ ] OAuth flow completes successfully
- [ ] "Connected!" message appears
- [ ] Manual sync works on a trip
- [ ] Check-ins display with all details
- [ ] Photos appear (if you have any)
- [ ] Automatic hourly sync runs (check logs)
- [ ] Disconnect/reconnect works

---

## 🆘 Support

### Check Logs

```bash
# Web application logs
docker-compose logs web | grep -i foursquare

# Scheduler logs
docker-compose logs scheduler | grep -i foursquare
```

### Common Log Messages

**Success:**
```
INFO: Added 5 check-ins to trip 123: Paris Adventure
INFO: Foursquare sync completed. Added 15 total check-ins.
```

**Errors:**
```
ERROR: Foursquare API error: 401 - Invalid token
ERROR: Error syncing trip 123: Connection timeout
```

---

## 🎉 You're Done!

Your Travel Tracker now automatically imports your Swarm check-ins! Every trip will show:
- Where you went
- When you were there
- What you said about each place
- Photos you took

Enjoy your enhanced travel memories! ✈️🌍📍
