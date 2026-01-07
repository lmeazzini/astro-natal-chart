/**
 * Registration E2E Tests
 *
 * Tests for the registration functionality including:
 * - Valid registration flow
 * - Form validation (password requirements, email format)
 * - Terms acceptance
 * - Navigation to related pages
 */

import { test, expect } from '../fixtures/base.fixture';
import { generateTestEmail, generateTestPassword, TEST_USER } from '../fixtures/test-data';

test.describe('Registration Page', () => {
  test.beforeEach(async ({ registerPage }) => {
    await registerPage.goto();
  });

  test.describe('Page Load', () => {
    test('should display registration form', async ({ registerPage, page }) => {
      await registerPage.expectToBeOnRegisterPage();

      // Check for essential form elements
      await expect(page.locator('input[type="email"]')).toBeVisible();
      await expect(page.locator('input[autocomplete="name"]')).toBeVisible();
      await expect(page.locator('input[autocomplete="new-password"]').first()).toBeVisible();
      await expect(page.locator('[role="checkbox"]')).toBeVisible();
      await expect(page.locator('button[type="submit"]')).toBeVisible();
    });

    test('should display password requirements', async ({ page }) => {
      // Should show password requirements info
      await expect(page.getByText(/8.*caracteres|8.*characters/i)).toBeVisible();
    });

    test('should have link to login page', async ({ page }) => {
      await expect(page.locator('a[href="/login"]')).toBeVisible();
    });

    test('should have links to terms and privacy policy', async ({ page }) => {
      await expect(page.locator('a[href="/terms"]')).toBeVisible();
      await expect(page.locator('a[href="/privacy"]')).toBeVisible();
    });
  });

  test.describe('Form Validation', () => {
    test('should show error for empty email', async ({ registerPage }) => {
      await registerPage.fillName('Test User');
      await registerPage.fillPassword(generateTestPassword());
      await registerPage.fillConfirmPassword(generateTestPassword());
      await registerPage.acceptTerms();
      await registerPage.submit();

      await registerPage.expectEmailError(/obrigatório|required/i);
    });

    test('should show error for invalid email format', async ({ registerPage }) => {
      await registerPage.fillEmail('invalid-email');
      await registerPage.fillName('Test User');
      await registerPage.fillPassword(generateTestPassword());
      await registerPage.fillConfirmPassword(generateTestPassword());
      await registerPage.acceptTerms();
      await registerPage.submit();

      await registerPage.expectEmailError(/inválido|invalid|email/i);
    });

    test('should show error for short password', async ({ registerPage }) => {
      await registerPage.fillEmail(generateTestEmail());
      await registerPage.fillName('Test User');
      await registerPage.fillPassword('Short1!');
      await registerPage.fillConfirmPassword('Short1!');
      await registerPage.acceptTerms();
      await registerPage.submit();

      await registerPage.expectPasswordError(/mínimo|minimum|8.*caracteres|8.*characters/i);
    });

    test('should show error for password without uppercase', async ({ registerPage }) => {
      await registerPage.fillEmail(generateTestEmail());
      await registerPage.fillName('Test User');
      await registerPage.fillPassword('password123!');
      await registerPage.fillConfirmPassword('password123!');
      await registerPage.acceptTerms();
      await registerPage.submit();

      await registerPage.expectPasswordError(/maiúscula|uppercase/i);
    });

    test('should show error for password without lowercase', async ({ registerPage }) => {
      await registerPage.fillEmail(generateTestEmail());
      await registerPage.fillName('Test User');
      await registerPage.fillPassword('PASSWORD123!');
      await registerPage.fillConfirmPassword('PASSWORD123!');
      await registerPage.acceptTerms();
      await registerPage.submit();

      await registerPage.expectPasswordError(/minúscula|lowercase/i);
    });

    test('should show error for password without number', async ({ registerPage }) => {
      await registerPage.fillEmail(generateTestEmail());
      await registerPage.fillName('Test User');
      await registerPage.fillPassword('Password!@#');
      await registerPage.fillConfirmPassword('Password!@#');
      await registerPage.acceptTerms();
      await registerPage.submit();

      await registerPage.expectPasswordError(/número|number|digit/i);
    });

    test('should show error for password without special character', async ({ registerPage }) => {
      await registerPage.fillEmail(generateTestEmail());
      await registerPage.fillName('Test User');
      await registerPage.fillPassword('Password123');
      await registerPage.fillConfirmPassword('Password123');
      await registerPage.acceptTerms();
      await registerPage.submit();

      await registerPage.expectPasswordError(/especial|special/i);
    });

    test('should show error for mismatched passwords', async ({ registerPage }) => {
      await registerPage.fillEmail(generateTestEmail());
      await registerPage.fillName('Test User');
      await registerPage.fillPassword(generateTestPassword());
      await registerPage.fillConfirmPassword('DifferentPassword123!');
      await registerPage.acceptTerms();
      await registerPage.submit();

      await registerPage.expectPasswordError(/coincidem|match/i);
    });

    test('should show error for unaccepted terms', async ({ registerPage }) => {
      await registerPage.fillEmail(generateTestEmail());
      await registerPage.fillName('Test User');
      const password = generateTestPassword();
      await registerPage.fillPassword(password);
      await registerPage.fillConfirmPassword(password);
      // Don't accept terms
      await registerPage.submit();

      await registerPage.expectTermsError(/aceitar|accept|termos|terms/i);
    });

    test('should show error for short name', async ({ registerPage }) => {
      await registerPage.fillEmail(generateTestEmail());
      await registerPage.fillName('AB');
      const password = generateTestPassword();
      await registerPage.fillPassword(password);
      await registerPage.fillConfirmPassword(password);
      await registerPage.acceptTerms();
      await registerPage.submit();

      // Should show name validation error (min 3 characters)
      await expect(registerPage['page'].getByText(/mínimo|minimum|3.*caracteres|3.*characters/i)).toBeVisible();
    });
  });

  test.describe('Registration Flow', () => {
    test('should register successfully with valid data', async ({ registerPage, page }) => {
      const email = generateTestEmail();
      const password = generateTestPassword();

      await registerPage.register(email, 'Test User E2E', password);

      // Should redirect to dashboard after successful registration
      await page.waitForURL('**/dashboard**', { timeout: 15000 });
      await expect(page).toHaveURL(/.*\/dashboard/);
    });

    test('should show error for existing email', async ({ registerPage }) => {
      // Try to register with an email that already exists
      await registerPage.register(
        TEST_USER.email,
        'Test User',
        generateTestPassword()
      );

      // Should show error about existing user
      await registerPage.expectGeneralError(/já existe|already exists|cadastrado|registered/i);
    });

    test('should show loading state during submission', async ({ registerPage, page }) => {
      const email = generateTestEmail();
      const password = generateTestPassword();

      await registerPage.fillEmail(email);
      await registerPage.fillName('Test User');
      await registerPage.fillPassword(password);
      await registerPage.fillConfirmPassword(password);
      await registerPage.acceptTerms();
      await registerPage.submit();

      // Button should show loading state briefly
      await expect(page.locator('button[type="submit"]')).toContainText(/carregando|loading/i);
    });
  });

  test.describe('Terms Checkbox', () => {
    test('should toggle terms checkbox', async ({ registerPage }) => {
      await registerPage.expectTermsUnchecked();

      await registerPage.acceptTerms();

      await registerPage.expectTermsChecked();
    });
  });

  test.describe('Navigation', () => {
    test('should navigate to login page', async ({ registerPage, page }) => {
      await registerPage.clickLogin();

      await expect(page).toHaveURL(/.*\/login/);
    });

    test('should open terms page in new tab', async ({ registerPage, context }) => {
      // Listen for new page (tab)
      const pagePromise = context.waitForEvent('page');

      await registerPage.clickTerms();

      const newPage = await pagePromise;
      await newPage.waitForLoadState();

      await expect(newPage).toHaveURL(/.*\/terms/);
    });

    test('should open privacy page in new tab', async ({ registerPage, context }) => {
      // Listen for new page (tab)
      const pagePromise = context.waitForEvent('page');

      await registerPage.clickPrivacy();

      const newPage = await pagePromise;
      await newPage.waitForLoadState();

      await expect(newPage).toHaveURL(/.*\/privacy/);
    });
  });

  test.describe('Accessibility', () => {
    test('should have proper form labels', async ({ page }) => {
      // Check for labels
      await expect(page.locator('label').filter({ hasText: /email/i })).toBeVisible();
      await expect(page.locator('label').filter({ hasText: /nome|name/i })).toBeVisible();
      await expect(page.locator('label').filter({ hasText: /senha|password/i }).first()).toBeVisible();
    });
  });
});
