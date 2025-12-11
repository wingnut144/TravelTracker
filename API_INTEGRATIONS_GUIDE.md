# API Integrations Setup Guide

## Overview

Travel Tracker supports **per-user API integrations** for enhanced features. Each user configures their own API keys and credentials, ensuring privacy, security, and independent usage.

## Supported Integrations

### 1. **Immich** - Photo Management
- Link photos from your Immich server to trips
- Automatic photo discovery based on dates
- Location-based photo matching

### 2. **Google Maps** - Geocoding
- Convert addresses to coordinates
- Display accommodations on maps
- Location-based features

### 3. **Airline APIs** - Flight Status
- Real-time flight status updates
- Gate and terminal information
- Delay notifications
- Supported: United, American, Delta, Southwest

### 4. **Email Integration** (OAuth Apps)
- Gmail and Outlook scanning
- Automatic flight detection
- Trip creation from emails

## Quick Setup Guide

### Access API Integrations

1. Log in to Travel Tracker
2. Go to **Settings** → **API Integrations**
3. Configure the services you want to use
4. Test each integration before saving

---

## Immich Integration

### What You Need
- Your Immich server URL
- An Immich API key

### Step-by-Step Setup

#### 1. Get Your Immich API Key

1. Open your Immich web interface
2. Click on your profile → **Account Settings**
3. Navigate to **API Keys**
4. Click **Create New Key**
5. Give it a name (e.g., "Travel Tracker")
6. Copy the generated API key

#### 2. Configure in Travel Tracker

1. Go to **Settings** → **API Integrations**
2. Find the **Immich Integration** section
3. Enter your details:
   - **Server URL**: `http://your-server:2283/api`
     - Examples:
       - Local: `http://192.168.1.100:2283/api`
       - Remote: `https://immich.yourdomain.com/api`
   - **API Key**: Paste the key from step 1
4. Click **Test Connection** to verify
5. If successful, click **Save**

#### 3. Enable for Your Account

Ask your administrator to enable **Immich Integration** for your account in the admin panel.

### Testing

The test button will:
- ✅ Connect to your Immich server
- ✅ Verify API key is valid
- ✅ Check server version
- ✅ Confirm accessibility

### How It Works

When viewing a trip:
1. Travel Tracker queries your Immich server
2. Searches for photos taken during trip dates
3. Filters by trip location (if available)
4. Displays thumbnails in the trip view
5. Links to full-resolution photos in Immich

---

## Google Maps Integration

### What You Need
- A Google Cloud account (free tier available)
- A Google Maps API key with Geocoding API enabled

### Step-by-Step Setup

#### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click **Select a project** → **New Project**
3. Name: "Travel Tracker" (or any name)
4. Click **Create**

#### 2. Enable Geocoding API

1. Navigate to **APIs & Services** → **Library**
2. Search for "Geocoding API"
3. Click on it and press **Enable**

#### 3. Create API Key

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **API key**
3. Copy the generated API key

#### 4. (Recommended) Restrict API Key

1. Click on the API key to edit it
2. Under **API restrictions**, select **Restrict key**
3. Choose **Geocoding API** from the dropdown
4. Save

#### 5. Configure in Travel Tracker

1. Go to **Settings** → **API Integrations**
2. Find the **Google Maps API** section
3. Paste your API key
4. Click **Test API Key** to verify
5. If successful, click **Save**

#### 6. Enable for Your Account

Ask your administrator to enable **Google Maps** for your account in the admin panel.

### Testing

The test button will:
- ✅ Make a sample geocoding request
- ✅ Verify API key is valid
- ✅ Check for proper permissions
- ✅ Confirm quota is available

### How It Works

When adding an accommodation:
1. You enter an address
2. Travel Tracker sends it to Google Maps API
3. Gets back latitude and longitude
4. Stores coordinates for map display
5. Shows location on trip view

### Pricing

- **Free tier**: 28,500 geocoding requests per month
- Travel Tracker usage: ~1 request per accommodation added
- Most users stay well within free tier

---

## Airline APIs Integration

### What You Need
- Direct API partnerships with airlines
- API keys from airline developer programs

### Important Notes

⚠️ **Airline APIs typically require:**
- Business partnerships with airlines
- API access agreements
- Developer program enrollment
- May have costs associated

These integrations are for users who already have airline API access through their organizations.

### Supported Airlines

1. **United Airlines**
2. **American Airlines**
3. **Delta Air Lines**
4. **Southwest Airlines**

### How to Get Airline API Keys

Each airline has its own developer program:

