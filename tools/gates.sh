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

# R13: the committed Linux binaries must be executable, or a fresh checkout cannot run
# them (tests/run_tests.py stopped with PermissionError). A merge that uploads files one
# by one loses the mode; this gate says so instead of the next newcomer finding out.
# R19: it runs FIRST, because tests/run_tests.py sets +x on a copy it finds unset
# (with a NOTE), and the build step below rewrites the three binaries with ld, which
# makes them executable: a check made after either would hide the loss.
# R19: outside a git checkout (a tarball, a zip from GitHub) the gate checks the
# files themselves instead of the index, so it never says NOT-RUN. The two
# readings agree when the tree is the committed one; they differ only after a
# chmod that is not yet in the index, which `git ls-files -s` would still show.
EXES="sutram_compiler sutram-ide sutram-gui sutram-fmt sutram-link sutram-elf2smo sutram-coff2smo"
if command -v git >/dev/null 2>&1 && git rev-parse --git-dir >/dev/null 2>&1; then
  m=$(git ls-files -s $EXES | awk '$1 != "100755" {print $4}' | tr '\n' ' ')
  for f in $EXES; do git ls-files --error-unmatch "$f" >/dev/null 2>&1 || m="$m$f(not committed) "; done   # R28: a missing one is not a pass
  [ -z "$m" ] && ok "committed modes ($(echo $EXES | wc -w) x 100755, git index)" || bad "committed modes" "not 100755: $m(git update-index --chmod=+x)"
else
  m=""; for f in $EXES; do [ -x "$f" ] || m="$m$f "; done
  [ -z "$m" ] && ok "committed modes ($(echo $EXES | wc -w) executable, no git: the files' own mode)" || bad "committed modes" "not executable: $m(chmod +x; in git also update-index --chmod=+x)"
fi


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

$NASM -f elf64 linker/sutram_link.asm -o /tmp/g_l.o 2>/tmp/g_l.log \
  && $LD -o ./sutram-link /tmp/g_l.o 2>>/tmp/g_l.log \
  && line "build: linker (R28)" "ok  ($(wc -c < sutram-link) B)" \
  || bad "build: linker (R28)" "see /tmp/g_l.log"

$NASM -f elf64 linker/sutram_elf2smo.asm -o /tmp/g_e.o 2>/tmp/g_e.log \
  && $LD -o ./sutram-elf2smo /tmp/g_e.o 2>>/tmp/g_e.log \
  && line "build: ELF reader (R32)" "ok  ($(wc -c < sutram-elf2smo) B)" \
  || bad "build: ELF reader (R32)" "see /tmp/g_e.log"

$NASM -f elf64 -I. linker/sutram_coff2smo.asm -o /tmp/g_k.o 2>/tmp/g_k.log \
  && $LD -o ./sutram-coff2smo /tmp/g_k.o 2>>/tmp/g_k.log \
  && line "build: COFF reader (R35)" "ok  ($(wc -c < sutram-coff2smo) B)" \
  || bad "build: COFF reader (R35)" "see /tmp/g_k.log"

[ "$BUILD_FAIL" = 1 ] && { echo; echo "compiler did not build — gates not run"; exit 1; }
echo

