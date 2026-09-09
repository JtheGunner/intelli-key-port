# phpstorm-keymap-port

Port your **active JetBrains IDE keymap** — PhpStorm by default, but also
IntelliJ IDEA, WebStorm, DataGrip, PyCharm, GoLand, … — to the **VS Code
family** (VS Code, Antigravity, Cursor, VSCodium, …), reproducibly, by reading
the IDE's own keymap files rather than a third-party export. Works on
**macOS, Windows and Linux**.

Nothing here is specific to one machine or user: every path is derived at
runtime from the OS + the IDE's `product-info.json`. The per-user build
outputs (`source/*.resolved.xml`, `keybindings.generated.json`, `report.md`)
are git-ignored; only the code, `overrides.jsonc` and the pinned `vendor/kkato/`
fallback are tracked.

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
generate.py  ──uses k--kato's own resources (installed extension, else vendor/kkato/):
                        ActionIdCommandMapping.json     (IntelliJ action → VS Code command)
                        KeystrokeKeyMapping.json        (AWT key token → VS Code key)
                        default/<OS>/VSCode.json        ("already shipped by the extension" skip-set)
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

The three mapping resources come from
`k--kato.intellij-idea-keybindings` (<https://github.com/kasecato/vscode-intellij-idea-keybindings>).
Since that extension is installed into every target editor anyway,
`generate.py` reads them **live from the newest installed copy** and matches
the skip-set to this OS. `vendor/kkato/` is a pinned fallback (with a
`VERSION` file) for a fresh checkout / CI / the raw-export path; when the
installed version differs from the pin, the build prints a one-line note.
`./port.py --sync-vendor` refreshes `vendor/kkato/` from the installed
extension.

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

## What ends up in `keybindings.json`

**`keybindings.json` is a *delta* file, not a full list.** VS Code ships
hundreds of default bindings and the k--kato extension adds ~220 more; your
`keybindings.json` only **adds, removes or overrides** on top of those.
`keybindings.generated.json` *is* that file — `install.py` copies it in
verbatim (replacing whatever was there; the old one is kept as
`keybindings.json.bak-<timestamp>`).

It has two blocks, marked by `// ----` comments:

| Block | Roughly | What each line is |
|---|---|---|
| **generated** | ~135 | One entry per keymap action that (a) has a VS Code command in the mapping tables **and** (b) sits on a *different* key than the VS Code / k--kato default for this OS. `{ "key", "command" }` — plus `"when": "!terminalFocus"` on keys the shell needs (`ctrl`/`alt`+letter, word motion, `ctrl+ins` … ). |
| **overrides.jsonc `entries`** | ~55 | The curated hand-layer, appended **last** so it beats both the generated block and the extension. |

**A shortcut that is *not* in the file is not "missing".** It just has no
custom binding, so the VS Code default (or the extension's) still applies —
e.g. `ctrl+shift+p` works without an entry because it is already the VS Code
default. What is genuinely **not reproduced** is listed in `report.md`:

- **~340** keymap actions under *"No VS Code command mapping"* — no VS Code
  equivalent command (or none in the mapping tables). Their keystroke is
  left to whatever VS Code / the extension already do with it.
- **~14** mouse shortcuts — `keybindings.json` cannot express mouse bindings.
- extended keys that could not be decoded (usually 0).

### `overrides.jsonc` — the curated layer

Not a catalogue of "available" shortcuts; it is three lists that steer the
generator and the final file:

| Key | Purpose |
|---|---|
| `entries` | Literal keybinding rules appended **last** (they win over everything). The delicate stuff: terminal-signal guards (`ctrl+c` only `!terminalFocus` so the shell keeps Ctrl+C), `-cmd+x` removals so the macOS default doesn't *also* fire, and a few deliberate choices (`ctrl+y`=redo, zoom on numpad, `shift+enter`=terminal newline). |
| `manualActionCommand` | `IntelliJ actionId → VS Code command`, filling gaps / fixing stale entries in the vendored k--kato table. Only feeds the generator, so *more* actions get mapped. |
| `dropActions` | IntelliJ actionIds the generator must never emit (noise, duplicates such as `Diff.ShowDiff` on `ctrl+d`). |

### Keeping your own extra shortcuts

The tool only ports what is in your **JetBrains keymap**. It never invents
VS Code-only bindings, and — because `install.py` replaces the whole file —
a binding you added by hand in VS Code's own `keybindings.json` is
**overwritten** on the next run (recoverable from the `.bak-<timestamp>`).

To keep a personal binding permanently, add it to `overrides.jsonc` →
`entries` (VS Code syntax: `alt`, not `opt`). Example — *Accessible Diff
Viewer: Go to Next Difference*, a VS Code-native command with no JetBrains
equivalent:

```jsonc
{ "key": "ctrl+shift+alt+h", "command": "editor.action.accessibleDiffViewer.next", "when": "accessibleDiffViewerVisible" }
```

Find a command's exact id in **Preferences: Open Keyboard Shortcuts** →
right-click the row → *Copy Command ID*. After editing `overrides.jsonc`,
re-run `./port.py` (or `./port.py --skip-resolve` to skip the IDE read).

## Files

| Tracked in git | |
|---|---|
| `port.py` | one-shot driver (resolve → generate → install) |
| `resolve_keymap.py`, `generate.py`, `install.py` | the three stages, each runnable alone |
| `kkato.py` | locates the k--kato extension's resources (installed, else `vendor/kkato/`) |
| `sync_vendor.py` | refreshes `vendor/kkato/` from the installed extension (`./port.py --sync-vendor`) |
| `overrides.jsonc` | curated layer (edit this) |
| `vendor/kkato/` | pinned k--kato resources + `VERSION` — offline fallback for the three mapping tables |
| `README.md`, `source/README.md` | docs |

| Created by `./port.py` (git-ignored, per-user) | Stage | Purpose |
|---|---|---|
| `source/<active-keymap>.resolved.xml` | resolve | the IDE's active keymap, flattened with its full parent chain + plugin defaults — the single input to `generate.py` |
| `keybindings.generated.json` | generate | the deployable file (generated block + `overrides.jsonc` entries) |
| `report.md` | generate | audit: mapped / already-covered / no-command / untranslatable key / mouse |
| `<editor>/User/keybindings.json.bak-<timestamp>` | install | backup of each editor's previous keybindings |

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
./port.py --sync-vendor                # refresh vendor/kkato/ from the installed extension, then exit
```

A step that fails stops the chain. Each stage also runs on its own, same options:

```sh
python3 resolve_keymap.py [--product … --keymap … --app … --config-dir …]
python3 generate.py
python3 install.py        [--only NAME … --dry-run --file PATH]
python3 sync_vendor.py
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

Generated bindings on keys the shell needs (`ctrl`/`alt`+letter, `ctrl+left`/
`ctrl+right`, `ctrl+backspace`, `ctrl+ins`, …) carry a `!terminalFocus` guard,
so the integrated terminal keeps its readline / word-motion / clipboard keys.
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
list (~190 here), not a dozen.
