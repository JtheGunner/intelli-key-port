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
   `vendor/kkato/`) plus `manualActionCommand` from the curated layers.
3. Translate every AWT keystroke token -> VS Code key token via
   `KeystrokeKeyMapping.json` (same source) plus a few hard-coded rules.
4. Drop anything already provided identically by the curated layers or by the
   extension's shipped bindings (`default/<OS>/VSCode.json`, matched to this
   platform).
5. Emit `keybindings.generated.json`:
      <header>
      [ ...generated entries...,
        ...curated `entries`, layer by layer (LAST so they win)... ]
6. Emit `report.md`: what mapped, what the curated layers already covered, what
   has no VS Code equivalent, and the mouse shortcuts (not portable).

Curated layers
--------------
`overrides.jsonc` is always applied and stays keymap- and machine-neutral.
`--layer NAME` stacks `layers/NAME.jsonc` on top (e.g. `windows-keymap` for a
Ctrl-based keymap on macOS); `--layer PATH` stacks your own file. Later layers
win.

Design note
-----------
Keystrokes are ported literally: a Ctrl-based keymap ($default / XWin) keeps
`ctrl`, a macOS keymap keeps `cmd`. Being user keybindings loaded after the
k--kato extension, generated entries win over the extension's bindings for
every action we map. Actions we cannot map fall through to the extension -
listed in report.md so `manualActionCommand` can be extended over time.
"""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

import kkato

ROOT = Path(__file__).resolve().parent
SOURCE_DIR = ROOT / "source"
OVERRIDES_PATH = ROOT / "overrides.jsonc"
LAYERS_DIR = ROOT / "layers"
LAYER_KEYS = {"manualActionCommand", "dropActions", "entries"}
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


# Context-only VS Code commands -> the `when` clause that confines them to their
# context. IntelliJ scopes these actions implicitly (e.g. the lookup popup); a
# VS Code binding without `when` is active everywhere and swallows the key even
# where the command is a no-op - a bare `tab` on a suggest-widget command kills
# indentation and inline (AI) completions. Context keys of the widget itself
# only: focus keys like `textInputFocus` are unreliable across the VS Code family.
_SUGGEST_WIDGET_WHEN = "suggestWidgetVisible && !inInlineEditsPreviewEditor && !inlineEditIsVisible"
_COMMAND_WHEN = {
    "acceptSelectedSuggestion": _SUGGEST_WIDGET_WHEN,
    "acceptAlternativeSelectedSuggestion": _SUGGEST_WIDGET_WHEN,
}


def binding_when(command: str, key: str) -> str:
    """`when` clause for a generated binding: the command's own context (if it
    is context-only) plus the terminal guard for keys the shell needs. Empty
    string means the binding applies everywhere."""
    terms = [_COMMAND_WHEN.get(command, "")]
    # Keys the shell / integrated terminal needs for itself (readline control
    # chars, word motion, X11 clipboard) must never be swallowed there.
    if needs_terminal_guard(key):
        terms.append("!terminalFocus")
    return " && ".join(t for t in terms if t)


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
      soft - a curated layer (overrides.jsonc or a --layer) also binds the key,
             so a human already chose. Only reported.
    `-command` removals and pairs with mutually exclusive `when` clauses are not
    counted as conflicts.
    """
    from collections import defaultdict
    slots: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for default_origin, entries in (("generated", generated), ("overrides.jsonc", base_entries)):
        for e in entries:
            cmd = e.get("command", "")
            if not cmd.startswith("-"):
                origin = e.get("_layer", default_origin)
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
        bucket = soft if any(o != "generated" for _, _, o in live) else hard
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


@dataclass
class Overrides:
    """The base overrides.jsonc plus every --layer, stacked in order."""
    layers: list[str] = field(default_factory=list)
    manual_action_command: dict[str, str] = field(default_factory=dict)
    drop_actions: set[str] = field(default_factory=set)
    drop_origin: dict[str, str] = field(default_factory=dict)
    entries: list[dict] = field(default_factory=list)   # each tagged with `_layer`


def resolve_layer(spec: str) -> Path:
    """`--layer NAME` -> layers/NAME.jsonc; `--layer PATH` -> that file."""
    looks_like_path = "/" in spec or "\\" in spec or spec.endswith((".jsonc", ".json"))
    if looks_like_path:
        path = Path(spec).expanduser()
        if not path.is_file():
            raise SystemExit(f"layer file not found: {spec}")
        return path.resolve()
    named = LAYERS_DIR / f"{spec}.jsonc"
    if named.is_file():
        return named
    available = ", ".join(sorted(p.stem for p in LAYERS_DIR.glob("*.jsonc"))) or "none"
    raise SystemExit(f"unknown layer '{spec}' - bundled layers: {available}; "
                     f"or pass the path to your own .jsonc file")


def _layer_label(path: Path) -> str:
    if path == OVERRIDES_PATH:
        return "overrides.jsonc"
    if path.parent == LAYERS_DIR:
        return f"layer:{path.stem}"
    return path.name


def _load_layer(path: Path, label: str) -> dict:
    try:
        data = load_jsonc(path)
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"{label}: cannot read {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"{label}: top level must be an object")
    unknown = set(data) - LAYER_KEYS
    if unknown:
        raise SystemExit(f"{label}: unknown key(s) {sorted(unknown)} - "
                         f"allowed: {sorted(LAYER_KEYS)}")
    if not isinstance(data.get("manualActionCommand", {}), dict):
        raise SystemExit(f"{label}: manualActionCommand must be an object")
    if not isinstance(data.get("dropActions", []), list):
        raise SystemExit(f"{label}: dropActions must be a list")
    entries = data.get("entries", [])
    if not isinstance(entries, list):
        raise SystemExit(f"{label}: entries must be a list")
    for e in entries:
        if not (isinstance(e, dict) and isinstance(e.get("key"), str)
                and isinstance(e.get("command"), str)):
            raise SystemExit(f"{label}: every entry needs a string key and command: {e!r}")
    return data


