# Sutram 1.0 (v315) — release notes

**Compiler `Sutram 1.0 (v315) - sampurna sutra`, 9 November 2026.** Linux x86-64 (ELF) and Windows x64 (PE).
The installer `Sutram-Setup.exe` carries this compiler (payload v315). Its SHA-256 is in `Sutram-Setup.sha256`.

These notes say what the release does, what it **does not include**, and every limitation known. A limitation
left out would be a false promise, so the list is long on purpose. Each claim names where it is pinned
(an example, a gate, or the reference). Sources: ChatGPT R197 (the corrections are applied below), the R116
contract table, the Windows rounds 1-4 and the v297 IDE run.

## Status: what v315 closes, and what it does not (R140-R154)

v315 is v314 plus (R153-R154):
- **the syntax tree's limit has its own code,** `E_VRIKSHA_SEEMA`, and its advice is one that works (a smaller
  program, fewer modules - not split statements). v314's notes said both limits named themselves; the tree limit
  had no code.
- **the constant folder cannot turn `k[0:1] + 0` into a bare slice** (Muse's reading): its identity rule now skips a
  slice or anything holding a `kosh`, as it skipped a `kosh`. The walk refused such an expression first, so nothing
  that compiles changes.
- **the installer records what it did, not that it did something:** shortcuts by the SHA-256 of each link as it
  wrote it (R153: v314 could delete a user's own desktop link on uninstall); PATH as the text of the one entry it
  added (`PathAdded`; uninstall removes that one entry, not every equal one); the `.sm` default as the value it set
  (`AssociationSet`); and uninstall removes the `Sutram.Source` values it wrote, and each key only when empty (v314
  removed the whole tree, a verb a user added under it included).

**Evidence scope for v315.** *The pinned v315 package (the setup committed with these notes) passed the Linux
gates, the byte-for-byte guard against v314 and the Windows compiler under Wine; it has not been installed, run or
uninstalled on Windows, and untested guarantees remain unclaimed.* Not claimed: any of the installer's ownership
changes on Windows (`tests/windows/test_installer_shortcuts.ps1` is written, not run), and what earlier native runs
did not establish.

v314 was v313 plus (R152):
- **a slice is not given to a foreign function** (`--ffi`): `E_KOSH_VIBHAG`. v313 compiled it, and passed the
  slice's descriptor - so the C side read an address, and as an `i64` count it crashed (found by Muse's reading,
  confirmed here). Every other door already refused it; this one had no check.
- **`--analysis-steps=N`** sets the expression check's budget for one compile; the default is **200,000** (ChatGPT
  R214-R217's contract: 1 to 2147483647, one argument with `=`, refused otherwise, `E_PARIKSHA_PADANI`). The widest
  statement the syntax tree holds, of the shapes measured, takes 87,316 steps; no measured statement reaches the
  default (a statement the tree holds is bounded at 349,521 steps, so a shape above 200,000 is possible in principle).
- **the two size limits:** the analysis limit names its number, the prakriya, and says it is not the syntax
  tree's; the syntax tree's full message said it was not the analysis limit, but had no code of its own until v315
  (this note said "the two limits now name themselves"; that overstated it).
- **the desktop shortcut:** when a user's own `Sutram IDE.lnk` is on the desktop it is kept and the installer's
  is `Sutram IDE (Sutram).lnk` (v312 made none, and the only "Sutram IDE" opened the user's target); the checkbox
  says "Sutram IDE", not "Sutram Terminal".
- **shortcut ownership, in the package rebuilt for R153 (the compiler is unchanged):** v314's first package could
  delete a user's own desktop `Sutram IDE.lnk` on uninstall when it pointed at the installed IDE (ChatGPT's trace:
  the helper kept it, its caller recorded it as the installer's, uninstall trusted that and the target), and could
  overwrite on reinstall a link the user had changed. Now one function decides and records: a link is written only
  when its name is free or it is the installer's own, unchanged since (its bytes have the SHA-256 recorded when it
  was written); the desktop link takes the first free of ten names; uninstall removes only links whose bytes still
  have the recorded hash. A matching target is no longer taken as ownership.

**Evidence scope for v314.** *The pinned v314 package (the setup committed with these notes - its hash is in
`Sutram-Setup.sha256`) passed the Linux gates, the byte-for-byte guard against v313 and the Windows compiler
under Wine; it has not been installed, run or uninstalled on Windows, and untested guarantees remain unclaimed.*
Not claimed: the shortcut fix and the checkbox on Windows; `--analysis-steps` with the Windows compiler natively;
the foreign-function refusal with the Windows FFI natively; what v313's and v312's native runs did not establish.

v313 was v312 plus (R147):
- **the expression check's budget is a defensive stop, not a language limit.** v312 set it to 65,536 steps, which
  refused one expression of 8,200 to 16,400 terms that the compiler can otherwise hold - generated code, as
  ChatGPT said, not anything in the tree. From v313 it is 349,521, the most a statement the syntax tree can hold can
  take (8 fields for each of its 43,690 nodes, plus one), so **no statement the compiler can hold is refused by
  it**; the widest, 21,829 terms, compiles. If it ever fires it is a compiler defect, and the message says that:
  report it, and split the statement meanwhile. The size limit a program meets is the syntax tree's (below and in
  the language reference). The refusal is tested by a build with the budget at 64, on every gate run.
