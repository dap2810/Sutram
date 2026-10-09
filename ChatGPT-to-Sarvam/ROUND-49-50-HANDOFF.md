# Sutram R49 + R50 — ChatGPT → Sarvam engineering handoff (draft review)
**Date:** 2026-10-09 (America/Toronto)
**Assignment source:** `Sarvam-to-ChatGPT/ROUND-49.md`, then `ROUND-50.md`.
**Review branch:** `feature/r49-r50-completion-20261009`
**Draft PR:** https://github.com/dap2810/Sutram/pull/8
**Base:** current main at start of round, `83ef4074d62fd5cd305bf8ee9d95c1408517b031`; accepted R44 compiler.
**Release status:** **R50 byte-store feature passes Linux native tests. R49 universal provenance / error accumulation and full Windows end-to-end acceptance are NOT yet certified. Do NOT merge without independent Sarvam review.**

## What changed
1. Carried accepted R46 call optimization, R48 Stage1 `--check` and Stage2 bounded recovery onto a fresh main-derived branch. All standard generated code from four tested samples is byte-identical to accepted R46. R47 rejected experimental code remains excluded.
2. R49 unresolved-call source positions now match the *exact lexer token pointer* rather than the first same-named identifier, so `missing_repeat` at three different lines produces three distinct located diagnostics with carets.
3. R49 check-only original `ayojan` module location helper reopens importer and locates `ayojan` column for `E_MODULE_MISSING`. This does **not** fix provenance inside a malformed imported module; current output still falsely attributes it to root, listed as a blocker.
4. R50 `set_char(buffer,byte_index,value)` builtin ID 41, one-byte x86-64 store at byte stride, returns the low byte. No bounds checking: allocate writable memory and provide valid offsets. `char_at` and existing NUL-byte `vartani_len`/`vartani_cmp` need no new equivalent. `buf[i]=v` still uses eight-byte qword stride and existing width_repro goldens must not be modified.
5. Win64 host runtime fixes under `win/winrt.inc`: load WinAPI via named modules, correct 16-byte call alignment and 32-byte shadow, route real CreateFile handles through `os_read`/`os_write` while keeping 0/1/2 stdio, use `win_stack` rather than native RSP for argv in Windows _start. CI-only diagnostic builds `-DR49_WIN_DIAG_0...7` localize startup errors; these blocks are disabled in standard builds.

## Actually observed Linux CI output
Native invocation from `.github/workflows/r49-r50-native.yml`:
```sh
nasm -f elf64 -I. src/sutram_compiler.asm -o /tmp/new.o
ld -o r48_after /tmp/new.o
python3 tools/r48_native_acceptance.py
python3 tools/r48_stage2_acceptance.py
python3 tools/r50_native_acceptance.py
python3 tools/r49_repeated_semantic.py
python3 tools/r49_diagnostic_audit.py
cp r48_after sutram_compiler
python3 tests/run_tests.py
python3 tools/codegen_gate.py
python3 tools/test_lang_packs.py
python3 -m unittest discover -s tests/module_graph -p 'test_*.py' -v
```
Native observations in GitHub workflow: https://github.com/dap2810/Sutram/actions/runs/37981360567
```
R48_ACCEPTED_CHECK_TESTS,parse_diags=3,native_byte_equal=4,check_valid=1,no_output=1
STAGE2_PASS structural=3 nested=2 unclosed=1 undefined=3
R50_RUN runtime_hi.sm rc 0 stdout '104\n105\n104\n105\n2\n0\n' stderr ''
R50_RUN byte_truncation.sm rc 0 stdout '44\n44\n255\n255\n2\n' stderr ''
R50_ACCEPTED: runtime byte writes, byte truncation, char_at, vartani_len and vartani_cmp; 2/2 native executions; 2/2 --check
R49_REPEATED_SEMANTIC_PASS,unique_correct_lines=3,no_output=1
PASS=186
12 native codegen gate PASS lines
30/30 pack checks pass
Ran 18 tests ... OK
R50_PE32_LINK_OK bytes 156492
```
Byte parity source: accepted R46 compiler `72b824f70049765c3977db07d712a1a604b89434`; output sha256: `41_recursion` 846 B = `8ab871455f57bff8a95ac7c840c52f8245e434c7016af5b3e3cedf6bfbd6d0e3`, `126_numeric_pipeline` 7450 B = `38c50da9ec00d8cffbc1d2f42abe63fd1580572f894a74b3677727f7c9b8b8e2`, `163_r40_transitive_diamond` 575 B = `e3024b0282767501627e44d5243e32fcbd3ee5ad717a030cd3e7b8e7a7e2f984`, `111_t18_kosh_dasham_function_return` 1307 B = `96e602630d053ddf7a61ed32badde5b293597569977ccd4bfbc7a61e07cc14b2`.

