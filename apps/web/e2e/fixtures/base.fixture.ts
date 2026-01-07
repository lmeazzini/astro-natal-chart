/**
 * Base test fixture that extends Playwright's test with custom fixtures.
 *
 * Usage:
 * ```ts
 * import { test, expect } from '../fixtures/base.fixture';
 *
 * test('my test', async ({ page, loginPage }) => {
 *   // ...
 * });
 * ```
 */

import { test as base, expect } from '@playwright/test';
import { LoginPage } from '../pages/login.page';
import { RegisterPage } from '../pages/register.page';
import { DashboardPage } from '../pages/dashboard.page';
import { NewChartPage } from '../pages/new-chart.page';
import { ChartPage } from '../pages/chart.page';
import { PricingPage } from '../pages/pricing.page';
import { loginViaAPI, logout, ensureLoggedOut } from './auth.fixture';
import { TEST_USER } from './test-data';

/**
 * Custom fixtures for E2E tests
 */
type CustomFixtures = {
  // Page Objects
  loginPage: LoginPage;
  registerPage: RegisterPage;
  dashboardPage: DashboardPage;
  newChartPage: NewChartPage;
  chartPage: ChartPage;
  pricingPage: PricingPage;

  // Auth helpers
  authenticatedPage: void;
  unauthenticatedPage: void;
};

/**
 * Extended test with custom fixtures
 */
export const test = base.extend<CustomFixtures>({
  // Page Object fixtures
  loginPage: async ({ page }, use) => {
    const loginPage = new LoginPage(page);
    await use(loginPage);
  },

  registerPage: async ({ page }, use) => {
    const registerPage = new RegisterPage(page);
    await use(registerPage);
  },

  dashboardPage: async ({ page }, use) => {
    const dashboardPage = new DashboardPage(page);
    await use(dashboardPage);
  },

  newChartPage: async ({ page }, use) => {
    const newChartPage = new NewChartPage(page);
    await use(newChartPage);
  },

  chartPage: async ({ page }, use) => {
    const chartPage = new ChartPage(page);
    await use(chartPage);
  },

  pricingPage: async ({ page }, use) => {
    const pricingPage = new PricingPage(page);
    await use(pricingPage);
  },

  // Auth state fixtures
  authenticatedPage: async ({ page }, use) => {
    // Login before test
    await loginViaAPI(page, TEST_USER.email, TEST_USER.password);
    await use();
    // Logout after test
    await logout(page);
  },

  unauthenticatedPage: async ({ page }, use) => {
    // Ensure logged out before test
    await ensureLoggedOut(page);
    await use();
  },
});

export { expect };
