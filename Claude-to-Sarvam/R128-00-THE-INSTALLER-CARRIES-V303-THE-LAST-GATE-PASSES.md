# R128-00 — The installer carries the compiler and the gate passes: **68 PASS / 0 FAIL / 1 NOT-RUN**. ChatGPT R203 (landed mid-round) named three descriptor defects by reading; I reproduced all three on v302 - one SIGSEGV, one silent memory overwrite, one wrong `parimana()` - and fixed them: v303. I built it on Linux with a port of `build-installer.ps1`, and also rebuilt the Windows linker, whose embedded runtime predated v300. WS3: 36 goldens asserted a compiled size, all in the pack-message test; they now check the words and not the number. The release notes are written with R197's corrections.

- **Commit on `main`:** the commit that carries this file; its SHA is in my chat report.
- **Compiler: `Sutram 1.0 (v303) - sampurna sutra`** (was v302; the three R203 fixes, below). Linux x86-64 cloud; Windows binaries run under Wine 64.
- **`crash corpus: 227 cases + manifest, 0 failed`.** **Suite: `suite: NO-EXPECTATION=4  PASS=327  (331 run)`.**
- **Gates (`sh tools/gates.sh`, Xvfb, Linux): 68 PASS / 0 FAIL / 1 NOT-RUN** (NOT-RUN: Windows execution). How that number was reached:
  - **the full run on v303 gave 66 / 2 / 1**: `installer version` failed (the payload was v302 then), and so did `doc counts`, which counts the documents' claims against that;
  - I then rebuilt the installer with v303 and reran those two and `R93 installer gate`: **all PASS**.
  - In that full run: `codegen shapes` 12/12, `R127 descriptor` 24 checks, `pack messages` 12 sets × 11 cases.
- **The guard, v302 (`1202455`) → v303, 737 programs** (`evidence-r128/guard.txt`):
  - **Linux ELF and PE alike: 491 byte-identical, 154 refused identically, 92 DIFFER.** The 92 are the programs with a `kosh`: each `kosh` declaration now checks its capacity.
  - **Run old and new: all 92 the same output and exit, on ELF and under Wine.** **The Windows compiler (v303) under Wine compiled every program: its output is byte-identical to the Linux compiler's PE output in 583, both refuse 154, 0 differ.**

## Then: ChatGPT R203's three descriptor defects - reproduced on v302, fixed in v303

R203 landed during this round. It is a source reading, NOT RUN, and it says *do not publish "the memory model has no known defect"*. **It is right.** I ran each finding on v302 before touching code:

| R203 | the program | v302 | v303 |
|---|---|---|---|
| **F1** an index that changes the `kosh` | `k[kosh_kship(k, 5) - 2]`, `k` past 8,388,608 numbers | **SIGSEGV**: the length and elements were read before the index, which moved them and gave the old region back | `8388608` |
| F1 | `k[kosh_hri(k) - 1]` | **`2`, a read past the new length** (checked against the old one) | refused: `mala ank seema atikram` |
| F1 | `k[kosh_kship(k, 2) - 1] = 9` | refused wrongly (the old length) | stores; prints `1`, `9` |
| F1 | a slice bound `k[kosh_kship(k, 8) - 2 : 2]` | refused wrongly | `7` |
| **F2** a capacity whose bytes wrap | `kosh k[2305843009213693952]` (2^61), then 8 pushes | **another buffer's 77 became 1**: (2^61 + 4) × 8 wrapped to a 32-byte allocation | `kosh rachayitum smritih na labdha`, exit 1 |
| **F3** `parimana()` and a region | 20,000 numbers | `234096` - the new capacity read from `r11`, which the Linux `syscall` had just overwritten | `294976` (32,832 arena + 262,144 region; worked out in the evidence) |

**The fixes:**

- **F1:** when the index, or a slice's bound, **has a call in it** - the only way it can change the `kosh` (a `kosh` cannot be reached through a global, a cell or a raw builtin since v301) - the descriptor stays on the stack, and the length and elements are read after the index.
  - Without a call, v302's code is kept. My first fix refreshed every index, and **the codegen-shape gate caught it**: two float-index shapes exceeded their instruction ceilings (46 / 43, 47 / 44). Now 12 / 12.
  - **A note on the gate:** `tools/codegen_gate.py` ignores its argument and reads `SUTRAM_COMPILER` or the tree's `sutram_compiler`.
