#!/usr/bin/env python3
"""
Generate a VS Code / Antigravity `keybindings.json` delta overlay from a
PhpStorm ("Windows" keymap) export.

Pipeline
--------
1. Parse `source/Windows.xml` (full resolved keymap exported from PhpStorm).
2. Translate every IntelliJ action id -> VS Code command via
   `vendor/ActionIdCommandMapping.json` (shipped by the
   `k--kato.intellij-idea-keybindings` extension) plus `overrides.jsonc`
   -> `manualActionCommand`.
3. Translate every AWT keystroke token -> VS Code key token via
   `vendor/KeystrokeKeyMapping.json` plus a few hard-coded rules.
4. Drop anything already provided identically by the curated base
   (`overrides.jsonc` -> `entries`) or by the extension's shipped bindings
   (`vendor/default-Windows-VSCode.json`).
5. Emit `keybindings.generated.json`:
      <header>
      [ ...generated entries...,
        ...overrides.jsonc "entries" verbatim (LAST so they win)... ]
6. Emit `report.md`: what mapped, what the base already covered, what has no
   VS Code equivalent, and the mouse shortcuts (not portable).

Design note
-----------
The PhpStorm export is a *Windows* keymap: it uses the physical Ctrl key.
On macOS the k--kato extension rebinds IntelliJ actions to Cmd. This user
deliberately wants Windows/PC muscle memory (see the Karabiner + "Default
for XWin" setup), so generated entries keep `ctrl` literally and, being
user keybindings loaded after the extension, win over the extension's
Cmd bindings for every action we map. Actions we cannot map fall through
to the extension (Cmd-based) - listed in report.md so the mapping table
in overrides.jsonc can be extended over time.
"""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE_XML = ROOT / "source" / "Windows.xml"
VENDOR = ROOT / "vendor"
OVERRIDES_PATH = ROOT / "overrides.jsonc"
OUT_KEYBINDINGS = ROOT / "keybindings.generated.json"
OUT_REPORT = ROOT / "report.md"

# AWT key tokens that KeystrokeKeyMapping.json does not cover.
EXTRA_KEY_MAP = {
    "multiply": "numpad_multiply",
    "add": "numpad_add",
    "subtract": "numpad_subtract",
    "divide": "numpad_divide",
    "decimal": "numpad_decimal",
    "separator": "numpad_separator",
    **{f"numpad{n}": f"numpad{n}" for n in range(10)},
    "context_menu": None,   # no reliable VS Code equivalent
    "printscreen": None,
    "begin": None,
}

MODIFIERS = {"ctrl", "shift", "alt", "meta"}
MOD_TRANSLATE = {"meta": "cmd"}  # ctrl/shift/alt pass through unchanged


def strip_jsonc(text: str) -> str:
    """Remove // line comments and /* */ block comments, keeping string literals intact."""
    out = []
    i, n = 0, len(text)
    in_str = False
    while i < n:
        ch = text[i]
        if in_str:
            out.append(ch)
            if ch == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if ch == '"':
                in_str = False
            i += 1
            continue
        if ch == '"':
            in_str = True
            out.append(ch)
            i += 1
            continue
        if ch == "/" and i + 1 < n and text[i + 1] == "/":
            while i < n and text[i] != "\n":
                i += 1
            continue
        if ch == "/" and i + 1 < n and text[i + 1] == "*":
            i += 2
            while i + 1 < n and not (text[i] == "*" and text[i + 1] == "/"):
                i += 1
            i += 2
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def load_jsonc(path: Path):
    return json.loads(strip_jsonc(path.read_text(encoding="utf-8")))


def load_key_map() -> dict[str, str | None]:
    raw = json.loads((VENDOR / "KeystrokeKeyMapping.json").read_text(encoding="utf-8"))
    m: dict[str, str | None] = {}
    for row in raw:
        m[row["intellij"].strip().lower()] = row["vscode"]
    m.update(EXTRA_KEY_MAP)
    return m


def load_action_map(manual: dict[str, str]) -> dict[str, list[str]]:
    raw = json.loads((VENDOR / "ActionIdCommandMapping.json").read_text(encoding="utf-8"))
    m: dict[str, list[str]] = {}
    for row in raw:
        m.setdefault(row["intellij"], [])
        if row["vscode"] not in m[row["intellij"]]:
            m[row["intellij"]].append(row["vscode"])
    for action, command in manual.items():
        m[action] = [command]
    return m


def translate_token(tok: str, key_map: dict[str, str | None]) -> str | None:
    """Translate one AWT keystroke element (e.g. 'shift ctrl RIGHT') to a VS Code chord part."""
    parts = tok.strip().split()
    if not parts:
        return None
    mods: list[str] = []
    key: str | None = None
    for p in parts:
        low = p.lower()
        if low in MODIFIERS:
            mods.append(MOD_TRANSLATE.get(low, low))
            continue
        # the key itself
        if len(low) == 1 and (low.isalnum()):
            key = low
        elif low in key_map:
            key = key_map[low]
        elif re.fullmatch(r"f\d{1,2}", low):
            key = low
        else:
            # last resort: hand it over lowercased and let VS Code validate
            key = low
        if key is None:
            return None
    if key is None:
        return None
    # stable modifier order matches VS Code's normaliser: ctrl shift alt cmd
    order = {"ctrl": 0, "shift": 1, "alt": 2, "cmd": 3}
    mods_sorted = sorted(set(mods), key=lambda m: order.get(m, 9))
    return "+".join(mods_sorted + [key])


