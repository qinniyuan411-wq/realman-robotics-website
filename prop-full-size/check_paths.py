# -*- coding: utf-8 -*-
import sys, os, re
sys.stdout.reconfigure(encoding='utf-8')
root = r'C:\Users\Qinni Yuan\Desktop\realman-robotics-website\cn'
for dp, dirs, files in os.walk(root):
    for fn in files:
        if not fn.endswith('.html'):
            continue
        fp = os.path.join(dp, fn)
        with open(fp, 'r', encoding='utf-8') as f:
            c = f.read()
        for m in re.finditer(r'src="([^"]*)"', c):
            path = m.group(1)
            if '升降机器人' in path and 'products-images' in path:
                rel = os.path.relpath(fp, r'C:\Users\Qinni Yuan\Desktop\realman-robotics-website')
                print(f'{rel}: {path}')
print('Check done')
