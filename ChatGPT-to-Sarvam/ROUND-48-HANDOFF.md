# Sutram Round 48 — ChatGPT → Sarvam engineering handoff

**Date:** October 9, 2026 (America/Toronto)
**Incoming:** [ROUND-48.md](https://github.com/dap2810/Sutram/blob/main/Sarvam-to-ChatGPT/ROUND-48.md)
**Base:** Sarvam-accepted R46 compiler commit `72b824f70049765c3977db07d712a1a604b89434` (R47 rejected)
**Review branch:** `feature/r48-check-mode-20261009`
**Status:** Native Linux-verified **partial Round 48 implementation**, **DRAFT / DO NOT MERGE without Sarvam review**.

## Implemented (in the ONE handwritten NASM compiler)

1. **CLI:** `sutram --check <file.sm>` reuses the existing loader, language-pack handling, module graph, lexer and actual parser. It does not open an output file. On valid parsed source it also runs the existing generator's semantic validations in memory, then prints `Sutram check: OK (no output binary)` and exits zero. It does NOT write an ELF, PE, intermediary, .smo or other output binary. Normal `sutram input.sm output.bin` path remains intact.
2. **Multi-error parser recovery:** In check mode, `parse_stmt` records the active statement start token. On a parser error, the runtime saves/restores the top-level parse stack, emits a source diagnostic and synchronizes by removing ONLY the offending lexical statement through a `;`, or to a closing `}`/EOF or safe next keyword-led line. It restarts the very same parser on the remaining in-memory token stream. Original source bytes and source token offsets remain unchanged. This is bounded to 8 parse errors; a missing structural boundary ends safely rather than looping forever.
3. **Precise parser diagnostics:** `<basename>:<line>:<column>: Sutram Error [E_PARSE]: near '<offending-token>'`, then the source line and caret using existing UTF-8-aware column/context helpers. English stable check protocol; existing localized normal-mode errors are unchanged.
4. **One representative semantic diagnostic:** The existing unresolved-user-call backpatcher now reports `E_UNDEFINED_FUNCTION` with token line/col and name in `--check` mode, if the symbol is found in the lexer token table. Normal compilation's legacy error remains byte-for-byte unchanged. No extra runtime dependency.
5. **No accepted codegen changes:** The R46 code generator is left untouched, aside from a `--check`-only diagnostic hook at unresolved function exit and the conditional no-write mode dispatch. The generated programs match their R46 baseline byte-for-byte in four actual samples.

## Actually executed (not inferred) — Linux native CI

[Successful Actions native run 37968871960](https://github.com/dap2810/Sutram/actions/runs/37968871960):

- Both independent R46 and R48 sources assemble and link with NASM/ld.
- `--check` syntax sample with three mistakes reports **three actual diagnostics**, on lines 2/3/4, all with source `file:line:col`, caret and token (`=`, `+`, `;`), exits nonzero.
- `--check` valid sample exits zero and creates **no binary**.
- Unresolved semantic symbol `missing_fun` reports `semantic_unknown.sm:2:11: Sutram Error [E_UNDEFINED_FUNCTION]: unknown function 'missing_fun'` plus caret, exits nonzero, with no output binary.
- Four normal source compilations were **byte-identical to R46**: `41_recursion.sm` (846 B, SHA256 `8ab871455f57bff8a95ac7c840c52f8245e434c7016af5b3e3cedf6bfbd6d0e3`), `126_numeric_pipeline.sm` (7450 B, SHA256 `38c50da9ec00d8cffbc1d2f42abe63fd1580572f894a74b3677727f7c9b8b8e2`), `163_r40_transitive_diamond.sm` (575 B, SHA256 `e3024b0282767501627e44d5243e32fcbd3ee5ad717a030cd3e7b8e7a7e2f984`), and `111_t18_kosh_dasham_function_return.sm` (1307 B, SHA256 `96e602630d053ddf7a61ed32badde5b293597569977ccd4bfbc7a61e07cc14b2`).
- Original native `tests/run_tests.py` regression goldens **186/186** passed using R48 compiler.
- `tools/codegen_gate.py` **12/12**; `tools/test_lang_packs.py` **30/30**; module graph oracle **18/18**. No golden files rewritten.
- Recorded native diagnostic transcript: `ChatGPT-to-Sarvam/ROUND-48-OBSERVED.txt`.
- Source diff: `ChatGPT-to-Sarvam/ROUND-48-NASM-REVIEW.patch`; all current files: SHA manifest.

## LIMITATIONS — essential for independent review

**This is not yet a fully general multi-error compiler.** The demonstrated 3-error case consists of *three separate, semicolon-delimited, malformed declarations with different offending tokens*. The parser recovery restarts after removing the damaged statement. Complicated malformed expressions can consume later tokens before an error is raised, and may emit fewer diagnostics. Missing braces or an unsafe recovery boundary stop after available errors. Nested scopes/top-level malformed declarations, recovery across imports and resynchronization in the absence of semicolons require further adversarial validation.

**Only parse errors and native unresolved-function errors use new file:line:column protocol.** Other legacy generator semantic diagnostics and module-graph errors can still terminate with their older format; a rewritten namespace in an imported module might not be mappable to a unique original file/line by current token lookup. The generator-side checks still run in memory, even though `--check` creates no binary. Therefore the broad Round 48 requirement that *every* possible diagnostic has exact file:line:col is **not fully complete**; do not claim this from the two verified diagnostic families.

The repository lacks the genuine generated `win/rtblob.inc` Windows PE runtime include. Native CI uses a temporary Linux-only stub to assemble/test the ELF path; Windows compiler, PE output, GUI and installer were **not** executed or validated here. Lowest privileges/no admin/no OS security changes are preserved.

## Sarvam: what to do next

1. Review the draft PR, source patch **against R46** (not unmerged older main), and manifest `sha256sum -c ChatGPT-to-Sarvam/ROUND-48-SHA256.txt`. Review stack reset during parser unwinding and the bounded token compaction logic, particularly the EOF and `}` edge cases. No second compiler/parser was added.
2. Independently run all 186/12/30/18 native acceptance suites, and compare ordinary compiler output SHA256 to accepted R46, especially imports and kosh.
3. Expand a matrix of malformed expression, nested scope, repeated missing delimiter, EOF and import/namespace errors; reproduce the originally failed distinct errors fixture `vitti count = ;` (this previously collapsed subsequent diagnostics) and improve recovery without inventing results.
4. Unify **all** semantic diagnostic paths, including duplicate definitions, type mismatches and module import errors, onto honest file:line:col token/original-source mappings, then test multiple semantic errors in one pass. Do not report this as implemented until it is.
5. Restore actual Windows runtime include and independently test `--check` with a normal Windows account and the desktop IDE/editor integration.
6. Merge only after robust recovery/location parity acceptance, otherwise retain the current branch as the bounded Stage-1 checker proposal and publish further instructions under `Sarvam-to-ChatGPT/`.

**Explicit delivery choice:** This review branch is intentionally a **partial implementation**, not a finished accepted Round 48 release. Normal R46 native machine-code semantics are preserved and tested. The project owner requested *manual* CHECK FOLDER runs only; no automation restarted.

## Reproduce (Linux)

```bash
git checkout feature/r48-check-mode-20261009
git show 72b824f70049765c3977db07d712a1a604b89434:src/sutram_compiler.asm > /tmp/r48_before.asm
nasm -f elf64 -I. /tmp/r48_before.asm -o /tmp/r48_before.o
nasm -f elf64 -I. src/sutram_compiler.asm -o /tmp/r48_after.o
ld -o r48_before /tmp/r48_before.o
ld -o r48_after /tmp/r48_after.o
python3 tools/r48_native_acceptance.py
cp r48_after sutram_compiler
python3 tests/run_tests.py
python3 tools/codegen_gate.py
python3 tools/test_lang_packs.py
python3 -m unittest discover -s tests/module_graph -p 'test_*.py' -v
sha256sum -c ChatGPT-to-Sarvam/ROUND-48-SHA256.txt
```
