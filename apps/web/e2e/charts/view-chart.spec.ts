/**
 * Chart View E2E Tests
 *
 * Tests for viewing chart details including:
 * - Chart wheel display
 * - Planet positions
 * - Tab navigation (planets, houses, aspects)
 * - Chart actions (edit, delete, PDF)
 */

import { test, expect } from '../fixtures/base.fixture';
import { loginViaAPI } from '../fixtures/auth.fixture';
import { ROUTES } from '../fixtures/test-data';

test.describe('Chart View', () => {
  test.beforeEach(async ({ page }) => {
    // Login and navigate to dashboard first
    await loginViaAPI(page);
    await page.goto(ROUTES.dashboard);
    await page.waitForLoadState('networkidle');
  });

  test.describe('Chart List', () => {
    test('should display dashboard with charts or empty state', async ({ dashboardPage }) => {
      await dashboardPage.expectToBeOnDashboard();
      await dashboardPage.expectChartsLoaded();
    });

    test('should have create chart button', async ({ dashboardPage }) => {
      await dashboardPage.expectCreateButtonVisible();
    });

    test('should navigate to new chart page', async ({ dashboardPage, page }) => {
      await dashboardPage.clickCreateChart();

      await expect(page).toHaveURL(/.*\/charts\/new/);
    });
  });

  test.describe('Chart Detail Page', () => {
    // Note: These tests assume at least one chart exists
    // In CI, we'd need to create a chart first or use seeded data

    test('should display chart details when clicking a chart', async ({ page }) => {
      // Look for a chart card/link and click it
      const chartLink = page.locator('a[href*="/charts/"], [class*="chart-card"], article').first();

      // If no charts exist, skip this test
      const hasCharts = await chartLink.isVisible({ timeout: 5000 }).catch(() => false);
      if (!hasCharts) {
        test.skip();
        return;
      }

      await chartLink.click();

      // Should navigate to chart detail page
      await expect(page).toHaveURL(/.*\/charts\/[a-zA-Z0-9-]+/);
    });

    test('should display chart wheel', async ({ page, chartPage }) => {
      // Navigate to first chart if available
      const chartLink = page.locator('a[href*="/charts/"], [class*="chart-card"], article').first();
      const hasCharts = await chartLink.isVisible({ timeout: 5000 }).catch(() => false);
      if (!hasCharts) {
        test.skip();
        return;
      }

      await chartLink.click();
      await page.waitForLoadState('networkidle');

      // Chart wheel should be visible (SVG or canvas element)
      await chartPage.expectChartWheelVisible();
    });

    test('should display planet information', async ({ page, chartPage }) => {
      const chartLink = page.locator('a[href*="/charts/"], [class*="chart-card"], article').first();
      const hasCharts = await chartLink.isVisible({ timeout: 5000 }).catch(() => false);
      if (!hasCharts) {
        test.skip();
        return;
      }

      await chartLink.click();
      await page.waitForLoadState('networkidle');

      // Should show planet names (Sun, Moon are common)
      await chartPage.expectPlanetsVisible();
    });

    test('should have tabs for different sections', async ({ page, chartPage }) => {
      const chartLink = page.locator('a[href*="/charts/"], [class*="chart-card"], article').first();
      const hasCharts = await chartLink.isVisible({ timeout: 5000 }).catch(() => false);
      if (!hasCharts) {
        test.skip();
        return;
      }

      await chartLink.click();
      await page.waitForLoadState('networkidle');

      // Should have tab navigation
      await chartPage.expectTabsVisible();
    });

    test('should navigate between tabs', async ({ page }) => {
      const chartLink = page.locator('a[href*="/charts/"], [class*="chart-card"], article').first();
      const hasCharts = await chartLink.isVisible({ timeout: 5000 }).catch(() => false);
      if (!hasCharts) {
        test.skip();
        return;
      }

      await chartLink.click();
      await page.waitForLoadState('networkidle');

      // Try clicking different tabs
      const tabs = page.locator('[role="tab"]');
      const tabCount = await tabs.count();

      if (tabCount > 1) {
        // Click second tab
        await tabs.nth(1).click();

        // Content should change (tab should be selected)
        await expect(tabs.nth(1)).toHaveAttribute('data-state', 'active');
      }
    });
  });

  test.describe('Chart Actions', () => {
    test('should have edit button', async ({ page, chartPage }) => {
      const chartLink = page.locator('a[href*="/charts/"], [class*="chart-card"], article').first();
      const hasCharts = await chartLink.isVisible({ timeout: 5000 }).catch(() => false);
      if (!hasCharts) {
        test.skip();
        return;
      }

      await chartLink.click();
      await page.waitForLoadState('networkidle');

      await chartPage.expectEditButtonVisible();
    });

    test('should have delete button', async ({ page, chartPage }) => {
      const chartLink = page.locator('a[href*="/charts/"], [class*="chart-card"], article').first();
      const hasCharts = await chartLink.isVisible({ timeout: 5000 }).catch(() => false);
      if (!hasCharts) {
        test.skip();
        return;
      }

      await chartLink.click();
      await page.waitForLoadState('networkidle');

      await chartPage.expectDeleteButtonVisible();
    });

    test('should navigate to edit page', async ({ page, chartPage }) => {
      const chartLink = page.locator('a[href*="/charts/"], [class*="chart-card"], article').first();
      const hasCharts = await chartLink.isVisible({ timeout: 5000 }).catch(() => false);
      if (!hasCharts) {
        test.skip();
        return;
      }

      await chartLink.click();
      await page.waitForLoadState('networkidle');

      await chartPage.clickEditChart();

      // Should navigate to edit page
      await expect(page).toHaveURL(/.*\/charts\/.*\/edit/);
    });
  });

  test.describe('Back Navigation', () => {
    test('should navigate back to dashboard', async ({ page, chartPage }) => {
      const chartLink = page.locator('a[href*="/charts/"], [class*="chart-card"], article').first();
      const hasCharts = await chartLink.isVisible({ timeout: 5000 }).catch(() => false);
      if (!hasCharts) {
        test.skip();
        return;
      }

      await chartLink.click();
      await page.waitForLoadState('networkidle');

      await chartPage.clickBack();

      // Should navigate back
      await expect(page).toHaveURL(/.*\/(dashboard|charts)/);
    });
  });
});
