#!/bin/sh
# Developer build only. Does not download/install tools or run generated code.
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
exec python3 "$ROOT/tools/r69_build.py" --target linux --output "$ROOT/sutram_compiler" "$@"
