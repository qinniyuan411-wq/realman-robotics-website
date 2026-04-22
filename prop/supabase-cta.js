(function () {
  var isLocal = location.hostname === 'localhost' || location.hostname === '127.0.0.1';

  // 表单提交端点：本地走 Supabase REST，生产走 Edge Function 代理
  var ENDPOINT = isLocal
    ? { type: 'rest', url: 'http://127.0.0.1:54321/rest/v1/contact_submissions_en', key: 'sb_publishable_ACJWlzQHlZjBrEguHvfOxg_3BJgxAaH' }
    : { type: 'edge', url: 'https://dwtfijvpelpavdslvyry.supabase.co/functions/v1/submit-contact', lang: 'en' };

  var SUBMIT_COOLDOWN_MS = 60 * 1000;
  var STORAGE_KEY = 'rm_cta_last_submit_en';
  // Cloudflare Turnstile site key（公开可见，区别于 secret key）
  // TODO: 注册 Turnstile 后替换为真实 site key
  var TURNSTILE_SITE_KEY = '0x4AAAAAADA6F3o-puTE8mWb';

  var MAX_LEN = { name: 100, email: 255, company: 200, details: 2000 };
  var ALLOWED_REGIONS = ['asia-pacific', 'europe', 'north-america', 'south-america', 'middle-east-africa'];
  var ALLOWED_INQUIRY = ['partnership', 'sales', 'technical', 'media', 'careers', 'other'];

  var EMAIL_RE = /^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$/;
  var NAME_RE = /^[\p{L}\p{M}\s.\-']{2,100}$/u;
  var SCRIPT_TAG_RE = /<\s*\/?\s*(script|iframe|object|embed|link|meta|style|svg|on\w+)/i;

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

  // 限制 input/textarea 长度（前端硬约束）
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

    // 客户端节流（60s 一次）
    try {
      var lastTs = parseInt(localStorage.getItem(STORAGE_KEY) || '0', 10);
      if (lastTs && Date.now() - lastTs < SUBMIT_COOLDOWN_MS) {
        var waitSec = Math.ceil((SUBMIT_COOLDOWN_MS - (Date.now() - lastTs)) / 1000);
        alert('Please wait ' + waitSec + ' seconds before submitting again.');
        return;
      }
    } catch (_) { /* localStorage may be unavailable */ }

    var btnSnapshot = snapshotBtn(btn);
    setBtnContent(btn, 'SENDING...', 'hourglass_top');
    btn.disabled = true;

    var nameVal = nameI ? nameI.value.trim() : '';
    var emailVal = emailI ? emailI.value.trim() : '';
    var companyVal = companyI ? companyI.value.trim() : '';
    var selects = form.querySelectorAll('select.git-select');
    var regionVal = selects[0] ? selects[0].value : '';
    var inquiryTypeVal = selects[1] ? selects[1].value : '';
    var detailsVal = detailsI ? detailsI.value.trim() : '';

    function fail(msg) {
      restoreBtn(btn, btnSnapshot);
      btn.disabled = false;
      alert(msg);
    }

    if (!nameVal || !emailVal || !companyVal || !regionVal || !inquiryTypeVal) {
      return fail('Please fill in all required fields.');
    }
    if (nameVal.length > MAX_LEN.name || !NAME_RE.test(nameVal)) {
      return fail('Please enter a valid name (2-100 characters).');
    }
    if (emailVal.length > MAX_LEN.email || !EMAIL_RE.test(emailVal)) {
      return fail('Please enter a valid email address.');
    }
    if (companyVal.length > MAX_LEN.company) {
      return fail('Company name is too long (max 200 characters).');
    }
    if (detailsVal.length > MAX_LEN.details) {
      return fail('Message is too long (max 2000 characters).');
    }
    if (SCRIPT_TAG_RE.test(nameVal) || SCRIPT_TAG_RE.test(companyVal) || SCRIPT_TAG_RE.test(detailsVal)) {
      return fail('Submission contains forbidden content.');
    }
    if (ALLOWED_REGIONS.indexOf(regionVal) === -1) {
      return fail('Please select a valid region.');
    }
    if (ALLOWED_INQUIRY.indexOf(inquiryTypeVal) === -1) {
      return fail('Please select a valid inquiry type.');
    }

    var payload = {
      name: nameVal,
      work_email: emailVal,
      company: companyVal,
      region: regionVal,
      inquiry_type: inquiryTypeVal,
      details: stripTags(detailsVal),
      page_source: stripTags(document.title || location.pathname).slice(0, 200)
    };

    // Cloudflare Turnstile token (生产路径上才需要)
    if (ENDPOINT.type === 'edge') {
      var ts = (window.turnstile && form.querySelector('[name="cf-turnstile-response"]'))
        ? form.querySelector('[name="cf-turnstile-response"]').value : '';
      if (!ts) {
        return fail('Please complete the human verification.');
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

      setBtnContent(btn, 'SENT', 'check_circle');
      btn.style.backgroundColor = '#22c55e';
      form.querySelectorAll('input, textarea').forEach(function (el) { el.value = ''; });
      form.querySelectorAll('select').forEach(function (el) { el.selectedIndex = 0; });
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
      fail('Submission failed. Please try again later.');
    }
  });
})();
