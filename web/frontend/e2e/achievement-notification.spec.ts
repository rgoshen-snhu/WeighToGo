import { expect, test } from '@playwright/test';

/**
 * E2E: achievement notification and achievements page (FR-N-1, FR-Ach-4).
 *
 * Verifies that a weight entry crossing the 5 lb milestone threshold shows
 * a toast notification and that the achievement appears on /achievements.
 */
test.describe.serial('achievement notification flow', () => {
  const unique = Date.now();
  const email = `ach-e2e-${unique}@example.com`;
  const password = 'Aa1!aaaaaaaa';

  test('seed: register and set a lose goal (start=200, target=150)', async ({ page }) => {
    await page.goto('/register');
    await page.getByLabel(/display name/i).fill('Ach E2E');
    await page.getByLabel(/email/i).fill(email);
    await page.getByLabel(/^password$/i).fill(password);
    await page.getByLabel(/confirm password/i).fill(password);
    await page.getByRole('button', { name: /create account/i }).click();
    await expect(page).toHaveURL('/', { timeout: 10_000 });

    await page.goto('/goals');
    await page.getByLabel(/target weight/i).fill('150');
    await page.getByLabel(/starting weight/i).fill('200');
    await page.getByRole('button', { name: /set goal/i }).click();
    await expect(page.getByRole('progressbar')).toBeVisible({ timeout: 10_000 });
  });

  test('weight entry at 195 lbs shows 5 lb milestone toast', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel(/email/i).fill(email);
    await page.getByLabel(/password/i).fill(password);
    await page.getByRole('button', { name: /log in/i }).click();
    await expect(page).toHaveURL('/', { timeout: 10_000 });

    await page.goto('/weight/new');
    await page.getByLabel(/weight value/i).fill('195');
    await page.getByRole('button', { name: /save/i }).click();

    // Achievement toast should appear (role="status", FR-N-1)
    await expect(page.getByRole('status')).toBeVisible({ timeout: 10_000 });
    await expect(page.getByText(/5 lb milestone/i)).toBeVisible({ timeout: 10_000 });
  });

  test('/achievements page lists the earned 5 lb milestone', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel(/email/i).fill(email);
    await page.getByLabel(/password/i).fill(password);
    await page.getByRole('button', { name: /log in/i }).click();
    await expect(page).toHaveURL('/', { timeout: 10_000 });

    await page.goto('/achievements');
    await expect(page.getByText(/5 lb milestone/i)).toBeVisible({ timeout: 10_000 });
  });
});
