# -*- coding: utf-8 -*-
import sys, openpyxl
sys.stdout.reconfigure(encoding='utf-8')
wb = openpyxl.load_workbook(r'C:\Users\Qinni Yuan\Desktop\realman-robotics-website\prop\translation\odm.xlsx')
ws = wb.active
with open(r'C:\Users\Qinni Yuan\Desktop\realman-robotics-website\cn\main\solutions.html', 'r', encoding='utf-8') as f:
    content = f.read()
for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True)):
    cn = str(row[1]) if row[1] else ''
    if not cn or len(cn) < 4:
        continue
    if cn not in content:
        en = str(row[0]) if row[0] else ''
        print(f'Row {i+2}: NOT in HTML:')
        print(f'  CN: "{cn}"')
        print(f'  EN: "{en}"')
        print()
print('Done')
