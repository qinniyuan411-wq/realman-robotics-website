"""
Subset HarmonyOS Sans SC woff2 fonts to only the CJK + Latin characters
actually used across the site. Reduces 4×4.2MB → 4×~200KB while keeping
brand-required typography (VI compliance).
"""
import re
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.subset import Subsetter, Options

ROOT = Path(__file__).resolve().parent.parent

# 1. Collect every unique character used across all HTML, including
#    JavaScript inline string literals (alt text, button labels, error
#    messages, dynamically-injected privacy notice, etc).
def collect_characters() -> set[str]:
    chars: set[str] = set()
    html_files = list((ROOT / "cn").rglob("*.html")) + list((ROOT / "en").rglob("*.html"))
    js_files = list((ROOT / "prop").glob("supabase-cta*.js"))
    for f in html_files + js_files:
        try:
            text = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = f.read_text(encoding="utf-8", errors="ignore")
        chars.update(text)
    return chars

# 2. Build a Unicode codepoint set: keep CJK + Latin + punctuation + digits.
#    Skip control chars, surrogates, private-use area.
def build_codepoints(chars: set[str]) -> set[int]:
    cps: set[int] = set()
    for c in chars:
        cp = ord(c)
        if cp < 0x20:
            continue
        if 0xD800 <= cp <= 0xDFFF:
            continue
        if 0xE000 <= cp <= 0xF8FF:
            continue
        cps.add(cp)
    # Always include core Latin + ASCII punctuation, common symbols, even if
    # not seen — these may appear after deploy via dynamic content.
    cps.update(range(0x20, 0x7F))
    cps.update(range(0x00A0, 0x00FF))
    cps.update(range(0x2000, 0x206F))
    cps.update(range(0x3000, 0x303F))
    cps.update(range(0xFF00, 0xFFEF))
    return cps

def subset_font(input_path: Path, output_path: Path, codepoints: set[int]) -> tuple[int, int]:
    font = TTFont(input_path)
    options = Options()
    options.flavor = "woff2"
    options.layout_features = ["*"]
    options.notdef_outline = True
    options.recalc_bounds = True
    options.drop_tables = ["DSIG"]
    options.name_IDs = ["*"]
    options.name_languages = ["*"]
    options.glyph_names = False
    subsetter = Subsetter(options=options)
    subsetter.populate(unicodes=sorted(codepoints))
    subsetter.subset(font)
    font.flavor = "woff2"
    font.save(output_path)
    before = input_path.stat().st_size
    after = output_path.stat().st_size
    return before, after

def main():
    chars = collect_characters()
    cps = build_codepoints(chars)
    cjk_cps = sum(1 for cp in cps if 0x4E00 <= cp <= 0x9FFF)
    print(f"Collected {len(chars):,} unique characters (CJK in subset: {cjk_cps:,})")

    fonts = [
        "HarmonyOS_Sans_SC_Light",
        "HarmonyOS_Sans_SC_Regular",
        "HarmonyOS_Sans_SC_Medium",
        "HarmonyOS_Sans_SC_Bold",
    ]
    fonts_dir = ROOT / "prop" / "fonts"
    total_before = 0
    total_after = 0
    print(f"\n{'Font':<35} {'Before':>10} {'After':>10} {'Saved':>8}")
    print("-" * 70)
    for name in fonts:
        in_path = fonts_dir / f"{name}.woff2"
        out_path = fonts_dir / f"{name}.subset.woff2"
        if not in_path.exists():
            print(f"  SKIP missing: {in_path}")
            continue
        before, after = subset_font(in_path, out_path, cps)
        total_before += before
        total_after += after
        print(f"{name:<35} {before/1024:>8.0f}KB {after/1024:>8.0f}KB {(1-after/before)*100:>6.1f}%")
    print("-" * 70)
    print(f"{'TOTAL':<35} {total_before/1024:>8.0f}KB {total_after/1024:>8.0f}KB {(1-total_after/total_before)*100:>6.1f}%")

if __name__ == "__main__":
    main()
