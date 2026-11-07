# Design: any JetBrains IDE (incl. Android Studio) as keymap source and target

Issue: IKP-2. Date: 2026-11-07.

## Intent

intelli-key-port turns the active keymap of one JetBrains IDE into a VS Code
`keybindings.json` overlay. Two limits get in the way of the owner's day-to-day
setup:

- Android Studio cannot be a source. It keeps its config under
  `Google/AndroidStudio<version>`, not `JetBrains/`, and is not in the product list.
- JetBrains IDEs cannot be a target. Moving a keymap from PhpStorm to Android
  Studio or GoLand is a manual export/copy today.

Goal: choose **any JetBrains IDE or Android Studio as the source**, and install into
**any combination of JetBrains IDEs, Android Studio and VS Code-family editors**
(VS Code, Antigravity, Cursor, ...).

## Goals

- Android Studio is a known `--product` for the resolve step and is found on
  macOS, Linux and Windows (install and config dir).
- The install step discovers JetBrains-family targets (every `<Product><version>`
  config dir that has `options/` or `keymaps/`, including Android Studio) next to the
  existing VS Code-family targets, and offers all of them in the existing picker.
- Installing into a JetBrains target writes the resolved keymap as a selectable
  keymap in that IDE's `keymaps/` directory.
- `--only` and `--dry-run` keep working and cover both target families.
- Unit tests for discovery, install and the unchanged VS Code path; README updated.

## Non-goals

- VS Code (or any editor) as a **source**. The source is always a JetBrains IDE.
- Applying the `overrides.jsonc` layers to JetBrains output. They are VS Code-specific.
- Switching the active keymap in the target IDE. The user selects it in Settings.
- Managing plugins or other IDE settings.

## Anti-goals

- Never modify or overwrite the source IDE's own keymap files.
- Never replace an existing target file without a timestamped backup next to it.
- A change that breaks the current PhpStorm → VS Code flow, even if the new flow works.

## Constraints

- Plain Python 3 standard library, no new dependencies (project convention).
- Reuse existing mechanics: `resolve_keymap.py` discovery, `install.py` picker,
  backup convention (`<file>.bak-<timestamp>`).
- Android Studio facts, verified on the owner's machine:
  `product-info.json` has `name: "Android Studio"`, `dataDirectoryName:
  "AndroidStudio2026.2.2"`, vendor Google; config dir is
  `~/Library/Application Support/Google/AndroidStudio2026.2.2` with `keymaps/` and
  `options/mac/`.

## Design

### 1. Source side (`resolve_keymap.py`)

- Add `"AndroidStudio": ("Android Studio",)` to `PRODUCTS`.
- `jetbrains_config_homes()` also returns the vendor folder `Google` on each
  platform (macOS `~/Library/Application Support/Google`, Windows `%APPDATA%\Google`,
  Linux `$XDG_CONFIG_HOME/Google`). The existing exact match by `dataDirectoryName` and
  the `<product>*` fallback then find `AndroidStudio…` without further changes.
- Extend `install_search_roots()` with the usual Android Studio locations
  (`/opt/android-studio`, `~/android-studio`, Toolbox is already covered).

### 2. Target discovery (`install.py`)

- Extract a function that lists JetBrains config dirs: for each config home from
  `resolve_keymap.jetbrains_config_homes()`, every child dir with `options/` or
  `keymaps/`. A target is `(family="jetbrains", folder=<dir name>, label=<readable
  name>, dst=<dir>/keymaps)`.
- VS Code-family targets keep their current tuple shape; add a `family` field so
  the install loop can dispatch. Dedupe by destination as today.
- The picker lists both families, labelled `<label>  (<path>)`. Heading changes to
  "Install into which IDEs?".

### 3. Install (`install.py`)

- VS Code family: unchanged (`keybindings.generated.json` → `User/keybindings.json`).
- JetBrains family: write the resolved keymap XML to `<config>/keymaps/<name>.xml`.
- Input file: new `--resolved PATH`, default the newest `source/*.resolved.xml`.
  `port.py` passes the file `resolve_keymap` just wrote.
- The resolved XML has no `parent` (it is flattened), so the target IDE needs no
  parent keymap.
- Installed name: `<source keymap name> (ported)`, in both the `name` attribute
  and the file name, so a target that is also the source never overwrites the
  original. If the file exists, back it up first, then overwrite (re-runs update it).
- Output reminds the user to reopen Settings → Keymap (restart if the IDE was running).

### 4. CLI (`port.py`)

- `--only` accepts names of both families: VS Code folder names (`Code`, `Cursor`)
  and JetBrains config-dir names (`AndroidStudio2026.2.2`, `PhpStorm2025.3`).
- `--product AndroidStudio` selects the source. Flow stays resolve → generate →
  install; the generate step still runs (cheap, git-ignored artifacts).

## Acceptance criteria (from IKP-2, refined)

- [ ] `--product AndroidStudio` resolves the active keymap of Android Studio.
- [ ] Android Studio and other JetBrains IDEs appear as install targets next to VS Code-family editors.
- [ ] The resolved keymap lands in the target's `keymaps/` as a new, selectable keymap; the source keymap is untouched; an existing target file is backed up.
- [ ] `--only`, `--dry-run` and the picker work for both target families.
- [ ] Tests cover success, missing install/config, several versions, backup and collision with the source IDE; the VS Code path has a regression test.
- [ ] README documents the new sources and targets.

## Decided by the owner

- Sources: all JetBrains IDEs and Android Studio.
- Targets: all JetBrains IDEs, Android Studio, and VS Code-family editors.

## Default selection (decided by the owner)

JetBrains targets are **opt-in**: they are installed only when picked in the
interactive picker or named with `--only`. A non-interactive run without `--only`
(script, CI, no TTY, single hit) keeps writing to VS Code-family editors only, so the
current flow is unchanged. `--dry-run` previews all discovered targets of both families.

## My calls (flag in review)

- Installed keymap name is `<source keymap name> (ported)`; the target file name is the
  same string sanitised like `write_resolved` does (`-` for runs of other characters).
  The `name` attribute is rewritten with a targeted text substitution on the
  `<keymap ...>` line; the leading comments are kept.
- A hand-made keymap that has the exact same name in the target is overwritten after a
  backup. Backups are `<file>.xml.bak-<timestamp>` in `keymaps/`; the `.bak-…` suffix
  means the IDE does not list them (the owner's keymap dirs already contain such files).
- No OS- or IDE-specific filtering of actions or mouse shortcuts: unknown action IDs are
  ignored by the IDE. If the real-IDE check (below) fails, fall back to emitting a
  `parent` keymap.
- Verify the parent-less format in a real Android Studio **first** (manual install of a
  resolved file), then build.
- `--resolved PATH` is the input flag. `port.py` always passes it explicitly. A standalone
  `install.py` run with several `source/*.resolved.xml` files and no `--resolved` stops
  and lists them instead of guessing "newest".
- `--only` matches a config-dir name exactly (`AndroidStudio2026.2.2`) or a product prefix
  (`AndroidStudio`, `PhpStorm`) for all installed versions; unknown names warn as today.
- Messages are family-aware: "no target found" names the families searched, and the
  footer says "Reload each window" only for VS Code-family targets and "Reopen
  Settings → Keymap (restart a running IDE)" for JetBrains targets.
- Exact Linux/Windows Android Studio search roots are my guess; only macOS is verified.
- A picker pre-selects nothing special, as today.
