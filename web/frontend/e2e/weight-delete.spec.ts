import { expect, test } from '@playwright/test';

test.describe.serial('weight entry delete flow', () => {
  const unique = Date.now();
  const email = `weight-delete-${unique}@example.com`;
  const password = 'Aa1!aaaaaaaa';

  test('seed: register and create two entries on different dates', async ({ page }) => {
    await page.goto('/register');
    await page.getByLabel(/display name/i).fill('Delete Tester');
    await page.getByLabel(/email/i).fill(email);
    await page.getByLabel(/^password$/i).fill(password);
    await page.getByLabel(/confirm password/i).fill(password);
    await page.getByRole('button', { name: /create account/i }).click();
    await expect(page).toHaveURL('/', { timeout: 10_000 });

    // First entry: today
    await page.goto('/weight/new');
    await page.getByLabel(/weight value/i).fill('175.5');
    await page.getByRole('button', { name: /save/i }).click();
    await expect(page).toHaveURL('/weight', { timeout: 10_000 });

    // Second entry: yesterday
    const yesterday = new Date(Date.now() - 86_400_000).toISOString().split('T')[0]!;
    await page.goto('/weight/new');
    await page.getByLabel(/weight value/i).fill('174');
    await page.getByLabel(/observation date/i).fill(yesterday);
    await page.getByRole('button', { name: /save/i }).click();
    await expect(page).toHaveURL('/weight', { timeout: 10_000 });
  });

  test('delete the first entry, second entry remains', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel(/email/i).fill(email);
    await page.getByLabel(/password/i).fill(password);
    await page.getByRole('button', { name: /log in/i }).click();
    await page.goto('/weight');

    // Click the first delete button (most recent entry)
    const deleteButtons = page.getByRole('button', { name: /delete/i });
    await deleteButtons.first().click();

    // Confirm in the dialog
    await page.getByRole('button', { name: /^delete$/i }).click();

    // Only 174 remains, 175.5 is gone
    await expect(page.getByText('174')).toBeVisible({ timeout: 10_000 });
    await expect(page.getByText('175.5')).not.toBeVisible({ timeout: 5_000 });
  });
});
