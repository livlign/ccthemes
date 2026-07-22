#!/usr/bin/env python3
"""Validate every theme JSON in plugins/theme-gallery/themes/.

Checks the shape Claude Code expects: name/base/overrides, a valid base,
color values in an accepted format, and known token names (unknown tokens
are ignored by Claude Code but almost always signal a typo). Exits non-zero
on any error so CI fails the PR.
"""
import json, os, re, sys

BASES = {"dark", "light", "dark-daltonized", "light-daltonized", "dark-ansi", "light-ansi"}

ANSI_NAMES = {
    "black", "red", "green", "yellow", "blue", "magenta", "cyan", "white",
    "blackBright", "redBright", "greenBright", "yellowBright", "blueBright",
    "magentaBright", "cyanBright", "whiteBright", "gray", "grey",
}

KNOWN = {
    "claude", "claudeShimmer", "text", "inverseText", "inactive", "inactiveShimmer",
    "subtle", "suggestion", "permission", "permissionShimmer", "remember",
    "success", "error", "warning", "warningShimmer", "merged",
    "promptBorder", "promptBorderShimmer", "planMode", "autoAccept", "bashBorder",
    "ide", "fastMode", "fastModeShimmer",
    "diffAdded", "diffRemoved", "diffAddedDimmed", "diffRemovedDimmed",
    "diffAddedWord", "diffRemovedWord",
    "userMessageBackground", "userMessageBackgroundHover", "bashMessageBackgroundColor",
    "memoryBackgroundColor", "selectionBg",
    "rate_limit_fill", "rate_limit_empty", "briefLabelYou", "briefLabelClaude",
}
KNOWN |= {f"{c}_FOR_SUBAGENTS_ONLY" for c in
         ("red", "blue", "green", "yellow", "purple", "orange", "pink", "cyan")}
KNOWN |= {f"rainbow_{c}" for c in ("red", "orange", "yellow", "green", "blue", "indigo", "violet")}
KNOWN |= {f"rainbow_{c}_shimmer" for c in ("red", "orange", "yellow", "green", "blue", "indigo", "violet")}

HEX = re.compile(r"^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
RGB = re.compile(r"^rgb\(\s*\d{1,3}\s*,\s*\d{1,3}\s*,\s*\d{1,3}\s*\)$")
ANSI256 = re.compile(r"^ansi256\(\s*\d{1,3}\s*\)$")


def valid_color(v):
    if not isinstance(v, str):
        return False
    if HEX.match(v) or RGB.match(v) or ANSI256.match(v):
        return True
    if v.startswith("ansi:"):
        return v[5:] in ANSI_NAMES
    return False


def check(path):
    errors, warnings = [], []
    try:
        data = json.load(open(path))
    except json.JSONDecodeError as e:
        return [f"invalid JSON: {e}"], []
    if not isinstance(data.get("name", ""), str) or not data.get("name"):
        errors.append("missing/invalid 'name'")
    base = data.get("base", "dark")
    if base not in BASES:
        errors.append(f"invalid 'base': {base!r}")
    ov = data.get("overrides", {})
    if not isinstance(ov, dict) or not ov:
        errors.append("'overrides' must be a non-empty object")
        ov = {}
    for tok, val in ov.items():
        if not valid_color(val):
            errors.append(f"{tok}: invalid color {val!r}")
        if tok not in KNOWN:
            warnings.append(f"unknown token {tok!r} (typo?)")
    return errors, warnings


def main():
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tdir = os.path.join(here, "plugins", "theme-gallery", "themes")
    files = sorted(f for f in os.listdir(tdir) if f.endswith(".json"))
    total_err = 0
    for f in files:
        errors, warnings = check(os.path.join(tdir, f))
        for w in warnings:
            print(f"  warn  {f}: {w}")
        for e in errors:
            print(f"  ERROR {f}: {e}")
        total_err += len(errors)
    print(f"\n{len(files)} themes checked, {total_err} error(s)")
    sys.exit(1 if total_err else 0)


if __name__ == "__main__":
    main()
