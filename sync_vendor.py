#!/usr/bin/env python3
"""
Refresh vendor/kkato/ from the k--kato.intellij-idea-keybindings extension
installed on this machine, and record its version in vendor/kkato/VERSION.

vendor/kkato/ is the offline fallback used when no editor / no extension is
present. The build normally reads the installed extension live (see kkato.py);
run this only to update that pinned fallback.

    python3 sync_vendor.py          # or:  ./port.py --sync-vendor
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import kkato


def main(argv: list[str] | None = None) -> int:
    import argparse
    argparse.ArgumentParser(description="Refresh vendor/kkato/ from the installed extension.").parse_args(argv)

    hit = kkato.installed_resource_dir()
    if not hit:
        print("no k--kato.intellij-idea-keybindings extension installed - "
              "cannot refresh vendor/kkato/. Install it in VS Code / Cursor / … first:\n"
              "  code --install-extension k--kato.intellij-idea-keybindings",
              file=sys.stderr)
        return 1
    res_dir, version = hit
    before = kkato.vendored_version()

    changed = 0
    for rel in kkato.RESOURCE_FILES:
        src = res_dir / rel
        dst = kkato.VENDOR / rel
        if not src.is_file():
            print(f"  skip (not in extension): {rel}", file=sys.stderr)
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        old = dst.read_bytes() if dst.is_file() else None
        new = src.read_bytes()
        if old != new:
            shutil.copyfile(src, dst)
            changed += 1
            print(f"  updated  {rel}")
        else:
            print(f"  same     {rel}")

    (kkato.VENDOR / "VERSION").write_text(version + "\n", encoding="utf-8")
    print(f"\nvendor/kkato pinned: v{before} -> v{version}  "
          f"({changed} file(s) changed)  source: {res_dir.parent.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
