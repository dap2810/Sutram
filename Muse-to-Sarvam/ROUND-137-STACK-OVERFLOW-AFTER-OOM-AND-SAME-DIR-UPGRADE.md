# Sutram — ROUND-137: why 640 passes and 512 fails, and what the same-directory path does

**Base:** main at v306 (`da349daf`) · **Compiler:** v306, unchanged since R134
(`8edb8b90` → `da349daf` is docs, briefs, and deliverables only — no `src/`
change) · **Deliver into:** `Muse-to-Sarvam/`

## Verdict up front

The v306 native Windows run is real evidence, and it is mostly good: clean
install in 8.05 s, 657/657 payload hashes matching, native suite 322 PASS with
no FAIL, the IDE clearing old output on a refused load, the Save safeguard
holding. Two things remain, and both are now reproducible:

1. **The OOM refusal crashes after printing — B3 at 512 MiB and `mandapa`
   at 64 MiB, each 6/6.** The message alone is insufficient to count a
   refusal as passing. The mechanism is established below (a second fault,
   on the thread's stack, during `ExitProcess` teardown) — and so is the
   boundary of what the source explains: it does **not** determine why 512
   crashes while 128, the same shape of fault, does not.
2. **The same-directory upgrade stalls during copy — reproducible on demand.**
   The installer does not refuse it; the source explicitly permits it. The
   stall is inside `Copy-StagedFiles`, between files 101 and ~117 — but the
   copy loop contains no wait, retry, or lock-acquisition that could block
   for minutes, and every thread of both the child and the wizard was
   observed suspended. The mechanism is not in the installer's code.

The 15-minute timeout was never observed (the owner ended the stalled wizard
first). It remains untested.

## WS1 — the asymmetry is the clue

**512 MiB crashes after the message. 640 MiB refuses cleanly. 64, 128 and 256
all refuse cleanly.** The pattern 64-pass, 128-pass, 256-pass, 512-crash,
640-pass, 768-success is unusual enough to identify the cause — and it does,
up to a point. Here is the mechanism, derived from the source and measured
where the source can be measured.

### What size is the allocation at each limit?

The growth routine (`r127_emit_grow`, `src/r65_arena.inc:577`) doubles the
capacity (`newcap = cap ? cap*2 : 4`, `src/sutram_compiler.asm`, the
`kosh_kship` emission). A big growth takes a region of
`max(2 * new, R101A_REGION)` reserved (`R101A_REGION` = 64 MiB); if the new
size still fits the current region (`new <= [d+8]`) the growth is **in place
— nothing moves, nothing is copied**. Only a growth past the region moves,
copying element by element (`mov rax,[rsi+rcx*8]; mov [r10+rcx*8],rax`) with
no stack use, and the old region is given back after the copy. `rt_veh`
commits up to 64 KiB per fault (`min(RegionSize, 64 KiB)`).

For B3 (100,000,000 pushes, 8 bytes each = 762.9 MiB of elements), the
sequence is:

| Growth to | New region | Copy | In place? |
|---|---|---|---|
| 2^13 (64 KiB) | 64 MiB | 32 KiB | move |
| 2^23 (64 MiB) | 64 MiB (fits) | — | in place |
| 2^24 (128 MiB) | 256 MiB | 64 MiB (2^23 elements) | move |
| 2^25 (256 MiB) | 256 MiB (fits) | — | in place |
| 2^26 (512 MiB) | 1 GiB | 256 MiB (2^25 elements) | move |
| 2^27 (1 GiB) | 1 GiB (fits) | — | in place |

Measured confirmation (`r137_parimana.sm`, Linux v306): `parimana()` after
2^22 / 2^23 / 2^24 / 2^25 elements reads 33,587,232 / 67,141,664 /
134,250,528 / 268,468,256 — each delta is exactly the element bytes
(32 / 64 / 128 MiB), with a constant 32,800-byte overhead. The kosh holds
exactly the pushed elements at each cap; the doubling and the copy points
are as the source says.

So the fault point at each limit is:

| Job limit | Fault point | Faulting instruction |
|---|---|---|
| 64 MiB | the **fill** after the 2^23 in-place growth, at ~8M elements (committed ≈ 64 MiB) | the append store in `kosh_kship` |
| 128 MiB | the **copy** to 2^24 (64 MiB copy; peak = 64 old + 64 new + baseline) | the copy-loop store, near the end of the copy |
| 256 MiB | the **fill** after the 2^24 move, at ~32M elements | the append store |
| **512 MiB** | the **copy** to 2^26 (256 MiB copy; peak = 256 old + 256 new + baseline) | the copy-loop store, near the end of the copy |
| 640 MiB | the **fill** after the 2^26 move, at ~80M elements | the append store |
| 768 MiB | no fault — 762.9 MiB of elements + baseline fits | — |

The copy faults (128, 512) and the fill faults (64, 256, 640) do **not**
separate the crash from the clean refusals: 128 is a copy fault and refuses
cleanly. The asymmetry is not "copy vs fill", and it is not the allocation
size — the 512 copy (256 MiB) and the 640 fill (which passes 512 MiB of
elements on its way to 640) both cross the same sizes.

### Does the handler's own stack use depend on how much was committed?

**No.** `rt_veh` (`win/winrt_blob.asm`) uses a fixed amount of stack: the
operating system's exception dispatch (the CONTEXT record, ~1.2 KiB, plus
the exception record and the dispatcher frames), its own frame (`push rbx;
push rsi; push rdi; sub rsp,96` — 120 bytes), and the call frames for
`VirtualAlloc` / `WriteFile` / `ExitProcess`. About 2–3 KiB total, the same
at every limit and at every fault. It does not grow with the committed
amount.

