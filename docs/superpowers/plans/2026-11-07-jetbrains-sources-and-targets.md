# JetBrains Sources and Targets Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Android Studio and every JetBrains IDE selectable as keymap source and as install target, next to the existing VS Code-family targets.

**Architecture:** `resolve_keymap.py` learns the `Google/` config home and the `AndroidStudio` product. A new stdlib module `jb_keymap.py` renders and installs the resolved keymap XML as a new `(ported)` keymap. `install.py` discovers JetBrains config dirs as a second target family; they are opt-in (picker or `--only`), so non-interactive runs keep writing to VS Code-family editors only.

**Tech Stack:** Python 3 standard library, `unittest` (`python3 -m unittest discover -s tests -v`).

**Spec:** `docs/superpowers/specs/2026-11-07-jetbrains-sources-and-targets-design.md`

## Global Constraints

- Standard library only; no new dependencies.
- Existing backup convention: `<file>.bak-<YYYYmmdd-HHMMSS>`; JetBrains backups are `<file>.xml.bak-<stamp>` in `keymaps/`.
- Installed keymap name is `<source keymap name> (ported)`; file name is that string sanitised with `re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-")` plus `.xml`.
- Never modify the source IDE's own keymap files; never overwrite a target file without a backup.
- JetBrains targets are installed only when picked in the interactive picker or named via `--only`; `--dry-run` previews both families.
- The existing `select_targets(targets, args)` call shape and the `(folder, label, dst)` target tuple stay valid (existing tests use them).
- Code, comments, identifiers, commit messages in English; commits `type: description`, no attribution trailers.

## Review Focus

- Source keymap name containing `"`, `'` or `&` still yields well-formed XML (use `xml.sax.saxutils.quoteattr`).
- Target IDE config dir without a `keymaps/` dir: the dir is created on install.
- Source IDE is also a target: its original keymap file is untouched, a `(ported)` file appears next to it.
- Two installed versions of one product (`PhpStorm2025.3`, `PhpStorm2026.1`): `--only PhpStorm` selects both; the picker lists both.
- Lowercase config dir names (`Datagrip2026.2`) and non-IDE dirs in the JetBrains home (`consentOptions`, `Daemon`, `acp-agents`) are classified correctly.
- Running the install twice leaves one current file plus one backup per overwrite.
- Non-TTY run with a JetBrains IDE installed writes to VS Code-family editors only.

---

### Task 1: Gate — verify the parent-less keymap format in a real Android Studio

Manual; needs the owner (it writes into their IDE config). Do this before building.

- [ ] **Step 1:** Run `python3 resolve_keymap.py --product PhpStorm` to produce `source/*.resolved.xml`.
- [ ] **Step 2:** The owner copies that file as `<name>-ported-check.xml` into `~/Library/Application Support/Google/AndroidStudio2026.2.2/keymaps/` and changes the `name` attribute to `<name> (ported)`.
- [ ] **Step 3:** The owner restarts Android Studio and opens Settings → Keymap. Expected: `<name> (ported)` is listed and selectable, shortcuts show up. Record the result in the PR description.
- [ ] **Step 4:** If it is not listed or empty, stop and ask the owner: the fallback is to emit `parent="$default"` (or the chain root) in `render_ported_xml`; the signature and tests in Task 3 stay the same, only the output differs.

### Task 2: Android Studio as a source product

**Files:**
- Modify: `resolve_keymap.py` (`PRODUCTS`, `jetbrains_config_homes`, `install_search_roots`; add `CONFIG_DIR_PREFIXES`)
- Test: `tests/test_resolve_install.py`

**Interfaces:**
- Produces: `rk.PRODUCTS["AndroidStudio"] == ("Android Studio",)`; `rk.CONFIG_DIR_PREFIXES: tuple[str, ...]` = `("PhpStorm", "IntelliJIdea", "IdeaIC", "WebStorm", "PyCharm", "DataGrip", "GoLand", "RubyMine", "CLion", "Rider", "RustRover", "AndroidStudio")`, matched case-insensitively by Task 4; `jetbrains_config_homes()` additionally returns the existing `Google` vendor dir (macOS `~/Library/Application Support/Google`, Windows `%APPDATA%\Google`, Linux `$XDG_CONFIG_HOME|~/.config` + `/Google`).

- [ ] **Step 1: Write failing tests** in `tests/test_resolve_install.py` (new class `AndroidStudio`), following the existing fake-tree style:
  - `test_discover_installs_finds_android_studio`: a fake `*.app/Contents/Resources/product-info.json` with `{"name": "Android Studio", "version": "AI-262.1", "dataDirectoryName": "AndroidStudio2026.2.2"}` and a `lib/` with a jar is returned by `discover_installs("AndroidStudio")`.
  - `test_config_dir_found_under_google_home`: with `Path.home` patched to a tmp dir, `IS_MAC` true and `~/Library/Application Support/Google/AndroidStudio2026.2.2/keymaps` present, `resolve_config_dir("AndroidStudio", None, "AndroidStudio2026.2.2")` returns that dir; with `data_dir_name=""` the `AndroidStudio*` fallback returns it too.
  - `test_google_home_listed_only_when_present`.
