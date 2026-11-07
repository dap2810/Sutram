# Sutram 1.0 (v307) — release notes

**Compiler `Sutram 1.0 (v307) - sampurna sutra`, 6 November 2026.** Linux x86-64 (ELF) and Windows x64 (PE).
The installer `Sutram-Setup.exe` carries this compiler (payload v307). Its SHA-256 is in `Sutram-Setup.sha256`.

These notes say what the release does, what it **does not include**, and every limitation known. A limitation
left out would be a false promise, so the list is long on purpose. Each claim names where it is pinned
(an example, a gate, or the reference). Sources: ChatGPT R197 (the corrections are applied below), the R116
contract table, the Windows rounds 1-4 and the v297 IDE run.

## What is in it

- **A language with Sanskrit keywords and builtins** (Devanagari accepted). The keywords and messages have
  eleven language packs. **Only the Sanskrit pack is developed; the other ten are frozen:** they work, and get
  no new development (see *Not included*).
- **One compiler; native executables with their support code embedded.** There is no separately installed language
  runtime or VM; programs use the platform's system interfaces (Linux system calls, Windows' own DLLs). It writes a
  Linux ELF or a Windows PE directly, and
  `sutram-link` links separately compiled modules. A terminal IDE, an X11 IDE and a Windows IDE are included.
- **Memory you can see:**
  - `nirmmita` comes from an arena;
  - a `mandapa` block gives back the scratch `nirmmita` written inside it when it ends (its pages are kept for
    reuse, not returned to the system), and `mandapa parimita N` refuses a scratch allocation past `N` bytes - a
    budget for that block's `nirmmita`, not for the whole program, nor for `kosh` storage;
  - `parimana()` reports the allocator's accounted bytes (below), not memory in use or reserved;
  - **a `kosh` is a descriptor:** its names always agree, at any size, and the fixed 64 MiB reservation every small
    `kosh` had up to v301 is gone (v302); memory is still finite, a `kosh` past 64 KiB of elements reserves a region
    of at least 64 MiB, and a declared capacity above 2^40 numbers is refused (v303);
  - **when the checked allocation paths get no memory** - making or growing a `kosh`, a declared capacity too
    large - the program stops with a message and exit 1 instead of crashing. That says nothing about a failure
    later, when the system cannot back a reserved page that is first touched, nor about raw-pointer errors.
- **Checked by the compiler:**
  - a name keeps one kind for its whole `prakriya` (`E_VITTI_PRAKAR`);
  - a `kosh` cannot become a raw number (`E_KOSH_DVARA`);
  - a block's `kosh` cannot leave its block (`E_KOSH_MANDAPA`);
  - `mala` / `kosh` indexing is bounds-checked;
  - division by zero stops with `E_SHUNYA_BHAJAN`;
  - a literal or constant expression past 64 bits is refused (`E_ATIPRAVAH`).
- **Tests:**
  - 331 examples (327 with a golden);
  - 69 Linux gates, including a guard that compiles every program before and after each change and compares
    the bytes;
  - 227 crash-corpus cases;
  - 229 library proofs and 86 property proofs - these are executable tests, not formal proofs (below).

## Not included in v1.0

