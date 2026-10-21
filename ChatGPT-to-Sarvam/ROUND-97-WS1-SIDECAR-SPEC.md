# ROUND-97 WS1 — Checked foreign declarations, sidecar v1 (proposed, not compiled by Sutram)

**Purpose:** give the opt-in Sutram object compiler a *compile-time signature* for a foreign function **without a fake Sutram body**, changing any of the 11 keyword packs, or inventing a second `SUTRAMO1` import table. Source pinned to main `18dbad0a9cb732d09ace5e3d348713149db83057`, native compiler v239. THIS IS NOT ACCEPTED SYNTAX OR AN IMPLEMENTED FLAG; Claude/Sarvam to review.

## Exact file bytes and grammar

Proposed extension `.sffi`, exact **UTF-8 ASCII subset** with LF-only lines (no BOM, CR, NUL, spaces or comments). Max file size **8192 bytes** and **64 declarations**. Required first line is exactly:

```text
sutram-ffi-v1|linux-x86_64-sysv
s_add|2|i64,i64|i64|sutram_ffi_add
```

Every declaration is **one LF-terminated line** of exactly FIVE `|`-separated fields, in this order: `sutram_name|arity|arg_kinds|return_kind|foreign_elf_symbol`. (The header has only two fields.) `sutram_name`: ASCII `[A-Za-z_][A-Za-z0-9_]{0,62}`; `external_symbol`: ASCII `[A-Za-z_][A-Za-z0-9_]{0,127}`; both case-sensitive and compared by exact bytes. `arity`: one ASCII digit `0`–`6`, no sign or zero padding; `arg_kinds`: exactly `arity` comma-separated tokens from `i64,ptr,f64` (empty for arity zero); `return_kind`: one `i64|ptr|f64|void` token. No unknown fields, duplicate local names, duplicate foreign-symbol bindings, local name collision, numeric overflow, implicit ABI selection or symbol normalization. **V1 implementation milestone supports ONLY `i64` arguments and `i64` return**; a `ptr,f64,void` signature is recognized but rejected with `E_FFI_ABI_UNSUPPORTED` until its representation and compiler type checker are reviewed. End with LF. No network/cache lookup, external package manager, admin or environment-dependent sidecar search.

**Why both names?** A Sutram source calls `s_add(17,25)`, which is declared *locally* with two integer arguments, while the linked symbol is exactly `sutram_ffi_add`. That external name is what the `SUTRAMO1` relocation **must** contain. The foreign `.text` converter emits one **definition** with the same `sutram_ffi_add` name. No aliases or stub implementations are emitted.

## Discovery: explicit opt-in flag first, never ambient `yoj`

Proposed **new CLI only**: `sutram_compiler --ffi-sidecar ./foreign.sffi --object main.sm main.smo` (or with approved `--separate` mode), and `sutram_build.py --ffi-sidecar ... main.sm -o out` if a builder is extended. The flag must be recognized **only alongside an opt-in object/separate mode**; `sutram_compiler main.sm out.bin` must be byte-for-byte unchanged and must never consult a sidecar. Resolve the one explicit path deterministically relative to the invoking project root, preserve source provenance and fail closed on missing/unreadable file, symlink/path traversal outside approved root, ambiguous path or oversized file. **Do not silently auto-import `.sffi` via `yoj`** in v1: `yoj` already has lexical and alias/visibility contracts. A later approved importer mapping could reuse module-root lookup but requires separate collision/alias tests. The sidecar itself does NOT define `prakriya` in source syntax.

## Compiler integration: a wrong arity must fail BEFORE writing `.smo`

1. Parse and validate sidecar **before** source compilation; register a separate `ffi_defs` table (local name, exact external symbol, arity, kinds, result ABI, sidecar line). Reject collisions with user `prakriya`, ordinary builtins, reserved names, alias-expanded names or other sidecars. **Do NOT create a normal `FUNCDEF`, `r7_defs`, R55 prototype expecting a body, or fake `prati 0` AST**: those could redirect codegen to a nonexistent body. Use a distinct foreign-call classification.
2. Reuse actual `r7_note_call` sites and `r7_check_arity` logic (`src/sutram_compiler.asm:7666–7767`): after the normal local-definition lookup, consult the **sidecar foreign signature**. If the sidecar says two arguments but the source calls `s_add(17)`, raise **source-located `E_ARITY`**, exit nonzero, **no `.smo` written**. `s_add(17,25,1)` must fail identically. A function never declared in source/sidecar must be rejected (not silently made into a foreign import by object mode); distinguish deliberate declared FFI references from generic opt-in unresolved-function relocations. Validate all calls before file output, including nested calls and statement calls.
3. For a correct direct call, use existing x86-64 SysV *integer* registers `rdi,rsi` (up to six integer args `rdi,rsi,rdx,rcx,r8,r9`), return `rax`. Check the normal stack-alignment/callee-saved contract, and prohibit indirect/function-value FFI calls until typed callable signatures exist. In `--object` mode, record an existing `R28` **named `rel32` hole with the external symbol bytes** instead of local-name bytes; **do not** insert any definition in the object's symbol list. `SUTRAMO1` on-disk format **does not change**.
4. Link with a **project-owned NASM** foreign ELF reader/converter (see WS2), then `sutram-link`. Duplicate/missing foreign definitions must fail, not default to zero. No implicit CRT/libc calls. Existing unmarked language modes, goldens and default codegen path must be unchanged.

**Proposed regression cases:** valid `s_add(17,25)` => object relocation name `sutram_ffi_add`, no `s_add` exported symbol, linked program prints `42\n`; wrong arities **1,3** => compile **`E_ARITY`**, located diagnostic and no file; no declaration => compile error; duplicate/invalid records and unsupported f64/ptr/void => compiler error; missing/malformed foreign object => linker error with no executable. Inference-only typed checks are not a substitute for explicit arity. **These native cases are NOT_RUN/NOT_IMPLEMENTED** in R97.

## Evidence boundary

A separate **Python developer-time model** exercised the *proposed sidecar grammar and arity guard* and passed **26/26** checks, with raw result and exact tested script uploaded in this same directory. This is **not** the handwritten NASM compiler enforcing `E_ARITY`. The compiler currently emits `E_ARITY` for *ordinary defined functions*; wiring a foreign-specific table into this stage remains the implementation task. See `ROUND-97-WS1-SIDECAR-ORACLE.py`, `ROUND-97-WS1-SIDECAR-OBSERVED.txt`.
