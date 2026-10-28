# WS1: code that matches the literal `Sutram Error`, so I stopped before changing it

Measured on `main` `5059e61c` (v254), Linux x86-64 (cloud). Found with `git grep 'Sutram Error'` over `src/`, `ide/`, `linker/`, `tools/`, `tests/`, `lang/` and `windows/`.

## A. Matches that would SILENTLY stop working: no failure, wrong behaviour

| Where | What it does with the literal | What happens after the change |
|---|---|---|
| **`ide/sutram_gui_linux.asm` `has_error` (line ~2421), called from the Run path (~2400)** | **Product code.** The Linux IDE decides that a compile failed by scanning the compiler's output for the bytes `Error`. | **A failed compile prints `Sutram dosh: …`, which contains no `Error`. The IDE then takes the failure for a success and runs `run_bin_z`, the binary left by the PREVIOUS successful build.** The user sees an old program's output under a new error. Nothing fails. |
| `tools/test_x11_run.py:72` | It passes if a drawn text contains `compiled` **or** `Sutram Error`. | The second half never matches again. The test keeps passing on the first half alone, so it is weaker and no one is told. |
| `tools/sandesh.py:267` and `tools/r83_pack_structure.py:32` (`TAGS = Sutram Error\|[E_…]`) | They check that every pack keeps the default's `Sutram Error` and `[E_*]` tags unchanged. | **The default loses the tag, and the 10 frozen packs keep it.** The check then fails. Fixing that means one of two things: change the frozen packs, which `LANGUAGE-PRIORITY.md` forbids; or remove `Sutram Error` from `TAGS`, which **silently drops the check.** **This needs a decision.** |
| `tools/test_x11_error_line.py:53`, `tools/test_x11_goto_line.py:47` | Their mock compilers print `Sutram Error [E_TEST]: …`. | They keep passing, but they no longer imitate the real compiler. The IDE finds the line from `<file>:<line>:`, not from the literal, so this is drift, not breakage. |

## B. Matches that would fail LOUDLY, and only need their expected text updated

- **Goldens: 44 in `tests/expect/`.** The list is in `ws1-goldens-that-would-change.txt`. `220_hindi_parse_error` holds the literal too, but runs under the frozen Hindi pack, so it would not change.
- **`tests/sandesh/expect/{default,sanskrit}/`: 18.** The other 90 are in frozen packs, which keep `Sutram Error` (see A).
- **`tests/negative/r70/manifest.json`: 6 expected texts.**
- **Test files:**
  - `tests/r23/test_capabilities.py` 9;
  - `tests/r25/test_phal.py` 9;
  - `tests/r28/test_link.py` 7;
  - `tests/r32/test_ffi.py` 1;
  - `tests/r33/test_ffi_kinds.py` 2;
  - `tests/r34/test_ffi_v2.py` 1;
  - `tests/r34/test_link_windows.py` 9;
  - `tests/r68/test_r68.py` 3;
  - `tests/r83/*` 11 (fixtures).
- **Tools:**
  - **`tools/crash_corpus.py:84`, the crash-corpus GATE.** It requires stdout to start with `Sutram Error`. With the change, 223 of 227 cases fail.
  - `tools/r48_native_acceptance.py`, `r48_stage2_acceptance.py`, `r49_diagnostic_audit.py`, `r49_repeated_semantic.py`, `r51_native_audit.py`, `r52_native_acceptance.py`, `r54_native_acceptance.py`, `r64_source_gate.py`, `r68_native_acceptance.py`, `r71_native_acceptance.py`.
  - `tools/test_namespace_contract_oracle.py`, `tools/module_graph_reference.py`.
  - `tools/ide_examples_windows.ps1`, which falls back to `Error`, so it would report DIFFER.

## C. Outside the 74, and not counted in them

- **Other compiler files: 4 more strings.** `src/r66_indic_lexer.inc` has 1, `src/r68_diagnostics.inc` 2, and `src/r71_unsafe_integration.inc` 1. With 74 changed and these 4 not, the compiler would print both prefixes.
- **The linkers: 38.** `linker/sutram_link.asm` has 8, `linker/sutram_elf2smo.asm` 15, and `linker/sutram_coff2smo.asm` 15.
- **The frozen packs' messages: 137 in each `lang/<pack>.sandesh`.** Under `--lang hindi` and the other frozen packs, messages would still say `Sutram Error`.

## The decisions WS1 needs before it is safe

1. **The Linux IDE has to stop detecting failure by the word `Error`.** I propose the compiler's exit status, which the Windows IDE already uses (`GetExitCodeProcess`). This must land with the rename or before it, never after.
2. **The frozen packs:** keep `Sutram Error` in them, as `LANGUAGE-PRIORITY.md` says, and change the tag rule to accept either prefix? Or change them too?
3. **Scope:** only the 74, or also the 4 other compiler strings and the 38 in the linkers?
