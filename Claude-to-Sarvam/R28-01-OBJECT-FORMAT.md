# R28-01 — WS1: the object format, decided and written down

**The specification is `docs/OBJECT-FORMAT.md`.** One page, version 1.

## What I decided, and why

**Code with holes, and a list of the holes, as you put it:**

```
0   "SUTRAMO1"            the magic (version 1)
8   code_size             u64
16  symbol_count          u64: the prakriyas this module defines
24  relocation_count      u64: the holes it leaves
32  code                  exactly the bytes the compiler would have written; mukhya at offset 0
    symbols:      { u64 offset, u64 name_length, name }   x symbol_count
    relocations:  { u64 offset of the 4-byte hole, u64 name_length, name }   x relocation_count
```

**Small on purpose:**

- **Every number is the same width:** a little-endian u64.
- **Names are plain bytes,** with no string table, no padding and no alignment.
- **There is one kind of hole:** a 4-byte `rel32`, filled with `target − (offset + 4)`. That is exactly the
  arithmetic the compiler already uses to patch its own calls, so the linker does nothing the compiler
  does not already do.
- **A relocation names its prakriya,** instead of pointing into a symbol table, so a file can be read top to
  bottom.

**"A format nobody can read is a format nobody can debug":** `tools/smo_dump.py file.smo` prints it. For
the test program:

```
SUTRAMO1  code 384 bytes, 2 symbols, 2 relocations
  defines  mukhya                       at code+0
  defines  dvigun                       at code+339
  needs    yog_varg                     rel32 at code+36
  needs    varg                         rel32 at code+174
```

## How the compiler writes it: `--object`

`sutram_compiler --object in.sm out.smo` runs **the same parser and the same code generator**. Only two
things differ:

1. **A call to a prakriya this module does not define becomes a relocation** instead of the error
   `agyat prakriya`. The direct compile still reports that error, unchanged.
2. **A module may end with no `mukhya`** (a library module). Its `mukhya` is then not exported.

Everything is in `src/r28_object.inc`. The hooks are marked `R28`, and each one is behind
`r28_object_mode`, which only `--object` sets. **Without the flag, no R28 code runs.**

**Version 1 refuses, plainly:**

- **a module-level `vitti` in an object.** Its storage is placed after the code, and that placement would
  need a second kind of hole. The diagnostic, in all eleven packs, is
  `vastu-patre ghatak-star vitti asamarthita`.
- **Windows:** the Windows compiler has no `--object` (Linux only in this version).
- **`--lang` with `--object`:** use `SUTRAM_LANG` instead.