def load_overrides(layer_specs: list[str]) -> Overrides:
    """Stack overrides.jsonc and the given layers. Later layers win: their
    entries come later in the file (VS Code: last entry wins) and their
    manualActionCommand rows replace earlier ones; dropActions accumulate."""
    paths = [OVERRIDES_PATH] + [resolve_layer(s) for s in layer_specs]
    if len(set(paths)) != len(paths):
        raise SystemExit(f"a layer is given twice: {layer_specs}")
    ov = Overrides()
    for path in paths:
        label = _layer_label(path)
        data = _load_layer(path, label)
        ov.layers.append(label)
        ov.manual_action_command.update(data.get("manualActionCommand", {}))
        for aid in data.get("dropActions", []):
            ov.drop_actions.add(aid)
            ov.drop_origin[aid] = label
        ov.entries += [dict(e, _layer=label) for e in data.get("entries", [])]
    return ov


_CHAIN_RE = re.compile(r"inheritance chain:\s*(.+?)\s*-->")
_MAC_KEYMAP_PREFIXES = ("Mac OS X", "macOS")


def keymap_chain(source_xml: Path) -> list[str]:
    """Parent chain written by resolve_keymap.py into the resolved file's header
    ($default -> ... -> active keymap). Empty for a raw export."""
    head = source_xml.read_text(encoding="utf-8")[:2048]
    m = _CHAIN_RE.search(head)
    return [n.strip() for n in m.group(1).split("->")] if m else []


def is_ctrl_keymap(chain: list[str]) -> bool:
    """True for the Ctrl-based family ($default / XWin / KDE / GNOME)."""
    return bool(chain) and not any(n.startswith(_MAC_KEYMAP_PREFIXES) for n in chain)


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
    ap = argparse.ArgumentParser(
        description="Generate keybindings.generated.json + report.md from "
                    "source/*.resolved.xml (or a raw source/*.xml export).",
    )
    ap.add_argument("--layer", action="append", default=[], metavar="NAME|PATH",
                    help="stack an override layer on top of overrides.jsonc: a bundled "
                         "one (layers/NAME.jsonc) or your own .jsonc file (repeatable, "
                         "applied in order)")
    args = ap.parse_args(argv)
    overrides = load_overrides(args.layer)
    source_xml = resolve_source_xml()
    print(f"source: {source_xml.relative_to(ROOT)}")
    print(f"layers: {' + '.join(overrides.layers)}")
    if (sys.platform == "darwin" and "layer:windows-keymap" not in overrides.layers
            and is_ctrl_keymap(keymap_chain(source_xml))):
        print("  hint: this is a Ctrl-based keymap - add `--layer windows-keymap` to keep "
              "terminal control keys and drop the stock Cmd shortcuts", file=sys.stderr)

    res_dir, kk_ver, kk_src = kkato.resolve()
    print(f"k--kato: {kk_src}  v{kk_ver}")
    if kk_src.startswith("installed") and kk_ver != kkato.vendored_version():
        print(f"  note: vendor/kkato is pinned at v{kkato.vendored_version()} - "
              f"run `./port.py --sync-vendor` to refresh the offline fallback",
              file=sys.stderr)

    manual_action_command = overrides.manual_action_command
    base_entries = overrides.entries
    drop_actions = overrides.drop_actions

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
            rep_covered.append(f"{aid}  (explicitly dropped by {overrides.drop_origin[aid]})")
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
                when = binding_when(command, vkey)
                if when:
                    entry["when"] = when
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
        f"// Curated layers: {' + '.join(overrides.layers)} - appended verbatim at the\n"
        "// BOTTOM of this array, in that order (VS Code: last entry wins).\n"
        "// Rebuild + deploy:  ./port.py [--layer ...]\n"
        "// ============================================================================\n"
    )

    sections = []
    if generated:
        sections.append(f"\n  // ---- generated from {src_rel} ----\n"
                        + ",\n".join("  " + json.dumps(e) for e in generated))
    for label in overrides.layers:
        rows = [{k: v for k, v in e.items() if k != "_layer"}
                for e in base_entries if e["_layer"] == label]
        if rows:
            sections.append(f"\n  // ---- {label} (curated, wins on conflict) ----\n"
                            + ",\n".join("  " + json.dumps(e) for e in rows))
    OUT_KEYBINDINGS.write_text(
        header + "[\n" + ",\n".join(sections) + "\n]\n",
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
        f"- curated layers: {', '.join(f'`{x}`' for x in overrides.layers)}\n"
        f"- curated entries: **{len(base_entries)}**\n"
        f"- total in keybindings.generated.json: **{len(generated) + len(base_entries)}**\n\n"
        + order_block("Key conflicts - resolved by keymap order (earlier action wins)", order_resolved)
        + "\n"
        + conflict_block("Key conflicts - no winner picked (resolve in a layer)", hard_conflicts)
        + "\n"
        + conflict_block("Key conflicts - a curated layer picks the winner", soft_conflicts)
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

    print(f"generated {len(generated)} entries + {len(base_entries)} curated -> {OUT_KEYBINDINGS.name}")
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
        print("  resolve by adding an entry to a layer's `entries`, or the "
              "IntelliJ action to its `dropActions`.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
