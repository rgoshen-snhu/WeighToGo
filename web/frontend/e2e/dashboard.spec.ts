import { expect, test } from '@playwright/test';

test.describe.serial('dashboard summary flow', () => {
  const unique = Date.now();
  const email = `dashboard-${unique}@example.com`;
  const password = 'Aa1!aaaaaaaa';

  test('seed: register', async ({ page }) => {
    await page.goto('/register');
    await page.getByLabel(/display name/i).fill('Dashboard User');
    await page.getByLabel(/email/i).fill(email);
    await page.getByLabel(/^password$/i).fill(password);
    await page.getByLabel(/confirm password/i).fill(password);
    await page.getByRole('button', { name: /create account/i }).click();
    await expect(page).toHaveURL('/', { timeout: 10_000 });
  });

  test('new user sees empty state CTA on dashboard', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel(/email/i).fill(email);
    await page.getByLabel(/password/i).fill(password);
    await page.getByRole('button', { name: /log in/i }).click();
    await expect(page).toHaveURL('/', { timeout: 10_000 });
    await expect(page.getByText(/add your first entry/i)).toBeVisible({ timeout: 5_000 });
  });

  test('after logging an entry, dashboard shows latest entry and count 1', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel(/email/i).fill(email);
    await page.getByLabel(/password/i).fill(password);
    await page.getByRole('button', { name: /log in/i }).click();
    await expect(page).toHaveURL('/', { timeout: 10_000 });

    await page.goto('/weight/new');
    await page.getByLabel(/weight value/i).fill('175.5');
    await page.getByRole('button', { name: /save/i }).click();
    await expect(page).toHaveURL('/weight', { timeout: 10_000 });

    await page.goto('/');
    await expect(page.getByText('175.5 lbs')).toBeVisible({ timeout: 5_000 });
    await expect(page.getByRole('heading', { level: 5, name: '1', exact: true })).toBeVisible({
      timeout: 5_000,
    });
  });
});
