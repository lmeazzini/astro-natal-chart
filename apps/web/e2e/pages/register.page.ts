/**
 * Register Page Object Model.
 */

import { type Page, expect } from '@playwright/test';
import { BasePage } from './base.page';
import { ROUTES } from '../fixtures/test-data';

export class RegisterPage extends BasePage {
  constructor(page: Page) {
    super(page);
  }

  // Locators
  private get emailInput() {
    return this.page.locator('input[type="email"]');
  }

  private get nameInput() {
    return this.page.locator('input[autocomplete="name"]');
  }

  private get passwordInput() {
    return this.page.locator('input[autocomplete="new-password"]').first();
  }

  private get confirmPasswordInput() {
    return this.page.locator('input[autocomplete="new-password"]').last();
  }

  private get termsCheckbox() {
    return this.page.locator('[role="checkbox"]');
  }

  private get submitButton() {
    return this.page.locator('button[type="submit"]');
  }

  private get loginLink() {
    return this.page.locator('a[href="/login"]');
  }

  private get termsLink() {
    return this.page.locator('a[href="/terms"]');
  }

  private get privacyLink() {
    return this.page.locator('a[href="/privacy"]');
  }

  // Actions
  async goto(): Promise<void> {
    await this.page.goto(ROUTES.register);
    await this.waitForLoad();
  }

  async fillEmail(email: string): Promise<void> {
    await this.emailInput.fill(email);
  }

  async fillName(name: string): Promise<void> {
    await this.nameInput.fill(name);
  }

  async fillPassword(password: string): Promise<void> {
    await this.passwordInput.fill(password);
  }

  async fillConfirmPassword(password: string): Promise<void> {
    await this.confirmPasswordInput.fill(password);
  }

  async acceptTerms(): Promise<void> {
    await this.termsCheckbox.click();
  }

  async submit(): Promise<void> {
    await this.submitButton.click();
  }

  async register(
    email: string,
    name: string,
    password: string,
    confirmPassword?: string,
    acceptTerms: boolean = true
  ): Promise<void> {
    await this.fillEmail(email);
    await this.fillName(name);
    await this.fillPassword(password);
    await this.fillConfirmPassword(confirmPassword || password);
    if (acceptTerms) {
      await this.acceptTerms();
    }
    await this.submit();
  }

  async registerAndWaitForDashboard(
    email: string,
    name: string,
    password: string
  ): Promise<void> {
    await this.register(email, name, password);
    await this.page.waitForURL('**/dashboard**');
  }

  async clickLogin(): Promise<void> {
    await this.loginLink.click();
  }

  async clickTerms(): Promise<void> {
    await this.termsLink.first().click();
  }

  async clickPrivacy(): Promise<void> {
    await this.privacyLink.first().click();
  }

  // Assertions
  async expectEmailError(message: string | RegExp): Promise<void> {
    const errorMessage = this.page.locator('form').getByText(message);
    await expect(errorMessage).toBeVisible();
  }

  async expectPasswordError(message: string | RegExp): Promise<void> {
    const errorMessage = this.page.locator('form').getByText(message);
    await expect(errorMessage).toBeVisible();
  }

  async expectTermsError(message: string | RegExp): Promise<void> {
    const errorMessage = this.page.locator('form').getByText(message);
    await expect(errorMessage).toBeVisible();
  }

  async expectGeneralError(message: string | RegExp): Promise<void> {
    await expect(this.getErrorAlert()).toContainText(message);
  }

  async expectToBeOnRegisterPage(): Promise<void> {
    await expect(this.page).toHaveURL(/.*\/register/);
    await expect(this.emailInput).toBeVisible();
  }

  async expectSubmitButtonDisabled(): Promise<void> {
    await expect(this.submitButton).toBeDisabled();
  }

  async expectSubmitButtonEnabled(): Promise<void> {
    await expect(this.submitButton).toBeEnabled();
  }

  async expectTermsChecked(): Promise<void> {
    await expect(this.termsCheckbox).toHaveAttribute('data-state', 'checked');
  }

  async expectTermsUnchecked(): Promise<void> {
    await expect(this.termsCheckbox).toHaveAttribute('data-state', 'unchecked');
  }
}
