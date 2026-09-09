# IntelliKeyPort

**Finally a sync that carries the keybindings you actually care about from
*any* JetBrains / IntelliJ IDE into the rest of your editors.**

Pick a keymap in one IntelliJ-based IDE — IntelliJ IDEA, PhpStorm, WebStorm,
PyCharm, GoLand, DataGrip, Rider, … — and IntelliKeyPort reproduces it in the
**VS Code family**: VS Code, VS Code Insiders, VSCodium, Cursor, Windsurf,
Antigravity. It does the whole trip from A to Z:

1. **Export** the keymap that is currently active in your IntelliJ IDE (read
   straight from the IDE's own config files — no third-party export step).
2. **Convert** it into the target format (VS Code `keybindings.json`), resolving
   IntelliJ action ids to VS Code commands and AWT keystrokes to VS Code keys.
3. **Import** it into the editor(s) you choose, backing up whatever was there.

Because every path is derived at runtime from the OS and the IDE's
`product-info.json`, nothing here is tied to one machine or user. Run it again
whenever your JetBrains keymap changes and every editor stays in sync — the
shortcuts that matter are identical everywhere. Works on **macOS, Windows and
Linux**.

---

## Workflow

```
1. Select the correct keymap in your IntelliJ IDE   (Settings → Keymap)
2. Run the tool                                      ./port.py
3. Choose which editors to import into               (checkbox prompt)
4. Done
```

That is the whole thing. `./port.py` with no arguments resolves the active
keymap, regenerates `keybindings.generated.json`, and — when more than one
editor is installed and you are on a terminal — shows an arrow-key checkbox
list so you tick the targets. Reload each editor window afterwards.

---

## Quick start

```sh
git clone <this-repo> intelli-key-port
cd intelli-key-port
./port.py            # macOS / Linux   (Windows:  python port.py)
```

No JetBrains IDE on this machine? Export the keymap by hand
(*Settings → Keymap → gear → Export Keymap*), drop the `.xml` into `source/`,
and run `./port.py --skip-resolve`.

---

## Explanations

### Project structure

IntelliKeyPort is a small set of plain-Python scripts (no dependencies) plus
one hand-maintained data file. The flow is a three-stage pipeline, and
`port.py` just runs the three stages in order:

```
                     ┌─────────────────┐
   IntelliJ IDE ────▶ resolve_keymap.py │  find the IDE, read its active keymap,
                     └────────┬─────────┘  flatten the whole parent chain
                              ▼
              source/<name>.resolved.xml    (per-user, git-ignored)
                              ▼
                     ┌─────────────────┐
                     │   generate.py   │  translate every action → VS Code command
                     │  + overrides.jsonc  and every keystroke → VS Code key
                     └────────┬─────────┘
                              ▼
          keybindings.generated.json  +  report.md    (per-user, git-ignored)
                              ▼
                     ┌─────────────────┐
                     │   install.py    │  copy into each editor's keybindings.json
                     └─────────────────┘  (timestamped backup first)
```

| File | Role |
|---|---|
| `port.py` | One-shot driver: `resolve → generate → install`. A failing stage stops the chain. |
| `resolve_keymap.py` | **Stage 1.** Locates the JetBrains IDE (`/Applications`, Program Files, `/opt`, JetBrains Toolbox, Snap, Flatpak), finds its config directory, reads `keymap.xml` for the active keymap, then walks the parent chain (`$default → … → your keymap`) and folds in plugin-registered defaults (Git, etc.). Output: one flat `source/*.resolved.xml`. |
| `generate.py` | **Stage 2.** Turns the resolved keymap into a VS Code `keybindings.json` delta. Uses the mapping tables shipped by the `k--kato.intellij-idea-keybindings` extension, applies `overrides.jsonc`, decodes extended key codes, adds `!terminalFocus` guards, and detects/resolves key collisions. Output: `keybindings.generated.json` + a human-readable `report.md`. |
| `install.py` | **Stage 3.** Detects installed VS Code-family editors, backs up each one's `keybindings.json` as `keybindings.json.bak-<timestamp>`, and writes the generated file. Interactive checkbox picker when several editors are found. |
| `overrides.jsonc` | **The one file you edit by hand.** Curated tweaks that steer stages 2 and 3 (see below). |
| `kkato.py` | Locates the `k--kato` extension's resources (newest installed copy, else `vendor/kkato/`). |
| `prompt_select.py` | Stdlib arrow-key checkbox prompt used by `install.py`. |
| `sync_vendor.py` | Refreshes `vendor/kkato/` from the installed extension. |
| `vendor/kkato/` | Pinned copy of the `k--kato` mapping tables + a `VERSION` file — offline fallback for a fresh checkout / CI. |
| `source/` | Where the resolved keymap (or a hand-exported one) lives. |
| `tests/` | Unit tests for install-layout discovery, the editor picker, and conflict resolution. |

Everything tracked in git is machine-independent. The per-user build outputs
(`source/*.xml`, `keybindings.generated.json`, `report.md`) are git-ignored and
regenerated on every run.

### `overrides.jsonc` — the curated layer

`generate.py` does a faithful, mechanical translation of your JetBrains keymap.
`overrides.jsonc` is the small human layer on top of it — the place for the
handful of decisions a machine cannot make for you. It is **not** a catalogue
of available shortcuts; it is three lists:

| Key | What it does | Typical use |
|---|---|---|
| **`entries`** | Literal VS Code keybinding rules, appended at the **very end** of `keybindings.generated.json`. VS Code applies "last entry wins", so these beat both the generated block and the extension. | Terminal-signal guards (`ctrl+c` only when the terminal is *not* focused, so the shell keeps Ctrl+C); `-cmd+x` removals so a stock macOS shortcut does not *also* fire; deliberate choices such as `ctrl+y` = redo, zoom on the numpad, `shift+enter` = terminal newline. Keep this list small. |
| **`manualActionCommand`** | Extra `IntelliJ actionId → VS Code command` pairs. Only feeds the generator. | Fill gaps or fix stale rows in the vendored `k--kato` table so **more** of your keymap actually gets mapped. |
| **`dropActions`** | IntelliJ action ids the generator must **never** emit. | Silence noise and duplicates (e.g. a second action that also wants `ctrl+d`). |

Why it exists: some shortcuts are genuinely ambiguous once they leave the IDE.
The integrated terminal needs `ctrl+c` / `ctrl+d` / `ctrl+r`; macOS binds some
combos at the OS level; a few IntelliJ actions have two ids on the same key.
`overrides.jsonc` records those decisions once, in one readable file, so every
regeneration keeps them. After editing it, re-run `./port.py` (or
`./port.py --skip-resolve` to skip the IDE read).

Rule of thumb for `when` clauses: only `!editorReadonly` and `!terminalFocus`
are reliable across the VS Code family — avoid `textInputFocus` /
`editorTextFocus`.

### Commands

Everything runs through **`port.py`**. Its flags are flat; it routes each one
to the stage that needs it.

```sh
./port.py
```
The default: resolve the **active** keymap of the default JetBrains product
(PhpStorm), regenerate, then install with the interactive picker.

```sh
./port.py --product IntelliJIdea
```
Resolve a different JetBrains IDE. Known values: `PhpStorm`, `IntelliJIdea`,
`WebStorm`, `PyCharm`, `DataGrip`, `GoLand`, `RubyMine`, `CLion`, `Rider`,
`RustRover`.

```sh
./port.py --keymap "macOS"
```
Resolve a specific keymap instead of the IDE's active one — a built-in
(`Default`, `macOS`, `Visual Studio`, …) or one of your own. Display names are
aliased to their internal names.

```sh
./port.py --app "/Applications/WebStorm.app"
```
Point at an explicit install when auto-discovery picks the wrong one or finds
nothing. Accepts a macOS `.app` bundle, a Windows program directory, or a
JetBrains Toolbox folder.

```sh
./port.py --config-dir "/path/to/WebStorm2025.2"
```
Point at an explicit IDE **config** directory (the one holding
`options/keymap.xml`), skipping install-based discovery entirely.

```sh
./port.py --only Code --only Cursor
```
Install into just these editors (repeatable). Names are the config-folder
names: `Code`, `Code - Insiders`, `VSCodium`, `Cursor`, `Windsurf`,
`Antigravity`, `Antigravity IDE`. Passing `--only` also skips the picker.

```sh
./port.py --dry-run
```
Resolve and generate as usual, but only **print** what the install step would
write — no files touched.

```sh
./port.py --file other.json
```
Install a different keybindings file instead of the freshly generated one.

```sh
./port.py --skip-resolve
```
Reuse the existing `source/*.resolved.xml` (or a hand-exported
`source/*.xml`) — no JetBrains IDE needed. Use this on a machine with no IDE,
or after editing `overrides.jsonc`.

```sh
./port.py --skip-install
```
Stop after `generate.py`. You get `keybindings.generated.json` + `report.md`
and nothing is deployed.

```sh
./port.py --sync-vendor
```
Refresh `vendor/kkato/` from the newest installed `k--kato` extension, then
exit. Run this after the extension updates so the offline fallback stays
current.

Each stage is also runnable on its own, with the same options:

```sh
python3 resolve_keymap.py [--product … --keymap … --app … --config-dir …]
python3 generate.py
python3 install.py        [--only NAME … --dry-run --file PATH]
python3 sync_vendor.py
```

---

## How the translation works

`generate.py` builds a **delta** file. VS Code already ships hundreds of
default bindings and the `k--kato.intellij-idea-keybindings` extension adds
~220 more; `keybindings.generated.json` only **adds, removes or overrides** on
top of those. It has two blocks, marked by `// ----` comments:

| Block | Roughly | Each line |
|---|---|---|
| **generated** | ~135 | One entry per keymap action that has a VS Code command **and** sits on a different key than the VS Code / `k--kato` default for this OS. Keys the shell needs also get `"when": "!terminalFocus"`. |
| **`overrides.jsonc` `entries`** | ~55 | The curated hand-layer, appended **last** so it wins. |

A shortcut that is **not** in the file is not "missing" — it just has no custom
binding, so the VS Code (or extension) default still applies. What is genuinely
**not reproduced** is listed in `report.md`:

- **~340** keymap actions with no VS Code command (tool windows, most
  refactorings, most navigation). The `k--kato` extension already binds many of
  these — on macOS to **Cmd**, not Ctrl. To pull one onto Ctrl, add it to
  `manualActionCommand` and regenerate.
- **~14** mouse shortcuts — `keybindings.json` cannot express mouse bindings.
- Any extended key code that could not be decoded (usually zero).

`report.md` also lists key collisions: resolved by keymap order (the earlier
action wins), left unresolved (fix in `overrides.jsonc`), or overridden by
`overrides.jsonc` on purpose.

### The `k--kato` extension stays installed

`k--kato.intellij-idea-keybindings` is the base layer in every target editor —
it covers the many IntelliJ actions that have no entry in its own command
table. IntelliKeyPort's output loads **after** it and re-binds everything it
maps to **Ctrl** (PC muscle memory, matching the resolved keymap). Install it
in each editor:

```sh
code   --install-extension k--kato.intellij-idea-keybindings
cursor --install-extension k--kato.intellij-idea-keybindings
```

### Extended / layout keys

Extended key codes (`#100XXXX`) are decoded to their character and mapped to a
VS Code **scan-code** token (`§`/`°` → `[Backquote]`, ISO `<`/`>` →
`[IntlBackslash]`, German `ä`/`ö`/`ü` → `[Quote]`/`[Semicolon]`/`[BracketLeft]`,
…), so the binding follows the physical key on any layout. `resolve_keymap.py`
prints every `#100XXXX` token it meets; add unmapped ones to
`EXTENDED_CHAR_KEY` in `generate.py`.

---

## Platform support

| | IDE discovery | Editor config dirs |
|---|---|---|
| **macOS** | `/Applications`, `~/Applications`, Toolbox | `~/Library/Application Support/<editor>/User` |
| **Windows** | `Program Files\JetBrains`, `%LOCALAPPDATA%\Programs`, Toolbox | `%APPDATA%\<editor>\User` |
| **Linux** | `/opt`, `/usr/local`, `/snap`, `~/Applications`, Toolbox, Flatpak | `~/.config/<editor>/User`, Flatpak `~/.var/app/<id>/config/…`, Snap `~/snap/<name>/current/.config/…` |

`--app` / `--config-dir` override discovery entirely.

---

## Known trade-offs (edit `overrides.jsonc` to change)

| Key | This port | Note |
|-----|-----------|------|
| `ctrl+numpad +` / `-` | zoom in / out | fold-all loses the bare-numpad combo; fold still works on `ctrl+=` / `ctrl+-` |
| `ctrl+y` | redo | matches this keymap (`$Redo`); `ctrl+shift+z` also redoes |
| `ctrl+s` | save current file | the keymap puts *Save All* here; VS Code auto-save covers the rest |
| `ctrl+,` | Settings UI | keymap also has `ctrl+alt+s` |
| `f7` | Step Into (debug) / Next Diff | both from the keymap; no-op outside their context |
| `ctrl+shift+c` | terminal: copy selection / editor: copy file path | different `when` contexts |
| `shift+enter` | terminal: send `ESC CR` / editor: new line below | different `when` contexts |
| `ctrl+§` (`[Backquote]`) | comment line | decoded from `ctrl #10000a7`; also on `ctrl+/` |
| mouse shortcuts (~14) | not ported | `keybindings.json` has no mouse bindings — see `report.md` |

---

## Verify after install

Reload each editor window, then spot-check with the **editor** focused (not the
terminal):

- `ctrl+d` → duplicate line · `ctrl+y` → redo
- `ctrl+w` / `ctrl+shift+w` → expand / shrink selection
- `ctrl+b` → go to definition · `ctrl+alt+b` → go to implementation
- `ctrl+alt+l` → reformat · `ctrl+§` and `ctrl+/` → comment line
- `ctrl+shift+a` → Find Action · `ctrl+o` / `ctrl+shift+o` → Go to Class / File
- `alt+1` / `alt+3` / `alt+9` → Explorer / Search / SCM
- terminal: `ctrl+c`, `ctrl+d`, `ctrl+r`, `ctrl+p` still hit the shell

Then open **Preferences: Open Keyboard Shortcuts**, filter `@source:user` — you
should see a full list (~190 entries), not a dozen.

---

## Contributing

Contributions are welcome — bug reports, new IDE/editor coverage, better action
mappings.

- **Report a mapping gap.** Run `./port.py` and open `report.md`. If an action
  you use is under *"No VS Code command mapping"* but a VS Code command does
  exist, add the pair to `manualActionCommand` in `overrides.jsonc` and send a
  PR.
- **Add a JetBrains product.** Extend the `PRODUCTS` table in
  `resolve_keymap.py`.
- **Add an editor.** Extend the `EDITORS` table in `install.py`.
- **Run the tests** before opening a PR:

  ```sh
  python3 -m unittest discover -s tests -v
  ```

- Keep developer-facing text (code, comments, commit messages) in English.
  Commit messages follow Conventional Commits (`feat:`, `fix:`, `docs:`, …).
- Do not commit the per-user build outputs — they are git-ignored for a reason.

---

## License

Released under the **MIT License** — see [`LICENSE`](LICENSE). MIT is a good fit
here: the project is a thin tool, and the mapping data it bundles under
`vendor/kkato/` is itself MIT-licensed.

---

## Credits

- **Inspired by** [vlad-ogol/intellij-keymap-xml-exporter](https://github.com/vlad-ogol/intellij-keymap-xml-exporter)
  — the idea of turning an IntelliJ keymap into something portable.
- **Mapping data** from [kasecato/vscode-intellij-idea-keybindings](https://github.com/kasecato/vscode-intellij-idea-keybindings)
  (`k--kato.intellij-idea-keybindings`). Its `ActionIdCommandMapping.json` and
  `KeystrokeKeyMapping.json` do the heavy lifting of matching IntelliJ actions
  and AWT keystrokes to their VS Code equivalents — without them this would
  have been a slog.
