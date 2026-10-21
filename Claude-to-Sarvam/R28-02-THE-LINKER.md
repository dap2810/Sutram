# R28-02 — WS2: our linker, `sutram-link`, in NASM

**`linker/sutram_link.asm`, about 500 lines, the way the compiler is written:** Linux x86-64, raw system calls,
no libc and no other language. It builds with the same `nasm` + `ld` step as the compiler and the IDEs
(`tools/gates.sh`, "build: linker"), and `sutram-link` is committed at 100755.

```
sutram-link out.bin a.smo [b.smo ...]
```

## What it does

1. **Reads each object and checks it.** The magic must be there, and every table must fit inside the file.
   A truncated file is a bad object.
2. **Exactly one object must define `mukhya`.** That one goes first, so `mukhya` is the entry point; the
   others follow in the order given.
3. **Lays the code end to end and collects every symbol.** A name defined twice is an error.
4. **Fills every hole from the symbols.** A name nobody defines is an error.
5. **Writes the same executable the compiler writes for an ordinary program:** the same header, one
   `PT_LOAD` at `0x400000 + 120`, RWX, and 64 KiB of zeroed memory after the code.

**Errors** (exit 1, on stdout like the compiler's): `agyat prakriya` (the compiler's own wording),
`prakriya dvih paribhashita` (defined twice, including two `mukhya`s), `kasminnapi vastu-patre mukhya
nasti` (no mukhya), `vastu-patram na` (not an object, or truncated), `patram na udghatitam` (cannot open).
A usage error exits 2.

## The proof

`tests/r28/test_link.py`, now a gate, makes **199 checks, 0 failed.** Environment: **Linux**.

| What | Result |
|---|---|
| **Identity.** Every program in `examples/` that compiles directly is also compiled with `--object` and linked alone; **the executable must be byte-identical to the direct compile** | **186 of 186 identical.** 1 refused (it has a module-level `vitti`), 35 are compile-fail examples |
| **Two modules.** A library object and a main object, with calls in **both** directions (the library calls back into the main object), linked in **both** argument orders | prints `126`, `50` both ways |
| **The errors:** undefined, duplicate, no `mukhya`, two `mukhya`s, not an object, a truncated object, a missing file, usage | all 8 |
| a module-level `vitti` in `--object` mode | refused, with its diagnostic |

**The identity check is the strongest evidence I have that the format loses nothing.** For 186 real
programs, the separate path writes exactly the bytes the one-pass path writes.

## The guard: the existing path did not change

**This is the check you said matters most.** I compiled **543 programs** (`examples/`, `examples/*/`,
`tests/stdlib/`, `tests/r*/`) with **main's committed compiler (v237)** and with **this one (v238)**, both
through the ordinary path, without `--object`:

| Environment | Result |
|---|---|
| **Linux** | **466 byte-identical executables, 77 refused identically** (the same diagnostic, byte for byte), **0 differ** |
| **Wine** (not Windows): every example, main's `win/sutram.exe` vs this one | **140 of 141 identical**, twice. The one that differed in the second run was identical in three targeted reruns, so it is a flake in the Wine loop, reported as seen (`evidence-r28/ordinary-path-windows.txt`) |

**This guard found a real problem, and I fixed it.** My first Windows comparison was **0 of 31 identical.**

- **The cause:** the compiler's PE import template uses absolute `align 2`. Adding one pack message (data
  that sits before the template) moved the template, and that shifted every Windows program's import table
  by a byte. The programs still worked, but they were not the same bytes.
- **The same shift may have happened at earlier rounds that added messages** (R23, R25, R26). I did not
  check, because nobody compared Windows outputs byte for byte then.
- **The fix:** the template is now pinned to a 16-byte boundary plus one byte, which is the position v237
  had. The output bytes are v237's again, and future message additions cannot move them.
- **I would make the Windows byte comparison a standing check,** but it needs Wine and takes minutes, so it
  is in the evidence, not in `gates.sh`.

The suite, the corpus and the fuzzers were also run before and after: see R28-00.

## What it does not do

- **Linux only.** A Windows linker needs the PE runtime blob placed first; that is a further step.
- **The linker's messages are romanised Sanskrit only.** It does not read the eleven packs yet (the
  compiler and the IDE do).
- **No module-level `vitti`, no data relocations, no archives, no C FFI, no package manager,** as you scoped it.
- **Every prakriya is exported.** So two objects that both `yoj` the same library module define it twice;
  `yoj` it in one object only.
- **No `--lang` with `--object`** (`SUTRAM_LANG` works).
