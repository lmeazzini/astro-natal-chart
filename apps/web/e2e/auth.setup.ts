/**
 * Authentication setup for Playwright tests.
 *
 * This file runs before all tests to set up authentication state.
 * Tests that need authentication can depend on this setup.
 */

import { test as setup, expect } from '@playwright/test';
import { TEST_USER, STORAGE_KEYS, ROUTES } from './fixtures/test-data';

const authFile = 'playwright/.auth/user.json';

setup('authenticate', async ({ page }) => {
  // Navigate to login page
  await page.goto(ROUTES.login);

  // Fill login form
  await page.fill('input[type="email"]', TEST_USER.email);
  await page.fill('input[type="password"]', TEST_USER.password);
  await page.click('button[type="submit"]');

  // Wait for successful login (redirect to dashboard)
  await expect(page).toHaveURL(/.*\/dashboard/, { timeout: 30000 });

  // Verify tokens are stored
  const hasToken = await page.evaluate((key) => {
    return !!localStorage.getItem(key);
  }, STORAGE_KEYS.accessToken);

  expect(hasToken).toBeTruthy();

  // Save auth state to file
  await page.context().storageState({ path: authFile });
});
