import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

CSS_INJECT = """
    /* ---- Ultra-wide viewport constraint ---- */
    body {
      max-width: 1920px;
      margin-left: auto;
      margin-right: auto;
    }
    html {
      background: #F6F6F6;
    }
    nav {
      max-width: 1920px;
      left: 0;
      right: 0;
      margin-left: auto;
      margin-right: auto;
    }
"""

base = r'C:\Users\Qinni Yuan\Desktop\realman-robotics-website'
count = 0

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

            original = content
            changes = []

            head_end = content.find('</head>')
            first_style_end = content.find('</style>', 0, head_end)

            if first_style_end != -1:
                content = content[:first_style_end] + CSS_INJECT + content[first_style_end:]
                changes.append('added ultra-wide CSS')

            if 'width: 100vw;' in content:
                content = content.replace('width: 100vw;', 'width: 100%;')
                changes.append('fixed 100vw → 100%')

            if content != original:
                with open(fp, 'w', encoding='utf-8') as fh:
                    fh.write(content)
                count += 1
                print(f'Updated: {rel} ({", ".join(changes)})')

print(f'\nTotal: {count} files updated')