## Adversarial diagnostic audit (real, not predicted)
- `missing_separators.sm`: E_PARSE three distinct `file:line:col`, lines 2,3,4.
- `nested_expressions.sm`: E_PARSE two distinct lines 2,4.
- `top_level_malformed.sm`: E_PARSE at 1:1.
- `module_missing.sm`: E_MODULE_MISSING initial audit had `module_missing.sm:2:` without column; later check-mode patch detects true `ayojan` position, newer audit lists located 1/1.
- `import_bad.sm`: Current **incorrect** diagnostic `import_bad.sm:2:20` for content originally in `tests/r49_check/lib/faulty_r49.smlib`. The file/column **protocol string** is present but *provenance is wrong*; don't confuse audited syntax completeness with source mapping.
- `three_undefined_functions.sm` and `repeated_undefined.sm`: report 3 separate errors, latter all same function name.
- Structured audit is `tools/r49_diagnostic_audit.py`; raw output available in linked CI job. Fixtures and README included in the same branch.

## Windows status and reproduction
The Windows compiler now assembles and links to native PE32+ using genuine `win/rtblob.inc`, and on Windows GitHub-hosted user-mode runner **`--version` prints Sutram 1.0 and exits zero** after fixing argv stack access. Windows `--check` still has a runtime issue (hang / older EOF result), under reproducible bounded probe investigation. `win_probe_0.exe`, 1,2 return 71,72,73; further probes 3..7 under latest job. Do not claim real Windows execution of generated byte strings until tested with `tests/r50_check/runtime_hi.sm`. Do not request admin, services or security relaxation.

## Sarvam — exact next instructions
1. Review PR #8, verify clean main ancestry, the accepted R46 optimized source and Stage1/Stage2 no-codegen-regression invariant; **keep PR as DRAFT / do not merge until all R49 acceptance passes**.
2. Reproduce full Linux commands and compare native outputs and SHA-256 manifests. Verify `set_char` semantics with `tests/r50_check/runtime_hi.sm`, `byte_truncation.sm`; preserve `width_repro` unchanged as intentional qword/byte distinction.
3. Run `tools/r49_diagnostic_audit.py` and fix actual imported **original filename and line/column**, avoiding fabricated positions. Extend source mapping through multiple `ayojan` expansion rounds and namespaced imports; cover full semantic/graph error family locations and accumulate independent module failures.
4. Verify Windows compiler `--check` on valid and invalid cases and compile **and actually run** `runtime_hi.exe` under normal Windows account; investigate CI probe stage results and pass native PE test without elevation.
5. Increase adversarial coverage (nested missing braces, top-level imports, multiple semantic & graph errors including 3+ in one file); never rewrite expected goldens to hide regressions. Include actual stdout/stderr, exit code and no-output checks.
6. Deliver independently accepted result or a new targeted assignment under `Sarvam-to-ChatGPT/`. Work happens only when the user says CHECK FOLDER; no background monitoring.

**Sutram fundamentals preserved:** single hand-written pure NASM compiler, Sanskrit core and Indian language packs, .sm, native ELF/PE, no external runtime, end users no toolchain.
