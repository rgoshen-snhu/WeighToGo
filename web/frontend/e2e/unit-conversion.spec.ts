import { expect, test } from '@playwright/test';

/**
 * E2E: weight unit conversion for display (FR-W-6).
 *
 * A weight logged in lbs must display in the user's preferred unit after the
 * preference changes to kg, while the stored row keeps its original lbs unit
 * and value (display-only conversion).
 */
test.describe.serial('unit conversion flow', () => {
  const unique = Date.now();
  const email = `unit-conv-e2e-${unique}@example.com`;
  const password = 'Aa1!aaaaaaaa';

  test('seed: register and log a 200 lb entry (default lbs preference)', async ({ page }) => {
    await page.goto('/register');
    await page.getByLabel(/display name/i).fill('Unit Conv E2E');
    await page.getByLabel(/email/i).fill(email);
    await page.getByLabel(/^password$/i).fill(password);
    await page.getByLabel(/confirm password/i).fill(password);
    await page.getByRole('button', { name: /create account/i }).click();
    await expect(page).toHaveURL('/', { timeout: 10_000 });

    await page.goto('/weight/new');
    await page.getByLabel(/weight value/i).fill('200');
    // Default unit is lbs; assert it before saving so the seed is unambiguous.
    await expect(page.locator('input[name="weight_unit"]')).toHaveValue('lbs', { timeout: 5_000 });
    await page.getByRole('button', { name: /save/i }).click();
    await expect(page).toHaveURL('/weight', { timeout: 10_000 });
    await expect(page.getByText('200.0 lbs')).toBeVisible({ timeout: 5_000 });
  });

  test('switching preference to kg converts the display; stored row stays lbs', async ({
    page,
  }) => {
    await page.goto('/login');
    await page.getByLabel(/email/i).fill(email);
    await page.getByLabel(/password/i).fill(password);
    await page.getByRole('button', { name: /log in/i }).click();
    await expect(page).toHaveURL('/', { timeout: 10_000 });

    // Change the unit preference to kg.
    await page.goto('/settings');
    await page.getByRole('radio', { name: 'kg' }).click();
    await expect(page.getByText(/preferences saved/i)).toBeVisible({ timeout: 5_000 });

    // The history now displays the 200 lb entry converted to kg (200 lb = 90.7 kg).
    await page.goto('/weight');
    await expect(page.getByText('90.7 kg')).toBeVisible({ timeout: 5_000 });
    await expect(page.getByText('200.0 lbs')).toHaveCount(0);

    // The stored row is unchanged: the edit form still shows lbs and value 200.
    await page.getByRole('link', { name: /edit/i }).first().click();
    expect(page.url()).toMatch(/\/weight\/\d+\/edit/);
    await expect(page.locator('input[name="weight_unit"]')).toHaveValue('lbs', { timeout: 5_000 });
    await expect(page.getByLabel(/weight value/i)).toHaveValue('200');
  });
});
