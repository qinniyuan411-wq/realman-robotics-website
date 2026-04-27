(function () {
  var isLocal = location.hostname === 'localhost' || location.hostname === '127.0.0.1';

  var ENDPOINT = isLocal
    ? { type: 'rest', url: 'http://127.0.0.1:54321/rest/v1/contact_submissions_cn', key: 'sb_publishable_ACJWlzQHlZjBrEguHvfOxg_3BJgxAaH' }
    : { type: 'edge', url: 'https://dwtfijvpelpavdslvyry.supabase.co/functions/v1/submit-contact', lang: 'cn' };

  var SUBMIT_COOLDOWN_MS = 60 * 1000;
  var STORAGE_KEY = 'rm_cta_last_submit_cn';
  // Cloudflare Turnstile site key（公开值，可前端可见；secret key 仅在 Edge Function env vars）
  // 已是生产真实 key，对应 hostnames：qinnitest.you / localhost / 127.0.0.1
  var TURNSTILE_SITE_KEY = '0x4AAAAAADA6F3o-puTE8mWb';

  var MAX_LEN = { name: 100, email: 255, company: 200, details: 2000, subRegion: 64, subRegionLabel: 64 };
  var ALLOWED_REGIONS = ['china', 'overseas'];
  var ALLOWED_INQUIRY = ['partnership', 'sales', 'technical', 'media', 'careers', 'other'];
  var ALLOWED_OVERSEAS = ['asia-pacific', 'europe', 'north-america', 'south-america', 'middle-east-africa'];
  // 省份 / 直辖市 / 自治区 / 特别行政区：使用宽松字母+连字符模式（≤32字符），避免硬编码近 40 个值
  var SUB_REGION_RE = /^[a-z]{2,32}$/;

  // C-6 修复（2026-04-27 第四轮）：客户端正则与服务端 Edge Function 严格对齐。
  // 服务端见 supabase/functions/submit-contact/index.ts EMAIL_RE / NAME_RE / DANGEROUS_RE。
  // 客户端做体验性预校验，服务端做权威校验；两端规则保持完全一致以避免「客户端通过、服务端拒绝」错觉。
  var EMAIL_RE = /^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$/;
  var NAME_RE = /^[\p{L}\p{M}\s.\-·']{2,100}$/u;
  var DANGEROUS_RE = /<\s*\/?\s*(script|iframe|object|embed|link|meta|style|svg|img|video|audio|source|details|marquee|form|input|textarea|select|button|applet|base|body|frame|frameset|noscript|template|isindex|portal)\b|\bon[a-z]{2,32}\s*=|(?:^|[\s"'])(?:javascript|vbscript|data)\s*:\s*(?:text\/html|application\/|[^\s])/i;

  function stripTags(s) {
    if (!s) return '';
    return String(s).replace(/<[^>]*>/g, '').replace(/[\u0000-\u001F\u007F]/g, '').trim();
  }

  function setBtnContent(btn, text, iconName) {
    while (btn.firstChild) btn.removeChild(btn.firstChild);
    btn.appendChild(document.createTextNode(text));
    if (iconName) {
      var icon = document.createElement('span');
      icon.className = 'material-symbols-outlined';
      icon.style.fontSize = '16px';
      icon.style.marginLeft = '8px';
      icon.textContent = iconName;
      btn.appendChild(icon);
    }
  }

  function snapshotBtn(btn) {
    var frag = document.createDocumentFragment();
    Array.prototype.slice.call(btn.childNodes).forEach(function (n) {
      frag.appendChild(n.cloneNode(true));
    });
    return frag;
  }

  function restoreBtn(btn, snapshot) {
    while (btn.firstChild) btn.removeChild(btn.firstChild);
    btn.appendChild(snapshot);
  }

  var form = document.getElementById('contact-form');
  if (!form) return;

  form.removeAttribute('onsubmit');

  // 动态注入 Cloudflare Turnstile（生产环境）
  if (ENDPOINT.type === 'edge' && TURNSTILE_SITE_KEY && TURNSTILE_SITE_KEY.indexOf('__') !== 0) {
    var submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn && !document.getElementById('cf-turnstile-wrap')) {
      var wrap = document.createElement('div');
      wrap.id = 'cf-turnstile-wrap';
      wrap.style.cssText = 'margin:16px 0;display:flex;justify-content:center;';
      var widget = document.createElement('div');
      widget.className = 'cf-turnstile';
      widget.setAttribute('data-sitekey', TURNSTILE_SITE_KEY);
      widget.setAttribute('data-theme', 'dark');
      widget.setAttribute('data-size', 'flexible');
      widget.setAttribute('data-language', 'zh-cn');
      wrap.appendChild(widget);
      submitBtn.parentNode.insertBefore(wrap, submitBtn);
    }
    if (!document.querySelector('script[data-cf-turnstile]')) {
      var s = document.createElement('script');
      s.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js';
      s.async = true;
      s.defer = true;
      s.setAttribute('data-cf-turnstile', '1');
      document.head.appendChild(s);
    }
  }

  // C-5 隐私合规（2026-04-27 第四轮）：表单提交前展示隐私告知与同意链接，
  // 满足 PIPL 第 14、17、23 条对告知义务的要求。链接指向 /cn/main/privacy.html。
  (function injectPrivacyNotice () {
    var submitBtn = form.querySelector('button[type="submit"]');
    if (!submitBtn || document.getElementById('cta-privacy-notice')) return;
    var note = document.createElement('div');
    note.id = 'cta-privacy-notice';
    note.style.cssText = 'margin:0 0 16px 0; font-size:11px; line-height:1.7; color:rgba(255,255,255,0.45); letter-spacing:-0.01em;';
    note.innerHTML = '提交即表示您已阅读并同意我们的 <a href="/cn/main/privacy.html" target="_blank" rel="noopener noreferrer" style="color:#3B82F6; text-decoration:underline;">《隐私政策》</a>。我们仅收集姓名、工作邮箱、公司名称、地区、咨询类型与详细需求，用于响应您本次咨询，<strong>不会</strong>用于其他用途或转售。';
    submitBtn.parentNode.insertBefore(note, submitBtn);
  })();

  var nameI = form.querySelectorAll('input.git-input')[0];
  var emailI = form.querySelectorAll('input.git-input')[1];
  var companyI = form.querySelectorAll('input.git-input')[2];
  var detailsI = form.querySelector('textarea.git-input');
  if (nameI) nameI.setAttribute('maxlength', MAX_LEN.name);
  if (emailI) { emailI.setAttribute('maxlength', MAX_LEN.email); emailI.setAttribute('type', 'email'); }
  if (companyI) companyI.setAttribute('maxlength', MAX_LEN.company);
  if (detailsI) detailsI.setAttribute('maxlength', MAX_LEN.details);

  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    var btn = form.querySelector('button[type="submit"]');
    if (!btn || btn.disabled) return;

    try {
      var lastTs = parseInt(localStorage.getItem(STORAGE_KEY) || '0', 10);
      if (lastTs && Date.now() - lastTs < SUBMIT_COOLDOWN_MS) {
        var waitSec = Math.ceil((SUBMIT_COOLDOWN_MS - (Date.now() - lastTs)) / 1000);
        alert('操作过于频繁，请 ' + waitSec + ' 秒后重试。');
        return;
      }
    } catch (_) {}

    var btnSnapshot = snapshotBtn(btn);
    setBtnContent(btn, '提交中...', 'hourglass_top');
    btn.disabled = true;

    var nameVal = nameI ? nameI.value.trim() : '';
    var emailVal = emailI ? emailI.value.trim() : '';
    var companyVal = companyI ? companyI.value.trim() : '';

    var regionEl = document.getElementById('region-select');
    var provinceEl = document.getElementById('province-select');
    var overseasEl = document.getElementById('overseas-select');
    var regionVal = regionEl ? regionEl.value : '';
    var subRegionVal = '';
    var subRegionLabel = '';

    if (regionVal === 'china' && provinceEl && provinceEl.value) {
      subRegionVal = provinceEl.value;
      subRegionLabel = provinceEl.options[provinceEl.selectedIndex].text;
    } else if (regionVal === 'overseas' && overseasEl && overseasEl.value) {
      subRegionVal = overseasEl.value;
      subRegionLabel = overseasEl.options[overseasEl.selectedIndex].text;
    }

    var inquirySelects = form.querySelectorAll('select.git-select:not(#region-select):not(#province-select):not(#overseas-select)');
    var inquiryTypeVal = inquirySelects[0] ? inquirySelects[0].value : '';
    var detailsVal = detailsI ? detailsI.value.trim() : '';

    function fail(msg) {
      restoreBtn(btn, btnSnapshot);
      btn.disabled = false;
      alert(msg);
    }

    if (!nameVal || !emailVal || !companyVal || !regionVal || !subRegionVal || !inquiryTypeVal) {
      return fail('请填写所有必填项。');
    }
    if (nameVal.length > MAX_LEN.name || !NAME_RE.test(nameVal)) {
      return fail('请输入有效的姓名（2-100 字符）。');
    }
    if (emailVal.length > MAX_LEN.email || !EMAIL_RE.test(emailVal)) {
      return fail('请输入有效的邮箱地址。');
    }
    if (companyVal.length > MAX_LEN.company) {
      return fail('公司名称过长（最多 200 字符）。');
    }
    if (detailsVal.length > MAX_LEN.details) {
      return fail('详细内容过长（最多 2000 字符）。');
    }
    if (DANGEROUS_RE.test(nameVal) || DANGEROUS_RE.test(companyVal) || DANGEROUS_RE.test(detailsVal) || DANGEROUS_RE.test(subRegionLabel)) {
      return fail('提交内容包含禁止字符。');
    }
    if (ALLOWED_REGIONS.indexOf(regionVal) === -1) {
      return fail('请选择有效的地区。');
    }
    if (ALLOWED_INQUIRY.indexOf(inquiryTypeVal) === -1) {
      return fail('请选择有效的咨询类型。');
    }
    if (subRegionVal.length > MAX_LEN.subRegion || !SUB_REGION_RE.test(subRegionVal)) {
      return fail('请选择有效的子区域。');
    }
    if (regionVal === 'overseas' && ALLOWED_OVERSEAS.indexOf(subRegionVal) === -1) {
      return fail('请选择有效的海外区域。');
    }
    if (subRegionLabel.length > MAX_LEN.subRegionLabel) {
      return fail('子区域名称过长。');
    }

    var payload = {
      name: nameVal,
      work_email: emailVal,
      company: companyVal,
      region: regionVal,
      sub_region: subRegionVal,
      sub_region_label: stripTags(subRegionLabel),
      inquiry_type: inquiryTypeVal,
      details: stripTags(detailsVal),
      page_source: stripTags(document.title || location.pathname).slice(0, 200)
    };

    if (ENDPOINT.type === 'edge') {
      var ts = (window.turnstile && form.querySelector('[name="cf-turnstile-response"]'))
        ? form.querySelector('[name="cf-turnstile-response"]').value : '';
      if (!ts) {
        return fail('请先完成人机验证。');
      }
      payload['cf-turnstile-response'] = ts;
      payload.lang = ENDPOINT.lang;
    }

    try {
      var headers = { 'Content-Type': 'application/json' };
      if (ENDPOINT.type === 'rest') {
        headers['apikey'] = ENDPOINT.key;
        headers['Authorization'] = 'Bearer ' + ENDPOINT.key;
        headers['Prefer'] = 'return=minimal';
      }

      var res = await fetch(ENDPOINT.url, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        throw new Error('HTTP_' + res.status);
      }

      try { localStorage.setItem(STORAGE_KEY, String(Date.now())); } catch (_) {}

      setBtnContent(btn, '已提交', 'check_circle');
      btn.style.backgroundColor = '#22c55e';
      form.querySelectorAll('input, textarea').forEach(function (el) { el.value = ''; });
      form.querySelectorAll('select').forEach(function (el) { el.selectedIndex = 0; });
      var subWrap = document.getElementById('sub-region-wrap');
      if (subWrap) subWrap.style.display = 'none';
      if (window.turnstile && typeof window.turnstile.reset === 'function') {
        try { window.turnstile.reset(); } catch (_) {}
      }
      setTimeout(function () {
        restoreBtn(btn, btnSnapshot);
        btn.disabled = false;
        btn.style.backgroundColor = '';
      }, 3000);
    } catch (err) {
      console.error('CTA submit error:', err);
      fail('提交失败，请稍后重试。');
    }
  });
})();
