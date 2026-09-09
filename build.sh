#!/usr/bin/env bash
# Full rebuild: resolve PhpStorm's keymap chain -> generate keybindings + report.
# Pass-through args go to resolve_keymap.py (e.g. --product IntelliJIdea --keymap "name").
set -euo pipefail
cd "$(dirname "$0")"
python3 resolve_keymap.py "$@"
echo
python3 generate.py
echo
echo "next: ./install.sh   (backs up + deploys to VS Code + Antigravity)"
