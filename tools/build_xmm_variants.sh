#!/bin/sh
# R32: self-contained verification of verified FG2 -> experimental Stage 1.
# Standard-user only. Requires NASM + binutils on PATH; does NOT install them.
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
DEST=${1:-"$ROOT/build/xmm-stage1"}
mkdir -p "$DEST"
python3 "$ROOT/tools/verify_fg2_restoration.py"
# The compiler resolves .smlib and language packs adjacent to its executable.
ln -sfn "$ROOT/lib" "$DEST/lib"
ln -sfn "$ROOT/lang" "$DEST/lang"
# Do not use packaged / stale compiler binary as baseline. Rebuild exact
# independently verified R30 FG2 source from our archived snapshot.
nasm -f elf64 -I"$ROOT/" "$ROOT/compiler/verified_snapshots/FG2_R30_verified.asm.txt" -o "$DEST/fg2_ref.o"
ld -o "$DEST/fg2_ref" "$DEST/fg2_ref.o"
nasm -f elf64 -I"$ROOT/" "$ROOT/src/sutram_compiler.asm" -o "$DEST/off.o"
ld -o "$DEST/off" "$DEST/off.o"
nasm -f elf64 -DSUTRAM_EXPERIMENTAL_XMM_CACHE=1 -I"$ROOT/" "$ROOT/src/sutram_compiler.asm" -o "$DEST/on.o"
ld -o "$DEST/on" "$DEST/on.o"
python3 "$ROOT/tools/test_xmm_stage1.py" --baseline "$DEST/fg2_ref" \
    --off "$DEST/off" --on "$DEST/on"
# Build the Windows-target native compiler for PE-format audit; no Windows run.
if command -v ld >/dev/null 2>&1; then
    nasm -f win64 -dWINDOWS -I"$ROOT/" "$ROOT/src/sutram_compiler.asm" -o "$DEST/off-win.obj"
    ld -mi386pep --entry=_start -o "$DEST/off-win.exe" "$DEST/off-win.obj"
    nasm -f win64 -dWINDOWS -DSUTRAM_EXPERIMENTAL_XMM_CACHE=1 -I"$ROOT/" "$ROOT/src/sutram_compiler.asm" -o "$DEST/on-win.obj"
    ld -mi386pep --entry=_start -o "$DEST/on-win.exe" "$DEST/on-win.obj"
fi
printf '%s\n' 'PASS rebuilt verified FG2 release + experimental ELF compilers; Win64 PE build attempted' \
  'Do not enable Stage 1 by default unless realistic 126 A/B improves.'
