import re, sys, os

sys.stdout.reconfigure(encoding='utf-8')

base_cn = r'C:\Users\Qinni Yuan\Desktop\realman-robotics-website\cn\products'
base_en = r'C:\Users\Qinni Yuan\Desktop\realman-robotics-website\en\products'

files = [
    'whj-joint-modules.html',
    'whj-torque-joint-modules.html',
    'whg-joint-modules.html',
    'rm65.html',
    'rm75.html',
    'rml63.html',
    'eco65.html',
    'eco63.html',
    'eco62.html',
    'rx75.html',
    'realbot-humanoid.html',
    'single-arm-lift.html',
    'dual-arm-lift.html',
]

def extract_structure(content):
    info = {}
    
    title_m = re.search(r'<title>([^<]+)</title>', content)
    info['title'] = title_m.group(1).strip() if title_m else 'N/A'
    
    h1_m = re.search(r'<h1[^>]*>([^<]+)</h1>', content)
    info['h1'] = h1_m.group(1).strip() if h1_m else 'N/A'
    
    h2s = re.findall(r'<h2[^>]*>([^<]+)</h2>', content)
    info['h2_sections'] = h2s
    
    adv_titles = re.findall(r'<h3 style="font-size:20px[^"]*">([^<]+)</h3>', content)
    info['advantage_titles'] = adv_titles
    info['advantage_count'] = len(adv_titles)
    
    imgs = re.findall(r'src="([^"]*\.(?:png|jpg|webp|svg))"', content)
    info['image_count'] = len(imgs)
    info['images'] = imgs
    
    spec_labels = re.findall(r'color:rgba\(0,0,0,0\.5\);">([^<]+)</span>', content)
    info['spec_labels'] = spec_labels
    info['spec_count'] = len(spec_labels)
    
    version_labels = re.findall(r'font-weight:500[^"]*color:#fff;">([^<]+)</span>', content)
    info['version_cols'] = [v for v in version_labels if v != '参数' and v != 'Parameter']
    
    spec_values = re.findall(r'font-weight:500; color:#000;">([^<]+)</span>', content)
    info['spec_values'] = spec_values
    
    nav_links = re.findall(r'href="([^"]*)"', content)
    info['link_count'] = len(nav_links)
    
    return info

for fn in files:
    cn_path = os.path.join(base_cn, fn)
    en_path = os.path.join(base_en, fn)
    
    with open(cn_path, 'r', encoding='utf-8') as f:
        cn_content = f.read()
    with open(en_path, 'r', encoding='utf-8') as f:
        en_content = f.read()
    
    cn_info = extract_structure(cn_content)
    en_info = extract_structure(en_content)
    
    issues = []
    
    if cn_info['advantage_count'] != en_info['advantage_count']:
        issues.append(f"  核心优势数量不同: CN={cn_info['advantage_count']}, EN={en_info['advantage_count']}")
    
    if cn_info['spec_count'] != en_info['spec_count']:
        issues.append(f"  技术参数行数不同: CN={cn_info['spec_count']}, EN={en_info['spec_count']}")
    
    if len(cn_info['version_cols']) != len(en_info['version_cols']):
        issues.append(f"  版本列数不同: CN={len(cn_info['version_cols'])}, EN={len(en_info['version_cols'])}")
    
    cn_version_set = set(cn_info['version_cols'])
    en_version_set = set(en_info['version_cols'])
    if cn_version_set != en_version_set:
        only_cn = cn_version_set - en_version_set
        only_en = en_version_set - cn_version_set
        if only_cn or only_en:
            issues.append(f"  版本列名差异: CN独有={only_cn}, EN独有={only_en}")
    
    if cn_info['image_count'] != en_info['image_count']:
        issues.append(f"  图片数量不同: CN={cn_info['image_count']}, EN={en_info['image_count']}")
    
    cn_img_files = [os.path.basename(i) for i in cn_info['images']]
    en_img_files = [os.path.basename(i) for i in en_info['images']]
    if cn_img_files != en_img_files:
        cn_set = set(cn_img_files)
        en_set = set(en_img_files)
        only_cn_imgs = cn_set - en_set
        only_en_imgs = en_set - cn_set
        if only_cn_imgs or only_en_imgs:
            issues.append(f"  图片文件名差异:")
            if only_cn_imgs:
                issues.append(f"    CN独有: {only_cn_imgs}")
            if only_en_imgs:
                issues.append(f"    EN独有: {only_en_imgs}")
    
    if len(cn_info['spec_values']) != len(en_info['spec_values']):
        issues.append(f"  参数数据单元格数量不同: CN={len(cn_info['spec_values'])}, EN={len(en_info['spec_values'])}")
    
    cn_nums = re.findall(r'[\d.]+\s*(?:kg|mm|N·m|N&middot;m|RPM|W|V|bit|m/s|°C|%)', cn_content)
    en_nums = re.findall(r'[\d.]+\s*(?:kg|mm|N·m|N&middot;m|RPM|W|V|bit|m/s|°C|%)', en_content)
    
    if len(cn_info['h2_sections']) != len(en_info['h2_sections']):
        issues.append(f"  H2板块数量不同: CN={len(cn_info['h2_sections'])}, EN={len(en_info['h2_sections'])}")
    
    print(f'===== {fn} =====')
    print(f'  Title: CN="{cn_info["title"]}" | EN="{en_info["title"]}"')
    print(f'  H1: CN="{cn_info["h1"]}" | EN="{en_info["h1"]}"')
    print(f'  核心优势: CN={cn_info["advantage_count"]}个 {cn_info["advantage_titles"]}')
    print(f'           EN={en_info["advantage_count"]}个 {en_info["advantage_titles"]}')
    print(f'  技术参数: CN={cn_info["spec_count"]}行 | EN={en_info["spec_count"]}行')
    print(f'  版本列: CN={cn_info["version_cols"]} | EN={en_info["version_cols"]}')
    print(f'  图片: CN={cn_info["image_count"]}张 | EN={en_info["image_count"]}张')
    
    if issues:
        print(f'  ⚠️ 发现差异:')
        for iss in issues:
            print(iss)
    else:
        print(f'  ✅ 结构一致')
    print()
