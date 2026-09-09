#!/usr/bin/env python3
"""
Generate a VS Code / Antigravity `keybindings.json` delta overlay from an
IntelliJ IDE keymap export (any product: PhpStorm, IntelliJ IDEA, WebStorm, ...).

Pipeline
--------
1. Parse the IntelliJ keymap export in `source/` (the single `*.xml` whose root
   is `<keymap>`; file name does not matter - see resolve_source_xml()).
2. Translate every IntelliJ action id -> VS Code command via
   `ActionIdCommandMapping.json` from the installed
   `k--kato.intellij-idea-keybindings` extension (see kkato.py; falls back to
   `vendor/kkato/`) plus `overrides.jsonc` -> `manualActionCommand`.
3. Translate every AWT keystroke token -> VS Code key token via
   `KeystrokeKeyMapping.json` (same source) plus a few hard-coded rules.
4. Drop anything already provided identically by the curated base
   (`overrides.jsonc` -> `entries`) or by the extension's shipped bindings
   (`default/<OS>/VSCode.json`, matched to this platform).
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

import kkato

ROOT = Path(__file__).resolve().parent
SOURCE_DIR = ROOT / "source"
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
    "unknown": None,        # the external exporter emits this for keys it cannot serialize
}

# Characters that IntelliJ stores as an extended key code (#100XXXX, XXXX = the
# Unicode codepoint of the character the key produces on the author's layout).
# Mapped to a VS Code *scan-code* token ("[Name]") so the binding follows the
# physical key regardless of the active keyboard layout. Extend as needed for
# other layouts (the resolver prints every #100XXXX token it sees).
EXTENDED_CHAR_KEY = {
    "§": "[Backquote]",     # §/° or `/~  - key left of "1" (Swiss/German/Nordic ISO)
    "°": "[Backquote]",
    "²": "[Backquote]",     # ²  - same key on French AZERTY
    "<": "[IntlBackslash]", # </>  - extra ISO key left of "Z"
    ">": "[IntlBackslash]",
    "|": "[IntlBackslash]",
    "´": "[Equal]",         # ´/` dead key (Swiss/German)
    "¨": "[BracketRight]",  # ¨/! dead key (Swiss)
    "+": "[BracketRight]",  # +/*  - German ISO
    "#": "[Backslash]",     # #/'  - German ISO
    "ä": "[Quote]", "ö": "[Semicolon]", "ü": "[BracketLeft]",  # German ISO letters
    "é": "[Digit2]", "è": "[Digit7]", "à": "[Digit0]",          # Swiss French / AZERTY
}

MODIFIERS = {"ctrl", "control", "shift", "alt", "meta"}
MOD_TRANSLATE = {"meta": "cmd", "control": "ctrl"}  # ctrl/shift/alt pass through unchanged

# Chords a shell / the integrated terminal needs for itself; generated editor
# bindings on these get a `!terminalFocus` guard so they only apply in editors.
_TERMINAL_KEY_RE = re.compile(r"^(?:ctrl|alt)\+[a-z]$")   # readline control / meta chars
_TERMINAL_KEYS = frozenset((
    "ctrl+left", "ctrl+right", "ctrl+shift+left", "ctrl+shift+right",
    "alt+left", "alt+right", "alt+shift+left", "alt+shift+right",
    "ctrl+backspace", "ctrl+delete", "alt+backspace", "alt+delete",
    "ctrl+home", "ctrl+end", "shift+pageup", "shift+pagedown",
    "ctrl+insert", "shift+insert", "shift+delete",          # X11-style clipboard
))


def needs_terminal_guard(key: str) -> bool:
    return bool(_TERMINAL_KEY_RE.match(key)) or key in _TERMINAL_KEYS


def _when_terms(expr: str) -> set[str]:
    return {t.strip() for t in (expr or "").split("&&") if t.strip()}


def _when_disjoint(a: str, b: str) -> bool:
    """True if two `when` clauses can never both be active (one needs `X`, the
    other `!X`) - e.g. `terminalFocus` vs `!terminalFocus`."""
    ta, tb = _when_terms(a), _when_terms(b)
    return (any(t.startswith("!") and t[1:] in tb for t in ta)
            or any(t.startswith("!") and t[1:] in ta for t in tb))


def resolve_conflicts_by_keymap_order(generated: list[dict]):
    """Two generated bindings on the same key with overlapping `when`: the one
    from the *earlier keymap action* wins - the IntelliJ keymap's own order is
    authoritative - and the later one is dropped.

    `generated` entries must carry `_src` (the source-action index). Returns
    (kept, dropped) with dropped a list of (key, winner_cmd, loser_cmd).
    """
    kept: list[dict] = []
    dropped: list[tuple[str, str, str]] = []
    taken: dict[str, list[tuple[str, str]]] = {}   # key -> [(when, command)]
    for e in sorted(generated, key=lambda x: x["_src"]):
        cmd, key, when = e["command"], e["key"], e.get("when", "")
        if cmd.startswith("-"):
            kept.append(e)
            continue
        clash = next((c for w, c in taken.get(key, [])
                      if c != cmd and not _when_disjoint(w, when)), None)
        if clash is not None:
            dropped.append((key, clash, cmd))
            continue
        taken.setdefault(key, []).append((when, cmd))
        kept.append(e)
    return kept, dropped


def find_key_conflicts(generated: list[dict], base_entries: list[dict]):
    """Keys bound to two or more *different* positive commands in the final file.

    The `(command, key)` dedup elsewhere only catches an identical binding; it
    says nothing when one key ends up driving two different commands. This does.

    Returns (hard, soft):
      hard - the clash is entirely inside the generated block; nobody has picked
             a winner. Gets a stderr warning.
      soft - overrides.jsonc also binds the key, so a human already chose. Only
             reported.
    `-command` removals and pairs with mutually exclusive `when` clauses are not
    counted as conflicts.
    """
    from collections import defaultdict
    slots: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for origin, entries in (("generated", generated), ("overrides.jsonc", base_entries)):
        for e in entries:
            cmd = e.get("command", "")
            if not cmd.startswith("-"):
                slots[e["key"]].append((cmd, e.get("when", ""), origin))

    hard, soft = [], []
    for key, binds in sorted(slots.items()):
        if len({c for c, _, _ in binds}) < 2:
            continue
        # keep only binds that actually overlap (non-disjoint `when`) another one
        live = [x for i, x in enumerate(binds)
                if any(not _when_disjoint(x[1], y[1])
                       for j, y in enumerate(binds) if j != i)]
        if len({c for c, _, _ in live}) < 2:
            continue
        bucket = soft if any(o == "overrides.jsonc" for _, _, o in live) else hard
        bucket.append((key, binds))
    return hard, soft


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


def load_key_map(res_dir: Path) -> dict[str, str | None]:
    raw = json.loads((res_dir / "KeystrokeKeyMapping.json").read_text(encoding="utf-8"))
    m: dict[str, str | None] = {}
    for row in raw:
        m[row["intellij"].strip().lower()] = row["vscode"]
    m.update(EXTRA_KEY_MAP)
    return m


def load_action_map(res_dir: Path, manual: dict[str, str]) -> dict[str, list[str]]:
    raw = json.loads((res_dir / "ActionIdCommandMapping.json").read_text(encoding="utf-8"))
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
        if p.startswith("#"):
            # IntelliJ extended key code: #100XXXX where XXXX is a Unicode codepoint.
            try:
                ch = chr(int(p[1:], 16) & 0xFFFF)
            except ValueError:
                return None
            key = EXTENDED_CHAR_KEY.get(ch) or key_map.get(ch) or (ch if ch.isprintable() and len(ch) == 1 and not ch.isspace() else None)
        elif len(low) == 1 and low.isalnum():
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


def resolve_source_xml() -> Path:
    """Locate the keymap to port from source/.

    A `*.resolved.xml` (produced by resolve_keymap.py from PhpStorm's own files)
    is preferred; otherwise any *.xml whose root element is <keymap> qualifies -
    the file name does not matter. Exactly one match -> use it. Several -> use
    the newest by mtime and say which. None -> hard error.
    """
    def keymaps(paths):
        out = []
        for p in sorted(paths):
            try:
                if ET.parse(p).getroot().tag == "keymap":
                    out.append(p)
            except ET.ParseError:
                continue
        return out

    resolved = keymaps(SOURCE_DIR.glob("*.resolved.xml"))
    candidates = resolved or keymaps(
        p for p in SOURCE_DIR.glob("*.xml") if not p.name.endswith(".resolved.xml")
    )
    if not candidates:
        raise SystemExit(
            f"no <keymap> *.xml in {SOURCE_DIR}/ - run `python3 resolve_keymap.py`, "
            f"or drop a PhpStorm 'Export Keymap' file there (any name)."
        )
    if len(candidates) == 1:
        return candidates[0]
    newest = max(candidates, key=lambda p: p.stat().st_mtime)
    others = ", ".join(p.name for p in candidates if p != newest)
    print(f"note: {len(candidates)} keymap files in source/; using newest "
          f"'{newest.name}' (ignoring: {others})", file=sys.stderr)
    return newest


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


def main(argv: list[str] | None = None) -> int:
    import argparse
    argparse.ArgumentParser(
        description="Generate keybindings.generated.json + report.md from "
                    "source/*.resolved.xml (or a raw source/*.xml export). No options.",
    ).parse_args(argv)
    source_xml = resolve_source_xml()
    print(f"source: {source_xml.relative_to(ROOT)}")

    res_dir, kk_ver, kk_src = kkato.resolve()
    print(f"k--kato: {kk_src}  v{kk_ver}")
    if kk_src.startswith("installed") and kk_ver != kkato.vendored_version():
        print(f"  note: vendor/kkato is pinned at v{kkato.vendored_version()} - "
              f"run `./port.py --sync-vendor` to refresh the offline fallback",
              file=sys.stderr)

    overrides = load_jsonc(OVERRIDES_PATH)
    manual_action_command = overrides.get("manualActionCommand", {})
    base_entries = overrides.get("entries", [])
    drop_actions = set(overrides.get("dropActions", []))

    key_map = load_key_map(res_dir)
    action_map = load_action_map(res_dir, manual_action_command)

    skip_set = kkato.skip_set_path(res_dir)
    ext_shipped = json.loads(skip_set.read_text(encoding="utf-8")) if skip_set.is_file() else []
    covered = {(e.get("command"), e.get("key")) for e in ext_shipped}
    covered |= {(e.get("command"), e.get("key")) for e in base_entries}

    source = parse_source(source_xml)

    generated: list[dict] = []
    emitted_pairs: set[tuple] = set()
    rep_mapped: list[str] = []
    rep_covered: list[str] = []
    rep_unmapped: list[str] = []
    rep_badkey: list[str] = []
    rep_mouse: list[str] = []

    for src_idx, (aid, keystrokes, mouse) in enumerate(source):
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
                entry = {"key": vkey, "command": command, "_src": src_idx}
                # Keys the shell / integrated terminal needs for itself (readline
                # control chars, word motion, X11 clipboard) get a guard so the
                # editor binding never swallows them in the terminal.
                if needs_terminal_guard(vkey):
                    entry["when"] = "!terminalFocus"
                generated.append(entry)
                rep_mapped.append(f"{command}  <-  {vkey}  ({aid})")

    generated, order_resolved = resolve_conflicts_by_keymap_order(generated)
    for e in generated:
        e.pop("_src", None)
    generated.sort(key=lambda e: (e["command"], e["key"]))

    hard_conflicts, soft_conflicts = find_key_conflicts(generated, base_entries)

    src_rel = source_xml.relative_to(ROOT)
    header = (
        "// ============================================================================\n"
        "// GENERATED by intelli-key-port/generate.py  -  DO NOT EDIT BY HAND.\n"
        f"// Source of truth: {src_rel} (resolved from the IDE's active keymap).\n"
        "// Curated base + terminal-signal guards live in overrides.jsonc and are\n"
        "// appended verbatim at the BOTTOM of this array (VS Code: last entry wins).\n"
        "// Rebuild + deploy:  ./port.py       (or: python3 generate.py && python3 install.py)\n"
        "// ============================================================================\n"
    )

    body_generated = ",\n".join("  " + json.dumps(e) for e in generated)
    body_overrides = ",\n".join("  " + json.dumps(e) for e in base_entries)
    parts = [p for p in (body_generated, body_overrides) if p]
    OUT_KEYBINDINGS.write_text(
        header
        + "[\n"
        + f"\n  // ---- generated from {src_rel} ----\n"
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

    def conflict_block(title, rows):
        if not rows:
            return f"## {title}  (0)\n\n_none_\n"
        lines = []
        for key, binds in rows:
            lines.append(key)
            for cmd, when, origin in binds:
                lines.append(f"    {cmd}  [{when or 'always'}]  ({origin})")
        return f"## {title}  ({len(rows)})\n\n```\n" + "\n".join(lines) + "\n```\n"

    def order_block(title, rows):
        if not rows:
            return f"## {title}  (0)\n\n_none_\n"
        lines = sorted(f"{key}   keep {win}   drop {lose}" for key, win, lose in rows)
        return f"## {title}  ({len(rows)})\n\n```\n" + "\n".join(lines) + "\n```\n"

    OUT_REPORT.write_text(
        "# IntelliKeyPort - keymap port report (IntelliJ -> VS Code)\n\n"
        f"- source file: `{src_rel}`\n"
        f"- source actions parsed: **{len(source)}**\n"
        f"- generated entries: **{len(generated)}**\n"
        f"- curated base entries (overrides.jsonc): **{len(base_entries)}**\n"
        f"- total in keybindings.generated.json: **{len(generated) + len(base_entries)}**\n\n"
        + order_block("Key conflicts - resolved by keymap order (earlier action wins)", order_resolved)
        + "\n"
        + conflict_block("Key conflicts - no winner picked (resolve in overrides.jsonc)", hard_conflicts)
        + "\n"
        + conflict_block("Key conflicts - overrides.jsonc picks the winner", soft_conflicts)
        + "\n"
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
          f"badkey={len(set(rep_badkey))}, mouse={len(set(rep_mouse))}, "
          f"conflicts: order-resolved={len(order_resolved)}, "
          f"unresolved={len(hard_conflicts)}, overridden={len(soft_conflicts)})")

    for key, win, lose in order_resolved:
        print(f"  keymap order: {key} -> kept {win}, dropped {lose}")

    if hard_conflicts:
        print(f"WARNING: {len(hard_conflicts)} key(s) bound to 2+ commands with no "
              f"curated winner (see {OUT_REPORT.name} 'Key conflicts'):", file=sys.stderr)
        for key, binds in hard_conflicts:
            cmds = ", ".join(sorted({c for c, _, _ in binds}))
            print(f"  {key}  ->  {cmds}", file=sys.stderr)
        print("  resolve by adding an entry to overrides.jsonc `entries`, or the "
              "IntelliJ action to `dropActions`.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
