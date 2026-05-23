import { expect, test } from '@playwright/test';

test.describe.serial('weight entry edit flow', () => {
  const unique = Date.now();
  const email = `weight-edit-${unique}@example.com`;
  const password = 'Aa1!aaaaaaaa';

  test('seed: register, log in, and create one entry', async ({ page }) => {
    await page.goto('/register');
    await page.getByLabel(/display name/i).fill('Edit Tester');
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

  test('click Edit, change the value, and save', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel(/email/i).fill(email);
    await page.getByLabel(/password/i).fill(password);
    await page.getByRole('button', { name: /log in/i }).click();
    await expect(page).toHaveURL('/', { timeout: 10_000 });
    await page.goto('/weight');

    await page.getByRole('link', { name: /edit/i }).first().click();
    expect(page.url()).toMatch(/\/weight\/\d+\/edit/);

    const weightInput = page.getByLabel(/weight value/i);
    await weightInput.clear();
    await weightInput.fill('180');
    await page.getByRole('button', { name: /save/i }).click();
    await expect(page).toHaveURL('/weight', { timeout: 10_000 });
    await expect(page.getByText('180')).toBeVisible({ timeout: 5_000 });
  });
});
