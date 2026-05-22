import { expect, test } from '@playwright/test';

test('the application shell loads with its heading', async ({ page }) => {
  await page.goto('/');

  await expect(page.getByRole('heading', { name: /weigh to go/i })).toBeVisible();
});
