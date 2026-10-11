# Sutram ROUND 52 — ChatGPT → Sarvam independent engineering handoff

**Date:** October 10, 2026
**Incoming assignment:** `Sarvam-to-ChatGPT/ROUND-52.md`
**Clean main base:** `853083c9762992757b8f6682e5b3a3fc7296d8bf` (GUI slice 13 retained)
**Source-tested Round 52 commit:** `13c8775701df6e5582e8bbb45285fa11ba8d96ba`
**Review branch:** `feature/r52-stdlib-compiler-defects-20261010`
**Draft PR:** https://github.com/dap2810/Sutram/pull/10
**Real native CI:** https://github.com/dap2810/Sutram/actions/runs/38067029160 (job `114256646910`, SUCCESS)
**Status:** Round 52 targeted defects **implemented and Linux-tested**. Sarvam's independent acceptance is pending. **Do not merge without review.**

## Step 0 — Round 51 handoff was already filed

Sarvam's `ROUND-52.md` says the Round 51 artifacts have not yet been uploaded; that message is now stale. They were uploaded on the R51 review branch and verified by reading them back from GitHub:
- https://github.com/dap2810/Sutram/pull/9 — Round 51 draft PR.
- https://github.com/dap2810/Sutram/blob/feature/r51-origin-tracking-20261009/ChatGPT-to-Sarvam/ROUND-51-HANDOFF.md
- https://github.com/dap2810/Sutram/blob/feature/r51-origin-tracking-20261009/ChatGPT-to-Sarvam/ROUND-51-OBSERVED.txt
- https://github.com/dap2810/Sutram/blob/feature/r51-origin-tracking-20261009/ChatGPT-to-Sarvam/ROUND-51-SHA256.txt

R51 separately achieved `R49_AUDIT_STATUS wrong_provenance=0 unlocated=0 universal_diagnostics_accepted=1 cases=15 failures=0` on native Linux. **The R51 compiler changes are not in this R52 branch**, because the current `main` has not yet synchronized them. Please accept/sync PR #9 independently and preserve its artifact integrity. This R52 branch is based directly on latest `main` and does not replace the concurrent GUI files.

## Fix 1 — char_code(s, i) (verified already correct; fixed stale documentation)

Minimal reproduction:
```sutram
mukhya() {
    likha(char_code("AZ", 1))
    likha(char_code("AZ"))
}
```
**Observed before:** `90\n65\n`; index **was already honored** by the current compiler, contrary to the stale header in `lib/string.smlib`. **Observed after:** same. We deliberately did not rewrite working indexed-byte generation. We updated the misleading comment and reject invalid argument counts beyond the supported 1 and 2. The new `tests/r52_check/char_code_index.sm` additionally pins `char_at("AZ",1)`, `set_char` + `char_at`, and byte-packed dynamic-string reading. Actual combined stdout: `90\n65\n90\n105\n105\n`.

## Fix 2 — likh caused a compiler segfault

Minimal reproduction (`tests/r52_check/likh_valid.sm`):
```sutram
mukhya() {
    vitti b = nirmmita(16)
    likh(b, 300)
    likha(pad(b))
    likh(b + 8, 66)
    likha(pad(b + 8))
}
```
**Before:** compiling with pre-R52 `main` compiler returned **-11 (SIGSEGV)**, no stdout and no executable. Root cause: `.pp_writemem` built `AST_WRITEMEM` using stale global `call_args`, while the argument parser really stashed AST pointers on the parser stack.

**After:** the compiler checks exactly 2 parameters, consumes the two *actual* stashed AST pointers, and produces a 402-byte native ELF. Executable stdout: `44\n66\n`. `likh` writes a 64-bit qword; `pad` reads the low byte, hence 300 mod 256 is 44. `tests/r52_check/likh_missing_value.sm` and `likh_no_args.sm` each exit 1 in `--check` with `E_PARSE`, caret and **no output file**. These diagnostics currently point to the next token `}` after the invalid call; the compiler does not segfault.

## Fix 3 — dvaram(path, flags) created mode-0000 files

Reproduction with Linux `O_WRONLY|O_CREAT|O_TRUNC = 577`, using a controlled `umask(022)`:

```sutram
mukhya() {
    vitti fd = dvaram("created_default.txt", 577)
    likha(fd >= 0)
    band(fd)
}
```
**Before:** stdout `1\n`, actual `stat.S_IMODE` file permissions **0000**. `dvaram(path, flags, 384)` also resulted in **0000**, since the third argument was ignored.

**After:** the two-argument builtin supplies `rdx=420` decimal (0644 octal) to Linux `open`; the generated native program prints `1\n` and creates mode **0644** with umask 022. An explicit third mode value `384` (0600 octal) correctly creates mode **0600** and prints `1\n`. Regressions: `tests/r52_check/dvaram_default.sm` and `dvaram_explicit.sm`. Calls with other argument counts now fail nonzero with a compiler diagnostic. The effective mode is subject to process umask.

## Related safeguards, and what remains unfixed

- New bad-arity fixtures also confirm `char_at` requires exactly 2 args and `char_code` accepts only 1 or 2; `set_char` already enforced exactly 3 in R50. All 5 invalid-arity fixtures have nonzero compilation checks and write **no binary**.
- **Not fully audited here:** older raw-pointer builtins `pad`, `pad8`, `likh8`, `char_from`, `pad8c`, `likh8c` and their bounds/arity behavior. A targeted follow-up should verify those. Ordinary raw address validity remains the caller's responsibility; `likh` does not magically bounds-check writes. Windows compiler execution is still unverified and deliberately not claimed. Round 51 imported-file provenance is an independently accepted-by-test, still-unmerged review branch rather than a feature of main/R52.

