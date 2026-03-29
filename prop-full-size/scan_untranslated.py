import re, os, sys, html
sys.stdout.reconfigure(encoding='utf-8')

BASE = r'C:\Users\Qinni Yuan\Desktop\realman-robotics-website\cn'

# Collect all HTML files
files = []
for sub in ['main', 'products', 'industry-solutions', 'ecosystem-solutions']:
    d = os.path.join(BASE, sub)
    for f in sorted(os.listdir(d)):
        if f.endswith('.html'):
            files.append(os.path.join(sub, f))

# Known English proper nouns / brand names / technical terms to SKIP
SKIP_WORDS = {
    'realman', 'realbot', 'rm65', 'rm75', 'rml63', 'eco62', 'eco63', 'eco65',
    'rx75', 'whj', 'whg', 'tcp', 'can', 'fd', 'ethercat', 'modbus', 'rtu',
    'wifi', 'bluetooth', 'usb', 'api', 'sdk', 'ros', 'linux', 'windows',
    'python', 'json', 'http', 'mqtt', 'ip', 'ces', 'ai', 'iot', 'abs',
    'intel', 'realsense', 'nvidia', 'jetson', 'orin', 'nano',
    'ctag', 'lidar', 'rgb', 'imu', 'gnss', 'gps', 'led', 'lcd',
    'inter', 'material', 'symbols', 'outlined', 'sans', 'serif',
    'tailwindcss', 'cdn', 'href', 'src', 'alt', 'div', 'img', 'svg',
    'png', 'jpg', 'jpeg', 'gif', 'webp', 'mp4', 'webm',
    'class', 'style', 'script', 'html', 'css', 'js',
    'rpm', 'kg', 'mm', 'nm', 'mpa', 'dof', 'dc', 'ac',
    'demo', 'app', 'sku', 'sop', 'erp', 'mes', 'scada', 'plc',
    'csr', 'forum', 'daily', 'people', 'spring', 'festival', 'gala',
    'robot', 'cobots', 'cobot',
    'cobe', 'esm', 'module', 'import', 'export', 'const', 'function',
    'true', 'false', 'null', 'undefined', 'return', 'var', 'let',
    'section', 'nav', 'header', 'footer', 'main', 'aside',
    'flex', 'grid', 'block', 'inline', 'none', 'auto', 'hidden',
    'transform', 'transition', 'opacity', 'scale', 'translate',
    'cubic', 'bezier', 'ease', 'linear',
    'http', 'https', 'www', 'com', 'org', 'net', 'io',
    'type', 'text', 'submit', 'button', 'input', 'form',
    'utf', 'charset', 'viewport', 'content', 'meta', 'link', 'rel',
    'icon', 'icons', 'logo',
    'cta', 'pdf', 'doc', 'xlsx',
    'ok', 'max', 'min',
    'observer', 'intersection', 'timeout', 'interval',
    'event', 'click', 'scroll', 'resize', 'load',
    'github', 'gitee',
    'ieee', 'iso', 'ce', 'fcc', 'rohs', 'ul',
    'wifi', 'ethernet',
    'end', 'effector', 'payload',
    'series',
    'data', 'index', 'item',
    'realman robotics',
    'core', 'products',
    'dexterous', 'hand',
}

SKIP_PATTERNS = [
    r'^[A-Z]{1,5}\d*$',        # acronyms like RM65, J1, V, W
    r'^\d+[\.\d]*\s*(mm|kg|nm|rpm|mpa|v|w|a|ah|ms|s|hz|kw|kwh|°c|°|bits|dof)?\s*$',
    r'^J\d+',                   # J1, J2-J3 etc
    r'^[A-Z]\d+\s*[–\-]\s*[A-Z]?\d+',  # J1-3, J4-6 etc
    r'^https?://',              # URLs
    r'^[\w\.\-]+@',             # emails
    r'^#[0-9a-fA-F]+$',        # hex colors
    r'^\d+px$',                 # pixel values
    r'^[\d\.\-\+×±≤≥<>%/\s]+$', # numbers and math
    r'^[A-Z]{1,3}\s*\d',       # like IP54, DC48
]

def strip_html(text):
    """Remove HTML tags, scripts, styles, and decode entities."""
    text = re.sub(r'<script[\s\S]*?</script>', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'<style[\s\S]*?</style>', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'<!--[\s\S]*?-->', ' ', text)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = html.unescape(text)
    return text

def is_skip(word):
    w = word.lower().strip()
    if w in SKIP_WORDS:
        return True
    for pat in SKIP_PATTERNS:
        if re.match(pat, word, re.IGNORECASE):
            return True
    return False

def find_english_segments(text):
    """Find segments of English text that look like untranslated content."""
    segments = re.findall(r'[A-Za-z][A-Za-z\s\-\'&,;:\.]{4,}', text)
    results = []
    for seg in segments:
        seg = seg.strip()
        if not seg:
            continue
        words = seg.split()
        meaningful = [w for w in words if len(w) >= 3 and not is_skip(w)]
        if len(meaningful) >= 2 or (len(meaningful) == 1 and len(meaningful[0]) >= 6):
            cleaned = ' '.join(words).strip()
            if len(cleaned) >= 6:
                results.append(cleaned)
    return results

