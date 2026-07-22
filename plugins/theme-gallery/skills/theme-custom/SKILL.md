---
name: theme-custom
description: Build a custom Claude Code color theme interactively — pick a base and accent, generate a valid theme file, write it to ~/.claude/themes/, and activate it live. Use when the user wants to create, design, or tweak their own Claude Code theme.
when_to_use: Use when the user asks to build, create, design, customize, or tweak a Claude Code theme, or wants colors that aren't in the shipped gallery.
disable-model-invocation: false
user-invocable: true
allowed-tools: Read, Write, Edit, Bash
---

# Build a custom Claude Code theme

Guide the user to a finished, activated custom theme. A theme is a JSON file at
`~/.claude/themes/<slug>.json` with three fields: `name`, `base`, and `overrides`.
Claude Code hot-reloads the folder, so a written file applies without restart
(if `~/.claude/themes/` did not exist before this session, the user restarts once).

## Steps

1. **Establish the direction.** Ask two quick questions if the user hasn't already said:
   - Light or dark? → sets `base` (`dark` is the default; `light`, `dark-daltonized`,
     `light-daltonized`, `dark-ansi`, `light-ansi` are the other options).
   - A hero/accent color or a vibe (e.g. "warm terracotta", "cool neon", "muted forest").
   Offer to start from an existing shipped theme as a base to tweak — read one from the
   plugin's `themes/` directory and adjust it.

2. **Generate the overrides.** Only set tokens you have a deliberate reason to change;
   everything else inherits from `base`. Colors accept `#rrggbb`, `#rgb`, `rgb(r,g,b)`,
   `ansi256(n)`, or `ansi:<name>`. The tokens that matter most, in priority order:

   | Token | Controls |
   |---|---|
   | `claude` | Primary accent — spinner, assistant label. Set `claudeShimmer` to a lighter tint of it. |
   | `text` | Default foreground text |
   | `inactive` / `subtle` | Hints, timestamps; faint borders |
   | `success` / `error` / `warning` | Pass / fail / caution |
   | `diffAdded` / `diffRemoved` | **Backgrounds** of added/removed lines — use dark, desaturated tints on dark bases and pale tints on light bases, NOT vivid foreground green/red |
   | `diffAddedWord` / `diffRemovedWord` | Word-level highlight, a shade stronger than the line |
   | `diffAddedDimmed` / `diffRemovedDimmed` | Faint context tint near a change |
   | `planMode` / `autoAccept` / `bashBorder` / `promptBorder` | Mode accents and input borders |

   Rule of thumb for diff backgrounds: composite the theme's green/red over its
   background at low alpha (~18–22% on dark, ~16% on light). Never reuse a vivid
   terminal foreground green as a background — it destroys the text contrast.

3. **Write the file.** Slug = a kebab-case name. Write `~/.claude/themes/<slug>.json`:
   ```json
   { "name": "My Theme", "base": "dark", "overrides": { "claude": "#bd93f9", "...": "..." } }
   ```

4. **Activate it.** Patch the user's settings so it's the live theme. Read
   `~/.claude/settings.json` (create `{}` if absent), set `"theme": "custom:<slug>"`,
   and write it back — preserve every other key. Then tell the user it applies
   immediately (or after one restart if the themes folder was just created).

5. **Confirm.** Report the slug, the file path, and that it's now active. Offer to
   contribute it to the gallery (the `theme-contribute` skill).
