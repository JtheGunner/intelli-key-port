#!/usr/bin/env bash
# Thin wrapper around the cross-platform installer.
exec python3 "$(dirname "$0")/install.py" "$@"
