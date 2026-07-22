#!/usr/bin/env python3
"""Render a palette-card gallery PNG of every theme in the plugin.

Reads plugins/theme-gallery/themes/*.json and writes .github/gallery.png —
one card per theme, grouped dark-then-light, showing the name and the tokens
that define the theme's look (accent, status, diff bars, mode borders).

Also writes .github/gallery.manifest.json: the exact theme data the image is
built from. CI runs `gallery.py --check` to fail if a theme was added, removed,
or recolored without regenerating the gallery. The check compares the manifest
(not the PNG) so it's independent of fonts / Pillow versions across machines.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
THEME_DIR = ROOT / "plugins/theme-gallery/themes"
OUT = ROOT / ".github/gallery.png"
MANIFEST = ROOT / ".github/gallery.manifest.json"

# The only tokens the card actually renders — the manifest tracks these so a
# change to any of them (or the theme set) counts as drift, while edits to
# tokens the image never shows do not cause false positives.
CARD_TOKENS = [
    "claude", "text", "inactive", "promptBorder", "userMessageBackground",
    "success", "error", "warning", "planMode", "bashBorder", "suggestion",
    "diffAdded", "diffRemoved", "diffAddedWord", "diffRemovedWord",
]

# Layout (2x scale for crisp rendering)
S = 2
COLS = 4
CARD_W, CARD_H = 300, 132
GAP = 16
PAD = 28
HEADER_H = 96
SWATCH = 20
SWATCH_GAP = 8


def load_themes():
    """Return themes sorted dark-then-light, alpha by name within each group."""
    themes = [json.loads(f.read_text()) for f in sorted(THEME_DIR.glob("*.json"))]
    themes.sort(key=lambda t: (t.get("base", "dark") != "dark", t["name"].lower()))
    return themes


def build_manifest(themes):
    """The card-relevant slice of every theme, in render order."""
    return [
        {
            "name": t["name"],
            "base": t.get("base", "dark"),
            "tokens": {k: t["overrides"].get(k) for k in CARD_TOKENS},
        }
        for t in themes
    ]


def hx(c):
    c = c.lstrip("#")
    return tuple(int(c[i : i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def load_font(size, bold=False):
    from PIL import ImageFont

    paths = [
        "/System/Library/Fonts/Menlo.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()


def render(themes):
    from PIL import Image, ImageDraw

    def rrect(d, box, r, **kw):
        d.rounded_rectangle(box, radius=r, **kw)

    rows = (len(themes) + COLS - 1) // COLS
    W = PAD * 2 + COLS * CARD_W + (COLS - 1) * GAP
    H = PAD + HEADER_H + rows * CARD_H + (rows - 1) * GAP + PAD

    img = Image.new("RGB", (W * S, H * S), hx("#0b0d12"))
    d = ImageDraw.Draw(img)

    f_title = load_font(30 * S, bold=True)
    f_sub = load_font(15 * S)
    f_name = load_font(16 * S, bold=True)
    f_base = load_font(11 * S)

    d.text((PAD * S, PAD * S), "ccthemes", font=f_title, fill=hx("#E6EDF3"))
    d.text(
        (PAD * S, (PAD + 44) * S),
        f"{len(themes)} custom color themes for Claude Code  ·  /theme-gallery",
        font=f_sub,
        fill=hx("#8B949E"),
    )

    for i, t in enumerate(themes):
        ov = t["overrides"]
        is_dark = t.get("base", "dark") == "dark"
        col, row = i % COLS, i // COLS
        x = PAD + col * (CARD_W + GAP)
        y = PAD + HEADER_H + row * (CARD_H + GAP)

        bg = hx(ov.get("userMessageBackground", "#12141a" if is_dark else "#f4f4f6"))
        bg = mix(bg, (255, 255, 255) if not is_dark else (0, 0, 0), 0.18)
        txt = hx(ov.get("text", "#E6EDF3" if is_dark else "#1b1f24"))
        border = hx(ov.get("promptBorder", ov.get("inactive", "#30363d")))

        box = [x * S, y * S, (x + CARD_W) * S, (y + CARD_H) * S]
        rrect(d, box, 12 * S, fill=bg, outline=border, width=1 * S)

        ix, iy = x + 18, y + 16
        d.text((ix * S, iy * S), t["name"], font=f_name, fill=txt)
        d.text(
            (ix * S, (iy + 24) * S),
            ("● DARK" if is_dark else "○ LIGHT"),
            font=f_base,
            fill=hx(ov.get("inactive", "#6e7681")),
        )

        d.text(
            ((x + CARD_W - 78) * S, iy * S),
            "claude",
            font=f_base,
            fill=hx(ov.get("inactive", "#6e7681")),
        )
        rrect(
            d,
            [(x + CARD_W - 78) * S, (iy + 16) * S, (x + CARD_W - 18) * S, (iy + 26) * S],
            5 * S,
            fill=hx(ov["claude"]),
        )

        keys = ["success", "error", "warning", "planMode", "bashBorder", "suggestion"]
        sx, sy = ix, y + CARD_H - 58
        for k in keys:
            c = ov.get(k)
            if not c:
                continue
            rrect(d, [sx * S, sy * S, (sx + SWATCH) * S, (sy + SWATCH) * S], 5 * S, fill=hx(c))
            sx += SWATCH + SWATCH_GAP

        dy = y + CARD_H - 26
        rrect(d, [ix * S, dy * S, (ix + 118) * S, (dy + 14) * S], 4 * S,
              fill=hx(ov.get("diffAdded", "#233b2b")))
        rrect(d, [(ix + 126) * S, dy * S, (ix + 244) * S, (dy + 14) * S], 4 * S,
              fill=hx(ov.get("diffRemoved", "#3b2326")))
        d.text(((ix + 8) * S, (dy + 1) * S), "+ added", font=f_base,
               fill=hx(ov.get("diffAddedWord", ov["success"])))
        d.text(((ix + 134) * S, (dy + 1) * S), "- removed", font=f_base,
               fill=hx(ov.get("diffRemovedWord", ov["error"])))

    OUT.parent.mkdir(exist_ok=True)
    img.save(OUT)
    print(f"wrote {OUT.relative_to(ROOT)}  ({W}x{H} @ {S}x = {W*S}x{H*S}px, {len(themes)} themes)")


def check(themes):
    """Fail if the committed manifest doesn't match the current themes."""
    current = build_manifest(themes)
    if not MANIFEST.exists():
        print("ERROR: .github/gallery.manifest.json is missing — run scripts/gallery.py")
        return 1
    committed = json.loads(MANIFEST.read_text())
    if committed == current:
        print(f"gallery is up to date ({len(themes)} themes)")
        return 0
    cur_names = {t["name"] for t in current}
    com_names = {t["name"] for t in committed}
    for n in sorted(cur_names - com_names):
        print(f"  added, not in gallery:   {n}")
    for n in sorted(com_names - cur_names):
        print(f"  removed, still in gallery: {n}")
    for c in current:
        for o in committed:
            if c["name"] == o["name"] and c != o:
                print(f"  recolored, gallery stale:  {c['name']}")
    print("\nERROR: gallery is out of date. Run `python3 scripts/gallery.py` and commit "
          ".github/gallery.png + .github/gallery.manifest.json")
    return 1


def main():
    themes = load_themes()
    if "--check" in sys.argv[1:]:
        sys.exit(check(themes))
    render(themes)
    MANIFEST.write_text(json.dumps(build_manifest(themes), indent=2) + "\n")
    print(f"wrote {MANIFEST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
