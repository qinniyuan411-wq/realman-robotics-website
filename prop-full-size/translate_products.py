# -*- coding: utf-8 -*-
import sys, os, re
sys.stdout.reconfigure(encoding='utf-8')

root = r'C:\Users\Qinni Yuan\Desktop\realman-robotics-website\cn\products'

# ===== COMMON TRANSLATIONS (apply to ALL files) =====
common = {
    '>Core Advantages<': '>核心优势<',
    '>Technical Specifications<': '>技术参数<',
    '>Parameter<': '>参数<',
    '>Weight<': '>重量<',
    '>Rated Voltage<': '>额定电压<',
    '>Rated Current<': '>额定电流<',
    '>Rated Power<': '>额定功率<',
    '>Peak Speed<': '>峰值转速<',
    '>Rated Torque<': '>额定扭矩<',
    '>Gear Ratio<': '>减速比<',
    '>Operating Temp<': '>工作温度<',
    '>Brake Type<': '>制动类型<',
    '>Comm Interface<': '>通信接口<',
    '>Communication<': '>通信接口<',
    '>Hollow Shaft<': '>中空通孔<',
    '>Degrees of Freedom<': '>自由度<',
    '>Configuration<': '>构型<',
    '>Joint Brake Type<': '>关节制动方式<',
    '>Working Radius<': '>工作半径<',
    '>Payload<': '>负载<',
    '>Net Weight<': '>净重<',
    '>Repeatability<': '>重复定位精度<',
    '>TCP Linear Speed<': '>TCP 线速度<',
    '>Typical Power<': '>额定功率<',
    '>Peak Power<': '>峰值功率<',
    '>Base Diameter<': '>底座直径<',
    '>Six-Axis Force Range<': '>六轴力范围<',
    '>Six-Axis Force Accuracy<': '>六轴力精度<',
    '>Power Supply<': '>供电电压<',
    '>Operating Temperature<': '>工作温度<',
    '>Overall Dimensions<': '>整体尺寸<',
    '>Total Weight<': '>整机重量<',
    '>Single Arm Payload<': '>单臂负载<',
    '>Lifting Stroke<': '>升降行程<',
    '>Movement Speed<': '>移动速度<',
    '>Turning Radius<': '>转弯半径<',
    '>Vertical Reach<': '>垂直臂展<',
    '>Horizontal Reach<': '>水平臂展<',
    '>Endurance<': '>续航时间<',
    '>Charging Supply<': '>充电电压<',
    '>Robot Arm Model<': '>机械臂型号<',
    '>Vision System<': '>视觉系统<',
    # Table header categories
    'Physical &amp; Performance': '物理与性能',
    'System &amp; Power': '系统与电源',
    'System &amp; Equipment': '系统与设备',
    'Sensors &amp; Power': '传感器与电源',
    # Table values (text-type values)
    '>Humanoid<': '>人形<',
    '>Collaborative<': '>协作型<',
    '>Electromagnetic<': '>电磁<',
    '>Integrated<': '>集成<',
}