- [ ] **Step 2:** Run `python3 -m unittest tests.test_resolve_install -v`. Expected: the new tests FAIL.
- [ ] **Step 3: Implement** the `PRODUCTS` entry, `CONFIG_DIR_PREFIXES`, the `Google` home in `jetbrains_config_homes`, and `/opt/android-studio` plus `~/android-studio` in the Linux branch of `install_search_roots`.
- [ ] **Step 4:** Run the same command. Expected: all PASS.
- [ ] **Step 5: Commit** `feat: resolve keymaps from Android Studio`.

### Task 3: Render and install a ported keymap (`jb_keymap.py`)

**Files:**
- Create: `jb_keymap.py`
- Test: `tests/test_jb_keymap.py`

**Interfaces:**
- Produces:
  - `PORTED_SUFFIX = " (ported)"`
  - `ported_name(source_name: str) -> str`
  - `read_keymap_name(xml_text: str) -> str` (raises `ValueError` without a `<keymap … name=…>`; accepts `"` or `'` quoting)
  - `render_ported_xml(xml_text: str) -> tuple[str, str]` → `(rewritten_xml, new_name)`; only the `name` attribute of the `<keymap` line changes, comments and actions are kept byte-identical
  - `target_filename(name: str) -> str`
  - `find_resolved_file(explicit: str | None, source_dir: Path) -> Path` (explicit path must exist; otherwise exactly one `*.resolved.xml` in `source_dir`; zero or several → `SystemExit` with a message listing candidates)
  - `install_keymap(resolved: Path, keymaps_dir: Path, *, dry_run: bool, stamp: str) -> Path` returns the destination; creates `keymaps_dir`; existing destination is copied to `<dst.name>.bak-<stamp>` first; `dry_run` writes nothing

- [ ] **Step 1: Write failing tests** `tests/test_jb_keymap.py` (tmp dirs via a helper like `_tmpdir` in the existing tests):
  - `test_ported_name_appends_suffix`: `ported_name("macOS") == "macOS (ported)"`.
  - `test_render_rewrites_only_name`: input with a leading `<!-- … -->` comment and `<keymap version="1" name="macOS">` yields the same text except `name="macOS (ported)"`; returns `("…", "macOS (ported)")`.
  - `test_render_quotes_special_characters`: source name `A "B" & C` produces XML that `xml.etree.ElementTree.fromstring` parses, with the attribute equal to `A "B" & C (ported)`.
  - `test_read_keymap_name_missing_raises_valueerror`.
  - `test_target_filename_sanitised`: `target_filename("jeffry (x) (ported)") == "jeffry-x-ported.xml"`.
  - `test_find_resolved_file_single / none / several / explicit_missing`: single returns it; none and several raise `SystemExit` (several: message contains every file name); explicit missing raises `SystemExit`.
  - `test_install_creates_missing_keymaps_dir`.
  - `test_install_backs_up_existing_destination`: second install leaves `<name>.xml` plus one `<name>.xml.bak-<stamp>` with the old content.
  - `test_install_leaves_source_keymap_untouched`: a `macOS.xml` already in the dir is byte-identical afterwards and `macOS-ported.xml` exists.
  - `test_install_dry_run_writes_nothing`.
- [ ] **Step 2:** Run `python3 -m unittest tests.test_jb_keymap -v`. Expected: FAIL (module missing).
- [ ] **Step 3: Implement** `jb_keymap.py` with the signatures above; name rewrite is a regex substitution on the `<keymap` tag using `quoteattr` for the new value.
- [ ] **Step 4:** Run the same command. Expected: all PASS.
- [ ] **Step 5: Commit** `feat: add jb_keymap module to install ported JetBrains keymaps`.

### Task 4: JetBrains install targets in `install.py`

**Files:**
- Modify: `install.py` (`discover_jetbrains_targets`, `target_matches`, `select_targets`, `build_arg_parser`, `main`)
- Test: `tests/test_install_select.py`, `tests/test_install_jetbrains.py`

**Interfaces:**
- Consumes: Task 2 `rk.jetbrains_config_homes`, `rk.CONFIG_DIR_PREFIXES`; Task 3 `jb_keymap.find_resolved_file`, `jb_keymap.install_keymap`.
- Produces:
  - `discover_jetbrains_targets() -> list[tuple[str, str, Path]]` — `(folder, label, keymaps_dir)`; one entry per child dir of each config home whose name matches `^(<prefix>)\d` case-insensitively and that has `options/` or `keymaps/`; `label` = dir name; `keymaps_dir` = `<dir>/keymaps` (may not exist yet); sorted by folder name, deduped by `keymaps_dir`
  - `target_matches(folder: str, wanted: set[str]) -> bool` — exact folder name, or case-insensitive prefix (`PhpStorm` matches `PhpStorm2025.3`)
  - `select_targets(targets, args, default=None)` — identical behaviour, except every "no choice made" return (single target, no TTY, prompt unavailable) returns `default` when it is not `None`; `--only`/`--dry-run` still return `targets`
  - CLI: new `--resolved PATH`; heading `Install into which IDEs?`

