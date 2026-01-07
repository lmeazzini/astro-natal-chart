/**
 * Pricing Page Object Model.
 */

import { type Page, expect } from '@playwright/test';
import { BasePage } from './base.page';
import { ROUTES } from '../fixtures/test-data';

export class PricingPage extends BasePage {
  constructor(page: Page) {
    super(page);
  }

  // Locators
  private get pageTitle() {
    return this.page.locator('h1, h2').first();
  }

  private get freePlanCard() {
    return this.page.locator('[class*="card"], article').filter({ hasText: /free|grátis|gratuito/i });
  }

  private get premiumPlanCard() {
    return this.page.locator('[class*="card"], article').filter({ hasText: /premium|pro/i });
  }

  private get subscribeButton() {
    return this.page.getByRole('button', { name: /assinar|subscribe|escolher|select|upgrade/i });
  }

  private get currentPlanBadge() {
    return this.page.getByText(/plano atual|current plan|seu plano|your plan/i);
  }

  private get priceDisplay() {
    return this.page.locator('[class*="price"], [data-testid="price"]');
  }

  private get featuresList() {
    return this.page.locator('ul, [class*="features"]');
  }

  private get billingToggle() {
    return this.page.locator('[role="switch"], button').filter({ hasText: /mensal|anual|monthly|yearly/i });
  }

  private get manageSubscriptionButton() {
    return this.page.getByRole('button', { name: /gerenciar|manage|portal/i });
  }

  private get cancelSubscriptionButton() {
    return this.page.getByRole('button', { name: /cancelar|cancel/i });
  }

  // Actions
  async goto(): Promise<void> {
    await this.page.goto(ROUTES.pricing);
    await this.waitForLoad();
  }

  async clickSubscribe(planType: 'free' | 'premium' = 'premium'): Promise<void> {
    const card = planType === 'free' ? this.freePlanCard : this.premiumPlanCard;
    await card.getByRole('button').click();
  }

  async toggleBilling(): Promise<void> {
    await this.billingToggle.click();
  }

  async clickManageSubscription(): Promise<void> {
    await this.manageSubscriptionButton.click();
  }

  async clickCancelSubscription(): Promise<void> {
    await this.cancelSubscriptionButton.click();
  }

  async getDisplayedPrice(): Promise<string | null> {
    return await this.priceDisplay.first().textContent();
  }

  // Assertions
  async expectToBeOnPricingPage(): Promise<void> {
    await expect(this.page).toHaveURL(/.*\/pricing/);
  }

  async expectPlansVisible(): Promise<void> {
    // Should see at least one plan card
    await expect(
      this.page.locator('[class*="card"], article').filter({ hasText: /plano|plan/i })
    ).toBeVisible();
  }

  async expectFreePlanVisible(): Promise<void> {
    await expect(this.freePlanCard).toBeVisible();
  }

  async expectPremiumPlanVisible(): Promise<void> {
    await expect(this.premiumPlanCard).toBeVisible();
  }

  async expectCurrentPlan(planName: string): Promise<void> {
    await expect(
      this.page.getByText(new RegExp(`${planName}.*atual|atual.*${planName}|current.*${planName}`, 'i'))
    ).toBeVisible();
  }

  async expectPriceVisible(): Promise<void> {
    await expect(this.priceDisplay.first()).toBeVisible();
  }

  async expectFeaturesVisible(): Promise<void> {
    await expect(this.featuresList.first()).toBeVisible();
  }

  async expectStripeRedirect(): Promise<void> {
    // When clicking subscribe, should redirect to Stripe checkout
    // In test mode, we just check for URL change or loading state
    await expect(
      this.page.locator('[class*="loading"], [class*="spinner"]').or(
        this.page.getByText(/redirecionando|redirecting|processando|processing/i)
      )
    ).toBeVisible({ timeout: 5000 }).catch(() => {
      // Or the URL might change to Stripe
      return expect(this.page).toHaveURL(/stripe\.com|checkout/);
    });
  }

  async expectSubscribeButtonVisible(): Promise<void> {
    await expect(this.subscribeButton.first()).toBeVisible();
  }

  async expectManageSubscriptionVisible(): Promise<void> {
    await expect(this.manageSubscriptionButton).toBeVisible();
  }

  async expectFeature(featureName: string): Promise<void> {
    await expect(this.page.getByText(new RegExp(featureName, 'i'))).toBeVisible();
  }

  async expectPlanPrice(planType: 'free' | 'premium', price: string | RegExp): Promise<void> {
    const card = planType === 'free' ? this.freePlanCard : this.premiumPlanCard;
    await expect(card).toContainText(price);
  }
}
