#!/usr/bin/env python3
"""
Tests for JetBrains install discovery across the pre-2025.3 (lib/app.jar) and
2025.3+/2026.x (split lib/*.jar module jars, no app.jar) packaging layouts.

    python3 -m unittest discover -s tests
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import resolve_keymap as rk  # noqa: E402

DEFAULT_KEYMAP_XML = b'<keymap version="1" name="$default"></keymap>'


def _tmpdir(case) -> Path:
    d = tempfile.mkdtemp()
    case.addCleanup(lambda: __import__("shutil").rmtree(d, ignore_errors=True))
    return Path(d)


def _jar(path: Path, entries: dict[str, bytes]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w") as z:
        for name, data in entries.items():
            z.writestr(name, data)


class IsIdeLib(unittest.TestCase):
    def test_missing_dir(self):
        self.assertFalse(rk.is_ide_lib(_tmpdir(self) / "nope"))

    def test_empty_dir(self):
        self.assertFalse(rk.is_ide_lib(_tmpdir(self)))

    def test_legacy_app_jar(self):
        lib = _tmpdir(self)
        (lib / "app.jar").touch()
        self.assertTrue(rk.is_ide_lib(lib))

    def test_split_core_jar(self):
        lib = _tmpdir(self)
        (lib / "intellij.platform.ide.impl.jar").touch()
        self.assertTrue(rk.is_ide_lib(lib))

    def test_any_jar_is_lenient(self):
        lib = _tmpdir(self)
        (lib / "something.jar").touch()
        self.assertTrue(rk.is_ide_lib(lib))

    def test_no_jars_at_all(self):
        lib = _tmpdir(self)
        (lib / "readme.txt").touch()
        self.assertFalse(rk.is_ide_lib(lib))


class DiscoverInstalls(unittest.TestCase):
    """Build a fake install tree for the current platform and discover it."""

    def _fake_install(self, root: Path, *, version: str, legacy: bool) -> Path:
        if rk.IS_MAC:
            home = root / "PhpStorm.app" / "Contents"
            info_dir = home / "Resources"
        else:
            home = root / f"phpstorm-{version}"
            info_dir = home
        info_dir.mkdir(parents=True, exist_ok=True)
        (info_dir / "product-info.json").write_text(json.dumps({
            "name": "PhpStorm", "version": version,
            "dataDirectoryName": f"PhpStorm{version[:6]}",
        }))
        lib = home / "lib"
        lib.mkdir(parents=True, exist_ok=True)
        if legacy:
            (lib / "app.jar").touch()
        else:  # split layout - no app.jar
            (lib / "intellij.platform.ide.impl.jar").touch()
            (lib / "util.jar").touch()
        (home / "plugins").mkdir(exist_ok=True)
        return home

    def _patch_roots(self, root: Path):
        self.addCleanup(setattr, rk, "install_search_roots", rk.install_search_roots)
        rk.install_search_roots = lambda: [root]

    def test_finds_split_layout_install(self):
        root = _tmpdir(self)
        self._fake_install(root, version="2026.2.2", legacy=False)
        self._patch_roots(root)
        installs = rk.discover_installs("PhpStorm")
        self.assertEqual(len(installs), 1, installs)
        self.assertEqual(installs[-1][0], (2026, 2, 2))

    def test_finds_legacy_layout_install(self):
        root = _tmpdir(self)
        self._fake_install(root, version="2024.3", legacy=True)
        self._patch_roots(root)
        self.assertEqual(len(rk.discover_installs("PhpStorm")), 1)

    def test_skips_dir_without_lib_jars(self):
        root = _tmpdir(self)
        home = self._fake_install(root, version="2026.2.2", legacy=False)
        for j in (home / "lib").glob("*.jar"):
            j.unlink()
        self._patch_roots(root)
        self.assertEqual(rk.discover_installs("PhpStorm"), [])


class KeymapSourceJarLayout(unittest.TestCase):
    def test_reads_builtin_from_split_core_jar(self):
        lib = _tmpdir(self)
        _jar(lib / "intellij.platform.ide.impl.jar",
             {"keymaps/$default.xml": DEFAULT_KEYMAP_XML})
        src = rk.KeymapSource(_tmpdir(self), lib, _tmpdir(self))
        self.assertTrue(src.has("$default"))
        self.assertIn(b"$default".decode(), src.get("$default"))

    def test_reads_builtin_from_legacy_app_jar(self):
        lib = _tmpdir(self)
        _jar(lib / "app.jar", {"keymaps/$default.xml": DEFAULT_KEYMAP_XML})
        src = rk.KeymapSource(_tmpdir(self), lib, _tmpdir(self))
        self.assertTrue(src.has("$default"))

    def test_falls_back_to_scanning_unknown_jar_name(self):
        lib = _tmpdir(self)
        _jar(lib / "renamed-platform-core.jar",
             {"keymaps/$default.xml": DEFAULT_KEYMAP_XML})
        src = rk.KeymapSource(_tmpdir(self), lib, _tmpdir(self))
        self.assertTrue(src.has("$default"))


if __name__ == "__main__":
    unittest.main()
