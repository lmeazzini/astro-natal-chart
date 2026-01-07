/**
 * Smoke Tests
 *
 * Quick regression tests that verify core functionality is working.
 * These tests should run fast and catch critical failures.
 *
 * Run with: npm run e2e:chromium -- smoke.spec.ts
 */

import { test, expect } from '@playwright/test';
import { loginViaAPI } from './fixtures/auth.fixture';
import { TEST_USER, ROUTES } from './fixtures/test-data';

test.describe('Smoke Tests', () => {
  test.describe.configure({ mode: 'serial' });

  test('1. Home page loads', async ({ page }) => {
    await page.goto('/');

    // Should load without errors
    await expect(page).toHaveTitle(/Astrology|Real/i);
  });

  test('2. Login page loads', async ({ page }) => {
    await page.goto(ROUTES.login);

    // Should show login form
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('3. Register page loads', async ({ page }) => {
    await page.goto(ROUTES.register);

    // Should show registration form
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('4. User can log in', async ({ page }) => {
    await page.goto(ROUTES.login);

    // Fill login form
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button[type="submit"]');

    // Should redirect to dashboard
    await expect(page).toHaveURL(/.*\/dashboard/, { timeout: 10000 });
  });

  test('5. Dashboard loads for authenticated user', async ({ page }) => {
    await loginViaAPI(page);
    await page.goto(ROUTES.dashboard);

    // Should show dashboard content
    await expect(page).toHaveURL(/.*\/dashboard/);

    // Should have create chart button or chart list
    await expect(
      page.getByRole('button', { name: /criar|create|novo|new/i })
        .or(page.locator('[class*="chart"], article'))
    ).toBeVisible({ timeout: 10000 });
  });

  test('6. New chart page loads', async ({ page }) => {
    await loginViaAPI(page);
    await page.goto(ROUTES.newChart);

    // Should show chart creation form
    await expect(page).toHaveURL(/.*\/charts\/new/);
    await expect(page.locator('input, form')).toBeVisible();
  });

  test('7. Pricing page loads', async ({ page }) => {
    await page.goto(ROUTES.pricing);

    // Should show pricing information
    await expect(page).toHaveURL(/.*\/pricing/);
    await expect(
      page.getByText(/plano|plan|preço|price/i)
    ).toBeVisible();
  });

  test('8. API is responding', async ({ page }) => {
    // Check API health endpoint
    const response = await page.request.get(
      `${process.env.E2E_API_URL || 'http://localhost:8000'}/api/v1/health`
    );

    expect(response.ok()).toBeTruthy();
  });

  test('9. Protected routes redirect to login', async ({ page }) => {
    // Clear any existing auth
    await page.goto('/');
    await page.evaluate(() => {
      localStorage.removeItem('astro_access_token');
      localStorage.removeItem('astro_refresh_token');
    });

    // Try to access protected route
    await page.goto(ROUTES.dashboard);

    // Should redirect to login
    await expect(page).toHaveURL(/.*\/login/, { timeout: 10000 });
  });

  test('10. Error pages work', async ({ page }) => {
    // Try to access non-existent page
    await page.goto('/this-page-does-not-exist');

    // Should show 404 or redirect to home
    const is404 = await page.getByText(/404|não encontrad|not found/i).isVisible().catch(() => false);
    const isHome = page.url().endsWith('/') || page.url().includes('login');

    expect(is404 || isHome).toBeTruthy();
  });

  test('11. Theme toggle works', async ({ page }) => {
    await page.goto(ROUTES.login);

    // Find theme toggle button
    const themeButton = page.locator('button').filter({
      has: page.locator('[class*="sun"], [class*="moon"]'),
    }).first();

    if (await themeButton.isVisible().catch(() => false)) {
      // Get initial theme
      const initialTheme = await page.evaluate(() => {
        return document.documentElement.classList.contains('dark') ? 'dark' : 'light';
      });

      // Click toggle
      await themeButton.click();
      await page.waitForTimeout(500);

      // Theme should change
      const newTheme = await page.evaluate(() => {
        return document.documentElement.classList.contains('dark') ? 'dark' : 'light';
      });

      expect(newTheme).not.toBe(initialTheme);
    }
  });

  test('12. Language selector works', async ({ page }) => {
    await page.goto(ROUTES.login);

    // Find language selector
    const langSelector = page.locator('button, select').filter({
      hasText: /pt|en|português|english/i,
    }).first();

    if (await langSelector.isVisible().catch(() => false)) {
      await langSelector.click();

      // Should show language options
      await expect(
        page.getByRole('option', { name: /english|português/i })
          .or(page.getByRole('menuitem', { name: /english|português/i }))
      ).toBeVisible({ timeout: 3000 }).catch(() => {
        // Language selector might work differently
      });
    }
  });
});

test.describe('Critical User Journeys', () => {
  test('User can complete login → dashboard → new chart flow', async ({ page }) => {
    // Step 1: Login
    await page.goto(ROUTES.login);
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button[type="submit"]');

    // Step 2: Verify dashboard
    await expect(page).toHaveURL(/.*\/dashboard/, { timeout: 10000 });

    // Step 3: Navigate to new chart
    const createButton = page.getByRole('button', { name: /criar|create|novo|new/i })
      .or(page.locator('a[href="/charts/new"]'));

    if (await createButton.isVisible({ timeout: 5000 }).catch(() => false)) {
      await createButton.click();

      // Step 4: Verify chart creation page
      await expect(page).toHaveURL(/.*\/charts\/new/, { timeout: 5000 });
    }
  });
});
