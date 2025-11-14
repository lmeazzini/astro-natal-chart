# OAuth2 Setup Guide

This guide explains how to configure OAuth2 social login for Google, GitHub, and Facebook.

## Overview

The application supports social authentication through three providers:
- **Google** - OAuth 2.0
- **GitHub** - OAuth 2.0
- **Facebook** - OAuth 2.0

Users can register and login using any of these providers. The system automatically:
- Creates new user accounts from OAuth provider data
- Links OAuth accounts to existing users by email
- Marks OAuth-authenticated emails as verified
- Allows users to connect multiple OAuth providers to one account

## Provider Configuration

### 1. Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to **APIs & Services** > **Credentials**
4. Click **Create Credentials** > **OAuth client ID**
5. Select **Web application** as application type
6. Configure:
   - **Name**: Astro Natal Chart
   - **Authorized JavaScript origins**: `http://localhost:5173`
   - **Authorized redirect URIs**: `http://localhost:8000/api/v1/oauth/callback/google`
7. Copy the **Client ID** and **Client Secret**
8. Add to your `.env` file:
   ```env
   GOOGLE_CLIENT_ID=your-google-client-id
   GOOGLE_CLIENT_SECRET=your-google-client-secret
   GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/oauth/callback/google
   ```

### 2. GitHub OAuth Setup

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click **New OAuth App**
3. Configure:
   - **Application name**: Astro Natal Chart
   - **Homepage URL**: `http://localhost:5173`
   - **Authorization callback URL**: `http://localhost:8000/api/v1/oauth/callback/github`
4. Click **Register application**
5. Copy the **Client ID**
6. Click **Generate a new client secret** and copy it
7. Add to your `.env` file:
   ```env
   GITHUB_CLIENT_ID=your-github-client-id
   GITHUB_CLIENT_SECRET=your-github-client-secret
   GITHUB_REDIRECT_URI=http://localhost:8000/api/v1/oauth/callback/github
   ```

### 3. Facebook OAuth Setup

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Click **My Apps** > **Create App**
3. Select **Consumer** as app type
4. Configure:
   - **App name**: Astro Natal Chart
   - **App contact email**: your-email@example.com
5. In the app dashboard, go to **Settings** > **Basic**
6. Copy the **App ID** and **App Secret**
7. Click **+ Add Platform** > **Website**
8. Set **Site URL**: `http://localhost:5173`
9. Go to **Facebook Login** > **Settings**
10. Add **Valid OAuth Redirect URIs**: `http://localhost:8000/api/v1/oauth/callback/facebook`
11. Make the app live (switch from Development to Live mode)
12. Add to your `.env` file:
    ```env
    FACEBOOK_CLIENT_ID=your-facebook-app-id
    FACEBOOK_CLIENT_SECRET=your-facebook-app-secret
    FACEBOOK_REDIRECT_URI=http://localhost:8000/api/v1/oauth/callback/facebook
    ```

## Testing OAuth2

After configuring at least one provider:

1. Start the backend server:
   ```bash
   cd apps/api
   uvicorn app.main:app --reload
   ```

2. Start the frontend:
   ```bash
   cd apps/web
   npm run dev
   ```

3. Navigate to the login or register page
4. You should see OAuth login buttons for configured providers
5. Click a provider button to test the OAuth flow

## Production Configuration

For production deployment, update the redirect URIs to match your production domain:

```env
# Production example
GOOGLE_REDIRECT_URI=https://yourdomain.com/api/v1/oauth/callback/google
GITHUB_REDIRECT_URI=https://yourdomain.com/api/v1/oauth/callback/github
FACEBOOK_REDIRECT_URI=https://yourdomain.com/api/v1/oauth/callback/facebook
```

**Important**: Also update the authorized origins/redirect URIs in each provider's dashboard to match your production URLs.

## Troubleshooting

### OAuth buttons not appearing
- Check that at least one provider has both CLIENT_ID and CLIENT_SECRET set
- Verify the API server is running and accessible
- Check browser console for errors

### "Invalid redirect URI" error
- Verify the redirect URI in your .env matches exactly what's configured in the provider dashboard
- Ensure there are no trailing slashes in URLs

### "Email not available" error
- Some providers require additional permissions to access email
- For GitHub, ensure the user has a public email or verified email
- For Facebook, ensure email permission is requested in app settings

### User created but not logged in
- Check that the frontend callback page is correctly parsing tokens from URL
- Verify tokens are being stored in localStorage
- Check browser console for JavaScript errors

## Security Notes

1. **Never commit** `.env` files with real credentials to version control
2. Use different OAuth apps for development and production
3. Regularly rotate OAuth client secrets
4. Monitor OAuth app usage in provider dashboards
5. Implement rate limiting on OAuth endpoints for production
6. Consider implementing OAuth state parameter for CSRF protection

## Additional Resources

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [GitHub OAuth Documentation](https://docs.github.com/en/developers/apps/building-oauth-apps)
- [Facebook Login Documentation](https://developers.facebook.com/docs/facebook-login)
- [Authlib Documentation](https://docs.authlib.org/en/latest/)
