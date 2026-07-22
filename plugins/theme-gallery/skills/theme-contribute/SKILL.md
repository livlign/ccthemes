---
name: theme-contribute
description: Contribute a custom Claude Code theme to the ccthemes gallery — validate the theme file, then open a pull request adding it to the catalog. Use when the user wants to share or submit their theme.
when_to_use: Use when the user wants to contribute, submit, share, or publish one of their custom themes to the ccthemes gallery.
disable-model-invocation: false
user-invocable: true
allowed-tools: Read, Write, Edit, Bash
---

# Contribute a theme to the gallery

Take one of the user's custom themes and open a PR adding it to the `ccthemes`
catalog at `github.com/livlign/ccthemes` (themes live in
`plugins/theme-gallery/themes/`).

## Steps

1. **Pick the theme.** If the user didn't name one, list `~/.claude/themes/*.json`
   and ask which to contribute. Read the file.

2. **Validate it** before proposing a PR — fail loudly, don't silently "fix":
   - `name` (string) and `base` present; `base` is one of `dark`, `light`,
     `dark-daltonized`, `light-daltonized`, `dark-ansi`, `light-ansi`.
   - `overrides` is an object; every value is a valid color
     (`#rrggbb` / `#rgb` / `rgb(r,g,b)` / `ansi256(n)` / `ansi:<name>`).
   - Warn on unknown token names (Claude Code ignores them, but they usually mean a typo).
   - Sanity-check legibility: on a `dark` base, `diffAdded`/`diffRemoved` should be
     dark tints (not near-white); on `light`, pale tints. Flag anything that looks
     like a vivid foreground color used as a diff background.
   - Choose a kebab-case slug for the filename; make sure it doesn't collide with an
     existing file in the catalog.

3. **Open the PR** with `gh`:
   - Fork/clone `livlign/ccthemes` if the user doesn't have it (respect existing checkout).
   - Add the file at `plugins/theme-gallery/themes/<slug>.json`.
   - Branch `add-theme/<slug>`, commit `feat: add <name> theme`, push, and
     `gh pr create` with a body that names the theme, its base, and a one-line
     description of the look. Link the PR back to the user.

4. **Never** commit secrets or the user's unrelated settings — only the single theme JSON.
