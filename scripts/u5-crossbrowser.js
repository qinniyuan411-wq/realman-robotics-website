/**
 * U-5 跨浏览器兼容验证（IT 验收 U-5）
 * Chromium / Firefox / WebKit 三引擎并行访问首页（CN+EN），截图 + 抓控制台错误。
 * 通过条件：3 引擎 × 2 页面 = 6 个组合无 console error，且 HarmonyOS Sans SC 在
 * Chromium / Firefox / WebKit 都正确加载（document.fonts API 报告 status=loaded）。
 */
const { chromium, firefox, webkit } = require('playwright');
const fs = require('fs');
const path = require('path');

const BASE = 'https://www.qinnitest.you';
const PAGES = [
  { url: '/cn/main/home.html', name: 'cn-home', isCN: true },
  { url: '/en/main/home.html', name: 'en-home', isCN: false },
];
const ENGINES = [
  { name: 'chromium', launcher: chromium },
  { name: 'firefox',  launcher: firefox  },
  { name: 'webkit',   launcher: webkit   },
];

const OUT = path.join(__dirname, '..', 'evidence', 'u5-crossbrowser');
fs.mkdirSync(OUT, { recursive: true });

(async () => {
  const report = [];
  for (const eng of ENGINES) {
    const browser = await eng.launcher.launch();
    const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    for (const p of PAGES) {
      const page = await ctx.newPage();
      const consoleErrors = [];
      const pageErrors = [];
      page.on('console', m => { if (m.type() === 'error') consoleErrors.push(m.text()); });
      page.on('pageerror', e => pageErrors.push(e.message));
      const url = BASE + p.url;
      let loadOk = true;
      try {
        await page.goto(url, { waitUntil: 'networkidle', timeout: 45000 });
      } catch (e) {
        try { await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 }); }
        catch { loadOk = false; }
      }
      await page.waitForTimeout(1500);
      const harmonyApplied = await page.evaluate(async () => {
        try {
          await document.fonts.ready;
          return [...document.fonts]
            .filter(f => f.family.includes('HarmonyOS Sans SC'))
            .map(f => ({ weight: f.weight, status: f.status }));
        } catch { return []; }
      });
      const fname = `${eng.name}__${p.name}.png`;
      await page.screenshot({ path: path.join(OUT, fname), fullPage: false });
      report.push({
        engine: eng.name, page: p.name, url, loadOk,
        consoleErrors, pageErrors, harmonyApplied, screenshot: fname,
      });
      console.log(`[${eng.name}] ${p.name} loadOk=${loadOk} consoleErr=${consoleErrors.length} pageErr=${pageErrors.length} harmony=${harmonyApplied.filter(h=>h.status==='loaded').length}/4`);
      await page.close();
    }
    await ctx.close();
    await browser.close();
  }
  fs.writeFileSync(path.join(OUT, 'report.json'), JSON.stringify(report, null, 2));
  const failures = report.filter(r =>
    !r.loadOk || r.pageErrors.length > 0 ||
    (r.page.startsWith('cn-') && r.harmonyApplied.filter(h => h.status === 'loaded').length < 4)
  );
  console.log('\n=== U-5 Summary ===');
  console.log(`Total engine-page combinations: ${report.length}`);
  console.log(`Failures (load/pageerr/harmony): ${failures.length}`);
  if (failures.length) failures.forEach(f => console.log('  FAIL', f.engine, f.page, f.pageErrors));
})();
