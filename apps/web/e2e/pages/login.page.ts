/**
 * Login Page Object Model.
 */

import { type Page, expect } from '@playwright/test';
import { BasePage } from './base.page';
import { ROUTES } from '../fixtures/test-data';

export class LoginPage extends BasePage {
  constructor(page: Page) {
    super(page);
  }

  // Locators
  private get emailInput() {
    return this.page.locator('input[type="email"]');
  }

  private get passwordInput() {
    return this.page.locator('input[type="password"]');
  }

  private get submitButton() {
    return this.page.locator('button[type="submit"]');
  }

  private get forgotPasswordLink() {
    return this.page.locator('a[href="/forgot-password"]');
  }

  private get registerLink() {
    return this.page.locator('a[href="/register"]');
  }

  private get showPasswordButton() {
    return this.page.locator('button[aria-label]').filter({ has: this.page.locator('svg') }).first();
  }

  // Actions
  async goto(): Promise<void> {
    await this.page.goto(ROUTES.login);
    await this.waitForLoad();
  }

  async fillEmail(email: string): Promise<void> {
    await this.emailInput.fill(email);
  }

  async fillPassword(password: string): Promise<void> {
    await this.passwordInput.fill(password);
  }

  async submit(): Promise<void> {
    await this.submitButton.click();
  }

  async login(email: string, password: string): Promise<void> {
    await this.fillEmail(email);
    await this.fillPassword(password);
    await this.submit();
  }

  async loginAndWaitForDashboard(email: string, password: string): Promise<void> {
    await this.login(email, password);
    await this.page.waitForURL('**/dashboard**');
  }

  async togglePasswordVisibility(): Promise<void> {
    await this.showPasswordButton.click();
  }

  async clickForgotPassword(): Promise<void> {
    await this.forgotPasswordLink.click();
  }

  async clickRegister(): Promise<void> {
    await this.registerLink.click();
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

  async expectGeneralError(message: string | RegExp): Promise<void> {
    await expect(this.getErrorAlert()).toContainText(message);
  }

  async expectToBeOnLoginPage(): Promise<void> {
    await expect(this.page).toHaveURL(/.*\/login/);
    await expect(this.emailInput).toBeVisible();
  }

  async expectSubmitButtonDisabled(): Promise<void> {
    await expect(this.submitButton).toBeDisabled();
  }

  async expectSubmitButtonEnabled(): Promise<void> {
    await expect(this.submitButton).toBeEnabled();
  }

  async expectPasswordVisible(): Promise<void> {
    await expect(this.passwordInput).toHaveAttribute('type', 'text');
  }

  async expectPasswordHidden(): Promise<void> {
    await expect(this.passwordInput).toHaveAttribute('type', 'password');
  }
}
