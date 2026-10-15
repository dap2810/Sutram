# Sutram (सूत्रम्)

**A programming language whose keywords are Sanskrit, whose compiler is one
hand-written NASM file, and whose output is native machine code with no
runtime, no interpreter, and no toolchain for the person using it.**

```
mukhya() {
    likha("Namaste, jagat")
}
```

```
sutram hello.sm hello.bin
./hello.bin
```

`sutram` is a compiler, not a wrapper. It reads `.sm` source and writes a
native executable directly — a flat ELF on Linux, a PE32+ image on Windows.
There is no C backend, no Python, no LLVM, and no runtime library. The
compiler itself is a single assembly source file.

## Why it exists

Every widely used language asks an Indian programmer to think in English
keywords. Sutram does not. The keyword set is Sanskrit — the source language
of most Indian technical vocabulary — and additional Indian languages are
supported through **language packs**, so you can write in Tamil, Bengali,
Telugu or Gujarati using that language's own technical words.

The name means *thread* — one thread running through many languages.

## The keywords

| Sanskrit | Meaning | Sanskrit | Meaning |
|---|---|---|---|
| `mukhya` | main | `yadi` | if |
| `vitti` | variable | `anyatra` | else |
| `anka` | integer | `yavat` | while |
| `sutra` | constant | `punaravartana` | for |
| `prakriya` | function | `pratiyati` | return |
| `likha` | print | `krama` | break |
| `kosh` | growable array | `uddeshya` | continue |
| `dasham` | float | `rachana` | struct |
| `pankti` | array | `srijana` | enum |
| `guna` | switch | `ayojan` | include |

Semicolons and braces are optional. The full reference is in
**docs/LANGUAGE-REFERENCE.md**.

## What is in this release

- **202 example programs** in `examples/` — 191 numbered plus 11 from recent
  rounds — with regression expectations in the test corpus. Cases without an
  accepted expectation are not counted as passing tests
- **21 standard-library modules with code** in `lib/`, 278 functions between
  them — mathematics, sorting, strings, statistics, calculus, matrix work, and
  heritage modules built on classical Indian mathematics. Three further files
  (`array`, `io`, `net`) are comment-only design sketches, not working modules
- **11 language packs** in `lang/` — Sanskrit, Hindi, Bengali, Gujarati, Kannada,
  Malayalam, Marathi, Odia, Punjabi, Tamil, Telugu
- **Six book editions** at `docs/sutram-book-*.html` — English, Hindi, Sanskrit, Tamil, Telugu,
  Gujarati
- **A GUI IDE** for Windows and a terminal IDE plus a native X11 GUI for Linux

## Running it

### Windows

Sutram runs natively — no WSL, no Python, no C runtime. `sutram.exe` is a
Win64 program, and compiled programs are real Windows executables (PE32+).

    sutram.exe examples\01_hello.sm hello.exe
    hello.exe

For an independently accepted Windows package, use its per-user wizard or
run the portable compiler directly. Do not use a legacy installer to work
around a blocked build. See **docs/INSTALLATION-ROUTES.md** for the source
layout, privilege contract, and remaining release blockers.
The output name picks the target: `.exe` -> Windows, `.bin` -> Linux.

Full guide: **docs/WINDOWS-SETUP.md** (install, usage, troubleshooting,
Linux-vs-Windows differences, feature status).

### Linux

    ./sutram_compiler examples/01_hello.sm hello.bin
    ./hello.bin

This source checkout does not contain a root `install.sh`. Build below and
run the compiler directly; do not assume a packaged installer is present.
The IDE sources are in `ide/`. See **docs/INSTALLATION-ROUTES.md**.

## Writing in your own language

    sutram --lang tamil program.sm program.bin

or set `SUTRAM_LANG=tamil`. A language pack is a plain text file mapping a
native word to its Sanskrit keyword, so anyone can add or correct one:

    <native word> <sanskrit keyword>

## Building the compiler from source

Only NASM and a linker are needed — nothing else.

    nasm -f elf64 -I. src/sutram_compiler.asm -o sutram.o
    ld -o sutram_compiler sutram.o

Windows target:

    nasm -f win64 -dWINDOWS -I. src/sutram_compiler.asm -o sutram.obj
    ld -mi386pep --entry=_start -o sutram.exe sutram.obj

## Where things are

| Path | What |
|---|---|
| `src/sutram_compiler.asm` | primary pure-NASM compiler source; keep its reviewed `.inc` files alongside it |
| `lib/` | standard library (`.smlib`) |
| `lang/` | language packs |
| `examples/` | example programs; consult the regression corpus for accepted expectations |
| `tests/` | regression suite and golden files |
| `tools/` | benchmarks, codegen gates, verification |
| `docs/` | reference, guides, generated HTML — incl. **`sutram-design-parameters.html`** (the 20 design requirements with honest status) and **`sutram-project-status.html`** (measured project state) |
| `docs/sutram-book-*.html` | the six language editions |
| `windows/` | Windows GUI, installer, build scripts |
| `ide/` | terminal IDE and Linux X11 GUI |
| `ROADMAP.md` | what is done, what is planned, what is not attempted |

## Honest status

The clean-project handoff reports a Linux baseline of **187 passing cases,
4 no-expectation cases, and 12/12 code-generation shape gates**. These are
maintainer-reported baseline measurements, not a Windows release certificate.
A clean-source audit must rerun them independently; a percentage-complete
estimate is not a substitute for those gates.

Known limits, stated plainly rather than buried:

- **No separate compilation.** `ayojan` expands modules textually within one
  translation unit. Transitive imports are resolved once, but there are no
  `.smo` object files yet.
- **No concurrency** in the language itself.
- **No first-class functions.**
- **The Windows GUI has never been run on real Windows** by the person who
  wrote it. It assembles and links correctly and passes its static tests; a
  human still has to confirm it on screen.
- **The Linux X11 GUI** speaks the X protocol correctly (verified against a
  mock server) but has not been rendered on a real display.

`ROADMAP.md` records what is deliberately out of scope, including
operating-system capability and the six specific blockers in the way.

## Licence

See `LICENSE.txt`.
