#!/bin/sh
# ============================================================================
# tools/gates.sh — the gate list.
#
# Builds the canonical compiler, the terminal IDE and the X11 GUI into the repo
# root, then runs EVERY gate the project reports, printing one line per gate as
# PASS / FAIL / NOT-RUN. Nothing else.
#
# PROJECT-MASTER.md section 6 should be "the output of this script on <commit>",
# so the numbers cannot drift from the tree.
#
# A gate that needs an environment this script cannot provide (X11, Windows)
# prints NOT-RUN with the reason, rather than being silently omitted.
#
# Usage:  sh tools/gates.sh            (from the repo root)
# ============================================================================
set -u

PASS=0; FAIL=0; SKIP=0
line() { printf '  %-28s %s\n' "$1" "$2"; }
ok()   { PASS=$((PASS+1)); line "$1" "PASS"; }
bad()  { FAIL=$((FAIL+1)); line "$1" "FAIL   $2"; }
skip() { SKIP=$((SKIP+1)); line "$1" "NOT-RUN $2"; }

[ -f src/r68_compiler_entry.asm ] || { echo "run this from the repo root"; exit 2; }

echo "Sutram gates — $(date -u +%Y-%m-%dT%H:%MZ)"
echo

# ---------------------------------------------------------------- build
NASM=${NASM:-nasm}
LD=${LD:-ld}
BUILD_FAIL=0
$NASM -f elf64 -I. src/r68_compiler_entry.asm -o /tmp/g_c.o 2>/tmp/g_c.log \
  && $LD -o ./sutram_compiler /tmp/g_c.o 2>>/tmp/g_c.log \
  || { bad "build: compiler" "see /tmp/g_c.log"; BUILD_FAIL=1; }
[ "$BUILD_FAIL" = 0 ] && line "build: compiler" "ok  ($(wc -c < sutram_compiler) B)"

$NASM -f elf64 ide/sutram_ide.asm -o /tmp/g_i.o 2>/tmp/g_i.log \
  && $LD -o ./sutram-ide /tmp/g_i.o 2>>/tmp/g_i.log \
  && line "build: terminal IDE" "ok  ($(wc -c < sutram-ide) B)" \
  || bad "build: terminal IDE" "see /tmp/g_i.log"

$NASM -f elf64 ide/sutram_gui_linux.asm -o /tmp/g_g.o 2>/tmp/g_g.log \
  && $LD -o ./sutram-gui /tmp/g_g.o 2>>/tmp/g_g.log \
  && line "build: X11 GUI" "ok  ($(wc -c < sutram-gui) B)" \
  || bad "build: X11 GUI" "see /tmp/g_g.log"

[ "$BUILD_FAIL" = 1 ] && { echo; echo "compiler did not build — gates not run"; exit 1; }
echo

# ---------------------------------------------------------------- the gates
run_gate() {                      # name, then the command
  name=$1; shift
  out=$("$@" 2>&1) || { bad "$name" "$(printf '%s' "$out" | tail -1 | cut -c1-60)"; return; }
  printf '%s' "$out" > /tmp/g_out.$$
  case "$name" in
    "regression suite")
      s=$(grep -oE 'PASS=[0-9]+|FAIL=[0-9]+|NO-EXPECTATION=[0-9]+' /tmp/g_out.$$ | tr '\n' ' ')
      case "$s" in *FAIL=[1-9]*) bad "$name" "$s";; *) ok "$name ($s)";; esac ;;
    "codegen shapes")   n=$(grep -c PASS /tmp/g_out.$$); [ "$n" -ge 12 ] && ok "$name ($n/12)" || bad "$name" "$n/12" ;;
    "language packs")   case "$(tail -1 /tmp/g_out.$$)" in *"33/33"*) ok "$name (33/33)";; *) bad "$name" "$(tail -1 /tmp/g_out.$$)";; esac ;;
    "library proofs")   case "$(tail -1 /tmp/g_out.$$)" in *"0 failed"*) ok "$name ($(tail -1 /tmp/g_out.$$))";; *) bad "$name" "$(tail -1 /tmp/g_out.$$)";; esac ;;
    "property proofs")  case "$(tail -1 /tmp/g_out.$$)" in *"86/86"*) ok "$name (86/86)";; *) bad "$name" "$(tail -1 /tmp/g_out.$$)";; esac ;;
    "module graph")     case "$(tail -1 /tmp/g_out.$$)" in *OK*) ok "$name";; *) bad "$name" "$(tail -1 /tmp/g_out.$$ | cut -c1-60)";; esac ;;
    "layer check")      case "$(tail -1 /tmp/g_out.$$)" in *"layers OK"*) ok "$name ($(tail -1 /tmp/g_out.$$ | sed 's/layers OK: //'))";; *) bad "$name" "$(tail -1 /tmp/g_out.$$)";; esac ;;
    "stdlib inventory") case "$(tail -1 /tmp/g_out.$$)" in *"modules"*) ok "$name ($(tail -1 /tmp/g_out.$$))";; *) bad "$name" "$(tail -1 /tmp/g_out.$$)";; esac ;;
    *)                  ok "$name" ;;
  esac
  rm -f /tmp/g_out.$$
}

run_gate "regression suite"  python3 tests/run_tests.py
run_gate "codegen shapes"    python3 tools/codegen_gate.py ./sutram_compiler
run_gate "language packs"    python3 tools/test_lang_packs.py ./sutram_compiler
run_gate "library proofs"    python3 tools/proof_lib.py --compiler ./sutram_compiler
run_gate "property proofs"   python3 tools/proof_props.py --compiler ./sutram_compiler
run_gate "layer check"       python3 tools/check_layers.py
run_gate "stdlib inventory"  python3 tools/gen_stdlib_ref.py
run_gate "module graph"      python3 -m unittest discover -s tests/module_graph -p 'test_*.py'

# the GUI needs an X server; say so rather than omitting it
if [ -n "${DISPLAY:-}" ] || [ -S /tmp/.X11-unix/X0 ]; then
  n=0; f=0
  for t in tools/test_x11_*.py; do
    SUTRAM_GUI="$PWD/sutram-gui" python3 "$t" >/dev/null 2>&1 && n=$((n+1)) || f=$((f+1))
  done
  [ "$f" = 0 ] && ok "X11 GUI protocol ($n/$n)" || bad "X11 GUI protocol" "$f of $((n+f)) failed"
else
  skip "X11 GUI protocol" "no DISPLAY and no /tmp/.X11-unix/X0"
fi

# Windows cannot be run here, and has never been run anywhere. Say it plainly.
skip "Windows execution" "cannot run here - never executed by anyone (Gate 6)"

# ---------------------------------------------------------------- summary
echo
echo "  ------------------------------------------"
printf '  %-28s %s\n' "PASS" "$PASS"
printf '  %-28s %s\n' "FAIL" "$FAIL"
printf '  %-28s %s\n' "NOT-RUN" "$SKIP"
echo
echo "  PASS, FAIL and NOT-RUN are separate on purpose."
echo "  A count that hides its own skips is worse than no count."
[ "$FAIL" = 0 ] || exit 1
exit 0
