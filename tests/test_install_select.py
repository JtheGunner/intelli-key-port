#!/usr/bin/env python3
"""
Tests for the interactive IDE picker wired into install.py.

    python3 -m unittest discover -s tests
"""

from __future__ import annotations

import os
import sys
import types
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import install  # noqa: E402
import prompt_select  # noqa: E402


def _args(**over):
    base = dict(only=None, dry_run=False, file="x")
    base.update(over)
    return types.SimpleNamespace(**base)


FAKE = [
    ("Code", "VS Code", Path("/tmp/a/Code/User/keybindings.json")),
    ("Cursor", "Cursor", Path("/tmp/a/Cursor/User/keybindings.json")),
    ("VSCodium", "VSCodium", Path("/tmp/a/VSCodium/User/keybindings.json")),
]


class SelectTargets(unittest.TestCase):
    def test_only_skips_prompt(self):
        self.assertEqual(install.select_targets(FAKE, _args(only=["Code"])), FAKE)

    def test_dry_run_skips_prompt(self):
        self.assertEqual(install.select_targets(FAKE, _args(dry_run=True)), FAKE)

    def test_single_target_skips_prompt(self):
        self.assertEqual(install.select_targets(FAKE[:1], _args()), FAKE[:1])

    def test_non_tty_falls_back_to_all(self):
        # Under the test runner stdin is not a tty -> choose() raises
        # PromptUnavailable, which select_targets swallows.
        self.assertEqual(install.select_targets(FAKE, _args()), FAKE)

    def test_prompt_unavailable_falls_back_to_all(self):
        self._patch_choose(lambda *a, **k: (_ for _ in ()).throw(prompt_select.PromptUnavailable()))
        self._force_tty()
        self.assertEqual(install.select_targets(FAKE, _args()), FAKE)

    def test_cancel_returns_none(self):
        self._patch_choose(lambda *a, **k: None)
        self._force_tty()
        self.assertIsNone(install.select_targets(FAKE, _args()))

    def test_subset_is_mapped_by_index(self):
        self._patch_choose(lambda *a, **k: [0, 2])
        self._force_tty()
        self.assertEqual(install.select_targets(FAKE, _args()), [FAKE[0], FAKE[2]])

    # -- helpers -----------------------------------------------------------
    def _patch_choose(self, fn):
        real = install.choose
        install.choose = fn
        self.addCleanup(lambda: setattr(install, "choose", real))

    def _force_tty(self):
        real = sys.stdin.isatty, sys.stdout.isatty
        sys.stdin.isatty = lambda: True
        sys.stdout.isatty = lambda: True
        self.addCleanup(lambda: (setattr(sys.stdin, "isatty", real[0]),
                                 setattr(sys.stdout, "isatty", real[1])))


class Choose(unittest.TestCase):
    def test_empty_options_return_empty_before_tty_check(self):
        self.assertEqual(prompt_select.choose([]), [])

    def test_non_tty_raises(self):
        with self.assertRaises(prompt_select.PromptUnavailable):
            prompt_select.choose(["a", "b"])


class RowStyling(unittest.TestCase):
    def test_checked_row_is_colored_by_default(self):
        row = prompt_select._row(pointer_on=True, checked=True, label="VS Code")
        self.assertIn("\x1b[32m", row)   # green box
        self.assertIn("\x1b[0m", row)    # reset
        self.assertIn("VS Code", row)

    def test_unchecked_box_is_dim(self):
        self.assertIn("\x1b[2m",
                      prompt_select._row(pointer_on=False, checked=False, label="x"))

    def test_no_color_env_strips_ansi(self):
        out = __import__("subprocess").run(
            [sys.executable, "-c",
             "import prompt_select as p;"
             "print(repr(p._row(True, True, 'x')))"],
            env={**os.environ, "NO_COLOR": "1"},
            cwd=str(Path(__file__).resolve().parent.parent),
            capture_output=True, text=True, check=True,
        ).stdout
        self.assertNotIn("\\x1b", out)


class MainRegression(unittest.TestCase):
    def test_dry_run_lists_all_without_prompting(self):
        real_discover = install.discover_targets
        real_choose = install.choose
        install.discover_targets = lambda wanted: FAKE
        install.choose = lambda *a, **k: self.fail("choose() must not run on --dry-run")
        self.addCleanup(lambda: setattr(install, "discover_targets", real_discover))
        self.addCleanup(lambda: setattr(install, "choose", real_choose))

        src = Path(__file__).resolve().parent.parent / "prompt_select.py"  # any real file
        self.assertEqual(install.main(["--dry-run", "--file", str(src)]), 0)


@unittest.skipUnless(sys.platform != "win32", "pty is POSIX-only")
class ChoosePtyIntegration(unittest.TestCase):
    """Drive the real curses-free picker through a pseudo-terminal."""

    def _run(self, keystrokes: list[bytes]) -> str:
        import pty
        import select
        import time

        script = (
            "import sys; sys.path.insert(0, %r);"
            "import prompt_select;"
            "r = prompt_select.choose(['one', 'two', 'three'], title='pick');"
            "sys.stderr.write('RESULT=' + repr(r) + chr(10))"
            % str(Path(__file__).resolve().parent.parent)
        )
        pid, fd = pty.fork()
        if pid == 0:  # child
            os.execv(sys.executable, [sys.executable, "-u", "-c", script])
            os._exit(1)  # pragma: no cover

        def drain(first_wait: float = 3.0, quiet: float = 0.3) -> bytes:
            """Wait up to first_wait for output, then read until a quiet gap."""
            buf = b""
            deadline = time.time() + first_wait
            while time.time() < deadline:
                ready, _, _ = select.select([fd], [], [], quiet)
                if ready:
                    try:
                        chunk = os.read(fd, 4096)
                    except OSError:
                        break
                    if not chunk:
                        break
                    buf += chunk
                    deadline = time.time() + quiet
                elif buf:
                    break
            return buf

        out = drain()  # initial render (pays the interpreter cold-start cost)
        for chunk in keystrokes:  # each escape sequence sent as one write
            os.write(fd, chunk)
            out += drain(1.0)
        os.waitpid(pid, 0)
        return out.decode(errors="replace")

    def test_down_space_enter_selects_first_and_third(self):
        # down, space (toggle "two" off), enter -> [0, 2]
        out = self._run([b"\x1b[B", b" ", b"\r"])
        self.assertIn("RESULT=[0, 2]", out)

    def test_esc_cancels(self):
        out = self._run([b"\x1b"])
        self.assertIn("RESULT=None", out)


if __name__ == "__main__":
    unittest.main()