# ---------------------------------------------------------------- the gates
run_gate() {                      # name, then the command
  # NOTE: do not judge a gate by its exit code. tests/run_tests.py exits non-zero
  # even when every test passes, so the exit code is parsed out of the output instead.
  # Claude caught this as a false positive on every run.
  name=$1; shift
  out=$("$@" 2>&1)
  printf '%s' "$out" > /tmp/g_out.$$
  case "$name" in
    "regression suite")
      s=$(grep -oE 'PASS=[0-9]+|FAIL=[0-9]+|NO-EXPECTATION=[0-9]+' /tmp/g_out.$$ | tr '\n' ' ')
      SUITE_PASS=$(printf '%s' "$s" | grep -oE 'PASS=[0-9]+' | head -1 | cut -d= -f2)
      case "$s" in *FAIL=[1-9]*) bad "$name" "$s";; *) ok "$name ($s)";; esac ;;
    "codegen shapes")   n=$(grep -c PASS /tmp/g_out.$$); [ "$n" -ge 12 ] && ok "$name ($n/12)" || bad "$name" "$n/12" ;;
    "language packs")   case "$(tail -1 /tmp/g_out.$$)" in *"33/33"*) ok "$name (33/33)";; *) bad "$name" "$(tail -1 /tmp/g_out.$$)";; esac ;;
    "library proofs")   case "$(tail -1 /tmp/g_out.$$)" in *"0 failed"*) ok "$name ($(tail -1 /tmp/g_out.$$))";; *) bad "$name" "$(tail -1 /tmp/g_out.$$)";; esac ;;
    "property proofs")  case "$(tail -1 /tmp/g_out.$$)" in *"86/86"*) ok "$name (86/86)";; *) bad "$name" "$(tail -1 /tmp/g_out.$$)";; esac ;;
    "guard pages")      line=$(tail -1 /tmp/g_out.$$); case "$line" in *", 0 failed"*) ok "$name ($(echo "$line" | sed 's/guard pages: //; s/, 0 failed//'))";; *) bad "$name" "${line:-no summary}";; esac ;;
    "module graph")     case "$(tail -1 /tmp/g_out.$$)" in *OK*) ok "$name";; *) bad "$name" "$(tail -1 /tmp/g_out.$$ | cut -c1-60)";; esac ;;
    "layer check")      case "$(tail -1 /tmp/g_out.$$)" in *"layers OK"*) ok "$name ($(tail -1 /tmp/g_out.$$ | sed 's/layers OK: //'))";; *) bad "$name" "$(tail -1 /tmp/g_out.$$)";; esac ;;
    "performance")
      # the summary line is not the last line; look for it anywhere in the output
      line=$(grep -E "[0-9]+ ran, [0-9]+ failed" /tmp/g_out.$$ | tail -1)
      case "$line" in *", 0 failed"*) ok "$name ($line)";; *) bad "$name" "${line:-no summary}";; esac ;;
    "stdlib inventory") case "$(tail -1 /tmp/g_out.$$)" in *"modules"*) ok "$name ($(tail -1 /tmp/g_out.$$))";; *) bad "$name" "$(tail -1 /tmp/g_out.$$)";; esac ;;
    "version string")   case "$(tail -1 /tmp/g_out.$$)" in PASS*) ok "$name ($(tail -1 /tmp/g_out.$$ | sed 's/PASS version //'))";; *) bad "$name" "$(tail -1 /tmp/g_out.$$ | cut -c6-90)";; esac ;;
    "formatted tree")   case "$(tail -1 /tmp/g_out.$$)" in FORMATTED) ok "$name";; *) bad "$name" "$(grep -c 'would change' /tmp/g_out.$$) file(s) would change: $(grep -m1 'would change' /tmp/g_out.$$ | cut -c15-70)";; esac ;;
    "operator precedence") line=$(head -1 /tmp/g_out.$$); case "$line" in *"; 0 disagree"*) ok "$name ($(echo "$line" | sed 's/;.*//'))";; *) bad "$name" "${line:-no summary}";; esac ;;
    "crash corpus")     line=$(tail -1 /tmp/g_out.$$); case "$line" in *", 0 failed"*) ok "$name ($(echo "$line" | sed 's/crash corpus: //'))";; *) bad "$name" "${line:-no summary}";; esac ;;
    "keyword packs built in") case "$(tail -1 /tmp/g_out.$$)" in "BUILT-IN PACKS CURRENT"*) ok "$name (11, = lang/*.lang)";; *) bad "$name" "$(tail -1 /tmp/g_out.$$ | cut -c1-70)";; esac ;;
    "pack found without lang/") line=$(tail -1 /tmp/g_out.$$); case "$line" in *", 0 failed"*) ok "$name ($(echo "$line" | sed 's/lang built-in: //'))";; *) bad "$name" "$(grep -m1 '^FAIL' /tmp/g_out.$$ | cut -c7-80)";; esac ;;
    "R23 capabilities") line=$(tail -1 /tmp/g_out.$$); case "$line" in *", 0 failed"*) ok "$name ($(echo "$line" | sed 's/r23 capabilities: //'))";; *) bad "$name" "$(grep -m1 '^FAIL' /tmp/g_out.$$ | cut -c7-80)";; esac ;;
    "valid fuzzer + function values") line=$(grep -E "agree" /tmp/g_out.$$ | tail -1); case "$line" in *", 0 fail;"*) ok "$name ($(echo "$line" | sed 's/.*: //; s/;.*//'))";; *) bad "$name" "${line:-no summary}";; esac ;;
    "R25 error type")   line=$(tail -1 /tmp/g_out.$$); case "$line" in *", 0 failed"*) ok "$name ($(echo "$line" | sed 's/r25 phal: //'))";; *) bad "$name" "$(grep -m1 '^FAIL' /tmp/g_out.$$ | cut -c7-80)";; esac ;;
    "R28 linker")       line=$(tail -1 /tmp/g_out.$$); case "$line" in *", 0 failed"*) ok "$name ($(grep -m1 'identity:' /tmp/g_out.$$ | sed 's/PASS  identity: //; s/ byte-identical.*//') identical; $(echo "$line" | sed 's/r28 link: //'))";; *) bad "$name" "$(grep -m1 '^FAIL' /tmp/g_out.$$ | cut -c7-80)";; esac ;;
    "R29 separate compilation") line=$(tail -1 /tmp/g_out.$$); case "$line" in *", 0 failed"*) ok "$name ($(echo "$line" | sed 's/r29 separate: //; s/, 0 failed//'))";; *) bad "$name" "$(grep -m1 '^FAIL' /tmp/g_out.$$ | cut -c6-80)";; esac ;;
    "R73 scratch")      line=$(tail -1 /tmp/g_out.$$); case "$line" in *", 0 failed"*) ok "$name ($(echo "$line" | sed 's/r73 scratch: //; s/, 0 failed//'))";; *) bad "$name" "$(grep -m1 '^FAIL' /tmp/g_out.$$ | cut -c7-80)";; esac ;;
    "R74 compose")      line=$(tail -1 /tmp/g_out.$$); case "$line" in *", 0 failed"*) ok "$name ($(echo "$line" | sed 's/r74 compose: //; s/, 0 failed//'))";; *) bad "$name" "$(grep -m1 '^FAIL' /tmp/g_out.$$ | cut -c7-80)";; esac ;;
    "R77 format")       line=$(tail -1 /tmp/g_out.$$); case "$line" in *", 0 failed"*) ok "$name ($(echo "$line" | sed 's/r77 format: //; s/, 0 failed//'))";; *) bad "$name" "$(grep -m1 '^FAIL' /tmp/g_out.$$ | cut -c7-80)";; esac ;;
    "R77 stray")        line=$(tail -1 /tmp/g_out.$$); case "$line" in *", 0 failed"*) ok "$name ($(echo "$line" | sed 's/r77 stray: //; s/, 0 failed//'))";; *) bad "$name" "$(grep -m1 '^FAIL' /tmp/g_out.$$ | cut -c7-80)";; esac ;;
    "R79 real")         line=$(tail -1 /tmp/g_out.$$); case "$line" in *", 0 failed"*) ok "$name ($(echo "$line" | sed 's/r79 real: //; s/, 0 failed//'))";; *) bad "$name" "$(grep -m1 '^FAIL' /tmp/g_out.$$ | cut -c7-80)";; esac ;;
    "R72 mandapa")      line=$(tail -1 /tmp/g_out.$$); case "$line" in *", 0 failed"*) ok "$name ($(echo "$line" | sed 's/r72 mandapa: //; s/, 0 failed//'))";; *) bad "$name" "$(grep -m1 '^FAIL' /tmp/g_out.$$ | cut -c7-80)";; esac ;;
    "R30 module vitti") line=$(tail -1 /tmp/g_out.$$); case "$line" in *", 0 failed"*) ok "$name ($(echo "$line" | sed 's/r30 vitti: //'))";; *) bad "$name" "$(grep -m1 '^FAIL' /tmp/g_out.$$ | cut -c6-80)";; esac ;;
    "R31 incremental")  line=$(tail -1 /tmp/g_out.$$); case "$line" in *", 0 failed"*) ok "$name ($(echo "$line" | sed 's/r31 incremental: //; s/, 0 failed//'))";; *) bad "$name" "$(grep -m1 '^FAIL' /tmp/g_out.$$ | cut -c6-80)";; esac ;;
    "R32 FFI")          line=$(tail -1 /tmp/g_out.$$); case "$line" in *", 0 failed"*) ok "$name ($(echo "$line" | sed 's/r32 ffi: //'))";; *) bad "$name" "$(grep -m1 '^FAIL' /tmp/g_out.$$ | cut -c6-80)";; esac ;;
    "R33 FFI kinds")    line=$(tail -1 /tmp/g_out.$$); case "$line" in *", 0 failed"*) ok "$name ($(echo "$line" | sed 's/r33 ffi kinds: //'))";; *) bad "$name" "$(grep -m1 '^FAIL' /tmp/g_out.$$ | cut -c6-80)";; esac ;;
    "R35 COFF reader")  line=$(tail -1 /tmp/g_out.$$); case "$line" in *", 0 failed"*) ok "$name ($(echo "$line" | sed 's/r35 coff2smo: //'))";; *) bad "$name" "$(grep -m1 '^FAIL' /tmp/g_out.$$ | cut -c7-80)";; esac ;;
    "COFF reader fuzzer") line=$(tail -1 /tmp/g_out.$$); case "$line" in *", 0 broke the contract"*) ok "$name ($(echo "$line" | sed 's/fuzz_coff2smo: seed [0-9]*, //; s/, 0 broke the contract//'))";; *) bad "$name" "${line:-no summary}";; esac ;;
    "R34 Windows fixes") line=$(tail -1 /tmp/g_out.$$); case "$line" in *", 0 failed"*) ok "$name ($(echo "$line" | sed 's/r34 windows fixes: //'))";; *) bad "$name" "$(grep -m1 '^FAIL' /tmp/g_out.$$ | cut -c7-80)";; esac ;;
    "FFI fuzzer")       line=$(tail -1 /tmp/g_out.$$); case "$line" in *", 0 differ"*) ok "$name ($(echo "$line" | sed 's/fuzz_ffi: seed [0-9]*, //; s/ printed values.*//'))";; *) bad "$name" "${line:-no summary}";; esac ;;
    "ELF reader fuzzer") line=$(tail -1 /tmp/g_out.$$); case "$line" in *", 0 broke the contract"*) ok "$name ($(echo "$line" | sed 's/fuzz_elf2smo: seed [0-9]*, //; s/, 0 broke the contract//'))";; *) bad "$name" "${line:-no summary}";; esac ;;
    "R34 FFI v2")       line=$(tail -1 /tmp/g_out.$$); case "$line" in *", 0 failed"*) ok "$name ($(echo "$line" | sed 's/r34 ffi v2: //'))";; *) bad "$name" "$(grep -m1 '^FAIL' /tmp/g_out.$$ | cut -c6-80)";; esac ;;
    "R38 fail-alloc")   line=$(tail -1 /tmp/g_out.$$); case "$line" in *", 0 failed"*) ok "$name ($(echo "$line" | sed 's/r38 fail-alloc: //; s/, 0 failed//'))";; *) bad "$name" "$(grep -m1 '^FAIL' /tmp/g_out.$$ | cut -c6-80)";; esac ;;
    "alloc bounds")     line=$(tail -1 /tmp/g_out.$$); case "$line" in *", 0 failed"*) ok "$name ($(echo "$line" | sed 's/alloc bounds: //; s/ computed allocations in lib\/:/:/; s/, 0 failed//'))";; *) bad "$name" "$(grep -m1 '^FAIL' /tmp/g_out.$$ | cut -c6-80)";; esac ;;
    "R45 debug")        line=$(tail -1 /tmp/g_out.$$); case "$line" in *", 0 failed"*) ok "$name ($(grep -m1 'the suite under --debug' /tmp/g_out.$$ | sed 's/.*--debug: //; s/ print exactly.*//') the same under the trace; $(echo "$line" | sed 's/r45 debug: //; s/, 0 failed//'))";; *) bad "$name" "$(grep -m1 '^FAIL' /tmp/g_out.$$ | cut -c7-80)";; esac ;;
    "R46 debug usable") line=$(tail -1 /tmp/g_out.$$); case "$line" in *", 0 failed"*) ok "$name ($(echo "$line" | sed 's/r46 debug usable: //; s/, 0 failed//'))";; *) bad "$name" "$(grep -m1 '^FAIL' /tmp/g_out.$$ | cut -c7-80)";; esac ;;
    "Devanagari default") line=$(tail -1 /tmp/g_out.$$); case "$line" in *", 0 failed"*) ok "$name ($(echo "$line" | sed 's/r50 devanagari default: //; s/, 0 failed//'))";; *) bad "$name" "$(grep -m1 '^FAIL' /tmp/g_out.$$ | cut -c6-80)";; esac ;;
    "R54 migration")    line=$(tail -1 /tmp/g_out.$$); case "$line" in *", 0 failed"*) ok "$name ($(echo "$line" | sed 's/r54 nivartanam migration: //; s/, 0 failed//'))";; *) bad "$name" "$(grep -m1 '^FAIL' /tmp/g_out.$$ | cut -c7-80)";; esac ;;
    "R53 nivartanam")   line=$(tail -1 /tmp/g_out.$$); case "$line" in *", 0 failed"*) ok "$name ($(echo "$line" | sed 's/r53 nivartanam: //; s/, 0 failed//'))";; *) bad "$name" "$(grep -m1 '^FAIL' /tmp/g_out.$$ | cut -c7-80)";; esac ;;
    "R52 additions")    line=$(tail -1 /tmp/g_out.$$); case "$line" in *", 0 failed"*) ok "$name ($(echo "$line" | sed 's/r52: //; s/, 0 failed//'))";; *) bad "$name" "$(grep -m1 '^FAIL' /tmp/g_out.$$ | cut -c7-80)";; esac ;;
    "R52 lib index")    line=$(tail -1 /tmp/g_out.$$); case "$line" in *"in step with lib/"*) ok "$name ($(echo "$line" | sed 's/lib index: //; s/, in step with lib\///'), in step)";; *) bad "$name" "${line:-no output}";; esac ;;
    "keyword boundary") line=$(tail -1 /tmp/g_out.$$); case "$line" in *", 0 failed"*) ok "$name ($(echo "$line" | sed 's/r43 keyword boundary: //; s/, 0 failed//'))";; *) bad "$name" "$(grep -m1 '^FAIL' /tmp/g_out.$$ | cut -c7-80)";; esac ;;
    "keyword prefix")   line=$(tail -1 /tmp/g_out.$$); case "$line" in *"RESULT: PASS"*) ok "$name ($(grep -m1 '^keyword prefix: ' /tmp/g_out.$$ | sed 's/keyword prefix: //; s/ (allowed: tests\/r43)//; s/; 0 is a keyword//'), reported)";; *) bad "$name" "$(grep -m1 '^FAIL' /tmp/g_out.$$ | cut -c7-80)";; esac ;;
    "doc signatures")   line=$(tail -1 /tmp/g_out.$$); case "$line" in *"RESULT: PASS"*) ok "$name ($(grep -E 'Document: ' /tmp/g_out.$$ | sed 's/Document: //; s/ function signatures//') signatures, 0 mismatches)";; *) bad "$name" "$(grep -m1 'Issues:' /tmp/g_out.$$)";; esac ;;
    "stale claims")     line=$(grep -E 'absence-shaped sentences' /tmp/g_out.$$ | head -1); case "$line" in *"absence-shaped sentences"*) ok "$name ($(echo "$line" | sed 's/stale-claim scan: //; s/ absence-shaped sentences/ hits/'))";; *) bad "$name" "scanner produced no count";; esac ;;
    "R23 fuzzer")       line=$(tail -1 /tmp/g_out.$$); case "$line" in *", 0 differ"*) ok "$name ($(echo "$line" | sed 's/fuzz_r23: //'))";; *) bad "$name" "${line:-no summary}";; esac ;;
    "pack messages")    case "$(tail -1 /tmp/g_out.$$)" in OK*) ok "$name (12 sets x 11 cases)";; *) bad "$name" "$(grep -m1 -E 'FAIL|differ|Error' /tmp/g_out.$$ | cut -c1-60)";; esac ;;
    *)                  ok "$name" ;;
  esac
  rm -f /tmp/g_out.$$
}

