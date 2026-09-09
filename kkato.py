#!/usr/bin/env python3
"""
Locate the `k--kato.intellij-idea-keybindings` extension's `resource/` folder.

The extension is installed into every target editor, so its mapping tables and
"already shipped" skip-set are read **live from the newest installed copy**.
`vendor/kkato/` is a pinned fallback for when no editor / no extension is present
(e.g. a fresh checkout, CI, the raw-export path).

Shared by generate.py and sync_vendor.py.
"""

from __future__ import annotations

import json
import platform
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENDOR = ROOT / "vendor" / "kkato"
EXT_ID = "k--kato.intellij-idea-keybindings"

# platform.system() -> the resource/default/<dir> that matches this OS
OS_DIR = {"Darwin": "Mac", "Windows": "Windows"}.get(platform.system(), "Linux")

RESOURCE_FILES = (
    "ActionIdCommandMapping.json",
    "KeystrokeKeyMapping.json",
    "default/Windows/VSCode.json",
    "default/Mac/VSCode.json",
    "default/Linux/VSCode.json",
)


def _extension_dirs() -> list[Path]:
    """Every VS Code-family `extensions/` dir that could hold the extension."""
    home = Path.home()
    names = (".vscode", ".vscode-insiders", ".vscode-oss", ".vscode-server",
             ".cursor", ".cursor-server", ".windsurf", ".windsurf-server",
             ".antigravity", ".antigravity-ide")
    dirs = [home / n / "extensions" for n in names]
    for fp in (home / ".var" / "app").glob("*"):            # Flatpak
        dirs += [fp / "data" / "vscode" / "extensions",
                 fp / "data" / "codium" / "extensions"]
    for sp in ("code", "code-insiders", "codium"):          # Snap
        dirs.append(home / "snap" / sp / "current" / ".vscode" / "extensions")
    return [d for d in dirs if d.is_dir()]


def _ver_tuple(text: str) -> tuple[int, ...]:
    m = re.search(r"(\d+(?:\.\d+)+)", text)
    return tuple(int(x) for x in m.group(1).split(".")) if m else (0,)


def _pkg_version(ext_dir: Path) -> str | None:
    try:
        return json.loads((ext_dir / "package.json").read_text(encoding="utf-8")).get("version")
    except (OSError, ValueError):
        return None


def installed_resource_dir() -> tuple[Path, str] | None:
    """(resource_dir, version) of the newest installed extension, or None."""
    best: tuple[tuple, Path, str] | None = None
    for exts in _extension_dirs():
        for ext in exts.glob(f"{EXT_ID}-*"):
            res = ext / "resource"
            if not (res / "ActionIdCommandMapping.json").is_file():
                continue
            ver = _pkg_version(ext) or ".".join(map(str, _ver_tuple(ext.name)))
            key = _ver_tuple(ver)
            if best is None or key > best[0]:
                best = (key, res, ver)
    return (best[1], best[2]) if best else None


def vendored_version() -> str:
    p = VENDOR / "VERSION"
    return p.read_text(encoding="utf-8").strip() if p.is_file() else "?"


def resolve() -> tuple[Path, str, str]:
    """(resource_dir, version, source_label) - installed extension preferred."""
    hit = installed_resource_dir()
    if hit:
        return hit[0], hit[1], f"installed ({hit[0].parent.name})"
    return VENDOR, vendored_version(), "vendored fallback"


def skip_set_path(resource_dir: Path) -> Path:
    """resource/default/<OS>/VSCode.json for this platform."""
    return resource_dir / "default" / OS_DIR / "VSCode.json"
