/**
 * OAuth service for social authentication
 */

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface OAuthProvider {
  name: string;
  display_name: string;
}

export const oauthService = {
  /**
   * Get list of available OAuth providers
   */
  async getProviders(): Promise<OAuthProvider[]> {
    const response = await fetch(`${API_URL}/api/v1/oauth/providers`);
    if (!response.ok) {
      throw new Error('Failed to fetch OAuth providers');
    }
    const data = await response.json();
    return data.providers || [];
  },

  /**
   * Initiate OAuth login with a provider
   * This will redirect the user to the OAuth provider's authorization page
   */
  initiateLogin(provider: string) {
    window.location.href = `${API_URL}/api/v1/oauth/login/${provider}`;
  },

  /**
   * Parse OAuth callback parameters from URL
   */
  parseCallbackParams(): { access_token?: string; refresh_token?: string } | null {
    const params = new URLSearchParams(window.location.search);
    const accessToken = params.get('access_token');
    const refreshToken = params.get('refresh_token');

    if (accessToken && refreshToken) {
      return {
        access_token: accessToken,
        refresh_token: refreshToken,
      };
    }

    return null;
  },
};
