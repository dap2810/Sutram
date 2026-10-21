# ROUND-95 WS1 — `.smo/1`: byte-exact minimum for OUR NASM linker

**PROPOSED INTEROPERABILITY CONTRACT, NOT YET ACCEPTED CODE.** For Claude R28 review before freezing. Based on R93, pinned main `8dcd3f8cf74fbd008d879ef0e9472ff33cb6fb4e` (project v270, compiler v237). **The ordinary `.sm → native ELF/PE` path must remain unchanged and never invoke any linker.** Only an explicit opt-in mode emits `.smo` or invokes our own NASM linker; **never `ld` in shipping paths**.

## File: exact order and widths

All integers **little-endian**; offsets **0-based byte offsets**; no native pointers, trailing data, compression or implicit padding. File order is **64-byte header → CODE → zero-filled 4-byte alignment → STRINGS → zero-filled 4-byte alignment → SYMBOLS → RELOCS → EOF**. No section can overlap another; arithmetic is checked before allocation or reading. Mandatory `file_size == actual file length`.

| Header byte(s) | Type | Field / required value |
|---|---|---|
| 0–7 | char[8] | `53 55 54 53 4d 4f 31 00` = `SUTSMO1\0` |
| 8–9 / 10–11 | u16 / u16 | `version=1` / `header_bytes=64` |
| 12–13 / 14–15 | u16 / u16 | `target=1` (Linux x86-64) / `ABI=1` (plain signed/unsigned 64-bit integer calls) |
| 16–19 / 20–23 | u32 / u32 | `flags` (only bit0=ROOT allowed) / total `file_size` |
| 24–27 / 28–31 | u32 / u32 | `code_off=64` / `code_bytes` |
| 32–35 / 36–39 | u32 / u32 | `strings_off=align4(code_off+code_bytes)` / `strings_bytes` |
| 40–43 / 44–47 | u32 / u32 | `symbols_off=align4(strings_off+strings_bytes)` / `symbol_count` |
| 48–51 / 52–55 | u32 / u32 | `relocs_off=symbols_off+24*symbol_count` / `reloc_count` |
| 56–59 / 60–61 / 62–63 | u32 / u16 / u16 | `module_name_off` (relative to STRINGS) / `module_name_len` / `entry_symbol_index` or `0xffff` (library) |

For v1: `file_size=relocs_off+16*reloc_count`; `1 ≤ code_bytes ≤ 262144`, `1 ≤ strings_bytes ≤ 8192`, `0 ≤ symbol_count ≤ 128`, `0 ≤ reloc_count ≤ 512`; reject bad flags/targets/ABI/version, overflow, nonzero padding and out-of-range name lengths. ROOT means one defined entry symbol, at CODE offset 0, with a valid `entry_symbol_index`; non-root must use `0xffff`. One ROOT overall. Strings are **raw, strict UTF-8 (no terminator, no embedded NUL)** with bounded byte lengths: module 1–63, symbol leaf 1–128; **compare exact byte strings, never strip, transliterate, concatenate ambiguously or normalize**. The module ID is canonical source resolution identity; aliases attach only to import edges.

**SYMBOL entry: 24 bytes**, repeated `symbol_count` times:

| Entry byte(s) | Field |
|---|---|
| 0–3 / 4–5 | `module_off:u32`, `module_len:u16` (within STRINGS) |
| 6 / 7 | `kind:u8` = 1 defined or 2 imported / `visibility:u8` = 0 private, 1 public (imports require 0) |
| 8–11 / 12–13 | `leaf_off:u32`, `leaf_len:u16` (within STRINGS) |
| 14 / 15 | `arity:u8` = 0..6 / `call_abi:u8` = 1 (integer `rdi,rsi,rdx,rcx,r8,r9 → rax`) |
| 16–19 / 20–23 | `code_offset:u32` for a local definition, `0xffffffff` for import / `reserved:u32=0` |

Defined symbols must belong to this object's header `module_name` and have `code_offset < code_bytes`. Imported symbols must name a specific other module. Keys are pairs `(module bytes, leaf bytes)`. All definitions unique; imports resolve to exactly one **public** definition with identical ABI/arity; no first-match-wins, silent placeholders or private access. Every imported symbol referenced by a relocation must resolve before output.

**RELOC entry: 16 bytes**, repeated `reloc_count` times:

| Entry byte(s) | Field |
|---|---|
| 0–3 | `field_offset:u32`, **relative to this object's CODE start**, points to first of exactly four placeholder bytes |
| 4–7 | `symbol_index:u32`, into this object's SYMBOL table |
| 8 / 9 / 10–11 / 12–15 | `kind:u8=1` (`CALL_REL32`) / `flags:u8=0` / `reserved:u16=0` / `addend:i32=0` |

**How the linker knows a hole:** compiler emits `E8 00 00 00 00`; relocation names its **four zero displacement bytes**, so `field_offset≥1`, `code[field_offset−1]=E8`, `field_offset+4≤code_bytes`, `code[field_offset:field_offset+4]=00000000`, and no overlapping relocation sites. Validate first, patch second. With root CODE at final offset 0 and each library CODE concatenated once, calculate `D = (target_unit_code_base + defined.code_offset) − (caller_unit_code_base + field_offset + 4)`. Require `−2^31 ≤ D < 2^31`, then write `D` as signed little-endian i32. **No addend in the first milestone.** The GNU ELF `-4` addend convention uses a different `P` and must not be blindly copied.

**Minimal measured fixture:** ROOT CODE=69 bytes, imported `ganita::joda(2)` index 1, call hole at CODE offset **11**; library `ganita` CODE=7 bytes, exported `joda(2)` at 0. ROOT file regions: CODE `64+69`, STRINGS `136+20`, SYMBOLS `156+48`, RELOCS `204+16`, total **220** bytes. Library: CODE `64+7`, STRINGS `72+10`, SYMBOLS `84+24`, no relocations, total **108** bytes. Patched call is `69−(11+4)=54` or `36 00 00 00`. The development-only oracle verifies this layout and executes a synthetic linked ELF printing `42\n`. **Not a Sutram compiler output.**

**Deliberately omitted from `.smo/1` milestone:** `LEA_RIP32` function-address relocations (R93 measured `R_X86_64_PC32`; future kind 2 must validate `48 8d 05`), cross-object function values, methods, `phal`/`rdx` status, globals/initializers, `dasham`, slices, `kosh`, ABS/data relocations, Windows/PE, native C `ET_REL` parsing, C FFI, package graph/cache, hashes/interface digests and debug tables. **Unknown relocation kinds MUST fail** rather than quietly linking. This stage needs **no 371 parameter annotations**: plain integer direct-call arity is already available. General type-safe cross-unit APIs will require a separately reviewed typing/ABI phase. Development-time Python/GNU tests do not become shipping dependencies.

**Boundary:** This is a proposed format for Claude's review, not a unilateral freeze. Any changes to widths/layout require a new version and renewed negative corpus; do not silently reinterpret objects. Use temp output and rename only after exhaustive validation; no executable on error. The existing compiler's one-pass `write_elf`/PE output path remains the default, unchanged.
