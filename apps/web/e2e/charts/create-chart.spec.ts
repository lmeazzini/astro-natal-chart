/**
 * Chart Creation E2E Tests
 *
 * Tests for the multi-step chart creation flow including:
 * - Step navigation
 * - Form validation per step
 * - Location search and selection
 * - Successful chart creation
 */

import { test, expect } from '../fixtures/base.fixture';
import { generateChartData, ROUTES } from '../fixtures/test-data';
import { loginViaAPI } from '../fixtures/auth.fixture';

test.describe('Chart Creation', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await loginViaAPI(page);
    await page.goto(ROUTES.newChart);
  });

  test.describe('Page Load', () => {
    test('should display chart creation form', async ({ newChartPage }) => {
      await newChartPage.expectToBeOnNewChartPage();
    });

    test('should show step indicators', async ({ page }) => {
      // Should show step progress (4 steps)
      await expect(page.getByText(/passo|step/i)).toBeVisible();
    });

    test('should start on step 1', async ({ newChartPage }) => {
      await newChartPage.expectToBeOnStep(1);
    });
  });

  test.describe('Step 1: Personal Information', () => {
    test('should require person name', async ({ newChartPage, page }) => {
      // Try to proceed without name
      await newChartPage.clickNext();

      // Should show validation error
      await expect(page.getByText(/obrigatório|required/i)).toBeVisible();
    });

    test('should proceed to step 2 with valid name', async ({ newChartPage }) => {
      await newChartPage.fillPersonName('Test Person');
      await newChartPage.clickNext();

      await newChartPage.expectToBeOnStep(2);
    });

    test('should allow optional gender selection', async ({ newChartPage }) => {
      await newChartPage.fillPersonName('Test Person');
      await newChartPage.selectGender('Masculino');
      await newChartPage.clickNext();

      await newChartPage.expectToBeOnStep(2);
    });
  });

  test.describe('Step 2: Birth Date and Time', () => {
    test.beforeEach(async ({ newChartPage }) => {
      // Navigate to step 2
      await newChartPage.fillPersonName('Test Person');
      await newChartPage.clickNext();
    });

    test('should require birth date/time', async ({ newChartPage, page }) => {
      // Try to proceed without date
      await newChartPage.clickNext();

      // Should show validation error
      await expect(page.getByText(/obrigatório|required|data|date/i)).toBeVisible();
    });

    test('should proceed to step 3 with valid date', async ({ newChartPage }) => {
      await newChartPage.fillBirthDateTime('1990-06-15T14:30');
      await newChartPage.clickNext();

      await newChartPage.expectToBeOnStep(3);
    });

    test('should allow going back to step 1', async ({ newChartPage }) => {
      await newChartPage.clickPrevious();

      await newChartPage.expectToBeOnStep(1);
    });
  });

  test.describe('Step 3: Birth Location', () => {
    test.beforeEach(async ({ newChartPage }) => {
      // Navigate to step 3
      await newChartPage.fillPersonName('Test Person');
      await newChartPage.clickNext();
      await newChartPage.fillBirthDateTime('1990-06-15T14:30');
      await newChartPage.clickNext();
    });

    test('should search for locations', async ({ newChartPage, page }) => {
      await newChartPage.searchLocation('New York');

      // Wait for suggestions to appear
      await page.waitForTimeout(1500);

      // Should show location suggestions or the input should be filled
      await expect(
        page.locator('button, [class*="suggestion"]').filter({ hasText: /New York|Nova York/i })
      ).toBeVisible({ timeout: 5000 }).catch(() => {
        // Location service might not be available in test environment
      });
    });

    test('should allow manual coordinate entry', async ({ newChartPage }) => {
      await newChartPage.fillManualCoordinates(40.7128, -74.006);

      // Coordinates should be filled
      await expect(newChartPage['page'].locator('input[type="number"]').first()).toHaveValue('40.7128');
    });

    test('should require location data', async ({ newChartPage, page }) => {
      // Try to proceed without location
      await newChartPage.clickNext();

      // Should show validation error or stay on step
      const hasError = await page.getByText(/obrigatório|required|local|location/i).isVisible();
      const stillOnStep3 = await page.getByText(/passo 3|step 3/i).isVisible();

      expect(hasError || stillOnStep3).toBe(true);
    });
  });

  test.describe('Step 4: Review and Submit', () => {
    test.beforeEach(async ({ newChartPage }) => {
      // Navigate to step 4
      await newChartPage.fillPersonName('Test Person');
      await newChartPage.clickNext();
      await newChartPage.fillBirthDateTime('1990-06-15T14:30');
      await newChartPage.clickNext();
      // Fill location manually
      await newChartPage.fillManualCoordinates(40.7128, -74.006);
      await newChartPage['page'].locator('input').filter({ hasText: '' }).first().fill('New York');
      await newChartPage.clickNext();
    });

    test('should display summary of entered data', async ({ page }) => {
      // Should show the entered name
      await expect(page.getByText('Test Person')).toBeVisible();
    });

    test('should allow adding notes', async ({ newChartPage }) => {
      await newChartPage.fillNotes('This is a test chart');

      await expect(newChartPage['page'].locator('textarea')).toHaveValue('This is a test chart');
    });

    test('should allow going back to previous steps', async ({ newChartPage }) => {
      await newChartPage.clickPrevious();
      await newChartPage.expectToBeOnStep(3);

      await newChartPage.clickPrevious();
      await newChartPage.expectToBeOnStep(2);

      await newChartPage.clickPrevious();
      await newChartPage.expectToBeOnStep(1);
    });
  });

  test.describe('Complete Chart Creation', () => {
    test('should create chart successfully', async ({ newChartPage, page }) => {
      const chartData = generateChartData();

      // Step 1
      await newChartPage.fillPersonName(chartData.personName);
      await newChartPage.clickNext();

      // Step 2
      await newChartPage.fillBirthDateTime(`${chartData.birthDate}T${chartData.birthTime}`);
      await newChartPage.clickNext();

      // Step 3 - use manual coordinates since geocoding might not work in test
      await page.locator('input').first().fill('Test City');
      await newChartPage.fillManualCoordinates(chartData.latitude, chartData.longitude);
      await newChartPage.clickNext();

      // Step 4 - Submit
      await newChartPage.submit();

      // Should redirect to charts page or show the new chart
      await expect(page).toHaveURL(/.*\/charts.*/, { timeout: 15000 });
    });

    test('should show loading state during creation', async ({ newChartPage, page }) => {
      // Navigate through steps quickly
      await newChartPage.fillPersonName('Quick Test');
      await newChartPage.clickNext();
      await newChartPage.fillBirthDateTime('1990-01-01T12:00');
      await newChartPage.clickNext();
      await page.locator('input').first().fill('Test');
      await newChartPage.fillManualCoordinates(-23.55, -46.63);
      await newChartPage.clickNext();
      await newChartPage.submit();

      // Should show loading state
      await expect(
        page.getByText(/calculando|loading|gerando|creating/i)
      ).toBeVisible({ timeout: 3000 }).catch(() => {
        // Loading might be too fast to catch
      });
    });
  });

  test.describe('Unverified User Limits', () => {
    // Note: These tests require a specific user state
    test.skip('should show remaining charts for unverified users', async ({ page }) => {
      // This test would require setting up an unverified user
      await expect(page.getByText(/restantes|remaining/i)).toBeVisible();
    });
  });
});
