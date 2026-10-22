# R34-00 — Hand-back to Sarvam: the Windows linker

> **Read `R34-01-FIXES.md` with this.** Since this was written: the object's magic is **`SUTRAMO2`**,
> version 2 of the same format, as the linker plan (R29-02) asked (it was `SUTRAMO2`; the name is updated
> below, the layout never changed); findings 1, 3 and 4 below are **fixed**; a compiler crash and five IDE
> defects - one of them data loss - are fixed; `gates.sh` is now 28 PASS / 3 FAIL / 1 NOT-RUN. The numbers
> in the table are re-measured on the final build in `evidence-r34/`.

**Asked by the owner on 2026-10-21, on his real Windows PC: "make the linker for Windows, that is the priority,
and test it here."** It is built and tested there. **On a review branch, `claude/windows-linker`, not on
`main`:** accept it or not.

- **Compiler: `Sutram 1.0 (v243) - sampurna sutra`.** The Windows compiler now has `--object` and `--separate`.
- **`sutram-link.exe` is new:** the same linker source, built for Windows. It writes a Windows `.exe`.
- **The ordinary path did not move: 562 programs, v242 vs v243, 0 differ, on Windows and on Linux.**

## What it does

```
sutram.exe --object main.sm main.smo               # a SUTRAMO2 object
sutram.exe --object lib.sm  lib.smo
sutram-link.exe prog.exe main.smo lib.smo          # a Windows .exe
python tools\sutram_build.py main.sm -o prog.exe   # every module compiled once, then linked
```

**Why the Windows side needed more than the Linux one.** A Linux program's code stands alone. A Windows
program's does not: the compiler writes `[headers][runtime blob][code]` and a read/write `.data` section with the
`vitti` and the kernel32 imports, and the code reaches the blob and `.data` by fixed distances. Those three
things - the call to `rt_init`, every call into `rt_syscall`, every `vitti` access - **become holes in a
`SUTRAMO2` object**, named `rt:init`, `rt:syscall` and `vitti:<name>`. **So the format needs no new kind of
entry:** it is `SUTRAMO1`'s layout, version 2. A `vitti:` symbol in a `SUTRAMO2` object is an offset in
the object's data, not its code.

**`sutram-link` chooses the output from the magic.** `SUTRAMO1` gives the ELF, exactly as before; `SUTRAMO2` a
PE written **field for field as the compiler's `write_pe`**. Mixing them is refused, and so is more `vitti`
than `.data` holds (128). **One source, two hosts:** `linker/sutram_link.asm` builds as a Linux program and, with
`-DWINDOWS`, as a Windows one, through the compiler's own `win/winrt.inc`. **Either host links either target,
to the same bytes.**

## What I ran, on what

**Real Windows 11 Pro 10.0.26300, AMD Ryzen 7 7700X, a standard user, not elevated.** Linux in WSL (Ubuntu,
GNU ld 2.42). NASM 3.01.

| Check | Result |
|---|---|
| `tests/r34/test_link_windows.py` (new, a Windows gate) | **PASS — 1018 checks, 0 failed** |
| — every example the Windows compiler compiles, through `--object` + `sutram-link.exe` | **182 / 182 byte-identical** to the direct compile |
| — programs with modules, built separately (`sutram_build.py`) | **252 print and exit the same**; 145 without modules byte-identical; 10 namespaced, refused as on Linux |
| — two modules both orders; 10 linker errors; 128 `vitti` link, 129 refused; `vitti` in `.data`, shared, one copy | PASS |
| **The ordinary path, Windows** (562 programs, v242 vs v243) | **0 differ** (475 identical, 87 refused identically) |
| **The ordinary path, Linux** (562 programs, v242 vs v243, LF clone) | **0 differ** (476 identical, 86 refused identically) |
| Cross-host: 182 `SUTRAMO2` objects, Linux linker vs Windows linker | **182 / 182 identical PEs** |
| Cross-host: 185 `SUTRAMO1` objects, Windows linker vs Linux linker | **182 identical ELFs; 3 refused by both alike** |
| The committed binaries rebuilt from the committed sources | **4 / 4 byte-identical**; `r69_build.py --check-only`: `SOURCE_PINS_CHECKED` |
| `tools/gates.sh`, Linux, branch **and** main side by side | **the same 3 FAILs on both**; branch 28 PASS (the new R34 gate), main 27 |

**The three gate FAILs are the same on `main`, so they are not this round's** (evidence: `gates-linux.txt`):

- **library proofs** and **R29 separate compilation** — both are `tests/stdlib/r18_srij_overflow_guard.sm`:
  `suchi_srij(3037000499)` is meant to return 0, and **under WSL it returns a real address** (`127406310879232`).
  **On real Windows it does too** (`4456448`, different each run). The guard relies on the allocation
  failing, and on these two systems it does not fail. **A real defect, on two of the three systems the
  project now runs on.**
- **X11 GUI protocol** — no X display in WSL.

## Findings, not fixed here

1. **[FIXED in R34-01: committed, `tests/r32/OBJECTS.md`]** **The FFI tests' `.o` files were never committed.** `tests/r32/test_ffi.py` says *"the .o files are
   committed"*; `.gitignore` has `*.o`, so they never were. **On a fresh clone R32, R33, the FFI fuzzer and the
   ELF-reader fuzzer all fail.** I built them with gcc for the gate runs, on both trees, and did not commit them.
   Either commit them with `git add -f` or build them in the tests.
2. **The overflow guard** above.
3. **[FIXED in R34-01: `.gitattributes`]** **`tools/r69_build.py --check-only` refuses on a CRLF checkout** (Git for Windows' default
   `core.autocrlf=true`). It hashes the raw bytes. Pins are right on an LF clone.
4. **[FIXED in R34-01: `.gitattributes`]** **From CRLF sources, the Linux compiler refuses `tests/stdlib/r11_sets_lists.sm`** (`vistarit srot seema
   atikram`): the CR bytes push it over the expanded-source limit. v242 does the same.
5. **The Windows compiler does not read the environment,** so `SUTRAM_LANG` does nothing there, and an
   `--object` for another pack is not possible on Windows yet (`--object` takes no `--lang`).

## Not done

- **The FFI on Windows.** The sidecar is `linux-x86_64-sysv`; Windows x64 passes arguments differently.
  `--ffi` stays Linux-only.
- **The installer** is not rebuilt. Its payload list now includes `sutram-link.exe` (R34-01), so the next
  rebuild carries it.

## Files

- `linker/sutram_link.asm` — the PE writer, the two targets, the Windows host layer
- `src/r28_object.inc`, `src/sutram_compiler.asm` — `SUTRAMO2`; `--object`/`--separate` on Windows; v243
- `sutram.exe`, `win/sutram.exe`, **`sutram-link.exe` (new)**, `sutram_compiler`, `sutram-link`
- `tests/r34/test_link_windows.py` — the Windows gate
- `tools/sutram_build.py` (Windows defaults), `tools/smo_dump.py` (reads `SUTRAMO2`)
- `docs/OBJECT-FORMAT.md` (the Windows section), `docs/BUILDING.md` (the linker's build); pins moved
- `Claude-to-Sarvam/evidence-r34/` — every number above
