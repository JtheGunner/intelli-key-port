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

# VS Code-family editors: config-folder base name -> friendly label
EDITORS = {
    "Code": "VS Code",
    "Code - Insiders": "VS Code Insiders",
    "VSCodium": "VSCodium",
    "Cursor": "Cursor",
    "Windsurf": "Windsurf",
    "Antigravity": "Antigravity",
    "Antigravity IDE": "Antigravity IDE",
}


def user_data_root() -> Path:
    system = platform.system()
    if system == "Darwin":
        return Path.home() / "Library" / "Application Support"
    if system == "Windows":
        return Path(os.environ.get("APPDATA") or (Path.home() / "AppData" / "Roaming"))
    return Path(os.environ.get("XDG_CONFIG_HOME") or (Path.home() / ".config"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", default=str(ROOT / "keybindings.generated.json"),
                    help="source keybindings file (default: keybindings.generated.json)")
    ap.add_argument("--only", action="append", metavar="NAME",
                    help="restrict to this editor config-folder name (repeatable)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    src = Path(args.file)
    if not src.is_file():
        raise SystemExit(f"{src} missing - run:  python3 generate.py")

    root = user_data_root()
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    wanted = set(args.only) if args.only else None

    wrote = skipped = 0
    for folder, label in EDITORS.items():
        if wanted is not None and folder not in wanted:
            continue
        user_dir = root / folder / "User"
        if not user_dir.is_dir():
            continue
        dst = user_dir / "keybindings.json"
        if args.dry_run:
            print(f"would write : {dst}")
            wrote += 1
            continue
        if dst.exists():
            backup = dst.with_name(f"keybindings.json.bak-{stamp}")
            shutil.copy2(dst, backup)
            print(f"backup      : {backup}")
        shutil.copyfile(src, dst)
        print(f"wrote       : {dst}   ({label})")
        wrote += 1

    if wanted:
        missing = wanted - {f for f in EDITORS}
        for m in missing:
            print(f"unknown editor name: {m}", file=sys.stderr)

    if wrote == 0:
        print("no VS Code-family editors found under " + str(root), file=sys.stderr)
        return 1
    if not args.dry_run:
        print(f"\ndone - {wrote} editor(s). Reload each window "
              f"(Developer: Reload Window) to pick up the changes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
