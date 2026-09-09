# phpstorm-keymap-port

Port your **active JetBrains IDE keymap** — PhpStorm by default, but also
IntelliJ IDEA, WebStorm, DataGrip, PyCharm, GoLand, … — to the **VS Code
family** (VS Code, Antigravity, Cursor, VSCodium, …), reproducibly, by reading
the IDE's own keymap files rather than a third-party export. Works on
**macOS, Windows and Linux**.

Nothing here is specific to one machine or user: every path is derived at
runtime from the OS + the IDE's `product-info.json`. The only per-user file,
`source/*.resolved.xml`, is generated and git-ignored.

## Why the naive routes failed

**`isudox.vscode-jetbrains-keybindings` XML import** — not a real porter:
~232 of 378 entries were invisible `-command` removals; ~30 kept raw Java
AWT key tokens VS Code silently drops; many `command`s were IntelliJ ids
with no VS Code equivalent. Net: a handful of working bindings.

**`intellij-keymap-xml-exporter`** — flattens the keymap but mangles keys
it cannot serialize. It turned `ctrl §` (the IDE stores it as the extended
key code `ctrl #10000a7`, `0xA7` = section sign) into `ctrl UNKNOWN`.

## How this works instead

```
resolve_keymap.py
   • finds the IDE install via product-info.json          (macOS .app / Win / Linux / Toolbox)
   • finds the matching config dir via dataDirectoryName
   • reads options/[mac/]keymap.xml → <active_keymap>      (--keymap overrides)
   • walks the parent chain  $default → … → <active>
   • folds in plugin-registered defaults (Git etc.) from  plugins/**/*.jar  META-INF/*.xml
        ▼
source/<name>.resolved.xml     flat, fully-inherited keymap (per-user, git-ignored)
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
        ▼
install.py   →  <user-data>/{Code, Code - Insiders, VSCodium, Cursor, Windsurf,
                              Antigravity, Antigravity IDE}/User/keybindings.json
```

`generate.py` prefers `source/*.resolved.xml`; with none it falls back to any
hand-dropped `source/*.xml` with a `<keymap>` root (a raw export still works,
it just carries the exporter's `UNKNOWN` bug).

`vendor/` files are copied from `k--kato.intellij-idea-keybindings` **v1.7.7**
(<https://github.com/kasecato/vscode-intellij-idea-keybindings>) so the
generator is self-contained and version-pinned.

Extended key codes (`#100XXXX`) are decoded to their character and mapped to a
VS Code **scan-code** token (`§`/`°` → `[Backquote]`, ISO `<`/`>` →
`[IntlBackslash]`, German `ä`/`ö`/`ü` → `[Quote]`/`[Semicolon]`/`[BracketLeft]`,
…) so the binding follows the physical key on any layout. `resolve_keymap.py`
prints every `#100XXXX` token it meets; add unmapped ones to `EXTENDED_CHAR_KEY`
in `generate.py`.

### The extension stays installed

`k--kato.intellij-idea-keybindings` is the base layer in every target editor
(install it there). It covers the IntelliJ actions with **no** entry in its
command table (tool windows, refactorings, most navigation) — see `report.md`
→ *"No VS Code command mapping"*.

Caveat: on macOS the extension binds those residual actions to **Cmd**, not
Ctrl. Everything this port maps is re-bound to **Ctrl** (PC muscle memory,
matching the resolved keymap) and wins because user keybindings load after
extension keybindings. To pull more actions onto Ctrl, add them to
`manualActionCommand` in `overrides.jsonc` and re-generate.

## Usage

macOS / Linux:

```sh
./build.sh                 # resolve active keymap + generate
python3 install.py         # back up + deploy to every VS Code-family editor found
```

Windows (PowerShell):

```powershell
.\build.ps1
python install.py
```

Any OS, no wrapper:

```sh
python3 resolve_keymap.py && python3 generate.py && python3 install.py
```

`build.*` / `resolve_keymap.py` options:

```sh
--product IntelliJIdea            # PhpStorm (default), WebStorm, DataGrip, PyCharm, GoLand, …
--keymap "macOS"                  # a specific keymap (user or built-in; display names aliased)
--app  "/path/to/IDE"             # explicit install (.app bundle, Program Files dir, Toolbox dir)
--config-dir "/path/to/<Product><version>"
```

`install.py` options: `--dry-run`, `--only Code` (repeatable), `--file X.json`.

No JetBrains IDE on this machine? Drop a raw *Settings → Keymap → gear →
Export Keymap* `.xml` into `source/` (any name) and run `python3 generate.py`
directly.

## Known trade-offs (edit `overrides.jsonc` to change)

Generated bare `ctrl+<letter>` bindings carry a `!terminalFocus` guard so the
integrated terminal keeps its readline control chars (Ctrl+R, Ctrl+P, …).
`overrides.jsonc` entries win over the generated block.

| Key | This port | Note |
|-----|-----------|------|
| `ctrl+numpad +` / `-` | zoom in / out | fold-all loses the bare-numpad combo; **fold still works on `ctrl+=` / `ctrl+-`** |
| `ctrl+y` | redo | matches this keymap (`$Redo` / `Editor Redo`); `ctrl+shift+z` also redoes |
| `ctrl+s` | save current file | the keymap puts *Save All* here; VS Code auto-save covers the rest |
| `ctrl+,` | Settings UI | keymap also has `ctrl+alt+s` |
| `f7` | Step Into (debug) / Next Diff | both from the keymap; no-op outside their context |
| `ctrl+shift+c` | terminal: copy selection / editor: copy file path | different `when` contexts |
| `shift+enter` | terminal: send `ESC CR` / editor: new line below | different `when` contexts |
| `ctrl+§` (`[Backquote]`) | comment line | decoded from `ctrl #10000a7`; also on `ctrl+/` |
| mouse shortcuts (~14) | **not ported** | `keybindings.json` has no mouse bindings — see `report.md` |

## Verify after install

Reload each editor window, then spot-check (editor focused, **not** the terminal):

- `ctrl+d` → duplicate line · `ctrl+y` → redo
- `ctrl+w` / `ctrl+shift+w` → expand / shrink selection
- `ctrl+b` → go to definition · `ctrl+alt+b` → go to implementation
- `ctrl+alt+l` → reformat · `ctrl+§` and `ctrl+/` → comment line
- `ctrl+shift+a` → Find Action · `ctrl+o` / `ctrl+shift+o` → Go to Class / File
- `ctrl+k` commit · `ctrl+alt+k` commit & push · `ctrl+t` update project
- `alt+1` / `alt+3` / `alt+9` → Explorer / Search / SCM
- terminal: `ctrl+c`, `ctrl+d`, `ctrl+r`, `ctrl+p` still hit the shell

Then **Preferences: Open Keyboard Shortcuts**, filter `@source:user` — a full
list (~177 here), not a dozen.
