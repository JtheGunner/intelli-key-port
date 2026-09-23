"""`when` clauses on generated bindings (generate.binding_when).

A binding without `when` is active everywhere in VS Code and swallows its key
even where the command is a no-op - e.g. a bare `tab` bound to a suggest-widget
command kills indentation and inline (AI) completion acceptance.
"""

import unittest

import generate


class BindingWhen(unittest.TestCase):
    def test_suggest_accept_is_scoped_to_the_suggest_widget(self):
        terms = generate._when_terms(
            generate.binding_when("acceptAlternativeSelectedSuggestion", "tab"))
        self.assertIn("suggestWidgetVisible", terms)
        self.assertIn("!inlineEditIsVisible", terms)

    def test_every_suggest_accept_command_is_scoped(self):
        for cmd in ("acceptSelectedSuggestion", "acceptAlternativeSelectedSuggestion"):
            with self.subTest(cmd=cmd):
                self.assertIn("suggestWidgetVisible",
                              generate._when_terms(generate.binding_when(cmd, "ctrl+shift+enter")))

    def test_no_unreliable_focus_keys(self):
        # README: only !editorReadonly / !terminalFocus are reliable family-wide.
        for cmd in generate._COMMAND_WHEN:
            with self.subTest(cmd=cmd):
                terms = generate._when_terms(generate.binding_when(cmd, "tab"))
                self.assertFalse(terms & {"textInputFocus", "editorTextFocus"})

    def test_terminal_guard_is_combined_with_command_scope(self):
        terms = generate._when_terms(generate.binding_when("acceptSelectedSuggestion", "ctrl+j"))
        self.assertIn("suggestWidgetVisible", terms)
        self.assertIn("!terminalFocus", terms)

    def test_terminal_guard_alone_for_unscoped_command(self):
        self.assertEqual(generate.binding_when("workbench.action.quickOpen", "ctrl+e"),
                         "!terminalFocus")

    def test_unscoped_command_on_plain_key_has_no_when(self):
        self.assertEqual(generate.binding_when("workbench.action.quickOpen", "f4"), "")


if __name__ == "__main__":
    unittest.main()
