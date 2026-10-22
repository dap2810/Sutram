# R34-01 — What the real Windows run found, and what is fixed

**The owner asked, on his Windows 11 PC: "fix the project where it requires, but do not change the
fundamentals or the philosophy; run the GUI on Windows, run every sample file one by one, and correct
the project accordingly; check the Windows linker plan."** Every item below was found by running
something on real Windows 11 (or WSL), fixed, and run again. **No fundamental moved:** the compiler is
still one pure-NASM source, no runtime, no new dependency; an ordinary program still compiles to the
same bytes (562 programs, 0 differ, Windows and Linux).

## 1. The Windows linker plan (`R29-02-WINDOWS-LINKER-PLAN.md`), checked point by point

| The plan | Done | |
|---|---|---|
| The real Windows baseline first, in `Windows-to-Sarvam\` | `WIN-RUN-2026-10-21.md` on main, before the linker | yes |
| **The same format; if Windows needs more, "a version 2, not a second format"** | **Now `SUTRAMO2`, version 2** - it was `SUTRAMW1`, which read as a second format. Same layout | **fixed** |
| `--object`, then `--separate`, on the Windows compiler | both | yes |
| `sutram-link` writes a PE: runtime, code, import table; in NASM | field for field as the compiler's `write_pe` | yes |
| Every ordinary Windows output byte-identical | 562 programs, 0 differ | yes |
| Every example linked alone byte-identical | 182 / 182 | yes |
| "Wine first, then the owner confirms on real Windows" | real Windows directly; **Wine not run** | more than asked |
| Stop if the ordinary path would have to change | it did not | yes |
| The FFI is not in the plan | `--ffi` stays Linux-only | yes |

## 2. Fixed

| # | Found | Fix | Proof |
|---|---|---|---|
| 1 | **The compiler crashed** on a Windows program with more than 256 calls into its runtime (a 200-`likha` program: exit 139 and a broken `.exe`; main's v242 too). `blob_calls` had 256 entries and no bound check | Sized to the code buffer (`CODE_BUF_CAP / 5 + 1`: every such call is 5 code bytes, so it cannot fill) and bounded anyway | `tests/r34/test_windows_fixes.py` (new, **a gate**; on Linux through the cross PE): 100/200/250 `likha` compile and print every line; v242 fails it (`0xC0000005`) |
| 2 | **In the IDE an input program spun until the 10 s limit, and the IDE stopped answering** (the run had no stdin handle, so every read failed) | A run's stdin is the `NUL` device - end of input, exactly `prog < NUL` | the 6 input examples now finish at once (`Input ended. Goodbye!`); 0 hangs |
| 3 | **In the IDE a program that `yoj`s its own module never compiled** (`E_MODULE_MISSING`): the IDE compiles a copy in `%TEMP%`, and the compiler looks for modules beside the source | An opened or saved file with **no unsaved change** is compiled where it is. Unsaved text still uses the temp copy; the shell is unchanged | 15 examples that failed now match |
| 4 | **The IDE's status line showed `???????`** in every pack (Sanskrit, Hindi, Gujarati, Tamil ...) | The status line and the find label are Unicode windows (`CreateWindowExW`); an ANSI `STATIC` turned every Indic letter into `?` | 14 `?` status lines -> 0; `evidence-r34/ide/after-status-line-devanagari.png` |
| 4a | **The IDE could overwrite a file with another file's text (data loss).** Open an example, then open one the editor refuses (over 65534 bytes): the IDE kept the old text but now named the refused file - and **File > Save wrote the old text over it**. Reproduced on a throwaway copy: a 70,686-byte program became **67 bytes** | A refused load (example list, File > Open, or the file given on the command line) puts the previous name back; the command-line case leaves the editor untitled | the same steps on the fixed IDE: the file is untouched (`tools/ide_examples_windows.ps1`, its first guard) |
| 4b | **Loading an example dropped unsaved work without asking** (File > New and File > Open asked; the example list and *Load example* did not) | `load_example` asks first, like the others | the second guard: the question is shown, and Cancel keeps the text |
| 5 | `tools/accept-windows.ps1` **did not run as documented** on Windows PowerShell 5.1 | `$PSScriptRoot` is empty in a `[CmdletBinding()]` script's `param()` defaults on 5.1; the default is set in the body | reproduced with a 3-line script, and the fix shown, on 5.1.26100 |
| 6 | **The FFI tests' C objects were never committed** (`.gitignore` `*.o`); R32, R33, the FFI fuzzer and the ELF-reader fuzzer failed on every fresh clone | Committed, with a `.gitignore` exception; `tests/r32/OBJECTS.md` says how they were built (gcc 13.3.0, the documented flags) | the four gates PASS on a clean clone with no C compiler |
| 7 | **Git for Windows' CRLF checkout** broke 94 of 213 r17 hashes, `r69_build.py --check-only`, and one Linux compile | `.gitattributes`: sources always LF, test data byte-exact. No file's content changes | a fresh default Windows clone: **213 / 213**, `SOURCE_PINS_CHECKED` |
| 8 | Two GUI source tests failed on Windows (read files as cp1252) | `read_text(encoding='utf-8')` | both OK on Windows |
| 9 | The installer would not carry `sutram-link.exe` | added to the payload (`bin\`); the uninstaller removes it by the manifest | **rebuilt in R34-02**; acceptance checks the installed linker |
| 10 | `gates.sh` said Windows was "never executed by anyone" | it has been; the line says where the Windows gates are | - |

## 3. Every example through the real IDE (`tools/ide_examples_windows.ps1`, new)

The script opens the IDE, and for each of the 218 examples with a golden **double-clicks it in the
example list, chooses its language from the menu, presses Run**, and reads the output pane and the status
line - what a user does. On Windows 11, same compiler:

| IDE | match | differ | not opened | input programs | hung | `?` in status line | Save after a refused load | example over unsaved work |
|---|---|---|---|---|---|---|---|---|
| committed (v290's) | 193 | 18 | 1 | 1 ok, 2 hung | 3 | 14 | **overwrote the file** | **dropped it silently** |
| the same source rebuilt here (toolchain check, earlier sweep) | 193 | 19 | - | 1 ok, 2 hung | 3 | 14 | - | - |
| **fixed** | **210** | **1** | **1** | **6 ok** | **0** | **0** | **untouched** | **asks** |

(Run to run, the committed IDE's hangs move between the input programs; it is the same defect.)
**Not opened:** `105_block_nesting_capacity` is 70,686 bytes and the IDE's editor holds 65,534; it says
so and now keeps the previous file's name. A 48,080-byte program opens whole (`ide/large-file.txt`).
**The one difference:** `245_r18_netsock` - the Windows runtime has no sockets (`rt_syscall` returns -38 for
them). Implementing them changes every Windows `.exe`'s runtime bytes - **a decision for Sarvam, not made here.**

## 4. Found, not fixed (each needs a decision that is not mine)

- **`r18_srij_overflow_guard`'s golden depends on the machine.** `suchi_srij(3037000499)` asks for 24 GB;
  it does not wrap, so the documented guard does not apply; `0` comes out only where the system refuses
  the allocation (Sarvam's sandbox). Windows and WSL grant it. **Library proofs and R29 fail there for this
  reason** - on main too. Fix the golden, or cap the allocation: Muse / Sarvam.
- **`245_r18_netsock` and `29_nishkriya` are Linux programs** (sockets; a raw Linux `syscall`).
- **The Windows compiler reads no environment**, so `SUTRAM_LANG` does nothing there and an `--object`
  for another pack is not possible on Windows yet.
- **The Windows IDE gives a program no input** (now a clean end of input, no longer a hang). An input box
  is a feature.
- ~~`Sutram-Setup.exe` is not rebuilt~~ **Rebuilt in `R34-02-INSTALLER.md`** - v243, the linker, the fixed
  IDE; Windows acceptance PASS 16 / 0 / 0, run as documented.
- **The IDE's editor holds 65,534 bytes;** a bigger program cannot be opened in it (it says so). Raising it
  means larger buffers throughout the IDE - a change of its own.
- **The IDE binary was linked by MSYS2 ld 2.47** here. The committed v290 IDE was built by another `ld`;
  the same source does not give the same bytes across the two, so **the IDE is proved by behaviour**
  (the table above), not by bytes.

## 5. The numbers, all on the final build

`Claude-to-Sarvam/evidence-r34/` holds every one.

- Windows: `tests/r34/test_link_windows.py` **1018 checks, 0 failed**; `tests/r34/test_windows_fixes.py`
  **4 / 4** (main's v242 fails 3); the ordinary path **562 programs, 0 differ**; the IDE **210 match,
  6 input ok, 1 not opened (over its limit), 1 differ (sockets), 0 hung, both guards PASS**.
- Linux (WSL, LF clone of the branch): the four binaries **rebuild byte for byte**; `SOURCE_PINS_CHECKED`;
  the ordinary path **562 programs, 0 differ**; `gates.sh` **28 PASS / 3 FAIL / 1 NOT-RUN**, the 3 FAILs
  main's own (the r18 golden twice; X11 with no display) - `gates-linux.txt`. **The FFI gates now
  pass on a clean clone with no C compiler.**
- A fresh clone with Git for Windows' defaults: r17 hashes **213 / 213** (were 119), `SOURCE_PINS_CHECKED`.
- Cross-host: `SUTRAMO2` -> PE **182 / 182 identical** (Linux linker = Windows linker); `SUTRAMO1` -> ELF
  **182 / 182 identical**, 3 refused by both.