- [ ] **Step 1: Write failing tests:**
  - `tests/test_install_select.py`: `test_default_used_for_non_tty` (`select_targets(FAKE, _args(), default=FAKE[:1]) == FAKE[:1]`), `test_default_used_for_single_target`, `test_only_ignores_default`, `test_picker_ignores_default`.
  - `tests/test_install_jetbrains.py` (patch `rk.jetbrains_config_homes` to a tmp home):
    - `test_discovers_ide_dirs_only`: `PhpStorm2025.3`, `Datagrip2026.2`, `AndroidStudio2026.2.2` (with `options/` or `keymaps/`) are found; `consentOptions`, `Daemon`, `acp-agents`, and an IDE-named dir without `options/`/`keymaps/` are not.
    - `test_two_versions_listed` and `test_target_matches_prefix_and_exact` (`PhpStorm` matches both versions; `AndroidStudio2026.2.2` matches exactly; `Code` matches neither).
    - `test_main_non_interactive_skips_jetbrains`: with one VS Code editor and one JetBrains IDE present, `main(["--file", f, "--resolved", r])` writes the VS Code keybindings and leaves the JetBrains `keymaps/` empty.
    - `test_main_only_selects_jetbrains`: `--only AndroidStudio` installs the ported keymap there and does not touch VS Code.
    - `test_main_dry_run_lists_both_families_writes_nothing`.
    - `test_main_unknown_only_name_warns`.
    - `test_main_vscode_only_flow_unchanged` (regression: no JetBrains dirs → same output lines as before: `backup`, `wrote`, `Reload each window` footer).
    - `test_main_jetbrains_footer_wording`: footer mentions reopening Settings → Keymap, not "Reload each window", when only JetBrains targets were written.
- [ ] **Step 2:** Run `python3 -m unittest tests.test_install_select tests.test_install_jetbrains -v`. Expected: new tests FAIL.
- [ ] **Step 3: Implement** the interfaces above. In `main`: build both target lists; `--only` filters VS targets by exact folder name and JetBrains targets with `target_matches`, and warns for names matching neither; run `select_targets(vs + jb, args, default=vs)`; split the result by membership in the JetBrains list; VS Code targets use the existing write path unchanged; JetBrains targets call `jb_keymap.find_resolved_file(args.resolved, ROOT / "source")` then `install_keymap`; the "no target found" message names both families; the existing `--file` existence check applies only when a VS Code target is selected.
- [ ] **Step 4:** Run `python3 -m unittest discover -s tests -v`. Expected: all PASS, including the untouched existing tests.
- [ ] **Step 5: Commit** `feat: install ported keymaps into JetBrains IDEs`.

### Task 5: `port.py` wiring and README

**Files:**
- Modify: `resolve_keymap.py` (module variable `last_output: Path | None = None`, set in `main` after `write_resolved`), `port.py` (`--resolved`; pass the resolved path to install), `README.md`
- Test: `tests/test_resolve_install.py`, `tests/test_port_args.py`

**Interfaces:**
- Consumes: Task 4 `install.py --resolved`.
- Produces: `rk.last_output`; `port.py --resolved PATH` (install group); `port.main` passes `--resolved <rk.last_output>` to install when the resolve step ran, or the user's value when `--skip-resolve` is used.

- [ ] **Step 1: Write failing tests:** `test_main_records_last_output` (after a `resolve_keymap.main([...])` against a fake install, `rk.last_output` equals the printed output path; reuse the fake-tree helpers); `tests/test_port_args.py::test_resolved_flag_is_forwarded` (patch `resolve_keymap.main`, `generate.main`, `install.main` with recorders; `port.main(["--product", "AndroidStudio"])` forwards `--product AndroidStudio` to resolve and `--resolved <last_output>` to install; with `--skip-resolve --resolved X` forwards `X`).
- [ ] **Step 2:** Run both test modules. Expected: FAIL.
- [ ] **Step 3: Implement** the wiring. README: add Android Studio and the JetBrains target family to the feature list, the `install.py` row (`--resolved`, opt-in behaviour, `.xml.bak-<stamp>`), the `--only` description (config-dir names and product prefixes), a short "Install into JetBrains IDEs" usage example, and the "Add an editor" hint; keep house style from `~/.claude/rules/documentation.md`.
- [ ] **Step 4:** Run `python3 -m unittest discover -s tests -v`. Expected: all PASS.
- [ ] **Step 5: Commit** `feat: forward resolved keymap through port.py and document JetBrains targets`.

### Task 6: End-to-end verification

- [ ] **Step 1:** `python3 -m unittest discover -s tests -v`. Expected: all PASS.
- [ ] **Step 2:** `./port.py --product AndroidStudio --dry-run`. Expected: resolves the active Android Studio keymap and lists VS Code-family and JetBrains targets under `would write`.
- [ ] **Step 3:** With the owner's go-ahead (it writes into their IDE config): run `./port.py --product PhpStorm --only AndroidStudio` and confirm `<name> (ported)` is selectable in Android Studio (same check as Task 1). Expected: the original keymaps are unchanged.
- [ ] **Step 4:** `git status` clean, branch ready for `/youtrack-task pr`.
