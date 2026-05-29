import { expect, test } from '@playwright/test';

/**
 * E2E: goal creation flow.
 *
 * Verifies that a registered user can set an active goal and see the
 * GoalProgressBar rendered on the /goals page (FR-G-1, FR-D-4).
 */
test.describe.serial('goal creation flow', () => {
  const unique = Date.now();
  const email = `goal-create-${unique}@example.com`;
  const password = 'Aa1!aaaaaaaa';

  test('seed: register and reach dashboard', async ({ page }) => {
    await page.goto('/register');
    await page.getByLabel(/display name/i).fill('Goal Tester');
    await page.getByLabel(/email/i).fill(email);
    await page.getByLabel(/^password$/i).fill(password);
    await page.getByLabel(/confirm password/i).fill(password);
    await page.getByRole('button', { name: /create account/i }).click();
    await expect(page).toHaveURL('/', { timeout: 10_000 });
  });

  test('navigate to /goals and fill the goal form', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel(/email/i).fill(email);
    await page.getByLabel(/password/i).fill(password);
    await page.getByRole('button', { name: /log in/i }).click();
    await expect(page).toHaveURL('/', { timeout: 10_000 });

    await page.goto('/goals');
    // Fill target weight (default goal_type=lose, default unit=lbs)
    await page.getByLabel(/target weight/i).fill('150');
    await page.getByLabel(/starting weight/i).fill('200');
    await page.getByRole('button', { name: /set goal/i }).click();

    // After successful creation, the progress bar should be visible
    await expect(page.getByRole('progressbar')).toBeVisible({ timeout: 10_000 });
  });

  test('active goal shows "No entries yet" with no weight entries', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel(/email/i).fill(email);
    await page.getByLabel(/password/i).fill(password);
    await page.getByRole('button', { name: /log in/i }).click();
    await expect(page).toHaveURL('/', { timeout: 10_000 });

    await page.goto('/goals');
    await expect(page.getByText(/no entries yet/i)).toBeVisible({ timeout: 10_000 });
  });
});