| not included | what there is instead |
|---|---|
| **Non-local exception handling** - no `try` / `catch`, no unwinding through callers | **Explicit result handling exists:** a *phal-prakriya* returns `siddhi(v)` or `dosh(c)`, `prasar` passes a failure up, and `yadi dosh (q = f(...)) {..} anya {..}` handles it (reference §18). Its limits: a result cannot be kept in a variable; there are no typed results (`phal<T>`); calling one through a function value does not check the status; a result cannot carry a `dasham`, nor a `kosh` (`E_KOSH_DVARA`) |
| **An interactive debugger** - no breakpoints, no stepping, no watch window in any IDE | **Debug diagnostics exist:** `--debug` traces each statement of your file with its line and its scalar variables. `--debug=<names>@N-M` watches chosen names over a line range; `--debug-from=N` starts at a line (R45-R49). `--check` checks without writing a program; `sutram -i` is an interactive session. An external native debugger (gdb, WinDbg) can run the output, but **sees machine code only: the output has no debug symbols** |
| **Generics** | none: a `kosh` holds whole numbers (`kosh`) or `dasham` (`kosh dasham`); a `prakriya` parameter is untyped, or `kosh`, `kosh dasham`, `vibhag`, `dasham` |
| **Threads, or any concurrent execution within a process** | none. The arena, its budgets and `kosh` growth are unsynchronised. **Deferred beyond v1.0, not ruled out** (ChatGPT R195: per-thread arenas, a multi-week design) |
| **Freeing memory inside a live scope** | a `mandapa` block gives back its scratch `nirmmita` at its end; other memory lives as long as the program (see *Memory and pointers* for what the allocator returns by itself). No `free`, no garbage collector |
| **Closures**, calling an expression directly (`t[0](x)`), a checked type for function values, methods dispatched on type / traits, slices of a `kosh dasham`, a slice outliving its function | reference §17 lists them as not done |
| **Formal verification** | the library proofs and property proofs are **executable tests** - they run code and compare results - and the native and Windows tests run programs. **No library function is marked `parikshita`** (0 of 310): R81's checked-function marker exists and works for your own `prakriya`, but the library does not use it. None of this is a machine-checked proof of the compiler or the library |
| **Development of the ten non-Sanskrit packs** | Hindi, Gujarati and the other eight are frozen: in the tree and working, with no new development. A defect in one is reported, not fixed. Messages added since the freeze appear in the default (Sanskrit transliteration) form in those packs |

## Integer arithmetic: what wraps, what refuses, what reports

**The operators wrap; the compiler refuses only what it can see; the library follows each function's
contract.** Measured on v306, Linux:

| you write | you get |
|---|---|
| `vitti a = 9223372036854775807` then `likha(a + 1)` | `-9223372036854775808` - **the operator wraps, silently** |
| `vitti a = 4000000000` then `likha(a * a * a)` | `-855667187417874432` - wraps |
| `vitti a = MIN` (`0 - 9223372036854775807 - 1`), then `likha(a / (0 - 1))` | `-9223372036854775808` - wraps, does not crash |
| `likha(9223372036854775808)` | refused when compiled: `E_ATIPRAVAH` (a literal past 64 bits) |
| `likha(9223372036854775807 + 1)` | refused when compiled: `E_ATIPRAVAH` (a constant expression) |
| `likha(7 / z)` with `z = 0` at run time | stops: `E_SHUNYA_BHAJAN`, exit 1 |
| `ganita_janchit_gun(a, b, ok)` (`yoj ganita`) | the product, `ok[0] = 1` - or **0 and `ok[0] = 0` when it does not fit**: check `ok` |
| `ganita_paripurna_gun(a, b)` | the product, **or the largest / smallest `vitti`** when it does not fit (saturates) |
| `dvigun`, `trigun`, `vardh` (`ganit`) | stop with `E_ATIPRAVAH` when the result does not fit |
| `kramgun` (factorial), `fib`, `varg` and the others listed in reference §4 (v276) | return **−1** when the answer is too large |

So **"the library refuses" is not true of every function:**

- some stop the program;
- some return a status (`ok[0]`, 0, or −1);
- some saturate.

Reference §4 and its R116 table give each one. A zero or a Sanskrit name does not prove a computation
succeeded; use the checked form when the program must detect a failure and go on.

## Limitations of what is included

**Memory and pointers**
- **A raw `nirmmita` buffer is not bounds-checked**, except `p = nirmmita(CONST)` never reassigned (R78). Its
  extent and lifetime are the programmer's: the address is valid for the program's life, or until its block ends
  inside a `mandapa` (escaping a block is refused, `E_SCRATCH_ESCAPE`).
