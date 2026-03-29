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
      'SENDING...<span class="material-symbols-outlined" style="font-size:16px;margin-left:8px;">hourglass_top</span>';
    btn.disabled = true;

    var inputs = form.querySelectorAll('input.git-input');
    var selects = form.querySelectorAll('select.git-select');
    var textarea = form.querySelector('textarea.git-input');

    var nameVal = inputs[0] ? inputs[0].value.trim() : '';
    var emailVal = inputs[1] ? inputs[1].value.trim() : '';
    var companyVal = inputs[2] ? inputs[2].value.trim() : '';
    var regionVal = selects[0] ? selects[0].value : '';
    var inquiryTypeVal = selects[1] ? selects[1].value : '';
    var detailsVal = textarea ? textarea.value.trim() : '';

    if (!nameVal || !emailVal || !companyVal || !regionVal || !inquiryTypeVal) {
      btn.innerHTML = btnOriginal;
      btn.disabled = false;
      alert('Please fill in all required fields.');
      return;
    }

    try {
      var res = await fetch(SUPABASE_URL + '/rest/v1/contact_submissions_en', {
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
        'SENT ✓<span class="material-symbols-outlined" style="font-size:16px;margin-left:8px;">check_circle</span>';
      btn.style.backgroundColor = '#22c55e';
      form.querySelectorAll('input, textarea').forEach(function (el) {
        el.value = '';
      });
      form.querySelectorAll('select').forEach(function (el) {
        el.selectedIndex = 0;
      });
      setTimeout(function () {
        btn.innerHTML = btnOriginal;
        btn.disabled = false;
        btn.style.backgroundColor = '';
      }, 3000);
    } catch (err) {
      console.error('CTA submit error:', err);
      btn.innerHTML = btnOriginal;
      btn.disabled = false;
      alert('Submission failed. Please try again.\n' + err.message);
    }
  });
})();
