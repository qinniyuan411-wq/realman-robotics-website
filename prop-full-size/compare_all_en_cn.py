import re, sys, os, glob

sys.stdout.reconfigure(encoding='utf-8')

base_cn = r'C:\Users\Qinni Yuan\Desktop\realman-robotics-website\cn'
base_en = r'C:\Users\Qinni Yuan\Desktop\realman-robotics-website\en'

def get_html_files(base):
    result = []
    for root, dirs, files in os.walk(base):
        for f in files:
            if f.endswith('.html'):
                rel = os.path.relpath(os.path.join(root, f), base)
                result.append(rel.replace('\\', '/'))
    return sorted(result)

cn_files = get_html_files(base_cn)
en_files = get_html_files(base_en)

print(f'CN files: {len(cn_files)}, EN files: {len(en_files)}')
only_cn = set(cn_files) - set(en_files)
only_en = set(en_files) - set(cn_files)
if only_cn:
    print(f'⚠️ Only in CN: {only_cn}')
if only_en:
    print(f'⚠️ Only in EN: {only_en}')
print()

common_files = sorted(set(cn_files) & set(en_files))

def normalize_html(text):
    text = text.replace('&middot;', '·').replace('&plusmn;', '±')
    text = text.replace('&times;', '×').replace('&ndash;', '–')
    text = text.replace('&le;', '≤').replace('&lt;', '<').replace('&gt;', '>')
    text = text.replace('&Oslash;', 'Ø').replace('&amp;', '&')
    text = text.replace('&nbsp;', ' ')
    return text

def extract_info(content):
    info = {}
    
    title_m = re.search(r'<title>([^<]+)</title>', content)
    info['title'] = title_m.group(1).strip() if title_m else 'N/A'
    
    imgs = re.findall(r'src="([^"]*\.(?:png|jpg|webp|svg|gif))"', content)
    info['images'] = imgs
    info['image_basenames'] = [os.path.basename(i) for i in imgs]
    
    links = re.findall(r'href="([^"#][^"]*\.html[^"]*)"', content)
    info['links'] = links
    
    h1s = re.findall(r'<h1[^>]*>([^<]+)</h1>', content)
    info['h1'] = h1s
    
    h2s = re.findall(r'<h2[^>]*>([^<]+)</h2>', content)
    info['h2'] = h2s
    
    h3s = re.findall(r'<h3[^>]*>([^<]+)</h3>', content)
    info['h3_count'] = len(h3s)
    
    icons = re.findall(r'class="material-symbols-outlined"[^>]*>([^<]+)<', content)
    info['icons'] = icons
    
    numbers = re.findall(r'(?<![a-zA-Z])(\d+(?:\.\d+)?)\s*(?:kg|mm|N·m|RPM|W|V|m/s|°C|Ah|bit)', normalize_html(content))
    info['numbers'] = numbers
    
    spec_values = re.findall(r'font-weight:500;[^"]*color:#000;">([^<]+)</span>', content)
    info['spec_values_count'] = len(spec_values)
    info['spec_values'] = [normalize_html(v).strip() for v in spec_values]
    
    switchlang = re.findall(r"switchLang\('([^']+)'\)", content)
    info['switchlang'] = switchlang
    
    cn_in_en = []
    if '/en/' in content or True:
        pass
    
    return info

def check_links_consistency(cn_links, en_links, filename):
    issues = []
    cn_normalized = []
    en_normalized = []
    for l in cn_links:
        cn_normalized.append(l.replace('/cn/', '/XX/').replace('/en/', '/XX/'))
    for l in en_links:
        en_normalized.append(l.replace('/cn/', '/XX/').replace('/en/', '/XX/'))
    
    if len(cn_normalized) != len(en_normalized):
        issues.append(f'链接数量不同: CN={len(cn_links)}, EN={len(en_links)}')
    
    for l in cn_links:
        if '/en/' in l:
            issues.append(f'CN文件中包含EN链接: {l}')
    for l in en_links:
        if '/cn/' in l:
            issues.append(f'EN文件中包含CN链接: {l}')
    
    return issues

all_issues = {}

