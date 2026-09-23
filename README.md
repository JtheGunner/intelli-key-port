<div align="center">

# ⌨️ IntelliKeyPort

**One keymap to rule them all.**
Carry the keybindings you actually care about from *any* JetBrains / IntelliJ IDE
into the rest of your editors.

<code>🧠 JetBrains keymap</code> &nbsp;→&nbsp; <code>🔄 IntelliKeyPort</code> &nbsp;→&nbsp; <code>💻 VS Code · Cursor · Windsurf · Antigravity</code>

![License](https://img.shields.io/badge/license-MIT-22c55e?style=flat-square)
![Python](https://img.shields.io/badge/python-3.9%2B-3776ab?style=flat-square&logo=python&logoColor=white)
![Dependencies](https://img.shields.io/badge/dependencies-none-8b5cf6?style=flat-square)
![Platforms](https://img.shields.io/badge/macOS%20·%20Windows%20·%20Linux-supported-0ea5e9?style=flat-square)
![PRs welcome](https://img.shields.io/badge/PRs-welcome-f59e0b?style=flat-square)

</div>

---

## 🎯 What it is

Pick a keymap in one IntelliJ-based IDE — IntelliJ IDEA, PhpStorm, WebStorm,
PyCharm, GoLand, DataGrip, Rider, … — and IntelliKeyPort reproduces it in the **VS Code family**: VS Code, VS Code Insiders, VSCodium, Cursor, Windsurf,
Antigravity.

It does the whole trip from A to Z:

|    | Step        | Description                                                                                                                             |
|:--:|-------------|-----------------------------------------------------------------------------------------------------------------------------------------|
| 📤 | **Export**  | reads the keymap that is *currently active* in your IntelliJ IDE, straight from the IDE's own config files — no third-party export step |
| 🔀 | **Convert** | rewrites it as a VS Code `keybindings.json`, mapping IntelliJ action ids → VS Code commands and AWT keystrokes → VS Code keys           |
| 📥 | **Import**  | drops it into the editor(s) you choose, backing up whatever was there first                                                             |

Every path is derived at runtime from the OS and the IDE's `product-info.json`,
so nothing is tied to one machine or user. **Re-run it whenever your JetBrains
keymap changes** and every editor stays in sync — the shortcuts that matter are
identical everywhere.

### ✨ At a glance

|                                  |                                                                                    |
|----------------------------------|------------------------------------------------------------------------------------|
| 📥&nbsp;&nbsp;**Input**          | the active keymap of any JetBrains IDE (or a hand-exported `.xml`)                 |
| 📤&nbsp;&nbsp;**Output**         | a ready-to-use `keybindings.json` for every installed VS Code-family editor        |
| 🧰&nbsp;&nbsp;**Dependencies**   | none — Python 3 standard library only                                              |
| 💾&nbsp;&nbsp;**Safe**           | each target's `keybindings.json` is backed up as `…bak-<timestamp>` before writing |
| 🔁&nbsp;&nbsp;**Repeatable**     | idempotent; discovery happens at runtime, so it survives IDE updates               |
| 🖥️&nbsp;&nbsp;**Cross-platform** | macOS, Windows, Linux (incl. JetBrains Toolbox, Snap, Flatpak)                     |

---

## 🧭 Workflow

```text
  ┌────────────────────────────────────────────────────────────┐
  │  1.  Pick the right keymap in your IntelliJ IDE             │  Settings → Keymap
  │  2.  Run the tool                          ./port.py        │
  │  3.  Tick the editors to import into       [x] Code  [x] …  │  checkbox prompt
  │  4.  Done — reload each editor window                       │
  └────────────────────────────────────────────────────────────┘
```

`./port.py` with no arguments resolves the active keymap, regenerates
`keybindings.generated.json`, and — when more than one editor is installed, and
you are on a terminal — shows an arrow-key checkbox list so you tick the
targets.

---

## 🚀 Quick start

```sh
git clone https://github.com/JtheGunner/intelli-key-port.git intelli-key-port
cd intelli-key-port

# macOS / Linux
./port.py

# Ctrl-based keymap (Windows / XWin style) on a Mac? add the matching layer
./port.py --layer windows-keymap

#  Windows
python port.py
```

> [!TIP]
> **No JetBrains IDE on this machine?** – Then you've two options
>> 1. Export the keymap by hand (*Settings → Keymap → gear ⚙️ → Export Keymap*), drop the `.xml` into source/`
>> 2. use the bundled `source/default.xml` — the stock IntelliJ `$default` keymap
>
> run `./port.py --skip-resolve`. That path is pure Python and needs no IDE detection.

---

## 🧩 How it fits together

IntelliKeyPort is a small set of plain-Python scripts plus **one**
hand-maintained data file. `port.py` runs a three-stage pipeline — read it
top to bottom:

```yaml
   "IntelliJ IDE · your active keymap"
     │
   ▼   resolve_keymap.py: find the IDE, flatten the parent chain
     "source/<name>.resolved.xml"
     │
   ▼   generate.py: actions → commands, keys → keys
     "keybindings.generated.json + report.md"
     │
   ▼   install.py: timestamped backup, then write
     "VS Code · Cursor · Windsurf · Antigravity · …"
```

Each stage is also a standalone script; `port.py` just runs the three in order
and stops at the first failure.

### 📂 The files

| File                              | Role                                                                                                                                                                                                                                                                                                                                     |
|-----------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 🎬&nbsp;&nbsp;`port.py`           | One-shot driver: `resolve → generate → install`. A failing stage stops the chain.                                                                                                                                                                                                                                                        |
| 🔍&nbsp;&nbsp;`resolve_keymap.py` | **Stage 1.** Locates the JetBrains IDE (`/Applications`, Program Files, `/opt`, JetBrains Toolbox, Snap, Flatpak), finds its config directory, reads `keymap.xml` for the active keymap, walks the parent chain (`$default → … → your keymap`), and folds in plugin-registered defaults (Git, etc.). → one flat `source/*.resolved.xml`. |
| 🏗️&nbsp;&nbsp;`generate.py`       | **Stage 2.** Turns the resolved keymap into a VS Code `keybindings.json` *delta*: applies the `k--kato` mapping tables + the curated layers, decodes extended key codes, adds `!terminalFocus` guards, and detects/resolves key collisions. → `keybindings.generated.json` + a readable `report.md`.                                     |
| 📦&nbsp;&nbsp;`install.py`        | **Stage 3.** Detects installed VS Code-family editors, backs up each one's `keybindings.json` as `…bak-<timestamp>`, then writes the generated file. Interactive checkbox picker when several editors are found.                                                                                                                         |
| 🎛️&nbsp;&nbsp;`overrides.jsonc`   | **Base layer**, always applied: keymap- and machine-neutral fixes that steer stage 2 — see below.                                                                                                                                                                                                                                        |
| 🧅&nbsp;&nbsp;`layers/`           | **Optional layers**, stacked on the base only with `--layer NAME` — see below.                                                                                                                                                                                                                                                           |
| 🧷&nbsp;&nbsp;`kkato.py`          | Locates the `k--kato` extension's resources (newest installed copy, else `vendor/kkato/`).                                                                                                                                                                                                                                               |
| ☑️&nbsp;&nbsp;`prompt_select.py`  | Stdlib arrow-key checkbox prompt used by `install.py`.                                                                                                                                                                                                                                                                                   |
| 🔄&nbsp;&nbsp;`sync_vendor.py`    | Refreshes `vendor/kkato/` from the installed extension.                                                                                                                                                                                                                                                                                  |
| 🗃️&nbsp;&nbsp;`vendor/kkato/`     | Pinned copy of the `k--kato` mapping tables + a `VERSION` file — offline fallback for a fresh checkout / CI.                                                                                                                                                                                                                             |
| 📁&nbsp;&nbsp;`source/`           | Where the resolved keymap (or a hand-exported one) lives.                                                                                                                                                                                                                                                                                |
| 🧪&nbsp;&nbsp;`tests/`            | Unit tests for install-layout discovery, the editor picker, conflict resolution, and layer stacking.                                                                                                                                                                                                                                     |

> [!NOTE]
> Everything tracked in git is machine-independent. The per-user build outputs
> (`source/*.xml`, `keybindings.generated.json`, `report.md`) are git-ignored
> and regenerated on every run.

---

## 🎛️ Curated layers

`generate.py` does a faithful, mechanical translation of your JetBrains keymap.
The curated layers are the small **human part** on top of it — the place for
the handful of decisions a machine cannot make for you.

| Layer                                         | Applied                      | What it holds                                                                                                                                                                                           |
|-----------------------------------------------|------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 🧱&nbsp;&nbsp;`overrides.jsonc`               | always                       | Keymap- and machine-neutral fixes: extra action mappings, noise drops, `F7` split between Step Into and Next Difference, `F2` next error.                                                               |
| 🪟&nbsp;&nbsp;`layers/windows-keymap.jsonc`   | `--layer windows-keymap`     | For a **Ctrl-based** keymap (`$default`, *Default for XWin*, KDE, GNOME): the terminal keeps `Ctrl + C` / `D` / `R`, and on macOS the stock `Cmd` shortcuts are removed so they don't fire as well.     |
| ⌨️&nbsp;&nbsp;`layers/karabiner-winkeys.jsonc` | `--layer karabiner-winkeys`  | Companion to the [Karabiner `[winkeys]` rules](https://github.com/JtheGunner/karabiner-windows-keyboard-mapping-macos): `Alt + ←/→` word jump, `Home`/`End`, tab switching moved to `Ctrl + Cmd + ←/→`. |
| 👤&nbsp;&nbsp;*your own file*                 | `--layer path/to/mine.jsonc` | Personal choices (e.g. `Ctrl + Y` = redo). Keep it next to your dotfiles, not in this repo.                                                                                                             |

Layers stack in order: `overrides.jsonc`, then each `--layer` in the order
given. A later layer wins. Its `entries` come later in the file, and VS Code
applies *"last entry wins"*. Its `manualActionCommand` rows replace earlier ones,
and `dropActions` from all layers add up. Without `--layer` you get a plain,
faithful port. `generate.py` tells you when a Ctrl-based keymap on a Mac probably
wants `--layer windows-keymap`.

Every layer is a JSONC object with up to three lists:

| Key                                     | What it does                                                                                                                                                                                   | Typical use                                                                                                     |
|-----------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------|
| 🥇&nbsp;&nbsp;**`entries`**             | Literal VS Code keybinding rules, appended at the **very end** of `keybindings.generated.json`. VS Code applies *"last entry wins"*, so these beat both the generated block and the extension. | Terminal-signal guards, `-cmd+x` removals so a stock macOS shortcut doesn't *also* fire, deliberate deviations. |
| ➕&nbsp;&nbsp;**`manualActionCommand`** | Extra `IntelliJ actionId → VS Code command` pairs. Feeds the generator only.                                                                                                                   | Fill gaps / fix stale rows in the vendored `k--kato` table so **more** of your keymap gets mapped.              |
| 🚫&nbsp;&nbsp;**`dropActions`**         | IntelliJ action ids the generator must **never** emit.                                                                                                                                         | Silence noise and duplicates, or free a key you reassign in `entries`.                                          |

After editing a layer, re-run `./port.py` with the same `--layer` flags (or add
`--skip-resolve` to skip the IDE read).

> [!IMPORTANT]
> Rule of thumb for `when` clauses: only `!editorReadonly` and `!terminalFocus`
> are reliable across the whole VS Code family — avoid `textInputFocus` /
> `editorTextFocus`.

---

## ⚙️ Commands

Everything runs through **`port.py`**. Its flags are flat; it routes each one to
the stage that needs it.

<table>
<tr><th>Command</th><th>What it does</th></tr>

<tr><td>

```sh
./port.py
```

</td><td>

**The default.** Resolve the *active* keymap of the default JetBrains product (PhpStorm), regenerate, then install with the interactive picker.

</td></tr>
<tr><td>

```sh
./port.py --product IntelliJIdea
```

</td><td>

Resolve a different JetBrains IDE. Known values: `PhpStorm`, `IntelliJIdea`,
`WebStorm`, `PyCharm`, `DataGrip`, `GoLand`, `RubyMine`, `CLion`, `Rider`,
`RustRover`.

</td></tr>
<tr><td>

```sh
./port.py --keymap "macOS"
```

</td><td>

Resolve a *specific* keymap instead of the IDE's active one — a built-in (`Default`, `macOS`, `Visual Studio`, …) or one of your own. Display names are
aliased to their internal names.

</td></tr>
<tr><td>

```sh
./port.py --app "/Applications/WebStorm.app"
```

</td><td>

Point at an explicit install when auto-discovery picks the wrong one or finds
nothing. Accepts a macOS `.app` bundle, a Windows program directory, or a
JetBrains Toolbox folder.

</td></tr>
<tr><td>

```sh
./port.py --config-dir "/path/to/WebStorm2025.2"
```

</td><td>

Point at an explicit IDE **config** directory (the one holding
`options/keymap.xml`), skipping install-based discovery entirely.

</td></tr>
<tr><td>

```sh
./port.py --only Code --only Cursor
```

</td><td>

Install into just these editors (repeatable). Names are the config-folder
names: `Code`, `Code - Insiders`, `VSCodium`, `Cursor`, `Windsurf`,
`Antigravity`, `Antigravity IDE`. Also skips the picker.

</td></tr>
<tr><td>

```sh
./port.py --dry-run
```

</td><td>

Resolve and generate as usual, but only **print** what the installation step would
write — no files touched.

</td></tr>
<tr><td>

```sh
./port.py --file other.json
```

</td><td>

Install a different keybindings file instead of the freshly generated one.

</td></tr>
<tr><td>

```sh
./port.py --layer windows-keymap --layer ~/dotfiles/mine.jsonc
```

</td><td>

Stack curated layers on top of `overrides.jsonc`, in the order given: a bundled
one from `layers/` by name, or your own `.jsonc` file by path. Repeatable.

</td></tr>
<tr><td>

```sh
./port.py --skip-resolve
```

</td><td>

Reuse the existing `source/*.resolved.xml` (or a hand-exported `source/*.xml`)
— no JetBrains IDE needed. Use on an IDE-less machine, or after editing a
curated layer.

</td></tr>
<tr><td>

```sh
./port.py --skip-install
```

</td><td>

Stop after `generate.py`. You get `keybindings.generated.json` + `report.md`,
nothing is deployed.

</td></tr>
<tr><td>

```sh
./port.py --sync-vendor
```

</td><td>

Refresh `vendor/kkato/` from the newest installed `k--kato` extension, then
exit. Run after the extension updates so the offline fallback stays current.

</td></tr>
</table>

Each stage also runs on its own, with the same options:

```sh
python3 resolve_keymap.py [--product … --keymap … --app … --config-dir …]
python3 generate.py
python3 install.py        [--only NAME … --dry-run --file PATH]
python3 sync_vendor.py
```

> [!NOTE]
> By default, the tool is looking for IDEs and config-dirs by itself.<br>
> If you're using `--app` / `--config-dir` that will override discovery entirely.

---

## 🔬 How the translation works

`generate.py` builds a **delta** file. VS Code already ships hundreds of default
bindings and the `k--kato.intellij-idea-keybindings` extension adds a few
hundred more; `keybindings.generated.json` only **adds, removes or overrides**
on top of those. It has two blocks, marked by `// ----` comments:

| Block                                           | Each line                                                                                                                                                                                          |
|-------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 🏗️&nbsp;&nbsp;**generated**                     | One entry per keymap action that has a VS Code command **and** sits on a different key than the VS Code / `k--kato` default for this OS. Keys the shell needs also get `"when": "!terminalFocus"`. |
| 🎛️&nbsp;&nbsp;**curated layers&nbsp;`entries`** | One block per layer (`overrides.jsonc`, then each `--layer`), appended **last** so they win.                                                                                                       |

Every run writes a `report.md` that accounts for **all** of it. The figures
below are from the bundled sample keymap — the full output is committed as the **[example report](docs/example-report.md)** (`source/default.xml`, the stock `$default` keymap, 485 actions, no layers):

| `report.md` section                       |  Sample | Meaning                                                                                                                                                                    |
|-------------------------------------------|--------:|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| generated → emitted                       | **141** | actions that became a `keybindings.json` entry                                                                                                                             |
| curated entries                           |   **4** | entries from the curated layers, appended last                                                                                                                             |
| already covered by the layers / extension |  **24** | same key + command already shipped — skipped                                                                                                                               |
| no VS Code command mapping                | **328** | tool windows, most refactorings & navigation — left to VS Code / the extension (on macOS often on `Cmd`, not `Ctrl`; move one with `manualActionCommand`, then regenerate) |
| mouse shortcuts                           |  **14** | `keybindings.json` cannot express mouse bindings                                                                                                                           |
| key could not be translated               |   **0** | an AWT keystroke with no VS Code token                                                                                                                                     |

`report.md` also lists key collisions: resolved by keymap order (earlier action
wins), left unresolved (fix in a layer), or overridden on purpose.

> [!NOTE]
> A shortcut that is **not** in the file is not *"missing"* — it just has no
> custom binding, so the VS Code (or extension) default still applies.

<br>

### 🧱 The `k--kato` extension stays installed

`k--kato.intellij-idea-keybindings` is the base layer in every target editor —
it covers the many IntelliJ actions that have no entry in its own command
table. IntelliKeyPort's output loads **after** it and re-binds everything it
maps to `Ctrl`(PC muscle memory, matching the resolved keymap).
Install it in each editor:

```sh
code   --install-extension k--kato.intellij-idea-keybindings
cursor --install-extension k--kato.intellij-idea-keybindings
```

<br>

### 🌍 Extended / layout keys

Extended key codes (`#100XXXX`) are decoded to their character and mapped to a VS Code **scan-code** token, ensuring keybindings follow the *physical key* across different keyboard layouts.

| Input Character | Physical Key (Scan Code) | Notes / Region          |
|:----------------|:-------------------------|:------------------------|
| `§` / `°`       | `[Backquote]`            | Swiss / German Top-Left |
| `<` / `>`       | `[IntlBackslash]`        | ISO Extra Key           |
| `ä`             | `[Quote]`                | German Umlaut           |
| `ö`             | `[Semicolon]`            | German Umlaut           |
| `ü`             | `[BracketLeft]`          | German Umlaut           |

> [!NOTE]
> **Adding Missing Keys**  
> `resolve_keymap.py` prints every unmapped `#100XXXX` token it encounters. Add new mappings to `EXTENDED_CHAR_KEY` in `generate.py`.

---

## 🖥️ Platform support

|                           | 🔍 IDE discovery                                                       | 📁 Editor config dirs                                                                                    |
|---------------------------|------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------|
| 🍎&nbsp;&nbsp;**macOS**   | `/Applications` · `~/Applications` · Toolbox                           | `~/Library/Application Support/<editor>/User`                                                            |
| 🪟&nbsp;&nbsp;**Windows** | `Program Files\JetBrains` · `%LOCALAPPDATA%\Programs` · Toolbox        | `%APPDATA%\<editor>\User`                                                                                |
| 🐧&nbsp;&nbsp;**Linux**   | `/opt` · `/usr/local` · `/snap` · `~/Applications` · Toolbox · Flatpak | `~/.config/<editor>/User` ·  Flatpak `~/.var/app/<id>/config/…` · Snap `~/snap/<name>/current/.config/…` |

---

## ⚖️ Known trade-offs

| Key                       | This port                         | Layer               | Note                                                            |
|---------------------------|-----------------------------------|---------------------|-----------------------------------------------------------------|
| `F7`                      | Step Into (debug) / Next Diff     | `overrides.jsonc`   | both from the keymap; no-op outside their context               |
| `Ctrl + Shift + C` / `V`  | terminal: copy / paste            | `windows-keymap`    | the editor keeps whatever the keymap puts there                 |
| `Cmd + C` / `S` / `F` / … | **removed** (macOS)               | `windows-keymap`    | so only the Ctrl binding fires                                  |
| `Alt + ←` / `→`           | word jump (not tab switching)     | `karabiner-winkeys` | tabs move to `Ctrl + Cmd + ←` / `→`                             |
| `Home` / `End`            | line start / end (not smart home) | `karabiner-winkeys` | matches the Karabiner rules; also works in the agent-chat input |
| 🖱️ mouse shortcuts        | **not ported**                    | –                   | `keybindings.json` has no mouse bindings — see `report.md`      |

> [!WARNING]
> **Characters typed with Option / AltGr (macOS).** On Swiss / German layouts
> AltGr is `Option`, so `Option + 2` / `3` / `7` type `@` `#` `|`. macOS apps
> cannot tell left from right Option, so a JetBrains shortcut on `Alt + <digit>`
> (the Windows-style tool-window keys) is ported as `alt+<digit>` and swallows
> those characters in VS Code too. Move such shortcuts in your JetBrains keymap
> to a combination that types nothing, then re-run the port.

---

## ✅ Verify after install

Reload each editor window, then spot-check with the **editor** focused (not the
terminal). With the bundled `$default` keymap (or any Ctrl-based one) plus
`--layer windows-keymap`:

| Shortcut                                              | Expected                          |
|-------------------------------------------------------|-----------------------------------|
| `Ctrl + D`                                            | duplicate line                    |
| `Ctrl + W` · `Ctrl + Shift + W`                       | expand · shrink selection         |
| `Ctrl + B` · `Ctrl + Alt + B`                         | go to definition · implementation |
| `Ctrl + Alt + L` · `Ctrl + /`                         | reformat · comment line           |
| `Ctrl + Shift + A` · `Ctrl + N` / `Ctrl + Shift + N`  | Find Action · Go to Class / File  |
| terminal: `Ctrl + C` `Ctrl + D` `Ctrl + R` `Ctrl + P` | still hit the shell               |

---

## 🤝 Contributing

Contributions are welcome — bug reports, new IDE/editor coverage, better action
mappings.

- <span style="display: inline-flex; align-items: flex-start; gap: 10px;"><span>🧭</span><span>**Report a mapping gap.** Run `./port.py` and open `report.md`. If an action you use is under *"No VS Code command mapping"*
  but a VS Code command does exist, add the pair to `manualActionCommand` in `overrides.jsonc` and send a PR.</span></span>
- <span style="display: inline-flex; align-items: flex-start; gap: 10px;"><span>🧠</span><span>**Add a JetBrains product** → extend the `PRODUCTS` table in `resolve_keymap.py`.</span></span>
- <span style="display: inline-flex; align-items: flex-start; gap: 10px;"><span>💻</span><span>**Add an editor** → extend the `EDITORS` table in `install.py`.</span></span>
- <span style="display: inline-flex; align-items: flex-start; gap: 10px;"><span>🧪</span><span>**Run the tests** before opening a PR:</span></span>
  ```sh
  python3 -m unittest discover -s tests -v
  ```
- <span style="display: inline-flex; align-items: flex-start; gap: 10px;"><span>🇬🇧</span><span>Keep developer-facing text (code, comments, commit messages) in English.
  Commit messages follow Conventional Commits (`feat:`, `fix:`, `docs:`, …).</span></span>
- <span style="display: inline-flex; align-items: flex-start; gap: 10px;"><span>🚫</span><span>Don't commit the per-user build outputs — they are git-ignored for a reason.</span></span>

---

## 📄 License

Released under the **MIT License** — see [`LICENSE`](LICENSE). MIT is a good fit
here: the project is a thin tool, and the mapping data it bundles under
`vendor/kkato/` is itself MIT-licensed.

---

## 🙏 Credits

- <span style="display: inline-flex; align-items: flex-start; gap: 10px;"><span>💡</span><span>**Inspired by** [vlad-ogol/intellij-keymap-xml-exporter](https://github.com/vlad-ogol/intellij-keymap-xml-exporter)
  — the idea of turning an IntelliJ keymap into something portable.</span></span>
- <span style="display: inline-flex; align-items: flex-start; gap: 10px;"><span>🗺</span><span>**Mapping data**
  from [kasecato/vscode-intellij-idea-keybindings](https://github.com/kasecato/vscode-intellij-idea-keybindings)
  (`k--kato.intellij-idea-keybindings`). Its `ActionIdCommandMapping.json` and
  `KeystrokeKeyMapping.json` do the heavy lifting of matching IntelliJ actions
  and AWT keystrokes to their VS Code equivalents — without them this would have
  been a slog.</span></span>

<div align="center">
<sub>Built for people who switch editors more often than they switch keymaps.</sub>
</div>
