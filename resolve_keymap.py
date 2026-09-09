#!/usr/bin/env python3
"""
Resolve the *active* JetBrains keymap into a flat, fully-inherited XML - our own
replacement for the `intellij-keymap-xml-exporter` round-trip.

Why do this ourselves
---------------------
The external exporter mangles keystrokes it cannot represent (it turned
`ctrl §`, stored by the IDE as `ctrl #10000a7`, into `ctrl UNKNOWN`). Reading
the IDE's own keymap files and walking the `parent=` chain keeps every token
intact and removes the third-party dependency.

What it does
------------
1. Locate the IDE install (via its `product-info.json`) and the matching
   config dir (`product-info.json` -> `dataDirectoryName`).  macOS, Windows
   and Linux, standalone installs and JetBrains Toolbox.
2. Read the ACTIVE keymap name from
   `<config>/options/mac/keymap.xml` (macOS) or `<config>/options/keymap.xml`
   -> `<active_keymap name="..."/>`.  `--keymap` overrides this.
3. Walk parent -> child (`$default` -> ... -> active), merging:
     * child <action id> with >=1 shortcut  -> REPLACES the parent's list
     * child <action id/> with no shortcut  -> clears the parent's list
   plus the shortcuts plugins register in their `META-INF/*.xml`
   (`<keyboard-shortcut keymap="$default"/>`), which live outside keymaps/*.xml.
4. Write `source/<name>.resolved.xml` (picked up by generate.py, which prefers
   *.resolved.xml when present).

Usage
-----
    python3 resolve_keymap.py                       # active keymap of the newest PhpStorm
    python3 resolve_keymap.py --product IntelliJIdea
    python3 resolve_keymap.py --keymap "macOS"      # a specific keymap (built-in or user)
    python3 resolve_keymap.py --app "/path/to/IDE"  # explicit install
    python3 resolve_keymap.py --config-dir "/path/to/<Product><version>"
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
from xml.sax.saxutils import quoteattr

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "source"
IS_MAC = platform.system() == "Darwin"
IS_WIN = platform.system() == "Windows"

# `--product` value -> substrings that identify the install (product-info.json
# "name") and the config-dir prefix (dataDirectoryName / folder name).
PRODUCTS = {
    "PhpStorm": ("PhpStorm",),
    "IntelliJIdea": ("IntelliJ IDEA", "IdeaIC", "IdeaIU"),
    "WebStorm": ("WebStorm",),
    "PyCharm": ("PyCharm",),
    "DataGrip": ("DataGrip",),
    "GoLand": ("GoLand",),
    "RubyMine": ("RubyMine",),
    "CLion": ("CLion",),
    "Rider": ("Rider",),
    "RustRover": ("RustRover",),
}


# --------------------------------------------------------------------------- #
# platform-aware locations
# --------------------------------------------------------------------------- #
def jetbrains_config_home() -> Path:
    if IS_MAC:
        return Path.home() / "Library" / "Application Support" / "JetBrains"
    if IS_WIN:
        base = os.environ.get("APPDATA") or (Path.home() / "AppData" / "Roaming")
        return Path(base) / "JetBrains"
    base = os.environ.get("XDG_CONFIG_HOME") or (Path.home() / ".config")
    return Path(base) / "JetBrains"


def install_search_roots() -> list[Path]:
    home = Path.home()
    roots: list[Path] = []
    if IS_MAC:
        roots += [Path("/Applications"), home / "Applications"]
        roots += [jetbrains_config_home() / "Toolbox" / "apps"]
    elif IS_WIN:
        for env in ("ProgramFiles", "ProgramFiles(x86)", "ProgramW6432"):
            if os.environ.get(env):
                roots.append(Path(os.environ[env]) / "JetBrains")
        if os.environ.get("LOCALAPPDATA"):
            la = Path(os.environ["LOCALAPPDATA"])
            roots += [la / "Programs", la / "JetBrains" / "Toolbox" / "apps",
                      la / "JetBrains"]
    else:
        roots += [Path("/opt"), Path("/usr/local"), Path("/snap"),
                  home / ".local" / "share" / "JetBrains" / "Toolbox" / "apps",
                  home / ".local" / "share" / "applications"]
    return [r for r in roots if r.exists()]


def _product_info_dirs(root: Path):
    """Yield directories that directly contain a product-info.json, a few levels deep."""
    for depth_glob in ("product-info.json",
                       "*/product-info.json",
                       "*/*/product-info.json",
                       "*/*/*/product-info.json",
                       "*/Contents/Resources/product-info.json",
                       "*/*/*/Contents/Resources/product-info.json"):
        for hit in root.glob(depth_glob):
            yield hit


def discover_installs(product: str):
    """Return [(version_tuple, install_dir, lib_dir, plugins_dir, data_dir_name), ...]."""
    names = PRODUCTS.get(product, (product,))
    found = {}
    for root in install_search_roots():
        for info_path in _product_info_dirs(root):
            try:
                info = json.loads(info_path.read_text(encoding="utf-8"))
            except (ValueError, OSError):
                continue
            if not any(n.lower() in info.get("name", "").lower() for n in names):
                continue
            # macOS: info is at <app>/Contents/Resources/ ; home = <app>/Contents
            # win/linux: info is at <install>/ ; home = <install>
            if info_path.parent.name == "Resources" and info_path.parent.parent.name == "Contents":
                home = info_path.parent.parent
                install_dir = home.parent
            else:
                home = info_path.parent
                install_dir = home
            lib = home / "lib"
            if not (lib / "app.jar").is_file():
                continue
            ver = tuple(int(x) for x in re.findall(r"\d+", info.get("version", "0"))[:4]) or (0,)
            found[install_dir] = (ver, install_dir, lib, home / "plugins",
                                  info.get("dataDirectoryName", ""))
    return sorted(found.values())


def resolve_install(product: str, app_override: str | None):
    if app_override:
        hint = Path(app_override).expanduser()
        if not hint.exists():
            raise SystemExit(f"--app not found: {hint}")
        for base in (hint, hint / "Contents", *sorted(hint.glob("*/Contents")),
                     *sorted(hint.glob("*")), *sorted(hint.glob("*/*"))):
            if (base / "lib" / "app.jar").is_file():
                data = ""
                for name in ("Resources/product-info.json", "product-info.json",
                             "../product-info.json"):
                    p = base / name
                    if p.is_file():
                        try:
                            data = json.loads(p.read_text(encoding="utf-8")).get("dataDirectoryName", "")
                        except ValueError:
                            pass
                        break
                return base / "lib", base / "plugins", data
        raise SystemExit(f"no lib/app.jar under {hint}")
    installs = discover_installs(product)
    if not installs:
        raise SystemExit(
            f"no {product} install found. Searched: "
            + ", ".join(str(r) for r in install_search_roots())
            + "  - pass --app /path/to/IDE"
        )
    if len(installs) > 1:
        others = ", ".join(".".join(map(str, v)) for v, *_ in installs[:-1])
        print(f"note: {len(installs)} {product} installs; using newest "
              f"{'.'.join(map(str, installs[-1][0]))} (others: {others})", file=sys.stderr)
    _, _, lib, plugins, data = installs[-1]
    return lib, plugins, data


def resolve_config_dir(product: str, config_override: str | None, data_dir_name: str) -> Path:
    if config_override:
        p = Path(config_override).expanduser()
        if not (p / "options").is_dir() and not (p / "keymaps").is_dir():
            raise SystemExit(f"--config-dir has no options/ or keymaps/: {p}")
        return p
    home = jetbrains_config_home()
    if data_dir_name and (home / data_dir_name).is_dir():
        return home / data_dir_name
    # fall back: newest <product>* dir with options/ or keymaps/
    cands = sorted(
        (d for d in home.glob(f"{product}*")
         if (d / "options").is_dir() or (d / "keymaps").is_dir()),
        key=lambda d: d.stat().st_mtime,
    )
    if not cands:
        raise SystemExit(f"no {product} config dir under {home}")
    return cands[-1]


def read_active_keymap(config_dir: Path) -> str | None:
    """`<active_keymap name>` from options/mac/keymap.xml (mac) or options/keymap.xml."""
    order = ["options/mac/keymap.xml", "options/keymap.xml"] if IS_MAC \
        else ["options/keymap.xml", "options/mac/keymap.xml"]
    for rel in order:
        p = config_dir / rel
        if not p.is_file():
            continue
        try:
            root = ET.fromstring(p.read_text(encoding="utf-8"))
        except ET.ParseError:
            continue
        el = root.find(".//active_keymap")
        if el is not None and el.get("name"):
            return el.get("name")
    return None


# --------------------------------------------------------------------------- #
# keymap sources + resolution
# --------------------------------------------------------------------------- #
class KeymapSource:
    """Keymap XML text by name, from the config dir or the IDE's jars."""

    def __init__(self, config_keymaps: Path, lib_dir: Path, plugins_dir: Path):
        self.config_keymaps = config_keymaps
        jars = [lib_dir / "app.jar"]
        if plugins_dir.is_dir():
            jars += sorted(plugins_dir.glob("keymap-*/lib/*.jar"))
        # index built-in keymaps by BOTH the file stem and the <keymap name="">
        # attribute inside (newer IDEs show "macOS" but ship "Mac OS X 10.5+.xml").
        self._jar_index: dict[str, tuple[Path, str]] = {}
        for jar in jars:
            if not jar.is_file():
                continue
            with zipfile.ZipFile(jar) as z:
                for n in z.namelist():
                    m = re.fullmatch(r"keymaps/(.+)\.xml", n)
                    if not m:
                        continue
                    self._jar_index.setdefault(m.group(1), (jar, n))
                    try:
                        inner = ET.fromstring(z.read(n)).get("name")
                    except ET.ParseError:
                        inner = None
                    if inner:
                        self._jar_index.setdefault(inner, (jar, n))

    # display-name -> shipped keymap name (the IDE UI renames some built-ins)
    ALIASES = {
        "macos": "Mac OS X 10.5+", "macos 10.5+": "Mac OS X 10.5+",
        "mac os x 10.5+": "Mac OS X 10.5+", "os x 10.5+": "Mac OS X 10.5+",
        "gnome": "Default for GNOME", "kde": "Default for KDE",
        "xwin": "Default for XWin", "default for gnome/kde": "Default for XWin",
        "windows": "$default", "default": "$default",
    }

    def canonical(self, name: str) -> str:
        if (self.config_keymaps / f"{name}.xml").is_file() or name in self._jar_index:
            return name
        return self.ALIASES.get(name.strip().lower(), name)

    def has(self, name: str) -> bool:
        name = self.canonical(name)
        return (self.config_keymaps / f"{name}.xml").is_file() or name in self._jar_index

    def get(self, name: str) -> str:
        name = self.canonical(name)
        local = self.config_keymaps / f"{name}.xml"
        if local.is_file():
            return local.read_text(encoding="utf-8")
        if name in self._jar_index:
            jar, entry = self._jar_index[name]
            with zipfile.ZipFile(jar) as z:
                return z.read(entry).decode("utf-8")
        raise SystemExit(f"keymap '{name}' not found in {self.config_keymaps} or the IDE jars")

    def user_keymaps(self) -> list[str]:
        return sorted(p.stem for p in self.config_keymaps.glob("*.xml"))

    def builtin_keymaps(self) -> list[str]:
        return sorted(self._jar_index)


