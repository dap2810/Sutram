# Sutram (सूत्रम्) — project overview

**Read this first.** It explains what the project is, what is fixed, what
exists, what is proven, and what is not. Everything else in this archive is
source, tests, documentation or build output.

---

## 1. What this is

Sutram is a programming language whose **keywords are Sanskrit**. Its compiler
is **one hand-written NASM assembly source file** that emits **native machine
code** directly. There is no C backend, no Python, no LLVM, no interpreter and
no runtime library. The person using the language needs no toolchain at all —
the installer ships a prebuilt binary.

The name means *thread* — one thread running through many languages.

```
mukhya() {
    likha("Namaste, jagat")
}
```

```
sutram hello.sm hello.bin
./hello.bin
```

Output target is chosen by the output filename: `.exe` produces a Windows
PE32+ image, anything else produces a Linux ELF.

## 2. The fundamentals — these do not change

Any contribution must preserve all six:

1. **Sanskrit keyword core.** Latin transliteration is primary; Devanagari and
   the other Indian scripts are supported through language packs.
2. **`.sm` file extension.**
3. **One hand-written pure-NASM compiler source.** No C, no Python, no
   generated code, no second implementation.
4. **Native machine code output.** Never interpreted.
5. **No runtime dependency.** A compiled program is self-contained.
6. **End users need no toolchain.** Prebuilt binaries ship in the installer.

Two more standing rules: **lowest practical permission level** (no admin, no
UAC elevation, no HKLM, no services, no disabling of OS security), and
**measured performance** — never assume a speed-up, measure it.

## 3. Repository layout

| Path | What |
|---|---|
| `src/sutram_compiler.asm` | **the entire compiler**, one file, ~15k lines |
| `lib/` | standard library — 12 modules with code, 103 functions (`.smlib`) |
| `lang/` | 10 language packs, one per Indian language |
| `examples/` | 178 programs, each with expected output and exit code |
| `tests/` | regression suite, golden files, per-host expectations |
| `tools/` | benchmarks, codegen gates, protocol tests, verification helpers |
| `docs/` | reference, guides, and generated HTML pages |
| `books/` | six complete book editions (English, Hindi, Sanskrit, Tamil, Telugu, Gujarati) |
| `windows/` | Windows GUI IDE source, installer, PowerShell install scripts |
| `ide/` | terminal IDE and the Linux X11 GUI |
| `benchmarks/` | performance corpora |
| `compiler/` | design notes and per-round change records |
| `ROADMAP.md` | what is done, planned, exploratory, and explicitly not attempted |

## 4. Building

Only NASM and a linker are required. Nothing else.

**Linux compiler**
```
nasm -f elf64 src/sutram_compiler.asm -o sutram.o
ld -o sutram_compiler sutram.o
```

**Windows compiler**
```
nasm -f win64 -dWINDOWS -I. src/sutram_compiler.asm -o sutram.obj
ld -mi386pep --entry=_start -o win/sutram.exe sutram.obj
```

**Terminal IDE** — `nasm -f elf64 ide/sutram_ide.asm -o ide.o && ld -o sutram-ide ide.o`

**Linux X11 GUI** — `nasm -f elf64 ide/sutram_gui_linux.asm -o g.o && ld -o sutram-gui g.o`

**Windows GUI** — `nasm -f win64 windows/gui/sutram_gui.asm -o g.obj && ld -mi386pep --subsystem windows --entry=_start -o sutram-ide-gui.exe g.obj`

**Windows installer** — needs `payload.zip`, `install-core.ps1` and
`uninstall-core.ps1` in the working directory (they are pulled in with
`incbin`): `nasm -f win64 windows/native-installer/sutram_setup.asm -o s.obj && ld -mi386pep --subsystem windows --entry=_start -o Sutram-Setup.exe s.obj`

## 5. Running the tests

```
python3 tests/run_tests.py          # 178/178 expected
python3 tools/codegen_gate.py       # 12/12 expected
python3 tools/test_lang_packs.py    # 30/30 expected
python3 tools/test_ide_undo.py      # 12/12 expected
python3 tools/test_x11_protocol.py  # 31 checks, no display needed
python3 tools/check_setup_abi.py    # static Win64 ABI audit of the installer
```

## 6. The language in brief

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
| `kuru` | do-while | `nishkriya` | inline assembly |
| `parigrah` | boolean | `grahan` | read input |

Semicolons and braces are optional. Full reference: `docs/LANGUAGE-REFERENCE.md`.

A language pack maps a native word to its Sanskrit keyword, one per line:
```
<native word> <sanskrit keyword>
```
Loaded with `sutram --lang tamil` or `SUTRAM_LANG=tamil`.

## 7. Current state

| | |
|---|---|
| Compiler SHA-256 | `c814a854607f395a63bd7b46ff1c74ec959e7287d19c964d3e0d41d1a10b073c` |
| Regression suite | **178/178** |
| Code-generation gates | **12/12** |
| Language packs | **30/30** |
| Examples | 178 |
| Library modules | 12 with code (103 functions); 3 more are comment-only sketches |
| Books | 6 editions, kept in step with the language |

## 8. What is proven, and what is not

This distinction matters more than any feature list.

**Proven by execution.** The compiler builds on both Linux and Windows targets
and passes 178 regression tests. Emitted code is byte-identical across the
performance benchmarks. The language packs each compile and run a real
program. The terminal IDE's undo log works. The X11 client's protocol bytes are
verified against a mock X server. The Windows installer's stack frames are
statically audited and its payload is embedded byte-for-byte.

**Not proven.** Nobody has run the **Windows GUI** on real Windows. Nobody has
**rendered the Linux X11 GUI** on a real display — the protocol is verified, the
picture is not. The **Windows installer has never been executed on Windows**.
Performance figures are directional (minimum of repeated runs), not
microbenchmark-grade.

**Not implemented.** No separate compilation — `ayojan` expands modules
textually within one translation unit; transitive imports resolve once, but
there are no `.smo` object files. No concurrency. No first-class functions. No
collections beyond `kosh` and `pankti`.

## 9. How this project was built

Two AI assistants worked in parallel with a human owner as integrator, handing
work back and forth through a shared folder. One side wrote features; the other
verified them independently — rebuilding, running the suite, testing claims
rather than trusting reports — and kept the books and docs current.

The verification discipline is the part worth preserving:

- Never report intent as completion. An artifact is finished when it has been
  built, run, and read back.
- Never state a hypothesis as a finding.
- Check the check. A test that asserts the bug is worse than no test. (One
  here asserted a wrong request length for weeks.)
- When something cannot be verified in this environment, say so plainly
  instead of implying it works.

## 10. Licence

See `LICENSE.txt`.
