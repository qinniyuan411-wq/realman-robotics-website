import openpyxl, re, sys

sys.stdout.reconfigure(encoding='utf-8')

base = r'C:\Users\Qinni Yuan\Desktop\realman-robotics-website\cn\products'
xlsx_path = r'C:\Users\Qinni Yuan\Desktop\realman-robotics-website\prop\translation\products-core-advantages.xlsx'

sheet_to_file = {
    'RM65': 'rm65.html',
    'RM75': 'rm75.html',
    'RML63': 'rml63.html',
    'ECO65': 'eco65.html',
    'ECO63': 'eco63.html',
    'ECO62': 'eco62.html',
    'RX75': 'rx75.html',
    'RealBot': 'realbot-humanoid.html',
    'Single-Arm Lift': 'single-arm-lift.html',
    'Dual-Arm Lift': 'dual-arm-lift.html',
}

wb = openpyxl.load_workbook(xlsx_path)

total_replacements = 0
errors = []

for sheet_name, html_file in sheet_to_file.items():
    ws = wb[sheet_name]
    rows = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        en = str(row[0]) if row[0] else ''
        cn = str(row[1]) if row[1] else ''
        rows.append((en, cn))

    advantages = []
    if '\n' in rows[0][0]:
        for en_cell, cn_cell in rows:
            en_parts = en_cell.split('\n', 1)
            cn_parts = cn_cell.split('\n', 1)
            en_title = en_parts[0].strip()
            en_desc = en_parts[1].strip() if len(en_parts) > 1 else ''
            cn_title = cn_parts[0].strip()
            cn_desc = cn_parts[1].strip() if len(cn_parts) > 1 else ''
            advantages.append((en_title, en_desc, cn_title, cn_desc))
    else:
        i = 0
        while i < len(rows) - 1:
            en_title = rows[i][0].strip()
            cn_title = rows[i][1].strip()
            en_desc = rows[i+1][0].strip()
            cn_desc_raw = rows[i+1][1].strip()
            if '\n' in cn_desc_raw:
                parts = cn_desc_raw.split('\n', 1)
                cn_desc = parts[1].strip()
            else:
                cn_desc = cn_desc_raw
            advantages.append((en_title, en_desc, cn_title, cn_desc))
            i += 2

    filepath = f'{base}\\{html_file}'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    file_replacements = 0

    for en_title, en_desc, cn_title, cn_desc in advantages:
        h3_pattern = re.compile(
            r'(<h3 style="font-size:20px;[^"]*">)([^<]+)(</h3>\s*'
            r'<p style="font-size:12px;[^"]*">)([^<]+)(</p>)'
        )

        matches = list(h3_pattern.finditer(content))
        matched = False

        for m in matches:
            current_p_text = m.group(4)
            en_desc_check = en_desc[:40]
            current_check = current_p_text[:40]

            en_desc_normalized = en_desc_check.replace('\u2013', '-').replace('\u00b1', '±').replace('\u00b7', '·').replace('&', '&amp;').replace('<', '&lt;').replace('≤', '&le;')
            current_normalized = current_check.replace('&middot;', '·').replace('&plusmn;', '±').replace('&ndash;', '-').replace('&amp;', '&').replace('&lt;', '<').replace('&le;', '≤')
            en_desc_normalized2 = en_desc_check.replace('&middot;', '·').replace('&plusmn;', '±').replace('&ndash;', '-').replace('&amp;', '&').replace('&lt;', '<').replace('&le;', '≤')

            if (current_check.startswith(en_desc_check[:30]) or
                current_normalized.startswith(en_desc_normalized2[:30]) or
                en_desc_normalized.startswith(current_check[:30])):

                old_text = m.group(0)
                new_text = m.group(1) + cn_title + m.group(3).replace(m.group(4), '') + cn_desc + m.group(5)
                new_text = m.group(1) + cn_title + '</h3>\n        <p style="font-size:12px; font-weight:400; line-height:1.7; letter-spacing:-0.02em; color:rgba(0,0,0,0.4);">' + cn_desc + '</p>'
                content = content.replace(old_text, new_text, 1)
                file_replacements += 1
                matched = True
                break

        if not matched:
            errors.append(f'  [{sheet_name}] Could not match: "{en_title}" / "{en_desc[:50]}..."')

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        total_replacements += file_replacements
        print(f'{html_file}: {file_replacements} advantages replaced')
    else:
        print(f'{html_file}: NO changes')

print(f'\nTotal: {total_replacements} replacements across {len(sheet_to_file)} files')
if errors:
    print('\nErrors:')
    for e in errors:
        print(e)
