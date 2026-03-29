# -*- coding: utf-8 -*-
import sys, os
sys.stdout.reconfigure(encoding='utf-8')

root = r'C:\Users\Qinni Yuan\Desktop\realman-robotics-website\cn\products'

replacements = [
    ('whj-torque-joint-modules.html',
     'Torque-sensing harmonic joint modules with built-in force feedback, available in 10, 30, and 60 N&middot;m rated torque options, in compact &Oslash;50\u201370 mm form factors for force-controlled robotic applications.',
     '力控谐波关节模组内置高精度力反馈，提供 10 至 60 N·m 额定扭矩选项，采用 Ø50–70 mm 紧凑构型，专为力控机器人应用深度定制。'),

    ('rm65.html',
     '6-DOF humanoid-configuration robotic arm with 5 kg payload, 610\u2013627 mm reach, 7.2 kg ultra-lightweight body, and &plusmn;0.05 mm repeatability. Available in Standard and Six-Axis Force variants.',
     '6 自由度仿人构型机械臂具备 5 kg 负载与 610–627 mm 臂展，其 7.2 kg 的超轻量化机身可实现 ±0.05 mm 重复定位精度，提供标准版与六维力版可选。'),

    ('rm75.html',
     '7-DOF humanoid-configuration robotic arm with redundant kinematics, 5 kg payload, 610\u2013627 mm reach, and &plusmn;0.05 mm repeatability. Available in Standard and Six-Axis Force variants.',
     '7 自由度仿人构型机械臂具备冗余运动学特性，提供 5 kg 负载与 610–627 mm 臂展，重复定位精度达 ±0.05 mm，提供标准版与六维力版可选。'),

    ('rml63.html',
     '6-DOF extended-reach humanoid robotic arm with 900\u2013917 mm working radius, 3 kg payload, &plusmn;0.05 mm repeatability, and up to 2.8 m/s TCP speed. Available in Standard and Six-Axis Force variants.',
     '6 自由度长臂展仿人机械臂工作半径达 900–917 mm，具备 3 kg 负载、±0.05 mm 重复定位精度及最高 2.8 m/s 的末端速度，提供标准版与六维力版可选。'),

    ('eco65.html',
     '6-DOF collaborative robotic arm with 5 kg payload, 610\u2013627 mm reach, full mechanical brakes on all joints, and &plusmn;0.05 mm repeatability. Available in Standard and Six-Axis Force variants.',
     '6 自由度协作机械臂具备 5 kg 负载与 610–627 mm 臂展，全关节标配机械抱闸，重复定位精度达 ±0.05 mm，提供标准版与六维力版可选。'),

    ('eco63.html',
     '6-DOF collaborative robotic arm with extended 900\u2013917 mm reach, 3 kg payload, and &plusmn;0.05 mm repeatability. Available in Standard and Six-Axis Force variants.',
     '6 自由度长臂展协作机械臂工作半径延伸至 900–917 mm，具备 3 kg 负载与 ±0.05 mm 重复定位精度，提供标准版与六维力版可选。'),

    ('rx75.html',
     '7-DOF humanoid-wrist robotic arm with built-in six-axis force sensing, 5 kg payload, 709\u2013732 mm reach, and dual-arm ready design. Available in Standard and Vision (Intel RealSense 405) variants.',
     '7 自由度仿人腕部机械臂内置六维力传感器，具备 5 kg 负载与 709–732 mm 臂展，支持双臂协同扩展，提供标准版与视觉版（搭载 Intel RealSense 405）可选。'),
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
        print(f'STILL NOT FOUND: {fn}')
        for i, line in enumerate(c.split('\n')):
            if 'margin-top:16px; max-width:640px' in line:
                content = c.split('\n')[i+1].strip() if i+1 < len(c.split('\n')) else ''
                print(f'  Actual: {repr(content[:200])}')
                print(f'  Expect: {repr(en[:200])}')
                break
