import { test, expect } from '@playwright/test';

test('expand generated catalog', async ({ page }) => {
  await page.goto('http://127.0.0.1:5173/playbook-library?view=repository');
  await page.getByRole('button', { name: /Repository/i }).click().catch(() => {});
  await page.getByRole('button', { name: /OCP 4\.20 Generated Catalog/i }).click();
  await page.screenshot({ path: 'reports/build_logs/catalog_expanded.png', fullPage: true });
  console.log('count', await page.locator('.factory-catalog-item').count());
  console.log('first text', await page.locator('.factory-catalog-item').first().textContent());
});
