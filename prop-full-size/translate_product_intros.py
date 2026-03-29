# -*- coding: utf-8 -*-
import sys, os
sys.stdout.reconfigure(encoding='utf-8')

root = r'C:\Users\Qinni Yuan\Desktop\realman-robotics-website\cn\products'

replacements = [
    ('whj-joint-modules.html',
     'Harmonic joint modules available in 3, 10, 30, 60, and 120 N&middot;m rated torque options, featuring ultra-compact form factors from 33 mm diameter, dual encoders, a hollow shaft, and a CAN FD interface.',
     '谐波关节模组提供 3 至 120 N·m 多种额定扭矩选项，采用小至 33 mm 外径的超紧凑构型，内置双编码器与中空走线设计，并支持 CAN FD 通信接口。'),

    ('whj-torque-joint-modules.html',
     'Torque-sensing harmonic joint modules with built-in force feedback, available in 10, 30, and 60 N&middot;m rated torque options, in compact &Oslash;50&ndash;70 mm form factors for force-controlled robotic applications.',
     '力控谐波关节模组内置高精度力反馈，提供 10 至 60 N·m 额定扭矩选项，采用 Ø50–70 mm 紧凑构型，专为力控机器人应用深度定制。'),

    ('whg-joint-modules.html',
     'High-performance power joint modules available in 10, 30, 60, 120, 240, and 360 N&middot;m rated torque options, with electromagnetic brakes, dual encoders, and a hollow-shaft design for multi-axis integration.',
     '高性能动力关节模组提供 10 至 360 N·m 额定扭矩选项，标配电磁抱闸、双编码器及中空走线设计，完美适配多轴系统的高效集成。'),

    ('rm65.html',
     '6-DOF humanoid-configuration robotic arm with 5 kg payload, 610&ndash;627 mm reach, 7.2 kg ultra-lightweight body, and &plusmn;0.05 mm repeatability. Available in Standard and Six-Axis Force variants.',
     '6 自由度仿人构型机械臂具备 5 kg 负载与 610–627 mm 臂展，其 7.2 kg 的超轻量化机身可实现 ±0.05 mm 重复定位精度，提供标准版与六维力版可选。'),

    ('rm75.html',
     '7-DOF humanoid-configuration robotic arm with redundant kinematics, 5 kg payload, 610&ndash;627 mm reach, and &plusmn;0.05 mm repeatability. Available in Standard and Six-Axis Force variants.',
     '7 自由度仿人构型机械臂具备冗余运动学特性，提供 5 kg 负载与 610–627 mm 臂展，重复定位精度达 ±0.05 mm，提供标准版与六维力版可选。'),

    ('rml63.html',
     '6-DOF extended-reach humanoid robotic arm with 900&ndash;917 mm working radius, 3 kg payload, &plusmn;0.05 mm repeatability, and up to 2.8 m/s TCP speed. Available in Standard and Six-Axis Force variants.',
     '6 自由度长臂展仿人机械臂工作半径达 900–917 mm，具备 3 kg 负载、±0.05 mm 重复定位精度及最高 2.8 m/s 的末端速度，提供标准版与六维力版可选。'),

    ('eco65.html',
     '6-DOF collaborative robotic arm with 5 kg payload, 610&ndash;627 mm reach, full mechanical brakes on all joints, and &plusmn;0.05 mm repeatability. Available in Standard and Six-Axis Force variants.',
     '6 自由度协作机械臂具备 5 kg 负载与 610–627 mm 臂展，全关节标配机械抱闸，重复定位精度达 ±0.05 mm，提供标准版与六维力版可选。'),

    ('eco63.html',
     '6-DOF collaborative robotic arm with extended 900&ndash;917 mm reach, 3 kg payload, and &plusmn;0.05 mm repeatability. Available in Standard and Six-Axis Force variants.',
     '6 自由度长臂展协作机械臂工作半径延伸至 900–917 mm，具备 3 kg 负载与 ±0.05 mm 重复定位精度，提供标准版与六维力版可选。'),

    ('eco62.html',
     '6-DOF ultra-compact collaborative robotic arm with 355 mm working radius, 3.3 kg self-weight, and &plusmn;0.05 mm repeatability.',
     '6 自由度超紧凑协作机械臂工作半径为 355 mm，自重仅 3.3 kg，重复定位精度达 ±0.05 mm，满足极致空间下的高精度作业需求。'),

    ('rx75.html',
     '7-DOF humanoid-wrist robotic arm with built-in six-axis force sensing, 5 kg payload, 709&ndash;732 mm reach, and dual-arm ready design. Available in Standard and Vision (Intel RealSense 405) variants.',
     '7 自由度仿人腕部机械臂内置六维力传感器，具备 5 kg 负载与 709–732 mm 臂展，支持双臂协同扩展，提供标准版与视觉版（搭载 Intel RealSense 405）可选。'),

    ('realbot-humanoid.html',
     'Wheeled humanoid robot with 21 active DOF, dual RX75 arms (5 kg payload each), stereo depth + LiDAR perception, and 40 AH battery for extended autonomous operation.',
     '轮式仿人机器人拥有 21 个主动自由度，搭载双 RX75 机械臂（单臂负载 5 kg），融合双目深度与激光雷达感知，并配备 40 AH 大容量电池以支持长时自主作业。'),

    ('single-arm-lift.html',
     'Vertical lift mobile robot with RM65-B-V arm, 900 mm lifting stroke, 5 kg payload, compact 505 mm circular base, and autonomous SLAM navigation.',
     '升降式移动机器人搭载 RM65-B-V 机械臂，具备 900 mm 升降行程与 5 kg 负载，采用 505 mm 紧凑型圆形底盘，全面支持自主 SLAM 导航。'),
]

for fn, en, cn in replacements:
    fp = os.path.join(root, fn)
    with open(fp, 'r', encoding='utf-8') as f:
        c = f.read()
    if en in c:
        c = c.replace(en, cn)
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(c)
        print(f'OK: {fn}')
    else:
        print(f'NOT FOUND: {fn}')
        # Try to find the line to debug
        import re
        for i, line in enumerate(c.split('\n')):
            if 'margin-top:16px; max-width:640px' in line or (i > 190 and i < 200):
                print(f'  L{i+1}: {line.strip()[:120]}')
