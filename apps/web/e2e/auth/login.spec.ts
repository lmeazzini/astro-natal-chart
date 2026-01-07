/**
 * Login E2E Tests
 *
 * Tests for the login functionality including:
 * - Valid login flow
 * - Invalid credentials handling
 * - Form validation
 * - Password visibility toggle
 * - Navigation to related pages
 */

import { test, expect } from '../fixtures/base.fixture';
import { TEST_USER, INVALID_USER } from '../fixtures/test-data';

test.describe('Login Page', () => {
  test.beforeEach(async ({ loginPage }) => {
    await loginPage.goto();
  });

  test.describe('Page Load', () => {
    test('should display login form', async ({ loginPage, page }) => {
      await loginPage.expectToBeOnLoginPage();

      // Check for essential form elements
      await expect(page.locator('input[type="email"]')).toBeVisible();
      await expect(page.locator('input[type="password"]')).toBeVisible();
      await expect(page.locator('button[type="submit"]')).toBeVisible();
    });

    test('should display logo and branding', async ({ page }) => {
      await expect(page.locator('img[alt*="Astrology"], img[src*="logo"]')).toBeVisible();
    });

    test('should have link to registration page', async ({ page }) => {
      await expect(page.locator('a[href="/register"]')).toBeVisible();
    });

    test('should have link to forgot password page', async ({ page }) => {
      await expect(page.locator('a[href="/forgot-password"]')).toBeVisible();
    });
  });

  test.describe('Form Validation', () => {
    test('should show error for empty email', async ({ loginPage }) => {
      await loginPage.fillPassword('somepassword');
      await loginPage.submit();

      // Should show validation error
      await loginPage.expectEmailError(/obrigatório|required/i);
    });

    test('should show error for invalid email format', async ({ loginPage }) => {
      await loginPage.fillEmail('invalid-email');
      await loginPage.fillPassword('somepassword');
      await loginPage.submit();

      // Should show email format error
      await loginPage.expectEmailError(/inválido|invalid|email/i);
    });

    test('should show error for empty password', async ({ loginPage }) => {
      await loginPage.fillEmail('test@example.com');
      await loginPage.submit();

      // Should show validation error
      await loginPage.expectPasswordError(/obrigatório|required/i);
    });
  });

  test.describe('Login Flow', () => {
    test('should login successfully with valid credentials', async ({ loginPage, page }) => {
      await loginPage.login(TEST_USER.email, TEST_USER.password);

      // Should redirect to dashboard
      await page.waitForURL('**/dashboard**', { timeout: 10000 });
      await expect(page).toHaveURL(/.*\/dashboard/);
    });

    test('should show error for invalid credentials', async ({ loginPage }) => {
      await loginPage.login(INVALID_USER.email, INVALID_USER.password);

      // Should show error message
      await loginPage.expectGeneralError(/inválido|invalid|incorret|senha|password|email/i);

      // Should stay on login page
      await loginPage.expectToBeOnLoginPage();
    });

    test('should show error for non-existent user', async ({ loginPage }) => {
      await loginPage.login('nonexistent@example.com', 'Password123!');

      // Should show error message
      await loginPage.expectGeneralError(/inválido|invalid|não encontrado|not found/i);
    });

    test('should show loading state during submission', async ({ loginPage, page }) => {
      await loginPage.fillEmail(TEST_USER.email);
      await loginPage.fillPassword(TEST_USER.password);
      await loginPage.submit();

      // Button should show loading state
      await expect(page.locator('button[type="submit"]')).toContainText(/carregando|loading/i);
    });
  });

  test.describe('Password Visibility', () => {
    test('should toggle password visibility', async ({ loginPage }) => {
      await loginPage.fillPassword('TestPassword123!');

      // Password should be hidden by default
      await loginPage.expectPasswordHidden();

      // Toggle visibility
      await loginPage.togglePasswordVisibility();

      // Password should now be visible
      await loginPage.expectPasswordVisible();
    });
  });

  test.describe('Navigation', () => {
    test('should navigate to register page', async ({ loginPage, page }) => {
      await loginPage.clickRegister();

      await expect(page).toHaveURL(/.*\/register/);
    });

    test('should navigate to forgot password page', async ({ loginPage, page }) => {
      await loginPage.clickForgotPassword();

      await expect(page).toHaveURL(/.*\/forgot-password/);
    });

    test('should navigate to home when clicking logo', async ({ page }) => {
      await page.locator('a').filter({ has: page.locator('img[alt*="Astrology"], img[src*="logo"]') }).first().click();

      await expect(page).toHaveURL(/^https?:\/\/[^/]+\/?$/);
    });
  });

  test.describe('Accessibility', () => {
    test('should have proper form labels', async ({ page }) => {
      // Email input should have label
      const emailLabel = page.locator('label').filter({ hasText: /email/i });
      await expect(emailLabel).toBeVisible();

      // Password input should have label
      const passwordLabel = page.locator('label').filter({ hasText: /senha|password/i });
      await expect(passwordLabel).toBeVisible();
    });

    test('should support keyboard navigation', async ({ page }) => {
      // Tab through form elements
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');

      // Should be able to submit with Enter
      await page.locator('input[type="email"]').fill(TEST_USER.email);
      await page.locator('input[type="password"]').fill(TEST_USER.password);
      await page.keyboard.press('Enter');

      // Should attempt submission
      await expect(page).toHaveURL(/.*\/(dashboard|login).*/);
    });
  });
});
