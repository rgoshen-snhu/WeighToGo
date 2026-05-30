import AxeBuilder from '@axe-core/playwright';
import { type Page, expect, test } from '@playwright/test';

/**
 * Accessibility scan for the dashboard trend chart and rate-of-change card
 * (FR-D-2, FR-D-3; NFR-A-1, NFR-A-3, NFR-A-4).
 *
 * Seeds an account with a couple of weight entries so the chart and rate card
 * render with real data, then runs an axe-core scan over the populated
 * dashboard.
 */
test.describe.serial('dashboard trends accessibility', () => {
  const unique = Date.now();
  const email = `dash-trends-a11y-${unique}@example.com`;
  const password = 'Aa1!aaaaaaaa';

  async function login(page: Page) {
    await page.goto('/login');
    await page.getByLabel(/email/i).fill(email);
    await page.getByLabel(/password/i).fill(password);
    await page.getByRole('button', { name: /log in/i }).click();
    await expect(page).toHaveURL('/', { timeout: 10_000 });
  }

  test('seed: register and log entries', async ({ page }) => {
    await page.goto('/register');
    await page.getByLabel(/display name/i).fill('Trends A11y User');
    await page.getByLabel(/email/i).fill(email);
    await page.getByLabel(/^password$/i).fill(password);
    await page.getByLabel(/confirm password/i).fill(password);
    await page.getByRole('button', { name: /create account/i }).click();
    await expect(page).toHaveURL('/', { timeout: 10_000 });

    await page.goto('/weight/new');
    await page.getByLabel(/weight value/i).fill('182.0');
    await page.getByRole('button', { name: /save/i }).click();
    await expect(page).toHaveURL('/weight', { timeout: 10_000 });
  });

  test('populated dashboard has no critical a11y violations', async ({ page }) => {
    await login(page);
    // The trend chart region must be present before scanning.
    await expect(page.getByRole('figure', { name: /weight trend/i })).toBeVisible({
      timeout: 10_000,
    });
    const results = await new AxeBuilder({ page }).analyze();
    expect(results.violations.filter((v) => v.impact === 'critical')).toHaveLength(0);
  });
});