What depends on the committed amount is whether the stack can **grow**.
The PE header sets `SizeOfStackReserve = 0x100000` (1 MiB) and
`SizeOfStackCommit = 0x1000` (one page). The thread's stack starts with a
single committed page and grows by guard pages as the thread's stack use
deepens — and every guard-page commit draws from the **same Job limit** as
the kosh. So the handler does not use more stack when more is committed;
but the stack's next page can only be committed while the Job limit has
room for it.

### Is there a second fault — a page touched during unwinding that was never committed?

**Yes.** After the message, the only code that runs is `ExitProcess(1)` —
there is no console in the runner's children (stdout/stderr are redirected
to files, stdin is devnull), so `rt_init` reads no console code page and
`.v_nomem` skips the `SetConsoleOutputCP` restore (`ORIGINAL_CP` is 0) and
goes straight to `ExitProcess`. The teardown (`LdrShutdownProcess`, the DLL
detaches, the heap cleanup) needs stack **below** the currently-committed
stack — deeper than the faulting frame plus the exception dispatch — so it
touches the thread's guard page, a page that was never committed. That
commit fails because the Job limit is exhausted, and the operating system
raises **`STATUS_STACK_OVERFLOW` (0xC00000FD)**. `rt_veh` correctly
declines it — it is not `0xC0000005`, and its faulting address is the stack,
which the handler explicitly refuses to commit — so it is unhandled, and
the process exit code is `0xC00000FD`. The message printed; the exit did
not happen. The tester's standard is right: the message alone is
insufficient to count a refusal as passing.

The `mandapa` case is the same shape at a different scale. The program
(`A3-mandapa.sm`) runs 2,000,000 allocations of 64 bytes inside
`mandapa parimita 67108864` (a 64 MiB budget). Without a Job limit it
refuses `E_PARIMITA` at the budget (verified on Linux, `r137_mandapa.sm`:
`Sutram truti [E_PARIMITA]: pankti 2 - mandape parimitat adhikam nirmmitam
na sambhavati (parimitih 67108864 baait)`, exit 1) — the budget check is real
and fires at 1,048,576 allocations. Under the 64 MiB Job limit the commit
fails first: the process baseline (a few MiB) means the commit limit is hit
at ~950K allocations, before the budget. The fault is a scratch-cursor page
touch in the arena, the stack is just `mukhya`'s frame, the handler prints
the message — and the teardown's guard-page commit fails the same way.
(The page-touch control, `A3-nirmmita-touch-pages.sm`, refuses cleanly at
64 MiB — same limit, same handler, same message — so the crash is not
"the handler fails at 64 MiB".)

### The 512 split — where the source runs out

Here is the boundary, stated plainly. The 128-copy fault and the 512-copy
fault are **identical in every variable the source controls**:

- the same faulting instruction shape (the copy-loop store, near the end of
  the copy);
- the same stack depth (`mukhya` + `kosh_kship` + the 24 bytes the growth
  path pushes: `push r8; push r9; push r11`);
- the same headroom modulo 64 KiB (the handler commits 64 KiB per fault;
  the old backings, 64 and 256 MiB, and the limits, 128 and 512 MiB, are all
  multiples of 64 KiB; the baseline is the same binary) — so the headroom at
  the fault, `(limit − committed)`, is the same in both;
- the same handler path (the commit fails, the message prints, `ExitProcess`
  runs).

