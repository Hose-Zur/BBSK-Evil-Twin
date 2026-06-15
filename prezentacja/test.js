const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('http://localhost:3030/6', { waitUntil: 'networkidle' });
  await page.screenshot({ path: 'slide6.png' });
  await browser.close();
})();
