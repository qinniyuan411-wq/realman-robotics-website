import re, sys, os

sys.stdout.reconfigure(encoding='utf-8')

base_cn = r'C:\Users\Qinni Yuan\Desktop\realman-robotics-website\cn\products'
base_en = r'C:\Users\Qinni Yuan\Desktop\realman-robotics-website\en\products'

files = [
    'whj-joint-modules.html', 'whj-torque-joint-modules.html', 'whg-joint-modules.html',
    'rm65.html', 'rm75.html', 'rml63.html',
    'eco65.html', 'eco63.html', 'eco62.html',
    'rx75.html', 'realbot-humanoid.html', 'single-arm-lift.html', 'dual-arm-lift.html',
]

def extract_advantages(content):
    pattern = re.compile(
        r'<span class="material-symbols-outlined"[^>]*>([^<]+)</span>\s*'
        r'<h3 style="font-size:20px[^"]*">([^<]+)</h3>\s*'
        r'<p style="font-size:12px[^"]*">([^<]+)</p>'
    )
    return pattern.findall(content)

for fn in files:
    cn_path = os.path.join(base_cn, fn)
    en_path = os.path.join(base_en, fn)

    with open(cn_path, 'r', encoding='utf-8') as f:
        cn_content = f.read()
    with open(en_path, 'r', encoding='utf-8') as f:
        en_content = f.read()

    cn_advs = extract_advantages(cn_content)
    en_advs = extract_advantages(en_content)

    print(f'===== {fn} =====')

    if len(cn_advs) != len(en_advs):
        print(f'  ⚠️ 数量不同: CN={len(cn_advs)}, EN={len(en_advs)}')

    max_len = max(len(cn_advs), len(en_advs))
    all_match = True
    for i in range(max_len):
        cn_icon = cn_advs[i][0] if i < len(cn_advs) else 'MISSING'
        en_icon = en_advs[i][0] if i < len(en_advs) else 'MISSING'
        cn_title = cn_advs[i][1] if i < len(cn_advs) else 'MISSING'
        en_title = en_advs[i][1] if i < len(en_advs) else 'MISSING'
        cn_desc = cn_advs[i][2][:40] if i < len(cn_advs) else 'MISSING'
        en_desc = en_advs[i][2][:40] if i < len(en_advs) else 'MISSING'

        icon_ok = '✅' if cn_icon == en_icon else '⚠️'
        if cn_icon != en_icon:
            all_match = False

        print(f'  {i+1}. {icon_ok} icon={cn_icon}{"" if cn_icon == en_icon else " vs " + en_icon}')
        print(f'     CN: {cn_title} | {cn_desc}...')
        print(f'     EN: {en_title} | {en_desc}...')

    if all_match and len(cn_advs) == len(en_advs):
        print(f'  ✅ 图标+顺序完全对应')
    print()
