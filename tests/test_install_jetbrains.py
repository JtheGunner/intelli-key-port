#!/usr/bin/env python3
"""
Tests for JetBrains IDEs (incl. Android Studio) as install targets in install.py.

    python3 -m unittest discover -s tests
"""

from __future__ import annotations

import contextlib
import io
import shutil
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import install  # noqa: E402
import resolve_keymap as rk  # noqa: E402

RESOLVED = (
    '<keymap version="1" name="macOS">\n'
    '  <action id="Run"><keyboard-shortcut first-keystroke="ctrl R" /></action>\n'
    "</keymap>\n"
)


def _tmpdir(case) -> Path:
    d = tempfile.mkdtemp()
    case.addCleanup(lambda: shutil.rmtree(d, ignore_errors=True))
    return Path(d)


class _TtyIO(io.StringIO):
    def isatty(self):
        return True


class Env(unittest.TestCase):
    """A fake machine: one VS Code user dir, a JetBrains home, a resolved file."""

    def setUp(self):
        root = _tmpdir(self)
        self.vscode_user = root / "data" / "Code" / "User"
        self.vscode_user.mkdir(parents=True)
        self.jb_home = root / "jb"
        self.jb_home.mkdir()
        self.keybindings = root / "kb.json"
        self.keybindings.write_text("[]", encoding="utf-8")
        self.resolved = root / "macOS.resolved.xml"
        self.resolved.write_text(RESOLVED, encoding="utf-8")
        for patcher in (
            unittest.mock.patch.object(install, "SYSTEM", "Darwin"),  # no flatpak/snap probing
            unittest.mock.patch.object(install, "user_data_root", return_value=root / "data"),
            unittest.mock.patch.object(rk, "jetbrains_config_homes", return_value=[self.jb_home]),
        ):
            patcher.start()
            self.addCleanup(patcher.stop)

    def ide(self, name: str, *, sub: str = "options") -> Path:
        d = self.jb_home / name
        (d / sub).mkdir(parents=True)
        return d

    def run_main(self, *argv: str, resolved: bool = True, tty: bool = False):
        out, err = (_TtyIO() if tty else io.StringIO()), io.StringIO()
        base = ["--file", str(self.keybindings)]
        if resolved:
            base += ["--resolved", str(self.resolved)]
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = install.main([*base, *argv])
        return rc, out.getvalue(), err.getvalue()

    def empty_source_dir(self) -> None:
        patcher = unittest.mock.patch.object(install, "ROOT", _tmpdir(self))
        patcher.start()
        self.addCleanup(patcher.stop)

    def force_stdin_tty(self) -> None:
        patcher = unittest.mock.patch.object(sys.stdin, "isatty", lambda: True, create=True)
        patcher.start()
        self.addCleanup(patcher.stop)


class Discovery(Env):
    def test_discovers_ide_dirs_only(self):
        self.ide("PhpStorm2025.3")
        self.ide("Datagrip2026.2", sub="keymaps")
        self.ide("AndroidStudio2026.2.2")
        for noise in ("consentOptions", "Daemon", "acp-agents"):
            self.ide(noise)
        (self.jb_home / "GoLand2026.2").mkdir()  # IDE name, but no options/ or keymaps/
        folders = [t[0] for t in install.discover_jetbrains_targets()]
        self.assertEqual(folders, ["AndroidStudio2026.2.2", "Datagrip2026.2", "PhpStorm2025.3"])

    def test_target_tuple_shape(self):
        ide = self.ide("PhpStorm2025.3")
        folder, label, dst = install.discover_jetbrains_targets()[0]
        self.assertEqual((folder, dst), ("PhpStorm2025.3", ide / "keymaps"))
        self.assertIn("PhpStorm2025.3", label)

    def test_more_config_dir_names_are_targets(self):
        for name in ("PyCharmCE2025.3", "AndroidStudioPreview2026.1", "DataSpell2025.3", "Aqua2025.3"):
            self.ide(name)
        folders = {t[0] for t in install.discover_jetbrains_targets()}
        self.assertEqual(folders, {"PyCharmCE2025.3", "AndroidStudioPreview2026.1",
                                   "DataSpell2025.3", "Aqua2025.3"})

    def test_two_versions_listed(self):
        self.ide("PhpStorm2025.3")
        self.ide("PhpStorm2026.1")
        self.assertEqual(len(install.discover_jetbrains_targets()), 2)

    def test_target_matches_prefix_and_exact(self):
        self.assertTrue(install.target_matches("PhpStorm2025.3", {"PhpStorm"}))
        self.assertTrue(install.target_matches("PhpStorm2026.1", {"phpstorm"}))
        self.assertTrue(install.target_matches("AndroidStudio2026.2.2", {"AndroidStudio2026.2.2"}))
        self.assertFalse(install.target_matches("AndroidStudio2026.2.2", {"Code"}))


