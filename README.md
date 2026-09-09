# phpstorm-keymap-port

Port your **active JetBrains IDE keymap** — PhpStorm by default, but also
IntelliJ IDEA, WebStorm, DataGrip, PyCharm, GoLand, … — to the **VS Code
family** (VS Code, Antigravity, Cursor, VSCodium, …), reproducibly, by reading
the IDE's own keymap files rather than a third-party export. Works on
**macOS, Windows and Linux**.

Nothing here is specific to one machine or user: every path is derived at
runtime from the OS + the IDE's `product-info.json`. The per-user build
outputs (`source/*.resolved.xml`, `keybindings.generated.json`, `report.md`)
are git-ignored; only the code, `overrides.jsonc` and pinned `vendor/` files
are tracked.

## Why the naive routes failed

**`isudox.vscode-jetbrains-keybindings` XML import** — not a real porter:
~232 of 378 entries were invisible `-command` removals; ~30 kept raw Java
AWT key tokens VS Code silently drops; many `command`s were IntelliJ ids
with no VS Code equivalent. Net: a handful of working bindings.

**`intellij-keymap-xml-exporter`** — flattens the keymap but mangles keys
it cannot serialize. It turned `ctrl §` (the IDE stores it as the extended
key code `ctrl #10000a7`, `0xA7` = section sign) into `ctrl UNKNOWN`.

## How this works instead

`port.py` runs the three stages in order. Each stage is also a standalone script.

```
resolve_keymap.py
   • finds the IDE install via product-info.json          (macOS .app / Win / Linux / Toolbox / Flatpak)
   • matches the config dir via dataDirectoryName
   • reads options/[mac/]keymap.xml → <active_keymap>     (--keymap overrides)
   • walks the parent chain  $default → … → <active>
   • folds in plugin-registered defaults (Git etc.) from  plugins/**/*.jar  META-INF/*.xml
        ▼
source/<name>.resolved.xml     flat, fully-inherited keymap (per-user, git-ignored)
        ▼
generate.py  ──uses──►  vendor/ActionIdCommandMapping.json   (IntelliJ action → VS Code command)
                        vendor/KeystrokeKeyMapping.json       (AWT key token → VS Code key)
                        vendor/default-Windows-VSCode.json    ("already shipped by extension")
        │  • decodes #100XXXX extended keys · !terminalFocus-guards bare ctrl+<letter>
        ├─ overrides.jsonc   curated layer: terminal-signal guards, `-cmd` removals,
        │                    stale/missing action→command fixes, drop-list  (appended LAST → wins)
        ▼
keybindings.generated.json    generated block  +  overrides.jsonc "entries"
report.md                     what mapped / was already covered / has no VS Code command / mouse
        ▼
install.py   →  <user-data>/<editor>/User/keybindings.json      (timestamped backup first)
                Code · Code - Insiders · VSCodium · Cursor · Windsurf · Antigravity · Antigravity IDE
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

`k--kato.intellij-idea-keybindings` is the base layer in every target editor:

```sh
code   --install-extension k--kato.intellij-idea-keybindings      # VS Code
cursor --install-extension k--kato.intellij-idea-keybindings      # Cursor
# Antigravity: its bundled CLI, e.g.
"/Applications/Antigravity IDE.app/Contents/Resources/app/bin/antigravity-ide" \
    --install-extension k--kato.intellij-idea-keybindings
```

It covers the IntelliJ actions with **no** entry in its command table (tool
windows, refactorings, most navigation) — see `report.md` → *"No VS Code
command mapping"*.

Caveat: on macOS the extension binds those residual actions to **Cmd**, not
Ctrl. Everything this port maps is re-bound to **Ctrl** (PC muscle memory,
matching the resolved keymap) and wins because user keybindings load after
extension keybindings. To pull more actions onto Ctrl, add them to
`manualActionCommand` in `overrides.jsonc` and re-generate.

## Usage

One command does everything — resolve the active keymap, generate, install:

```sh
./port.py                    # macOS / Linux   (or: python3 port.py)
python port.py               # Windows
```

All options are flat; `port.py` routes each to the right stage:

```sh
./port.py --product IntelliJIdea       # → resolve   PhpStorm (default), WebStorm, DataGrip, PyCharm, GoLand, …
./port.py --keymap "macOS"             # → resolve   a specific keymap (user or built-in; display names aliased)
./port.py --app "/path/to/IDE"         # → resolve   explicit install (.app bundle, Program Files dir, Toolbox dir)
./port.py --config-dir "/path/to/<Product><version>"
./port.py --only Code --only Cursor    # → install   restrict to these editors (repeatable)
./port.py --dry-run                    # → install   preview only (resolve + generate still run)
./port.py --file other.json            # → install   a different keybindings file
./port.py --skip-install               # stop after generate
./port.py --skip-resolve               # reuse the existing source/*.resolved.xml
```

A step that fails stops the chain. Each stage also runs on its own, same options:

```sh
python3 resolve_keymap.py [--product … --keymap … --app … --config-dir …]
python3 generate.py
python3 install.py        [--only NAME … --dry-run --file PATH]
```

No JetBrains IDE on this machine? Drop a raw *Settings → Keymap → gear →
Export Keymap* `.xml` into `source/` (any name) and run
`./port.py --skip-resolve` (or `python3 generate.py && python3 install.py`) —
this fallback is pure Python and needs no IDE detection.

### Platform support

| | IDE discovery | Editor config dirs |
|---|---|---|
| **macOS** | `/Applications`, `~/Applications`, Toolbox | `~/Library/Application Support/<editor>/User` |
| **Windows** | `Program Files\JetBrains`, `%LOCALAPPDATA%\Programs`, Toolbox | `%APPDATA%\<editor>\User` |
| **Linux** | `/opt`, `/usr/local`, `/snap`, `~/Applications`, Toolbox, **Flatpak** (`/var/lib/flatpak`, `~/.local/share/flatpak`) | `~/.config/<editor>/User`, **Flatpak** `~/.var/app/<id>/config/…`, **Snap** `~/snap/<name>/current/.config/…` |

Linux IDE discovery is a depth-limited directory walk (handles tar.gz, Toolbox
`ch-0/<build>`, Snap and Flatpak layouts in one pass). Flatpak IDEs keep their
config under `~/.var/app/<id>/config/JetBrains` — that is searched too.
`--app` / `--config-dir` override discovery entirely.

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