- **the licence page's instruction** is two lines high (its second line, "the terms to continue.", was cut off).
- **uninstall removes its own staging folder** (`%TEMP%\STMxxxx.tmp`, its script and log) when it succeeds.

**Evidence scope for v313.** *The pinned v313 package (the setup committed with these notes - its hash is in
`Sutram-Setup.sha256`, which a setup cannot carry inside itself) passed the Linux gates, the byte-for-byte guard
against v312 and the Windows compiler under Wine; it has not been installed, run or uninstalled on Windows, and
untested guarantees remain unclaimed.* What v313 does **not** claim: the licence label drawn on Windows (under
Wine it shows both lines); the staging folder gone after a real uninstall (read from the code and gated, not run);
the 21,829-term statement on Windows; anything the v312 and v311 native runs did not establish (below); the
compare-then-delete race under another writer.

**Evidence scope for v312, on Windows.** *The pinned v312 package (`5cca529c...`, source `06324ce`) passed the
reported Windows first-contact checks on one existing user account (Windows 11 Home build 26300, not elevated):
the em dash as one U+2014, CR LF line ends with the text equal to the licence source, the Sanskrit and Hindi lines
visibly rendered, no uninstall window, the empty `.sm` key and its parent removed, PATH restored, one canonical
installation with 657/657 hashes, the variable and global 20,000-term refusals and 10,000-term controls, and 322
suite cases; two acceptance findings were recorded (the clipped instruction label, the surviving uninstall
staging folder - both fixed in v313), and untested guarantees remain unclaimed* (`Windows-to-Sarvam/win-v312-2026-11-08/`).
**The licence rendering is verified on native Windows and not under Wine:** Wine draws the Devanagari and Tamil
lines in the licence box as empty boxes, a Wine font limitation. Not established by that run: a new machine or
user profile, font coverage on other machines, the suite time (one sample, 24% slower than v311's, not attributed),
a whole-machine cleanup guarantee, the out-of-memory exit, the race.

v312 was v311 plus (R143): the expression check's budget set to 65,536 (reachable; superseded in v313), the
licence decoded as UTF-8 with CR LF line ends, the uninstall without a console window, and no empty `.sm` key.

v311 was v310 plus (R142):
- **the expression check is inside expression code generation.** `gen_expr` generates without a check of its own
  only inside a statement or module-level initializer the check has already walked; anything reaching it another
  way is checked there, its own value counted as a number. A new entry that forgets the check can refuse more; it
  cannot let a slice through. The R137 gate builds two compilers whose entries forget it and shows every refusal
  still refused.
- **the check has its own stack.** It shared one with the analysis that works out what a `prakriya` returns, and
  when that analysis ran for the first time in the middle of the check it overwrote the nodes still to be checked:
  on v310, `likha(((m[0:2] * 1) * 1) + (f() + zero))` in a `prakriya` defined before `f` compiled and printed an
  address, and ChatGPT's stale-read probe written the same way read 7 while `k[0]` was 99. Both are refused now.
- **the installer deletes nothing on the strength of a name:** a stopped run's copy is deleted only when the copy
  already kept under its `_superseded` name has the same full SHA-256; a different one stops the run and both are
  kept. And (from the Windows branch, PR #68) a file staging reused that changed or disappeared before it was
  published is refused before anything is moved.

**What the native Windows runs of v311 establish** (`Windows-to-Sarvam/win-v311-2026-11-07/` and
`win-v311-acceptance-2026-11-07/`, the exact setup `134fae95...`, one existing Windows account - **not a new
machine, VM or user profile**): the v310 superseded-copy data loss refuses and keeps both files; the installer
fixtures pass (19 boundary, 14 reuse, 7 lock); concurrency, an edit during publishing, the suffix file and an
ordinary interrupted retry; a default install, a first program written in Notepad, reinstall, four IDE scenarios,
the add/XOR and global-initializer refusals, nesting to 1022, and 322 suite cases. **What they do not:** the
out-of-memory exit (not rerun on v310 or v311), the walk budget (the nesting probe measured the parser), the
mutant compilers, a byte-for-byte setup built on Windows, a clean uninstall (it left the empty key and a
PowerShell window, fixed in v312 and not yet seen natively), a new user profile, and the compare-then-delete race
under another writer, which no run has tested.

The native measurements below are of v309 unless they say otherwise.


Measured, with where:
- **On native Windows, on the tested v309 commit** (ChatGPT's v309 run, 7 November, `Windows-to-Sarvam/win-v309-2026-11-07/`):
  - the out-of-memory exit: 32 of 32 runs (448-640 MiB, `mandapa` and touched pages at 64 MiB) exit 1 with the
    message and no stack overflow;
  - the slice-arithmetic refusals: 7 of 7;
  - the native suite: 322 pass, 0 fail;
  - install: an upgrade, a clean install, and a run interrupted early, late, and with a user's edit, each retried;
    one canonical `sutram` in a new terminal; Windows shows `1.0.309`.
- **On Linux and under Wine:** every gate in `tools/gates.sh`; the guard (every program compiled before and after
  each change, the bytes compared). The Windows compiler under Wine produces the Linux PE, byte for byte.

**Not closed, and not claimed:**
- **A slice is refused in every form the gates test** (the R133, R134 and R137 gates); **that is not a proof that no
  other form exists.** The check covers every operator in one place, and from v311 every path into expression
  code generation (an expression outside a checked statement or initializer is checked where it is generated). It
  covers every statement and, from v310, the one expression path outside a statement, the module-level `vitti` initializers
  (`vitti leaked = make_kosh() + 0` held an address on v309, ChatGPT R208 C1; a `kosh` bound to a module `vitti`
  there was not refused either). The language has no other: no constants, no field defaults, no default
  arguments, no module-level `kosh` or `mala`.
- **The out-of-memory exit** is measured at those limits on one machine. Other allocation failures, a failed
  start-up reserve on Windows, and teardown in general are not.
- **The installer** is safe to interrupt and retry, file by file. It is not one atomic step: the shortcuts,
  registry and PATH are finished by a rerun, not rolled back. Its stops between two journal records are not yet
  tested natively: `tests/windows/test_installer_boundaries.ps1` (R142) stops the engine's own staging and
  publishing code before every record and rename, with and without a torn last record, and reruns it - written for
  the native run, not yet run. Acronis Active Protection suspended the v306 and v307 upgrades; the measured upgrades of the
  v309-era packages were not suspended. **Whether a security product suspends an installer is that product's
  decision, and no cause is established.**
- **The package:** from R140 one exact package, its manifest checked against the embedded ZIP. A package built on
  Windows with `windows/native-installer/build-installer.ps1` has LF text like the Linux build, but its ZIP dates
  are not fixed. The release package is the Linux build.
- **The Windows IDE**, the frozen language packs and the items under *Not included* are as described there.

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
  grows.** Nothing checks what the foreign side does with it. **A slice of a `kosh` is not given to one** (v314,
  `E_KOSH_VIBHAG`; v313 passed the slice's descriptor).
- **A slice of a `kosh` is a view of the elements as they are when it is made.** So (`E_KOSH_VIBHAG`):
  - it cannot be kept in a name (`vitti s = k[1:4]`);
  - it cannot be given to a `prakriya` that may grow a `kosh` (it, or one it calls, runs `kosh_kship`);
  - it cannot be given beside another argument that has a call in it (the call could grow the `kosh` first);
  - **it goes through no door a `kosh` may not** (v308, ChatGPT R207): not into a cell or field (`box[0] = k[0:1]`),
    a module `vitti`, another `kosh` (`kosh_kship(h, k[0:1])`), a raw store, nor to an untyped parameter
    (`keep(k[0:1])` with `prakriya keep(x)`) - **and so not through a function value at all**, whose parameters are
    untyped (v306 compiled `f(k[0:1], kosh_kship(k, 8))` and lost the write or crashed, R205-206 S3; v307 refused
    that form; v308 refuses every slice of a `kosh` to a function value). A `vibhag` parameter keeps the slice's
    kind, so forwarding it does not open a door. Up to v307 these printed the old value: the write went to elements
    the `kosh` had left.
  - **a slice is not a number** (v309, after ChatGPT's R207 follow-up S4): no operator takes one (`k[0:1] + zero`
    printed the descriptor's address, and passed to an untyped `prakriya` read the `kosh`'s old elements - 7 while
    `k[0]` was 99 - on v308), nor a condition, a loop bound, an index, a builtin other than `pankti_gan`, a cell or
    raw store, or an untyped or function-value parameter, for a slice of a `mala` too (`E_VIBHAG_ANKA`). A `kosh`
    made a number by a call or `?:` is `E_KOSH_GANIT`, as a bare one was.
  **What a slice is for:** an argument to a `vibhag` parameter of a `prakriya` called by name, `pankti_gan(s)`, the
  base of `s[i]` and `s[a:b]`, and a name of its own for a `mala`'s slice (`vitti t = m[1:3]`). Passed on directly,
  to a `prakriya` that only reads, it is safe: `yog(k[1:4])`. In `k[lo:]` the end is the length after `lo` is
  evaluated (v305). **These rules are what the gates test** (the R133, R134 and R137 gates: every escape and every
  expression form found so far, each refused); they are not a proof that no other form exists.
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
    printed nothing (native Windows, 64-640 MiB job commit limits). Under v306 two cases printed the message and then
    died with `STATUS_STACK_OVERFLOW` (512 MiB, and a `mandapa` at 64 MiB: the commit left after the failure was too
    little for the thread's stack to grow while exiting); **from v308 the runtime keeps 64 KiB of commit from the
    start and gives it back before the message**, so the exit should have room - **not yet measured natively**
    (`tests/windows/test_oom_headroom.py`). If that reserve cannot be had at start, the exit is v307's, without it.
    **It is fatal:** there is no recovery, and no
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
  - **an installation is a journaled transaction** (v308, after ChatGPT R207). A folder beside the installation
    (`<folder>.sutram-transaction`, same volume) holds a journal written through to disk before anything in the
    installation changes, the staged files (each logged when its copy starts and ends, and checked by hash) and the
    backups; every file reaches the installation by a rename, so none is ever half-written; a replaced file is
    backed up first; files the new version lacks go to the backup. **A run that stops is finished by the next**,
    which reads the journal. A file that is not what the installer wrote is never replaced: all such files are
    listed, with a way out (move them, or the folder, aside), and nothing in the installation changes. Each file is
    checked again just before it is replaced, and one changed meanwhile is kept and stops the run (v309). One
    installer or uninstaller at a time: a lock file beside the installation is held from the first read to the end
    (v309). A `*.sutram-partial` file (v307's temporary name) is no longer deleted on its name alone (v309). This is
    interruption-and-retry safety, not one atomic step: the shortcuts, registry and PATH are written after the files
    and finished, not rolled back, by a rerun. The backups are removed once the installation is complete;
  - **the stops themselves:** the v303 copy stopped inside file 132 of 657 (left empty) and the v306 same-folder
    upgrade after about 117 files (native, 6 November); both had just deleted the previous installation's files,
    and in the v306 stop Windows reported **every thread of the engine, and the wizard's original threads, suspended**.
    **Acronis Active Protection did it:** its own log records suspending the engine and the wizard at those moments
    (heuristic "Create Delete Full Read", native follow-up, 6 November). The v307 upgrade, which no longer deleted
    the old files first but replaced them one by one, was suspended too (at file 87). Whether v308's staged,
    renamed upgrade is suspended on such a machine is **not yet measured**; a clean install into an empty folder has
    not been suspended in any run. On a machine with such protection, the installer may need to be allowed; A wizard that is itself suspended cannot run
    its 15-minute stop; when the stop does fire, it now writes a line to the engine's log (v308);
  - Windows' list of installed apps shows the compiler's version (`1.0.307`), not `0.1.0` (v307);
  - **its PowerShell scripts are unsigned, and run with `-ExecutionPolicy Bypass`** for that process only. A policy
    set by Group Policy still overrides it;
  - install, an installation stopped and finished, a new terminal, and uninstall are the owner's acceptance test,
    not yet done for v307 (`tests/windows/test_installer_e2e.py` runs them); so is the upgrade over the owner's
    existing v305 installation, with the wizard;
  - the installer's hashes detect corruption, not the publisher.
  - **one exact package** (R140): every text file it carries is LF in every checkout (`.gitattributes`), the build
    writes LF and fixed ZIP dates whatever the checkout did, and the gate checks the embedded ZIP against its
    manifest. A package built from a CRLF checkout had 153 files that differed from the installed copies, and an
    upgrade replaced them all; that upgrade was suspended by Acronis, and the same upgrade from an LF package was
    not - one observation, not an established cause;
  - an upgrade or a retry copies only the files whose bytes change (R140); a late retry no longer stages all 657;
  - its logs are appended with full sharing, and a log line that cannot be written does not stop the installation
    (up to v308's first build, a program reading the log made the engine fail: ChatGPT's v307 fixture).
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
- **v315:** the tree limit's own code (`E_VRIKSHA_SEEMA`); the fold guard; the installer records what it did -
  shortcuts by their bytes, PATH by the entry, the association by its value, the class by what it wrote.
- **v314:** a slice is not given to a foreign function; `--analysis-steps=N` (default 200,000); the analysis limit
  names itself; the desktop shortcut collision and checkbox.
- **v313:** the expression check's budget is the bound a statement the syntax tree holds cannot pass (349,521), so
  it refuses only a compiler defect, and says so; the licence instruction shows both lines; uninstall removes its
  staging folder.
- **v312:** the licence page is decoded as UTF-8 with line breaks; the uninstall shows no console and leaves no
  empty `.sm` key.
- **v311:** the expression check is inside expression code generation, with its own stack; the installer deletes
  a stopped run's copy only on an equal full SHA-256.
- **v310:** module-level `vitti` initializers get a statement's checks (no `kosh` or slice used as a number, no
  `kosh` in a module `vitti`); an expression check that cannot finish refuses (`E_VAKYA_SEEMA`); the installer
  locks before any state read.
- **v309:** a slice is not a number - no operator, condition, bound, index, builtin (but `pankti_gan`), store or
  untyped parameter takes one (`E_VIBHAG_ANKA`), and a `kosh` made a number by a call or `?:` is `E_KOSH_GANIT`;
  the installer locks the folder from its first read, checks each file again before replacing it, and no longer
  deletes `*.sutram-partial` files on their name.
- **v308:** a slice of a `kosh` goes through no door a `kosh` may not - cells, fields, module `vitti`, another `kosh`,
  raw stores, untyped and function-value parameters - by one predicate (ChatGPT R207); the Windows out-of-memory exit
  keeps 64 KiB of commit in hand, so it no longer overflows the stack after the message; the installer is a
  journaled transaction beside the installation; the wizard logs its 15-minute stop.
- **v307:** a `kosh` slice given through a function value beside an argument with a call is refused, as for a
  direct call (ChatGPT R205-206 S3: v306 lost the write or crashed); the Windows runtime stops with a message if its
  memory handler cannot be installed (R205-206 W1); an interrupted installation is finished by the next run, the log
  names each file, and Windows is told the real version.

How these defects were found - a second platform, testing, an independent attack and reading each found some the
others missed - is in `docs/reports/HOW-DEFECTS-WERE-FOUND.md`.
