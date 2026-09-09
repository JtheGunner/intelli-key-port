#!/usr/bin/env python3
"""
Deploy keybindings.generated.json to every VS Code-family editor that is
installed on this machine (macOS, Windows, Linux). Each target's existing
keybindings.json is backed up with a timestamp first. Idempotent.

    python3 install.py                 # deploy to all detected editors
    python3 install.py --dry-run       # show what would happen
    python3 install.py --only Code --only Cursor
    python3 install.py --file other.json
"""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SYSTEM = platform.system()

# VS Code-family editors: config-folder name -> (label, flatpak id, snap name)
EDITORS = {
    "Code":            ("VS Code",           "com.visualstudio.code",  "code"),
    "Code - Insiders": ("VS Code Insiders",  None,                     "code-insiders"),
    "VSCodium":        ("VSCodium",          "com.vscodium.codium",    "codium"),
    "Cursor":          ("Cursor",            None,                     None),
    "Windsurf":        ("Windsurf",          None,                     None),
    "Antigravity":     ("Antigravity",       None,                     None),
    "Antigravity IDE": ("Antigravity IDE",   None,                     None),
}


def user_data_root() -> Path:
    if SYSTEM == "Darwin":
        return Path.home() / "Library" / "Application Support"
    if SYSTEM == "Windows":
        return Path(os.environ.get("APPDATA") or (Path.home() / "AppData" / "Roaming"))
    return Path(os.environ.get("XDG_CONFIG_HOME") or (Path.home() / ".config"))


def candidate_user_dirs(folder: str, flatpak_id: str | None, snap_name: str | None):
    """All <...>/<folder>/User dirs to consider for one editor, most-standard first."""
    dirs = [user_data_root() / folder / "User"]
    if SYSTEM == "Linux":
        home = Path.home()
        if flatpak_id:
            dirs.append(home / ".var" / "app" / flatpak_id / "config" / folder / "User")
        if snap_name:
            dirs += [home / "snap" / snap_name / "current" / ".config" / folder / "User",
                     home / "snap" / snap_name / "common" / ".config" / folder / "User"]
    # de-dupe, keep order
    seen, out = set(), []
    for d in dirs:
        if d not in seen:
            seen.add(d)
            out.append(d)
    return out


def build_arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", default=str(ROOT / "keybindings.generated.json"),
                    help="source keybindings file (default: keybindings.generated.json)")
    ap.add_argument("--only", action="append", metavar="NAME",
                    help="restrict to this editor config-folder name (repeatable)")
    ap.add_argument("--dry-run", action="store_true")
    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)

    src = Path(args.file)
    if not src.is_file():
        raise SystemExit(f"{src} missing - run:  python3 generate.py")

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    wanted = set(args.only) if args.only else None
    if wanted:
        for m in wanted - set(EDITORS):
            print(f"unknown editor name: {m}", file=sys.stderr)

    wrote = 0
    for folder, (label, flatpak_id, snap_name) in EDITORS.items():
        if wanted is not None and folder not in wanted:
            continue
        for user_dir in candidate_user_dirs(folder, flatpak_id, snap_name):
            if not user_dir.is_dir():
                continue
            dst = user_dir / "keybindings.json"
            if args.dry_run:
                print(f"would write : {dst}   ({label})")
                wrote += 1
                continue
            if dst.exists():
                backup = dst.with_name(f"keybindings.json.bak-{stamp}")
                shutil.copy2(dst, backup)
                print(f"backup      : {backup}")
            shutil.copyfile(src, dst)
            print(f"wrote       : {dst}   ({label})")
            wrote += 1

    if wrote == 0:
        print("no VS Code-family editor config dirs found "
              f"(looked under {user_data_root()}"
              + (", ~/.var/app, ~/snap" if SYSTEM == "Linux" else "") + ")",
              file=sys.stderr)
        return 1
    if not args.dry_run:
        print(f"\ndone - {wrote} editor(s). Reload each window "
              f"(Developer: Reload Window) to pick up the changes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