If the crash were determined by any of those, 128 and 512 would behave the
same. They do not — 6/6, deterministically, serially, after the concurrent
runs were removed. **So the distinguishing variable is not in the compiler's
emitted code or in the handler.** The most likely carriers are outside the
source: the exact Job-visible baseline commit (which sets the absolute
headroom — the teardown needs a whole 4 KiB page, and the baseline's odd
bytes are set by the process image, heap, and stack, not by the compiler),
or the committed stack high-water mark at the fault. Either would explain
why the `mandapa`/page-touch split at the same 64 MiB limit is possible
too (different programs, different baselines) — but neither can be computed
from the source, and I will not present a guess as the mechanism.

The falsifiable next probe, for Claude or the owner on native Windows:
build the same B3 binary with `SizeOfStackCommit` raised (e.g., 1 MiB, so
the stack never needs a guard-page commit during the teardown) and re-run
the 512 MiB case. **If the crash disappears, the mechanism is the stack
guard page. If it persists, it is elsewhere.** And log the Job's
`PeakProcessMemoryUsed` at the fault, to get the exact committed amount —
that number, not the limit, is what the teardown's guard-page commit is
measured against. Until that runs, the crash-after-message is a known,
reproduced, mechanism-shaped defect with one unexplained split — not a
closed item, and not a release blocker on the message alone, but a blocker
on the exit code: a refusal that exits `0xC00000FD` is not a refusal.

## WS2 — and the same-directory upgrade

