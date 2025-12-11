# Email Integration Setup Guide

## Overview

Travel Tracker now uses **per-user OAuth applications** for email integration. This means each user creates their own Google/Microsoft OAuth apps instead of using system-wide credentials.

## Why Per-User OAuth?

### Benefits
- ✅ **Privacy**: Your OAuth credentials belong only to you
- ✅ **Security**: No shared credentials across users
- ✅ **Control**: You manage your own app permissions
- ✅ **Flexibility**: Different users can use different OAuth apps
- ✅ **Scalability**: No API rate limit conflicts between users

### How It Works
1. **You create** a Google/Microsoft OAuth app (one-time, 5 minutes)
2. **You configure** the app credentials in Travel Tracker
3. **You connect** your Gmail/Outlook account
4. **Travel Tracker scans** your emails automatically

## Quick Start

### Step 1: Navigate to OAuth Apps
1. Log in to Travel Tracker
2. Go to **Settings** → **OAuth Apps**
3. Follow the in-app guide

### Step 2: Create Your OAuth App

#### For Gmail Integration

**A. Create Google Cloud Project**
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click "Select a project" → "New Project"
3. Name: "Travel Tracker"
4. Click "Create"

**B. Enable Gmail API**
1. Open hamburger menu (☰) → "APIs & Services" → "Library"
2. Search: "Gmail API"
3. Click "Enable"

**C. Configure OAuth Consent Screen**
1. "APIs & Services" → "OAuth consent screen"
2. Select "External" → "Create"
3. Fill in:
   - App name: Travel Tracker
   - User support email: Your email
   - Developer contact: Your email
4. Click "Save and Continue"
5. On "Scopes" page:
   - Click "Add or Remove Scopes"
   - Find and select: `https://www.googleapis.com/auth/gmail.readonly`
   - Click "Update" → "Save and Continue"
6. On "Test users" page:
   - Add your email address
   - Click "Save and Continue"

**D. Create OAuth Credentials**
1. "APIs & Services" → "Credentials"
2. "Create Credentials" → "OAuth client ID"
3. Application type: "Web application"
4. Name: "Travel Tracker Web"
5. Under "Authorized redirect URIs", add:
   ```
   https://your-domain.com/auth/google/callback
   ```
   (Copy exact URL from Travel Tracker settings page)
6. Click "Create"
7. **Copy the Client ID and Client Secret**
8. Paste into Travel Tracker OAuth Apps page

#### For Outlook Integration

**A. Register Application**
1. Go to [Azure App Registrations](https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationsListBlade)
2. Click "New registration"
3. Fill in:
   - Name: Travel Tracker
   - Supported account types: "Accounts in any organizational directory and personal Microsoft accounts"
   - Redirect URI: Select "Web" and enter:
     ```
     https://your-domain.com/auth/microsoft/callback
     ```
     (Copy exact URL from Travel Tracker settings page)
4. Click "Register"

**B. Copy Application ID**
1. On the app's Overview page
2. Copy the **Application (client) ID**
3. This is your **Client ID**

**C. Create Client Secret**
1. Left menu → "Certificates & secrets"
2. "New client secret"
3. Description: "Travel Tracker Secret"
4. Expires: 24 months (or longer)
5. Click "Add"
6. **IMPORTANT**: Copy the **Value** immediately (not the Secret ID)
7. This is your **Client Secret**

**D. Configure API Permissions**
1. Left menu → "API permissions"
2. "Add a permission" → "Microsoft Graph"
3. "Delegated permissions"
4. Find and check:
   - `Mail.Read`
   - `offline_access`
5. Click "Add permissions"

### Step 3: Configure in Travel Tracker

1. Go to **Settings** → **OAuth Apps**
2. Paste your credentials:
   - Google: Client ID + Client Secret
   - Microsoft: Client ID + Client Secret
3. Click "Save"

### Step 4: Connect Your Email

1. Go to **Settings** → **Email Accounts**
2. Click "Connect Gmail" or "Connect Outlook"
3. Authorize the connection
4. Done! Email scanning starts automatically

## Troubleshooting

### "OAuth app not configured" Error

**Problem**: You haven't set up your OAuth app credentials yet.

**Solution**: Go to Settings → OAuth Apps and follow the setup guide.

### "Authentication failed" Error

**Problem**: Invalid credentials or incorrect redirect URI.

