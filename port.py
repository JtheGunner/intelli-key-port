#!/usr/bin/env python3
"""
One command for the whole flow:  resolve the active JetBrains keymap  ->
generate keybindings.generated.json + report.md  ->  install into the
VS Code-family editors you pick (interactive checkbox prompt when more
than one is found; --only / --dry-run / no tty skip it).

    ./port.py                        # all three steps
    ./port.py --product WebStorm     # (resolve) a different JetBrains IDE
    ./port.py --keymap macOS         # (resolve) a specific keymap
    ./port.py --only Code --dry-run  # (install) restrict / preview
    ./port.py --skip-install         # stop after generate
    ./port.py --skip-resolve         # reuse the existing source/*.resolved.xml
    ./port.py --sync-vendor          # refresh vendor/kkato/ from the installed extension, then exit

Each step is still runnable on its own:
    python3 resolve_keymap.py [--product ... --keymap ... --app ... --config-dir ...]
    python3 generate.py
    python3 install.py       [--only NAME ... --dry-run --file PATH]
    python3 sync_vendor.py

`--dry-run` previews the install only; resolve/generate always run (they just
rewrite the git-ignored build artifacts).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import generate            # noqa: E402
import install             # noqa: E402
import resolve_keymap      # noqa: E402
import sync_vendor         # noqa: E402


def _run(title: str, fn, argv: list[str]) -> None:
    bar = "=" * (len(title) + 6)
    print(f"\n{bar}\n== {title} ==\n{bar}")
    try:
        rc = fn(argv)
    except SystemExit as exc:  # argparse errors / explicit raises inside a step
        rc = exc.code
        if isinstance(rc, str):
            print(rc, file=sys.stderr)
            rc = 1
    if rc:
        sys.exit(f"\n[port] '{title}' failed (exit {rc}) - stopping.")


def build_arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    g_res = ap.add_argument_group("resolve step (see resolve_keymap.py)")
    g_res.add_argument("--product", help="JetBrains product (default: PhpStorm)")
    g_res.add_argument("--keymap", help="keymap name (default: the IDE's active keymap)")
    g_res.add_argument("--config-dir", help="explicit <Product><version> config dir")
    g_res.add_argument("--app", help="explicit IDE install dir / .app bundle")

    g_ins = ap.add_argument_group("install step (see install.py)")
    g_ins.add_argument("--only", action="append", metavar="NAME",
                       help="restrict install to this editor config-folder (repeatable)")
    g_ins.add_argument("--dry-run", action="store_true", help="preview the install")
    g_ins.add_argument("--file", help="keybindings file to install (default: the generated one)")

    g_flow = ap.add_argument_group("flow")
    g_flow.add_argument("--skip-resolve", action="store_true",
                        help="reuse the existing source/*.resolved.xml")
    g_flow.add_argument("--skip-install", action="store_true",
                        help="stop after generate")
    g_flow.add_argument("--sync-vendor", action="store_true",
                        help="refresh vendor/kkato/ from the installed extension, then exit")
    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)

    if args.sync_vendor:
        _run("sync-vendor", sync_vendor.main, [])
        return 0

    resolve_argv: list[str] = []
    for flag, val in (("--product", args.product), ("--keymap", args.keymap),
                      ("--config-dir", args.config_dir), ("--app", args.app)):
        if val:
            resolve_argv += [flag, val]

    install_argv: list[str] = []
    if args.file:
        install_argv += ["--file", args.file]
    for name in args.only or []:
        install_argv += ["--only", name]
    if args.dry_run:
        install_argv.append("--dry-run")

    if args.skip_resolve and resolve_argv:
        print(f"[port] --skip-resolve: ignoring {' '.join(resolve_argv)}", file=sys.stderr)
    if args.skip_install and install_argv:
        print(f"[port] --skip-install: ignoring {' '.join(install_argv)}", file=sys.stderr)

    if not args.skip_resolve:
        _run("resolve", resolve_keymap.main, resolve_argv)
    _run("generate", generate.main, [])
    if not args.skip_install:
        _run("install", install.main, install_argv)

    print("\n[port] done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
