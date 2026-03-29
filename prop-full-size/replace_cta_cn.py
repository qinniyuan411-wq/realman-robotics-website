import os, sys, re
sys.stdout.reconfigure(encoding='utf-8')

BASE = r'C:\Users\Qinni Yuan\Desktop\realman-robotics-website\cn'

NEW_CTA = r'''<!-- CTA + FOOTER: GET IN TOUCH -->
<!-- ============================================================ -->
<style>
  .git-input, .git-select {
    width:100%; background:rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.1);
    border-radius:0.25rem; padding:14px 16px; font-size:15px; font-weight:400;
    letter-spacing:-0.05em; color:#fff; outline:none; font-family:Inter,sans-serif;
    transition:border-color 0.3s, background 0.3s;
  }
  .git-input::placeholder { color:rgba(255,255,255,0.3); }
  .git-input:focus, .git-select:focus {
    border-color:#3B82F6; background:rgba(59,130,246,0.06);
  }
  .git-select { appearance:none; cursor:pointer;
    background-image:url("data:image/svg+xml,%3Csvg width='12' height='8' viewBox='0 0 12 8' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1.5L6 6.5L11 1.5' stroke='rgba(255,255,255,0.35)' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
    background-repeat:no-repeat; background-position:right 16px center;
  }
  .git-select option { background:#111; color:#fff; }

  .cta-grid { grid-template-columns: 1fr !important; gap: 32px !important; }
  .cta-form-row { grid-template-columns: 1fr !important; }
  .cta-wrap { padding: 20px !important; }
  #git-title { font-size: 28px !important; }
  #contact-form button[type="submit"] { width: 100%; justify-content: center; }
  @media (min-width: 768px) {
    .cta-grid { grid-template-columns: 1.6fr 0.7fr !important; gap: 64px !important; }
    .cta-form-row { grid-template-columns: 1fr 1fr !important; }
    .cta-wrap { padding: 32px !important; }
    #git-title { font-size: 36px !important; }
    #contact-form button[type="submit"] { width: auto !important; }
    .cta-grid a[href^="mailto:"], .cta-grid a[href^="tel:"] { font-size: 20px !important; }
  }
</style>
<section id="get-in-touch" class="w-full relative" style="font-family:Inter,sans-serif; min-height:calc(100vh - 56px); background:#000; display:flex; flex-direction:column;">
  <div class="cta-wrap" style="padding:32px; flex:1; display:flex; flex-direction:column; max-width:1280px;">
    <h2 id="git-title" style="font-size:36px; font-weight:400; line-height:1; color:#fff; letter-spacing:-0.05em; margin-bottom:12px; display:inline-block; overflow:hidden; white-space:nowrap; width:0;">联系我们</h2>
    <p style="font-size:14px; font-weight:400; letter-spacing:-0.05em; color:rgba(255,255,255,0.4); margin-bottom:36px;">如有任何疑问或合作意向，欢迎随时与我们联系</p>

    <div class="cta-grid" style="flex:1; display:grid; grid-template-columns:1.6fr 0.7fr; gap:64px; align-content:start;">

      <form id="contact-form" style="max-width:100%;" onsubmit="return false;">
        <div class="cta-form-row" style="display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-bottom:16px;">
          <input type="text" class="git-input" placeholder="姓名 *" required>
          <input type="email" class="git-input" placeholder="工作邮箱 *" required>
        </div>
        <div class="cta-form-row" style="display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-bottom:16px;">
          <input type="text" class="git-input" placeholder="公司名称 *" required>
          <select id="region-select" class="git-select" required onchange="handleRegionChange(this.value)">
            <option value="" disabled selected>所在地区 *</option>
            <option value="china">中国地区</option>
            <option value="overseas">海外地区</option>
          </select>
        </div>
        <div id="sub-region-wrap" style="display:none; margin-bottom:16px;">
          <select id="province-select" class="git-select" style="display:none;">
            <option value="" disabled selected>省 / 自治区 / 直辖市 *</option>
            <optgroup label="直辖市">
              <option value="beijing">北京市</option>
              <option value="tianjin">天津市</option>
              <option value="shanghai">上海市</option>
              <option value="chongqing">重庆市</option>
            </optgroup>
            <optgroup label="省">
              <option value="hebei">河北省</option>
              <option value="shanxi">山西省</option>
              <option value="liaoning">辽宁省</option>
              <option value="jilin">吉林省</option>
              <option value="heilongjiang">黑龙江省</option>
              <option value="jiangsu">江苏省</option>
              <option value="zhejiang">浙江省</option>
              <option value="anhui">安徽省</option>
              <option value="fujian">福建省</option>
              <option value="jiangxi">江西省</option>
              <option value="shandong">山东省</option>
              <option value="henan">河南省</option>
              <option value="hubei">湖北省</option>
              <option value="hunan">湖南省</option>
              <option value="guangdong">广东省</option>
              <option value="hainan">海南省</option>
              <option value="sichuan">四川省</option>
              <option value="guizhou">贵州省</option>
              <option value="yunnan">云南省</option>
              <option value="shaanxi">陕西省</option>
              <option value="gansu">甘肃省</option>
              <option value="qinghai">青海省</option>
              <option value="taiwan">台湾省</option>
            </optgroup>
            <optgroup label="自治区">
              <option value="neimenggu">内蒙古自治区</option>
              <option value="guangxi">广西壮族自治区</option>
              <option value="xizang">西藏自治区</option>
              <option value="ningxia">宁夏回族自治区</option>
              <option value="xinjiang">新疆维吾尔自治区</option>
            </optgroup>
            <optgroup label="特别行政区">
              <option value="hongkong">香港特别行政区</option>
              <option value="macao">澳门特别行政区</option>
            </optgroup>
          </select>
          <select id="overseas-select" class="git-select" style="display:none;">
            <option value="" disabled selected>海外区域 *</option>
            <option value="asia-pacific">亚太</option>
            <option value="europe">欧洲</option>
            <option value="north-america">北美</option>
            <option value="south-america">南美</option>
            <option value="middle-east-africa">中东和非洲</option>
          </select>
        </div>
        <div style="margin-bottom:16px;">
          <select class="git-select" required>
            <option value="" disabled selected>咨询类型 *</option>
            <option value="partnership">合作洽谈</option>
            <option value="sales">销售咨询</option>
            <option value="technical">技术支持</option>
            <option value="media">媒体垂询</option>
            <option value="careers">招聘相关</option>
            <option value="other">其他</option>
          </select>
        </div>
        <div style="margin-bottom:28px;">
          <textarea class="git-input" placeholder="详细需求（选填）" rows="4" style="resize:vertical; min-height:80px;"></textarea>
        </div>
        <button type="submit" style="display:inline-flex; align-items:center; gap:8px; padding:14px 32px; background:#3B82F6; color:#fff; border:none; border-radius:0.25rem; font-size:12px; font-weight:500; letter-spacing:0.08em; text-transform:uppercase; font-family:Inter,sans-serif; cursor:pointer; transition:background 0.3s; width:100%; justify-content:center;" onmouseover="this.style.background='#2563EB'" onmouseout="this.style.background='#3B82F6'">
          立即提交
          <span class="material-symbols-outlined" style="font-size:16px;">arrow_outward</span>
        </button>
      </form>

      <div style="display:flex; flex-direction:column; gap:36px; padding-top:0;">
        <div style="display:flex; flex-direction:column; gap:24px;">
          <div>
            <span style="font-size:12px; font-weight:500; letter-spacing:0.08em; text-transform:uppercase; color:rgba(255,255,255,0.35); display:block; margin-bottom:10px;">通用咨询</span>
            <a href="mailto:info@realman-robot.com" style="font-size:16px; font-weight:400; letter-spacing:-0.05em; color:#fff; text-decoration:none; transition:color 0.3s; word-break:break-all;" onmouseover="this.style.color='#3B82F6'" onmouseout="this.style.color='#fff'">info@realman-robot.com</a>
          </div>
          <div>
            <span style="font-size:12px; font-weight:500; letter-spacing:0.08em; text-transform:uppercase; color:rgba(255,255,255,0.35); display:block; margin-bottom:10px;">销售咨询</span>
            <a href="mailto:Sales@realman-robot.com" style="font-size:16px; font-weight:400; letter-spacing:-0.05em; color:#fff; text-decoration:none; transition:color 0.3s; word-break:break-all;" onmouseover="this.style.color='#3B82F6'" onmouseout="this.style.color='#fff'">Sales@realman-robot.com</a>
          </div>
          <div>
            <span style="font-size:12px; font-weight:500; letter-spacing:0.08em; text-transform:uppercase; color:rgba(255,255,255,0.35); display:block; margin-bottom:10px;">服务热线</span>
            <a href="tel:400-898-2018" style="font-size:16px; font-weight:400; letter-spacing:-0.05em; color:#fff; text-decoration:none; transition:color 0.3s; word-break:break-all;" onmouseover="this.style.color='#3B82F6'" onmouseout="this.style.color='#fff'">400-898-2018</a>
          </div>
        </div>

        <div>
          <span style="font-size:12px; font-weight:500; letter-spacing:0.08em; text-transform:uppercase; color:rgba(255,255,255,0.35); display:block; margin-bottom:16px;">关注我们</span>
          <span style="font-size:13px; font-weight:400; letter-spacing:-0.02em; color:rgba(255,255,255,0.3);">平台二维码即将上线</span>
        </div>

        <div style="margin-top:auto; padding-top:24px;">
          <span style="font-size:12px; font-weight:400; letter-spacing:-0.05em; color:rgba(255,255,255,0.25);">&copy; 2026 睿尔曼智能 版权所有</span>
        </div>
      </div>

    </div>
  </div>
</section>

<script>
if (typeof initTypewriter === 'undefined') {
  function initTypewriter(id, text) {
    var el = document.getElementById(id);
    if (!el) return;
    var typed = false;
    var obs = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting && !typed) {
          typed = true;
          var i = 0;
          el.style.width = 'auto';
          el.textContent = '';
          var typeChar = function() {
            if (i < text.length) {
              el.textContent += text[i];
              i++;
              setTimeout(typeChar, 80);
            }
          };
          typeChar();
          obs.unobserve(el);
        }
      });
    }, { threshold: 0.2 });
    obs.observe(el);
  }
}
initTypewriter('git-title', '联系我们');

function handleRegionChange(val) {
  var wrap = document.getElementById('sub-region-wrap');
  var prov = document.getElementById('province-select');
  var over = document.getElementById('overseas-select');
  wrap.style.display = 'block';
  if (val === 'china') {
    prov.style.display = ''; prov.required = true; prov.selectedIndex = 0;
    over.style.display = 'none'; over.required = false;
  } else if (val === 'overseas') {
    over.style.display = ''; over.required = true; over.selectedIndex = 0;
    prov.style.display = 'none'; prov.required = false;
  } else {
    wrap.style.display = 'none';
    prov.required = false; over.required = false;
  }
}
</script>

<script src="../../prop/supabase-cta.js"></script>
<script>function switchLang(){var h=location.href;if(h.indexOf("/en/")>-1){location.href=h.replace("/en/","/cn/")}else if(h.indexOf("/cn/")>-1){location.href=h.replace("/cn/","/en/")}}</script>
</body>
</html>
'''

# Collect all CN HTML files except home.html
files = []
for sub in ['main', 'products', 'industry-solutions', 'ecosystem-solutions']:
    d = os.path.join(BASE, sub)
    for f in sorted(os.listdir(d)):
        if f.endswith('.html'):
            rel = os.path.join(sub, f)
            if rel != os.path.join('main', 'home.html'):
                files.append(rel)

MARKER = '<!-- CTA + FOOTER: GET IN TOUCH -->'
changed = 0
errors = []

for filepath in files:
    fullpath = os.path.join(BASE, filepath)
    with open(fullpath, 'r', encoding='utf-8') as f:
        content = f.read()

    idx = content.find(MARKER)
    if idx == -1:
        errors.append(f"❌ {filepath}: 未找到 CTA 标记")
        continue

    new_content = content[:idx] + NEW_CTA
    with open(fullpath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    changed += 1
    print(f"✅ {filepath}")

print(f"\n{'=' * 60}")
print(f"总计：{changed} 个文件已更新")
if errors:
    print(f"错误：{len(errors)} 个")
    for e in errors:
        print(f"  {e}")
print(f"{'=' * 60}")
