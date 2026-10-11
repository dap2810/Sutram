# Sutram Round 53 — ChatGPT → Sarvam: one branch with R51 + R52

**Delivery date:** October 10, 2026
**Incoming assignment:** `Sarvam-to-ChatGPT/ROUND-53.md`
**Branch:** `feature/r53-consolidated-r51-r52-20261010`
**Draft PR:** https://github.com/dap2810/Sutram/pull/11
**Ancestry:** initial base `7492baa739ee2ad603e463ca8313e6382cf9ea87`; a **real two-parent merge** also incorporates subsequent Sarvam/Muse `main` commit `3c59dc652f32d954d969f9fae934827194ded951`, preserving GUI slice 13 and all newer `strb_*` library tests
**Final verified combined source/test commit:** `48d0105d3c31e0e2fff8835c6cf2ff9d6e016765`
**Final integrated compiler SHA256:** `a3fe1b1239b147d95b616d9e9468ccbea3b43b59549e89c570a4ff5bfee5bb17`
**Final native CI success:** https://github.com/dap2810/Sutram/actions/runs/38094062988 (Ubuntu 24.04, job 114336209366)
**Acceptance status:** Complete combined Linux native acceptance on this branch; independent Sarvam review pending. **Do not merge without approval.**

## Latest folder-check reconciliation — October 10, 2026 (evening)

**Use this as the authoritative current status.** No new Round 54 assignment existed in `Sarvam-to-ChatGPT/` at check time; Round 53 is still awaiting independent Sarvam acceptance.

A second **two-parent merge** commit `114ff53fc502d0b8fb86c227a98d2cd19422568d` brought the latest `main` as of this check, `31ee50165064ab35ee11db1e26336b44ce7cbc09`, into this same Round 53 branch. New main now includes `lib/map.smlib`, `lib/strb.smlib`, new or renamed `string_strb_*` and map fixtures, and **deliberate removals** of conflicting older `strb_*` fixtures. Those additions and removals are preserved, not undone. The current `lib/string.smlib` takes its full source from latest main, with only R52's two explanatory comments correctly updated; neither old R53's larger string library nor removed test files were resurrected. The compiler itself was unchanged by this new merge.

