/**
 * Base Page Object class.
 *
 * Provides common functionality for all page objects.
 */

import { type Page, type Locator, expect } from '@playwright/test';

export abstract class BasePage {
  constructor(protected page: Page) {}

  /**
   * Navigate to the page
   */
  abstract goto(): Promise<void>;

  /**
   * Wait for the page to be fully loaded
   */
  async waitForLoad(): Promise<void> {
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Get a visible alert with error styling
   */
  getErrorAlert(): Locator {
    return this.page.locator('[role="alert"]').filter({ hasText: /.+/ });
  }

  /**
   * Expect an error message to be visible
   */
  async expectError(message: string | RegExp): Promise<void> {
    await expect(this.page.getByText(message)).toBeVisible();
  }

  /**
   * Expect a success message to be visible
   */
  async expectSuccess(message: string | RegExp): Promise<void> {
    await expect(this.page.getByText(message)).toBeVisible();
  }

  /**
   * Wait for navigation to a specific URL pattern
   */
  async waitForUrl(pattern: string | RegExp): Promise<void> {
    await this.page.waitForURL(pattern);
  }

  /**
   * Get the current URL
   */
  getCurrentUrl(): string {
    return this.page.url();
  }

  /**
   * Take a screenshot for debugging
   */
  async screenshot(name: string): Promise<void> {
    await this.page.screenshot({ path: `e2e/screenshots/${name}.png` });
  }

  /**
   * Wait for a toast notification
   */
  async waitForToast(message?: string | RegExp): Promise<void> {
    const toast = this.page.locator('[data-sonner-toast], [role="status"]');
    await expect(toast).toBeVisible();
    if (message) {
      await expect(toast).toContainText(message);
    }
  }
}
