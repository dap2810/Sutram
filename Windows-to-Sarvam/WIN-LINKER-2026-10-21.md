# The Windows linker (R29-02's plan) — delivery from Windows

- **Commit tested:** `main` at **`4c325b51`** (v295's CHANGELOG, after the R34 merge `27768270`)
- **Compiler:** **`Sutram 1.0 (v243) - sampurna sutra`** (`sutram.exe` = `win\sutram.exe` `4533c46c…`; `sutram-link.exe` `b53dcbbd…`)
- **Crash corpus:** `crash corpus: 227 cases + manifest, 0 failed` (Linux, WSL)
- **Suite:** `NO-EXPECTATION=4  PASS=218` (Linux, WSL); Windows: 215 of 218 examples match, the 3 known Windows-specific (below)
- **Gates:** `tools/gates.sh` **28 PASS / 3 FAIL / 1 NOT-RUN** - **WSL Ubuntu on the owner's PC** (kernel
  6.6.87.2-microsoft-standard-WSL2, GNU ld 2.42, NASM 3.01 through a path wrapper), a clean LF clone of `4c325b51`.
  The 3 FAILs are `main`'s own: library proofs and R29 (both `r18_srij_overflow_guard`, below), X11 (no display).
- **Windows:** real Windows 11 Pro 10.0.26300, a standard user, **not elevated**, a fresh clone with Git for
  Windows' defaults (`core.autocrlf=true` + the repository's `.gitattributes`).

## The plan was already delivered - this is its measurement on `main`

R29-02's three steps were built in R34 and merged into `main` (`27768270`); v295 records them. This delivery
re-measures them on today's `main`, as the brief asks:

| R29-02 | Where it stands |
|---|---|
| 1. The same format; a Windows need makes it **a version 2, not a second format** | **`SUTRAMO2`** - version 1's layout, entry for entry. The three things in a PE program's code that depend on its place in the image are holes: `rt:init`, `rt:syscall`, `vitti:<name>` (whose symbol is an offset in the object's data). No new kind of entry. `docs/OBJECT-FORMAT.md` |
| 2. `--object`, then `--separate`, on the Windows compiler | both (no longer `%ifndef WINDOWS`; `--ffi` still is) |
| 3. `sutram-link` writes a PE: runtime, code, import table; in NASM | written field for field as the compiler's `write_pe`; one source, `sutram-link` (Linux) and `sutram-link.exe` (Windows); **either host links either target to the same bytes** |

## The guard

| | Windows | Linux |
|---|---|---|
| **Ordinary path**, v242 (`c062434f`) vs `main`'s v243, every `.sm` in `examples/`, `examples/*/`, `tests/stdlib/`, `tests/r*/` - the executable's bytes, the compiler's output, its exit status | **562 programs: 476 byte-identical, 86 refused identically, 0 DIFFER** | **562 programs: 476 byte-identical, 86 refused identically, 0 DIFFER** |
| **Every example linked alone = its direct compile** | **182 / 182 byte-identical** (`tests/r34/test_link_windows.py`) | 187 identical (`tests/r28/test_link.py`, the R28 gate) |

**The Windows equivalent of Linux's "470 byte-identical, 0 differ" is 476 byte-identical, 0 differ, over the
same 562 programs** - the two hosts now give the same split. (The first Windows run gave 475 / 87: from a CRLF
checkout one program crossed the expanded-source limit; `.gitattributes` gives every checkout LF sources now.)

`tests/r34/test_link_windows.py` on `main`: **1020 of 1021 checks PASS** - identity 182 / 182; two modules both
orders; 10 linker errors; 128 `vitti` link, 129 refused; 253 programs with modules behave the same built
separately; 145 without are byte-identical. **The 1 FAIL is `tests/stdlib/r18_srij_overflow_guard.sm`, and it
is not the linker:** that program prints heap addresses. Compiled once, directly, with no linker, the same
`.exe` printed **four different first lines in six runs** (`windows-r18-variance.txt`). The test runs the direct
build twice to set such programs aside; this time the two runs happened to agree. Its golden expects `0`; see
the open items.

`tests/r34/test_windows_fixes.py`: **4 / 4** (a PE program with more than 256 runtime calls - v242's compiler
crashed on it).

## The r17 check, on a Windows clone

**213 / 213 OK.** The 119 / 213 the brief names was the first run's checkout (`core.autocrlf=true` turned 94
files CRLF); R34's `.gitattributes` keeps `tests/negative/**` byte-exact on every checkout, so **a Windows user
who clones `main` now gets 213 / 213.** (`windows-examples-and-r17.txt`)

## The ABI

**The linker needed no ABI answer, so I did not wait for one or guess at one.** A Sutram program's own calls
and its calls into the runtime blob are Sutram's, not C's; `sutram-link` only places code and fills rel32
holes. **ChatGPT's ROUND-100-WS3 (`ChatGPT-to-Sarvam/ROUND-100-WS3-WINDOWS-X64-ABI.md`) has since landed** -
it is what the FFI on Windows needs.

## Not done, and why

- **The FFI on Windows** - a separate change, as the brief says. `--ffi` stays Linux-only; the sidecar's ABI
  is `linux-x86_64-sysv`. ROUND-100-WS3 is its input.
- **`sutram-elf2smo` on Windows** - it reads ELF; Windows foreign code would be COFF. Part of the FFI.
- **`SUTRAM_LANG` on Windows** - the Windows compiler reads no environment, so an `--object` for another
  pack is not possible there (`--object` takes no `--lang`). Not a linker change.
- **Three examples do not match on Windows**, unchanged from the first run and none the linker's:
  `245_r18_netsock` (the Windows runtime has no sockets: -38), `29_nishkriya` (exits through a raw Linux
  `syscall`), `79_ayojan_cwd` (compiled from outside the repository by `win\sutram.exe`, which has no `win\lib`
  in a checkout - the installer copies `lib` there, so installed users are not affected).
- **`r18_srij_overflow_guard`'s golden** expects `0` where Windows and WSL grant a 24 GB allocation - it is
  why library proofs and R29 FAIL here, on `main` and before R34 alike. A library decision (Muse / Sarvam).
- **Nothing in `Sarvam-to-Claude/` or `Claude-to-Sarvam/` was touched** by this delivery.

## Evidence

`Windows-to-Sarvam/win-linker-2026-10-21/`: `linux-gates.txt`, `linux-suite.txt`, `linux-crash-corpus.txt`,
`linux-ordinary-path.txt`, `windows-ordinary-path.txt`, `windows-test_link_windows.txt`,
`windows-test_windows_fixes.txt`, `windows-examples-and-r17.txt`, `windows-r18-variance.txt`. After
`gates.sh` rebuilt the compiler and linker from the clone's sources, `git status` showed only
`docs/sutram-stdlib.html` (regenerated by the stdlib-inventory gate): the committed binaries were reproduced.