def translate_keystroke(first: str, second: str | None, key_map) -> str | None:
    a = translate_token(first, key_map)
    if a is None:
        return None
    if second:
        b = translate_token(second, key_map)
        if b is None:
            return None
        return f"{a} {b}"
    return a


def parse_source(path: Path):
    """Return list of (action_id, [ (first, second|None) ... ], [mouse strings])."""
    tree = ET.parse(path)
    root = tree.getroot()
    actions = []
    for action in root.findall("action"):
        aid = action.get("id")
        keystrokes = []
        mouse = []
        for ks in action.findall("keyboard-shortcut"):
            keystrokes.append((ks.get("first-keystroke"), ks.get("second-keystroke")))
        for ms in action.findall("mouse-shortcut"):
            mouse.append(ms.get("keystroke"))
        actions.append((aid, keystrokes, mouse))
    return actions


def main() -> int:
    if not SOURCE_XML.exists():
        print(f"missing {SOURCE_XML}", file=sys.stderr)
        return 1

    overrides = load_jsonc(OVERRIDES_PATH)
    manual_action_command = overrides.get("manualActionCommand", {})
    base_entries = overrides.get("entries", [])
    drop_actions = set(overrides.get("dropActions", []))

    key_map = load_key_map()
    action_map = load_action_map(manual_action_command)

    ext_shipped = json.loads(
        (VENDOR / "default-Windows-VSCode.json").read_text(encoding="utf-8")
    )
    covered = {(e.get("command"), e.get("key")) for e in ext_shipped}
    covered |= {(e.get("command"), e.get("key")) for e in base_entries}

    source = parse_source(SOURCE_XML)

    generated: list[dict] = []
    emitted_pairs: set[tuple] = set()
    rep_mapped: list[str] = []
    rep_covered: list[str] = []
    rep_unmapped: list[str] = []
    rep_badkey: list[str] = []
    rep_mouse: list[str] = []

    for aid, keystrokes, mouse in source:
        for m in mouse:
            rep_mouse.append(f"{aid}  <-  mouse: {m}")

        commands = action_map.get(aid)
        if aid in drop_actions:
            rep_covered.append(f"{aid}  (explicitly dropped in overrides.jsonc)")
            continue
        if not commands:
            if keystrokes:
                rep_unmapped.append(
                    f"{aid}  <-  " + ", ".join(k[0] + (f" , {k[1]}" if k[1] else "") for k in keystrokes)
                )
            continue

        for first, second in keystrokes:
            vkey = translate_keystroke(first, second, key_map)
            if vkey is None:
                rep_badkey.append(f"{aid}  <-  {first}" + (f" , {second}" if second else ""))
                continue
            for command in commands:
                pair = (command, vkey)
                if pair in covered:
                    rep_covered.append(f"{command}  <-  {vkey}  ({aid})")
                    continue
                if pair in emitted_pairs:
                    continue
                emitted_pairs.add(pair)
                generated.append({"key": vkey, "command": command})
                rep_mapped.append(f"{command}  <-  {vkey}  ({aid})")

    generated.sort(key=lambda e: (e["command"], e["key"]))

    header = (
        "// ============================================================================\n"
        "// GENERATED by phpstorm-keymap-port/generate.py  -  DO NOT EDIT BY HAND.\n"
        "// Source of truth: source/Windows.xml (PhpStorm 'Windows' keymap export).\n"
        "// Curated base + terminal-signal guards live in overrides.jsonc and are\n"
        "// appended verbatim at the BOTTOM of this array (VS Code: last entry wins).\n"
        "// Re-generate:  python3 generate.py      Deploy:  ./install.sh\n"
        "// ============================================================================\n"
    )

    body_generated = ",\n".join("  " + json.dumps(e) for e in generated)
    body_overrides = ",\n".join("  " + json.dumps(e) for e in base_entries)
    parts = [p for p in (body_generated, body_overrides) if p]
    OUT_KEYBINDINGS.write_text(
        header
        + "[\n"
        + "\n  // ---- generated from source/Windows.xml ----\n"
        + (body_generated + ",\n" if body_generated else "")
        + "\n  // ---- overrides.jsonc (curated base, wins on conflict) ----\n"
        + body_overrides
        + "\n]\n",
        encoding="utf-8",
    )

    def block(title, rows):
        rows = sorted(set(rows))
        return f"## {title}  ({len(rows)})\n\n" + (
            "```\n" + "\n".join(rows) + "\n```\n" if rows else "_none_\n"
        )

    OUT_REPORT.write_text(
        "# PhpStorm -> VS Code keymap port report\n\n"
        f"- source actions parsed: **{len(source)}**\n"
        f"- generated entries: **{len(generated)}**\n"
        f"- curated base entries (overrides.jsonc): **{len(base_entries)}**\n"
        f"- total in keybindings.generated.json: **{len(generated) + len(base_entries)}**\n\n"
        + block("Mapped -> emitted", rep_mapped)
        + "\n"
        + block("Already covered by base / extension (skipped)", rep_covered)
        + "\n"
        + block("No VS Code command mapping (fell through to extension / lost)", rep_unmapped)
        + "\n"
        + block("Key could not be translated", rep_badkey)
        + "\n"
        + block("Mouse shortcuts (not portable to keybindings.json)", rep_mouse),
        encoding="utf-8",
    )

    print(f"generated {len(generated)} entries + {len(base_entries)} base -> {OUT_KEYBINDINGS.name}")
    print(f"report -> {OUT_REPORT.name}  "
          f"(unmapped={len(set(rep_unmapped))}, covered={len(set(rep_covered))}, "
          f"badkey={len(set(rep_badkey))}, mouse={len(set(rep_mouse))})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
