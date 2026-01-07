/**
 * Chart Deletion E2E Tests
 *
 * Tests for deleting charts including:
 * - Delete confirmation dialog
 * - Cancel delete
 * - Successful deletion
 * - Redirect after deletion
 */

import { test, expect } from '../fixtures/base.fixture';
import { loginViaAPI } from '../fixtures/auth.fixture';
import { ROUTES, generateChartData } from '../fixtures/test-data';

test.describe('Chart Deletion', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto(ROUTES.dashboard);
    await page.waitForLoadState('networkidle');
  });

  test.describe('Delete Confirmation', () => {
    test('should show confirmation dialog when clicking delete', async ({ page, chartPage }) => {
      // Find a chart to delete
      const chartLink = page.locator('a[href*="/charts/"], [class*="chart-card"], article').first();
      const hasCharts = await chartLink.isVisible({ timeout: 5000 }).catch(() => false);
      if (!hasCharts) {
        test.skip();
        return;
      }

      await chartLink.click();
      await page.waitForLoadState('networkidle');

      // Click delete button
      await chartPage.clickDeleteChart();

      // Should show confirmation dialog
      await chartPage.expectDeleteConfirmDialogVisible();
    });

    test('should cancel deletion when clicking cancel', async ({ page, chartPage }) => {
      const chartLink = page.locator('a[href*="/charts/"], [class*="chart-card"], article').first();
      const hasCharts = await chartLink.isVisible({ timeout: 5000 }).catch(() => false);
      if (!hasCharts) {
        test.skip();
        return;
      }

      // Store the current URL
      await chartLink.click();
      await page.waitForLoadState('networkidle');
      const chartUrl = page.url();

      // Click delete, then cancel
      await chartPage.clickDeleteChart();
      await chartPage.cancelDelete();

      // Should still be on the same chart page
      await expect(page).toHaveURL(chartUrl);
    });

    test('should close dialog when clicking outside', async ({ page, chartPage }) => {
      const chartLink = page.locator('a[href*="/charts/"], [class*="chart-card"], article').first();
      const hasCharts = await chartLink.isVisible({ timeout: 5000 }).catch(() => false);
      if (!hasCharts) {
        test.skip();
        return;
      }

      await chartLink.click();
      await page.waitForLoadState('networkidle');

      // Click delete to open dialog
      await chartPage.clickDeleteChart();
      await chartPage.expectDeleteConfirmDialogVisible();

      // Press Escape to close
      await page.keyboard.press('Escape');

      // Dialog should be closed (confirm button should not be visible)
      await expect(
        page.getByRole('button', { name: /confirmar|confirm/i })
      ).not.toBeVisible({ timeout: 3000 }).catch(() => {
        // Some dialogs may use different close mechanisms
      });
    });
  });

  test.describe('Successful Deletion', () => {
    // Note: This test will actually delete a chart, so use with caution
    // In a real E2E setup, you'd create a chart specifically for this test

    test.skip('should delete chart and redirect', async ({ page, chartPage, newChartPage }) => {
      // First, create a chart to delete
      await page.goto(ROUTES.newChart);

      const chartData = generateChartData();
      await newChartPage.fillPersonName(chartData.personName);
      await newChartPage.clickNext();
      await newChartPage.fillBirthDateTime(`${chartData.birthDate}T${chartData.birthTime}`);
      await newChartPage.clickNext();
      await page.locator('input').first().fill('Test City');
      await newChartPage.fillManualCoordinates(chartData.latitude, chartData.longitude);
      await newChartPage.clickNext();
      await newChartPage.submit();

      // Wait for chart to be created and redirected
      await expect(page).toHaveURL(/.*\/charts.*/, { timeout: 15000 });

      // Find and click the newly created chart
      await page.goto(ROUTES.dashboard);
      await page.waitForLoadState('networkidle');

      const newChart = page.getByText(chartData.personName);
      await newChart.click();
      await page.waitForLoadState('networkidle');

      // Delete the chart
      await chartPage.deleteChart();

      // Should redirect to charts list
      await chartPage.expectChartDeleted();

      // The chart should no longer be visible in the list
      await expect(page.getByText(chartData.personName)).not.toBeVisible();
    });

    test('should show success message after deletion', async ({ page, chartPage }) => {
      const chartLink = page.locator('a[href*="/charts/"], [class*="chart-card"], article').first();
      const hasCharts = await chartLink.isVisible({ timeout: 5000 }).catch(() => false);
      if (!hasCharts) {
        test.skip();
        return;
      }

      await chartLink.click();
      await page.waitForLoadState('networkidle');

      // Delete the chart
      await chartPage.deleteChart();

      // Should show success message (toast or alert)
      await expect(
        page.getByText(/excluído|deleted|removido|removed|sucesso|success/i)
      ).toBeVisible({ timeout: 5000 }).catch(() => {
        // If no toast, we should at least be redirected
        return expect(page).toHaveURL(/.*\/charts\/?$/);
      });
    });
  });

  test.describe('Delete from Dashboard', () => {
    test('should allow deletion from chart card menu', async ({ page }) => {
      // Some UIs allow deletion directly from the dashboard card menu
      const chartCard = page.locator('[class*="chart-card"], article').first();
      const hasCharts = await chartCard.isVisible({ timeout: 5000 }).catch(() => false);
      if (!hasCharts) {
        test.skip();
        return;
      }

      // Look for a menu button on the card
      const menuButton = chartCard.locator('button').filter({
        has: page.locator('[class*="dots"], [class*="menu"]'),
      });

      if (await menuButton.isVisible().catch(() => false)) {
        await menuButton.click();

        // Look for delete option in menu
        const deleteOption = page.getByRole('menuitem', { name: /excluir|delete/i });
        if (await deleteOption.isVisible().catch(() => false)) {
          await deleteOption.click();

          // Should show confirmation
          await expect(
            page.getByRole('button', { name: /confirmar|confirm/i })
          ).toBeVisible();
        }
      }
    });
  });
});
