import os, sys
sys.stdout.reconfigure(encoding='utf-8')
BASE = r'C:\Users\Qinni Yuan\Desktop\realman-robotics-website\cn'
OLD = '<span style="font-size:13px; font-weight:400; letter-spacing:-0.02em; color:rgba(255,255,255,0.3);">平台二维码即将上线</span>'
NEW = '<img src="../../prop/qr_code_official-wechat-account.png" alt="微信公众号二维码" style="width:120px; height:120px; border-radius:0.25rem;">'
count = 0
for sub in ['main', 'products', 'industry-solutions', 'ecosystem-solutions']:
    d = os.path.join(BASE, sub)
    for f in sorted(os.listdir(d)):
        if f.endswith('.html') and not (sub == 'main' and f == 'home.html'):
            fp = os.path.join(d, f)
            with open(fp, 'r', encoding='utf-8') as fh:
                c = fh.read()
            if OLD in c:
                c = c.replace(OLD, NEW)
                with open(fp, 'w', encoding='utf-8') as fh:
                    fh.write(c)
                count += 1
print(f'✅ {count} 个文件已同步')
