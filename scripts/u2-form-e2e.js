/**
 * U-2 表单全流程验证（IT 验收 U-2）
 *
 * 表单字段没有 name 属性，全靠 placeholder + class + id 选择。
 * Turnstile widget 由 supabase-cta-cn.js 动态注入到 #contact-form 内 .cf-turnstile。
 *
 * Strategy:
 *   Part A — automated front-end:
 *     1) 打开 home 页，等待 #contact-form 出现
 *     2) 滚动表单进视区
 *     3) 用 placeholder 选择器填写 姓名 / 邮箱 / 公司
 *     4) 选 "中国地区" → "北京市" → "销售咨询"
 *     5) 填写需求
 *     6) 等 Cloudflare Turnstile iframe 注入并加载
 *     7) 截图：表单已填好，Turnstile 等你点
 *
 *   Part B — semi-automated back-end:
 *     8) 暂停脚本，让人类点 Turnstile checkbox
 *     9) 人类回到终端按 Enter
 *    10) 脚本点提交按钮
 *    11) 监听 fetch 到 *.supabase.co/functions/v1/* 的请求和响应
 *    12) 截图最终 UI 状态（成功 / 失败提示）
 *
 *   Output: evidence/u2-form/{01-filled,02-turnstile-solved,03-post-submit}.png
 *           + report.json with the captured network log
 */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const readline = require('readline');

const TARGET = 'https://www.qinnitest.you/cn/main/home.html';
const OUT = path.join(__dirname, '..', 'evidence', 'u2-form');
fs.mkdirSync(OUT, { recursive: true });

const ask = q => new Promise(r => {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  rl.question(q, () => { rl.close(); r(); });
});

(async () => {
  const browser = await chromium.launch({ headless: false, args: ['--start-maximized'] });
  const ctx = await browser.newContext({ viewport: null });
  const page = await ctx.newPage();

  const networkLog = [];
  page.on('response', async r => {
    const url = r.url();
    if (/supabase\.co\/functions\/v1|contact-form|\/api\//.test(url)) {
      let body = '';
      try { body = (await r.text()).slice(0, 1500); } catch {}
      networkLog.push({
        method: r.request().method(),
        url,
        status: r.status(),
        body,
        ts: new Date().toISOString(),
      });
      console.log(`    [net] ${r.request().method()} ${r.status()} ${url}`);
    }
  });
  page.on('pageerror', e => console.log('    [page-error]', e.message));

  console.log('[1/12] Opening', TARGET);
  await page.goto(TARGET, { waitUntil: 'networkidle', timeout: 60000 });

  console.log('[2/12] Waiting for #contact-form');
  await page.waitForSelector('#contact-form', { timeout: 15000 });
  await page.evaluate(() =>
    document.getElementById('contact-form').scrollIntoView({ block: 'center' })
  );
  await page.waitForTimeout(800);

  console.log('[3-5/12] Filling form fields');
  await page.locator('#contact-form input[placeholder*="姓名"]').fill('Test 自测张三');
  await page.locator('#contact-form input[placeholder*="工作邮箱"]').fill('qa-test@example.com');
  await page.locator('#contact-form input[placeholder*="公司名称"]').fill('睿尔曼（测试）');
  await page.selectOption('#region-select', 'china');
  await page.waitForTimeout(400);
  await page.selectOption('#province-select', 'beijing');
  // The 3rd select (consultation type) has no id; pick by required + first option-less default
  const consultSelects = await page.$$('#contact-form select.git-select');
  // sequential: region-select, province-select, overseas-select, then consult-type
  const consultSel = consultSelects[consultSelects.length - 1];
  if (consultSel) {
    await consultSel.selectOption('sales');
  }
  await page.locator('#contact-form textarea').fill(
    '这是 U-2 表单端到端自测，请忽略。需求：双臂人形机器人样机询价。'
  );

  console.log('[6/12] Verifying form values + Turnstile widget');
  const state = await page.evaluate(() => {
    const f = document.getElementById('contact-form');
    if (!f) return { exists: false };
    const inputs = [...f.querySelectorAll('input,textarea,select')].map(el => ({
      tag: el.tagName,
      ph: el.getAttribute('placeholder') || el.id || '',
      type: el.type,
      required: el.required,
      valueLen: (el.value || '').length,
      preview: (el.value || '').slice(0, 40),
    }));
    const tsIframe = [...document.querySelectorAll('iframe')].find(f =>
      /challenges\.cloudflare\.com/.test(f.src)
    );
    const tsContainer = document.querySelector('.cf-turnstile');
    return {
      exists: true,
      formAction: f.getAttribute('action') || '(submit handled by JS)',
      onsubmit: f.getAttribute('onsubmit'),
      inputs,
      turnstile: {
        containerPresent: !!tsContainer,
        sitekey: tsContainer?.getAttribute('data-sitekey') || null,
        iframeLoaded: !!tsIframe,
        iframeSrc: tsIframe?.src.slice(0, 120) || null,
      },
    };
  });
  console.log('    form state:', JSON.stringify(state, null, 2));

  console.log('[7/12] Screenshot 01-filled.png');
  await page.screenshot({ path: path.join(OUT, '01-filled.png'), fullPage: false });

  console.log('\n>>> ACTION REQUIRED <<<');
  console.log('  1) Switch to the Chromium window that just opened');
  console.log('  2) Click the Cloudflare Turnstile checkbox ("I am human")');
  console.log('  3) Wait for the green check');
  console.log('  4) Come back to this terminal and press Enter');
  console.log('     (If you do not see Turnstile, scroll the form into view first.)\n');
  await ask('Press Enter when Turnstile is solved... ');

  console.log('[8/12] Screenshot 02-turnstile-solved.png');
  await page.screenshot({ path: path.join(OUT, '02-turnstile-solved.png'), fullPage: false });

  const tokenInfo = await page.evaluate(() => {
    const tokInput = document.querySelector('input[name="cf-turnstile-response"]');
    return {
      tokenInputPresent: !!tokInput,
      tokenLength: tokInput?.value?.length || 0,
      tokenPrefix: tokInput?.value?.slice(0, 20) || '',
    };
  });
  console.log('    turnstile token:', tokenInfo);

  console.log('[9/12] Clicking submit button');
  await page.locator('#contact-form button[type="submit"]').click();

  console.log('[10/12] Waiting up to 8s for Edge Function response');
  await page.waitForTimeout(8000);

  console.log('[11/12] Screenshot 03-post-submit.png');
  await page.screenshot({ path: path.join(OUT, '03-post-submit.png'), fullPage: false });

  const postState = await page.evaluate(() => {
    const status = document.getElementById('form-status') || document.querySelector('[class*="success"],[class*="error"]');
    return {
      statusElText: status?.textContent?.trim().slice(0, 200) || null,
      bodyAlerts: [...document.querySelectorAll('[role="alert"]')].map(el => el.textContent.trim().slice(0, 200)),
    };
  });
  console.log('    post-submit UI:', postState);

  console.log('[12/12] Writing report.json');
  fs.writeFileSync(
    path.join(OUT, 'report.json'),
    JSON.stringify({ state, tokenInfo, postState, networkLog }, null, 2)
  );

  console.log('\n=== U-2 Network Log ===');
  if (networkLog.length === 0) {
    console.log('  (no requests to Supabase / Edge Function captured — see post-submit UI)');
  } else {
    networkLog.forEach(n =>
      console.log(`  ${n.method} ${n.status} ${n.url}\n    body: ${n.body.slice(0, 250)}`)
    );
  }

  console.log('\nDone. Press Enter to close the browser.');
  await ask('Press Enter to close... ');
  await browser.close();
})();