class Main(Env):
    def test_non_interactive_skips_jetbrains(self):
        ide = self.ide("AndroidStudio2026.2.2")
        rc, _, _ = self.run_main()
        self.assertEqual(rc, 0)
        self.assertEqual((self.vscode_user / "keybindings.json").read_text(encoding="utf-8"), "[]")
        self.assertFalse((ide / "keymaps").exists())

    def test_only_selects_jetbrains_and_leaves_vscode_alone(self):
        ide = self.ide("AndroidStudio2026.2.2")
        rc, out, _ = self.run_main("--only", "AndroidStudio")
        self.assertEqual(rc, 0)
        self.assertTrue((ide / "keymaps" / "macOS-ported.xml").is_file())
        self.assertFalse((self.vscode_user / "keybindings.json").exists())
        self.assertIn("Keymap", out)
        self.assertNotIn("Reload each window", out)

    def test_only_with_missing_keybindings_file_still_installs_jetbrains(self):
        ide = self.ide("PhpStorm2025.3")
        self.keybindings.unlink()
        rc, _, _ = self.run_main("--only", "PhpStorm")
        self.assertEqual(rc, 0)
        self.assertTrue((ide / "keymaps" / "macOS-ported.xml").is_file())

    def test_source_ide_original_keymap_untouched_and_backup_on_rerun(self):
        ide = self.ide("PhpStorm2025.3", sub="keymaps")
        original = ide / "keymaps" / "macOS.xml"
        original.write_bytes(b"<keymap name='macOS'/>")
        self.run_main("--only", "PhpStorm")
        self.run_main("--only", "PhpStorm")
        self.assertEqual(original.read_bytes(), b"<keymap name='macOS'/>")
        names = sorted(p.name for p in (ide / "keymaps").iterdir())
        self.assertEqual(len([n for n in names if ".xml.bak-" in n]), 1, names)
        self.assertIn("macOS-ported.xml", names)

    def test_two_versions_both_installed_by_prefix(self):
        a, b = self.ide("PhpStorm2025.3"), self.ide("PhpStorm2026.1")
        self.run_main("--only", "PhpStorm")
        self.assertTrue((a / "keymaps" / "macOS-ported.xml").is_file())
        self.assertTrue((b / "keymaps" / "macOS-ported.xml").is_file())

    def test_dry_run_lists_both_families_and_writes_nothing(self):
        ide = self.ide("AndroidStudio2026.2.2")
        rc, out, _ = self.run_main("--dry-run")
        self.assertEqual(rc, 0)
        self.assertIn(str(self.vscode_user / "keybindings.json"), out)
        self.assertIn(str(ide / "keymaps" / "macOS-ported.xml"), out)
        self.assertFalse((ide / "keymaps").exists())
        self.assertFalse((self.vscode_user / "keybindings.json").exists())

    def test_dry_run_without_resolved_file_still_previews(self):
        ide = self.ide("PhpStorm2026.3")
        self.empty_source_dir()
        rc, out, _ = self.run_main("--dry-run", resolved=False)
        self.assertEqual(rc, 0)
        self.assertIn(str(self.vscode_user / "keybindings.json"), out)
        self.assertIn(str(ide / "keymaps"), out)
        self.assertFalse((ide / "keymaps").exists())

    def test_real_install_without_resolved_file_exits(self):
        self.ide("PhpStorm2026.3")
        self.empty_source_dir()
        with self.assertRaises(SystemExit):
            self.run_main("--only", "PhpStorm", resolved=False)

    def test_picker_preselects_only_vscode_family_targets(self):
        self.ide("AndroidStudio2026.2.2")
        seen = {}

        def fake_choose(labels, **kwargs):
            seen["labels"], seen["preselected"] = list(labels), kwargs.get("preselected")
            return [0]

        with unittest.mock.patch.object(install, "choose", fake_choose):
            self.force_stdin_tty()
            rc, _, _ = self.run_main(tty=True)
        self.assertEqual(rc, 0)
        self.assertEqual(len(seen["labels"]), 2)
        self.assertEqual(list(seen["preselected"]), [0])

    def test_unknown_only_name_warns(self):
        _, _, err = self.run_main("--only", "NoSuchEditor")
        self.assertIn("unknown editor name: NoSuchEditor", err)

    def test_known_jetbrains_only_name_does_not_warn(self):
        self.ide("AndroidStudio2026.2.2")
        _, _, err = self.run_main("--only", "AndroidStudio")
        self.assertNotIn("unknown editor name", err)

    def test_vscode_only_flow_unchanged(self):
        (self.vscode_user / "keybindings.json").write_text("old", encoding="utf-8")
        rc, out, _ = self.run_main()
        self.assertEqual(rc, 0)
        self.assertIn("backup      :", out)
        self.assertIn("wrote       :", out)
        self.assertIn("Reload each window", out)
        self.assertEqual((self.vscode_user / "keybindings.json").read_text(encoding="utf-8"), "[]")

    def test_nothing_found_message_names_both_families(self):
        shutil.rmtree(self.vscode_user.parent)
        rc, _, err = self.run_main()
        self.assertEqual(rc, 1)
        self.assertIn("VS Code", err)
        self.assertIn("JetBrains", err)


if __name__ == "__main__":
    unittest.main()