run_gate "regression suite"  python3 tests/run_tests.py
run_gate "codegen shapes"    python3 tools/codegen_gate.py ./sutram_compiler
run_gate "language packs"    python3 tools/test_lang_packs.py ./sutram_compiler
run_gate "library proofs"    python3 tools/proof_lib.py --compiler ./sutram_compiler
run_gate "property proofs"   python3 tools/proof_props.py --compiler ./sutram_compiler
run_gate "guard pages"       python3 tools/guard_page.py   # R69: every block flush against PROT_NONE; suite + both proof sets touch nothing they were not given; 4 control bugs must fault
run_gate "layer check"       python3 tools/check_layers.py
run_gate "stdlib inventory"  python3 tools/gen_stdlib_ref.py
run_gate "module graph"      python3 -m unittest discover -s tests/module_graph -p 'test_*.py'
run_gate "pack messages"     python3 tests/sandesh/test_sandesh.py   # R11: every message in every pack
run_gate "keyword packs built in" python3 tools/lang_builtin.py --check   # R22 (F8): src/r22_lang_builtin.inc is lang/*.lang
run_gate "pack found without lang/" python3 tests/r22/test_lang_builtin.py --compiler ./sutram_compiler   # R22 (F8): --lang <pack> on a valid program does not warn
run_gate "R23 capabilities"  python3 tests/r23/test_capabilities.py --compiler ./sutram_compiler   # R23: function values, methods, slices: the errors and the checks
run_gate "R25 error type"    python3 tests/r25/test_phal.py --compiler ./sutram_compiler   # R25: siddhi, dosh, prasar: the rules and the edges
run_gate "R28 linker"        python3 tests/r28/test_link.py --compiler ./sutram_compiler --linker ./sutram-link   # R28: --object + sutram-link = the direct compile, byte for byte; two modules; the errors
run_gate "R29 separate compilation" python3 tests/r29/test_separate.py --compiler ./sutram_compiler --linker ./sutram-link   # R29: each module compiled once, linked; behaves as the whole-program compile
run_gate "R30 module vitti"  python3 tests/r30/test_vitti.py --compiler ./sutram_compiler --linker ./sutram-link   # R30: a module's vitti held once, in its own object
run_gate "R31 incremental"   python3 tests/r31/test_incremental.py --compiler ./sutram_compiler --linker ./sutram-link   # R31: --cache rebuilds only what changed; the same executable as a clean build
run_gate "R32 FFI"           python3 tests/r32/test_ffi.py --compiler ./sutram_compiler --linker ./sutram-link --elf2smo ./sutram-elf2smo   # R32: C functions, checked declarations, read from ELF
run_gate "R33 FFI kinds"     python3 tests/r33/test_ffi_kinds.py --compiler ./sutram_compiler --linker ./sutram-link --elf2smo ./sutram-elf2smo   # R33: f64, ptr, void; checked; the stage-2 reader
run_gate "R35 COFF reader"   python3 tests/r35/test_coff2smo.py --coff2smo ./sutram-coff2smo   # R35: the Windows FFI's COFF reader - the same bytes as on Windows; its refusals
run_gate "COFF reader fuzzer" python3 tools/fuzz_coff2smo.py --seed 35 --count 3000 --coff2smo ./sutram-coff2smo --out /tmp/fuzz-coff2smo-gate   # R35: malformed COFF: no crash, no hang, no output on a refusal
run_gate "R34 Windows fixes" python3 tests/r34/test_windows_fixes.py --compiler ./sutram_compiler   # R34: a PE program with more than 256 runtime calls (the compiler crashed); PE through the Linux compiler here
run_gate "FFI fuzzer"       python3 tools/fuzz_ffi.py --seed 33 --count 60 --compiler ./sutram_compiler --linker ./sutram-link --elf2smo ./sutram-elf2smo --out /tmp/fuzz-ffi-gate   # R33: random programs against a model
run_gate "ELF reader fuzzer" python3 tools/fuzz_elf2smo.py --seed 33 --count 3000 --elf2smo ./sutram-elf2smo --out /tmp/fuzz-elf2smo-gate   # R33: malformed objects: no crash, no hang, no output on a refusal
run_gate "R34 FFI v2"        python3 tests/r34/test_ffi_v2.py --compiler ./sutram_compiler --linker ./sutram-link --elf2smo ./sutram-elf2smo   # R34 (cloud): the sidecar's version; a dasham bit for bit; the edges
run_gate "R38 fail-alloc"    python3 tests/r38/test_fail_alloc.py --compiler ./sutram_compiler   # R38: --fail-alloc N; every allocating library function at every allocation it makes
run_gate "alloc bounds"      python3 tools/check_alloc_bounds.py   # R37: every computed allocation in lib/ bounds its count before multiplying, or says why not
run_gate "R45 debug"         python3 -B tests/r45/test_debug.py --compiler ./sutram_compiler   # R45: --debug traces each statement (line + scalar variables) and the suite runs the same under it
run_gate "R46 debug usable"  python3 -B tests/r46/test_debug_usable.py --compiler ./sutram_compiler   # R46: watch list, line range, statement count and summary, module vitti; a sign error found by the trace
run_gate "Devanagari default" python3 -B tests/r50/test_devanagari_default.py --compiler ./sutram_compiler   # R50: Devanagari Sanskrit needs no flag; prati is प्रति
run_gate "R53 nivartanam"    python3 -B tests/r53/test_nivartanam.py --compiler ./sutram_compiler   # R53: nivartanam the return keyword, prati the alias - the same binaries, both scripts
run_gate "R72 mandapa"       python3 -B tests/r72_mandapa/test_mandapa.py --compiler ./sutram_compiler   # R72: with and without a block, the same output; a scratch address may not be returned
run_gate "R73 scratch"       python3 -B tests/r73_scratch/test_scratch.py --compiler ./sutram_compiler   # R73: the block reclaims (1M x 64 B: flat memory), rewinds on every exit, refuses escapes, names its blind spots
run_gate "R74 compose"       python3 -B tests/r74_compose/test_compose.py --compiler ./sutram_compiler   # R74: the memory model as a whole - kosh outside a block, scratch into a call, siblings, 100 MB, recursion 1,000 deep
run_gate "R77 format"        python3 -B tests/r77_format/test_format_mutator.py --compiler ./sutram_compiler   # R77: every example, saved 7 ways (CRLF, trailing spaces, whitespace-only lines in bodies, tabs, no/extra final newline, BOM) - same output
run_gate "R77 stray"         python3 -B tests/r77_format/test_stray_tokens.py --compiler ./sutram_compiler   # R77: a stray token in every kind of body is refused or every statement runs - no silent partial compilation
run_gate "R79 real"          python3 -B tests/r79_real/test_real_program.py --compiler ./sutram_compiler   # R79: a 185-line program, with and without mandapa blocks - same output as a Python reference, block version under 75% of the memory
run_gate "R54 migration"     python3 -B tests/r54/test_r54.py --compiler ./sutram_compiler   # R54: lib/ and examples/ say nivartanam; the expanded source may be 128 KiB; प्रति still works
run_gate "R52 additions"     python3 -B tests/r52/test_r52.py --compiler ./sutram_compiler   # R52: likha up to six values, lkhb dasham, the yoj hint, arabhya/paryantam
run_gate "R52 lib index"     python3 tools/lib_index.py --check   # R52: src/r52_lib_index.inc (the yoj hint's names) is what lib/ declares
run_gate "keyword boundary"  python3 -B tests/r43/test_keyword_boundary.py --compiler ./sutram_compiler   # R43: a keyword never matches inside a longer word - every keyword of lang/sanskrit.lang, both scripts, plus controls
run_gate "keyword prefix"    python3 tools/check_keyword_prefix.py   # R43 WS4: lib names that begin with a keyword, REPORTED (legal); FAILs only if a lib name IS a keyword
run_gate "doc signatures"    python3 tools/check_doc_signatures.py   # R38: lib signatures = docs/sutram-stdlib.html signatures, 305/305, 0 mismatches; a drift FAILs
run_gate "stale claims"      python3 tools/doc_stale_claims.py   # R38: the absence-claim scanner runs; hits are review items, NOT failures (its own docstring: "Exit 0 always"), so this gate PASSes when the scanner completes and reports its count - FAILing on hits would permanently break the build at 160 hits
run_gate "R23 fuzzer"        python3 tools/fuzz_r23.py --seed 23 --count 100 --compiler ./sutram_compiler --out /tmp/fuzz-r23-gate   # R23: 100 random programs against the model
run_gate "valid fuzzer + function values" python3 tools/fuzz_valid.py --seed 24 --count 60 --capabilities --compiler ./sutram_compiler --out /tmp/fuzz-valid-gate   # R24: the main fuzzer with calls through function values
run_gate "crash corpus"      python3 tools/crash_corpus.py --compiler ./sutram_compiler   # R17: invalid input must error, never crash
run_gate "operator precedence" python3 tools/check_precedence.py --compiler ./sutram_compiler   # R17: the documented table, pair by pair
run_gate "formatted tree"    sh -c 'python3 tools/sutram_fmt.py --check --exclude-from tools/fmt-exclude.txt examples/*.sm examples/*/*.sm examples/lib/*.smlib lib/*.smlib tests/stdlib/*.sm tests/r*/*.sm tests/r*/*/*.sm tests/r*/lib/*.smlib tests/sandesh/cases/*.sm && echo FORMATTED'   # R19: sutram-fmt would change nothing
run_gate "version string"    python3 tools/check_version.py --binary ./sutram_compiler   # R13: --version is the current version
run_gate "performance"        python3 tools/bench_gate.py --compiler ./sutram_compiler --repeat 3

