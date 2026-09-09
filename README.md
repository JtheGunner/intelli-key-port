# phpstorm-keymap-port

Port a customized **PhpStorm keymap** to **VS Code** and **Antigravity**
(both variants), reproducibly - by reading PhpStorm's own keymap files, not
a third-party export.

## Why the naive routes failed

**`isudox.vscode-jetbrains-keybindings` XML import** — not a real porter:
~232 of 378 entries were invisible `-command` removals; ~30 kept raw Java
AWT key tokens VS Code silently drops; many `command`s were IntelliJ ids
with no VS Code equivalent. Net: a handful of working bindings.

**`intellij-keymap-xml-exporter`** — flattens the keymap but mangles keys
it cannot serialize. It turned `ctrl §` (PhpStorm stores it as the
extended key code `ctrl #10000a7`, `0xA7` = section sign) into
`ctrl UNKNOWN`. So we don't use it either.

## How this works instead

```
resolve_keymap.py  ──reads──►  ~/Library/Application Support/JetBrains/PhpStorm*/keymaps/<user>.xml
        │                      /Applications/PhpStorm.app  →  app.jar keymaps/  +  plugin META-INF/*.xml
        │            walks the parent chain  $default → Default for XWin → <user>
        │            + folds in plugin-registered defaults (Git etc.)
        ▼
source/<user>.resolved.xml     flat, fully-inherited keymap (committed, diffable)
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

`generate.py` prefers `source/*.resolved.xml`; if there is none it falls
back to any hand-dropped `source/*.xml` with a `<keymap>` root (a raw
export still works, it just carries the exporter's `UNKNOWN` bug).

The `vendor/` files are copied from the installed
`k--kato.intellij-idea-keybindings` **v1.7.7**
(<https://github.com/kasecato/vscode-intellij-idea-keybindings>) so the
generator is self-contained and version-pinned.

Extended key codes (`#100XXXX`) are decoded to their character and mapped
to a VS Code **scan-code** token (`§`/`°` → `[Backquote]`, ISO `<`/`>` →
`[IntlBackslash]`) so the binding follows the physical key on any layout.

### The extension stays installed

`k--kato.intellij-idea-keybindings` remains the base layer in all three
editors. It covers the IntelliJ actions with **no** entry in its command
table (tool windows, refactorings, most navigation) — see `report.md` →
*"No VS Code command mapping"* for the exact list from the last run.

Caveat: on macOS the extension binds those residual actions to **Cmd**,
not Ctrl. Everything this port maps is re-bound to **Ctrl** (PC muscle
memory, matching the resolved keymap) and wins because user keybindings
load after extension keybindings. To pull more actions onto Ctrl, add
them to `manualActionCommand` in `overrides.jsonc` and re-generate.

## Usage

```sh
./build.sh              # resolve_keymap.py + generate.py
./install.sh            # back up + deploy to the 3 editors, then reload windows
```

`build.sh` passes extra args to `resolve_keymap.py`:

```sh
./build.sh --product IntelliJIdea          # a different JetBrains IDE
./build.sh --keymap "my other keymap"      # a specific keymap by name
./build.sh --app "/Applications/PhpStorm 2025.2.app"
```

No PhpStorm on this machine? Drop a raw *Export Keymap* `.xml` into
`source/` (any name) and run `python3 generate.py` directly.

## Known trade-offs (edit `overrides.jsonc` to change)

Generated bare `ctrl+<letter>` bindings carry a `!terminalFocus` guard so
the integrated terminal keeps its readline control chars (Ctrl+R, Ctrl+P,
Ctrl+T, …). The `overrides.jsonc` entries win over the generated block.

| Key | This port | Note |
|-----|-----------|------|
| `ctrl+numpad +` / `-` | zoom in / out | fold-all loses the bare-numpad combo; **fold still works on `ctrl+=` / `ctrl+-`** and fold-all on `ctrl+shift+=` / `ctrl+shift+-` |
| `ctrl+y` | redo | matches this export (`$Redo` / `Editor Redo`); `ctrl+shift+z` also redoes |
| `ctrl+s` | save current file | the export puts *Save All* here; VS Code auto-save covers the rest |
| `ctrl+,` | Settings UI | export also has `ctrl+alt+s`; both open settings |
| `f7` | Step Into (debug) / Next Diff | both come straight from the export; no-op outside their context |
| `ctrl+shift+c` | terminal: copy selection / editor: copy file path | different `when` contexts, no real clash |
| `shift+enter` | terminal: send `ESC CR` (multiline in Claude Code etc.) / editor: new line below | different `when` contexts |
| `ctrl+§` (`[Backquote]`) | comment line | decoded from `ctrl #10000a7`; also on `ctrl+/` |
| mouse shortcuts (~14) | **not ported** | `keybindings.json` has no mouse bindings — see `report.md` |

## Verify after install

Reload each editor window, then spot-check (editor focused, **not** the terminal):

- `ctrl+d` → duplicate line
- `ctrl+y` → redo
- `ctrl+w` / `ctrl+shift+w` → expand / shrink selection
- `ctrl+b` → go to definition, `ctrl+alt+b` → go to implementation
- `ctrl+alt+l` → reformat code
- `ctrl+§` and `ctrl+/` → comment line
- `ctrl+shift+a` → Find Action (command palette)
- `ctrl+o` → Go to Class, `ctrl+shift+o` → Go to File
- `ctrl+k` → commit, `ctrl+alt+k` → commit & push, `ctrl+t` → update project (from plugin defaults)
- `alt+1` / `alt+3` / `alt+9` → Explorer / Search / SCM
- In the **terminal**: `ctrl+c`, `ctrl+d`, `ctrl+r`, `ctrl+p` still behave as shell control chars.

Then open **Preferences: Open Keyboard Shortcuts** and filter `@source:user`
— you should now see ~177 entries, not a dozen.
