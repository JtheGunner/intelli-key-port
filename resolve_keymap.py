#!/usr/bin/env python3
"""
Resolve a JetBrains user keymap into a flat, fully-inherited XML - our own
replacement for the `intellij-keymap-xml-exporter` round-trip.

Why do this ourselves
---------------------
The external exporter mangles keystrokes it cannot represent. Concretely it
turned the user's `ctrl §` (stored by PhpStorm as the extended key code
`ctrl #10000a7`, 0xA7 = section sign) into `ctrl UNKNOWN`. Reading PhpStorm's
own keymap files and walking the `parent=` chain keeps every token intact and
removes the third-party dependency.

Chain for this user:
    jeffry-default-macos-win   (~19 action overrides, in the config dir)
      └─ parent "Default for XWin"   (16 overrides, bundled in app.jar)
           └─ parent "$default"      (424 actions, bundled in app.jar, root)

Merge rule (standard IntelliJ semantics):
  * child <action id> with >=1 shortcut  -> REPLACES the parent's short
    list for that action id (not merged).
  * child <action id/> with no shortcut  -> action has no shortcuts
    (clears whatever the parent gave it).

Output: source/<name>.resolved.xml  (picked up by generate.py, which prefers
*.resolved.xml when present).

Usage:
    python3 resolve_keymap.py                      # auto-detect newest PhpStorm + its single user keymap
    python3 resolve_keymap.py --product IntelliJIdea
    python3 resolve_keymap.py --keymap "my keymap"
    python3 resolve_keymap.py --config-dir ~/... --app /Applications/PhpStorm.app
"""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
from xml.sax.saxutils import quoteattr

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "source"

JETBRAINS = Path.home() / "Library" / "Application Support" / "JetBrains"
# product config dir -> .app bundle name stem
APP_STEM = {
    "PhpStorm": "PhpStorm",
    "IntelliJIdea": "IntelliJ IDEA",
    "IdeaIC": "IntelliJ IDEA CE",
    "WebStorm": "WebStorm",
    "PyCharm": "PyCharm",
    "DataGrip": "DataGrip",
    "GoLand": "GoLand",
    "RubyMine": "RubyMine",
    "CLion": "CLion",
    "Rider": "Rider",
}


def newest_product_dir(product: str) -> Path:
    hits = sorted(
        (p for p in JETBRAINS.glob(f"{product}*") if (p / "keymaps").is_dir()),
        key=lambda p: p.stat().st_mtime,
    )
    if not hits:
        raise SystemExit(
            f"no '{product}*' dir with a keymaps/ folder under {JETBRAINS}"
        )
    return hits[-1]


def find_app(product: str, override: str | None) -> Path:
    if override:
        p = Path(override).expanduser()
        if not p.exists():
            raise SystemExit(f"--app not found: {p}")
        return p
    stem = APP_STEM.get(product, product)
    for base in (Path("/Applications"), Path.home() / "Applications"):
        hits = sorted(base.glob(f"{stem}*.app"))
        if hits:
            return hits[-1]
    raise SystemExit(
        f"could not locate {stem}*.app in /Applications or ~/Applications - pass --app"
    )


class KeymapSource:
    """Provides keymap XML text by name, from the config dir or the app's jars."""

    def __init__(self, config_keymaps: Path, app: Path):
        self.config_keymaps = config_keymaps
        self.jars = [app / "Contents" / "lib" / "app.jar"]
        self.jars += sorted((app / "Contents" / "plugins").glob("keymap-*/lib/*.jar"))
        self._jar_index: dict[str, tuple[Path, str]] = {}
        for jar in self.jars:
            if not jar.exists():
                continue
            with zipfile.ZipFile(jar) as z:
                for n in z.namelist():
                    m = re.fullmatch(r"keymaps/(.+)\.xml", n)
                    if m:
                        self._jar_index.setdefault(m.group(1), (jar, n))

    def get(self, name: str) -> str:
        local = self.config_keymaps / f"{name}.xml"
        if local.is_file():
            return local.read_text(encoding="utf-8")
        if name in self._jar_index:
            jar, entry = self._jar_index[name]
            with zipfile.ZipFile(jar) as z:
                return z.read(entry).decode("utf-8")
        raise SystemExit(
            f"keymap '{name}' not found in {self.config_keymaps} or "
            f"{[j.name for j in self.jars]}"
        )