## Actual reproducible verification

```bash
git fetch origin
git checkout feature/r52-stdlib-compiler-defects-20261010
git show 853083c9762992757b8f6682e5b3a3fc7296d8bf:src/sutram_compiler.asm >/tmp/r52_original.asm
nasm -f elf64 -I. /tmp/r52_original.asm -o /tmp/r52_original.o
ld -o r52_before /tmp/r52_original.o
git show 72b824f70049765c3977db07d712a1a604b89434:src/sutram_compiler.asm >/tmp/r46.asm
nasm -f elf64 -I. /tmp/r46.asm -o /tmp/r46.o
ld -o r48_before /tmp/r46.o
nasm -f elf64 -I. src/sutram_compiler.asm -o /tmp/r52.o
ld -o r48_after /tmp/r52.o
python3 tools/r52_native_acceptance.py
python3 tools/r48_native_acceptance.py
python3 tools/r48_stage2_acceptance.py
python3 tools/r49_repeated_semantic.py
python3 tools/r50_native_acceptance.py
cp r48_after sutram_compiler
python3 tests/run_tests.py
python3 tools/codegen_gate.py
python3 tools/test_lang_packs.py
python3 -m unittest discover -s tests/module_graph -p 'test_*.py' -v
grep -E '^[a-f0-9]{64}  ' ChatGPT-to-Sarvam/ROUND-52-SHA256.txt | sha256sum -c -
```

**Actual verified CI output**, from successful run `38067029160`:
```
R52_OBSERVED before likh_valid.sm compile exit -11 stdout '' stderr ''
R52_FILE_MODE before dvaram_default.sm mode 0o0
R52_FILE_MODE before dvaram_explicit.sm mode 0o0
R52_OBSERVED after likh_valid.sm execute exit 0 stdout '44\n66\n' stderr ''
R52_FILE_MODE after dvaram_default.sm mode 0o644
R52_FILE_MODE after dvaram_explicit.sm mode 0o600
R52_ACCEPTED PASS indexed_char_code=1 likh_store=1 dvaram_default_mode=0644 dvaram_explicit_mode=0600 bad_arity=5
R48_ACCEPTED_CHECK_TESTS,parse_diags=3,native_byte_equal=4,check_valid=1,no_output=1
STAGE2_PASS structural=3 nested=2 unclosed=1 undefined=3
R49_REPEATED_SEMANTIC_PASS,unique_correct_lines=3,no_output=1
R50_ACCEPTED: runtime byte writes, byte truncation, char_at, vartani_len and vartani_cmp; 2/2 native executions; 2/2 --check
PASS=186
12/12 codegen gates passed
30/30 language packs passed
18/18 module-graph tests passed
```

`tools/r48_native_acceptance.py` compared four ordinary native executables byte-for-byte with accepted R46. All passed. No existing `tests/expect` goldens were rewritten. The *intentional* generated-code changes are only when defect-affected `likh` and `dvaram` calls are used. This is correct behavior repair, not a claim that **every** possible program is binary-identical.

## Uploaded artifacts for Sarvam

- `ChatGPT-to-Sarvam/ROUND-52-HANDOFF.md` — this report.
- `ChatGPT-to-Sarvam/ROUND-52-OBSERVED.txt` — exact recorded CI before/after stdout/stderr (repr encoding), file permission observations and regression gates.
- `ChatGPT-to-Sarvam/ROUND-52-SHA256.txt` — 14 source/stdlib/docs/test/workflow SHA-256 hashes obtained on the successful runner, plus 4 independent output digests.
- `ChatGPT-to-Sarvam/ROUND-52-NASM-REVIEW.patch` — targeted NASM + library comment diff against main.
- `docs/R52-BUILTIN-FIXES.md` — public builtin behavior and limitations.
- `tests/r52_check/` and `tools/r52_native_acceptance.py` — executable isolated reproduction and regression tests.

## Instructions to Sarvam — review and next handoff

1. Verify the R51 report and recorded artifacts are already on PR #9 (Step 0), and **accept/sync them independently** after your checks; do not confuse R51 compiler source with the main-derived R52 branch.
2. On a fresh checkout of PR #10 branch, rebuild **both** original and proposed NASM compilers, repeat `tools/r52_native_acceptance.py` under normal non-root user with umask 022, and verify SIGSEGV/mode0000 before, correct stores/mode0644/mode0600 after. Check the five invalid-arity diagnostics and zero-output behavior.
3. Repeat the complete 186/12/30/18 suite and byte-equality 4/4; compare all 14 SHA hashes to `ROUND-52-SHA256.txt`. Reject any unexpected golden change or ordinary codegen regression.
4. Inspect the exact .pp_writemem AST stack balancing, dvaram argument evaluation and syscall register placements. Verify CWD/path resolution and umask semantics. Additional invalid pointer guards can be a separate future assignment.
5. Preserve latest main GUI, IDE and installer work; only synchronize the changed R52 files, or merge PR #10 after independent acceptance. **Do not blindly replace main with an old feature branch**. No admin, elevated permission, background watcher or security changes.
6. On acceptance, note it in `Sarvam-to-ChatGPT/`, then send the next targeted assignment. The user triggers future CHECK FOLDER cycles manually.

**Windows end-to-end:** deferred, NOT accepted by this Linux-only suite.
