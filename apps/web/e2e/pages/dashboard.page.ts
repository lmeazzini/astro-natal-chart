/**
 * Dashboard Page Object Model.
 */

import { type Page, expect } from '@playwright/test';
import { BasePage } from './base.page';
import { ROUTES } from '../fixtures/test-data';

export class DashboardPage extends BasePage {
  constructor(page: Page) {
    super(page);
  }

  // Locators
  private get createChartButton() {
    return this.page.locator('a[href="/charts/new"], button').filter({ hasText: /criar|create|novo|new/i }).first();
  }

  private get chartList() {
    return this.page.locator('[data-testid="chart-list"], .chart-list, main').first();
  }

  private get userMenu() {
    return this.page.locator('[data-testid="user-menu"], button').filter({ has: this.page.locator('svg') }).first();
  }

  private get logoutButton() {
    return this.page.getByRole('menuitem', { name: /sair|logout/i });
  }

  private get settingsLink() {
    return this.page.locator('a[href="/settings"]');
  }

  private get emptyState() {
    return this.page.locator('[data-testid="empty-state"]').or(
      this.page.getByText(/nenhum mapa|no charts|comece criando|start creating/i)
    );
  }

  // Actions
  async goto(): Promise<void> {
    await this.page.goto(ROUTES.dashboard);
    await this.waitForLoad();
  }

  async clickCreateChart(): Promise<void> {
    await this.createChartButton.click();
  }

  async openUserMenu(): Promise<void> {
    await this.userMenu.click();
  }

  async logout(): Promise<void> {
    await this.openUserMenu();
    await this.logoutButton.click();
  }

  async goToSettings(): Promise<void> {
    await this.settingsLink.click();
  }

  async clickChart(name: string): Promise<void> {
    await this.page.getByText(name).click();
  }

  async getChartCards() {
    return this.page.locator('[data-testid="chart-card"], .chart-card, article').all();
  }

  // Assertions
  async expectToBeOnDashboard(): Promise<void> {
    await expect(this.page).toHaveURL(/.*\/dashboard/);
  }

  async expectChartVisible(name: string): Promise<void> {
    await expect(this.page.getByText(name)).toBeVisible();
  }

  async expectChartNotVisible(name: string): Promise<void> {
    await expect(this.page.getByText(name)).not.toBeVisible();
  }

  async expectEmptyState(): Promise<void> {
    await expect(this.emptyState).toBeVisible();
  }

  async expectChartsLoaded(): Promise<void> {
    // Wait for either charts or empty state
    await expect(
      this.chartList.or(this.emptyState)
    ).toBeVisible({ timeout: 10000 });
  }

  async expectChartCount(count: number): Promise<void> {
    const cards = await this.getChartCards();
    expect(cards.length).toBe(count);
  }

  async expectCreateButtonVisible(): Promise<void> {
    await expect(this.createChartButton).toBeVisible();
  }
}