def parse_actions(xml_text: str):
    root = ET.fromstring(xml_text)
    out: dict[str, dict] = {}
    for a in root.findall("action"):
        aid = a.get("id")
        kbd = [(ks.get("first-keystroke"), ks.get("second-keystroke"))
               for ks in a.findall("keyboard-shortcut")]
        mouse = [ms.get("keystroke") for ms in a.findall("mouse-shortcut")]
        out[aid] = {"kbd": kbd, "mouse": mouse, "empty": not kbd and not mouse}
    return root.get("parent"), out


def plugin_default_shortcuts(plugins_dir: Path, lib_dir: Path, keymap_names: set[str]):
    """Shortcuts plugins register in META-INF/*.xml for a keymap (real IDE
    defaults that live outside keymaps/*.xml).

    -> {keymap_name: {action_id: {"add": [...], "remove": [...]}}}
    """
    acc: dict[str, dict[str, dict]] = {n: {} for n in keymap_names}
    jars = []
    if plugins_dir.is_dir():
        jars += sorted(plugins_dir.glob("**/*.jar"))
    jars += sorted(lib_dir.glob("**/*.jar"))   # incl. lib/modules/*.jar (VCS etc.)
    for jar in jars:
        try:
            zf = zipfile.ZipFile(jar)
        except (zipfile.BadZipFile, OSError):
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
                        if ks.get("keymap") not in keymap_names:
                            continue
                        combo = (ks.get("first-keystroke"), ks.get("second-keystroke"))
                        if not combo[0]:
                            continue
                        slot = acc[ks.get("keymap")].setdefault(aid, {"add": [], "remove": []})
                        bucket = "remove" if ks.get("remove") == "true" else "add"
                        if combo not in slot[bucket]:
                            slot[bucket].append(combo)
    return acc