#### United Airlines
- Visit: [United Developer Portal](https://developer.united.com)
- Apply for API access
- Enroll in developer program

#### American Airlines
- Visit: American Airlines Developer Program
- Request API credentials
- Complete partnership application

#### Delta Air Lines
- Contact Delta Technology Solutions
- Request developer access
- Complete API agreement

#### Southwest Airlines
- Contact Southwest Developer Relations
- Apply for API partnership

### Configuration

1. Go to **Settings** → **API Integrations**
2. Find the **Airline APIs** section
3. Enter API keys for airlines you have access to
4. Test each airline individually
5. Click **Save All**

### Testing

The test button will:
- ✅ Validate API key format
- ⚠️ Note: Full validation requires active API partnership

### How It Works

For flights with configured airline APIs:
1. Click "Update Status" on a flight
2. Travel Tracker queries the airline API
3. Gets real-time flight information
4. Updates: status, gate, terminal, delays
5. Displays in trip view

### Without Airline APIs

If you don't have airline API access:
- ✅ Email scanning still works
- ✅ Manual flight entry works
- ❌ Real-time status updates unavailable
- Alternative: Check airline websites/apps

---

## Email Integration (OAuth Apps)

Covered in detail in [EMAIL_INTEGRATION_GUIDE.md](EMAIL_INTEGRATION_GUIDE.md)

### Quick Summary

1. **Settings** → **OAuth Apps**
2. Create Google Cloud / Azure app
3. Configure OAuth credentials
4. **Settings** → **Email Accounts**
5. Connect Gmail or Outlook
6. Email scanning starts automatically

---

## Security & Privacy

### Your Data
- ✅ All API keys stored encrypted in database
- ✅ Only you can access your credentials
- ✅ Admin cannot see your API keys
- ✅ Keys are never shared between users
- ✅ You can remove keys anytime

### Rate Limits
- Each user has independent rate limits
- Your usage doesn't affect other users
- No shared quotas

### Best Practices

1. **Use API Key Restrictions**
   - Restrict Google Maps key to Geocoding API only
   - Restrict by IP if possible
   - Set usage quotas

2. **Monitor Usage**
   - Check Google Cloud Console for API usage
   - Watch for unexpected spikes
   - Set up billing alerts

3. **Keep Keys Secure**
   - Never share your API keys
   - Don't commit keys to public repos
   - Rotate keys periodically

4. **Test Before Deploying**
   - Always use test buttons
   - Verify connectivity
   - Confirm permissions

---

## Troubleshooting

### Immich Connection Failed

**Symptoms**: "Connection timeout" or "Connection error"

**Solutions**:
1. ✅ Check server URL is correct (include `/api`)
2. ✅ Verify Immich server is accessible from Travel Tracker
3. ✅ Confirm API key is valid in Immich
4. ✅ Check firewall/network settings
5. ✅ Try with `http://` if `https://` fails (local networks)

### Google Maps API Error

**Symptoms**: "API key invalid" or "Request denied"

**Solutions**:
1. ✅ Verify API key is copied completely
2. ✅ Check Geocoding API is enabled
3. ✅ Confirm API key restrictions allow request
4. ✅ Check billing is enabled (if past free tier)
5. ✅ Wait a few minutes after creating key

### Email Integration Not Working

**Symptoms**: No trips being created automatically

**Solutions**:
1. ✅ Check OAuth apps configured in **OAuth Apps**
2. ✅ Verify email connected in **Email Accounts**
3. ✅ Confirm admin enabled email integration
4. ✅ Check "Auto scan emails" in **Preferences**
5. ✅ Verify flight confirmation emails in inbox

### Airline API Not Updating

**Symptoms**: "Failed to update flight status"

**Solutions**:
1. ✅ Verify you have API access with that airline
2. ✅ Check API key is correct and active
3. ✅ Confirm flight number and date are valid
4. ✅ Try again later (API may be temporarily down)

---

## Testing Checklist

Before considering an integration complete:

### Immich
- [ ] Test connection succeeds
- [ ] Server version displayed
- [ ] Photos appear in trip view
- [ ] Thumbnails load correctly
- [ ] Can click through to full photos

### Google Maps
- [ ] Test API key succeeds
- [ ] Can add accommodation with address
- [ ] Coordinates are populated
- [ ] (Future) Map displays location

### Airline APIs
- [ ] API key format validated
- [ ] Can update flight status
- [ ] Status, gate, terminal update
- [ ] Delays are reflected

### Email Integration
- [ ] OAuth apps configured
- [ ] Email account connected
- [ ] Test email creates trip
- [ ] Flight details extracted correctly
- [ ] Trip marked as auto-detected

---

## Feature Comparison

| Feature | Requires API | Admin Enable | User Config | Test Available |
|---------|--------------|--------------|-------------|----------------|
| Immich Photos | Yes | Yes | Yes | ✅ |
| Google Maps | Yes | Yes | Yes | ✅ |
| Airline Status | Yes | No | Yes | ⚠️ |
| Gmail Scan | Yes (OAuth) | Yes | Yes | Via Connection |
| Outlook Scan | Yes (OAuth) | Yes | Yes | Via Connection |

**Legend:**
- Admin Enable: Admin must enable feature for user
- User Config: User must configure their own credentials
- Test Available: ✅ Full test | ⚠️ Format validation only

---

## FAQ

**Q: Do I need all these integrations?**  
A: No! Only configure the ones you want to use.

**Q: Can I use the same API keys as other users?**  
A: No, each user must configure their own for security and privacy.

**Q: What if I don't have airline API access?**  
A: You can still use email scanning and manual entry. Real-time updates just won't work.

**Q: Are these free?**  
A: Immich is self-hosted (free). Google Maps has free tier. Airline APIs typically require partnerships.

**Q: Can admin see my API keys?**  
A: No, keys are encrypted and only accessible to you.

**Q: What happens if I remove an integration?**  
A: The feature stops working for you. Existing data is preserved.

**Q: Can I change API keys later?**  
A: Yes, update them anytime in API Integrations.

**Q: How do I know if it's working?**  
A: Use the test buttons and check the Settings dashboard for status.

---

## Getting Help

If you encounter issues:

1. **Check this guide** for your specific integration
2. **Use test buttons** to diagnose problems
3. **Review error messages** carefully
4. **Check Settings dashboard** for integration status
5. **Verify admin settings** (for admin-controlled features)
6. **Contact your administrator** for feature access issues

---

## What's Next?

After configuring your integrations:

1. ✅ Create your first trip
2. ✅ Add flights and accommodations
3. ✅ Let email scanning work automatically
4. ✅ Check for linked Immich photos
5. ✅ Update flight status in real-time

**Happy travels with fully-integrated trip tracking! 🌍✈️**