def parse_actions(xml_text: str):
    """id -> {'kbd': [(first, second|None), ...], 'mouse': [str, ...], 'empty': bool}"""
    root = ET.fromstring(xml_text)
    out: dict[str, dict] = {}
    for a in root.findall("action"):
        aid = a.get("id")
        kbd = [
            (ks.get("first-keystroke"), ks.get("second-keystroke"))
            for ks in a.findall("keyboard-shortcut")
        ]
        mouse = [ms.get("keystroke") for ms in a.findall("mouse-shortcut")]
        out[aid] = {"kbd": kbd, "mouse": mouse, "empty": not kbd and not mouse}
    return root.get("parent"), out


def plugin_default_shortcuts(app: Path, keymap_names: set[str]):
    """Shortcuts that plugins register for a keymap via their META-INF/*.xml
    (`<action id><keyboard-shortcut keymap="$default"/>` etc.). These are real
    IDE defaults but live outside keymaps/*.xml.

    Returns {keymap_name: {action_id: {"add": [(first, second|None)],
                                       "remove": [(first, second|None)]}}}
    """
    acc: dict[str, dict[str, dict]] = {n: {} for n in keymap_names}
    for jar in sorted(app.glob("Contents/**/*.jar")):
        try:
            zf = zipfile.ZipFile(jar)
        except zipfile.BadZipFile:
            continue
        with zf:
            for entry in zf.namelist():
                if not (entry.startswith("META-INF/") and entry.endswith(".xml")):
                    continue
                try:
                    root = ET.fromstring(zf.read(entry))
                except ET.ParseError:
                    continue
                for node in root.iter():
                    if node.tag not in ("action", "reference"):
                        continue
                    aid = node.get("id") or node.get("ref")
                    if not aid:
                        continue
                    for ks in node.findall("keyboard-shortcut"):
                        km = ks.get("keymap")
                        if km not in keymap_names:
                            continue
                        combo = (ks.get("first-keystroke"), ks.get("second-keystroke"))
                        if not combo[0]:
                            continue
                        slot = acc[km].setdefault(aid, {"add": [], "remove": []})
                        bucket = "remove" if ks.get("remove") == "true" else "add"
                        if combo not in slot[bucket]:
                            slot[bucket].append(combo)
    return acc


def resolve(name: str, src: KeymapSource, app: Path):
    """Walk parent -> child, return (chain, merged actions dict, plugin_added count)."""
    chain: list[str] = []
    layers: list[dict] = []
    cur = name
    seen = set()
    while cur:
        if cur in seen:
            raise SystemExit(f"cycle in keymap parents at '{cur}'")
        seen.add(cur)
        parent, actions = parse_actions(src.get(cur))
        chain.append(cur)
        layers.append(actions)
        cur = parent
    chain.reverse()
    layers.reverse()  # root ($default) first

    plugin = plugin_default_shortcuts(app, set(chain))
    plugin_added = 0

    merged: dict[str, dict] = {}
    for layer_name, actions in zip(chain, layers):
        # 1. plugin-registered defaults for this chain level (lowest precedence)
        for aid, slot in plugin.get(layer_name, {}).items():
            cur_kbd = merged.get(aid, {}).get("kbd", []) if aid in merged else []
            cur_kbd = [c for c in cur_kbd if c not in slot["remove"]]
            for c in slot["add"]:
                if c not in cur_kbd:
                    cur_kbd.append(c)
                    plugin_added += 1
            merged.setdefault(aid, {"kbd": [], "mouse": []})["kbd"] = cur_kbd
        # 2. the keymaps/<name>.xml layer overrides
        for aid, spec in actions.items():
            if spec["empty"]:
                merged[aid] = {"kbd": [], "mouse": []}
            else:
                merged[aid] = {"kbd": list(spec["kbd"]), "mouse": list(spec["mouse"])}
    return chain, merged, plugin_added


