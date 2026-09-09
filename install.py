#!/usr/bin/env python3
"""
Deploy keybindings.generated.json to every VS Code-family editor that is
installed on this machine (macOS, Windows, Linux). Each target's existing
keybindings.json is backed up with a timestamp first. Idempotent.

When more than one editor is found and the run is interactive, an
arrow-key checkbox prompt asks which of them to write to (all pre-checked).
The prompt is skipped with --only, --dry-run, or when there is no tty.

    python3 install.py                 # detect editors, then pick interactively
    python3 install.py --dry-run       # show what would happen (all editors)
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

sys.path.insert(0, str(Path(__file__).resolve().parent))

from prompt_select import PromptUnavailable, choose  # noqa: E402

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


def discover_targets(wanted: set[str] | None):
    """[(folder, label, dst)] for every existing candidate dir, deduped by dst."""
    out, seen = [], set()
    for folder, (label, flatpak_id, snap_name) in EDITORS.items():
        if wanted is not None and folder not in wanted:
            continue
        for user_dir in candidate_user_dirs(folder, flatpak_id, snap_name):
            if not user_dir.is_dir():
                continue
            dst = user_dir / "keybindings.json"
            if dst in seen:
                continue
            seen.add(dst)
            out.append((folder, label, dst))
    return out


def select_targets(targets, args):
    """Let the user pick from `targets` interactively; return the kept subset.

    Falls back to all of `targets` when a prompt is not appropriate (--only,
    --dry-run, a single hit, or no interactive terminal). Returns None when the
    user explicitly cancelled the picker.
    """
    if args.only or args.dry_run or len(targets) <= 1:
        return targets
    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        return targets

    print(f"found: {len(targets)} VS Code-compatible IDE(s)")
    labels = [f"{label}  ({dst.parent})" for _, label, dst in targets]
    try:
        picked = choose(labels, title="Install keybindings into which IDEs?")
    except PromptUnavailable:
        return targets
    if picked is None:
        return None
    return [targets[i] for i in picked]


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

    wanted = set(args.only) if args.only else None
    if wanted:
        for m in wanted - set(EDITORS):
            print(f"unknown editor name: {m}", file=sys.stderr)

    targets = discover_targets(wanted)
    if not targets:
        print("no VS Code-family editor config dirs found "
              f"(looked under {user_data_root()}"
              + (", ~/.var/app, ~/snap" if SYSTEM == "Linux" else "") + ")",
              file=sys.stderr)
        return 1

    targets = select_targets(targets, args)
    if targets is None:
        print("nothing selected - aborted.")
        return 0
    if not targets:
        print("no IDE selected - nothing to do.")
        return 0

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    wrote = 0
    for _folder, label, dst in targets:
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

    if not args.dry_run:
        print(f"\ndone - {wrote} editor(s). Reload each window "
              f"(Developer: Reload Window) to pick up the changes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
