import re, os, sys, html
sys.stdout.reconfigure(encoding='utf-8')

BASE = r'C:\Users\Qinni Yuan\Desktop\realman-robotics-website\cn'

files = []
for sub in ['main', 'products', 'industry-solutions', 'ecosystem-solutions']:
    d = os.path.join(BASE, sub)
    for f in sorted(os.listdir(d)):
        if f.endswith('.html'):
            files.append(os.path.join(sub, f))

# ── Material Symbols icon names (these appear as <span class="material-symbols-outlined">iconname</span>) ──
MATERIAL_ICONS = {
    'outward','menu','close','home','search','download','open_in_new','forward',
    'inventory','shipping','factory','construction','health_and_safety','school',
    'storefront','support_agent','security','restaurant','shopping_cart','medical_services',
    'museum','science','format_paint','engineering','android','sports_martial_arts',
    'vacuum','biotech','elderly','devices','settings','monitor','history','emergency',
    'training','precision_manufacturing','compress','sensors','handshake','savings',
    'accessibility','height','visibility','tethering','shield','target','verified',
    'location_on','unchecked','rotation','terminal','schedule','camera','workspace_premium',
    'description','fitness_center','center_focus_strong','arrow_forward','arrow_back',
    'expand_more','expand_less','chevron_right','chevron_left','check','check_circle',
    'star','grade','trending_up','speed','bolt','memory','hub','cloud','language',
    'precision', 'manufacturing', 'fitness', 'center', 'workspace', 'premium',
    'support', 'safety', 'shopping', 'services', 'format', 'martial', 'sports',
    'focus', 'strong', 'location', 'health', 'paint', 'agent', 'cart',
    'in_new', 'and', 'on', 'of',
    'contactless', 'motion_photos_on', 'swap_horiz', 'flip_camera_android',
    'done', 'error', 'info', 'warning', 'help', 'add', 'remove', 'edit', 'delete',
    'touch_app', 'smart_toy', 'psychology', 'developer_mode',
    'drag_indicator', 'more_vert', 'more_horiz',
    'fullscreen', 'fullscreen_exit', 'zoom_in', 'zoom_out',
    'play_arrow', 'pause', 'stop', 'skip_next', 'skip_previous',
    'volume_up', 'volume_off', 'mic', 'mic_off',
    'share', 'favorite', 'bookmark', 'print',
    'account_circle', 'person', 'group', 'people',
    'place', 'map', 'navigation', 'directions',
    'calendar_today', 'event', 'alarm', 'timer',
    'attach_file', 'link', 'image', 'photo', 'video', 'audio',
    'folder', 'file', 'save', 'upload', 'backup',
    'email', 'phone', 'chat', 'message', 'notifications',
    'lock', 'vpn_key', 'fingerprint', 'face',
    'wifi', 'bluetooth', 'signal', 'battery',
    'light_mode', 'dark_mode', 'contrast',
    'translate', 'spellcheck', 'text_fields',
    'code', 'bug_report', 'build', 'extension', 'api',
    'dashboard', 'analytics', 'insights',
    'shopping_bag', 'payments', 'receipt',
    'local_shipping', 'flight', 'train', 'directions_car',
    'eco', 'park', 'water_drop', 'air', 'thermostat',
    'celebration', 'cake', 'redeem', 'card_giftcard',
}

# Brand names / proper nouns / technical terms to skip
SKIP_PROPER = {
    'realman', 'realbot', 'rm65', 'rm75', 'rml63', 'eco62', 'eco63', 'eco65',
    'rx75', 'whj', 'whg', 'tcp', 'can', 'fd', 'ethercat', 'modbus', 'rtu',
    'wifi', 'bluetooth', 'usb', 'api', 'sdk', 'ros', 'linux', 'windows',
    'python', 'json', 'http', 'mqtt', 'ip', 'ces', 'ai', 'iot', 'abs',
    'intel', 'realsense', 'nvidia', 'jetson', 'orin', 'nano',
    'linkedin', 'facebook', 'instagram', 'youtube', 'tiktok', 'twitter',
    'github', 'gitee', 'alibaba', 'amazon', 'microsoft', 'samsung',
    'huawei', 'lenovo', 'qualcomm', 'xiaomi', 'tsinghua',
    'lerobot',
    'ieee', 'iso', 'ce', 'fcc', 'rohs', 'ul',
    'lidar', 'rgb', 'imu', 'gnss', 'gps', 'led', 'lcd',
    'rpm', 'kg', 'mm', 'nm', 'mpa', 'dof', 'dc', 'ac',
    'sku', 'sop', 'erp', 'mes', 'scada', 'plc',
    'pip', 'install', 'realman-sdk',
    'inter', 'sans-serif',
    'pdf', 'doc', 'xlsx',
    'cobe',
}

def read_file(filepath):
    with open(os.path.join(BASE, filepath), 'r', encoding='utf-8') as f:
        return f.read()

def remove_scripts_styles(content):
    content = re.sub(r'<script[\s\S]*?</script>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'<style[\s\S]*?</style>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'<!--[\s\S]*?-->', '', content)
    return content

def is_material_icon(text):
    t = text.strip().lower().replace(' ', '_')
    if t in MATERIAL_ICONS:
        return True
    parts = t.split('_')
    if all(p in MATERIAL_ICONS or len(p) <= 2 for p in parts):
        return True
    return False

def has_meaningful_english(text):
    """Check if text contains meaningful English words (not just numbers, units, brand names)."""
    words = re.findall(r'[A-Za-z]+', text)
    meaningful = []
    for w in words:
        if len(w) < 3:
            continue
        if w.lower() in SKIP_PROPER:
            continue
        if re.match(r'^[A-Z]{1,4}\d', w):
            continue
        meaningful.append(w)
    return meaningful

