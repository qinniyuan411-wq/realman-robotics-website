import re, sys, os

sys.stdout.reconfigure(encoding='utf-8')
base = r'C:\Users\Qinni Yuan\Desktop\realman-robotics-website\cn\products'
files = ['rm65.html','rm75.html','rml63.html','eco65.html','eco63.html','eco62.html',
         'rx75.html','realbot-humanoid.html','single-arm-lift.html','dual-arm-lift.html']

pattern = re.compile(r'<h3 style="font-size:20px;[^"]*">([^<]+)</h3>\s*<p style="font-size:12px;[^"]*">([^<]+)</p>')

for fn in files:
    fp = os.path.join(base, fn)
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()
    matches = pattern.findall(content)
    print(f'===== {fn} ({len(matches)} cards) =====')
    for i, (title, desc) in enumerate(matches):
        has_en = bool(re.search(r'[a-zA-Z]{4,}', desc))
        status = 'EN!' if has_en else 'OK'
        print(f'  {i+1}. [{status}] {title} / {desc[:60]}...')
    print()
