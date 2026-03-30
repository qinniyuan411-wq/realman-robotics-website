import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

CJK = r'[\u4e00-\u9fff\u3400-\u4dbf]'
LATIN = r'[A-Za-z]'
DIGIT = r'[0-9]'

def pangu_space(text):
    text = re.sub(f'({CJK})({LATIN})', r'\1 \2', text)
    text = re.sub(f'({LATIN})({CJK})', r'\1 \2', text)
    text = re.sub(f'({CJK})({DIGIT})', r'\1 \2', text)
    text = re.sub(f'({DIGIT})({CJK})', r'\1 \2', text)
    return text

meta_desc_re = re.compile(r'(<meta\s+name="description"\s+content=")([^"]*?)(")')

base = r'C:\Users\Qinni Yuan\Desktop\realman-robotics-website\cn'
count = 0

for root, dirs, files in os.walk(base):
    for f in sorted(files):
        if not f.endswith('.html'):
            continue
        fp = os.path.join(root, f)
        rel = os.path.relpath(fp, base)
        with open(fp, 'r', encoding='utf-8') as fh:
            content = fh.read()

        original = content
        changes = []

        def fix_meta(m):
            old_content = m.group(2)
            new_content = pangu_space(old_content)
            if old_content != new_content:
                changes.append(('meta description', old_content[:50], new_content[:50]))
            return m.group(1) + new_content + m.group(3)

        content = meta_desc_re.sub(fix_meta, content)

        text_replacements = [
            ('TCP线速度', 'TCP 线速度'),
            ('尺寸(直径x长度)', '尺寸 (直径 x 长度)'),
        ]
        for old, new in text_replacements:
            if old in content:
                content = content.replace(old, new)
                changes.append(('text', old, new))

        if content != original:
            with open(fp, 'w', encoding='utf-8') as fh:
                fh.write(content)
            count += 1
            print(f'Updated: {rel}')
            for typ, old, new in changes:
                print(f'  [{typ}] "{old}..." → "{new}..."')

print(f'\nTotal: {count} files updated')
