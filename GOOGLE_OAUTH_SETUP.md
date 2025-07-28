# Google OAuth Setup Guide for Mimesis

## Overview
Mimesis now supports Google OAuth 2.0 authentication alongside traditional email/password login. This provides users with a secure, one-click sign-in option using their Google accounts.

## Features Added
- ✅ Google OAuth 2.0 authentication
- ✅ Automatic user profile creation from Google data
- ✅ Profile picture integration from Google
- ✅ Seamless login/registration flow
- ✅ Fallback to email/password authentication

## Setup Instructions

### 1. Create Google OAuth 2.0 Application

1. Go to [Google Cloud Console](https://console.developers.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google+ API" and enable it
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Choose "Web application"
   - Set authorized redirect URIs:
     - For development: `http://localhost:5000/google-login/callback`
     - For production: `https://yourdomain.com/google-login/callback`

### 2. Configure Environment Variables

Add these to your `.env` file:

```env
# Google OAuth Configuration
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
```

### 3. Database Schema Updated

The User model now includes:
- `google_id`: Unique Google OAuth identifier
- `profile_picture`: URL to user's Google profile picture
- `password_hash`: Now nullable (for OAuth users)

### 4. How It Works

#### For New Users:
1. User clicks "Sign in with Google"
2. Redirected to Google OAuth consent screen
3. User authorizes the application
4. Google returns user profile data
5. System creates new user account automatically
6. User is logged in and redirected to homepage

#### For Existing Users:
1. User clicks "Sign in with Google"
2. System checks if Google ID exists
3. If found, user is logged in immediately
4. If email exists but no Google ID, shows error message
5. User must use email/password login

### 5. Security Features

- ✅ Email verification required (Google handles this)
- ✅ Secure token exchange
- ✅ CSRF protection
- ✅ Session management
- ✅ Automatic logout on session expiry

### 6. User Experience

#### Login Page:
- Traditional email/password form
- "Or continue with" divider
- Google Sign-In button with official Google branding
- Responsive design for all devices

#### Registration Page:
- Same Google Sign-In option
- Automatic account creation
- No additional steps required

#### Profile Page:
- Shows Google profile picture if available
- Falls back to username initial avatar
- Displays user information from Google

### 7. Testing

1. **Without Google OAuth configured:**
   - Google button shows error message
   - Falls back to email/password authentication

2. **With Google OAuth configured:**
   - Test new user registration
   - Test existing user login
   - Verify profile picture display
   - Check style history persistence

### 8. Production Deployment

For production deployment:

1. Update redirect URIs in Google Console
2. Set environment variables on your hosting platform
3. Ensure HTTPS is enabled (required for OAuth)
4. Test the complete authentication flow

### 9. Troubleshooting

#### Common Issues:

**"Google OAuth is not configured"**
- Check if `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are set
- Verify environment variables are loaded correctly

**"User email not available or not verified"**
- User must have a verified Google account
- Check Google API permissions

**"An account with this email already exists"**
- User tried to sign in with Google but email already exists
- They must use email/password login instead

**Redirect URI mismatch**
- Ensure redirect URI in Google Console matches exactly
- Check for trailing slashes or protocol differences

### 10. Benefits

- **User Convenience**: One-click sign-in
- **Security**: Google's robust authentication
- **Profile Integration**: Automatic profile pictures
- **Reduced Friction**: Faster user onboarding
- **Trust**: Users trust Google's security

## Files Modified

- `models.py`: Added Google OAuth fields to User model
- `app.py`: Added Google OAuth configuration
- `routes.py`: Added Google OAuth routes
- `templates/login.html`: Added Google Sign-In button
- `templates/register.html`: Added Google Sign-In button
- `templates/profile.html`: Added profile picture support
- `requirements.txt`: Added Google OAuth dependencies

## Next Steps

1. Set up your Google OAuth application
2. Add credentials to `.env` file
3. Test the authentication flow
4. Deploy to production with proper HTTPS
5. Monitor authentication logs for any issues

The Google OAuth integration is now complete and ready for use! 🎉 