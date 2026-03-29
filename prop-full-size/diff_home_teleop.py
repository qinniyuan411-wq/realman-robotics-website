# -*- coding: utf-8 -*-
import sys, openpyxl
sys.stdout.reconfigure(encoding='utf-8')

def check_diff(xlsx_path, html_path, label):
    wb = openpyxl.load_workbook(xlsx_path)
    ws = wb.active
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    print(f'\n===== {label} =====')
    diffs = []
    for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True)):
        cn = str(row[1]).strip() if row[1] else ''
        if not cn or len(cn) < 2:
            continue
        if cn not in content:
            en = str(row[0]).strip() if row[0] else ''
            diffs.append((i+2, en, cn))
    if not diffs:
        print('All matched - no differences found.')
    else:
        for row_num, en, cn in diffs:
            print(f'Row {row_num}: NOT in HTML')
            print(f'  EN: {en[:80]}')
            print(f'  CN: {cn[:80]}')
            print()

check_diff(
    r'C:\Users\Qinni Yuan\Desktop\realman-robotics-website\prop\translation\home.xlsx',
    r'C:\Users\Qinni Yuan\Desktop\realman-robotics-website\cn\main\home.html',
    'home.xlsx vs cn/main/home.html'
)

check_diff(
    r'C:\Users\Qinni Yuan\Desktop\realman-robotics-website\prop\translation\teleoperation-network.xlsx',
    r'C:\Users\Qinni Yuan\Desktop\realman-robotics-website\cn\main\teleoperation-network.html',
    'teleoperation-network.xlsx vs cn/main/teleoperation-network.html'
)