def resolve(name: str, src: KeymapSource, plugins_dir: Path, lib_dir: Path):
    chain: list[str] = []
    layers: list[dict] = []
    cur, seen = name, set()
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

    plugin = plugin_default_shortcuts(plugins_dir, lib_dir, set(chain))
    plugin_added = 0
    merged: dict[str, dict] = {}
    for layer_name, actions in zip(chain, layers):
        for aid, slot in plugin.get(layer_name, {}).items():
            cur_kbd = merged.get(aid, {}).get("kbd", []) if aid in merged else []
            cur_kbd = [c for c in cur_kbd if c not in slot["remove"]]
            for c in slot["add"]:
                if c not in cur_kbd:
                    cur_kbd.append(c)
                    plugin_added += 1
            merged.setdefault(aid, {"kbd": [], "mouse": []})["kbd"] = cur_kbd
        for aid, spec in actions.items():
            if spec["empty"]:
                merged[aid] = {"kbd": [], "mouse": []}
            else:
                merged[aid] = {"kbd": list(spec["kbd"]), "mouse": list(spec["mouse"])}
    return chain, merged, plugin_added


def write_resolved(name: str, chain: list[str], merged: dict[str, dict]):
    safe = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-") or "keymap"
    lines = [
        "<!-- GENERATED by resolve_keymap.py - flattened from the IDE's own keymap files. -->",
        f"<!-- inheritance chain: {' -> '.join(chain)} -->",
        f"<keymap version=\"1\" name={quoteattr(name)}>",
    ]
    kept = 0
    for aid in sorted(merged):
        spec = merged[aid]
        if not spec["kbd"] and not spec["mouse"]:
            continue
        kept += 1
        lines.append(f"  <action id={quoteattr(aid)}>")
        for first, second in spec["kbd"]:
            attrs = f" first-keystroke={quoteattr(first)}"
            if second:
                attrs += f" second-keystroke={quoteattr(second)}"
            lines.append(f"    <keyboard-shortcut{attrs} />")
        for ms in spec["mouse"]:
            lines.append(f"    <mouse-shortcut keystroke={quoteattr(ms)} />")
        lines.append("  </action>")
    lines.append("</keymap>")
    OUT_DIR.mkdir(exist_ok=True)
    out = OUT_DIR / f"{safe}.resolved.xml"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out, kept


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--product", default="PhpStorm",
                    help=f"JetBrains product (default: PhpStorm). Known: {', '.join(PRODUCTS)}")
    ap.add_argument("--keymap", help="keymap name to resolve (default: the IDE's active keymap)")
    ap.add_argument("--config-dir", help="explicit <Product><version> config dir")
    ap.add_argument("--app", help="explicit IDE install dir / .app bundle")
    args = ap.parse_args()

    lib_dir, plugins_dir, data_dir_name = resolve_install(args.product, args.app)
    config_dir = resolve_config_dir(args.product, args.config_dir, data_dir_name)
    src = KeymapSource(config_dir / "keymaps", lib_dir, plugins_dir)

    if args.keymap:
        name, how = args.keymap, "--keymap"
    else:
        name = read_active_keymap(config_dir)
        how = "active keymap"
        if not name:
            users = src.user_keymaps()
            if len(users) == 1:
                name, how = users[0], "only user keymap (active unknown)"
            else:
                raise SystemExit(
                    "could not read the active keymap from "
                    f"{config_dir/'options'} and there "
                    + (f"are {len(users)} user keymaps ({', '.join(users)})"
                       if users else "are no user keymaps")
                    + " - pass --keymap <name> (built-in names work too, e.g. \"macOS\")"
                )

    if not src.has(name):
        raise SystemExit(
            f"keymap '{name}' not found.\n"
            f"  user keymaps : {', '.join(src.user_keymaps()) or '(none)'}\n"
            f"  built-in     : {', '.join(src.builtin_keymaps())}"
        )
    name = src.canonical(name)

    chain, merged, plugin_added = resolve(name, src, plugins_dir, lib_dir)
    out, kept = write_resolved(name, chain, merged)

    install_root = lib_dir.parent.parent if lib_dir.parent.name == "Contents" else lib_dir.parent
    print(f"product : {args.product}")
    print(f"config  : {config_dir}")
    print(f"install : {install_root}")
    print(f"keymap  : {name}   ({how})")
    print(f"chain   : {' -> '.join(chain)}")
    print(f"actions : {kept} with shortcuts (incl. {plugin_added} from plugin descriptors)")
    print(f"output  : {out.relative_to(ROOT)}")
    ext = sorted({t for spec in merged.values() for f, s in spec["kbd"]
                  for t in re.findall(r"#[0-9a-fA-F]+", f or "")})
    if ext:
        print("extended: " + ", ".join(
            f"{t} = {chr(int(t[1:], 16) & 0xFFFF)!r}" for t in ext))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
