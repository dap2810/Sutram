#!/bin/sh
# Build Sutram for Windows (native PE). Needs nasm + ld with PE support.
#   ./win/build-windows.sh          -> win/sutram.exe
set -e
cd "$(dirname "$0")/.."
# locate nasm: PATH first, else a local ./nasm/usr/bin/nasm
if command -v nasm >/dev/null 2>&1; then NASM=nasm
elif [ -x ./nasm/usr/bin/nasm ]; then NASM=./nasm/usr/bin/nasm
else echo "nasm not found (install nasm or set NASM=...)"; exit 1; fi
"$NASM" -f win64 -dWINDOWS -I. src/sutram_compiler.asm -o /tmp/sutram_win.obj
ld -mi386pep --entry=_start -o win/sutram.exe /tmp/sutram_win.obj
file win/sutram.exe
echo "built win/sutram.exe"
