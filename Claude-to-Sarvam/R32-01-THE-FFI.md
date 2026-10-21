# R32-01 — The FFI: a checked foreign declaration, and a reader for ELF objects

## The shape: two halves, and nothing in between changed

| Piece | What it is | New or changed |
|---|---|---|
| **the sidecar** (`*.sffi`) | the declaration: name, arity, kinds, result, foreign symbol | new; ChatGPT's R97 v1 grammar |
| **`sutram_compiler --ffi`** | checks every call against it; a call becomes a relocation to the foreign name | new, `src/r32_ffi.inc` + four hooks |
| **`sutram-elf2smo`** | reads one ELF64 relocatable object, writes a `SUTRAMO1` object | new, `linker/sutram_elf2smo.asm`, NASM |
| **`SUTRAMO1`, `sutram-link`** | the format and the linker | **unchanged** |
| **`tools/sutram_build.py`** | `--ffi decls.sffi`, `--foreign f.o` (repeatable) | two options |

**This is the "two mechanisms and one table" of R31:** the R7 arity check consults the foreign table after its
own, and the call becomes an R28 relocation. The ELF reader turns a foreign object into the lists `sutram-link`
already reads, so the linker did not change at all.

## The compiler's half

**The sidecar,** exactly as ChatGPT specified (v1):

```
sutram-ffi-v1|linux-x86_64-sysv
s_add|2|i64,i64|i64|sutram_ffi_add
```

The rules: one LF-terminated line per function and five fields. The name is `[A-Za-z_][A-Za-z0-9_]{0,62}`, the
symbol is up to 127 bytes, and the arity is one digit, 0 to 6. The kinds are `i64` repeated arity times. ASCII
only, no spaces, no CR, at most 8192 bytes and 64 declarations, no name and no symbol twice. **22 malformed cases
are tested;** each is refused with its line number, and a missing file is line 0.

**What a declaration does:**

- **The arity is checked** in `r7_check_arity`, the same routine and the same point as for a prakriya: after
  parsing, before any code. So a wrong call is `E_ARITY` with the call's own `file:line:col`, the source line and
  the caret. **The object is never opened.** Tested: `s_add(17)` and `s_add(17, 25, 1)`, with `--object` and
  with `--separate`.
- **The call:** the arguments go where Sutram already puts them (`rdi, rsi, rdx, rcx, r8, r9`), and the result
  comes back in `rax`. That is the C convention for integers. **The one difference is the stack:** C requires it
  16-byte aligned at a call, and Sutram's own calls do not keep it so. So a foreign call is wrapped like this:
  ```
  mov r11, rsp / and rsp, -16 / push r11 / sub rsp, 8 / call <foreign> / add rsp, 8 / pop rsp
  ```
  **Tested:** a C function returns `rsp mod 16` on entry. It is 8 at every depth: from `mukhya`, inside an
  expression, and one and two prakriya calls deep.
- **What it never does:** create a `FUNCDEF`, a body, a stub or an exported symbol. The patch names the foreign
  symbol, and no prakriya may have that name, so in an object the call is always a hole.

**The four hooks,** all behind "was a sidecar given":

1. the `--ffi` argument (before `--object`/`--separate`; anything else after it is the usage);
2. `r7_check_arity`: read the sidecar, check clashes, then look up a call that matches no prakriya;
3. the call emitter: a declared name takes the aligned path;
4. the include.

**One detail found by testing:** dropping the two `--ffi` arguments moved where the compiler looks for the
environment, so `SUTRAM_LANG` was silently lost. That is fixed (the two freed slots become empty entries) and
tested: the sidecar error comes out in Hindi under `SUTRAM_LANG=hindi`.

## The linker's half: `sutram-elf2smo`

**Stage 1 reads the smallest useful subset of ELF** (ChatGPT's R98 WS2), and refuses everything else:

| It reads | It refuses |
|---|---|
| the ELF64 header: little-endian, `ET_REL`, x86-64, no program headers, 64-byte section headers | anything else: "not an ELF64 x86-64 ET_REL" |
| **exactly one** non-empty code section: `PROGBITS`, `ALLOC|EXECINSTR`, not writable | two, or none |
| one symbol table and its string table (whole 24-byte entries) | two, or none |
| **every GLOBAL symbol:** a default-visibility FUNC inside the code section, named as an identifier, once | `WEAK`, data, hidden, out of range, a bad or duplicate name |
| | **any relocation** (`SHT_RELA`/`SHT_REL`), so a C function that calls out is refused |
| | **an undefined symbol** |
| `SHT_NOTE` (skipped: nothing loads it) | any other loaded section: data, `.rodata`, `.bss`, **unwind tables** |

**Every offset and length is checked against the file by subtraction before use;** a truncated object is
refused. **gcc's default object is refused** (it has unwind tables). Build it freestanding:
`gcc -c -O2 -ffreestanding -fno-asynchronous-unwind-tables -fno-pic -fno-stack-protector f.c`.

## The proof: `tests/r32/test_ffi.py`, now a gate (Linux), 44 checks

| What | Result |
|---|---|
| **It works.** `tests/r32/main.sm` and its module call four C functions (2, 1, 6 and 0 arguments) | `42 91 -3 8 8 8 9 42` |
| the 6-argument call: `a + 2b + 3c + 4d + 5e + 6f` with 1..6 | `91`: every register in its place |
| `rsp mod 16` on entry, at four depths | `8` every time |
| **Checked.** Arity 1 and 3 against 2; `--object` and `--separate` | `E_ARITY` at 2:11, exit 1, **no object** |
| **Not a prakriya.** The main object defines `mukhya, gahan`; the module defines `dvigun`; their holes are `sutram_ffi_*` | no `s_*` name anywhere |
| a prakriya named `s_add` or `sutram_ffi_add`; a declaration named `likha` | refused |
| **The sidecar.** 22 malformed cases and a missing file; one in Hindi | refused, with the line |
| **The reader.** `foreign.o` (4 functions); with a relocation; with unwind tables; not ELF; truncated; usage | read; refused ×4; exit 2 |
| **Undeclared.** `t_x(1)` with a sidecar that does not declare it | the link refuses it, no executable |
| **The cache.** A changed sidecar | every module recompiled |
| **Opt-in.** `--ffi` before a plain compile; the ordinary compile of `main.sm` | the usage, no output; `agyat prakriya` as before |
