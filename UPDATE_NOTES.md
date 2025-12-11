# Update Notes - Per-User OAuth Integration

## Version 1.1.0 - December 2024

### Major Changes

#### 🔐 Per-User OAuth Applications

**What Changed**: Email integration now uses per-user OAuth applications instead of system-wide credentials.

**Why**: 
- Better privacy and security
- Users control their own OAuth apps
- No shared rate limits
- Easier to set up for new users

**Action Required**: Users need to set up their own OAuth apps

### New Features

1. **OAuth App Configuration Page**
   - In-app setup guide for Google and Microsoft OAuth
   - Step-by-step instructions with copy-paste URLs
   - No need to reference external documentation

2. **Email Accounts Management**
   - Visual setup progress tracker
   - Easy connect/disconnect buttons
   - Status indicators for connected accounts

3. **Enhanced Security**
   - OAuth credentials stored per-user in database
   - Encrypted at rest
   - Separate token refresh per user

## Migration Guide

### For Administrators

#### Before the Update

If your system was using system-wide OAuth credentials:
```env
GOOGLE_CLIENT_ID=system-wide-id
GOOGLE_CLIENT_SECRET=system-wide-secret
MICROSOFT_CLIENT_ID=system-wide-id
MICROSOFT_CLIENT_SECRET=system-wide-secret
```

#### After the Update

1. **Database Migration**
   ```bash
   docker-compose exec web flask db upgrade
   ```
   This adds new columns to `user_settings` table:
   - `google_client_id`
   - `google_client_secret`
   - `microsoft_client_id`
   - `microsoft_client_secret`

2. **User Communication**
   Send this message to users:
   ```
   Subject: Action Required - Email Integration Update
   
   We've updated Travel Tracker's email integration to be more secure 
   and private. You now create your own OAuth apps instead of using 
   shared credentials.
   
   To continue using email integration:
   1. Go to Settings → OAuth Apps
   2. Follow the 5-minute setup guide
   3. Reconnect your email account
   
   Your existing trips and data are safe - only email connection needs 
   to be reset.
   
   Questions? Check the EMAIL_INTEGRATION_GUIDE.md
   ```

3. **System-Wide Credentials**
   - You can remove these from `.env` (optional)
   - They're no longer used
   - Keep for backward compatibility if needed

### For Users

#### What You Need to Do

1. **Set Up OAuth Apps** (one-time, 5 minutes)
   - Go to Settings → OAuth Apps
   - Follow the in-app guide for Gmail and/or Outlook
   - Copy your Client ID and Secret into Travel Tracker

2. **Reconnect Email** (30 seconds)
   - Go to Settings → Email Accounts
   - Click "Connect Gmail" or "Connect Outlook"
   - Authorize the connection

3. **Verify** (check your dashboard)
   - Email scanning resumes automatically
   - New trips appear as before

#### Your Data

- ✅ All existing trips are safe
- ✅ All flight information is preserved
- ✅ Shared trips still work
- ⚠️ Only email connection needs to be re-established

## Technical Details

### Database Changes

**New columns in `user_settings`:**
```python
google_client_id = db.Column(db.String(255))
google_client_secret = db.Column(db.String(255))
microsoft_client_id = db.Column(db.String(255))
microsoft_client_secret = db.Column(db.String(255))
```

**New methods in `UserSettings`:**
- `has_google_oauth()` - Check if Google OAuth configured
- `has_microsoft_oauth()` - Check if Microsoft OAuth configured

### API Changes

**Modified routes:**
- `GET /auth/google` - Now requires login, uses user's credentials
- `GET /auth/google/callback` - Now requires login, saves to user's account
- `GET /auth/microsoft` - Now requires login, uses user's credentials
- `GET /auth/microsoft/callback` - Now requires login, saves to user's account

**New routes:**
- `GET/POST /settings/oauth-apps` - OAuth app configuration
- `GET /settings/email-accounts` - Email account management
- `POST /settings/email-accounts/<id>/disconnect` - Disconnect email

### Security Improvements

1. **Credential Isolation**: Each user's OAuth credentials are separate
2. **Token Refresh**: Uses per-user credentials for token refresh
3. **Access Control**: Users can only manage their own OAuth apps
4. **Revocation**: Disconnecting removes only that user's access

### Backward Compatibility

The system still supports system-wide OAuth credentials as fallback, but they're deprecated. All new installations should use per-user OAuth.

## Testing Checklist

### For Developers

- [ ] Database migration completes successfully
- [ ] OAuth Apps page loads
- [ ] Google OAuth setup guide displays correctly
- [ ] Microsoft OAuth setup guide displays correctly
- [ ] Can save Google credentials
- [ ] Can save Microsoft credentials
- [ ] Email Accounts page loads
- [ ] Can connect Gmail with user's credentials
- [ ] Can connect Outlook with user's credentials
- [ ] Email scanning works with per-user credentials
- [ ] Token refresh uses per-user credentials
- [ ] Can disconnect email accounts
- [ ] Multiple users can have different OAuth apps

### For Users

- [ ] Can navigate to OAuth Apps page
- [ ] In-app guide is clear and helpful
- [ ] Can copy redirect URIs easily
- [ ] Can save credentials successfully
- [ ] Can connect email account
- [ ] Email scanning starts automatically
- [ ] Trips are created from emails
- [ ] Can disconnect email account

## Rollback Plan

If you need to rollback:

1. **Keep Database Changes**: The new columns won't break anything
2. **Revert Code**: Use previous version
3. **Re-enable System OAuth**: Add credentials back to `.env`
4. **User Action**: Users keep their connected accounts

## Support

### Common Issues

**Issue**: "OAuth app not configured"
- **Solution**: User needs to set up OAuth apps first

**Issue**: "Authentication failed"
- **Solution**: Check redirect URI matches exactly

**Issue**: Email scanning stopped
- **Solution**: Reconnect email after OAuth app setup

### Getting Help

1. Check `EMAIL_INTEGRATION_GUIDE.md`
2. Review error messages
3. Verify setup steps completed
4. Check application logs

## Future Enhancements

Planned improvements:
- [ ] OAuth app validation before saving
- [ ] Test connection button
- [ ] Automatic OAuth app setup wizard
- [ ] Import/export OAuth credentials (encrypted)
- [ ] OAuth app rotation reminders

## Files Changed

**Modified:**
- `models.py` - Added OAuth credential columns
- `auth.py` - Updated OAuth flows for per-user credentials
- `app.py` - Added OAuth app management routes
- `utils.py` - Updated token refresh for per-user credentials

**New:**
- `templates/settings/oauth_apps.html` - OAuth app setup page
- `templates/settings/email_accounts.html` - Email account management
- `EMAIL_INTEGRATION_GUIDE.md` - Complete setup guide

**Updated:**
- `templates/settings/index.html` - Added navigation links

## Release Notes

### Version 1.1.0

**Release Date**: December 2024

**Breaking Changes**:
- Email integration now requires per-user OAuth apps
- Existing email connections need to be re-established

**New Features**:
- In-app OAuth setup guide
- Per-user OAuth credential storage
- Email account management page
- Setup progress tracker

**Security**:
- Improved credential isolation
- Enhanced privacy protection
- Better access control

**Documentation**:
- Complete email integration guide
- Step-by-step setup instructions
- Troubleshooting section

**Upgrade Path**:
1. Deploy new version
2. Run database migrations
3. Notify users to set up OAuth apps
4. Users reconnect email accounts

---

**Questions?** Check `EMAIL_INTEGRATION_GUIDE.md` for detailed setup instructions.
