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

def extract_spec_values(content):
    return re.findall(r'font-weight:500; color:#000;">([^<]+)</span>', content)

def normalize(val):
    val = val.replace('&middot;', '·').replace('&plusmn;', '±')
    val = val.replace('&times;', '×').replace('&ndash;', '–')
    val = val.replace('&le;', '≤').replace('&lt;', '<')
    val = val.replace('&Oslash;', 'Ø').replace('&amp;', '&')
    val = val.replace('\u00b1', '±').replace('\u00d7', '×')
    return val.strip()

known_translations = {
    '人形': '仿人构型', '协作型': '协作臂构型', '协作': 'Collaborative',
    '电磁': 'Electromagnetic', '集成': 'Integrated',
    '弹簧': 'Spring', '销钉式': 'Pin',
    '软抱闸': '', '硬抱闸': '', '插销式制动': '', '电磁抱闸': '',
    '仿人构型': '', '协作臂构型': '',
    '铝合金 / ABS': 'Aluminum Alloy / ABS',
}

is_translated = lambda cn, en: True

for fn in files:
    cn_path = os.path.join(base_cn, fn)
    en_path = os.path.join(base_en, fn)

    with open(cn_path, 'r', encoding='utf-8') as f:
        cn_content = f.read()
    with open(en_path, 'r', encoding='utf-8') as f:
        en_content = f.read()

    cn_vals = [normalize(v) for v in extract_spec_values(cn_content)]
    en_vals = [normalize(v) for v in extract_spec_values(en_content)]

    if len(cn_vals) != len(en_vals):
        print(f'⚠️ {fn}: 数据单元格数不同 CN={len(cn_vals)} vs EN={len(en_vals)}')
        continue

    diffs = []
    for i, (cv, ev) in enumerate(zip(cn_vals, en_vals)):
        if cv != ev:
            has_cn_char = bool(re.search(r'[\u4e00-\u9fff]', cv))
            has_en_word = bool(re.search(r'[a-zA-Z]{3,}', ev))
            if has_cn_char or has_en_word:
                continue
            nums_cn = set(re.findall(r'[\d.]+', cv))
            nums_en = set(re.findall(r'[\d.]+', ev))
            if nums_cn and nums_en and nums_cn != nums_en:
                diffs.append(f'  [{i}] CN="{cv}" vs EN="{ev}"')

    if diffs:
        print(f'⚠️ {fn}: 数值差异:')
        for d in diffs:
            print(d)
    else:
        print(f'✅ {fn}: 数值数据一致')
