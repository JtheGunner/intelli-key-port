#!/usr/bin/env python3
"""
Install a resolved JetBrains keymap (source/*.resolved.xml) into another
JetBrains IDE (including Android Studio) as a new, selectable keymap.

The installed keymap is named "<source name> (ported)" so it never replaces the
original; an existing file of that name is backed up first.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path
from xml.sax.saxutils import quoteattr, unescape

PORTED_SUFFIX = " (ported)"

_KEYMAP_NAME = re.compile(r"""(<keymap\b[^>]*?\bname=)(?:"([^"]*)"|'([^']*)')""")
_ENTITIES = {"&quot;": '"', "&apos;": "'"}


def ported_name(source_name: str) -> str:
    return f"{source_name}{PORTED_SUFFIX}"


def target_filename(name: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-") or "keymap"
    return f"{safe}.xml"


def read_keymap_name(xml_text: str) -> str:
    match = _KEYMAP_NAME.search(xml_text)
    if not match:
        raise ValueError("no <keymap name=...> found")
    raw = match.group(2) if match.group(2) is not None else match.group(3)
    return unescape(raw, _ENTITIES)


def render_ported_xml(xml_text: str) -> tuple[str, str]:
    """Return (xml with the keymap renamed to "<name> (ported)", that new name)."""
    new_name = ported_name(read_keymap_name(xml_text))
    rewritten = _KEYMAP_NAME.sub(
        lambda m: m.group(1) + quoteattr(new_name), xml_text, count=1)
    return rewritten, new_name


def find_resolved_file(explicit: str | None, source_dir: Path) -> Path:
    if explicit:
        path = Path(explicit).expanduser()
        if not path.is_file():
            raise SystemExit(f"--resolved file not found: {path}")
        return path
    candidates = sorted(source_dir.glob("*.resolved.xml"))
    if len(candidates) == 1:
        return candidates[0]
    if not candidates:
        raise SystemExit(
            f"no *.resolved.xml in {source_dir} - run resolve_keymap.py or pass --resolved")
    raise SystemExit(
        "several resolved keymaps found, pass --resolved PATH:\n  "
        + "\n  ".join(p.name for p in candidates))


def install_keymap(resolved: Path, keymaps_dir: Path, *, dry_run: bool, stamp: str) -> Path:
    """Write the ported keymap into `keymaps_dir`; return its destination path."""
    xml, name = render_ported_xml(resolved.read_text(encoding="utf-8"))
    dst = keymaps_dir / target_filename(name)
    if dry_run:
        return dst
    keymaps_dir.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        shutil.copy2(dst, dst.with_name(f"{dst.name}.bak-{stamp}"))
    dst.write_text(xml, encoding="utf-8")
    return dst
