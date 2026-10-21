# The Sutram object file (`.smo`), version 1

**ROUND-28.** This file is written by `sutram_compiler --object in.sm out.smo`, read by `sutram-link`
(`linker/sutram_link.asm`), and printed for people by `tools/smo_dump.py`.
**ROUND-34:** the Windows compiler writes it too, as a `SUTRAMW1` object, and `sutram-link` (also built as
`sutram-link.exe`) links those into a Windows `.exe`. See *Windows* below.

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

## The FFI (ROUND-32): calling a C function

```
sutram_compiler --ffi decls.sffi --object   in.sm out.smo
sutram_compiler --ffi decls.sffi --separate in.sm out.smo [root.sm]
sutram-elf2smo  foreign.o foreign.smo
sutram-link     prog out.smo foreign.smo
python3 tools/sutram_build.py --ffi decls.sffi --foreign foreign.o main.sm -o prog   # all of it
```

**The declaration is a sidecar file, not syntax** (no parser change, no keyword, no pack):

```
sutram-ffi-v1|linux-x86_64-sysv
s_add|2|i64,i64|i64|sutram_ffi_add
```

One LF-terminated line per function: the name Sutram calls it by, its arity (0-6), the argument kinds, the
result kind, and the foreign symbol. ASCII, no spaces, no CR, at most 8192 bytes and 64 lines. Any other line is
refused with its line number.

**The kinds (ROUND-33):**

| Kind | As an argument | As the result |
|---|---|---|
| `i64` | an integer; a `dasham`, a string or a kosh is `E_FFI_KIND` (never truncated) | an integer |
| `f64` | a `dasham`, or an integer converted to `dasham`; a string or kosh is `E_FFI_KIND` | a `dasham` (from `xmm0`) |
| `ptr` | a string, a kosh (the address of its elements) or an integer; a `dasham` is `E_FFI_KIND` | an integer |
| `void` | — | none: the call is a statement; its value used anywhere is `E_FFI_KIND` |

Integer and pointer arguments go to `rdi, rsi, rdx, rcx, r8, r9` in order; `f64` arguments to `xmm0..xmm5` in
order (the System V rule: the two sequences are counted separately). A declared function may be called in an
expression or as a statement.

- **It is checked:** a call with the wrong number of arguments is `E_ARITY` at the call's own location, at the
  same point as for a prakriya (after parsing, before any code), so **no object is written**.
- **It is not a prakriya:** no body, no stub, nothing exported. A prakriya, builtin or keyword with either name
  is an error. A call becomes a relocation carrying the **foreign** name, with the stack aligned to 16 bytes
  around it for the C ABI (arguments in `rdi, rsi, rdx, rcx, r8, r9`, the result in `rax`, as Sutram's own calls).
- **It is opt-in:** `--ffi` is accepted only before `--object` or `--separate`. The ordinary compile never reads
  a sidecar.

**`sutram-elf2smo`** (`linker/sutram_elf2smo.asm`, NASM) reads one ELF64 x86-64 relocatable object and writes a
`SUTRAMO1` object with its code and one symbol per global function. **Stage 2 (ROUND-33)** reads what real C needs
for numbers and strings: exactly one code section; **read-only data** (a double constant, a string literal),
placed after the code at its alignment, at most 8; **PC-relative relocations in the code** (`R_X86_64_PC32`,
`R_X86_64_PLT32`) to the code or that data, resolved in the converter so nothing is left for the linker. It still
refuses: an undefined symbol (a C function that calls out), writable data, bss, unwind tables, a 16-byte constant,
any other relocation. Build the C side freestanding, for example
`gcc -c -O2 -ffreestanding -fno-asynchronous-unwind-tables -fno-pic -fno-stack-protector f.c`.
**`SUTRAMO1` and `sutram-link` are unchanged.**

## Windows (ROUND-34): `SUTRAMW1` and a PE

```
sutram.exe --object   in.sm out.smo                 # a SUTRAMW1 object
sutram.exe --separate in.sm out.smo [root.sm]
sutram-link.exe prog.exe a.smo [b.smo ...]          # a Windows .exe
python tools\sutram_build.py main.sm -o prog.exe    # all of it (Windows defaults: sutram.exe, sutram-link.exe)
```

**The same layout under the magic `"SUTRAMW1"`.** A Windows program's code is not self-contained: the PE the
compiler writes is `[headers][runtime blob][code]`, then a read/write `.data` section with the module-level
`vitti` (1024 bytes, 128 of them) and the kernel32 imports, and the code reaches the blob and `.data` by
rel32. In a `SUTRAMW1` object each of those is a hole, so **no new kind of entry is needed**:

| In the code | In a `SUTRAMW1` object |
|---|---|
| the call to the blob's `rt_init`, the first instruction of `mukhya` | a relocation to **`rt:init`** |
| every call into the blob's `rt_syscall` (each I/O, allocation and exit) | a relocation to **`rt:syscall`** |
| every access to a `vitti`, the object's own ones too | a relocation to **`vitti:<name>`** |
| a `vitti` the object holds | the symbol **`vitti:<name>`**, its offset **in this object's data** (8 bytes each, in order), not its code; no storage after the code |

**`sutram-link` decides the output from the magic.** All `SUTRAMO1`: the ELF, exactly as before. All
`SUTRAMW1`: a PE, written field for field as the compiler's `write_pe` writes it - the blob in front of the
code, so `rt:init` and `rt:syscall` are defined by the linker at the blob's two entries; each object's data
after the data of the objects before it, in `.data`, so a `vitti:` relocation is filled with
`.data − (site + 4)`. **Mixed objects are refused** (`vastu-patrani bhinna-lakshyani`), and so is more `vitti`
than `.data` holds (`ghatak-star vitti seema atikram`, as the compiler says it).

**Either host links either target.** The one source builds as a Linux program (raw syscalls) and, with
`-DWINDOWS`, as a Windows one (kernel32 through `win/winrt.inc`, the compiler's own layer):

```
nasm -f win64 -DWINDOWS=1 -I. linker/sutram_link.asm -o link.obj
ld -mi386pep --subsystem console --entry=_start --no-insert-timestamp -o sutram-link.exe link.obj
```

**The proof** (`tests/r34/test_link_windows.py`, run on Windows): every example the Windows compiler compiles
(182) is **byte-identical** through `--object` + `sutram-link.exe`; 253 programs with modules print and exit the
same built separately, and 145 without are byte-identical; two modules in both orders; ten linker errors; 128
`vitti` link, 129 are refused.

**Not on Windows yet:** the FFI (`--ffi`; its sidecar is `linux-x86_64-sysv`, and the Windows x64 calling
convention is a different one), `sutram-elf2smo`, and `SUTRAM_LANG` (the Windows compiler does not read the
environment; an object for another pack is not possible there yet).

## What version 1 does not do

- **No `--lang` flag** with `--object` (`SUTRAM_LANG` works).
- ~~**Linux only.**~~ **R34: Windows too** (above). The FFI is still Linux only.
- **With `--object`, every prakriya is exported** (including the library modules a `yoj` pulled in), so two
  objects that both `yoj` the same module define its prakriyas twice. **`--separate` (ROUND-29) is the fix:**
  a `yoj`'d module's prakriyas are not in the object that `yoj`s it.
- **No archives, no package manager;** the FFI (above) has no variadic, struct or callback functions, and foreign code may not call out. (No data relocation kind is needed for `vitti`: see above.)
