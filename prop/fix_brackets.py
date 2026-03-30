import os

base = r'C:\Users\Qinni Yuan\Desktop\realman-robotics-website\cn'
count = 0
for root, dirs, files in os.walk(base):
    for f in files:
        if not f.endswith('.html'):
            continue
        fp = os.path.join(root, f)
        with open(fp, 'r', encoding='utf-8') as fh:
            content = fh.read()
        if '详细需求（选填）' in content:
            content = content.replace('详细需求（选填）', '详细需求 (选填)')
            with open(fp, 'w', encoding='utf-8') as fh:
                fh.write(content)
            count += 1
            print(f'Updated: {os.path.relpath(fp, base)}')
print(f'\nTotal: {count} files updated')