def extract_visible_text_blocks(filepath):
    """Extract text from specific visible HTML elements."""
    with open(os.path.join(BASE, filepath), 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove script and style blocks entirely
    clean = re.sub(r'<script[\s\S]*?</script>', '', content, flags=re.IGNORECASE)
    clean = re.sub(r'<style[\s\S]*?</style>', '', clean, flags=re.IGNORECASE)
    clean = re.sub(r'<!--[\s\S]*?-->', '', clean)

    findings = []

    # Extract text from visible elements: h1-h6, p, span, a, li, td, th, label, button, div with text
    # Focus on text content within tags
    tag_pattern = re.compile(
        r'<(h[1-6]|p|span|a|li|td|th|label|button|figcaption)\b[^>]*>([\s\S]*?)</\1>',
        re.IGNORECASE
    )

    for m in tag_pattern.finditer(clean):
        tag = m.group(1)
        inner = m.group(2)
        # Remove nested tags
        text = re.sub(r'<[^>]+>', ' ', inner)
        text = html.unescape(text).strip()
        if not text:
            continue

        en_segs = find_english_segments(text)
        for seg in en_segs:
            # Additional context check - skip if it's within a class/style attribute
            if seg not in findings:
                findings.append(seg)

    # Also check alt attributes for images
    alt_pattern = re.compile(r'alt="([^"]*)"', re.IGNORECASE)
    for m in alt_pattern.finditer(clean):
        alt_text = html.unescape(m.group(1)).strip()
        if alt_text and re.search(r'[A-Za-z]{4,}', alt_text):
            en_segs = find_english_segments(alt_text)
            for seg in en_segs:
                if seg not in findings:
                    findings.append(f'[alt] {seg}')

    # Check placeholder attributes
    ph_pattern = re.compile(r'placeholder="([^"]*)"', re.IGNORECASE)
    for m in ph_pattern.finditer(clean):
        ph_text = html.unescape(m.group(1)).strip()
        if ph_text and re.search(r'[A-Za-z]{4,}', ph_text):
            en_segs = find_english_segments(ph_text)
            for seg in en_segs:
                if seg not in findings:
                    findings.append(f'[placeholder] {seg}')

    # Check title attributes
    title_pattern = re.compile(r'title="([^"]*)"', re.IGNORECASE)
    for m in title_pattern.finditer(clean):
        t_text = html.unescape(m.group(1)).strip()
        if t_text and re.search(r'[A-Za-z]{4,}', t_text):
            en_segs = find_english_segments(t_text)
            for seg in en_segs:
                if seg not in findings:
                    findings.append(f'[title] {seg}')

    return findings

# Also do a simpler approach: look for common English phrases/sentences
COMMON_EN_PHRASES = [
    r'Learn More',
    r'Read More',
    r'Contact Us',
    r'Submit',
    r'Subscribe',
    r'Download',
    r'View All',
    r'See More',
    r'Get Started',
    r'Sign Up',
    r'Log In',
    r'Back to',
    r'Next',
    r'Previous',
    r'Loading',
    r'Search',
    r'Close',
    r'Open',
    r'Menu',
    r'Home',
    r'About',
    r'Products',
    r'Solutions',
    r'News',
    r'Careers',
    r'Partnership',
    r'Privacy Policy',
    r'Terms of Service',
    r'All Rights Reserved',
    r'Copyright',
    r'Powered by',
]

def check_common_phrases(filepath):
    with open(os.path.join(BASE, filepath), 'r', encoding='utf-8') as f:
        content = f.read()
    # Remove scripts/styles
    clean = re.sub(r'<script[\s\S]*?</script>', '', content, flags=re.IGNORECASE)
    clean = re.sub(r'<style[\s\S]*?</style>', '', clean, flags=re.IGNORECASE)

    found = []
    for phrase in COMMON_EN_PHRASES:
        matches = re.findall(r'>[^<]*(' + phrase + r')[^<]*<', clean, re.IGNORECASE)
        if matches:
            for m in matches:
                if m not in found:
                    found.append(f'[常见短语] {m}')
    return found

# Run analysis
print("=" * 80)
print("CN 页面未翻译英文内容扫描报告")
print("=" * 80)

all_issues = {}
for filepath in files:
    issues = []

    # Method 1: Extract visible text blocks
    text_issues = extract_visible_text_blocks(filepath)
    issues.extend(text_issues)

    # Method 2: Check common English phrases
    phrase_issues = check_common_phrases(filepath)
    issues.extend(phrase_issues)

    # Deduplicate
    seen = set()
    unique = []
    for item in issues:
        key = item.lower().strip()
        if key not in seen:
            seen.add(key)
            unique.append(item)

    if unique:
        all_issues[filepath] = unique

# Output results
if not all_issues:
    print("\n✅ 所有 52 个文件均未发现未翻译的英文内容。")
else:
    total_count = sum(len(v) for v in all_issues.values())
    print(f"\n共发现 {len(all_issues)} 个文件存在疑似未翻译内容，共 {total_count} 处：\n")
    for filepath, issues in sorted(all_issues.items()):
        print(f"\n📄 {filepath} ({len(issues)} 处)")
        print("-" * 60)
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")

print("\n" + "=" * 80)
print("扫描完成")
print("=" * 80)
