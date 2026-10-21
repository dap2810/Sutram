# ROUND-95 WS1 — Byte-exact audit of the ALREADY IMPLEMENTED `SUTRAMO1` format

**AUTHORITATIVE IMPLEMENTATION:** `docs/OBJECT-FORMAT.md`, `src/r28_object.inc` and `linker/sutram_link.asm` from Claude's **R28**. On 2026-10-21, Claude's R28 was integrated **while this review was under way**; the earlier `SUTSMO1\0`/64-byte-header proposal was incompatible and is **SUPERSEDED**, not an accepted on-disk format. **Never implement it against `SUTRAMO1` without an explicitly versioned migration.** This document pins the *actual* R28 bytes and notes review boundaries. Normal compilation (without `--object`) continues on the original no-linker path.

## Binary schema — implemented version 1

Every integer is **little-endian unsigned 64-bit**. All sizes and offsets are **byte counts**. No padding, string table, signatures, module IDs or flags. Layout (this order is exact):

| Offset / width | Value |
|---|---|
| byte 0, 8 bytes | ASCII `SUTRAMO1` = `53 55 54 52 41 4d 4f 31` (magic includes format version) |
| byte 8, u64 | `code_size` = `C` |
| byte 16, u64 | `symbol_count` = `S` |
| byte 24, u64 | `relocation_count` = `R` |
| byte 32, `C` bytes | raw x86-64 CODE; the object defining `mukhya` has its entry at code offset 0 |
| byte `32+C` | first **symbol** (if `S > 0`) |
| after S symbols | first **relocation** (if `R > 0`) |
| after R relocations | mandatory EOF; trailing bytes rejected |

Each symbol entry is **`offset:u64, name_len:u64, name[name_len] (exact bytes)`**. The offset is relative to that object's CODE, **not** to the file or final ELF. Each relocation entry is the *same serialization* **`field_offset:u64, name_len:u64, name[name_len]`**: the field offset identifies the **first of four disp32 bytes inside this object's CODE**, not the preceding opcode. Names are length-delimited raw source-name bytes, without NUL or implicit Unicode normalization. There is **no module qualifier or visibility flag** in R28's format: symbols occupy one global linker namespace, and all defined functions are exported.

**Field/hole rule:** the compiler leaves four bytes to fill for an unresolved function reference. The linker finds the target by exact symbol name, lays the unique `mukhya` object first and other objects in command-line order, and calculates **`D = target_final_CODE_offset − (caller_final_CODE_field_offset + 4)`**, then writes little-endian **signed rel32** into that field. The same formula works for the existing internal `E8 + disp32` direct call and RIP-relative function-address reference. Missing/duplicate symbols and no/multiple main must fail. **R28 does not encode opcode/kind or arity in a relocation**; this is a deliberate *limitation*, not a claim that every kind of relocation is safe. A real LLVM/ELF `-4` relocation addend uses a different `P` convention: do not copy the `-4` into these records.

**One concrete synthetic two-object fixture (reference-oracle only, NOT compiled from `.sm`):**
- ROOT: `C=69, S=1, R=1`, symbol `mukhya@0`, relocation `joda@11`. Header 32 + code 69 + symbol `(16+6)=22` + reloc `(16+4)=20` = **143 bytes**. Offset 11 points at an `E8` instruction's displacement; the `E8` is at code offset 10.
- LIB: `C=7, S=1, R=0`, symbol `joda@0`. Header 32 + code 7 + symbol `(16+4)=20` = **59 bytes**.
- With root first and LIB second, target is final CODE offset 69; relocation field is 11; `D=69-(11+4)=54` = **`36 00 00 00`**. Combined CODE=76 bytes; a synthetic developer-time ELF can print `42\n` and exit 0. These numbers specify the byte format and arithmetic; **they do not prove Sutram `.sm` emission**.

## Smallest milestone already delivered; what remains

Claude R28 reports `sutram_compiler --object in.sm out.smo`, a **project-owned NASM** `sutram-link out.bin main.smo lib.smo`, a real two-object linking test, and **199/199 linker checks**; its suite remains **218 PASS**, with ordinary-path v237-v238 Linux outputs **466 identical / 77 identically refused**. This is *Claude's reported execution*, not newly executed here. The on-disk R28 format **does not** need the owner's pending 371 variable-kind annotations to *link by name*. They **are** needed (or equivalent signature metadata and checking) for **verified cross-object arity/type safety**. Current linker cannot check arity and exports every name. Do not call it full module privacy, typed linking, Windows linking, or C FFI.

**Review-only defensive hardening (does not redefine version 1 bytes):** before parsing arbitrary `.smo`, use overflow-safe `C ≤ actual_length−32`, enforce table counts/bounds, `0 ≤ symbol.offset < C`, exactly one `mukhya` at 0, `field_offset+4 ≤ C`, optional stricter opcode/hole checks consistent with all R28 generated forms, no overlapping reloc fields, and signed rel32 range before mutation. `linker/sutram_link.asm` currently checks a truncated table and bad/missing/duplicate names but writes `eax` without an explicit signed-range check and does not validate every defined symbol offset; malformed-object differential tests are recommended. These are source-review findings, **not an observed exploit**. Any on-disk addition of module IDs, visibility, target/ABI, signature, hash, data relocs or new relocation kinds must use a **new version** and retain the existing R28 reader's fail-closed behavior.

**Boundaries:** `SUTRAMO1` is a custom object, **not ELF `ET_REL`**; the native linker builds with NASM/ld at developer time, but a normal Sutram end user never invokes a linker. The existing independent GNU control (R93) measured PLT32/PC32 relocations, not Sutram's object serialization. The synthetic reference oracle is a developer-time validation, not a replacement linker.
