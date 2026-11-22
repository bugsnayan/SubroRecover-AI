import { test, expect } from '@playwright/test';

test.describe('Overview Page Global Filtering', () => {
  test('applying High priority filter updates all page widgets', async ({ page }) => {
    // Navigate to Overview page
    await page.goto('/');

    // Wait for initial data to load
    await expect(page.locator('text=Executive overview')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=180 claims').first()).toBeVisible({ timeout: 10000 });

    // Verify initial unfiltered state in the funnel
    const initialIngested = page.locator('div:has-text("Ingested")').filter({ hasText: '180 claims' }).first();
    await expect(initialIngested).toBeVisible();

    // Click "High" priority button on the Priority Distribution card
    const highBtn = page.locator('button').filter({ hasText: 'High' }).first();
    await expect(highBtn).toBeVisible();
    await highBtn.click();

    // 1. Assert active filter chip appears in global filter bar
    await expect(page.locator('text=Priority: High')).toBeVisible({ timeout: 5000 });

    // 2. Assert Funnel updates: Ingested count updates from 180 to 27
    const filteredIngested = page.locator('div:has-text("Ingested")').filter({ hasText: '27 claims' }).first();
    await expect(filteredIngested).toBeVisible({ timeout: 5000 });

    // 3. Assert Priority Donut center label updates to "High claims"
    await expect(page.locator('text=High claims')).toBeVisible({ timeout: 5000 });

    // 4. Assert Dismiss filter pill works and resets page to 180 claims
    const clearPill = page.locator('button:has-text("Clear all")');
    if (await clearPill.isVisible()) {
      await clearPill.click();
      await expect(page.locator('text=180 claims').first()).toBeVisible({ timeout: 5000 });
      await expect(page.locator('text=Total claims')).toBeVisible({ timeout: 5000 });
    }
  });
});
