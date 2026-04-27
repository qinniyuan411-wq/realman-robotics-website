/**
 * Loads cn/main/home.html via an in-process HTTP server (Node http) and
 * verifies that .material-symbols-outlined spans render as ligature glyphs.
 * Logs all font requests and their statuses for debugging.
 */
const { chromium } = require('playwright');
const http = require('http');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const PORT = 8771;
const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.woff2': 'font/woff2',
  '.woff': 'font/woff',
  '.ttf': 'font/ttf',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.webp': 'image/webp',
  '.svg': 'image/svg+xml',
  '.json': 'application/json',
  '.mp4': 'video/mp4',
};

const server = http.createServer((req, res) => {
  const u = decodeURI(req.url.split('?')[0]);
  const filePath = path.join(ROOT, u.replace(/^\/+/, ''));
  if (!filePath.startsWith(ROOT)) {
    res.writeHead(403); res.end('forbidden'); return;
  }
  fs.stat(filePath, (err, st) => {
    if (err || !st.isFile()) { res.writeHead(404); res.end('not found'); return; }
    res.writeHead(200, { 'Content-Type': MIME[path.extname(filePath).toLowerCase()] || 'application/octet-stream' });
    fs.createReadStream(filePath).pipe(res);
  });
});

(async () => {
  await new Promise((r) => server.listen(PORT, '127.0.0.1', r));

  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await ctx.newPage();

  const fontReqs = [];
  page.on('response', (r) => {
    const u = r.url();
    if (/\.(woff2?|ttf)(\?|$)/.test(u) || /material/i.test(u)) {
      fontReqs.push({ url: u.replace(`http://127.0.0.1:${PORT}`, ''), status: r.status() });
    }
  });
  page.on('requestfailed', (r) => {
    fontReqs.push({ url: r.url().replace(`http://127.0.0.1:${PORT}`, ''), status: 'FAILED', err: r.failure()?.errorText });
  });

  const PAGES = [
    '/cn/main/home.html',
    '/en/main/home.html',
    '/cn/products/rm65.html',
    '/en/products/rm65.html',
    '/cn/products/realbot-humanoid.html',
    '/cn/main/core-products.html',
    '/cn/main/about-us.html',
    '/en/main/about-us.html',
  ];
  let allPass = true;
  for (const PG of PAGES) {
    fontReqs.length = 0;
    await page.goto(`http://127.0.0.1:${PORT}${PG}`, { waitUntil: 'load', timeout: 30000 });
  await page.evaluate(async () => {
    // Force-load the icon font even though it's font-display: swap (browsers
    // would otherwise paint with a fallback first and only swap on the next
    // frame, racing the test).
    await document.fonts.load('24px "Material Symbols Outlined"', 'arrow_outward');
    await document.fonts.ready;
  });
  await page.waitForTimeout(800);

    const results = await page.evaluate(() => {
      const out = { iconCount: 0, sample: [], renderedAsGlyph: 0, literalText: 0 };
      document.querySelectorAll('span.material-symbols-outlined').forEach((el) => {
        out.iconCount++;
        const cs = getComputedStyle(el);
        const fontSizePx = parseFloat(cs.fontSize) || 24;
        // Measure the actual rendered text width via a Range, NOT the span box —
        // many icons are display:block / flex children whose box width is the
        // parent column width (e.g. 194px), even when the glyph inside is just 28px.
        let textW = 0;
        if (el.firstChild && el.firstChild.nodeType === Node.TEXT_NODE) {
          const range = document.createRange();
          range.selectNodeContents(el);
          textW = range.getBoundingClientRect().width;
        } else {
          textW = el.getBoundingClientRect().width;
        }
        // A correctly-rendered ligature is ~font-size wide (single glyph cluster);
        // literal fallback text expands beyond ~2× font-size.
        const threshold = fontSizePx * 2;
        if (textW > 0 && textW <= threshold) out.renderedAsGlyph++;
        else if (textW > threshold) out.literalText++;
        if (out.sample.length < 3 && textW > threshold) {
          out.sample.push({
            text: el.textContent.trim(),
            textW: Math.round(textW),
            fs: cs.fontSize,
            ff: cs.fontFamily,
          });
        }
      });
      return out;
    });

    const woff2Loaded = fontReqs.some((r) => /MaterialSymbolsOutlined-subset\.woff2/.test(r.url) && r.status === 200);
    const ok = woff2Loaded && results.iconCount >= 3 && results.literalText === 0;
    allPass = allPass && ok;
    console.log(`[${PG}]  icons=${results.iconCount}  glyph=${results.renderedAsGlyph}  literal=${results.literalText}  woff2=${woff2Loaded}  ${ok ? 'PASS' : 'FAIL'}  sample=${JSON.stringify(results.sample)}`);
  }

  await browser.close();
  server.close();

  console.log(allPass ? '\nALL PAGES PASS' : '\nSOME PAGES FAILED');
  process.exit(allPass ? 0 : 1);
})().catch((e) => { console.error(e); process.exit(2); });
