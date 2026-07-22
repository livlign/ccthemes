# ccthemes

A curated gallery of **custom color themes for [Claude Code](https://claude.com/claude-code)** — 48 hand-tuned dark and light themes that drop straight into your `/theme` picker, plus a builder for your own and a one-command way to contribute it back.

```
/plugin marketplace add livlign/ccthemes
/plugin install theme-gallery@ccthemes
```

Then open `/theme` and pick one. It recolors the whole interface — diffs, the accent, status, prompt — and hot-reloads live.

> Requires Claude Code **v2.1.118+** (custom theme support).

## The gallery

![The 48 themes in ccthemes, each shown as a palette card with its accent, status colors, and diff bars](.github/gallery.png)

## What you get

| | |
|---|---|
| **48 themes in your picker** | Dracula, Nord, Gruvbox, Tokyo Night, Everforest, Catppuccin, Solarized, Synthwave, Amber CRT, Porcelain, and more — dark and light. Shipped by the plugin, so they appear in `/theme` alongside the built-ins. |
| **`/theme-gallery:theme-custom`** | Build your own: pick a base and accent, and it writes + activates a valid theme file for you. |
| **`/theme-gallery:theme-contribute`** | Validate one of your themes and open a PR to add it to this gallery. |

Every theme sets the tokens that actually change how Claude Code looks: the `claude`
accent (spinner, assistant label), `diffAdded`/`diffRemoved` line backgrounds tuned
to each theme's own hue, `success`/`error`/`warning`, and the mode/prompt borders.

## Themes as files

Each theme is a small JSON file in [`plugins/theme-gallery/themes/`](plugins/theme-gallery/themes/) —
`{ "name", "base", "overrides" }`, exactly the format Claude Code reads from
`~/.claude/themes/`. Shipped themes appear as `custom:theme-gallery:<slug>` and are
read-only; press `Ctrl+E` on one in `/theme` to fork it into your own editable copy.

## Where the palettes come from

The color systems are derived from [**PoshPalette**](https://github.com/livlign/posh-palette),
a terminal theming tool with 48 hand-built palettes — so a theme here matches its
PoshPalette namesake, and your terminal and your Claude Code session can share one look.

## Contributing

New themes are welcome — a contribution is a single JSON file. See
[CONTRIBUTING.md](CONTRIBUTING.md), or just run the `theme-contribute` skill and let
it open the PR for you.

## License

MIT — see [LICENSE](LICENSE).
