#!/bin/sh
# Usage, from the repository root:  sh Claude-to-Sarvam/evidence-r9/F1/run-f1.sh [compiler]
# Compiles each F1 file with the given compiler (default ./sutram_compiler) and
# prints the expected and the actual output side by side.
C=${1:-./sutram_compiler}
D=Claude-to-Sarvam/evidence-r9/F1
T=${TMPDIR:-/tmp}/sutram-f1.$$
mkdir -p "$T"
for f in "$D"/f1_*.sm; do
  b=$(basename "$f" .sm)
  want=$(sed -n 's/^# Expected: //p' "$f")
  "$C" "$f" "$T/$b" > "$T/$b.cc" 2>&1 || { echo "$b: COMPILE ERROR"; cat "$T/$b.cc"; continue; }
  got=$(timeout 5 "$T/$b" 2>/dev/null | head -20 | tr '\n' ' '); rc=$?
  [ -z "$got" ] && got="(no output)"
  echo "$b"
  echo "    expected: $want"
  echo "    got:      $got"
done
rm -rf "$T"