- **F2:** a declared capacity above 2^40 numbers (8 TiB) stops with the "cannot make a kosh" message before any arithmetic. Growth only doubles from there, one push at a time, so it cannot reach a wrapping size.
- **F3:** the new capacity is read from the runtime stack, where it was pushed before the `syscall`.

**Gate `R127 descriptor` +6 checks, these six. v302 fails all six; v303 passes 24 of 24 with PE.**

**What R203 also says, and I agree:**

- old arena buffers are retained;
- a block does not reclaim its `kosh`;
- `parimana()` is accounted bytes, not physical memory;
- the release notes must not claim "no known defect" - **they do not.**

**Muse R129** (also mid-round) attacked v302 and found no crash or silent wrong. Its probes could not reach R203's F1-F3: no index with a call, no capacity near 2^61, no `parimana()` with a region. Its "gap": growing a `kosh` parameter is refused. That is my R127 WS3 step 5, a language decision. **Its nit:** that refusal still says `kosh_push`, the old name.

## WS3 first - goldens that assert a compiled size

**Found: 36, all in one test - `tests/sandesh/expect/<pack>/{ok,oob,kosh_empty}.out`.** That is 3 cases × the default and the eleven packs.

- **Why they assert it:** each records the compiler's success line, `Siddh: 678 baait sankalit` (in each pack's words), and the size is in it.
- **What it cost:** R127 re-recorded the 12 `kosh_empty` ones for a reason that had nothing to do with messages. The 24 `ok` / `oob` ones would have gone the same way at the next change to the code generator.
- **The fix, in the test, not the goldens' meaning:**
  - `tests/sandesh/test_sandesh.py` now writes the number in a successful compile's line as `#` (`Siddh: # baait sankalit`), so the pack's words are still checked.
  - `#`, not `N`: the test also refuses Latin letters in a pack's output.
  - Re-recorded: **the diff is those 36 numbers and nothing else.** The gate passes.

**Searched and clean:**

- `tests/expect/` (the suite): a successful compile's output is not compared, only the program's. A `.compile_fail` golden holds a refusal, which has no size.
- `tests/r*/` gate scripts: the one that reads the success line (`tests/r50`) compares the Latin and Devanagari compiles **with each other**, not with a number.
- The Windows harness (`tools/test_windows_native.py`) compares the same `tests/expect` files. `Windows-to-Sarvam/*/native-cases.json` records sizes, but as results, not expectations.
- **Not a size golden, on purpose:** the guard, R28 / R29 (`--object` + `sutram-link` = the direct compile) and R50 compare **bytes for identity**. They fail when the code changes, and that is their job.

## WS1 - the installer payload is v302

**`python3 tools/check_installer_version.py`:**

```
PASS payload v303 = compiler v303 (bin/ and win/sutram.exe, packed 2026-11-04; the wizard has no version of its own; 0 of its 138 lib/lang files differ from the tree; sutram_compiler, sutram.exe, win/sutram.exe v303; sha256 0a278682f8333419...)
```

**How, without a Windows machine:**

- `tools/build_installer_linux.py` is a step-for-step port of `windows\native-installer\build-installer.ps1`, the Windows build. In the same order:
  - stage the payload;
  - `payload.manifest.sha256` (paths with backslashes, as `install-core.ps1` reads them);
  - `payload.zip` (deflate, backslash names as Windows PowerShell 5.1 writes them - the v243 payload has them too);
  - `embedded_hashes.inc`;
  - the icon resource (`Write-IconResourceInclude`, ported);
  - `nasm -f win64` the wizard, link it with mingw `ld` (kernel32, bcrypt);
  - `--self-test`;
  - `Sutram-Setup.sha256`.
- **Differences from the Windows build, said:** text files keep the tree's LF line endings, and the link uses mingw's import libraries. `docs/INSTALLER-REBUILD.md` has both routes now.

**What the brief asked me to verify:**

| check | result |
|---|---|
| the version the installed compiler reports: `bin\sutram.exe --version`, `win\sutram.exe --version`, extracted from the installer and run under Wine | **`Sutram 1.0 (v303) - sampurna sutra`**, both |
| the payload compilers are the tree's verified binary | SHA-256 of both = `win/sutram.exe`'s, `4c05d5cbad99b32b...` |
| SHA-256 of `Sutram-Setup.exe` = `Sutram-Setup.sha256` | **`0a278682f8333419fcdb874674910c5201e85df741b7835f77fe061845b669e0`** both |
| `Sutram-Setup.exe --self-test` (embedded hashes of the payload and the two scripts) | exit 0 under Wine. **A copy with one payload byte flipped: exit 1** - so it checks, not only runs |
| `install-core.ps1`'s `Verify-Payload`, replayed in Python on the extracted payload | 656 manifest lines (the final build, with these notes), 0 hash mismatches, 0 unmanifested files |

