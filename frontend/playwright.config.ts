import { defineConfig } from '@playwright/test';
import path from 'path';

export default defineConfig({
  testDir: './e2e',
  timeout: 30000,
  fullyParallel: false,
  workers: 1,
  retries: 0,
  use: {
    baseURL: 'http://127.0.0.1:8000',
    channel: 'msedge',
    headless: true,
  },
  webServer: {
    command: `"${path.resolve('..', 'venv', 'Scripts', 'python.exe')}" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000`,
    url: 'http://127.0.0.1:8000/api/health',
    reuseExistingServer: true,
    timeout: 30000,
    cwd: path.resolve('..'),
  },
  projects: [
    {
      name: 'msedge',
      use: {
        channel: 'msedge',
        viewport: { width: 1440, height: 900 },
      },
    },
  ],
});