# the GUI needs an X server; say so rather than omitting it
if [ -n "${DISPLAY:-}" ] || [ -d /tmp/.X11-unix ]; then
  n=0; f=0
  for t in tools/test_x11_*.py; do
    SUTRAM_GUI="$PWD/sutram-gui" python3 "$t" >/dev/null 2>&1 && n=$((n+1)) || f=$((f+1))
  done
  [ "$f" = 0 ] && ok "X11 GUI protocol ($n/$n)" || bad "X11 GUI protocol" "$f of $((n+f)) failed"
else
  skip "X11 GUI protocol" "no DISPLAY and no /tmp/.X11-unix/X0"
fi

# Windows cannot be run here. R34: it HAS been run, on real Windows 11 (Windows-to-Sarvam/,
# Claude-to-Sarvam/evidence-r34/): there, run tests/r34/test_link_windows.py,
# tools/ide_examples_windows.ps1 and tools/accept-windows.ps1. Say plainly it is not run here.
skip "Windows execution" "cannot run here (Linux) - on Windows: tests/r34/test_link_windows.py, tests/r35/test_ffi_windows.py, tools/ide_examples_windows.ps1, tools/accept-windows.ps1"

# R38: doc counts, LAST. doc_counts_gate.py normally runs gates.sh itself, which
# would recurse if called from here. It now accepts --totals/--suite-pass (see its
# header): gates.sh passes its final totals, counting this gate itself as a pass.
# That is exact when this gate passes, and moot when it fails, since a failed build
# is not trusted. An impossible document claim (a gate total above the final total,
# or a suite pass above the measured one) FAILs the build, which is the point.
# Labelled-count checks are skipped in this mode; the standalone run with --gates
# still covers them.
DOC_TOTAL_PASS=$((PASS+1))
DOC_OUT=$(python3 tools/doc_counts_gate.py --totals "$DOC_TOTAL_PASS $FAIL $SKIP" --suite-pass "${SUITE_PASS:-0}" 2>&1)
DOC_EXIT=$?
case "$DOC_EXIT" in
  0) ok "doc counts ($(echo "$DOC_OUT" | head -1 | sed 's/measured: //'))" ;;
  *) bad "doc counts" "$(echo "$DOC_OUT" | grep -m1 '^FAIL' | cut -c6-80)" ;;
esac

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