- **A foreign function** (`--ffi`, a `ptr` parameter) **receives a `kosh`'s elements' address, valid until the `kosh` next
  grows.** Nothing checks what the foreign side does with it.
- **A slice of a `kosh` is a view of the elements as they are when it is made.** So (`E_KOSH_VIBHAG`):
  - it cannot be kept in a name (`vitti s = k[1:4]`);
  - it cannot be given to a `prakriya` that may grow a `kosh` (it, or one it calls, runs `kosh_kship`);
  - it cannot be given beside another argument that has a call in it (the call could grow the `kosh` first) - to a
    `prakriya` called by its name, **or through a function value** (`vitti f = badal; f(k[0:1], kosh_kship(k, 8))`:
    v306 compiled that, and the callee wrote into the old elements or read a released region - ChatGPT R205-206 S3,
    refused from v307).
  Passed on directly, to a `prakriya` that only reads, it is safe: `yog(k[1:4])`. In `k[lo:]` the end is the length
  after `lo` is evaluated (v305).
- **`parimana()` counts:** occupied arena storage (including temporary buffers in open blocks, `kosh` descriptors and
  retained old arena buffers) plus the current capacity of a `kosh` whose elements have a region of their own. It is
  not resident memory, commit or reserved address space, and an allocation that falls back to its own `mmap` (past the
  arena, or with no arena) is not in it.
- **There is no free a program can call.** What the allocator gives back by itself: a `mandapa`'s scratch at the
  block's end, and an outgrown region of a large `kosh`. **What it keeps:** a small `kosh` that grows past
  something allocated after it leaves its old elements in the arena (at most about its own size again, under 64 KiB);
  a `kosh`'s first elements, which sit beside its descriptor, stay allocated when it grows - **for a `kosh` declared
  large (`kosh k[1000000]`) that is the whole declared capacity**; and a block's `kosh` storage is not reclaimed at
  the block's end. `parimana()` counts all of these.
- **Helper allocations are kept for the program's life:** `anka_akshar`, string `+` and similar take new memory
  for each result, and it is not given back - not even at the end of an enclosing `mandapa` (measured: a
  16-byte `a + "cd"` made inside a block is still counted by `parimana()` after it).
