import AxeBuilder from '@axe-core/playwright';
import { type Page, expect, test } from '@playwright/test';

/**
 * Accessibility scans for weight and dashboard pages.
 *
 * Uses @axe-core/playwright to run WCAG 2.1 AA checks on each key page.
 * Rate limiting is disabled in the Playwright webServer configuration via
 * RATE_LIMIT_ENABLED=false so that seeding does not trigger 429s.
 */
test.describe.serial('weight and dashboard accessibility', () => {
  const unique = Date.now();
  const email = `a11y-${unique}@example.com`;
  const password = 'Aa1!aaaaaaaa';

  test('seed: register user and create one entry', async ({ page }) => {
    await page.goto('/register');
    await page.getByLabel(/display name/i).fill('A11y User');
    await page.getByLabel(/email/i).fill(email);
    await page.getByLabel(/^password$/i).fill(password);
    await page.getByLabel(/confirm password/i).fill(password);
    await page.getByRole('button', { name: /create account/i }).click();
    await expect(page).toHaveURL('/', { timeout: 10_000 });

    await page.goto('/weight/new');
    await page.getByLabel(/weight value/i).fill('175.5');
    await page.getByRole('button', { name: /save/i }).click();
    await expect(page).toHaveURL('/weight', { timeout: 10_000 });
  });

  async function loginAndGoto(page: Page, path: string) {
    await page.goto('/login');
    await page.getByLabel(/email/i).fill(email);
    await page.getByLabel(/password/i).fill(password);
    await page.getByRole('button', { name: /log in/i }).click();
    await expect(page).toHaveURL('/', { timeout: 10_000 });
    await page.goto(path);
  }

  test('dashboard / has no critical a11y violations', async ({ page }) => {
    await loginAndGoto(page, '/');
    const results = await new AxeBuilder({ page }).analyze();
    expect(results.violations.filter((v) => v.impact === 'critical')).toHaveLength(0);
  });

  test('/weight has no critical a11y violations', async ({ page }) => {
    await loginAndGoto(page, '/weight');
    const results = await new AxeBuilder({ page }).analyze();
    expect(results.violations.filter((v) => v.impact === 'critical')).toHaveLength(0);
  });

  test('/weight/new has no critical a11y violations', async ({ page }) => {
    await loginAndGoto(page, '/weight/new');
    const results = await new AxeBuilder({ page }).analyze();
    expect(results.violations.filter((v) => v.impact === 'critical')).toHaveLength(0);
  });
});
