import re, os, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE = r'C:\Users\Qinni Yuan\Desktop\realman-robotics-website\cn'

# ── Translation map for alt/title/visible text fragments ──
# Order matters: longer/more specific patterns first
TRANSLATIONS = [
    # Visible text
    ('Standard Version — Detail Views', '标准版 — 细节展示'),
    ('ECO62 Standard — Main View', 'ECO62 标准版 — 主视图'),

    # title attributes
    ('Download Product Specs PDF', '下载产品手册 PDF'),

    # about-us news alt
    ('Spring Festival Gala Robot', '春晚机器人'),
    ("People's Daily Coverage", '人民日报报道'),
    ('2025 CSR Forum', '2025 社会责任论坛'),
    ('ETH Zürich', '苏黎世联邦理工学院'),

    # home.html alt
    ('Robotic Arms', '机械臂'),
    ('Joint Modules', '关节模组'),
    ('Wheeled Robots', '轮式机器人'),
    ('Teleoperation', '遥操作'),

    # developer-center alt
    ('Product Specs', '产品手册'),

    # Dual-arm lift robot alt
    ('Dual-Arm Lift Robot 3/4 View', '双臂升降机器人 3/4 视图'),
    ('Dual-Arm Lift Robot Front View', '双臂升降机器人 正视图'),
    ('Dual-Arm Lift Robot Side View', '双臂升降机器人 侧视图'),
    ('Dual-Arm Lift Robot Top View', '双臂升降机器人 俯视图'),

    # Single-arm lift robot alt
    ('Single-Arm Lift Robot Perspective', '单臂升降机器人 透视图'),
    ('Single-Arm Lift Robot Side View', '单臂升降机器人 侧视图'),
    ('Single-Arm Lift Robot Top View', '单臂升降机器人 俯视图'),

    # RealBOT alt
    ('RealBOT Front View', 'RealBOT 正视图'),
    ('RealBOT Side Profile', 'RealBOT 侧面图'),
    ('RealBOT Front Alternate', 'RealBOT 正面备选'),
    ('RealBOT 3/4 Angle', 'RealBOT 3/4 角度'),

    # Product alt - compound patterns (more specific first)
    # RM65
    ('RM65 Standard - Front View', 'RM65 标准版 - 正视图'),
    ('RM65 Standard - Side View', 'RM65 标准版 - 侧视图'),
    ('RM65 Standard - Perspective', 'RM65 标准版 - 透视图'),
    ('RM65 Standard - Detail', 'RM65 标准版 - 细节图'),
    ('RM65 Six-Axis Force - Front View', 'RM65 六维力版 - 正视图'),
    ('RM65 Six-Axis Force - Side View', 'RM65 六维力版 - 侧视图'),
    ('RM65 Six-Axis Force - Perspective', 'RM65 六维力版 - 透视图'),
    ('RM65 Six-Axis Force - Detail', 'RM65 六维力版 - 细节图'),
    ('RM65 Standard Version', 'RM65 标准版'),
    ('RM65 Six-Axis Force Version', 'RM65 六维力版'),

    # RM75
    ('RM75 Standard - Front View', 'RM75 标准版 - 正视图'),
    ('RM75 Standard - Side View', 'RM75 标准版 - 侧视图'),
    ('RM75 Standard - Perspective', 'RM75 标准版 - 透视图'),
    ('RM75 Standard - Detail', 'RM75 标准版 - 细节图'),
    ('RM75 Six-Axis Force - Front View', 'RM75 六维力版 - 正视图'),
    ('RM75 Six-Axis Force - Side View', 'RM75 六维力版 - 侧视图'),
    ('RM75 Six-Axis Force - Perspective', 'RM75 六维力版 - 透视图'),
    ('RM75 Six-Axis Force - Detail', 'RM75 六维力版 - 细节图'),
    ('RM75 Standard Version', 'RM75 标准版'),
    ('RM75 Six-Axis Force Version', 'RM75 六维力版'),

    # RML63
    ('RML63 Standard - View 1', 'RML63 标准版 - 视角 1'),
    ('RML63 Standard - View 2', 'RML63 标准版 - 视角 2'),
    ('RML63 Standard - View 3', 'RML63 标准版 - 视角 3'),
    ('RML63 Standard - View 4', 'RML63 标准版 - 视角 4'),
    ('RML63 Six-Axis Force - View 1', 'RML63 六维力版 - 视角 1'),
    ('RML63 Six-Axis Force - View 2', 'RML63 六维力版 - 视角 2'),
    ('RML63 Six-Axis Force - View 3', 'RML63 六维力版 - 视角 3'),
    ('RML63 Six-Axis Force - View 4', 'RML63 六维力版 - 视角 4'),
    ('RML63 Standard Version', 'RML63 标准版'),
    ('RML63 Six-Axis Force Version', 'RML63 六维力版'),

    # ECO62
    ('ECO62 Standard - Main View', 'ECO62 标准版 - 主视图'),
    ('ECO62 - Angle 1', 'ECO62 - 角度 1'),
    ('ECO62 - Angle 2', 'ECO62 - 角度 2'),
    ('ECO62 - Angle 3', 'ECO62 - 角度 3'),
    ('ECO62 - Angle 4', 'ECO62 - 角度 4'),

    # ECO63
    ('ECO63 Standard - Angle 1', 'ECO63 标准版 - 角度 1'),
    ('ECO63 Standard - Angle 2', 'ECO63 标准版 - 角度 2'),
    ('ECO63 Standard - Angle 3', 'ECO63 标准版 - 角度 3'),
    ('ECO63 Standard - Angle 4', 'ECO63 标准版 - 角度 4'),
    ('ECO63 Standard - Angle 5', 'ECO63 标准版 - 角度 5'),
    ('ECO63 Standard - Angle 6', 'ECO63 标准版 - 角度 6'),
    ('ECO63 Six-Axis Force - Angle 1', 'ECO63 六维力版 - 角度 1'),
    ('ECO63 Six-Axis Force - Angle 2', 'ECO63 六维力版 - 角度 2'),
    ('ECO63 Six-Axis Force - Angle 3', 'ECO63 六维力版 - 角度 3'),
    ('ECO63 Six-Axis Force - Angle 4', 'ECO63 六维力版 - 角度 4'),
    ('ECO63 Six-Axis Force - Angle 5', 'ECO63 六维力版 - 角度 5'),
    ('ECO63 Six-Axis Force - Angle 6', 'ECO63 六维力版 - 角度 6'),
    ('ECO63 Standard Version', 'ECO63 标准版'),
    ('ECO63 Six-Axis Force Version', 'ECO63 六维力版'),

    # ECO65
    ('ECO65 Standard - Angle 1', 'ECO65 标准版 - 角度 1'),
    ('ECO65 Standard - Angle 2', 'ECO65 标准版 - 角度 2'),
    ('ECO65 Standard - Angle 3', 'ECO65 标准版 - 角度 3'),
    ('ECO65 Standard - Angle 4', 'ECO65 标准版 - 角度 4'),
    ('ECO65 Standard - Angle 5', 'ECO65 标准版 - 角度 5'),
    ('ECO65 Standard - Angle 6', 'ECO65 标准版 - 角度 6'),
    ('ECO65 Six-Axis Force - Angle 1', 'ECO65 六维力版 - 角度 1'),
    ('ECO65 Six-Axis Force - Angle 2', 'ECO65 六维力版 - 角度 2'),
    ('ECO65 Six-Axis Force - Angle 3', 'ECO65 六维力版 - 角度 3'),
    ('ECO65 Six-Axis Force - Angle 4', 'ECO65 六维力版 - 角度 4'),
    ('ECO65 Six-Axis Force - Angle 5', 'ECO65 六维力版 - 角度 5'),
    ('ECO65 Six-Axis Force - Angle 6', 'ECO65 六维力版 - 角度 6'),
    ('ECO65 Standard Version', 'ECO65 标准版'),
    ('ECO65 Six-Axis Force Version', 'ECO65 六维力版'),

    # RX75
    ('RX75 Standard - Angle 1', 'RX75 标准版 - 角度 1'),
    ('RX75 Standard - Angle 2', 'RX75 标准版 - 角度 2'),
    ('RX75 Standard - Angle 3', 'RX75 标准版 - 角度 3'),
    ('RX75 Standard - Angle 4', 'RX75 标准版 - 角度 4'),
    ('RX75 Standard - Angle 5', 'RX75 标准版 - 角度 5'),
    ('RX75 Standard - Angle 6', 'RX75 标准版 - 角度 6'),
    ('RX75 Standard Version', 'RX75 标准版'),
    ('RX75 Vision Version', 'RX75 视觉版'),

    # WHJ Joint Modules
    ('WHJ03 Joint Module', 'WHJ03 关节模组'),
    ('WHJ10-B Joint Module', 'WHJ10-B 关节模组'),
    ('WHJ10-N Joint Module', 'WHJ10-N 关节模组'),
    ('WHJ30 Joint Module', 'WHJ30 关节模组'),
    ('WHJ60 Joint Module', 'WHJ60 关节模组'),
    ('WHJ120 Joint Module', 'WHJ120 关节模组'),

    # WHJ Torque
    ('WHJ10 Torque Version', 'WHJ10 力矩版'),
    ('WHJ30 Torque Version', 'WHJ30 力矩版'),
    ('WHJ60 Torque Version', 'WHJ60 力矩版'),

    # WHG Joint Modules
    ('WHG1410 Joint Module', 'WHG1410 关节模组'),
    ('WHG1730 Joint Module', 'WHG1730 关节模组'),
    ('WHG2060 Joint Module', 'WHG2060 关节模组'),
    ('WHG25120 Joint Module', 'WHG25120 关节模组'),
    ('WHG32240 Joint Module', 'WHG32240 关节模组'),
    ('WHG32360 Joint Module', 'WHG32360 关节模组'),
]

