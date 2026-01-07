/**
 * Authentication fixtures for E2E tests.
 *
 * Provides helpers for logging in, logging out, and managing auth state.
 */

import { type Page, expect } from '@playwright/test';
import { TEST_USER, STORAGE_KEYS, ROUTES } from './test-data';

const API_BASE_URL = process.env.E2E_API_URL || 'http://localhost:8000';

/**
 * Login via the UI (slower but tests the full flow)
 */
export async function loginViaUI(
  page: Page,
  email: string = TEST_USER.email,
  password: string = TEST_USER.password
): Promise<void> {
  await page.goto(ROUTES.login);

  // Fill login form
  await page.fill('input[type="email"]', email);
  await page.fill('input[type="password"]', password);

  // Submit and wait for navigation
  await Promise.all([
    page.waitForURL('**/dashboard**'),
    page.click('button[type="submit"]'),
  ]);
}

/**
 * Login via API and set tokens directly (faster for authenticated tests)
 */
export async function loginViaAPI(
  page: Page,
  email: string = TEST_USER.email,
  password: string = TEST_USER.password
): Promise<{ accessToken: string; refreshToken: string }> {
  // Make API request to get tokens
  const response = await page.request.post(`${API_BASE_URL}/api/v1/auth/login`, {
    form: {
      username: email,
      password: password,
    },
  });

  if (!response.ok()) {
    throw new Error(`Login failed: ${response.status()} ${await response.text()}`);
  }

  const data = await response.json();
  const accessToken = data.access_token;
  const refreshToken = data.refresh_token;

  // Set tokens in localStorage
  await page.goto('/');
  await page.evaluate(
    ({ accessToken, refreshToken, keys }) => {
      localStorage.setItem(keys.accessToken, accessToken);
      localStorage.setItem(keys.refreshToken, refreshToken);
    },
    { accessToken, refreshToken, keys: STORAGE_KEYS }
  );

  // Reload to apply auth state
  await page.reload();

  return { accessToken, refreshToken };
}

/**
 * Set auth tokens directly in localStorage (for pre-obtained tokens)
 */
export async function setAuthTokens(
  page: Page,
  accessToken: string,
  refreshToken: string
): Promise<void> {
  await page.goto('/');
  await page.evaluate(
    ({ accessToken, refreshToken, keys }) => {
      localStorage.setItem(keys.accessToken, accessToken);
      localStorage.setItem(keys.refreshToken, refreshToken);
    },
    { accessToken, refreshToken, keys: STORAGE_KEYS }
  );
  await page.reload();
}

/**
 * Logout and clear auth state
 */
export async function logout(page: Page): Promise<void> {
  await page.evaluate((keys) => {
    localStorage.removeItem(keys.accessToken);
    localStorage.removeItem(keys.refreshToken);
  }, STORAGE_KEYS);

  await page.reload();
}

/**
 * Check if the user is currently logged in
 */
export async function isLoggedIn(page: Page): Promise<boolean> {
  const hasToken = await page.evaluate((keys) => {
    return !!localStorage.getItem(keys.accessToken);
  }, STORAGE_KEYS);

  return hasToken;
}

/**
 * Wait for authentication to be ready (tokens set and user data loaded)
 */
export async function waitForAuth(page: Page): Promise<void> {
  // Wait for the dashboard or authenticated content to load
  await expect(page.locator('[data-testid="user-menu"], .user-menu, nav')).toBeVisible({
    timeout: 10000,
  });
}

/**
 * Ensure user is logged out before test
 */
export async function ensureLoggedOut(page: Page): Promise<void> {
  await page.goto('/');
  await page.evaluate((keys) => {
    localStorage.removeItem(keys.accessToken);
    localStorage.removeItem(keys.refreshToken);
  }, STORAGE_KEYS);
}

/**
 * Create a new test user via API (for registration tests)
 */
export async function createTestUser(
  page: Page,
  email: string,
  password: string,
  name: string = 'Test User'
): Promise<void> {
  const response = await page.request.post(`${API_BASE_URL}/api/v1/auth/register`, {
    data: {
      email,
      password,
      full_name: name,
      accepted_terms: true,
    },
  });

  if (!response.ok() && response.status() !== 409) {
    // 409 = user already exists, which is fine
    throw new Error(`Failed to create test user: ${response.status()} ${await response.text()}`);
  }
}
