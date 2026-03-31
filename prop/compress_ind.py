import subprocess, os

ffmpeg = r"C:\Users\Qinni Yuan\AppData\Local\Programs\Python\Python311\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
video_dir = r"C:\Users\Qinni Yuan\Desktop\realman-robotics-website\prop\industry-solutions-video-new"

targets = [
    ("data-collection.mp4", 10),
    ("autonomous-delivery.mp4", 60),
    ("home-assistant.mp4", 45),
    ("smart-retail.mp4", 45),
    ("industrial-sorting.mp4", 18),
    ("smart-food-service.mp4", 18),
]

for name, target_mb in targets:
    src = os.path.join(video_dir, name)
    tmp = os.path.join(video_dir, f"_compressed_{name}")
    size_mb = os.path.getsize(src) / (1024*1024)

    print(f"\n{'='*50}")
    print(f"Processing: {name} ({size_mb:.1f} MB -> target {target_mb} MB)")

    probe = subprocess.run([ffmpeg, "-i", src], capture_output=True, text=True, timeout=30)
    stderr = probe.stderr
    duration = None
    src_width = src_height = 0
    for line in stderr.split('\n'):
        if 'Duration:' in line:
            parts = line.split('Duration:')[1].split(',')[0].strip()
            h, m, s = parts.split(':')
            duration = int(h)*3600 + int(m)*60 + float(s)
        if 'Video:' in line:
            for seg in line.split('Video:')[1].split(','):
                seg = seg.strip()
                if 'x' in seg:
                    res_part = seg.split()[0]
                    if 'x' in res_part:
                        try:
                            w, h2 = res_part.split('x')
                            if w.isdigit() and h2.isdigit():
                                src_width, src_height = int(w), int(h2)
                        except:
                            pass

    if not duration:
        print("  Could not determine duration, skipping")
        continue

    print(f"  Duration: {duration:.1f}s, Resolution: {src_width}x{src_height}")

    target_bitrate_kbps = int((target_mb * 8 * 1024) / duration)
    video_bitrate = max(target_bitrate_kbps - 128, 500)

    scale_filter = []
    if src_width > 1920 or src_height > 1920:
        if src_width > src_height:
            scale_filter = ["-vf", "scale=1920:-2"]
        else:
            scale_filter = ["-vf", "scale=-2:1920"]
        print(f"  Downscaling to 1080p")

    print(f"  Video bitrate: {video_bitrate} kbps")

    cmd = [
        ffmpeg, "-y", "-i", src,
        *scale_filter,
        "-c:v", "libx264",
        "-b:v", f"{video_bitrate}k",
        "-maxrate", f"{int(video_bitrate*1.5)}k",
        "-bufsize", f"{video_bitrate*2}k",
        "-preset", "slow",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        tmp
    ]

    print(f"  Compressing...")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr[-500:]}")
        continue

    new_size = os.path.getsize(tmp) / (1024*1024)
    os.remove(src)
    os.rename(tmp, src)
    print(f"  Done: {size_mb:.1f} MB -> {new_size:.1f} MB")

print(f"\n{'='*50}")
print("Final sizes (all files):")
total = 0
for f in sorted(os.listdir(video_dir)):
    if f.endswith('.mp4'):
        sz = os.path.getsize(os.path.join(video_dir, f)) / (1024*1024)
        total += sz
        print(f"  {f}: {sz:.1f} MB")
print(f"\n  TOTAL: {total:.1f} MB")
