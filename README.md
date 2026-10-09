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
of most Indian technical vocabulary — and every other Indian language is
supported through a **language pack**, so you can write in Tamil, Bengali,
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

- **178 worked examples** in `examples/`, each with expected output and exit code
- **12 standard-library modules with code** in `lib/`, 103 functions between
  them — mathematics, sorting, strings, statistics, calculus, matrix work, and
  heritage modules built on classical Indian mathematics. Three further files
  (`array`, `io`, `net`) are comment-only design sketches, not working modules
- **10 language packs** in `lang/` — Hindi, Bengali, Gujarati, Kannada,
  Malayalam, Marathi, Odia, Punjabi, Tamil, Telugu
- **Six book editions** in `books/` — English, Hindi, Sanskrit, Tamil, Telugu,
  Gujarati
- **A GUI IDE** for Windows and a terminal IDE plus a native X11 GUI for Linux

## Running it

### Windows

Sutram runs natively — no WSL, no Python, no C runtime. `sutram.exe` is a
Win64 program, and compiled programs are real Windows executables (PE32+).

    sutram.exe examples\01_hello.sm hello.exe
    hello.exe

Install with the wizard (`Sutram-Setup.exe`), or unzip the portable folder and
run `sutram.exe` from it, or run `install.bat` to add it to PATH.
The output name picks the target: `.exe` -> Windows, `.bin` -> Linux.

Full guide: **docs/WINDOWS-SETUP.md** (install, usage, troubleshooting,
Linux-vs-Windows differences, feature status).

### Linux

    ./sutram_compiler examples/01_hello.sm hello.bin
    ./hello.bin

`install.sh` installs it for the current user. `sutram-ide` is a terminal IDE
with syntax highlighting, and Ctrl-R to run.

## Writing in your own language

    sutram --lang tamil program.sm program.bin

or set `SUTRAM_LANG=tamil`. A language pack is a plain text file mapping a
native word to its Sanskrit keyword, so anyone can add or correct one:

    <native word> <sanskrit keyword>

## Building the compiler from source

Only NASM and a linker are needed — nothing else.

    nasm -f elf64 src/sutram_compiler.asm -o sutram.o
    ld -o sutram_compiler sutram.o

Windows target:

    nasm -f win64 -dWINDOWS -I. src/sutram_compiler.asm -o sutram.obj
    ld -mi386pep --entry=_start -o sutram.exe sutram.obj

## Where things are

| Path | What |
|---|---|
| `src/sutram_compiler.asm` | the entire compiler, one file |
| `lib/` | standard library (`.smlib`) |
| `lang/` | language packs |
| `examples/` | 178 programs with expected output |
| `tests/` | regression suite and golden files |
| `tools/` | benchmarks, codegen gates, verification |
| `docs/` | reference, guides, generated HTML |
| `books/` | the six book editions |
| `windows/` | Windows GUI, installer, build scripts |
| `ide/` | terminal IDE and Linux X11 GUI |
| `ROADMAP.md` | what is done, what is planned, what is not attempted |

## Honest status

Sutram is roughly **85% of the way to a solid compiler** and around **50% of
the way to a practical general-purpose language**. The current suite is
178/178 with 12/12 code-generation shape gates.

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
