import AxeBuilder from '@axe-core/playwright';
import { type Page, expect, test } from '@playwright/test';

/**
 * Accessibility scans for the goals page (NFR-A-1, NFR-A-3, NFR-A-4).
 *
 * Checks for critical WCAG 2.1 violations using axe-core/playwright.
 */
test.describe.serial('goals page accessibility', () => {
  const unique = Date.now();
  const email = `goal-a11y-${unique}@example.com`;
  const password = 'Aa1!aaaaaaaa';

  test('seed: register user', async ({ page }) => {
    await page.goto('/register');
    await page.getByLabel(/display name/i).fill('A11y Goals User');
    await page.getByLabel(/email/i).fill(email);
    await page.getByLabel(/^password$/i).fill(password);
    await page.getByLabel(/confirm password/i).fill(password);
    await page.getByRole('button', { name: /create account/i }).click();
    await expect(page).toHaveURL('/', { timeout: 10_000 });
  });

  async function loginAndGoto(page: Page, path: string) {
    await page.goto('/login');
    await page.getByLabel(/email/i).fill(email);
    await page.getByLabel(/password/i).fill(password);
    await page.getByRole('button', { name: /log in/i }).click();
    await expect(page).toHaveURL('/', { timeout: 10_000 });
    await page.goto(path);
  }

  test('/goals (no active goal) has no critical a11y violations', async ({ page }) => {
    await loginAndGoto(page, '/goals');
    // Wait for the page to fully load
    await expect(page.getByRole('button', { name: /set goal/i })).toBeVisible({
      timeout: 10_000,
    });
    const results = await new AxeBuilder({ page }).analyze();
    expect(results.violations.filter((v) => v.impact === 'critical')).toHaveLength(0);
  });

  test('/goals (with active goal) has no critical a11y violations', async ({ page }) => {
    await loginAndGoto(page, '/goals');
    await page.getByLabel(/target weight/i).fill('150');
    await page.getByLabel(/starting weight/i).fill('200');
    await page.getByRole('button', { name: /set goal/i }).click();
    await expect(page.getByRole('progressbar')).toBeVisible({ timeout: 10_000 });
    const results = await new AxeBuilder({ page }).analyze();
    expect(results.violations.filter((v) => v.impact === 'critical')).toHaveLength(0);
  });
});
