# ROUND-93 WS1 — Smallest object/linker design shared by modules and future FFI

**Status: DESIGN ONLY. NO compiler changes, no Sutram `.smo` output, no native Sutram linker test.** Source pin: `main` `00388c3c0b3625ac475b8d6f47866e6e64373223` (project log v266, compiler v236). This is an architecture phase, **not a one-round capability patch**.

## The smallest *real* milestone

Keep existing `# sutram-module-v1`, `niryat`, and `yoj ganita@g` semantics intact. A **new explicit, opt-in object/link profile** (proposed commands, **not existing CLI**) compiles **each source independently**:

```text
sutram --emit-object lib/ganita.smlib -o ganita.smo
sutram --emit-object main.sm -o main.smo
sutram --link main.smo ganita.smo -o main.bin
```

`lib/ganita.smlib`: `# sutram-module-v1`; `niryat joda`; `prakriya joda(a, b) { prati a + b }`. `main.sm`: `# sutram-module-v1`; `yoj ganita@g`; `mukhya() { likha(g__joda(17,25)) }`. **Acceptance:** two source files independently yield two actual Sutram objects; a native link produces standalone Linux executable printing `42\n` and exiting 0. The source of `ganita` must **not** be pasted into the root translation unit.

## `.smo/1` (proposed *private* versioned binary container, little-endian)

- **Header:** exact magic/version, target OS/arch, ABI/version and compiler feature profile; canonical module ID (independent of import alias); source SHA-256 and public-interface digest; bounded counts, file length, checked offsets/sizes for CODE, STRINGS, SYMBOLS, RELOCS and imports. All on-disk references are **offsets/lengths, never process pointers**. Reject overlap, integer overflow, unsupported versions, bad encodings and hash mismatch.
- **CODE:** complete module-local text fragment with entry offsets; **no implicit `_start` in library modules**. Initially one root entry only. No source-text expansion, duplicate runtime startup, module globals/initializers, shared mutable data, foreign objects, `dasham`, `kosh`, `vibhag`, methods or `phal` *across* object boundaries: explicit diagnostic until ABI rules exist.
- **SYMBOL:** exact UTF-8 byte-string `(module_id, source_name)`, section-local offset, defined/imported, exported/private, and **plain integer function signature** (0–6 qword arguments; integer return; ABI ID). Aliases are import-edge bindings and do **not** replace a module identity. Private symbols cannot satisfy external references; duplicate public definitions are errors.
- **RELOC:** `{section=CODE, field_offset, kind, target_symbol_index, signed_addend}`. Define **CALL_REL32** for `E8 [disp32]` and **FUNCPTR_RIP32** for `48 8D 05 [disp32]` (`lea rax,[rip+disp32]`). Validate the expected instruction bytes and that the 4-byte field fits CODE. Compute `disp32 = target_final_offset + addend - (field_final_offset + 4)`; require signed-32-bit reach and apply only after all validations. `addend=0` for the two normal call/address cases; ELF `R_X86_64_* ` `-4` addends use a different `P` convention and must be translated, not copied blindly. **Only CALL_REL32 is required for the first two-module executable**; represent FUNCPTR_RIP32 now so R23 function values cannot be silently mislinked, but reject external funcrefs until tested.

## Link driver and fail-closed phase boundary

1. In **object mode only**, reuse the existing v1 module-graph/`niryat` visibility checks but **bypass `expand_imports` text flattening**. Refactor the compiler's code-generation entry so it can emit independent library functions **without a root `mukhya` startup**, preserve unresolved external names and typed patch sites, and serialize symbol/reloc metadata. The unchanged default route remains source flattening + native `ET_EXEC` / PE.
2. Validate **all** objects, module identities, imported signatures, interface hashes, graph order, symbol uniqueness, visibility and relocation bounds before mutation. Dedupe diamond imports by canonical module ID; deterministic order (root startup first, dependency function bodies once). Resolve every symbol and patch an in-memory final CODE image. Reject missing, private, duplicate, wrong-arity/type, stale, overflow, malformed, unsupported-ABI inputs with an explicit nonzero diagnostic and **no executable**. Write temporary output, publish only after success; no network resolver, registry, privileged location or required end-user linker.
3. Emit **one** native image. For the integer-only Linux milestone, a final combined `code_buf` with one entry can use the existing `write_elf` header/program-header/output path. Later, PE requires one final runtime shim/import table and recalculated RVAs; foreign ELF64 `ET_REL` parsing and the actual platform C ABI are a **separate subsequent FFI adapter**, not magically provided by a custom `.smo`.

## How much can be reused? The decisive answer

**The final executable *wrapper* can mostly be reused; almost none of the missing *object writer and linker* exists.** `src/sutram_compiler.asm:2105–2188` always graph-checks, flattens imports, parses, calls one `gen_code`, then writes the result. `backpatch_calls` at **12046–12138** resolves into a single `func_table`/`code_buf`; R23 emits a separate RIP-relative function-address patch (`src/r23_capabilities.inc:130–168`). The Linux writer at **23409–23486** emits **ET_EXEC (type 2)** with one program header and no section table; it has no object symbols or relocations. Its simple final header/byte writer can be reused **after** linking, **not** to emit `.smo`. R56 also finalizes globals relative to a single `code_sz` (**22279–22330**) and PE emits one blob/import/data arrangement (**23794 onward**): these are distinct future relocations, not safe to copy by concatenation. `src/r71_module_link.inc` provides only an **in-memory** checked symbol resolver and **E8-only** patcher, not a loader/object emitter/driver. **Therefore STOP at reviewed design and stage implementation separately; do not describe this as a small patch.**

**Required promotion evidence:** actual two-`.sm` Sutram objects + linked `42\n`, private/missing/duplicate/arity/rel32-range/corrupt-object negatives, unchanged old `yoj` goldens, full Linux gates and fuzzers/crash corpus, Windows owner acceptance in its own gate. The accompanying two-object GNU assembly control is **not** a Sutram compiler/object-format test.