# Files to process
TARGET_FILES = []
for sub in ['main', 'products']:
    d = os.path.join(BASE, sub)
    for f in sorted(os.listdir(d)):
        if f.endswith('.html'):
            TARGET_FILES.append(os.path.join(sub, f))

total_changes = 0
changed_files = []

for filepath in TARGET_FILES:
    fullpath = os.path.join(BASE, filepath)
    with open(fullpath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    file_changes = 0

    for en, cn in TRANSLATIONS:
        count = content.count(en)
        if count > 0:
            content = content.replace(en, cn)
            file_changes += count

    if file_changes > 0:
        with open(fullpath, 'w', encoding='utf-8') as f:
            f.write(content)
        total_changes += file_changes
        changed_files.append((filepath, file_changes))
        print(f"✅ {filepath}: {file_changes} 处替换")
    else:
        pass  # no changes needed

print(f"\n{'=' * 60}")
print(f"总计：{len(changed_files)} 个文件，{total_changes} 处替换")
print(f"{'=' * 60}")

# Verify no src paths were accidentally changed
print("\n🔍 验证 src 路径完整性...")
errors = 0
for filepath in TARGET_FILES:
    fullpath = os.path.join(BASE, filepath)
    with open(fullpath, 'r', encoding='utf-8') as f:
        content = f.read()
    # Check all src attributes still point to valid-looking paths
    for m in re.finditer(r'src="([^"]+)"', content):
        src = m.group(1)
        if '标准版' in src or '六维力版' in src or '关节模组' in src or '角度' in src or '视图' in src:
            if '../../prop/' in src:
                # This is a file path that got accidentally translated
                print(f"  ❌ {filepath}: src 路径被意外修改: {src}")
                errors += 1

# Also verify href paths
for filepath in TARGET_FILES:
    fullpath = os.path.join(BASE, filepath)
    with open(fullpath, 'r', encoding='utf-8') as f:
        content = f.read()
    for m in re.finditer(r'href="([^"]+)"', content):
        href = m.group(1)
        if href.startswith('../../prop/') or href.startswith('../'):
            if '标准版' in href and 'products-images' not in href:
                print(f"  ❌ {filepath}: href 路径被意外修改: {href}")
                errors += 1

if errors == 0:
    print("  ✅ 所有 src/href 路径均未被意外修改")
else:
    print(f"  ⚠️ 发现 {errors} 处路径问题，需要修复！")
