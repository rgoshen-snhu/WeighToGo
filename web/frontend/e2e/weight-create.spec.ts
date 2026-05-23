import { expect, test } from '@playwright/test';

test.describe.serial('weight entry create flow', () => {
  const unique = Date.now();
  const email = `weight-create-${unique}@example.com`;
  const password = 'Aa1!aaaaaaaa';

  test('seed: register and reach dashboard', async ({ page }) => {
    await page.goto('/register');
    await page.getByLabel(/display name/i).fill('Create Tester');
    await page.getByLabel(/email/i).fill(email);
    await page.getByLabel(/^password$/i).fill(password);
    await page.getByLabel(/confirm password/i).fill(password);
    await page.getByRole('button', { name: /create account/i }).click();
    await expect(page).toHaveURL('/', { timeout: 10_000 });
  });

  test('navigate to /weight/new and fill the form', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel(/email/i).fill(email);
    await page.getByLabel(/password/i).fill(password);
    await page.getByRole('button', { name: /log in/i }).click();
    await expect(page).toHaveURL('/', { timeout: 10_000 });

    await page.goto('/weight/new');
    await page.getByLabel(/weight value/i).fill('175.5');
    // observation_date defaults to today — leave as is
    await page.getByRole('button', { name: /save/i }).click();
    await expect(page).toHaveURL('/weight', { timeout: 10_000 });
  });

  test('new entry appears as the first row in the history list', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel(/email/i).fill(email);
    await page.getByLabel(/password/i).fill(password);
    await page.getByRole('button', { name: /log in/i }).click();
    await expect(page).toHaveURL('/', { timeout: 10_000 });
    await page.goto('/weight');
    await expect(page.getByText('175.5')).toBeVisible({ timeout: 10_000 });
  });
});