- **Measured memory commitment:**
  - **Linux** reserves the 1 GiB arena and commits only touched pages.
  - **Windows** (v300) reserves and commits 64 KiB where a page is first touched. One `nirmmita(64)` commits about
    0 MB (measured under Wine; native Windows commit is the owner's measurement).
  - **When Windows refuses that commit** (a commit limit, or the system out of memory), the program stops with
    `Sutram truti: smritih na labdha` on stderr and exit 1 (v306). Up to v305 it died with an access violation and
    printed nothing (native Windows, 64-640 MiB job commit limits). **It is fatal:** there is no recovery, and no
    promise that the operation in progress was left whole. It applies after the runtime's memory handler is
    installed; **if Windows refuses to install that handler**, the program stops at once with
    `Sutram truti: smriti-prabandhah na arabdhah` and exit 1 (v307; up to v306 it ran on and died at the first touch
    of reserved memory). The handler commits a page that is reserved and private to the process and not a thread's
    stack; it does not know which reservations are Sutram's, so a raw or foreign pointer into another reservation of
    that kind is outside this promise.
  - **On Linux, a limit is a different thing.** An address-space limit (`ulimit -v`) refuses the reservation, and
    the checked paths print their own message (`kosh vardhayitum smritih na labdha`); with overcommit, the system
    may instead end the program when a page is touched. A Windows job commit limit and a Linux limit are not the
    same resource, and these notes do not equate them.
- **A program under an address-space limit below about 1 GiB** gets no arena; every allocation then is its own
  `mmap`. It still runs (1,000 `kosh` under a 300 MB limit: measured).

**Strings and files**
- **Strings are bytes, not characters.**
  - `vartani_aayam` counts bytes. A Devanagari letter is several bytes in UTF-8, so `akshar(s, i)` reads a byte.
  - Case and character helpers (`akshar_guru`, `akshar_laghu`, the `varna` library's `asti_*_akshar`) are
    **ASCII-only**.
- **In-place string writing needs room the caller gives.** `vartani_pratilip(d, s)` (copy), `vartani_sandhi(s, t)`
  (append in place, like C's `strcat`) and the formatting routines write into a destination the caller provides,
  and **do not check its capacity**. A string literal as the destination is refused (v298, `E_VARTANI_STHIRA`);
  for a new string, write `s + t`.
- **`patra_asti(path)` means "opens read-only"**, not "exists". A missing file, a missing directory and a permission
  failure all give 0. Its contract waits on an operating-system query the compiler does not make (R116).
- **File flags differ by platform:** the `patra` builtins are Linux system calls, mapped on Windows by the runtime
  (open, read, write, close). Flags beyond those the library uses are not mapped.

**Windows**
- **Every Linux gate runs here; the Windows gates run on the owner's machine.**
  - The native Windows runs: rounds 1-4 (v297: 305 passes and 8 failures; then 312 passes and 0 failures, merged as
    v299), and v305 (6 November: 321 passes, 1 compile failure that was the harness's working folder, fixed in
    R131; the memory probes passed except the out-of-memory one, fixed in v306). ChatGPT's PR #66 runs (a v305
    source build with the v306 out-of-memory change, Windows build 26100): 8 of 8 out-of-memory checks.
  - **Native Windows execution of v307 is not yet done.** Acceptance applies to the exact binary hashes run.
- **An open observation under Wine:** about 1 run in 200 of a finished program, Wine reports an unhandled page
  fault at exit - after all the output, with exit code 0, at the same address in Wine's own code each time. Seen
  on v301 and v305 (also on programs with no `kosh`), not in 200 runs each of v299 and v300 - too few to say when
  it began. Its cause is not known. It has not been reported from the native v305 runs; watch for it there.
- **Skipped on Windows, by design:**
  - `examples/29_nishkriya`: inline Linux system calls;
  - socket examples, which differ by platform (`245_r18_netsock`).
- **The Windows IDE:**
  - **an editor limit of about 64 KiB refuses a larger file.** From v306 the refusal clears the output pane and
    says the editor still holds the previous file (`[patram na udghatitam - sampadake purvam patram eva asti]`);
    up to v305 the previous program's output stayed on screen above the refusal;
  - **its menus and buttons are partly English;**
  - **Run Module gives no interactive input** (end of input at once).
- **The installer (v306-v307):**
  - **it refuses to install while another Sutram is installed** where a terminal could find it - on the machine or
    user PATH, or in the folder older installers used (`%LOCALAPPDATA%\Sutram`) - and names it. Up to v305 it
    installed beside it, and a new terminal ran the older one (`Sutram 1.4.0`, Windows round of v303);
  - **with Add to PATH, it finishes only when a new terminal runs this compiler:** it opens `cmd.exe` with the PATH a
    new terminal would get and compares `sutram --version`;
  - **it cannot wait forever:** the engine runs without a console window, with `-NonInteractive`, no progress bars
    and no prompts, and the wizard stops it after 15 minutes and reports a failure (v306);
  - **an installation that stops part-way is finished by the next run** (v307). The v303 copy stopped inside file
    132 of 657 (left empty), after deleting the previous installation's 643 files; every later run refused it as "a
    user file". Now the first change to the folder records what is being installed (`payload.pending.sha256`), the
    next run treats those files as its own, each file is named in the log before it is copied and written under a
    temporary name first, and an upgrade overwrites files in place and deletes only those the new payload lacks.
    **Why the v303 copy stopped is still not known** (security software that watches mass deletes is the leading
    candidate; not confirmed);
  - Windows' list of installed apps shows the compiler's version (`1.0.307`), not `0.1.0` (v307);
  - **its PowerShell scripts are unsigned, and run with `-ExecutionPolicy Bypass`** for that process only. A policy
    set by Group Policy still overrides it;
  - install, an installation stopped and finished, a new terminal, and uninstall are the owner's acceptance test,
    not yet done for v307 (`tests/windows/test_installer_e2e.py` runs them); so is the upgrade over the owner's
    existing v305 installation, with the wizard;
  - the installer's hashes detect corruption, not the publisher.
- **The linker:** `sutram-link` and the object tools still print `Sutram Error` where the compiler prints
  `Sutram truti` (v294 renamed only the compiler's).

**Other**
- **Objects from different compiler versions are not supported:** v302 changed how a `kosh` is passed, and
  `sutram-link` does not check the version - mixing objects is not refused, it is wrong. Rebuild every object with
  the same compiler.
- **The breaking changes of v301-v304:**
  - a name cannot change kind (`vitti w = 0` then `w = k` is refused);
  - a `kosh` cannot go into a cell, a module `vitti` or an untyped parameter;
  - a slice of a `kosh` cannot be kept in a name, nor go beside a growth (above) - through a function value too (v307);
  - a declared capacity above 2^40 numbers is refused.
  - Three examples were rewritten for the first rule. The gain: a `kosh` parameter can grow (v304).

## Changes since the last installer before R128 (v243)

The full record is `docs/CHANGELOG.md` and `docs/rounds/CHANGELOG-ARCHIVE.md`. Since v297, the first Windows
testing exposed two defects. A passing earlier Linux sample had not proved them correct; R121 then reproduced both
on Linux as well:

- `anka_akshar` returned memory it did not own;
- `vartani_sandhi` wrote into a read-only literal.

v298 fixed both. Then:

- **v299-v300:** brought the memory model to Windows, and made Windows commit only what is touched.
- **v301:** fixed three live defects in how the compiler tracks a name's kind (two crashes, one silent
  over-read), and closed the eight Muse found.
- **v302:** made a `kosh` a descriptor.
- **v303:** fixed three defects in it that ChatGPT R203 found by reading the source:
  - an index or a slice bound that grew the `kosh` read its old elements (SIGSEGV after a region was given back);
  - a huge declared capacity wrapped its byte count into a tiny allocation (2^61 did; v303 refuses any declared
    capacity above 2^40, which is not to say every one above it wrapped);
  - `parimana()` miscounted a large `kosh`.
- **v304:** a `kosh` parameter can grow, and the caller sees it (refused up to v303). A slice of a `kosh` cannot be
  given to a `prakriya` that may grow one, or beside an argument with a call (`E_KOSH_VIBHAG`) - that closes the
  stale-slice case ChatGPT R204 found (S1: v303 crashed on it).
- **v305:** `k[lo:]` ends at the length after `lo` is evaluated (R204 S2), and a growth past 2^40 numbers stops with
  the grow message (a stated invariant, checked; no machine reaches it).
- **v306:** the Windows out-of-memory path (a refused commit) is a message and exit 1, not an access violation; the
  installer refuses a second Sutram, checks a new terminal and cannot wait forever; the IDE clears its output on a
  refused load and says the editor kept the previous file.
- **v307:** a `kosh` slice given through a function value beside an argument with a call is refused, as for a
  direct call (ChatGPT R205-206 S3: v306 lost the write or crashed); the Windows runtime stops with a message if its
  memory handler cannot be installed (R205-206 W1); an interrupted installation is finished by the next run, the log
  names each file, and Windows is told the real version.

How these defects were found - a second platform, testing, an independent attack and reading each found some the
others missed - is in `docs/reports/HOW-DEFECTS-WERE-FOUND.md`.
