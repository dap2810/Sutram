# Sutram ROUND 51 — ChatGPT → Sarvam acceptance handoff
**Date:** 2026-10-10
**Incoming assignment:** `Sarvam-to-ChatGPT/ROUND-51.md`
**Main base:** `8a81350389d8ba7eeb9038ac71338403fab8a414` (retains accepted R49/R50 + newer Linux GUI slice 12)
**Source-tested commit:** `1773cb759fff9d1773ad26a568a139f4376808f3`
**Review branch:** `feature/r51-origin-tracking-20261009`
**Draft PR:** https://github.com/dap2810/Sutram/pull/9
**Native CI:** https://github.com/dap2810/Sutram/actions/runs/38053564203
**CI job:** `114217388156` — SUCCESS
**Review status:** Ready for independent Sarvam reproduction; **do not merge until accepted**.

## Implementation and why
- Preserved a check-mode-only **byte-level origin sidecar** through repeated `ayojan` expansion: `r51_src_file/r51_src_off` and destination arrays track actual original path and byte offset. Legacy imports stamp original file; copy operations preserve prior origin; namespaced rewrite tracks original offsets through token rewriting and removed `niryat` directives; the sidecars swap alongside expanded source each pass.
- `r51_print_origin` and `r51_print_original_context` derive original basename, 1-based line/UTF-8-aware column, source text and caret from true on-disk origin, including imported semantic backpatches and nested imports.
- In recoverable check-mode compilation, independent missing imports are accumulated up to the bounded diagnostic cap, avoiding first-error-only behavior; this is distinct from graph cycle handling, whose traversal has its own safety limits.
- Standard graph diagnostics now include source column for tested missing module, cycle, not exported, duplicate export, v1 alias and namespaced alias reuse; corrected `E_MODULE_V1_ALIAS` to use `file:line:column: Sutram Error [...]` including the required space.
- `tools/r49_diagnostic_audit.py` now uses the **actual native compiler output**, verifies 15 fixtures with exact expected source basename, line number, error code, positive column, count and nonzero exit, and asserts no binary side effects. It fails CI if any error is unlocated, attributed to the wrong source or unexpectedly omitted.
- Added `tools/r51_native_audit.py`, `tools/r51_graph_inventory.py`, five adversarial `tests/r51_check/*.sm` and four module fixtures `tests/r51_check/lib/*.smlib`.
- No accepted golden output was updated. No ordinary codegen changes were intended; four independently built programs matched accepted R46 byte for byte.

## Actual CI observations (not projected)
```
R49_AUDIT_STATUS wrong_provenance=0 unlocated=0 universal_diagnostics_accepted=1 cases=15 failures=0
R51_ACCEPTANCE PASS failed_cases 0
R48_ACCEPTED_CHECK_TESTS,parse_diags=3,native_byte_equal=4,check_valid=1,no_output=1
STAGE2_PASS structural=3 nested=2 unclosed=1 undefined=3
R49_REPEATED_SEMANTIC_PASS,unique_correct_lines=3,no_output=1
R50_ACCEPTED: runtime byte writes, byte truncation, char_at, vartani_len and vartani_cmp; 2/2 native executions; 2/2 --check
PASS=186
12 codegen-gate PASS tests
30/30 pack checks pass
Ran 18 tests ... OK
```
The 15 audit cases cover root/top-level and nested syntax, original imported `faulty_r49.smlib`, two-level nested `inner_r51.smlib`, namespaced `broken_ns_r51.smlib`, 3 independently located imported unresolved functions, 3 missing `ayojan` modules in a single source, nested brace failures/EOF, and five graph diagnostic classes. Exact raw compiler stdout (every new fixture) is in **`ChatGPT-to-Sarvam/ROUND-51-OBSERVED.txt`** with links to full immutable CI logs.

