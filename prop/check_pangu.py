import os
import re
from html.parser import HTMLParser

class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.texts = []
        self.skip_tags = {'script', 'style', 'code', 'pre'}
        self.current_skip = 0
        self.line_map = []

    def handle_starttag(self, tag, attrs):
        if tag in self.skip_tags:
            self.current_skip += 1
        if self.current_skip == 0:
            for attr_name, attr_val in attrs:
                if attr_val and attr_name in ('alt', 'title', 'placeholder', 'content'):
                    line = self.getpos()[0]
                    self.texts.append((attr_val, line, f'{attr_name}='))

    def handle_endtag(self, tag):
        if tag in self.skip_tags:
            self.current_skip -= 1

    def handle_data(self, data):
        if self.current_skip == 0:
            line = self.getpos()[0]
            self.texts.append((data, line, 'text'))

CJK = r'[\u4e00-\u9fff\u3400-\u4dbf]'
LATIN = r'[A-Za-z]'
DIGIT = r'[0-9]'

cjk_then_latin = re.compile(f'({CJK})({LATIN})')
latin_then_cjk = re.compile(f'({LATIN})({CJK})')
cjk_then_digit = re.compile(f'({CJK})({DIGIT})')
digit_then_cjk = re.compile(f'({DIGIT})({CJK})')

IGNORE_PATTERNS = [
    re.compile(r'realman', re.IGNORECASE),
    re.compile(r'mailto:'),
    re.compile(r'https?://'),
    re.compile(r'\.html'),
    re.compile(r'\.js'),
    re.compile(r'\.css'),
    re.compile(r'\.png'),
    re.compile(r'\.jpg'),
    re.compile(r'\.svg'),
    re.compile(r'\.\./'),
]

def find_violations(text):
    violations = []
    for pattern, desc in [
        (cjk_then_latin, 'CJK+Latin'),
        (latin_then_cjk, 'Latin+CJK'),
        (cjk_then_digit, 'CJK+Digit'),
        (digit_then_cjk, 'Digit+CJK'),
    ]:
        for m in pattern.finditer(text):
            context_start = max(0, m.start() - 8)
            context_end = min(len(text), m.end() + 8)
            context = text[context_start:context_end].strip()
            skip = False
            for ip in IGNORE_PATTERNS:
                if ip.search(context):
                    skip = True
                    break
            if not skip:
                violations.append((desc, m.group(), context))
    return violations

base = r'C:\Users\Qinni Yuan\Desktop\realman-robotics-website'
total_issues = 0

for lang in ['cn', 'en']:
    lang_dir = os.path.join(base, lang)
    for root, dirs, files in os.walk(lang_dir):
        for f in sorted(files):
            if not f.endswith('.html'):
                continue
            fp = os.path.join(root, f)
            rel = os.path.relpath(fp, base)
            with open(fp, 'r', encoding='utf-8') as fh:
                content = fh.read()
            
            extractor = TextExtractor()
            try:
                extractor.feed(content)
            except:
                continue
            
            file_issues = []
            for text, line, src in extractor.texts:
                text_clean = text.strip()
                if not text_clean:
                    continue
                vs = find_violations(text_clean)
                for desc, match, context in vs:
                    file_issues.append((line, src, desc, match, context))
            
            if file_issues:
                print(f'\n=== {rel} ({len(file_issues)} issues) ===')
                for line, src, desc, match, context in file_issues:
                    print(f'  L{line} [{src}] {desc}: ...{context}...')
                total_issues += len(file_issues)

print(f'\n\nTotal: {total_issues} Pangu spacing issues found')
