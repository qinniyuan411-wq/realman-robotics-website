(function () {
  var isLocal = location.hostname === 'localhost' || location.hostname === '127.0.0.1';

  var ENDPOINT = isLocal
    ? { type: 'rest', url: 'http://127.0.0.1:54321/rest/v1/contact_submissions_cn', key: 'sb_publishable_ACJWlzQHlZjBrEguHvfOxg_3BJgxAaH' }
    : { type: 'edge', url: 'https://dwtfijvpelpavdslvyry.supabase.co/functions/v1/submit-contact', lang: 'cn' };

  var SUBMIT_COOLDOWN_MS = 60 * 1000;
  var STORAGE_KEY = 'rm_cta_last_submit_cn';
  // Cloudflare Turnstile site key（公开可见，区别于 secret key）
  // TODO: 注册 Turnstile 后替换为真实 site key
  var TURNSTILE_SITE_KEY = '0x4AAAAAADA6F3o-puTE8mWb';

  var MAX_LEN = { name: 100, email: 255, company: 200, details: 2000, subRegion: 64, subRegionLabel: 64 };
  var ALLOWED_REGIONS = ['china', 'overseas'];
  var ALLOWED_INQUIRY = ['partnership', 'sales', 'technical', 'media', 'careers', 'other'];
  var ALLOWED_OVERSEAS = ['asia-pacific', 'europe', 'north-america', 'south-america', 'middle-east-africa'];
  // 省份 / 直辖市 / 自治区 / 特别行政区：使用宽松字母+连字符模式（≤32字符），避免硬编码近 40 个值
  var SUB_REGION_RE = /^[a-z]{2,32}$/;

  var EMAIL_RE = /^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$/;
  var NAME_RE = /^[\p{L}\p{M}\s.\-·']{2,100}$/u;
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
    if (SCRIPT_TAG_RE.test(nameVal) || SCRIPT_TAG_RE.test(companyVal) || SCRIPT_TAG_RE.test(detailsVal) || SCRIPT_TAG_RE.test(subRegionLabel)) {
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
