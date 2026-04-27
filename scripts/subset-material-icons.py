"""
Subset Material Symbols Outlined to only the icons actually used across the site.

The original prop/material-symbols.css declares 14 @font-face rules covering
7 weights × 2 ranges (latin + latin-ext). The actual TTF files in prop/fonts/
total ~16.4MB. CSS hard-codes `'wght' 400` so only the 2 weight-400 files would
ever be requested in practice (~2.4MB combined), but Lighthouse still flags
the full @font-face graph as part of the critical CSS.

This script:
  1. Scans cn/**/*.html + en/**/*.html for every <span class="material-symbols-
     outlined">ICON_NAME</span>;
  2. Subsets the weight-400 latin TTF down to those ICON_NAMES (Material
     Symbols renders icons via OpenType ligatures, so we pass the icon names
     as `text` and let fontTools keep the ligature subtable + glyph + Latin
     letters/underscore needed to compose them);
  3. Writes prop/fonts/MaterialSymbolsOutlined-subset.woff2 (~target 30-60KB).

Re-run whenever new icon names are introduced.
"""
import re
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.subset import Subsetter, Options

ROOT = Path(__file__).resolve().parent.parent

ICON_PATTERN = re.compile(
    r'<span[^>]*class="[^"]*material-symbols-outlined[^"]*"[^>]*>([^<]+)</span>',
    re.IGNORECASE,
)


def collect_icons() -> set[str]:
    icons: set[str] = set()
    for html in list((ROOT / "cn").rglob("*.html")) + list((ROOT / "en").rglob("*.html")):
        text = html.read_text(encoding="utf-8", errors="ignore")
        for m in ICON_PATTERN.finditer(text):
            name = m.group(1).strip()
            if name:
                icons.add(name)
    return icons


def find_weight400_latin_ttf() -> Path:
    """Identify the weight-400 latin TTF (the smaller ~955KB latin file).

    The originals are kept on disk as kJF1Bv*.full.ttf (gitignored). The
    latin file is the smaller of the two weight-400 variants (~927-956 KB);
    the larger one (~1.4 MB) is the latin-extended cut.
    """
    candidates = sorted(
        (ROOT / "prop" / "fonts").glob("kJF1Bv*.full.ttf"),
        key=lambda p: p.stat().st_size,
    )
    for ttf in candidates:
        size = ttf.stat().st_size
        if 800_000 < size < 1_100_000:
            return ttf
    raise SystemExit(
        "Could not locate weight-400 latin TTF backup. Restore the originals "
        "named prop/fonts/kJF1Bv*.full.ttf (or kJF1Bv*.ttf) before running."
    )


def main():
    icons = collect_icons()
    print(f"Collected {len(icons)} unique icon names from HTML")

    src = find_weight400_latin_ttf()
    print(f"Source font: {src.name} ({src.stat().st_size / 1024:.1f} KB)")

    font = TTFont(str(src))
    glyph_order = set(font.getGlyphOrder())
    keep_glyphs = sorted(icons & glyph_order)
    missing = sorted(icons - glyph_order)
    if missing:
        print(f"WARNING: {len(missing)} icon names not in font glyph order:", missing)
    print(f"Resolved {len(keep_glyphs)} glyph names against font cmap")

    # Reverse-lookup each icon glyph's Private-Use codepoint in the cmap.
    # Without these codepoints in the keep-set, fontTools Subsetter prunes
    # the ligature subtables that target our icons (the OpenType
    # post-substitution glyph is "unreachable" from the kept cmap entries).
    glyph_to_cp = {}
    for cp, gname in font.getBestCmap().items():
        glyph_to_cp.setdefault(gname, cp)
    keep_codepoints = sorted(
        glyph_to_cp[g] for g in keep_glyphs if g in glyph_to_cp
    )
    print(
        f"Mapped {len(keep_codepoints)}/{len(keep_glyphs)} icon glyphs to PUA codepoints "
        f"(sample: {[hex(c) for c in keep_codepoints[:5]]})"
    )

    text = " ".join(sorted(icons))

    opts = Options()
    opts.flavor = "woff2"
    opts.layout_features = ["liga", "rlig", "dlig", "ccmp"]
    # Keep the essential `name` table records (1=family, 2=subfamily, 3=unique
    # id, 4=full, 5=version, 6=PostScript name); WITHOUT these the browser
    # can't match @font-face by family name and silently drops the rule.
    opts.name_IDs = [1, 2, 3, 4, 5, 6]
    opts.name_languages = [0x0409]
    opts.glyph_names = True
    opts.legacy_kern = False
    opts.notdef_outline = False
    opts.notdef_glyph = True
    opts.recalc_bounds = True
    opts.recalc_timestamp = False
    opts.canonical_order = True
    opts.drop_tables = ["DSIG", "STAT", "fvar", "MVAR", "HVAR", "VVAR", "avar"]
    opts.hinting = False
    opts.desubroutinize = True
    # Ensure ligature chains stay intact by both retaining the source ASCII
    # codepoints (text=) AND the target ligature glyphs (glyphs=). Without
    # the explicit glyphs= the Subsetter drops the PUA glyphs that the
    # liga lookups substitute INTO, breaking icon rendering.
    subsetter = Subsetter(options=opts)
    subsetter.populate(
        text=text,
        glyphs=keep_glyphs,
        unicodes=keep_codepoints,
    )
    subsetter.subset(font)

    out_path = ROOT / "prop" / "fonts" / "MaterialSymbolsOutlined-subset.woff2"
    font.flavor = "woff2"
    font.save(str(out_path))

    out_size = out_path.stat().st_size
    src_size = src.stat().st_size
    print(
        f"Wrote {out_path.relative_to(ROOT)}: "
        f"{out_size / 1024:.1f} KB "
        f"(source {src_size / 1024:.1f} KB → {100 * out_size / src_size:.1f}% kept)"
    )

    total_pre = sum(p.stat().st_size for p in (ROOT / "prop" / "fonts").glob("*.ttf")
                    if p.name.startswith("kJF1Bv"))
    print(
        f"All Material Symbols TTFs total {total_pre / 1024 / 1024:.2f} MB "
        f"→ subset {out_size / 1024:.1f} KB "
        f"(reduction {100 - 100 * out_size / total_pre:.2f}%)"
    )


if __name__ == "__main__":
    main()