# ===== PER-FILE TRANSLATIONS =====
per_file = {
    'whj-joint-modules.html': {
        '>WHJ Series<': '>WHJ 系列<',
        '>High Torque Density<': '>高扭矩密度<',
        '>High Reliability<': '>高可靠性<',
        '>High Precision<': '>高精度<',
        'Dimensions (D&times;L)': '尺寸 (D×L)',
        '>Hollow Shaft</span>': '>中空通孔</span>',
        '>Spring<': '>弹簧<',
        '>Pin-Type<': '>销钉式<',
    },
    'whj-torque-joint-modules.html': {
        '>WHJ Torque Series<': '>WHJ 力矩系列<',
        '>High Force Sensitivity<': '>高力感灵敏度<',
        '>Dynamic Force Closed-Loop Control<': '>动态力闭环控制<',
        '>Intrinsic Compliant Interaction<': '>本征柔顺交互<',
        '>Unit Weight<': '>单元重量<',
        'Dimensions (D&times;L)': '尺寸 (D×L)',
        'Hollow Shaft &Oslash;': '中空通孔 Ø',
        '>Spring-Applied<': '>常闭弹簧<',
        '>Pin-Type<': '>销钉式<',
    },
    'whg-joint-modules.html': {
        '>WHG Series<': '>WHG 系列<',
        '>High Power Density<': '>高功率密度<',
        '>High Rigidity<': '>高刚度<',
        '>High Precision<': '>高精度<',
        'Dimensions (D&times;H)': '尺寸 (D×H)',
    },
    'rm65.html': {
        '>RM65 Series<': '>RM65 系列<',
        '>Ultra-Lightweight<': '>超轻量化<',
        '>Humanoid Config<': '>人形构型<',
        '>Integrated Force Sensing<': '>集成力感知<',
        '>High Repeatability<': '>高重复精度<',
        '>Versatile Applications<': '>多场景应用<',
        '>RM65 Standard Version<': '>RM65 标准版<',
        '>RM65 Six-Axis Force Version<': '>RM65 六轴力版<',
        '>RM65 Standard<': '>RM65 标准版<',
        '>RM65 Six-Axis Force<': '>RM65 六轴力版<',
        '>Standard Version<': '>标准版<',
        '>Six-Axis Force Version<': '>六轴力版<',
    },
    'rm75.html': {
        '>RM75 Series<': '>RM75 系列<',
        '>7-DOF Redundancy<': '>7 自由度冗余<',
        '>Ultra-Lightweight<': '>超轻量化<',
        '>Integrated Force Sensing<': '>集成力感知<',
        '>High Repeatability<': '>高重复精度<',
        '>Versatile Applications<': '>多场景应用<',
        '>RM75 Standard Version<': '>RM75 标准版<',
        '>RM75 Six-Axis Force Version<': '>RM75 六轴力版<',
        '>RM75 Standard<': '>RM75 标准版<',
        '>RM75 Six-Axis Force<': '>RM75 六轴力版<',
        '>Standard Version<': '>标准版<',
        '>Six-Axis Force Version<': '>六轴力版<',
    },
    'rml63.html': {
        '>RML63 Series<': '>RML63 系列<',
        '>Extended Reach<': '>超长臂展<',
        '>High-Speed TCP<': '>高速 TCP<',
        '>Integrated Force Sensing<': '>集成力感知<',
        '>High Repeatability<': '>高重复精度<',
        '>Versatile Applications<': '>多场景应用<',
        '>RML63 Standard Version<': '>RML63 标准版<',
        '>RML63 Six-Axis Force Version<': '>RML63 六轴力版<',
        '>RML63 Standard<': '>RML63 标准版<',
        '>RML63 Six-Axis Force<': '>RML63 六轴力版<',
        '>Standard Version<': '>标准版<',
        '>Six-Axis Force Version<': '>六轴力版<',
    },
    'eco62.html': {
        '>Ultra-Compact<': '>超紧凑<',
        '>Low Power Draw<': '>低功耗<',
        '>Multi-Industry Ready<': '>多行业适配<',
        '>Standard Version<': '>标准版<',
    },
    'eco63.html': {
        '>ECO63 Series<': '>ECO63 系列<',
        '>Extended Cobot Reach<': '>超长协作臂展<',
        '>High-Speed TCP<': '>高速 TCP<',
        '>Integrated Force Sensing<': '>集成力感知<',
        '>Multi-Industry Ready<': '>多行业适配<',
        '>ECO63 Standard Version<': '>ECO63 标准版<',
        '>ECO63 Six-Axis Force Version<': '>ECO63 六轴力版<',
        '>ECO63 Standard<': '>ECO63 标准版<',
        '>ECO63 Six-Axis Force<': '>ECO63 六轴力版<',
        '>Standard Version<': '>标准版<',
        '>Six-Axis Force Version<': '>六轴力版<',
    },
    'eco65.html': {
        '>ECO65 Series<': '>ECO65 系列<',
        '>Full Mechanical Brakes<': '>全机械制动<',
        '>Collaborative Design<': '>协作设计<',
        '>Integrated Force Sensing<': '>集成力感知<',
        '>Cost-Effective<': '>高性价比<',
        '>Multi-Industry Ready<': '>多行业适配<',
        '>ECO65 Standard Version<': '>ECO65 标准版<',
        '>ECO65 Six-Axis Force Version<': '>ECO65 六轴力版<',
        '>ECO65 Standard<': '>ECO65 标准版<',
        '>ECO65 Six-Axis Force<': '>ECO65 六轴力版<',
        '>Standard Version<': '>标准版<',
        '>Six-Axis Force Version<': '>六轴力版<',
    },
    'rx75.html': {
        '>7-DOF Humanoid Wrist<': '>7 自由度仿人腕<',
        '>Integrated Six-Axis Force<': '>集成六轴力传感<',
        '>Vision-Ready Platform<': '>视觉就绪平台<',
        '>Ultra-Lightweight<': '>超轻量化<',
        '>Dual-Arm Ready<': '>双臂适配<',
        '>Standard Version<': '>标准版<',
        '>Vision Version<': '>视觉版<',
        '>End-Effector Camera<': '>末端相机<',
        '>Material<': '>材质<',
    },
    'realbot-humanoid.html': {
        '>Modular System Design<': '>模块化系统设计<',
        '>21 Active Degrees of Freedom<': '>21 个主动自由度<',
        '>Multi-Sensor Fusion Perception<': '>多传感器融合感知<',
        '>Narrow-Passage Mobility<': '>窄通道通行能力<',
        '>Open Ecosystem Compatibility<': '>开放生态兼容<',
        '>Total Active DOF<': '>总主动自由度<',
        '>Wide-Angle Cameras<': '>广角摄像头<',
        '>LiDAR Reflectivity<': '>LiDAR 反射率<',
        '>Voice Module<': '>语音模块<',
        '>Battery Capacity<': '>电池容量<',
        '>Charging Time<': '>充电时间<',
        '>Camera Positions<': '>相机位置<',
        '>Chest / Back / Base<': '>胸部 / 背部 / 底座<',
        '>Stereo Depth / RGB<': '>立体深度 / RGB<',
        '>6-Mic (Optional)<': '>6 麦克风（可选）<',
    },
    'single-arm-lift.html': {
        '>RM65-B-V Arm<': '>RM65-B-V 机械臂<',
        '>900 mm Vertical Lift<': '>900 mm 垂直升降<',
        '>Compact Circular Base<': '>紧凑圆形底盘<',
        '>Autonomous Navigation<': '>自主导航<',
        '>Cross-Scenario<': '>跨场景应用<',
        '>Positioning Accuracy<': '>定位精度<',
        '>Core Capability<': '>核心能力<',
        '>Full-Body Control<': '>全身协同控制<',
        '>Applications<': '>应用场景<',
        '>Retail / Logistics<': '>零售 / 物流<',
        '>Navigation<': '>导航方式<',
        '>Autonomous SLAM<': '>自主 SLAM<',
        '>Manipulation<': '>操控方式<',
        '>Precise Single-Arm<': '>精准单臂操作<',
    },
    'dual-arm-lift.html': {
        '>Dual-Arm Coordination<': '>双臂协同<',
        '>900 mm Vertical Lift<': '>900 mm 垂直升降<',
        '>Vision-Equipped<': '>配备视觉<',
        '>Wired Teleoperation<': '>有线遥操<',
        '>Mobile Autonomy<': '>移动自主<',
        '>Lateral Reach<': '>横向臂展<',
        '>Forward Reach<': '>前向臂展<',
        '>Optional Arm<': '>可选机械臂<',
        '>End Effector<': '>末端执行器<',
        '>Vision Sensor<': '>视觉传感器<',
    },
}

total_changes = 0
for fn in sorted(os.listdir(root)):
    if not fn.endswith('.html'):
        continue
    fp = os.path.join(root, fn)
    with open(fp, 'r', encoding='utf-8') as f:
        c = f.read()
    orig = c
    file_changes = 0

    # Apply common translations
    for en, cn in common.items():
        if en in c:
            cnt = c.count(en)
            c = c.replace(en, cn)
            file_changes += cnt

    # Apply per-file translations
    if fn in per_file:
        for en, cn in per_file[fn].items():
            if en in c:
                cnt = c.count(en)
                c = c.replace(en, cn)
                file_changes += cnt

    if c != orig:
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(c)
        print(f'{fn}: {file_changes} replacements')
        total_changes += file_changes
    else:
        print(f'{fn}: no changes')

print(f'\nTotal: {total_changes} replacements across all files')
