"""
Strip the leftover inline `<script>tailwind.config = {...}</script>` block from
every HTML file. After we replaced tailwind.js (the JIT compiler that defined
the global `tailwind`) with a precompiled tailwind.css stylesheet, the inline
config script throws `tailwind is not defined` in every browser console (caught
by the U-5 cross-browser test on Chromium / Firefox / WebKit).

We delete the whole block (including its surrounding <script> tags) since
prop/tailwind.css is generated from tailwind.config.js, which already encodes
the same fontFamily/borderRadius theme.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# DOTALL: .* spans newlines; non-greedy to stop at the first </script>.
# We anchor on `tailwind.config` to avoid touching unrelated <script> blocks.
PATTERN = re.compile(
    r"\s*<script>\s*tailwind\.config\s*=\s*\{.*?\}\s*</script>\s*",
    re.DOTALL,
)

def main():
    files = list((ROOT / "cn").rglob("*.html")) + list((ROOT / "en").rglob("*.html"))
    changed = 0
    for f in files:
        text = f.read_text(encoding="utf-8")
        new = PATTERN.sub("\n  ", text, count=1)
        if new != text:
            f.write_text(new, encoding="utf-8", newline="\n")
            changed += 1
    print(f"Stripped tailwind.config block from {changed}/{len(files)} files")

if __name__ == "__main__":
    main()
