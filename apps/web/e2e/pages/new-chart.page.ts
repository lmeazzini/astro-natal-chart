/**
 * New Chart Page Object Model.
 *
 * Handles the multi-step chart creation form.
 */

import { type Page, expect } from '@playwright/test';
import { BasePage } from './base.page';
import { ROUTES } from '../fixtures/test-data';

export class NewChartPage extends BasePage {
  constructor(page: Page) {
    super(page);
  }

  // Step indicators
  private get currentStepIndicator() {
    return this.page.locator('[class*="progress"], [class*="step"]').filter({ hasText: /\d/ });
  }

  // Step 1: Personal Information
  private get nameInput() {
    return this.page.locator('input').first();
  }

  private get genderSelect() {
    return this.page.locator('[role="combobox"]').first();
  }

  // Step 2: Birth Date and Time
  private get birthDateTimeInput() {
    return this.page.locator('input[type="datetime-local"]');
  }

  private get timezoneSelect() {
    return this.page.locator('button').filter({ hasText: /America|Europe|UTC/i });
  }

  // Step 3: Birth Location
  private get cityInput() {
    return this.page.locator('input[autocomplete="off"]');
  }

  private get countryInput() {
    return this.page.locator('input[placeholder*="Brasil"], input').nth(1);
  }

  private get latitudeInput() {
    return this.page.locator('input[type="number"]').first();
  }

  private get longitudeInput() {
    return this.page.locator('input[type="number"]').last();
  }

  private get locationSuggestions() {
    return this.page.locator('[class*="suggestion"], button').filter({ has: this.page.locator('svg') });
  }

  // Step 4: Review
  private get notesTextarea() {
    return this.page.locator('textarea');
  }

  // Navigation buttons
  private get nextButton() {
    return this.page.getByRole('button', { name: /próximo|next|avançar/i });
  }

  private get previousButton() {
    return this.page.getByRole('button', { name: /anterior|previous|voltar/i });
  }

  private get submitButton() {
    return this.page.getByRole('button', { name: /criar|create|gerar|calcular/i });
  }

  private get backToDashboardButton() {
    return this.page.locator('a[href="/dashboard"], button').filter({ hasText: /voltar|back/i });
  }

  // Actions
  async goto(): Promise<void> {
    await this.page.goto(ROUTES.newChart);
    await this.waitForLoad();
  }

  // Step 1 actions
  async fillPersonName(name: string): Promise<void> {
    await this.nameInput.fill(name);
  }

  async selectGender(gender: 'Masculino' | 'Feminino' | 'Outro'): Promise<void> {
    await this.genderSelect.click();
    await this.page.getByRole('option', { name: gender }).click();
  }

  // Step 2 actions
  async fillBirthDateTime(datetime: string): Promise<void> {
    // datetime should be in format "YYYY-MM-DDTHH:mm"
    await this.birthDateTimeInput.fill(datetime);
  }

  async selectTimezone(timezone: string): Promise<void> {
    await this.timezoneSelect.click();
    await this.page.getByRole('option', { name: new RegExp(timezone, 'i') }).click();
  }

  // Step 3 actions
  async searchLocation(query: string): Promise<void> {
    await this.cityInput.fill(query);
    // Wait for suggestions to appear
    await this.page.waitForTimeout(600); // debounce
  }

  async selectLocationSuggestion(index: number = 0): Promise<void> {
    const suggestions = this.page.locator('[class*="suggestion"] button, button').filter({
      has: this.page.locator('[class*="MapPin"], svg'),
    });
    await suggestions.nth(index).click();
  }

  async selectLocationByText(text: string): Promise<void> {
    await this.page.getByText(text).click();
  }

  async fillManualCoordinates(latitude: number, longitude: number): Promise<void> {
    await this.latitudeInput.fill(latitude.toString());
    await this.longitudeInput.fill(longitude.toString());
  }

  async fillCountry(country: string): Promise<void> {
    await this.countryInput.fill(country);
  }

  // Step 4 actions
  async fillNotes(notes: string): Promise<void> {
    await this.notesTextarea.fill(notes);
  }

  // Navigation actions
  async clickNext(): Promise<void> {
    await this.nextButton.click();
  }

  async clickPrevious(): Promise<void> {
    await this.previousButton.click();
  }

  async submit(): Promise<void> {
    await this.submitButton.click();
  }

  async goBackToDashboard(): Promise<void> {
    await this.backToDashboardButton.click();
  }

  // Complete chart creation flow
  async createChart(data: {
    name: string;
    birthDate: string;
    birthTime: string;
    location: string;
    gender?: 'Masculino' | 'Feminino' | 'Outro';
    notes?: string;
  }): Promise<void> {
    // Step 1: Personal Information
    await this.fillPersonName(data.name);
    if (data.gender) {
      await this.selectGender(data.gender);
    }
    await this.clickNext();

    // Step 2: Birth Date and Time
    const datetime = `${data.birthDate}T${data.birthTime}`;
    await this.fillBirthDateTime(datetime);
    await this.clickNext();

    // Step 3: Birth Location
    await this.searchLocation(data.location);
    await this.page.waitForTimeout(1000); // Wait for geocoding
    // Try to click on first suggestion
    try {
      await this.page.locator('button').filter({ hasText: data.location.split(',')[0] }).first().click({ timeout: 3000 });
    } catch {
      // If no suggestion appears, coordinates should be manually filled
    }
    await this.clickNext();

    // Step 4: Review
    if (data.notes) {
      await this.fillNotes(data.notes);
    }
    await this.submit();
  }

  // Assertions
  async expectToBeOnStep(stepNumber: number): Promise<void> {
    await expect(this.page.getByText(new RegExp(`passo ${stepNumber}|step ${stepNumber}`, 'i'))).toBeVisible();
  }

  async expectToBeOnNewChartPage(): Promise<void> {
    await expect(this.page).toHaveURL(/.*\/charts\/new/);
  }

  async expectNameError(message: string | RegExp): Promise<void> {
    await expect(this.page.getByText(message)).toBeVisible();
  }

  async expectDateError(message: string | RegExp): Promise<void> {
    await expect(this.page.getByText(message)).toBeVisible();
  }

  async expectLocationError(message: string | RegExp): Promise<void> {
    await expect(this.page.getByText(message)).toBeVisible();
  }

  async expectGeneralError(message: string | RegExp): Promise<void> {
    await expect(this.getErrorAlert()).toContainText(message);
  }

  async expectLocationSuggestionsVisible(): Promise<void> {
    await expect(
      this.page.locator('[class*="suggestion"], [class*="dropdown"]').filter({ hasText: /.+/ })
    ).toBeVisible();
  }

  async expectChartCreated(): Promise<void> {
    // Should redirect to charts page or chart detail
    await expect(this.page).toHaveURL(/.*\/charts.*/);
  }

  async expectLimitModal(): Promise<void> {
    await expect(this.page.getByText(/limite|limit/i)).toBeVisible();
  }

  async expectNextButtonEnabled(): Promise<void> {
    await expect(this.nextButton).toBeEnabled();
  }

  async expectNextButtonDisabled(): Promise<void> {
    await expect(this.nextButton).toBeDisabled();
  }
}
