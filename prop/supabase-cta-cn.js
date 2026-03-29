(function () {
  var SUPABASE_URL = 'https://dwtfijvpelpavdslvyry.supabase.co';
  var SUPABASE_KEY = 'sb_publishable_p0hMaphSABTlKZiLXtDcBQ_ZU_Nvel0';

  var form = document.getElementById('contact-form');
  if (!form) return;

  form.removeAttribute('onsubmit');

  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    var btn = form.querySelector('button[type="submit"]');
    if (!btn || btn.disabled) return;

    var btnOriginal = btn.innerHTML;
    btn.innerHTML =
      '提交中...<span class="material-symbols-outlined" style="font-size:16px;margin-left:8px;">hourglass_top</span>';
    btn.disabled = true;

    var inputs = form.querySelectorAll('input.git-input');
    var textarea = form.querySelector('textarea.git-input');

    var nameVal = inputs[0] ? inputs[0].value.trim() : '';
    var emailVal = inputs[1] ? inputs[1].value.trim() : '';
    var companyVal = inputs[2] ? inputs[2].value.trim() : '';

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

    var detailsVal = textarea ? textarea.value.trim() : '';

    if (!nameVal || !emailVal || !companyVal || !regionVal || !subRegionVal || !inquiryTypeVal) {
      btn.innerHTML = btnOriginal;
      btn.disabled = false;
      alert('请填写所有必填项');
      return;
    }

    try {
      var res = await fetch(SUPABASE_URL + '/rest/v1/contact_submissions_cn', {
        method: 'POST',
        headers: {
          'apikey': SUPABASE_KEY,
          'Authorization': 'Bearer ' + SUPABASE_KEY,
          'Content-Type': 'application/json',
          'Prefer': 'return=minimal'
        },
        body: JSON.stringify({
          name: nameVal,
          work_email: emailVal,
          company: companyVal,
          region: regionVal,
          sub_region: subRegionVal,
          sub_region_label: subRegionLabel,
          inquiry_type: inquiryTypeVal,
          details: detailsVal,
          page_source: document.title || location.pathname
        })
      });

      if (!res.ok) {
        var errText = await res.text();
        throw new Error('HTTP ' + res.status + ': ' + errText);
      }

      btn.innerHTML =
        '已提交 ✓<span class="material-symbols-outlined" style="font-size:16px;margin-left:8px;">check_circle</span>';
      btn.style.backgroundColor = '#22c55e';
      form.querySelectorAll('input, textarea').forEach(function (el) {
        el.value = '';
      });
      form.querySelectorAll('select').forEach(function (el) {
        el.selectedIndex = 0;
      });
      var subWrap = document.getElementById('sub-region-wrap');
      if (subWrap) subWrap.style.display = 'none';
      setTimeout(function () {
        btn.innerHTML = btnOriginal;
        btn.disabled = false;
        btn.style.backgroundColor = '';
      }, 3000);
    } catch (err) {
      console.error('CTA submit error:', err);
      btn.innerHTML = btnOriginal;
      btn.disabled = false;
      alert('提交失败，请稍后重试。\n' + err.message);
    }
  });
})();