for fn in common_files:
    cn_path = os.path.join(base_cn, fn)
    en_path = os.path.join(base_en, fn)
    
    with open(cn_path, 'r', encoding='utf-8') as f:
        cn_content = f.read()
    with open(en_path, 'r', encoding='utf-8') as f:
        en_content = f.read()
    
    cn_info = extract_info(cn_content)
    en_info = extract_info(en_content)
    
    issues = []
    
    if cn_info['image_basenames'] != en_info['image_basenames']:
        cn_set = set(cn_info['image_basenames'])
        en_set = set(en_info['image_basenames'])
        diff_cn = cn_set - en_set
        diff_en = en_set - cn_set
        if diff_cn or diff_en:
            if diff_cn:
                issues.append(f'图片差异 - CN独有: {diff_cn}')
            if diff_en:
                issues.append(f'图片差异 - EN独有: {diff_en}')
        elif len(cn_info['image_basenames']) != len(en_info['image_basenames']):
            issues.append(f'图片数量不同: CN={len(cn_info["image_basenames"])}, EN={len(en_info["image_basenames"])}')
    
    if cn_info['icons'] != en_info['icons']:
        issues.append(f'图标不同: CN={cn_info["icons"]}, EN={en_info["icons"]}')
    
    if cn_info['h3_count'] != en_info['h3_count']:
        issues.append(f'H3数量不同: CN={cn_info["h3_count"]}, EN={en_info["h3_count"]}')
    
    if cn_info['spec_values_count'] != en_info['spec_values_count']:
        issues.append(f'参数数据数量不同: CN={cn_info["spec_values_count"]}, EN={en_info["spec_values_count"]}')
    
    link_issues = check_links_consistency(cn_info['links'], en_info['links'], fn)
    issues.extend(link_issues)
    
    cn_has_en_text = []
    en_has_cn_text = []
    
    en_section_pattern = re.compile(r'<h2[^>]*>([^<]*[a-zA-Z]{3,}[^<]*)</h2>')
    cn_section_matches = en_section_pattern.findall(cn_content)
    for m in cn_section_matches:
        if m not in ['CAN FD', 'RealBOT', 'RX75', 'RM65', 'RM75', 'ECO62', 'ECO63', 'ECO65', 'RML63',
                     'WHJ', 'WHG', 'TCP', 'DOF', 'LiDAR', 'IMU', 'Intel', 'BMS']:
            if not re.search(r'[\u4e00-\u9fff]', m):
                cn_has_en_text.append(m)
    
    cn_char_pattern = re.compile(r'[\u4e00-\u9fff]')
    en_h2_matches = re.findall(r'<h2[^>]*>([^<]+)</h2>', en_content)
    for m in en_h2_matches:
        if cn_char_pattern.search(m):
            en_has_cn_text.append(m)
    en_h3_matches = re.findall(r'<h3[^>]*>([^<]+)</h3>', en_content)
    for m in en_h3_matches:
        if cn_char_pattern.search(m):
            en_has_cn_text.append(m)
    en_p_matches = re.findall(r'<p[^>]*>([^<]+)</p>', en_content)
    for m in en_p_matches:
        if cn_char_pattern.search(m) and len(m) > 5:
            en_has_cn_text.append(m[:50])
    
    if cn_has_en_text:
        issues.append(f'CN文件H2含英文: {cn_has_en_text}')
    if en_has_cn_text:
        issues.append(f'EN文件含中文文本: {en_has_cn_text[:5]}')
    
    numeric_diffs = []
    for i, (cv, ev) in enumerate(zip(cn_info['spec_values'], en_info['spec_values'])):
        cv_n = normalize_html(cv)
        ev_n = normalize_html(ev)
        has_cn = bool(re.search(r'[\u4e00-\u9fff]', cv_n))
        has_en = bool(re.search(r'[a-zA-Z]{3,}', ev_n))
        if has_cn or has_en:
            continue
        nums_cn = re.findall(r'[\d.]+', cv_n)
        nums_en = re.findall(r'[\d.]+', ev_n)
        if nums_cn and nums_en and nums_cn != nums_en:
            numeric_diffs.append(f'[{i}] CN="{cv}" vs EN="{ev}"')
    
    if numeric_diffs:
        issues.append(f'参数数值差异: {numeric_diffs[:5]}')
    
    if issues:
        all_issues[fn] = issues

print(f'===== 检查结果汇总 ({len(common_files)} 个文件) =====\n')

if not all_issues:
    print('✅ 所有文件结构完全一致，未发现异常')
else:
    ok_count = len(common_files) - len(all_issues)
    print(f'✅ {ok_count} 个文件无异常')
    print(f'⚠️ {len(all_issues)} 个文件有差异:\n')
    for fn, issues in sorted(all_issues.items()):
        print(f'--- {fn} ---')
        for iss in issues:
            print(f'  {iss}')
        print()
