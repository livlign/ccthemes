#!/usr/bin/env python3
"""Render a palette-card gallery PNG of every theme in the plugin.

Reads plugins/theme-gallery/themes/*.json and writes .github/gallery.png —
one card per theme, grouped dark-then-light, showing the name and the tokens
that define the theme's look (accent, status, diff bars, mode borders).
"""
import json
import pathlib

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
THEMES = sorted((ROOT / "plugins/theme-gallery/themes").glob("*.json"))
OUT = ROOT / ".github/gallery.png"

# Layout (2x scale for crisp rendering)
S = 2
COLS = 4
CARD_W, CARD_H = 300, 132
GAP = 16
PAD = 28
HEADER_H = 96
SWATCH = 20
SWATCH_GAP = 8


def hx(c):
    c = c.lstrip("#")
    return tuple(int(c[i : i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def load_font(size, bold=False):
    names = (
        ["Menlo.ttc", "DejaVuSansMono-Bold.ttf", "Arial Bold.ttf"]
        if bold
        else ["Menlo.ttc", "DejaVuSansMono.ttf", "Arial.ttf"]
    )
    paths = [
        "/System/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    ]
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()


def rrect(d, box, r, **kw):
    d.rounded_rectangle(box, radius=r, **kw)


themes = []
for f in THEMES:
    t = json.loads(f.read_text())
    themes.append(t)

# dark first, then light; alpha by name within each group
themes.sort(key=lambda t: (t.get("base", "dark") != "dark", t["name"].lower()))

rows = (len(themes) + COLS - 1) // COLS
W = PAD * 2 + COLS * CARD_W + (COLS - 1) * GAP
H = PAD + HEADER_H + rows * CARD_H + (rows - 1) * GAP + PAD

img = Image.new("RGB", (W * S, H * S), hx("#0b0d12"))
d = ImageDraw.Draw(img)

f_title = load_font(30 * S, bold=True)
f_sub = load_font(15 * S)
f_name = load_font(16 * S, bold=True)
f_base = load_font(11 * S)

# Header
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
    # nudge card bg toward the base so light themes read light
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

    # accent bar
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

    # swatch row: the tokens that carry theme identity
    keys = [
        "success",
        "error",
        "warning",
        "planMode",
        "bashBorder",
        "suggestion",
    ]
    sx, sy = ix, y + CARD_H - 58
    for k in keys:
        c = ov.get(k)
        if not c:
            continue
        rrect(
            d,
            [sx * S, sy * S, (sx + SWATCH) * S, (sy + SWATCH) * S],
            5 * S,
            fill=hx(c),
        )
        sx += SWATCH + SWATCH_GAP

    # diff bars (added / removed), mimicking a diff hunk
    dy = y + CARD_H - 26
    for j, (add, rem) in enumerate([("diffAdded", "diffRemoved")]):
        rrect(
            d,
            [ix * S, dy * S, (ix + 118) * S, (dy + 14) * S],
            4 * S,
            fill=hx(ov.get("diffAdded", "#233b2b")),
        )
        rrect(
            d,
            [(ix + 126) * S, dy * S, (ix + 244) * S, (dy + 14) * S],
            4 * S,
            fill=hx(ov.get("diffRemoved", "#3b2326")),
        )
        d.text(((ix + 8) * S, (dy + 1) * S), "+ added", font=f_base, fill=hx(ov.get("diffAddedWord", ov["success"])))
        d.text(((ix + 134) * S, (dy + 1) * S), "- removed", font=f_base, fill=hx(ov.get("diffRemovedWord", ov["error"])))

OUT.parent.mkdir(exist_ok=True)
img.save(OUT)
print(f"wrote {OUT.relative_to(ROOT)}  ({W}x{H} @ {S}x = {W*S}x{H*S}px, {len(themes)} themes)")
