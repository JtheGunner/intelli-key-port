# source/

`resolve_keymap.py` writes `<active-keymap-name>.resolved.xml` here - a flat,
fully-inherited copy of your IDE's **active** keymap. It is per-user output and
is git-ignored.

No JetBrains IDE on this machine? Drop a raw *Settings -> Keymap -> gear ->
Export Keymap* `.xml` here (any file name) and run `python3 generate.py`
directly - it falls back to any `<keymap>` XML in this folder.
