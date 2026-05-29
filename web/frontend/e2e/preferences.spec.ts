import { expect, test } from '@playwright/test';

/**
 * E2E: user preferences (FR-P-1, FR-P-3).
 *
 * 1. Changing the weight-unit preference on /settings causes the new
 *    weight-entry form to default to the selected unit.
 *
 * 2. Toggling achievement notifications off on /settings means no toast
 *    appears when a weight entry earns a milestone achievement.
 */
test.describe.serial('preferences flow', () => {
  const unique = Date.now();
  const email = `prefs-e2e-${unique}@example.com`;
  const password = 'Aa1!aaaaaaaa';

  // ── Seed ──────────────────────────────────────────────────────────────────

  test('seed: register user and set a lose goal (start=200, target=150)', async ({ page }) => {
    await page.goto('/register');
    await page.getByLabel(/display name/i).fill('Prefs E2E');
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

  // ── FR-P-1: unit preference drives form default ───────────────────────────

  test('changing unit to kg on /settings causes weight form to default to kg', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel(/email/i).fill(email);
    await page.getByLabel(/password/i).fill(password);
    await page.getByRole('button', { name: /log in/i }).click();
    await expect(page).toHaveURL('/', { timeout: 10_000 });

    // Change unit preference to kg on the settings page.
    await page.goto('/settings');
    await page.getByRole('radio', { name: 'kg' }).click();
    // Wait for the mutation to complete (aria-live "Preferences saved").
    await expect(page.getByText(/preferences saved/i)).toBeVisible({ timeout: 5_000 });

    // Navigate to the new weight-entry form and verify the default unit is kg.
    // MUI Select renders a hidden <input> for form submission — target that for
    // toHaveValue(), since toHaveValue() requires a native input element.
    await page.goto('/weight/new');
    await expect(page.locator('input[name="weight_unit"]')).toHaveValue('kg', { timeout: 5_000 });
  });

  // ── FR-P-3: notification toggle suppresses toast ──────────────────────────

  test('toggling milestone notifications off suppresses the toast', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel(/email/i).fill(email);
    await page.getByLabel(/password/i).fill(password);
    await page.getByRole('button', { name: /log in/i }).click();
    await expect(page).toHaveURL('/', { timeout: 10_000 });

    // Disable milestone alerts on the settings page.
    await page.goto('/settings');
    const milestoneToggle = page.getByLabel(/milestone alerts toggle/i);
    // Toggle is checked by default; uncheck it.
    if (await milestoneToggle.isChecked()) {
      await milestoneToggle.click();
    }
    await expect(page.getByText(/preferences saved/i)).toBeVisible({ timeout: 5_000 });

    // Log a weight entry that would normally trigger the 5 lb milestone.
    await page.goto('/weight/new');
    await page.getByLabel(/weight value/i).fill('195');
    // Unit might be kg from the previous test; explicitly choose lbs.
    // MUI Select is not a native <select>, so use click-to-open + option click.
    await page.getByRole('combobox', { name: /weight unit/i }).click();
    await page.getByRole('option', { name: 'lbs' }).click();
    await page.getByRole('button', { name: /save/i }).click();

    // The milestone toast should NOT appear (FR-P-3 toggle off).
    await expect(page.getByRole('status')).not.toBeVisible({ timeout: 3_000 });
  });
});
