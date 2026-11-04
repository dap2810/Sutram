# Sutram 1.0 (v303) — release notes

**Compiler `Sutram 1.0 (v303) - sampurna sutra`, 4 November 2026.** Linux x86-64 (ELF) and Windows x64 (PE).
The installer `Sutram-Setup.exe` carries this compiler (payload v303). Its SHA-256 is in `Sutram-Setup.sha256`.

These notes say what the release does, what it **does not include**, and every limitation known. A limitation
left out would be a false promise, so the list is long on purpose. Each claim names where it is pinned
(an example, a gate, or the reference). Sources: ChatGPT R197 (the corrections are applied below), the R116
contract table, the Windows rounds 1-4 and the v297 IDE run.

## What is in it

- **A language with Sanskrit keywords and builtins** (Devanagari accepted). The keywords and messages have
  eleven language packs. **Only the Sanskrit pack is developed; the other ten are frozen:** they work, and get
  no new development (see *Not included*).
- **One compiler, no runtime, no dependencies.** It writes a Linux ELF or a Windows PE directly, and
  `sutram-link` links separately compiled modules. A terminal IDE, an X11 IDE and a Windows IDE are included.
- **Memory you can see:**
  - `nirmmita` comes from an arena;
  - a `mandapa` block gives its memory back at its end, and `mandapa parimita N` refuses past a budget;
  - `parimana()` reports the bytes held;
  - **a `kosh` is a descriptor:** its names always agree, at any size, and there is no limit on how many a
    program makes (v302);
  - running out of memory is a message and exit 1, not a crash.
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
| **Freeing memory inside a live scope** | a `mandapa` block gives its memory back at its end; outside a block, memory lives as long as the program. No `free`, no garbage collector |
| **Closures**, calling an expression directly (`t[0](x)`), a checked type for function values, methods dispatched on type / traits, slices of a `kosh dasham`, a slice outliving its function | reference §17 lists them as not done |
| **Formal verification** | the library proofs and property proofs are **executable tests** - they run code and compare results - and the native and Windows tests run programs. **No library function is marked `parikshita`** (0 of 310): R81's checked-function marker exists and works for your own `prakriya`, but the library does not use it. None of this is a machine-checked proof of the compiler or the library |
| **Development of the ten non-Sanskrit packs** | Hindi, Gujarati and the other eight are frozen: in the tree and working, with no new development. A defect in one is reported, not fixed. Messages added since the freeze appear in the default (Sanskrit transliteration) form in those packs |

## Integer arithmetic: what wraps, what refuses, what reports

**The operators wrap; the compiler refuses only what it can see; the library follows each function's
contract.** Measured on v303, Linux:

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
- **A slice of a `kosh` cannot be kept in a name** (`E_KOSH_VIBHAG`); pass it on directly.
- **A small `kosh` that grows past something allocated after it leaves its old elements in the arena** (at most about
  its own size again, under 64 KiB); `parimana()` counts them.
- **Helper allocations are kept for the program's life:** `anka_akshar`, string `+` and similar take new memory
  for each result, and it is not given back - not even at the end of an enclosing `mandapa` (measured: a
  16-byte `a + "cd"` made inside a block is still counted by `parimana()` after it).
- **Measured memory commitment:**
  - **Linux** reserves the 1 GiB arena and commits only touched pages.
  - **Windows** (v300) reserves and commits 64 KiB where a page is first touched. One `nirmmita(64)` commits about
    0 MB (measured under Wine; native Windows commit is the owner's measurement).
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
  - The last native Windows runs were the Windows rounds 1-4: v297 had 305 passes and 8 failures; after the
    round 3 and round 4 fixes, 312 passes and 0 failures, on the branch merged as v299.
  - v298-v303 have been run on Windows only under Wine 64 here, with every program's output compared.
  - **Native Windows execution of v303 is not yet done.**
- **Skipped on Windows, by design:**
  - `examples/29_nishkriya`: inline Linux system calls;
  - socket examples, which differ by platform (`245_r18_netsock`).
- **The Windows IDE:**
  - **an editor limit of about 64 KiB refuses a larger file and leaves the previous program and its output on
    screen** - a student can see output that is not theirs (`105_block_nesting_capacity`, 70 KB);
  - **its menus and buttons are partly English;**
  - **Run Module gives no interactive input** (end of input at once).
- **The installer's PowerShell scripts are unsigned.**
  - Under a `Restricted` or `AllSigned` execution policy they are blocked.
  - Install and uninstall on a fresh machine are the owner's acceptance test, not yet done for v303.
  - The installer's hashes detect corruption, not the publisher.
- **The linker:** `sutram-link` and the object tools still print `Sutram Error` where the compiler prints
  `Sutram truti` (v294 renamed only the compiler's).

**Other**
- **Separately compiled objects must come from the same compiler version:** `sutram-link` does not check the
  version, and v302 changed how a `kosh` is passed.
- **The breaking changes of v301-v302:**
  - a name cannot change kind (`vitti w = 0` then `w = k` is refused);
  - a `kosh` cannot go into a cell, a module `vitti` or an untyped parameter;
  - a slice of a `kosh` cannot be kept in a name.
  - Three examples were rewritten for the first rule.

## Changes since the last installer before R128 (v243)

The full record is `docs/CHANGELOG.md` and `docs/rounds/CHANGELOG-ARCHIVE.md`. Since v297, Windows found two
defects Linux never showed:

- `anka_akshar` returned memory it did not own;
- `vartani_sandhi` wrote into a read-only literal.

v298 fixed both. Then:

- **v299-v300:** brought the memory model to Windows, and made Windows commit only what is touched.
- **v301:** fixed three live defects in how the compiler tracks a name's kind (two crashes, one silent
  over-read), and closed the eight Muse found.
- **v302:** made a `kosh` a descriptor.
- **v303:** fixed three defects in it that ChatGPT R203 found by reading the source:
  - an index or a slice bound that grew the `kosh` read its old elements (SIGSEGV after a region was given back);
  - a capacity past 2^40 wrapped into a tiny allocation;
  - `parimana()` miscounted a large `kosh`.
