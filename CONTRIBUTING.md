# Contributing a theme

A theme is one JSON file in `plugins/theme-gallery/themes/<slug>.json`. That's the
whole contribution.

## Format

```json
{
  "name": "Display Name",
  "base": "dark",
  "overrides": {
    "claude": "#bd93f9",
    "text": "#f8f8f2",
    "success": "#50fa7b",
    "error": "#ff5555",
    "warning": "#f1fa8c",
    "diffAdded": "#305444",
    "diffRemoved": "#53333c"
  }
}
```

- **`name`**: shown in the `/theme` picker.
- **`base`**: one of `dark`, `light`, `dark-daltonized`, `light-daltonized`,
  `dark-ansi`, `light-ansi`. Tokens you don't override inherit from it.
- **`overrides`**: token to color. Colors accept `#rrggbb`, `#rgb`, `rgb(r,g,b)`,
  `ansi256(n)`, or `ansi:<name>`. The full token list is in the
  [Claude Code docs](https://code.claude.com/docs/en/terminal-config#color-token-reference).

## Guidelines

- **Diff backgrounds are backgrounds.** `diffAdded`/`diffRemoved` should be *dark,
  desaturated tints* on a dark base and *pale tints* on a light base, never a vivid
  foreground green/red, which makes the code on top unreadable. Word-level
  (`diffAddedWord`/`diffRemovedWord`) sits a shade stronger; dimmed variants are fainter.
- **Set `claude`** (the accent). It is the most recognizable part of a theme.
- **Keep it legible:** `text` on the base background, and every status color, should
  pass a reasonable contrast check.
- **Filename** is a kebab-case slug and must be unique.

## Submitting

Open a PR adding your file to `plugins/theme-gallery/themes/`. Title it
`feat: add <name> theme` and include a one-line description of the look (and a
screenshot if you have one).

Then regenerate the gallery image so it includes your theme:

```
python3 scripts/gallery.py
```

Commit the updated `.github/gallery.png` and `.github/gallery.manifest.json` alongside
your theme. CI validates the JSON shape and color values, and fails if the gallery is
out of date (`python3 scripts/gallery.py --check`).

Not sure? Run the `theme-contribute` skill inside Claude Code. It validates your
theme and opens the PR for you.
