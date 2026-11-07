#!/usr/bin/env bash
# Run the whole unit-test suite from anywhere: bash tests/run.sh
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
exec python3 -m unittest discover -s tests -v
