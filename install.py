#!/usr/bin/env python3
"""
Deploy the ported keymap to the IDEs installed on this machine (macOS,
Windows, Linux). Two target families:

  * VS Code-family editors: keybindings.generated.json -> User/keybindings.json
    (existing file backed up with a timestamp first).
  * JetBrains IDEs incl. Android Studio: the resolved keymap
    (source/*.resolved.xml) -> <config>/keymaps/<name> (ported).xml, a new
    keymap next to the originals (an existing file of that name is backed up).

When more than one target is found and the run is interactive, an arrow-key
checkbox prompt asks which of them to write to. JetBrains IDEs are opt-in:
non-interactive runs without --only write to VS Code-family editors only.
The prompt is skipped with --only, --dry-run, or when there is no tty.

    python3 install.py                 # detect targets, then pick interactively
    python3 install.py --dry-run       # show what would happen (all targets)
    python3 install.py --only Code --only Cursor
    python3 install.py --only AndroidStudio   # config-dir name or product prefix
    python3 install.py --file other.json --resolved source/x.resolved.xml
"""

from __future__ import annotations

import argparse
import os
import platform
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import jb_keymap  # noqa: E402
import resolve_keymap  # noqa: E402
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


def discover_jetbrains_targets():
    """[(folder, label, keymaps_dir)] for every JetBrains IDE config dir found.

    A config dir is `<Product><version>` (Product from CONFIG_DIR_PREFIXES,
    case-insensitive) holding `options/` or `keymaps/`. Includes Android Studio.
    """
    pattern = re.compile(
        rf"^(?:{'|'.join(resolve_keymap.CONFIG_DIR_PREFIXES)})\d", re.IGNORECASE)
    out, seen = [], set()
    for home in resolve_keymap.jetbrains_config_homes():
        for config_dir in sorted(home.iterdir()):
            if not (config_dir.is_dir() and pattern.match(config_dir.name)):
                continue
            if not ((config_dir / "options").is_dir() or (config_dir / "keymaps").is_dir()):
                continue
            dst = config_dir / "keymaps"
            if dst in seen:
                continue
            seen.add(dst)
            out.append((config_dir.name, config_dir.name, dst))
    return sorted(out)


def target_matches(folder: str, wanted: set[str]) -> bool:
    """True if `folder` equals a wanted name or starts with it (product prefix)."""
    return any(folder == w or folder.lower().startswith(w.lower()) for w in wanted)


def select_targets(targets, args, default=None, preselected=None):
    """Let the user pick from `targets` interactively; return the kept subset.

    Without a choice (a single hit, no interactive terminal) the result is
    `default`, or all of `targets` when `default` is None. --only and --dry-run
    return all of `targets`. In the picker, `preselected` (indices) are the rows
    that start checked (default: all). Returns None when the user cancelled.
    """
    fallback = targets if default is None else default
    if args.only or args.dry_run:
        return targets
    if len(targets) <= 1:
        return fallback
    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        return fallback

    print(f"found: {len(targets)} IDE(s)")
    labels = [f"{label}  ({dst.parent})" for _, label, dst in targets]
    try:
        picked = choose(labels, title="Install into which IDEs?", preselected=preselected)
    except PromptUnavailable:
        return fallback
    if picked is None:
        return None
    return [targets[i] for i in picked]


def build_arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", default=str(ROOT / "keybindings.generated.json"),
                    help="source keybindings file (default: keybindings.generated.json)")
    ap.add_argument("--resolved", metavar="PATH",
                    help="resolved keymap for JetBrains targets "
                         "(default: the only source/*.resolved.xml)")
    ap.add_argument("--only", action="append", metavar="NAME",
                    help="restrict to this editor config-folder name or JetBrains "
                         "config-dir name / product prefix, e.g. Code, PhpStorm, "
                         "AndroidStudio2026.2.2 (repeatable)")
    ap.add_argument("--dry-run", action="store_true")
    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)

    wanted = set(args.only) if args.only else None
    vscode = discover_targets(wanted)
    jetbrains_all = discover_jetbrains_targets()
    jetbrains = [t for t in jetbrains_all if wanted is None or target_matches(t[0], wanted)]
    for name in sorted(wanted or ()):
        if name not in EDITORS and not any(target_matches(t[0], {name}) for t in jetbrains_all):
            print(f"unknown editor name: {name}", file=sys.stderr)

    candidates = vscode + jetbrains
    if not candidates:
        print("no install target found: no VS Code-family editor config dirs "
              f"(looked under {user_data_root()}"
              + (", ~/.var/app, ~/snap" if SYSTEM == "Linux" else "")
              + "), no JetBrains IDE config dirs "
              f"(looked under {', '.join(map(str, resolve_keymap.jetbrains_config_homes())) or 'no config home'})",
              file=sys.stderr)
        return 1

    selected = select_targets(
        candidates, args, default=vscode,
        preselected=[i for i, t in enumerate(candidates) if t in vscode])
    if selected is None:
        print("nothing selected - aborted.")
        return 0
    if not selected:
        print("no IDE selected - nothing to do.")
        return 0

    jetbrains_dsts = {t[2] for t in jetbrains}
    selected_vscode = [t for t in selected if t[2] not in jetbrains_dsts]
    selected_jetbrains = [t for t in selected if t[2] in jetbrains_dsts]

    src = Path(args.file)
    if selected_vscode and not src.is_file():
        raise SystemExit(f"{src} missing - run:  python3 generate.py")
    resolved = None
    if selected_jetbrains:
        try:
            resolved = jb_keymap.find_resolved_file(args.resolved, ROOT / "source")
        except SystemExit as exc:
            if not args.dry_run:
                raise
            print(f"note: {exc}", file=sys.stderr)

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    wrote_vscode = wrote_jetbrains = 0
    for _folder, label, dst in selected_vscode:
        if args.dry_run:
            print(f"would write : {dst}   ({label})")
            wrote_vscode += 1
            continue
        if dst.exists():
            backup = dst.with_name(f"keybindings.json.bak-{stamp}")
            shutil.copy2(dst, backup)
            print(f"backup      : {backup}")
        shutil.copyfile(src, dst)
        print(f"wrote       : {dst}   ({label})")
        wrote_vscode += 1

    for _folder, label, keymaps_dir in selected_jetbrains:
        if resolved is None:  # dry-run without a resolved keymap: name is not known yet
            print(f"would write : {keymaps_dir}/<keymap> (ported).xml   ({label})")
            wrote_jetbrains += 1
            continue
        dst = jb_keymap.install_keymap(resolved, keymaps_dir, dry_run=True, stamp=stamp)
        if args.dry_run:
            print(f"would write : {dst}   ({label})")
            wrote_jetbrains += 1
            continue
        existed = dst.exists()
        jb_keymap.install_keymap(resolved, keymaps_dir, dry_run=False, stamp=stamp)
        if existed:
            print(f"backup      : {dst.with_name(f'{dst.name}.bak-{stamp}')}")
        print(f"wrote       : {dst}   ({label})")
        wrote_jetbrains += 1

    if not args.dry_run:
        if wrote_vscode:
            print(f"\ndone - {wrote_vscode} editor(s). Reload each window "
                  f"(Developer: Reload Window) to pick up the changes.")
        if wrote_jetbrains:
            print(f"\ndone - {wrote_jetbrains} JetBrains IDE(s). Reopen Settings → Keymap "
                  f"(restart a running IDE) and select the \"(ported)\" keymap.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
