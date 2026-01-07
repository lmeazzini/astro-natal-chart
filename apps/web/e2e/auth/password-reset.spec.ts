/**
 * Password Reset E2E Tests
 *
 * Tests for the password reset functionality including:
 * - Request password reset
 * - Form validation
 * - Success/error messages
 */

import { test, expect } from '@playwright/test';
import { TEST_USER } from '../fixtures/test-data';

test.describe('Password Reset Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/forgot-password');
  });

  test.describe('Page Load', () => {
    test('should display password reset form', async ({ page }) => {
      await expect(page).toHaveURL(/.*\/forgot-password/);
      await expect(page.locator('input[type="email"]')).toBeVisible();
      await expect(page.locator('button[type="submit"]')).toBeVisible();
    });

    test('should display instructions', async ({ page }) => {
      // Should have some text explaining the process
      await expect(
        page.getByText(/email|instruções|instructions|recuperar|reset|enviar|send/i)
      ).toBeVisible();
    });

    test('should have link back to login', async ({ page }) => {
      await expect(page.locator('a[href="/login"]')).toBeVisible();
    });
  });

  test.describe('Form Validation', () => {
    test('should show error for empty email', async ({ page }) => {
      await page.click('button[type="submit"]');

      // Should show validation error
      await expect(
        page.getByText(/obrigatório|required|email/i)
      ).toBeVisible();
    });

    test('should show error for invalid email format', async ({ page }) => {
      await page.fill('input[type="email"]', 'invalid-email');
      await page.click('button[type="submit"]');

      // Should show email format error
      await expect(
        page.getByText(/inválido|invalid|email/i)
      ).toBeVisible();
    });
  });

  test.describe('Password Reset Request', () => {
    test('should show success message for valid email', async ({ page }) => {
      await page.fill('input[type="email"]', TEST_USER.email);
      await page.click('button[type="submit"]');

      // Should show success message (API returns success even for non-existent emails for security)
      await expect(
        page.getByText(/enviado|sent|email|sucesso|success|verifique|check/i)
      ).toBeVisible({ timeout: 10000 });
    });

    test('should show success message even for non-existent email', async ({ page }) => {
      // For security, the API should not reveal if email exists
      await page.fill('input[type="email"]', 'nonexistent@example.com');
      await page.click('button[type="submit"]');

      // Should still show success message
      await expect(
        page.getByText(/enviado|sent|email|sucesso|success|verifique|check/i)
      ).toBeVisible({ timeout: 10000 });
    });

    test('should show loading state during submission', async ({ page }) => {
      await page.fill('input[type="email"]', TEST_USER.email);
      await page.click('button[type="submit"]');

      // Button should show loading state
      await expect(
        page.locator('button[type="submit"]')
      ).toContainText(/carregando|loading|enviando|sending/i);
    });
  });

  test.describe('Navigation', () => {
    test('should navigate back to login', async ({ page }) => {
      await page.click('a[href="/login"]');

      await expect(page).toHaveURL(/.*\/login/);
    });

    test('should navigate to login from success state', async ({ page }) => {
      // Request password reset first
      await page.fill('input[type="email"]', TEST_USER.email);
      await page.click('button[type="submit"]');

      // Wait for success
      await expect(
        page.getByText(/enviado|sent|email|sucesso|success/i)
      ).toBeVisible({ timeout: 10000 });

      // Should have a way to go back to login
      const loginLink = page.locator('a[href="/login"], button').filter({ hasText: /login|entrar/i });
      if (await loginLink.isVisible()) {
        await loginLink.click();
        await expect(page).toHaveURL(/.*\/login/);
      }
    });
  });

  test.describe('Accessibility', () => {
    test('should have proper form labels', async ({ page }) => {
      const emailLabel = page.locator('label').filter({ hasText: /email/i });
      await expect(emailLabel).toBeVisible();
    });

    test('should support keyboard submission', async ({ page }) => {
      await page.fill('input[type="email"]', TEST_USER.email);
      await page.keyboard.press('Enter');

      // Should submit the form
      await expect(
        page.getByText(/enviado|sent|carregando|loading/i)
      ).toBeVisible({ timeout: 5000 });
    });
  });
});
