#!/usr/bin/env python3
"""
Tests for how port.py wires the resolved keymap into the install step.

    python3 -m unittest discover -s tests
"""

from __future__ import annotations

import sys
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import generate  # noqa: E402
import install  # noqa: E402
import port  # noqa: E402
import resolve_keymap  # noqa: E402


class ResolvedForwarding(unittest.TestCase):
    def setUp(self):
        self.calls: dict[str, list[str]] = {}

        def resolve_main(argv):
            self.calls["resolve"] = list(argv)
            resolve_keymap.last_output = Path("/tmp/x/source/k.resolved.xml")
            return 0

        def recorder(name):
            def fn(argv):
                self.calls[name] = list(argv)
                return 0
            return fn

        for module, name, fn in (
            (resolve_keymap, "main", resolve_main),
            (generate, "main", recorder("generate")),
            (install, "main", recorder("install")),
        ):
            patcher = unittest.mock.patch.object(module, name, fn)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.addCleanup(setattr, resolve_keymap, "last_output", resolve_keymap.last_output)

    def test_product_and_resolved_output_are_forwarded(self):
        port.main(["--product", "AndroidStudio", "--only", "PhpStorm"])
        self.assertEqual(self.calls["resolve"], ["--product", "AndroidStudio"])
        self.assertEqual(
            self.calls["install"],
            ["--only", "PhpStorm", "--resolved", "/tmp/x/source/k.resolved.xml"])

    def test_explicit_resolved_wins_over_resolve_output(self):
        port.main(["--resolved", "mine.xml"])
        self.assertEqual(self.calls["install"], ["--resolved", "mine.xml"])

    def test_skip_resolve_forwards_explicit_resolved(self):
        port.main(["--skip-resolve", "--resolved", "mine.xml"])
        self.assertNotIn("resolve", self.calls)
        self.assertEqual(self.calls["install"], ["--resolved", "mine.xml"])

    def test_skip_resolve_without_resolved_adds_nothing(self):
        resolve_keymap.last_output = None
        port.main(["--skip-resolve"])
        self.assertEqual(self.calls["install"], [])


if __name__ == "__main__":
    unittest.main()