def scan_file(filepath):
    content = read_file(filepath)
    clean = remove_scripts_styles(content)
    findings = []
    
    # ── 1. Check visible text inside material-symbols spans (these are icon names, skip) ──
    # Remove material symbol spans so they don't pollute later checks
    clean_no_icons = re.sub(
        r'<span\s+class="material-symbols-outlined"[^>]*>[^<]*</span>',
        '', clean, flags=re.IGNORECASE
    )
    
    # ── 2. Find English text in visible elements ──
    # Extract text between > and < (visible text nodes)
    text_nodes = re.findall(r'>([^<]+)<', clean_no_icons)
    
    for node in text_nodes:
        text = html.unescape(node).strip()
        if not text or len(text) < 3:
            continue
        
        # Skip if it's purely numbers, punctuation, whitespace
        if not re.search(r'[A-Za-z]', text):
            continue
        
        # Skip if it's a URL or email
        if re.match(r'https?://', text) or '@' in text:
            continue
        
        # Skip domain names
        if re.match(r'[\w\.\-]+\.(com|org|net|io|cn)', text):
            continue
            
        # Skip if it's a material icon name
        if is_material_icon(text):
            continue
        
        # Check for meaningful English words
        en_words = has_meaningful_english(text)
        if not en_words:
            continue
        
        # If text is mostly Chinese with a few English words mixed in, 
        # check if the English portion is substantial
        has_chinese = bool(re.search(r'[\u4e00-\u9fff]', text))
        
        if has_chinese:
            # Mixed content: only flag if English words are long phrases, not just abbreviations
            en_text_len = sum(len(w) for w in en_words)
            if en_text_len < 10:
                continue
        else:
            # Pure English text - this is likely untranslated
            # But skip very short items or single common words
            if len(en_words) < 2 and all(len(w) < 8 for w in en_words):
                continue
        
        # Skip common navigation/UI framework words that appear in attribute-like contexts
        text_lower = text.strip().lower()
        if text_lower in {'menu', 'home', 'search', 'close', 'open', 'submit', 
                          'next', 'previous', 'loading', 'download', 'back',
                          'copyright', 'reserved'}:
            continue
        
        # Clean up for display
        display = text.strip()
        if len(display) > 120:
            display = display[:120] + '...'
        
        # Get line number for context
        line_num = content[:content.find(node)].count('\n') + 1 if node in content else '?'
        
        findings.append({
            'type': '页面文字',
            'text': display,
            'line': line_num,
            'words': en_words,
        })
    
    # ── 3. Check alt attributes ──
    for m in re.finditer(r'<img\b[^>]*\balt="([^"]+)"', clean_no_icons, re.IGNORECASE):
        alt = html.unescape(m.group(1)).strip()
        if not alt:
            continue
        en_words = has_meaningful_english(alt)
        if len(en_words) >= 2:
            line_num = content[:content.find(m.group(0))].count('\n') + 1
            findings.append({
                'type': 'alt属性',
                'text': alt,
                'line': line_num,
                'words': en_words,
            })
    
    # ── 4. Check title attributes (skip social media) ──
    social = {'linkedin', 'facebook', 'instagram', 'youtube', 'tiktok', 'twitter', 'x'}
    for m in re.finditer(r'\btitle="([^"]+)"', clean_no_icons, re.IGNORECASE):
        title = html.unescape(m.group(1)).strip()
        if title.lower() in social:
            continue
        en_words = has_meaningful_english(title)
        if len(en_words) >= 2:
            line_num = content[:content.find(m.group(0))].count('\n') + 1
            findings.append({
                'type': 'title属性',
                'text': title,
                'line': line_num,
                'words': en_words,
            })
    
    # ── 5. Check placeholder attributes ──
    for m in re.finditer(r'placeholder="([^"]+)"', clean_no_icons, re.IGNORECASE):
        ph = html.unescape(m.group(1)).strip()
        en_words = has_meaningful_english(ph)
        if len(en_words) >= 1:
            line_num = content[:content.find(m.group(0))].count('\n') + 1
            findings.append({
                'type': 'placeholder',
                'text': ph,
                'line': line_num,
                'words': en_words,
            })
    
    # Deduplicate
    seen = set()
    unique = []
    for f in findings:
        key = f['text'].lower().strip()
        if key not in seen:
            seen.add(key)
            unique.append(f)
    
    return unique

# ── Run scan ──
print("=" * 90)
print("CN 页面未翻译英文内容扫描报告（精细版）")
print("=" * 90)
print("说明：已过滤 Material Symbols 图标名、品牌名、社交媒体名、技术术语等")
print()

all_issues = {}
for filepath in files:
    issues = scan_file(filepath)
    if issues:
        all_issues[filepath] = issues

if not all_issues:
    print("✅ 所有 52 个文件均未发现未翻译的英文内容。")
else:
    total = sum(len(v) for v in all_issues.values())
    print(f"共 {len(all_issues)} 个文件存在疑似未翻译内容，共 {total} 处：\n")
    
    for filepath, issues in sorted(all_issues.items()):
        print(f"\n{'─' * 90}")
        print(f"📄 {filepath}  ({len(issues)} 处)")
        print(f"{'─' * 90}")
        for i, item in enumerate(issues, 1):
            tag = f"[{item['type']}]"
            line = f"L{item['line']}" if item['line'] != '?' else ''
            print(f"  {i:2d}. {tag:12s} {line:6s}  {item['text']}")

print(f"\n{'=' * 90}")
print("扫描完成")
print("=" * 90)
