import { defineConfig, devices } from '@playwright/test';

// Allow overriding the backend port so the dev server and CI can coexist with
// other services already bound to :8000.  Set VITE_API_PORT=8001 when port
// 8000 is occupied.
const API_PORT = process.env.VITE_API_PORT ?? '8000';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  use: { baseURL: 'http://localhost:5173', trace: 'retain-on-failure' },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: [
    {
      command: `cd ../backend && uv run uvicorn weighttogo.main:app --port ${API_PORT}`,
      url: `http://localhost:${API_PORT}/health`,
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
      env: { RATE_LIMIT_ENABLED: 'false' },
    },
    {
      command: `VITE_API_PORT=${API_PORT} npm run dev`,
      url: 'http://localhost:5173',
      reuseExistingServer: !process.env.CI,
    },
  ],
});