**Solutions**:
1. Verify you copied the **entire** Client ID and Secret
2. Check redirect URI in Google/Azure matches exactly
3. Make sure you enabled the Gmail API (Google) or Mail.Read permission (Microsoft)
4. For Google: Add yourself as a test user

### Email Scanning Not Working

**Problem**: No trips are being created automatically.

**Checklist**:
1. ✅ Admin enabled "Email Integration" for your account
2. ✅ You configured OAuth app credentials
3. ✅ You connected your email account
4. ✅ You have "Auto scan emails" enabled in Preferences
5. ✅ Flight confirmation emails exist in your inbox

**How to test**:
1. Forward a flight confirmation to yourself
2. Wait 5 minutes (scan interval)
3. Check dashboard for auto-detected trips

### Token Expired Error

**Problem**: OAuth token needs refresh.

**Solution**: This should happen automatically, but if it doesn't:
1. Go to Settings → Email Accounts
2. Disconnect your email
3. Reconnect it

### Google "App Not Verified" Warning

**Problem**: Google shows a warning during OAuth.

**Solution**: 
1. This is normal for apps in testing mode
2. Click "Advanced" → "Go to Travel Tracker (unsafe)"
3. Your app is safe - Google just hasn't verified it
4. To remove warning: Submit app for verification (optional)

## Security & Privacy

### What Access Does Travel Tracker Have?

**Gmail**:
- ✅ Read-only access to your emails
- ❌ Cannot send emails
- ❌ Cannot delete emails
- ❌ Cannot modify emails

**Outlook**:
- ✅ Read-only access to your emails
- ❌ Cannot send emails
- ❌ Cannot delete emails
- ❌ Cannot modify emails

### What Data Is Stored?

**Stored**:
- ✅ Your OAuth tokens (encrypted)
- ✅ Extracted flight information
- ✅ Trip details

**NOT Stored**:
- ❌ Your email content
- ❌ Email attachments
- ❌ Other people's emails
- ❌ Non-flight-related information

### How to Revoke Access

**Option 1: Disconnect in Travel Tracker**
1. Settings → Email Accounts
2. Click "Disconnect"

**Option 2: Revoke in Google/Microsoft**

**Google**:
1. [Google Account Security](https://myaccount.google.com/permissions)
2. Find "Travel Tracker"
3. Click "Remove Access"

**Microsoft**:
1. [Microsoft Account Apps](https://account.live.com/consent/Manage)
2. Find "Travel Tracker"
3. Click "Remove"

## Advanced Configuration

### Multiple Email Accounts

You can connect both Gmail and Outlook:
1. Set up OAuth apps for both providers
2. Connect each email account separately
3. Both will be scanned automatically

### Custom Redirect URIs

If you're running Travel Tracker on a custom domain:
1. Update redirect URI in Google Cloud Console / Azure Portal
2. Format: `https://your-domain.com/auth/google/callback`
3. Must match exactly (including https://)

### API Rate Limits

Each user's OAuth app has separate rate limits:
- **Gmail**: 250 quota units per user per second
- **Outlook**: 10,000 requests per 10 minutes

With default scanning (every 5 minutes), you won't hit limits.

## FAQs

**Q: Do I need both Gmail and Outlook?**  
A: No, only set up the ones you use.

**Q: Can I use someone else's OAuth app?**  
A: No, each user must create their own for security and privacy.

**Q: What if I change my email password?**  
A: OAuth tokens are separate - no action needed.

**Q: How long does setup take?**  
A: About 5 minutes per email provider (one-time).

**Q: Is this safe?**  
A: Yes. OAuth is the industry-standard secure authentication method used by all major apps.

**Q: Can the admin see my emails?**  
A: No. Your OAuth credentials are yours only. Admins can't access your emails.

**Q: What if my OAuth credentials leak?**  
A: 1) Immediately revoke access in Google/Azure, 2) Delete the OAuth app, 3) Create a new one.

## Support

For issues:
1. Check this guide
2. Review error messages
3. Verify all setup steps completed
4. Check Settings → Email Accounts for status
5. Contact your administrator

## Updates

This per-user OAuth system was introduced to improve privacy and security. If you had email integration before this update, you'll need to:
1. Set up your own OAuth app
2. Reconnect your email account

Your existing trips and data are not affected.

---

**Happy travels with automatic trip imports! 🌍✈️**
