"""Key-conflict handling in generate.py:
  _when_disjoint                     - mutually-exclusive `when` detection
  resolve_conflicts_by_keymap_order  - earlier keymap action keeps the key
  find_key_conflicts                 - classify what is left as hard / soft
"""

import unittest

import generate


class WhenDisjoint(unittest.TestCase):
    def test_negation_pair_is_disjoint(self):
        self.assertTrue(generate._when_disjoint("terminalFocus", "!terminalFocus"))

    def test_negation_pair_inside_conjunction(self):
        self.assertTrue(
            generate._when_disjoint("!inDebugMode && !terminalFocus", "inDebugMode")
        )

    def test_empty_clause_overlaps_everything(self):
        self.assertFalse(generate._when_disjoint("", "editorFocus"))

    def test_unrelated_clauses_are_not_disjoint(self):
        self.assertFalse(generate._when_disjoint("editorFocus", "editorTextFocus"))


class ResolveByKeymapOrder(unittest.TestCase):
    def test_earlier_action_keeps_the_key(self):
        gen = [
            {"key": "ctrl+-", "command": "editor.fold", "_src": 3},
            {"key": "ctrl+-", "command": "editor.foldAll", "_src": 9},
        ]
        kept, dropped = generate.resolve_conflicts_by_keymap_order(gen)
        self.assertEqual([e["command"] for e in kept], ["editor.fold"])
        self.assertEqual(dropped, [("ctrl+-", "editor.fold", "editor.foldAll")])

    def test_input_order_does_not_matter_only_src(self):
        gen = [
            {"key": "f7", "command": "later", "_src": 50},
            {"key": "f7", "command": "earlier", "_src": 10},
        ]
        kept, dropped = generate.resolve_conflicts_by_keymap_order(gen)
        self.assertEqual([e["command"] for e in kept], ["earlier"])
        self.assertEqual(dropped, [("f7", "earlier", "later")])

    def test_disjoint_when_keeps_both(self):
        gen = [
            {"key": "f7", "command": "a", "when": "inDebugMode", "_src": 1},
            {"key": "f7", "command": "b", "when": "!inDebugMode", "_src": 2},
        ]
        kept, dropped = generate.resolve_conflicts_by_keymap_order(gen)
        self.assertEqual({e["command"] for e in kept}, {"a", "b"})
        self.assertEqual(dropped, [])

    def test_removal_entries_pass_through_untouched(self):
        gen = [
            {"key": "ctrl+-", "command": "editor.fold", "_src": 1},
            {"key": "ctrl+-", "command": "-something.else", "_src": 2},
        ]
        kept, dropped = generate.resolve_conflicts_by_keymap_order(gen)
        self.assertEqual([e["command"] for e in kept], ["editor.fold", "-something.else"])
        self.assertEqual(dropped, [])

    def test_same_command_twice_is_not_a_conflict(self):
        gen = [
            {"key": "ctrl+k", "command": "same", "_src": 1},
            {"key": "ctrl+k", "command": "same", "_src": 2},
        ]
        _, dropped = generate.resolve_conflicts_by_keymap_order(gen)
        self.assertEqual(dropped, [])


class FindKeyConflicts(unittest.TestCase):
    def test_generated_only_clash_is_hard(self):
        gen = [
            {"key": "f7", "command": "a"},
            {"key": "f7", "command": "b"},
        ]
        hard, soft = generate.find_key_conflicts(gen, [])
        self.assertEqual([k for k, _ in hard], ["f7"])
        self.assertEqual(soft, [])

    def test_overrides_participating_clash_is_soft(self):
        gen = [{"key": "ctrl+s", "command": "workbench.action.files.saveAll"}]
        base = [{"key": "ctrl+s", "command": "workbench.action.files.save"}]
        hard, soft = generate.find_key_conflicts(gen, base)
        self.assertEqual(hard, [])
        self.assertEqual([k for k, _ in soft], ["ctrl+s"])

    def test_disjoint_when_is_not_a_conflict(self):
        gen = [
            {"key": "f7", "command": "a", "when": "inDebugMode"},
            {"key": "f7", "command": "b", "when": "!inDebugMode"},
        ]
        hard, soft = generate.find_key_conflicts(gen, [])
        self.assertEqual((hard, soft), ([], []))

    def test_removals_are_ignored(self):
        gen = [
            {"key": "ctrl+y", "command": "redo"},
            {"key": "ctrl+y", "command": "-editor.action.deleteLines"},
        ]
        hard, soft = generate.find_key_conflicts(gen, [])
        self.assertEqual((hard, soft), ([], []))


if __name__ == "__main__":
    unittest.main()
