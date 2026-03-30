import os
import re
import sys
from html.parser import HTMLParser

sys.stdout.reconfigure(encoding='utf-8')

class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.texts = []
        self.skip_tags = {'script', 'style', 'code', 'pre'}
        self.current_skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.skip_tags:
            self.current_skip += 1
        if self.current_skip == 0:
            for attr_name, attr_val in attrs:
                if attr_val and attr_name in ('alt', 'title', 'placeholder', 'content'):
                    line = self.getpos()[0]
                    self.texts.append((attr_val, line, f'{attr_name}'))

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

patterns = [
    (re.compile(f'({CJK})({LATIN})'), 'CJK紧挨Latin'),
    (re.compile(f'({LATIN})({CJK})'), 'Latin紧挨CJK'),
    (re.compile(f'({CJK})({DIGIT})'), 'CJK紧挨数字'),
    (re.compile(f'({DIGIT})({CJK})'), '数字紧挨CJK'),
]

SKIP_WORDS = ['realman', 'mailto:', 'http://', 'https://', '.html', '.js', '.css',
              '.png', '.jpg', '.svg', '.pdf', '../', 'supabase', 'addEventListener',
              'querySelector', 'className', 'innerHTML', 'textContent', 'getElementById']

def find_violations(text):
    violations = []
    for pattern, desc in patterns:
        for m in pattern.finditer(text):
            s = max(0, m.start() - 10)
            e = min(len(text), m.end() + 10)
            ctx = text[s:e].strip()
            skip = False
            for sw in SKIP_WORDS:
                if sw.lower() in ctx.lower():
                    skip = True
                    break
            if not skip:
                violations.append((desc, ctx))
    return violations

base = r'C:\Users\Qinni Yuan\Desktop\realman-robotics-website'
total = 0

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

            ext = TextExtractor()
            try:
                ext.feed(content)
            except:
                continue

            issues = []
            for text, line, src in ext.texts:
                t = text.strip()
                if not t:
                    continue
                for desc, ctx in find_violations(t):
                    issues.append((line, src, desc, ctx))

            if issues:
                print(f'\n=== {rel} ({len(issues)}) ===')
                for line, src, desc, ctx in issues:
                    print(f'  L{line} [{src}] {desc}: "{ctx}"')
                total += len(issues)

print(f'\n共发现 {total} 处盘古之白缺失')