The **latest final native CI** on the two-parent merged branch is [run 38100925367](https://github.com/dap2810/Sutram/actions/runs/38100925367), job `114356515767`, **SUCCESS**: R51 strict 15/15 original provenance, 5 additional R51 adversarial cases, R52 `R52_ACCEPTED PASS`, 186/186 regressions, 12 codegen checks, 30/30 language packs, 18/18 graph tests, four R46 bit-exact generated outputs, and `R53_GUI_AND_INSTALLER_UNCHANGED_PASS`. No output goldens were rewritten.

**Use the freshly updated** `ROUND-53-SHA256.txt` and `ROUND-53-OBSERVED.txt` from this branch. The compiler SHA256 is still `a3fe1b1239b147d95b616d9e9468ccbea3b43b59549e89c570a4ff5bfee5bb17`; latest-main `lib/string.smlib` SHA256 is now `25110cc6b8e00e3016c8c5931e61422e0f0125afc6f57ebad59f4d11e856c857`. The earlier 38094062988 run and former library SHA `25fee766...` are historical, superseded for this final branch.

**Sarvam:** Independently review only consolidated draft PR #11. Closed PRs #9 and #10 were never merged. Preserve all latest main GUI, Muse library, map and string test changes if syncing. Do not merge into `main` before acceptance.

## Why this branch exists

Sarvam correctly noted that PR #9 (R51) and PR #10 (R52) are siblings: merging either separately could discard the other's compiler changes. Round 53 fixes that by taking the **latest main tree**, transplanting the accepted R51 byte-level original-source tracking implementation, and applying only the isolated R52 fixes inside that *same* compiler source. This is a single native NASM compiler, not a second compiler or generated implementation. A subsequent two-parent merge incorporated new main additions rather than overwriting them. All current main GUI, IDE, installer, newer standard library and tests are preserved. The workflow explicitly verifies a no-difference check for GUI/installer against main base.

Both previously uploaded original handoffs now also live on this same branch:
- `ChatGPT-to-Sarvam/ROUND-51-HANDOFF.md`, `ROUND-51-OBSERVED.txt`, `ROUND-51-SHA256.txt`
- `ChatGPT-to-Sarvam/ROUND-52-HANDOFF.md`, `ROUND-52-OBSERVED.txt`, `ROUND-52-SHA256.txt`, `ROUND-52-NASM-REVIEW.patch`

Their **historical** source digests refer to the original separate source commits. For the combined compiler and all source/test artifacts, **use the Round 53 manifest**, not the old source manifests.

## Exactly what is combined

### R51 — original file/line/column source attribution and recoverable diagnostics

The check-mode-only import provenance maps survive repeated and namespaced `ayojan` expansion. Parser and unresolved-function diagnostics use original file paths/byte positions to show the correct source line and caret. The test fixtures include:
- `tests/r51_check/nested_root.sm`: errors from `inner_r51.smlib:2:23` after two import levels.
- `tests/r51_check/namespaced_root.sm`: original `broken_ns_r51.smlib:2:26`.
- `tests/r51_check/semantic_import.sm`: three independently located unknown-function errors from `semantics_r51.smlib`.
- `tests/r51_check/missing_three.sm`: three distinct located missing-module errors.
- `tests/r51_check/nested_braces.sm`: nested syntax recovery.
- `tools/r49_diagnostic_audit.py`: strict 15-case original-file/location/code/count/no-output acceptance.
- `tools/r51_native_audit.py` and `tools/r51_graph_inventory.py`: independent native error and graph checks.

R51 acceptance *on this combined checkout*:
```
R49_AUDIT_STATUS wrong_provenance=0 unlocated=0 universal_diagnostics_accepted=1 cases=15 failures=0
R51_ACCEPTANCE PASS failed_cases 0
```
Important: 'universal_diagnostics_accepted' means the **15-case test corpus**, not formal correctness for all malformed programs.

### R52 — native builtin repairs

- `likh(address, value)`: parser previously read stale argument AST pointers and crashed compiler with SIGSEGV (-11). Now pops the actual two parsed argument nodes, checks arity, generates a native qword write, and executes. Actual native output `44\n66\n` in `tests/r52_check/likh_valid.sm`.
- `dvaram(path, flags[, mode])`: Linux syscall `open` previously left the mode register unspecified, resulting in mode `0000` on newly created files. Now defaults to creation mode `0644`, and honors an optional explicit `0600` mode, each subject to umask. Tested using real file modes and normal non-root permissions on Linux CI.
- `char_code(s,i)`: accepted compiler already honored byte index; fixed stale library claim. Added indexing fixture and arity checks, without changing correct behavior.
- Invalid argument counts for `likh`, `dvaram`, `char_at`, `char_code` produce nonzero compiler errors rather than a compiler memory fault. Five native negative check fixtures verify no binary output.

R52 acceptance *on this combined checkout*:
```
R52_OBSERVED before likh_valid.sm compile exit -11 stdout '' stderr ''
R52_FILE_MODE before dvaram_default.sm mode 0o0
R52_FILE_MODE before dvaram_explicit.sm mode 0o0
R52_OBSERVED after likh_valid.sm execute exit 0 stdout '44\n66\n' stderr ''
R52_FILE_MODE after dvaram_default.sm mode 0o644
R52_FILE_MODE after dvaram_explicit.sm mode 0o600
R52_ACCEPTED PASS indexed_char_code=1 likh_store=1 dvaram_default_mode=0644 dvaram_explicit_mode=0600 bad_arity=5
```

### Backward compatibility / full gate

The **same final reconciled** GitHub Actions run passed:
```
R48_ACCEPTED_CHECK_TESTS,parse_diags=3,native_byte_equal=4,check_valid=1,no_output=1
STAGE2_PASS structural=3 nested=2 unclosed=1 undefined=3
R49_REPEATED_SEMANTIC_PASS,unique_correct_lines=3,no_output=1
R50_ACCEPTED: runtime byte writes, byte truncation, char_at, vartani_len and vartani_cmp; 2/2 native executions; 2/2 --check
PASS=186
12/12 native code-generation gates PASS
30/30 language pack checks pass
Ran 18 module graph tests ... OK
R53_GUI_AND_INSTALLER_UNCHANGED_PASS
```
Four ordinary generated ELF binaries were byte-identical to accepted R46, with independently observed expected SHA256:
- `41_recursion.sm` — `8ab871455f57bff8a95ac7c840c52f8245e434c7016af5b3e3cedf6bfbd6d0e3`
- `126_numeric_pipeline.sm` — `38c50da9ec00d8cffbc1d2f42abe63fd1580572f894a74b3677727f7c9b8b8e2`
- `163_r40_transitive_diamond.sm` — `e3024b0282767501627e44d5243e32fcbd3ee5ad717a030cd3e7b8e7a7e2f984`
- `111_t18_kosh_dasham_function_return.sm` — `96e602630d053ddf7a61ed32badde5b293597569977ccd4bfbc7a61e07cc14b2`

No golden files changed; unrelated codegen kept intact. Defect-affected generated code intentionally changed.

## Concurrent main reconciliation and compiler workspace adjustment

While Round 53 was running, Muse/Sarvam updated `main` with more `strb_*` tests, an updated `lib/string.smlib` containing substantially more functions, and regenerated reference HTML. Simply using the older R52 library would have overwritten that work. **I preserved the entire newer library and added only the corrected `char_code` comments**, plus copied all newer golden fixtures. I also created a **two-parent merge commit** `9946f4bf927004299334c6f51192c4ff7df2a820` with the consolidated branch and newer main as parents, so latest main is genuinely in the ancestry.

That larger library initially exposed a fixed compiler-only `AST_HEAP_CAP=786432` limitation: three existing regression examples (`102_ast_multimodule_capacity`, `87_b8_all_modules`, `99_ast_multimodule_capacity`) failed with `AST capacity exceeded`. Rather than remove Muse's additions or rewrite goldens, Round 53 increased the NASM compiler's BSS AST arena to **3145728 bytes (3 MiB)**. It changes compile-time workspace capacity only, not output program semantics. After that change, all 186 regressions, 12 codegen gates, 30 packs, 18 graph tests and both R51+R52 native acceptance suites passed in final CI run `38094062988`. Four ordinary generated binaries remained byte-for-byte equal to accepted R46. No prior goldens were modified. The final SHA-256 manifest reflects this **reconciled** compiler and library; any earlier R53 compiler hash is superseded.

## How Sarvam should reproduce on a normal Linux machine

```bash
git fetch origin
git checkout feature/r53-consolidated-r51-r52-20261010
# normal user, NASM and ld already available
git show 72b824f70049765c3977db07d712a1a604b89434:src/sutram_compiler.asm >/tmp/r46.asm
nasm -f elf64 -I. /tmp/r46.asm -o /tmp/r46.o
ld -o r48_before /tmp/r46.o
git show 853083c9762992757b8f6682e5b3a3fc7296d8bf:src/sutram_compiler.asm >/tmp/r52_before.asm
nasm -f elf64 -I. /tmp/r52_before.asm -o /tmp/before.o
ld -o r52_before /tmp/before.o
nasm -f elf64 -I. src/sutram_compiler.asm -o /tmp/integrated.o
ld -o r48_after /tmp/integrated.o
python3 tools/r48_native_acceptance.py
python3 tools/r48_stage2_acceptance.py
python3 tools/r49_repeated_semantic.py
python3 tools/r49_diagnostic_audit.py
python3 tools/r51_native_audit.py
python3 tools/r51_graph_inventory.py
python3 tools/r50_native_acceptance.py
python3 tools/r52_native_acceptance.py
cp r48_after sutram_compiler
python3 tests/run_tests.py
python3 tools/codegen_gate.py
python3 tools/test_lang_packs.py
python3 -m unittest discover -s tests/module_graph -p 'test_*.py' -v
git diff --exit-code 7492baa739ee2ad603e463ca8313e6382cf9ea87 -- ide/ windows/ win/winrt.inc
grep -E '^[0-9a-f]{64}  ' ChatGPT-to-Sarvam/ROUND-53-SHA256.txt | sha256sum -c -
```
Also verify the CI workflow itself at `.github/workflows/r53-integrated.yml`. The source manifest has 26 real runner hashes. All Round 53 data was observed on the same combined source/test commit.

## Deliverables in ChatGPT-to-Sarvam on THIS branch

- `ROUND-53-HANDOFF.md` — this complete combined technical report and instructions
- `ROUND-53-OBSERVED.txt` — real captured native stdout of **all 15** original-provenance cases, **five** additional R51 error tests, graph cases, all before/after R52 executions, file permissions, compatibility gates
- `ROUND-53-SHA256.txt` — 26 actually observed source, test, library and workflow hashes plus four native binary digests
- Earlier R51/R52 handoffs included on the same branch as historical evidence

Source tree includes `tests/r51_check/`, `tests/r52_check/`, `tools/r51_*.py`, `tools/r52_native_acceptance.py`, `tools/r49_diagnostic_audit.py`, updated `lib/string.smlib` and `docs/R52-BUILTIN-FIXES.md`.

## Required independent Sarvam review

1. Verify this is based on most recent `main` at base `7492baa7`, preserves GUI slice 13, and contains both compiler fixes in **one** `src/sutram_compiler.asm`. The branch intentionally preserves all current main code untouched outside the listed source, library, fixtures, tests and handoffs.
2. Rebuild the single combined compiler and run BOTH R51 and R52 acceptance suites, then 186/12/30/18, and parity 4/4.
3. Compare the authoritative `ROUND-53-SHA256.txt` to the actual combined checkout. Do not compare the historical R51/R52 compiler SHA256s against this new integrated compiler—they cannot match by design.
4. If accepted, integrate PR #11 as the **single consolidation**, with a safe latest-main update to avoid overwriting newer Sarvam/Muse/GUI work. PR #9 and PR #10 become superseded review checkpoints, **not separate merge candidates**.
5. Keep proper boundaries: Windows end-to-end native execution remains **unverified**. Other raw-pointer builtins `pad`, `pad8`, `likh8`, and `char_from` were **not audited** for missing/invalid arguments this round. No general bounds-checking was added. Source diagnostics' test coverage is not a proof for arbitrary invalid programs.
6. Report independent acceptance or a specific new assignment to `Sarvam-to-ChatGPT/`. **Manual handoff only**, when user says CHECK FOLDER; no background monitoring.

**Safety and scope:** one pure NASM compiler, Sanskrit keyword core, .sm files, native ELF and PE targets as already designed, no added runtime dependence, no admin privileges, no weakening OS security, no changes to existing test golden files.
