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

## Separate compilation (ROUND-29): `--separate` and `tools/sutram_build.py`

```
python3 tools/sutram_build.py main.sm -o out        # each module compiled once, then linked
python3 tools/sutram_build.py --graph main.sm       # print the module graph
sutram_compiler --separate in.sm out.smo [root.sm]  # one module, by hand
```

**`--separate` is `--object` with one difference.** A prakriya that a `yoj` brought in is still read, parsed
and checked here - so a call into another module is checked for its **arity** and gets its **return type**
(`dasham` or not) - but it **generates no code** in this object. Its calls become relocations, and its code is
in the object of the module that defines it, compiled once. The optional `root.sm` is the program's root file:
`yoj` looks modules up from its directory, exactly as the whole-program compile does.

**`tools/sutram_build.py`** walks the module graph from the root (the compiler's own lookup: the root's
`lib/`, the compiler's `lib/`, the current directory's `lib/`), compiles the root and every module once with
`--separate`, and links the objects with `sutram-link`, the root's first. **A module two others `yoj` is
compiled once and defined once.**

**The proof** (`tests/r29/test_separate.py`, a gate): every program that `yoj`s a module and compiles the
ordinary way (253) prints the same bytes and exits with the same status when built separately; every
program in `examples/` with no `yoj` (144) is byte-identical; a wrong-arity call into another module is
refused with the ordinary compile's own diagnostic.

**Rebuilding only what changed (ROUND-31):** `tools/sutram_build.py --cache DIR main.sm -o out`. A module's
object is stored under a SHA-256 key of everything it depends on: the compiler's bytes, `SUTRAM_LANG`, the
module's path and bytes, and the path and bytes of every module it reaches through `yoj` (they are parsed in
its compile). An object whose key is in the cache is reused. Objects are reproducible, so a cached build is
**byte-identical** to a clean one (`tests/r31/test_incremental.py`, a gate: 254 programs, clean, cold and warm).

**Not yet:** a namespaced `yoj m@alias` (the builder refuses it); a module that calls back into the root sees no signature for it (the call is linked,
but its return type is assumed integer, as in `--object`).

## A module-level `vitti` in an object (ROUND-30)

**Each object holds the 8 bytes of every `vitti` declared in it,** after its code (where the one-pass compile
puts them), and exports each one as the symbol **`vitti:<name>`**, a name no prakriya can have. **No new kind of
hole is needed:** an access is `mov rax, [rip + disp32]` (or the store), whose displacement is the last four
bytes of the instruction, so it is filled with `target − (offset + 4)` like a call.

- **In `--separate`, a `vitti` that a `yoj` brought in is not held in the importing object.** Every access to it
  is a relocation to `vitti:<name>`, so the program has **one copy**, in its own module's object.
- **The program's root initializes every `vitti`,** its modules' too, at the start of `mukhya`, in source order,
  exactly as the one-pass compile does (the root sees every module's declarations).
- **So a library object compiled with plain `--object`** (no `mukhya`, no root) **refuses a `vitti` with an
  initializer**: nothing would run it. The diagnostic is `vastu-patre ghatak-star vitti asamarthita`. A `vitti`
  with no initializer is held (it starts at zero, as always).

## What version 1 does not do

- **No `--lang` flag** with `--object` (`SUTRAM_LANG` works).
- **Linux only.** The Windows executable has its runtime at the start of its image, so linking it needs more.
- **With `--object`, every prakriya is exported** (including the library modules a `yoj` pulled in), so two
  objects that both `yoj` the same module define its prakriyas twice. **`--separate` (ROUND-29) is the fix:**
  a `yoj`'d module's prakriyas are not in the object that `yoj`s it.
- **No C FFI, no archives, no package manager.** (No data relocation kind is needed for `vitti`: see above.)
