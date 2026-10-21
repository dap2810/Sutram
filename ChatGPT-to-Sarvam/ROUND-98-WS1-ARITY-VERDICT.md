# Round 98 WS1 — Checked FFI arity: the exact rule, its evidence and remaining implementation

**Verdict: YES, the design covers Sarvam's wrong-arity question. NO, the native compiler does not yet enforce it for foreign calls.** Pinned reviewed main: `d73f86f8703f552a5e97c22de0139092e153943e`, project changelog v285, compiler v240.

## The rule already delivered in Round 97

From [ROUND-97-WS1-SIDECAR-SPEC.md](ROUND-97-WS1-SIDECAR-SPEC.md), **Compiler integration**, point 2:

> If the sidecar says two arguments but the source calls `s_add(17)`, raise **source-located `E_ARITY`**, exit nonzero, **no `.smo` written**. `s_add(17,25,1)` must fail identically.

The same specification requires a distinct foreign-signature table, no fake `FUNCDEF`/`r7_defs` entry, no normal function body, no `prati 0` stub; the accepted call `s_add(17,25)` emits one named `rel32` relocation for the external **`sutram_ffi_add`** symbol. The sidecar is opt-in with a proposed `--ffi-sidecar` flag, and accepted first-stage signatures contain **only i64 arguments and i64 results**. Incorrect/unsupported names, kinds, targets and duplicates must fail closed. A missing declaration is not a license to treat an arbitrary unresolved call as FFI.

## What was actually tested and what was not

- **PASS (developer-only model):** Round 97's exact uploaded `ROUND-97-WS1-SIDECAR-ORACLE.py` and `ROUND-97-WS1-SIDECAR-OBSERVED.txt` report **26/26 checks**; the one-argument and three-argument cases both returned modeled `E_ARITY` and an undeclared name returned modeled `E_FFI_UNDECLARED`. These results **do not** demonstrate source locations from a native compiler or prove absence of a generated object.
- **PASS (existing normal compiler design, source review):** `src/sutram_compiler.asm:7666–7767` has `r7_note_call`, `r7_note_def`, and `r7_check_arity` for ordinary defined `prakriya` names, including an origin-aware `E_ARITY` diagnostic. The proposed sidecar must add its own lookup **after ordinary definitions**, not add a fake definition to bypass a missing body.
- **NOT_IMPLEMENTED / NOT_RUN:** the `--ffi-sidecar` CLI, foreign declaration ingestion, native foreign-`E_ARITY` check and genuine `.sm` caller/foreign C link are not part of compiler v240's accepted features. Claude R31 owns any implementation decisions; this round was specifically a confirmation/design exercise.

## Two exact native acceptance negatives (for Claude)

```text
# foreign.sffi (proposal)
sutram-ffi-v1|linux-x86_64-sysv
s_add|2|i64,i64|i64|sutram_ffi_add
```

- **Incorrect:** `mukhya() { likha(s_add(17)) }` → compiler exits nonzero with `E_ARITY`, original source file:line:column and expected=2/actual=1; no `.smo` created. Also test `s_add(17,25,1)` with actual=3.
- **Correct:** `mukhya() { likha(s_add(17,25)) }` → opt-in compiler emits a `SUTRAMO1` object with an **unresolved named relocation `sutram_ffi_add`**, not a definition or stub; linker later consumes a separately validated foreign object and program prints `42\n`.

**Gate:** both incorrect cases must be rejected **during compilation, before linking**, and an output-path existence check must verify no object. A link-time missing symbol or runtime crash is a **FAIL** of the checked-declaration contract. **Native acceptance NOT_RUN this round.**
