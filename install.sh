#!/usr/bin/env bash
# Deploy keybindings.generated.json to VS Code + both Antigravity variants.
# Each target is backed up with a timestamp first. Idempotent.
set -euo pipefail

cd "$(dirname "$0")"
SRC="keybindings.generated.json"
[[ -f "$SRC" ]] || { echo "run generate.py first ($SRC missing)"; exit 1; }

STAMP="$(date +%Y%m%d-%H%M%S)"
APPSUP="$HOME/Library/Application Support"

TARGETS=(
  "$APPSUP/Code/User/keybindings.json"
  "$APPSUP/Antigravity/User/keybindings.json"
  "$APPSUP/Antigravity IDE/User/keybindings.json"
)

for dst in "${TARGETS[@]}"; do
  dir="$(dirname "$dst")"
  if [[ ! -d "$dir" ]]; then
    echo "skip (not installed): $dst"
    continue
  fi
  if [[ -f "$dst" ]]; then
    cp -p "$dst" "$dst.bak-$STAMP"
    echo "backup: $dst.bak-$STAMP"
  fi
  cp "$SRC" "$dst"
  echo "wrote:  $dst"
done

echo
echo "Done. Restart the editors (or run 'Developer: Reload Window') to pick up the changes."
