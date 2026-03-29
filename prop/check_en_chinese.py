# -*- coding: utf-8 -*-
import sys, os, re
from html.parser import HTMLParser

sys.stdout.reconfigure(encoding='utf-8')

class VisibleTextExtractor(HTMLParser):
    SKIP_TAGS = {'script', 'style', 'meta', 'link', 'head', 'title', 'noscript'}

    def __init__(self):
        super().__init__()
        self.results = []
        self._skip_stack = 0
        self._current_tag = None

    def handle_starttag(self, tag, attrs):
        self._current_tag = tag
        if tag.lower() in self.SKIP_TAGS:
            self._skip_stack += 1
        attr_dict = dict(attrs)
        for attr_name in ('alt', 'placeholder', 'title', 'value', 'aria-label'):
            val = attr_dict.get(attr_name, '')
            if val and has_chinese(val):
                self.results.append((f'<{tag} {attr_name}=...>', val.strip()))

    def handle_endtag(self, tag):
        if tag.lower() in self.SKIP_TAGS:
            self._skip_stack = max(0, self._skip_stack - 1)

    def handle_data(self, data):
        if self._skip_stack == 0 and data.strip() and has_chinese(data):
            self.results.append(('text', data.strip()))

    def handle_comment(self, data):
        pass

def has_chinese(text):
    return bool(re.search(r'[\u4e00-\u9fff]', text))

root = r'C:\Users\Qinni Yuan\Desktop\realman-robotics-website\en'
found_any = False

for dirpath, dirs, files in os.walk(root):
    for fn in sorted(files):
        if not fn.endswith('.html'):
            continue
        fp = os.path.join(dirpath, fn)
        rel = os.path.relpath(fp, r'C:\Users\Qinni Yuan\Desktop\realman-robotics-website')
        with open(fp, 'r', encoding='utf-8') as f:
            content = f.read()

        parser = VisibleTextExtractor()
        try:
            parser.feed(content)
        except Exception as e:
            print(f'[ERROR] {rel}: {e}')
            continue

        if parser.results:
            found_any = True
            print(f'\n=== {rel} ===')
            for src, text in parser.results:
                short = text[:80].replace('\n', ' ')
                print(f'  [{src}] {short}')

if not found_any:
    print('\nAll clean - no Chinese characters found in visible text of en/ HTML files.')
else:
    print('\n--- Check complete ---')
