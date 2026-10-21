# The Sutram object file (`.smo`), version 1

**ROUND-28.** This file is written by `sutram_compiler --object in.sm out.smo`, read by `sutram-link`
(`linker/sutram_link.asm`), and printed for people by `tools/smo_dump.py`.

**The fundamental is unchanged.** An ordinary program is compiled to a finished executable by the compiler
alone, in one pass, exactly as before; it never touches this format or the linker. `--object` is opt-in.

## What it holds: code with holes, and a list of the holes

Every number is a **little-endian u64**. Names are UTF-8 bytes, with no terminator and no padding.

| Offset | Field | Meaning |
|---|---|---|
| 0 | `"SUTRAMO1"` | the magic, 8 bytes (version 1) |
| 8 | `code_size` | bytes of code |
| 16 | `symbol_count` | the prakriyas this module defines |
| 24 | `relocation_count` | the holes this module leaves |
| 32 | code | `code_size` bytes, exactly what the compiler would have written; `mukhya` (if any) is at offset 0 |
| … | symbols | `symbol_count` × { `offset`, `name_length`, name } |
| … | relocations | `relocation_count` × { `offset`, `name_length`, name } |

**A symbol** is a prakriya that the module defines, and its offset in this module's code. `mukhya` is a symbol
(at 0) when the module has one; a module may have none.

**A relocation** is a 4-byte hole at `offset` in this module's code, left by a call (or a function value) whose
prakriya this module does not define. **There is one kind:** the hole gets `target − (offset + 4)`, the same
rel32 the compiler writes for a call it can resolve itself.

**The file ends exactly after the last relocation.** Anything else is a bad object.

## How `sutram-link` uses it

```
sutram-link out.bin a.smo [b.smo ...]
```

1. Reads every object and checks it: the magic, and that every table fits inside the file.
2. **Exactly one** object must define `mukhya`. It goes first, so `mukhya` is at the start of the code; the
   others follow in the order given.
3. Lays the code end to end, and collects every symbol at its new offset. **A name defined twice is an error.**
4. Fills every relocation from the symbols. **A name nobody defines is an error.**
5. Writes the same executable the compiler writes for an ordinary program: one `PT_LOAD` at `0x400000 + 120`,
   entry at the start of the code, 64 KiB of zeroed memory after it.

**The proof that the format loses nothing:** every program in `examples/` that compiles is also compiled with
`--object` and linked alone; the result is **byte-identical** to the ordinary compile
(`tests/r28/test_link.py`, a gate).

## What version 1 does not do

- **No module-level `vitti`** in an object: its storage is placed after the code by the compiler, and that
  placement would need a second kind of relocation. `--object` refuses it with a diagnostic.
- **No `--lang` flag** with `--object` (`SUTRAM_LANG` works).
- **Linux only.** The Windows executable has its runtime at the start of its image, so linking it needs more.
- **Every prakriya is exported** (including the library modules a `yoj` pulled in), so two objects that both
  `yoj` the same module define its prakriyas twice: link one copy, or `yoj` it in one object only.
- **No C FFI, no data relocations, no archives, no package manager.**
