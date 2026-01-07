/**
 * Chart Detail Page Object Model.
 */

import { type Page, expect } from '@playwright/test';
import { BasePage } from './base.page';

export class ChartPage extends BasePage {
  constructor(page: Page) {
    super(page);
  }

  // Locators
  private get chartTitle() {
    return this.page.locator('h1, h2').first();
  }

  private get chartWheel() {
    return this.page.locator('svg, canvas, [class*="chart-wheel"], [class*="ChartWheel"]').first();
  }

  private get planetsList() {
    return this.page.locator('[class*="planet"], [data-testid="planets-list"]');
  }

  private get aspectsGrid() {
    return this.page.locator('[class*="aspect"], [data-testid="aspects-grid"]');
  }

  private get tabList() {
    return this.page.locator('[role="tablist"]');
  }

  private get editButton() {
    return this.page.getByRole('button', { name: /editar|edit/i });
  }

  private get deleteButton() {
    return this.page.getByRole('button', { name: /excluir|delete|remover|remove/i });
  }

  private get generatePdfButton() {
    return this.page.getByRole('button', { name: /pdf|download|baixar/i });
  }

  private get backButton() {
    return this.page.locator('a, button').filter({ hasText: /voltar|back/i });
  }

  private get shareButton() {
    return this.page.getByRole('button', { name: /compartilhar|share/i });
  }

  private get deleteConfirmButton() {
    return this.page.getByRole('button', { name: /confirmar|confirm|sim|yes/i });
  }

  private get deleteCancelButton() {
    return this.page.getByRole('button', { name: /cancelar|cancel|não|no/i });
  }

  // Tab buttons
  private get overviewTab() {
    return this.page.getByRole('tab', { name: /visão geral|overview|resumo/i });
  }

  private get planetsTab() {
    return this.page.getByRole('tab', { name: /planetas|planets/i });
  }

  private get housesTab() {
    return this.page.getByRole('tab', { name: /casas|houses/i });
  }

  private get aspectsTab() {
    return this.page.getByRole('tab', { name: /aspectos|aspects/i });
  }

  // Actions
  async goto(chartId: string): Promise<void> {
    await this.page.goto(`/charts/${chartId}`);
    await this.waitForLoad();
  }

  async clickEditChart(): Promise<void> {
    await this.editButton.click();
  }

  async clickDeleteChart(): Promise<void> {
    await this.deleteButton.click();
  }

  async confirmDelete(): Promise<void> {
    await this.deleteConfirmButton.click();
  }

  async cancelDelete(): Promise<void> {
    await this.deleteCancelButton.click();
  }

  async deleteChart(): Promise<void> {
    await this.clickDeleteChart();
    await this.confirmDelete();
  }

  async clickGeneratePdf(): Promise<void> {
    await this.generatePdfButton.click();
  }

  async clickShareChart(): Promise<void> {
    await this.shareButton.click();
  }

  async clickBack(): Promise<void> {
    await this.backButton.click();
  }

  // Tab navigation
  async clickOverviewTab(): Promise<void> {
    await this.overviewTab.click();
  }

  async clickPlanetsTab(): Promise<void> {
    await this.planetsTab.click();
  }

  async clickHousesTab(): Promise<void> {
    await this.housesTab.click();
  }

  async clickAspectsTab(): Promise<void> {
    await this.aspectsTab.click();
  }

  // Assertions
  async expectToBeOnChartPage(): Promise<void> {
    await expect(this.page).toHaveURL(/.*\/charts\/.*/);
  }

  async expectChartTitle(title: string | RegExp): Promise<void> {
    await expect(this.chartTitle).toContainText(title);
  }

  async expectChartWheelVisible(): Promise<void> {
    await expect(this.chartWheel).toBeVisible({ timeout: 10000 });
  }

  async expectPlanetsVisible(): Promise<void> {
    // Look for common planet names
    const sunMoon = this.page.getByText(/sol|sun|lua|moon/i);
    await expect(sunMoon.first()).toBeVisible();
  }

  async expectTabsVisible(): Promise<void> {
    await expect(this.tabList).toBeVisible();
  }

  async expectEditButtonVisible(): Promise<void> {
    await expect(this.editButton).toBeVisible();
  }

  async expectDeleteButtonVisible(): Promise<void> {
    await expect(this.deleteButton).toBeVisible();
  }

  async expectDeleteConfirmDialogVisible(): Promise<void> {
    await expect(this.deleteConfirmButton).toBeVisible();
    await expect(this.deleteCancelButton).toBeVisible();
  }

  async expectChartDeleted(): Promise<void> {
    // Should redirect to charts list
    await expect(this.page).toHaveURL(/.*\/charts\/?$/);
  }

  async expectPdfGenerating(): Promise<void> {
    await expect(this.page.getByText(/gerando|generating|aguarde|loading/i)).toBeVisible();
  }

  async expectPlanetInfo(planetName: string): Promise<void> {
    await expect(this.page.getByText(new RegExp(planetName, 'i'))).toBeVisible();
  }

  async expectAspectInfo(aspect: string): Promise<void> {
    await expect(this.page.getByText(new RegExp(aspect, 'i'))).toBeVisible();
  }
}
