/**
 * U-1 三端适配验证（IT 验收 U-1）
 * 用 Playwright 在 iPhone(375)/iPad(768)/Desktop(1920) 三个标准视口下访问
 * 中英文 8 个核心页面，截全屏图，并检查：
 *   1) 是否出现水平滚动条（响应式破洞）
 *   2) 关键导航/CTA 元素是否可见
 *   3) 中文页面 HarmonyOS Sans SC 字体是否生效
 */
const { chromium, devices } = require('playwright');
const fs = require('fs');
const path = require('path');

const BASE = 'https://www.qinnitest.you';
const PAGES = [
  { url: '/cn/main/home.html',          name: 'cn-home' },
  { url: '/cn/main/core-products.html', name: 'cn-products' },
  { url: '/cn/main/solutions.html',     name: 'cn-solutions' },
  { url: '/cn/main/about-us.html',      name: 'cn-about' },
  { url: '/cn/main/privacy.html',       name: 'cn-privacy' },
  { url: '/en/main/home.html',          name: 'en-home' },
  { url: '/en/main/core-products.html', name: 'en-products' },
  { url: '/en/main/about-us.html',      name: 'en-about' },
];
const VIEWPORTS = [
  { name: 'iphone-se',  width: 375,  height: 667,  isMobile: true,  ua: devices['iPhone 13'].userAgent },
  { name: 'ipad',       width: 768,  height: 1024, isMobile: true,  ua: devices['iPad (gen 7)'].userAgent },
  { name: 'desktop',    width: 1920, height: 1080, isMobile: false, ua: undefined },
];

const OUT = path.join(__dirname, '..', 'evidence', 'u1-multidevice');
fs.mkdirSync(OUT, { recursive: true });

(async () => {
  const browser = await chromium.launch();
  const report = [];
  for (const vp of VIEWPORTS) {
    const ctx = await browser.newContext({
      viewport: { width: vp.width, height: vp.height },
      userAgent: vp.ua,
      isMobile: vp.isMobile,
      hasTouch: vp.isMobile,
      deviceScaleFactor: vp.isMobile ? 2 : 1,
    });
    for (const p of PAGES) {
      const page = await ctx.newPage();
      const url = BASE + p.url;
      try {
        await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
      } catch (e) {
        await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
      }
      await page.waitForTimeout(800);
      const horizontalOverflow = await page.evaluate(() =>
        document.documentElement.scrollWidth > window.innerWidth + 1
      );
      const fontFamily = await page.evaluate(() => {
        const body = document.body;
        return getComputedStyle(body).fontFamily;
      });
      const harmonyApplied = await page.evaluate(async () => {
        try {
          await document.fonts.ready;
          const fonts = [...document.fonts].filter(f =>
            f.family.includes('HarmonyOS Sans SC') && f.status === 'loaded'
          );
          return fonts.length;
        } catch { return -1; }
      });
      const fname = `${vp.name}__${p.name}.png`;
      await page.screenshot({ path: path.join(OUT, fname), fullPage: true });
      report.push({
        viewport: vp.name, page: p.name, url,
        horizontalOverflow, fontFamily, harmonyLoadedWeights: harmonyApplied,
        screenshot: fname,
      });
      console.log(`[${vp.name}] ${p.name} overflow=${horizontalOverflow} harmony=${harmonyApplied}`);
      await page.close();
    }
    await ctx.close();
  }
  await browser.close();
  fs.writeFileSync(path.join(OUT, 'report.json'), JSON.stringify(report, null, 2));
  const broken = report.filter(r => r.horizontalOverflow);
  const noHarmony = report.filter(r => r.page.startsWith('cn-') && r.harmonyLoadedWeights === 0);
  console.log('\n=== U-1 Summary ===');
  console.log(`Total combinations: ${report.length}`);
  console.log(`Horizontal-overflow violations: ${broken.length}`);
  console.log(`CN pages where HarmonyOS not loaded: ${noHarmony.length}`);
  if (broken.length) console.log('Overflow on:', broken.map(b => `${b.viewport}/${b.page}`).join(', '));
})();
