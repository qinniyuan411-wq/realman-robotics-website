# -*- coding: utf-8 -*-
import sys, os, re, openpyxl
sys.stdout.reconfigure(encoding='utf-8')

wb = openpyxl.load_workbook(r'C:\Users\Qinni Yuan\Desktop\realman-robotics-website\prop\translation\products.xlsx')
ws = wb.active
root = r'C:\Users\Qinni Yuan\Desktop\realman-robotics-website\cn\products'

xlsx_cn = []
for row in ws.iter_rows(min_row=2, values_only=True):
    cn = str(row[1]) if row[1] else ''
    xlsx_cn.append(cn)

files_order = [
    'whj-joint-modules.html',
    'whj-torque-joint-modules.html',
    'whg-joint-modules.html',
    'rm65.html',
    'rm75.html',
    'rml63.html',
    'eco65.html',
    'eco63.html',
    'eco62.html',
    'rx75.html',
    'realbot-humanoid.html',
    'single-arm-lift.html',
    'dual-arm-lift.html',
]

for idx, fn in enumerate(files_order):
    fp = os.path.join(root, fn)
    with open(fp, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    current_intro = ''
    for i, line in enumerate(lines):
        if 'margin-top:16px; max-width:640px' in line:
            current_intro = lines[i+1].strip() if i+1 < len(lines) else ''
            break
    expected = xlsx_cn[idx]
    if not expected:
        print(f'[SKIP] {fn}: no Chinese in xlsx')
    elif expected in current_intro or current_intro in expected:
        if expected == current_intro:
            print(f'[OK] {fn}')
        else:
            print(f'[DIFF] {fn}')
            print(f'  Current: {current_intro[:80]}...')
            print(f'  New:     {expected[:80]}...')
    else:
        print(f'[DIFF] {fn}')
        print(f'  Current: {current_intro[:80]}...')
        print(f'  New:     {expected[:80]}...')
