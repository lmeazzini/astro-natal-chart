/**
 * API client configuration with automatic token refresh
 */

import i18n from '../i18n';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Token storage keys
const TOKEN_KEY = 'astro_access_token';
const REFRESH_TOKEN_KEY = 'astro_refresh_token';

export interface ApiError {
  detail: string | { msg: string; type: string }[];
}

interface RequestOptions extends RequestInit {
  skipRefresh?: boolean;
}

// Token management utilities
export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function setRefreshToken(token: string): void {
  localStorage.setItem(REFRESH_TOKEN_KEY, token);
}

export function clearTokens(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

// Event for notifying components about auth state changes
export const authEvents = {
  listeners: new Set<() => void>(),
  subscribe(callback: () => void): () => void {
    this.listeners.add(callback);
    return () => {
      this.listeners.delete(callback);
    };
  },
  notifyLogout() {
    this.listeners.forEach((callback) => callback());
  },
};

class ApiClient {
  private baseURL: string;
  private isRefreshing = false;
  private refreshSubscribers: ((token: string) => void)[] = [];

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  /**
   * Subscribe to wait for token refresh to complete
   */
  private subscribeToRefresh(callback: (token: string) => void): void {
    this.refreshSubscribers.push(callback);
  }

  /**
   * Notify all subscribers with the new token
   */
  private onRefreshSuccess(token: string): void {
    this.refreshSubscribers.forEach((callback) => callback(token));
    this.refreshSubscribers = [];
  }

  /**
   * Attempt to refresh the access token using the refresh token
   */
  private async refreshAccessToken(): Promise<string | null> {
    const refreshToken = getRefreshToken();

    if (!refreshToken) {
      return null;
    }

    try {
      const response = await fetch(`${this.baseURL}/api/v1/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (!response.ok) {
        return null;
      }

      const data = await response.json();

      if (data.access_token) {
        setToken(data.access_token);
        if (data.refresh_token) {
          setRefreshToken(data.refresh_token);
        }
        console.log('[Auth] Token refreshed successfully via API client');
        return data.access_token;
      }

      return null;
    } catch (error) {
      console.error('[Auth] Token refresh failed:', error);
      return null;
    }
  }

  /**
   * Handle 401 Unauthorized responses by attempting token refresh
   */
  private async handleUnauthorized<T>(
    endpoint: string,
    options: RequestOptions
  ): Promise<T> {
    // Prevent multiple simultaneous refresh attempts
    if (!this.isRefreshing) {
      this.isRefreshing = true;

      try {
        const newToken = await this.refreshAccessToken();

        if (newToken) {
          this.isRefreshing = false;
          this.onRefreshSuccess(newToken);

          // Retry original request with new token
          return this.request<T>(endpoint, { ...options, skipRefresh: true });
        } else {
          // Refresh failed - clear tokens and notify logout
          this.isRefreshing = false;
          clearTokens();
          authEvents.notifyLogout();
          throw new Error('Session expired. Please log in again.');
        }
      } catch (error) {
        this.isRefreshing = false;
        clearTokens();
        authEvents.notifyLogout();
        throw error;
      }
    } else {
      // Wait for ongoing refresh to complete
      return new Promise<T>((resolve, reject) => {
        this.subscribeToRefresh((newToken: string) => {
          // Retry request with new token
          const newOptions: RequestOptions = {
            ...options,
            skipRefresh: true,
            headers: {
              ...options.headers,
              Authorization: `Bearer ${newToken}`,
            },
          };

          this.request<T>(endpoint, newOptions).then(resolve).catch(reject);
        });
      });
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestOptions = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const token = getToken();
    const { skipRefresh, ...fetchOptions } = options;

    const config: RequestInit = {
      ...fetchOptions,
      headers: {
        'Content-Type': 'application/json',
        'Accept-Language': i18n.language || 'pt-BR',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...fetchOptions.headers,
      },
    };

    try {
      const response = await fetch(url, config);

      // Check for new token in response header (auto-refresh from middleware)
      const newToken = response.headers.get('X-New-Access-Token');
      if (newToken) {
        setToken(newToken);
        console.log('[Auth] Token auto-refreshed via middleware header');
      }

      // Handle 401 Unauthorized - attempt token refresh
      if (response.status === 401 && !skipRefresh && token) {
        return this.handleUnauthorized<T>(endpoint, options);
      }

      if (!response.ok) {
        const error: ApiError = await response.json();
        throw new Error(
          typeof error.detail === 'string'
            ? error.detail
            : error.detail[0]?.msg || 'Request error'
        );
      }

      // Handle 204 No Content
      if (response.status === 204) {
        return undefined as T;
      }

      return await response.json();
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Unknown request error');
    }
  }

  async get<T>(endpoint: string, token?: string): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'GET',
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
  }

  async post<T>(endpoint: string, data?: unknown, token?: string): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async put<T>(endpoint: string, data: unknown, token?: string): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: JSON.stringify(data),
    });
  }

  async patch<T>(endpoint: string, data: unknown, token?: string): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PATCH',
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: JSON.stringify(data),
    });
  }

  async delete<T>(endpoint: string, token?: string): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'DELETE',
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
  }
}

export const apiClient = new ApiClient(API_BASE_URL);
