# Task: Windows-Navigation & IDE-Keybindings Port (Home/End, Ctrl+Arrows, Tab-Switch)

## Kontext & Ziel
Im Rahmen des Setups für ein Windows-Tastaturlayout auf macOS (Schweizer Tastatur) sollen IDE-spezifische Tastenbelegungen **nicht** in Karabiner-Elements (`karabiner-windows-keyboard-mapping-macos`), sondern ausschliesslich über dieses Repository (`intelli-key-port`) verwaltet und portiert werden.

Ziel ist es, dass Standard-Windows-Navigations-Shortcuts konsistent sowohl im Editor-Fenster als auch in Text-Eingabefeldern (insbesondere in der Agenten-Chat-Ansicht von **AntiGravity IDE**) funktionieren und nach jedem IDE-Reload / Update erhalten bleiben.

---

## Anforderungen

### 1. Zeilen- & Dokumenten-Navigation (Home / End)
Standardmässig verhält sich macOS bei `Home` / `End` anders als Windows. Über `overrides.jsonc` müssen folgende Mappings für alle Text-Eingaben (`textInputFocus`) definiert werden:

| Tastenkombination | Befehl | Kontext (`when`) |
| :--- | :--- | :--- |
| `home` | `cursorLineStart` | `textInputFocus` |
| `shift+home` | `cursorLineStartSelect` | `textInputFocus` |
| `ctrl+home` | `cursorTop` | `textInputFocus` |
| `ctrl+shift+home` | `cursorTopSelect` | `textInputFocus` |
| `end` | `cursorLineEnd` | `textInputFocus` |
| `shift+end` | `cursorLineEndSelect` | `textInputFocus` |
| `ctrl+end` | `cursorBottom` | `textInputFocus` |
| `ctrl+shift+end` | `cursorBottomSelect` | `textInputFocus` |

### 2. Wortweises Navigieren (Ctrl + Links / Rechts)
Im Windows-Layout springt `Ctrl+Left` bzw. `Ctrl+Right` wortweise:

| Tastenkombination | Befehl | Kontext (`when`) |
| :--- | :--- | :--- |
| `ctrl+left` | `cursorWordLeft` | `textInputFocus` |
| `ctrl+right` | `cursorWordRight` | `textInputFocus` |
| `ctrl+shift+left` | `cursorWordLeftSelect` | `textInputFocus` |
| `ctrl+shift+right` | `cursorWordRightSelect` | `textInputFocus` |

> [!NOTE]
> Sicherstellen, dass widersprüchliche Standard-Bindings von VS Code / macOS für `alt+left`/`alt+right` bzw. `ctrl+left`/`ctrl+right` (z.B. Terminal-Switches oder native macOS Space-Wechsel) sauber entkoppelt bzw. überschrieben werden.

### 3. Editor Tab-Navigation
Um Konflikte mit Wort-Sprüngen und Standard-Kombinationen zu vermeiden:

| Tastenkombination | Befehl | Kontext |
| :--- | :--- | :--- |
| `ctrl+cmd+left` | `workbench.action.previousEditor` | Global |
| `ctrl+cmd+right` | `workbench.action.nextEditor` | Global |

### 4. Kompatibilität mit AntiGravity IDE Agenten-Chat
In AntiGravity IDE ist das Chat-Inputfeld ein separates Widget. Mit dem Scope `textInputFocus` greifen die Cursor- und Navigationsbefehle universell sowohl im normalen Code-Editor (`editorTextFocus`) als auch im Agenten-Eingabefeld (`inputBoxFocus`).

---

## Umsetzungsschritte in `intelli-key-port`

1. [ ] **`overrides.jsonc` aktualisieren**:
   - Die oben aufgeführten Keybindings in die `entries`-Sektion von `overrides.jsonc` einfügen.
   - Entfernen oder Überschreiben eventuell doppelter macOS Cmd-Defaults prüfen.
2. [ ] **Keybindings neu generieren**:
   ```bash
   python3 generate.py
   ```
3. [ ] **Installation in Editoren**:
   ```bash
   python3 install.py
   ```
   (Prüfen, ob "Antigravity IDE" und "Antigravity" in `install.py` erkannt und unterstützt werden).
4. [ ] **Verifikation**:
   - Code-Editor: Wortsprung (`Ctrl+Left/Right`), Zeilenanfang/-ende (`Home`/`End`), Dokumentanfang/-ende (`Ctrl+Home/End`) und Selektion mit `Shift`.
   - Agent-Chat: Dieselben Shortcuts im Chat-Eingabefeld von AntiGravity IDE testen.
