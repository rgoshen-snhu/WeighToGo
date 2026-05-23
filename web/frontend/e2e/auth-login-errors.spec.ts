import { expect, test, type Page } from '@playwright/test';

// Helper: register a user and log out, leaving the browser on /login.
async function seedUser(page: Page, email: string, password: string) {
  await page.goto('/register');
  await page.getByLabel(/display name/i).fill('Err User');
  await page.getByLabel(/email/i).fill(email);
  await page.getByLabel(/^password$/i).fill(password);
  await page.getByLabel(/confirm password/i).fill(password);
  await page.getByRole('button', { name: /create account/i }).click();
  await expect(page).toHaveURL('/', { timeout: 10_000 });
  await page.getByRole('button', { name: /account menu/i }).click();
  await page.getByRole('menuitem', { name: /log out/i }).click();
  await expect(page).toHaveURL(/\/login/);
}

test('invalid credentials surface "Invalid credentials." and clear password only', async ({
  page,
}) => {
  const unique = Date.now();
  const email = `err-cred-${unique}@example.com`;
  const password = 'Aa1!aaaaaaaa';
  await seedUser(page, email, password);

  await page.goto('/login');
  await page.getByLabel(/email/i).fill(email);
  await page.getByLabel(/password/i).fill('wrong-password-1!');
  await page.getByRole('button', { name: /log in/i }).click();

  const alert = page.getByRole('alert');
  await expect(alert).toBeVisible();
  await expect(alert).toHaveText(/invalid credentials/i);
  await expect(page.getByLabel(/password/i)).toHaveValue('');
  await expect(page.getByLabel(/email/i)).toHaveValue(email);
  await expect(page).toHaveURL(/\/login/);
});

test('5 consecutive failed attempts surface account locked message (NFR-S-6)', async ({ page }) => {
  // Use a separate user so this test starts with 0 prior failed attempts.
  const unique = Date.now();
  const email = `err-lock-${unique}@example.com`;
  const password = 'Aa1!aaaaaaaa';
  await seedUser(page, email, password);

  await page.goto('/login');
  for (let i = 1; i <= 6; i++) {
    await page.getByLabel(/email/i).fill(email);
    await page.getByLabel(/password/i).fill(`wrong-password-${i}!`);
    const responsePromise = page.waitForResponse((r) => r.url().includes('/api/v1/auth/login'));
    await page.getByRole('button', { name: /log in/i }).click();
    await responsePromise;
  }
  const alert = page.getByRole('alert');
  await expect(alert).toBeVisible();
  await expect(alert).toHaveText(/temporarily locked/i);
  await expect(page.getByRole('button', { name: /log in/i })).toBeEnabled();
});