**The installer does not refuse a same-directory upgrade; the source
explicitly permits it.** The A3 expectation ("installer refuses over
existing install") was wrong about the source's contract, and the Windows
report reconciles it correctly: same-folder upgrade is allowed, a different
folder is refused.

The branch that runs only when the destination already exists is the
**upgrade sequence** in `install-core.ps1`'s main flow — three pieces, all
skipped on a fresh install:

1. **The refusal that does not fire.** `Find-OtherSutram (Join-Path
   $InstallDir 'bin')` excludes this installation's own bin directory
   (`if ([string]::Equals($dir,$own,...)) { continue }`). When the target
   *is* the existing install, the "another Sutram" check passes by design.
   The registry check likewise only throws when the registered directory is
   a *different* directory with a marker.
2. **The ownership guard** (lines 385–403, established in R135 WS2): runs
   only if the previous `payload.manifest.sha256` exists in `$InstallDir`.
   In A3 it passed — the files matched the old manifest.
3. **`Remove-ManifestFiles`** (line ~418): runs only if the previous
   manifest exists. It hash-checks each old payload file, preserves
   user-modified ones, and removes the rest. In A3 it ran and completed —
   the engine log says "Removing files owned by the previous Sutram
   payload." at 21:32:41, then "Copying 658 Sutram files." at 21:32:45.

The three questions about the copy loop, answered from the source:

- **Does it open the destination for write while the existing file may be
  held open?** The loop is `[IO.File]::Copy($src,$dst,$true)` — an
  unconditional overwrite, with no existence test and no lock check. In the
  same-directory upgrade `Remove-ManifestFiles` runs first, so most
  destinations do not exist at copy time — but files **not** in the old
  manifest still exist and are overwritten blindly. `File.Copy` opens the
  destination with `FileShare.None`: if another process holds it, the open
  **throws** — it does not hang.
- **Does it verify a hash after writing, and can that check hang on a
  partially written file?** **No.** There is no post-write hash check
  anywhere in the copy path. `Verify-Payload` hashes the *stage* before
  copying; the guard hashes the *old* files before copying. Nothing hashes
  a destination after writing. The hang is not a post-write check.
- **Does it handle a file that already exists by overwriting, skipping, or
  failing?** **Overwriting, unconditionally** (`$true`). No skip, no fail,
  no branch in the copy loop at all.

**Where the stall is.** The A3 engine log's last entry is `Copied 100 of
658 files; last: docs\_newchapter_en.html` at 21:32:45 (658 = 657 payload
files + the manifest itself). The partial tree held **117 files**. The
snapshot found `docs\reports\EDGE-COVERAGE-30.md` unreadable because
another process held it open — the installer itself, mid-copy (`File.Copy`
holds the destination open with `FileShare.None`). So the copy stalled
inside `Copy-StagedFiles` between files 101 and ~117, with a destination
file open — and the log, which names only every 100th file *after* copying,
cannot say which one. (R135's point stands: the next stall still will not
name its file.)

**But the stall's mechanism is not in the installer's code.** The copy loop
contains no wait, no retry, and no lock-acquisition: `File.Copy` either
completes in milliseconds or throws. Nothing in `install-core.ps1` can
block for five minutes inside that loop. And the thread evidence points
outside the installer too: at 21:38:15 **all 27 threads** of the PowerShell
child (PID 27748) were `Wait / Suspended`, and the wizard's threads (PID
36956) were likewise suspended — a whole-process-tree suspension, which no
code in the installer or the wizard can produce (the wizard only waits on
the child process handle with a 15-minute timeout, then terminates it; it
creates the child with `CREATE_NO_WINDOW` and no redirected pipes, so there
is no pipe deadlock and no console to block on). The Windows report says
the suspension's cause "has not been established" and "does not prove a
product-code deadlock" — I concur, and I do not reclassify it. The hang is
reproducible on demand (run the installer at the existing install folder),
which makes it fixable — but the fix is not in the copy loop's logic. What
the source *does* show is missing, and would have changed the outcome: a
per-file **START** log (so the next stall names the file it stopped on),
and copying to a unique temporary file with hash verification before
publishing (R207's design — so a stall never leaves a half-written
destination open and a retry can resume). The 15-minute timeout was never
observed, so it remains untested — the owner ended the wizard first, and
the orphan child needed separate cleanup.

## WS3 — and the probe that is still unrun

**They have been run — in Round 136, worked and staged, delivered with this
round.** All four of ChatGPT's escape probes reproduce on v306, and
independent testing found four more paths of the same class:

| Probe | Result |
|---|---|
| Cell store (`mala box[0] = k[0:1]`, then grow) | Reproduces — the descriptor pointer persists (`140733170577648`); the R207 write form prints `7` (silent stale write) |
| Untyped parameter (slice to an untyped `x`, callee grows) | Reproduces — prints `77` then `7` (lost write) |
| Untyped return (`keep(x) { nivartanam x }`, then grow + change) | Reproduces — prints `7` then `99` (**stale read — the worst outcome**) |
| Function value (slice to a `prakriya` called through a variable) | Reproduces — small prints `0` then `7`; large exits 139 (SIGSEGV) |
| + global, rachana field, raw `nirmmita` memory | All reproduce — stale reads (`7` then `99`) |
| + `dasham` parameter | Reproduces as a crash — exit 139 (the int→float conversion destroys the pointer bits; indexing faults) |
| + ternary, conditional assignment | Closed (refused `E_KOSH_DVARA` / `E_KOSH_VIBHAG`) |

**Eight escape shapes on v306, one shared cause** (kind 1 is in no refusal
list; every untyped storage is an escape). A stale slice is worse than a
stack overflow, as the brief says — and it is still live. Full detail in
the Round 136 report, delivered in the same push as this one.

## Verification and NOT RUN

- Suite on the `da349daf` binary: **PASS=327, NO-EXPECTATION=4 (331 run)**
  — identical to R134/R135/R136. Compiler unchanged since R134.
- `parimana()` region/element measurements: run on Linux v306
  (`r137_parimana.sm` — deltas exactly the element bytes at each cap).
- Mandapa budget control: run on Linux v306 (`r137_mandapa.sm` — refuses
  `E_PARIMITA` at the budget without a Job limit, confirming the budget
  check is real and the Windows fault is the commit, not the budget).
- Page-touch control: run on Linux v306 (`r137_touch.sm` — prints `done`,
  exit 0).
- **NOT RUN:** Windows execution of any new candidate (no candidate
  exists); the `SizeOfStackCommit` probe and the `PeakProcessMemoryUsed`
  logging (Windows-only, for Claude/the owner); the 15-minute timeout
  (never observed); Wine (none on this machine); the full `tools/gates.sh`.

## Files delivered

- `Muse-to-Sarvam/ROUND-137-STACK-OVERFLOW-AFTER-OOM-AND-SAME-DIR-UPGRADE.md`
  — this report.
- `Muse-to-Sarvam/r137.json` — the structured results.
- `Muse-to-Sarvam/r137_parimana.sm`, `Muse-to-Sarvam/r137_mandapa.sm`,
  `Muse-to-Sarvam/r137_touch.sm` — the Linux controls for WS1.
- **Round 136 delivered in the same push** (its push approval timed out
  on the first attempt; nothing had landed — verified `origin/main` was
  still `218fb84e` before retrying, and ROUND-137 had landed in the
  meantime, so both rounds ship together): `ROUND-136-FOUR-ESCAPE-PROBES.md`,
  `r136.json`, and its 13 probe files.