def write_resolved(name: str, chain: list[str], merged: dict[str, dict]) -> Path:
    lines = [
        "<!-- GENERATED by resolve_keymap.py - flattened from PhpStorm's own keymap files. -->",
        f"<!-- inheritance chain: {' -> '.join(chain)} -->",
        f'<keymap version="1" name={quoteattr(name)}>',
    ]
    kept = 0
    for aid in sorted(merged):
        spec = merged[aid]
        if not spec["kbd"] and not spec["mouse"]:
            continue
        kept += 1
        lines.append(f"  <action id={quoteattr(aid)}>")
        for first, second in spec["kbd"]:
            attrs = f' first-keystroke={quoteattr(first)}'
            if second:
                attrs += f' second-keystroke={quoteattr(second)}'
            lines.append(f"    <keyboard-shortcut{attrs} />")
        for ms in spec["mouse"]:
            lines.append(f"    <mouse-shortcut keystroke={quoteattr(ms)} />")
        lines.append("  </action>")
    lines.append("</keymap>")
    OUT_DIR.mkdir(exist_ok=True)
    out = OUT_DIR / f"{name}.resolved.xml"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out, kept


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--product", default="PhpStorm", help="JetBrains product config prefix (default: PhpStorm)")
    ap.add_argument("--keymap", help="user keymap name (default: the single *.xml in keymaps/, newest if several)")
    ap.add_argument("--config-dir", help="explicit <Product><version> config dir (overrides --product autodetect)")
    ap.add_argument("--app", help="explicit .app bundle (default: /Applications/<Product>*.app)")
    args = ap.parse_args()

    product_dir = Path(args.config_dir).expanduser() if args.config_dir else newest_product_dir(args.product)
    keymaps_dir = product_dir / "keymaps"
    if not keymaps_dir.is_dir():
        raise SystemExit(f"no keymaps/ under {product_dir}")

    if args.keymap:
        name = args.keymap
        if not (keymaps_dir / f"{name}.xml").is_file():
            raise SystemExit(f"{name}.xml not in {keymaps_dir}")
    else:
        xmls = sorted(keymaps_dir.glob("*.xml"), key=lambda p: p.stat().st_mtime)
        if not xmls:
            raise SystemExit(f"no user keymaps in {keymaps_dir}")
        if len(xmls) > 1:
            print(f"note: {len(xmls)} user keymaps; using newest '{xmls[-1].stem}' "
                  f"(others: {', '.join(p.stem for p in xmls[:-1])})", file=sys.stderr)
        name = xmls[-1].stem

    app = find_app(args.product, args.app)
    src = KeymapSource(keymaps_dir, app)

    chain, merged, plugin_added = resolve(name, src, app)
    out, kept = write_resolved(name, chain, merged)

    print(f"product : {product_dir.name}")
    print(f"app     : {app}")
    print(f"chain   : {' -> '.join(chain)}")
    print(f"actions : {kept} with shortcuts  ->  {out.relative_to(ROOT)}")
    print(f"        : incl. {plugin_added} shortcuts from plugin descriptors")
    # surface extended / unusual tokens so they are never a silent surprise
    ext = sorted({t for spec in merged.values() for f, s in spec["kbd"]
                  for t in re.findall(r"#[0-9a-fA-F]+", f or "")})
    if ext:
        decoded = ", ".join(f"{t} = {chr(int(t[1:], 16) & 0xFFFF)!r}" for t in ext)
        print(f"extended: {decoded}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