## Reproduce independently on a clean checkout
```bash
git fetch origin
git checkout feature/r51-origin-tracking-20261009
# Ubuntu with NASM and ld available; compiler syntax remains pure x86-64 NASM.
git show 72b824f70049765c3977db07d712a1a604b89434:src/sutram_compiler.asm >/tmp/r46.asm
nasm -f elf64 -I. /tmp/r46.asm -o /tmp/r46.o && ld -o r48_before /tmp/r46.o
nasm -f elf64 -I. src/sutram_compiler.asm -o /tmp/r51.o && ld -o r48_after /tmp/r51.o
python3 tools/r48_native_acceptance.py
python3 tools/r48_stage2_acceptance.py
python3 tools/r49_repeated_semantic.py
python3 tools/r49_diagnostic_audit.py
python3 tools/r51_native_audit.py
python3 tools/r51_graph_inventory.py
python3 tools/r50_native_acceptance.py
cp r48_after sutram_compiler
python3 tests/run_tests.py
python3 tools/codegen_gate.py
python3 tools/test_lang_packs.py
python3 -m unittest discover -s tests/module_graph -p 'test_*.py' -v
grep -E '^[a-f0-9]{64}  ' ChatGPT-to-Sarvam/ROUND-51-SHA256.txt | sha256sum -c -
```
NOTE: the manifest includes descriptive header lines and a byte-output digest section, so use `grep -E '^[a-f0-9]{64}  ' ChatGPT-to-Sarvam/ROUND-51-SHA256.txt | sha256sum -c -` for manifest verification instead of passing the entire prose file to `sha256sum -c`.

## Sarvam: required independent review
1. Confirm ancestry at `8a813503` and preservation of `ide/sutram_gui_linux.asm`, `tools/test_x11_edit.py`, `win/winrt.inc` and all accepted main files. Only NASM source, diagnostic scripts/fixtures and new CI workflow should differ.
2. Inspect source-map capacity and byte bounds; verify correct origin after repeated **and namespaced** `ayojan` expansion, alias rewriting and inserted newlines. Try multi-level and cyclic imports with edge-position errors. Do not accept falsely attributed filenames/columns.
3. Reproduce 15-case audit on a clean Linux checkout, require `wrong_provenance=0, unlocated=0, universal_diagnostics_accepted=1`; run raw `tools/r51_native_audit.py` and `tools/r51_graph_inventory.py`; verify that 3 separate module errors and 3 semantic errors accumulate with no generated binary.
4. Verify four R46 byte-identical output SHA-256 digests in the accompanying manifest. Re-run 186/12/30/18 regressions; do **not** update expected goldens to camouflage regressions.
5. Inspect **limits**: this universal acceptance flag certifies the **15-case acceptance corpus**, not a formal proof for all possible invalid programs. Check additional `E_EXPORT_UNDEFINED`, `E_MODULE_LIMIT`, mixed semantic/graph errors, and max-8 recoverable error boundaries separately before declaring universal coverage outside the corpus.
6. Windows end-to-end `--check` and generated native executable execution remain explicitly **out of scope for Round 51** as instructed; do not claim Windows acceptance.
7. If independent verification passes, accept PR #9 or synchronize only its changed files into current main (preserve concurrent GUI work). Report decision and next assignment under `Sarvam-to-ChatGPT/`. This process remains manual: only check on user request, no background watcher.

## SHA-256 and exact logs
- `ChatGPT-to-Sarvam/ROUND-51-SHA256.txt` — GitHub Actions generated 13 file hashes and four R46 generated-binary digests; compiler source SHA256 `cc5c0ff9de3ace6b76a87ae71b4cff260c3648c49fcd3d3108ba4ae49260c318`.
- `ChatGPT-to-Sarvam/ROUND-51-OBSERVED.txt` — stdout for every accepted fixture and graph-family example extracted directly from successful CI.
- `https://github.com/dap2810/Sutram/pull/9/files` — source code diff for independent review.

**No automatic merge, no security relaxation, no unexpected toolchain/runtime dependencies.**
