#!/usr/bin/env python3
"""
Override layers in generate.py:
  resolve_layer     - `--layer NAME` -> layers/NAME.jsonc, `--layer PATH` -> that file
  load_overrides    - base overrides.jsonc + layers, stacked in order
  find_key_conflicts - a clash involving any curated layer is soft
  keymap_chain / is_ctrl_keymap - windows-keymap hint from the resolved chain
  translate_token   - a Ctrl+Shift+Alt+Cmd combo ports verbatim

    python3 -m unittest discover -s tests
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import generate  # noqa: E402


def _write(dir_: Path, name: str, text: str) -> Path:
    p = dir_ / name
    p.write_text(text, encoding="utf-8")
    return p


class ResolveLayer(unittest.TestCase):
    def test_name_resolves_to_bundled_layer(self):
        self.assertEqual(
            generate.resolve_layer("windows-keymap"),
            generate.LAYERS_DIR / "windows-keymap.jsonc",
        )

    def test_path_resolves_to_that_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = _write(Path(tmp), "mine.jsonc", "{}")
            self.assertEqual(generate.resolve_layer(str(p)), p.resolve())

    def test_unknown_name_fails_and_lists_bundled_layers(self):
        with self.assertRaises(SystemExit) as cm:
            generate.resolve_layer("no-such-layer")
        self.assertIn("windows-keymap", str(cm.exception.code))

    def test_missing_path_fails(self):
        with self.assertRaises(SystemExit):
            generate.resolve_layer("/nonexistent/dir/mine.jsonc")


class LoadOverrides(unittest.TestCase):
    def test_no_layers_is_the_base_alone(self):
        ov = generate.load_overrides([])
        base = generate.load_jsonc(generate.OVERRIDES_PATH)
        self.assertEqual(ov.layers, ["overrides.jsonc"])
        self.assertEqual(len(ov.entries), len(base["entries"]))
        self.assertEqual(ov.drop_actions, set(base["dropActions"]))

    def test_layer_entries_come_after_base_so_they_win(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = _write(Path(tmp), "mine.jsonc",
                       '{ "entries": [ { "key": "f2", "command": "mine" } ] }')
            ov = generate.load_overrides([str(p)])
        self.assertEqual(ov.entries[-1]["command"], "mine")
        self.assertEqual(ov.entries[-1]["_layer"], "mine.jsonc")
        self.assertEqual(ov.layers, ["overrides.jsonc", "mine.jsonc"])

    def test_later_layer_wins_manual_action_command_and_drops_accumulate(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = _write(Path(tmp), "a.jsonc",
                       '{ "manualActionCommand": { "X": "a.cmd" }, "dropActions": ["A"] }')
            b = _write(Path(tmp), "b.jsonc",
                       '{ "manualActionCommand": { "X": "b.cmd" }, "dropActions": ["B"] }')
            ov = generate.load_overrides([str(a), str(b)])
        self.assertEqual(ov.manual_action_command["X"], "b.cmd")
        self.assertTrue({"A", "B"} <= ov.drop_actions)
        self.assertEqual(ov.drop_origin["B"], "b.jsonc")

    def test_unknown_top_level_key_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = _write(Path(tmp), "typo.jsonc", '{ "entry": [] }')
            with self.assertRaises(SystemExit) as cm:
                generate.load_overrides([str(p)])
        self.assertIn("entry", str(cm.exception.code))

    def test_entry_without_command_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = _write(Path(tmp), "bad.jsonc", '{ "entries": [ { "key": "f2" } ] }')
            with self.assertRaises(SystemExit):
                generate.load_overrides([str(p)])

    def test_same_layer_twice_is_rejected(self):
        with self.assertRaises(SystemExit):
            generate.load_overrides(["windows-keymap", "windows-keymap"])


class BaseStaysNeutral(unittest.TestCase):
    """Without --layer the output carries no keymap-family or Karabiner assumptions."""

    def test_base_has_no_cmd_removals_or_ctrl_clipboard(self):
        keys = {e["key"] for e in generate.load_overrides([]).entries}
        for key in ("cmd+c", "cmd+s", "ctrl+c", "ctrl+v", "ctrl+y", "alt+left", "home"):
            self.assertNotIn(key, keys)

    def test_base_keeps_tab_switching_actions(self):
        drops = generate.load_overrides([]).drop_actions
        self.assertFalse({"NextTab", "PreviousTab"} & drops)


class ConflictOrigin(unittest.TestCase):
    def test_clash_with_any_curated_layer_is_soft(self):
        gen = [{"key": "ctrl+e", "command": "a"}]
        curated = [{"key": "ctrl+e", "command": "b", "_layer": "layer:windows-keymap"}]
        hard, soft = generate.find_key_conflicts(gen, curated)
        self.assertEqual(hard, [])
        self.assertEqual(soft[0][1][1][2], "layer:windows-keymap")


class KeymapChain(unittest.TestCase):
    def _chain(self, header: str) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            p = _write(Path(tmp), "k.xml", header + '\n<keymap version="1" name="x"/>\n')
            return generate.keymap_chain(p)

    def test_chain_is_read_from_the_resolver_header(self):
        chain = self._chain("<!-- inheritance chain: $default -> Default for XWin -> mine -->")
        self.assertEqual(chain, ["$default", "Default for XWin", "mine"])

    def test_raw_export_has_no_chain(self):
        self.assertEqual(self._chain("<!-- exported by hand -->"), [])

    def test_windows_family_is_ctrl_based(self):
        self.assertTrue(generate.is_ctrl_keymap(["$default", "Default for XWin", "mine"]))

    def test_macos_family_is_not_ctrl_based(self):
        self.assertFalse(generate.is_ctrl_keymap(["$default", "Mac OS X", "Mac OS X 10.5+"]))

    def test_unknown_chain_is_not_ctrl_based(self):
        self.assertFalse(generate.is_ctrl_keymap([]))


class HyperKeystroke(unittest.TestCase):
    def test_all_four_modifiers_translate_in_vscode_order(self):
        self.assertEqual(
            generate.translate_token("shift ctrl alt meta 3", {}),
            "ctrl+shift+alt+cmd+3",
        )


if __name__ == "__main__":
    unittest.main()
