import { expect, test } from '@playwright/test';

/**
 * SRS NFR-A-5: All interactive targets are at least 44 by 44 CSS pixels.
 *
 * This spec covers the F5 remediation in docs/standards/M2_WEB_APP_QUALITY.md
 * §5: the weight-entry row Edit/Delete controls used `IconButton size="small"`
 * which falls below the 44px target. After F5 they must render as full
 * MUI Button components with sx={{ minHeight: 44 }} and meet the dimension
 * floor at runtime.
 */
test.describe.serial('weight table action target sizes', () => {
  const unique = Date.now();
  const email = `target-size-${unique}@example.com`;
  const password = 'Aa1!aaaaaaaa';

  test('seed: register and create one entry', async ({ page }) => {
    await page.goto('/register');
    await page.getByLabel(/display name/i).fill('Target Size Tester');
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

  test('Edit and Delete row actions are at least 44x44 CSS pixels', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel(/email/i).fill(email);
    await page.getByLabel(/password/i).fill(password);
    await page.getByRole('button', { name: /log in/i }).click();
    await expect(page).toHaveURL('/', { timeout: 10_000 });
    await page.goto('/weight');

    // Edit is a link (renders as <a> via component={Link}); Delete is a button.
    const editControl = page.getByRole('link', { name: /^edit entry from/i }).first();
    const deleteControl = page.getByRole('button', { name: /^delete entry from/i }).first();

    await expect(editControl).toBeVisible({ timeout: 10_000 });
    await expect(deleteControl).toBeVisible({ timeout: 10_000 });

    const editBox = await editControl.boundingBox();
    const deleteBox = await deleteControl.boundingBox();

    expect(editBox, 'edit control bounding box').not.toBeNull();
    expect(deleteBox, 'delete control bounding box').not.toBeNull();
    // SRS NFR-A-5: 44 by 44 CSS pixels minimum.
    expect(editBox!.height).toBeGreaterThanOrEqual(44);
    expect(editBox!.width).toBeGreaterThanOrEqual(44);
    expect(deleteBox!.height).toBeGreaterThanOrEqual(44);
    expect(deleteBox!.width).toBeGreaterThanOrEqual(44);
  });
});
