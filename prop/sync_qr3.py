import os

old_block = '''        <div>
          <span style="font-size:12px; font-weight:500; letter-spacing:0.08em; text-transform:uppercase; color:rgba(255,255,255,0.35); display:block; margin-bottom:16px;">关注我们</span>
          <img src="../../prop/qr_code_official-wechat-account.png" alt="微信公众号二维码" style="width:120px; height:120px; border-radius:0.25rem;">
        </div>'''

new_block = '''        <div>
          <span style="font-size:12px; font-weight:500; letter-spacing:0.08em; text-transform:uppercase; color:rgba(255,255,255,0.35); display:block; margin-bottom:16px;">关注我们</span>
          <div style="display:flex; gap:24px;">
            <div style="text-align:center;">
              <img src="../../prop/qr-code-official-wechat-account.jpg" alt="微信公众号二维码" style="width:120px; border-radius:0.25rem;">
              <span style="font-size:11px; font-weight:400; color:rgba(255,255,255,0.5); display:block; margin-top:8px;">微信公众号</span>
            </div>
            <div style="text-align:center;">
              <img src="../../prop/qr-code-official-wechat-channels.jpg" alt="微信视频号二维码" style="width:120px; border-radius:0.25rem;">
              <span style="font-size:11px; font-weight:400; color:rgba(255,255,255,0.5); display:block; margin-top:8px;">微信视频号</span>
            </div>
            <div style="text-align:center;">
              <img src="../../prop/qr-code-official-douyin.jpg" alt="官方抖音号二维码" style="width:120px; border-radius:0.25rem;">
              <span style="font-size:11px; font-weight:400; color:rgba(255,255,255,0.5); display:block; margin-top:8px;">官方抖音号</span>
            </div>
          </div>
        </div>'''

base = r'C:\Users\Qinni Yuan\Desktop\realman-robotics-website\cn'
count = 0
for root, dirs, files in os.walk(base):
    for f in files:
        if not f.endswith('.html'):
            continue
        fp = os.path.join(root, f)
        if fp.replace(os.sep, '/').endswith('main/home.html'):
            continue
        with open(fp, 'r', encoding='utf-8') as fh:
            content = fh.read()
        if old_block in content:
            content = content.replace(old_block, new_block)
            with open(fp, 'w', encoding='utf-8') as fh:
                fh.write(content)
            count += 1
            print(f'Updated: {os.path.relpath(fp, base)}')
print(f'\nTotal: {count} files updated')
