# phpstorm-keymap-port

Port a **PhpStorm "Windows" keymap** (with personal customizations) to
**VS Code** and **Antigravity** (both variants), reproducibly.

## Why the naive route failed

`Windows.xml` was run through the `isudox.vscode-jetbrains-keybindings`
XML importer. That importer is not a real keymap porter:

- ~232 of 378 emitted entries were `-command` **removals** (they only
  unbind VS Code defaults, invisible in the shortcut list).
- ~30 entries kept raw Java AWT key tokens (`BACK_SPACE`, `PAGE_DOWN`,
  `SUBTRACT`, `MINUS`, `SLASH`, `ctrl+UNKNOWN`, …) that VS Code cannot
  parse and silently drops.
- Many `command`s were IntelliJ action ids with no VS Code equivalent, so
  even the entries that loaded did nothing.
- Two competing keymap extensions were installed at once
  (`isudox.*` **and** `k--kato.intellij-idea-keybindings`).

Net result: a handful of working bindings out of hundreds.

## How this works instead

```
source/Windows.xml            PhpStorm export = source of truth
        │
        ▼
generate.py  ──uses──►  vendor/ActionIdCommandMapping.json   (IntelliJ action → VS Code command)
                        vendor/KeystrokeKeyMapping.json       (AWT key token → VS Code key)
                        vendor/default-Windows-VSCode.json    ("already shipped by extension")
        │
        ├─ overrides.jsonc   curated layer: terminal-signal guards, `-cmd` removals,
        │                    stale/missing action→command fixes, drop-list
        ▼
keybindings.generated.json    generated block  +  overrides.jsonc "entries" (appended LAST → win)
report.md                     what mapped / was already covered / has no VS Code command / mouse
        │
        ▼
install.sh   →  ~/Library/Application Support/{Code, Antigravity, Antigravity IDE}/User/keybindings.json
```

The `vendor/` files are copied from the installed
`k--kato.intellij-idea-keybindings` **v1.7.7**
(<https://github.com/kasecato/vscode-intellij-idea-keybindings>) so the
generator is self-contained and version-pinned.

### The extension stays installed

`k--kato.intellij-idea-keybindings` remains the base layer in all three
editors. It covers the ~430 IntelliJ actions that have **no** entry in
its 134-row command table (tool windows, refactorings, most navigation) —
see `report.md` → *"No VS Code command mapping"*.

Caveat: on macOS the extension binds those residual actions to **Cmd**,
not Ctrl. Everything this port maps is re-bound to **Ctrl** (Windows
muscle memory, matching the export) and wins because user keybindings
load after extension keybindings. To pull more actions onto Ctrl, add
them to `manualActionCommand` in `overrides.jsonc` and re-generate.

## Usage

```sh
python3 generate.py     # rebuild keybindings.generated.json + report.md
./install.sh            # back up + deploy to the 3 editors, then reload windows
```

Re-export `Windows.xml` from PhpStorm (Settings → Keymap → gear → *Export
Keymap*, or the `intellij-keymap-xml-exporter`) into `source/`, then run
the two commands again.

## Known trade-offs (edit `overrides.jsonc` to change)

| Key | This port | Note |
|-----|-----------|------|
| `ctrl+numpad +` / `-` | zoom in / out | fold-all loses the bare-numpad combo; **fold still works on `ctrl+=` / `ctrl+-`** and fold-all on `ctrl+shift+=` / `ctrl+shift+-` |
| `ctrl+s` | save current file | PhpStorm's literal *Save All* is on the same key; VS Code auto-save covers the rest |
| `ctrl+shift+c` | terminal: copy selection / editor: copy file path | different `when` contexts, no real clash |
| `shift+enter` | terminal: send `ESC CR` (multiline in Claude Code etc.) / editor: new line below | different `when` contexts |
| mouse shortcuts (19) | **not ported** | `keybindings.json` has no mouse bindings — see `report.md` |
| `CONTEXT_MENU` key | dropped | no reliable VS Code equivalent |

## Verify after install

Reload each editor window, then spot-check (editor focused, **not** the terminal):

- `ctrl+d` → duplicate line
- `ctrl+y` → delete line
- `ctrl+w` / `ctrl+shift+w` → expand / shrink selection
- `shift+ctrl+right` → extend selection by word
- `ctrl+b` → go to definition
- `ctrl+alt+l` … actually `ctrl+alt+l` is reformat in PhpStorm → check `report.md` mapping
- `ctrl+shift+a` → Find Action (command palette)
- `alt+1` / `alt+3` / `alt+9` → Explorer / Search / SCM
- In the **terminal**: `ctrl+c`, `ctrl+d`, `ctrl+r` still behave as shell control chars.

Then open **Preferences: Open Keyboard Shortcuts** and filter `@source:user`
— you should now see ~170 entries, not a dozen.
