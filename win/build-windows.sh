#!/bin/sh
# Cross-build the canonical R68 entry; Python is a developer validator only.
# NASM and a PE-capable GNU ld must already be installed. No runtime dependencies added.
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
exec python3 "$ROOT/tools/r69_build.py" --target windows --output "$ROOT/win/sutram.exe" "$@"