**One more thing was stale, and the gate does not look at it: the Windows linker.**

- `sutram-link.exe` (built Oct 27) embeds the Windows runtime, and that runtime predated v300's lazy commit and v302's `munmap`.
- **Under Wine, a program linked by it was byte-identical to the direct compile in 0 of 21 cases.**
- Rebuilt from `linker/sutram_link.asm` (`nasm -f win64 -DWINDOWS`, `--no-insert-timestamp`): **21 of 21 byte-identical.** The payload carries the rebuilt one.
- **`sutram-ide-gui.exe` is unchanged:** its sources have not changed since it was built, it runs the payload's `win\sutram.exe`, and it is the binary the v297 IDE run tested.

**Not done here - the owner's acceptance:**

- running the wizard on a real Windows machine and installing;
- the installed IDE;
- uninstalling;
- the execution policy: the scripts are unsigned, and `Restricted` / `AllSigned` would block them, which the README already calls a release blocker.

**This is the gate going green, not the installer being accepted.** The gate will go red again at the next version bump: `tools/build_installer_linux.py` is then the one command.

## WS2 - the release notes

**`docs/RELEASE-NOTES.md`**, written with R197's corrections applied:

- **"no exception handling" →** *no non-local try / catch unwinding*. The explicit result handling that exists (`siddhi` / `dosh` / `prasar` / `yadi dosh`) is described, with its four limits: no stored result, no typed results, no status check through a function value, no `dasham` (and, from v301, no `kosh`) in a result.
- **"no debugger" →** *no interactive debugger, no breakpoints, no stepping*. The debug diagnostics that exist are listed (`--debug`, `--debug=<names>@N-M`, `--debug-from`, `--check`, `sutram -i`). An external native debugger sees machine code only: **I checked: the output has no symbols.**
- **"integer wrapping, and the library refuses" →** **a table of ten worked examples, each run on v302:**
  - `MAX + 1` wraps to `MIN`;
  - a literal or a constant expression past 64 bits is refused;
  - division by zero stops;
  - `MIN / -1` wraps;
  - `ganita_janchit_gun` reports in `ok`;
  - `ganita_paripurna_gun` saturates;
  - `dvigun` stops;
  - `kramgun` returns −1.
  - **So "the library refuses" is said to be false as a blanket claim.**
- **"no `parikshita` markers" →** stated as 0 of 310 library functions marked. The marker works for the student's own `prakriya`. The 229 library and 86 property proofs are **executable tests, not formal proofs**, and that is the guarantee stated as absent.
- **R197 line 119, every item there:**
  - raw-pointer extent and lifetime;
  - in-place string destinations - `vartani_pratilip`, and `vartani_sandhi`, which appends in place as `strcat` does;
  - bytes, not characters (`vartani_aayam("नमस्ते")` is 18);
  - ASCII-only helpers;
  - the `kosh` alias risk, now: the FFI borrow and the slice rule;
  - helper allocations kept even inside a block - measured: a 16-byte `a + "cd"` made in a `mandapa` is still counted after it;
  - no free inside a live scope;
  - file flags by platform;
  - `patra_asti` meaning "opens read-only";
  - the frozen packs - measured: a v301 message under `--lang hindi` prints the default text;
  - untested and skipped platform features;
  - measured commitment.
- **Added from the Windows rounds:**
  - the IDE's 64 KiB editor limit leaving the previous output on screen;
  - its partly English menus;
  - Run Module with no input;
  - the linker's `Sutram Error`;
  - objects from different compiler versions;
  - the v301-v302 breaking changes.

## Not done, and why

- **Native Windows: install, uninstall, IDE, gates** - the owner's acceptance; NOT RUN here.
- **The linker's `Sutram Error` messages:** stated in the release notes, not changed. The brief did not ask, and `sutram-link`'s byte identity is gated (R28).
- **Not touched:** `backups/`, `Windows-to-Sarvam/`, the frozen packs (their goldens' size numbers only, in the test), `MEMORY-DECISION.md`, `Muse-to-Sarvam/`.
