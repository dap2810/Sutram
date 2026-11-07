# R136-00 — WS1: all of Muse's escape programs - eight shapes, thirteen programs - are refused by v308, which landed after this round's base (v307). The one-predicate fix of R134 already covers the class. The gate now runs every one: v306 fails all sixteen escapes, v308 none. WS2: the source cannot explain 512-versus-128; the run-to-run split at 448 MiB says the deciding number is outside the compiler's code. A new Windows test measures it, and v308 is built so that it should not matter. WS3: no - removing the mass delete did not change the trigger. Acronis's own log shows it suspended the v307 upgrade too, during per-file replacement. Also fixed: the engine's logging failed when another program read the log.

## Release line

```
gates: 73 PASS / 0 FAIL / 1 NOT-RUN   (sh tools/gates.sh, Linux, Xvfb; NOT-RUN = Windows execution)
suite: NO-EXPECTATION=4  PASS=327  (331 run)
Sutram 1.0 (v308) - sampurna sutra      (compiler unchanged since 2625083)
```

- **Commit on `main`:** the commit carrying this file (SHA in my chat report).
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **The guard: NOT re-run, because no compiler byte changed.** `src/`, `win/`, `lib/`, `lang/` and the compiler and linker binaries are as at `2625083`. This round adds 13 test programs, changes the installer engine's logging, and changes docs. The v307 → v308 guard in R134-00 stands.
- **Installer rebuilt (engine logging, release notes):** `PASS payload v308 = compiler v308`, `Sutram-Setup.sha256` = `a8446b039b100aaf23830bff8f16f4851c1c1b9b11cff1e82b56af85e622a13d`. **This replaces R134-00's `e7370868...`;** the compiler inside is the same. Self-test exit 0 under Wine.

**Not done:**
- **The OOM measurement (WS2) is a Windows test, NOT RUN here.**
- **No PowerShell ran here.**
- **I have not built the folder-swap upgrade proposed in WS3** - it waits on v308's native result.

## WS1 - the class, closed: Muse's eight shapes on v306, v307 and v308

Muse's thirteen programs (`Muse-to-Sarvam/r136_*.sm`), copied unchanged into `tests/r134/escape/m_*.sm`, compiled and run here:

| shape | program | v306 | v307 | **v308** |
|---|---|---|---|---|
| mala cell | `ws1_cell_minimal` | compiles (prints an address) | compiles | **E_KOSH_VIBHAG** |
| mala cell | `ws1_cell_write` | compiles; **7** (lost write) | compiles; 7 | **E_KOSH_VIBHAG** |
| untyped parameter | `ws1_untyped_param` | `77 7` (lost write) | `77 7` | **E_KOSH_VIBHAG** |
| untyped result | `ws1_untyped_return` | `7 99` (**stale read**) | `7 99` | **E_KOSH_VIBHAG** |
| function value | `ws1_funcval_small` | `0 7` | E_KOSH_VIBHAG | **E_KOSH_VIBHAG** |
| function value | `ws1_funcval_large` | **SIGSEGV** | E_KOSH_VIBHAG | **E_KOSH_VIBHAG** |
| module `vitti` | `ws2_global` | `7 99` (stale read) | `7 99` | **E_KOSH_VIBHAG** |
| `rachana` field | `ws2_field` | `7 99` | `7 99` | **E_KOSH_VIBHAG** |
| raw `nirmmita` memory | `ws2_rawmem` | `7 99` | `7 99` | **E_KOSH_VIBHAG** |
| `dasham` parameter | `ws2_dasham_param` | **SIGSEGV** | SIGSEGV | **E_KOSH_VIBHAG** |
| `dasham` parameter | `ws2_dasham_diag` | prints the address as a float | same | **E_KOSH_VIBHAG** |
| (control) `?:` | `ws2_ternary` | E_KOSH_DVARA | E_KOSH_DVARA | E_KOSH_DVARA |
| (control) assignment in a block | `ws2_cond_assign` | E_KOSH_VIBHAG | E_KOSH_VIBHAG | E_KOSH_VIBHAG |

**This round's base was v307, and v307 was not closed** - Muse and the Windows v307 run are right: the cell, untyped-parameter and untyped-result shapes stayed open. My R133 "closed" was the claim of a fix for the paths I had tested. **v308 (R134, pushed before this round was read here) is the class fix you describe:**
- **One predicate,** `r134_holds_kosh`. It is true for a `kosh`, a slice of one, a slice of a slice name or `vibhag` parameter, or such a name.
- **It is the only check:** all seven door sites call it, and `r126_is_kosh_value` is called from nowhere else.
- **Muse's general rule - "every untyped storage is an escape" - is what it enforces:**
  - a cell, a field and raw memory (`r126_check_assign`, `r126_check_writemem`);
  - a module `vitti`;
  - any parameter that is not `kosh` or `vibhag` (untyped, `dasham`, function values: `r126_check_untyped_arg`);
  - a builtin's other arguments;
  - a phal result.
  - The untyped *result* shape is closed one step earlier: the slice can no longer reach the untyped parameter it would come back through.

**The gate now holds the class.** `R134 one predicate` runs 21 programs (my 8 and Muse's 13) and checks the single call site:
- **v306: 16 failed - every escape;**
- v307: 14;
- **v308: 0.**

**No shape is left open that I know of.** Not covered, as before, are foreign (`--ffi`) calls, where the release notes state that a foreign borrow expires at growth.

## WS2 - why 480-512 MiB and not 128: not determinable from the source; here is the measurement

**Muse's account of the mechanism agrees with mine** (R135-00): the commit limit that refused the page leaves the thread's stack no commit to grow while `ExitProcess` runs, so the guard-page commit fails and Windows raises `STATUS_STACK_OVERFLOW`.

**And Muse is right that the source cannot pick 512 over 128.** At both, the fault is the copy-loop store, the stack depth is the same, and the handler path is the same. Everything the program commits is in 64 KiB steps, so the headroom modulo 64 KiB is the same too.

**The new native data settles where the deciding variable lives** (v306 follow-up and v307, three runs per limit):

| limit (MiB) | 448 | 480 | 512 | 544 | 576-640 | 64 (mandapa) |
|---|---|---|---|---|---|---|
| `0xC00000FD` | **2 of 3** | 3 of 3 | 3 of 3 | 0 of 3 | 0 of 3 | 10 of 10 |

**448 MiB is split 1-2 across identical runs of the same binary.** So the outcome is not a function of the limit and the program alone. Something that varies between runs sets the headroom at the peak. The compiler's code does not vary. What does:
- the commit Windows itself takes for the process - loader and thread-pool worker threads, each with its own stack, created asynchronously;
- the heap;
- the console.

**Muse's two probes are the measurement,** and I have built them as one Windows test, `tests/windows/test_oom_headroom.py`:
1. **The headroom.** `tests/windows/job_runner.py` now records the job's `PeakProcessMemoryUsed` after every run, and `limit - peak`.
   - **Prediction:** `0xC00000FD` exactly when that headroom is under the few pages the exit's stack needs.
   - The 448 split should show up as two headroom values.
2. **Muse's stack-commit probe.** The same binary with `SizeOfStackCommit` raised to 1 MiB in its PE header, so the stack is committed at start and the exit never grows it.
   - **Prediction for a v307 binary:** no `0xC00000FD` at any limit.
   - **Checked here:** the patched binary loads and runs under Wine (prints `100000000`).
3. **The test runs both variants** at 448/480/512/544/640 MiB (B3, 3 runs each) and 64 MiB (`mandapa`, 5 runs).
   - Run it once with a v307 compiler: it should reproduce the crash, and show the headroom and stack-commit results.
   - Run it once with v308: **v308's runtime releases a 64 KiB reserve before the message, so the headroom at the exit is at least 64 KiB, and the prediction is no `0xC00000FD` without any header change.**

**What would refute this:** a crash with large headroom, or a crash with the stack committed - then the second fault is not the stack's, and the explanation is wrong.

## WS3 - did removing the mass delete change the trigger? No. The evidence is Acronis's own log.

- **v306** (deletes the old payload, then writes): suspended at about file 117, and again at file 107 in the follow-up. **Acronis Active Protection's log** records suspending both the engine and `Sutram-Setup.exe` at those moments, under its heuristic **"Create Delete Full Read"**.
- **v307** (no mass delete; each old file is deleted just before its replacement is moved in): **suspended at file 87**, both processes, by the same heuristic. **So it is not the mass delete as such.** Deleting files one at a time while creating their replacements matched it too.
- **Installs into an empty folder** (v305 repair, v306 A4, v307 clean): **never suspended.** They create and read files but delete nothing in the installation. The v307 interrupted-and-finished install was not suspended either; it began in an absent folder, so its finishing run replaced only the files the stopped run had written.
- **v308** (not yet run natively):
  - **no file in the installation is deleted:** old files are *renamed* into the transaction's backup folder, and the new ones are renamed in;
  - **but it still reads every old file in full** (the ownership hash), **creates** the staged copies, and replaces each file by rename.
  - **Whether Acronis's heuristic counts a rename-replace as its "Delete", I cannot know from here.** Read-original, write-new, rename-or-delete-original is also exactly what ransomware does. **My expectation: v308 may still be suspended. Only a native upgrade with Acronis on says.**
- **If it is, the clean-install observation points to the design that avoids the pattern.** An upgrade becomes a clean install into a new sibling folder (`<folder>.sutram-new`, same volume), then two directory renames swap it into place.
  - Files the user added inside the old folder are moved across by name.
  - The old folder becomes the transaction's backup.
  - **The cost:** removing that old folder later is itself many deletes. It would have to be removed lazily, by the next installer or by uninstall, or kept.
  - **I have not built this.** It waits on v308's native result, because building it blind would be guessing at a vendor's heuristic.
- **In all cases** v308's journal makes a suspended-then-killed upgrade finishable by the next run, and the release notes now say plainly that Acronis suspended the v306 and v307 upgrades, and that on such a machine the installer may need to be allowed.

## Also fixed: logging that failed when someone read the log (ChatGPT's v307 fixture)

ChatGPT's v307 fixture shows that Windows PowerShell 5.1's `Add-Content` fails while another process holds the file, even a reader that shares everything. The engine logged with `Add-Content` under `ErrorActionPreference = Stop`, so **a log viewer could fail the install.**
- **Now `Log`, in the engine and in the uninstaller, appends through a `FileStream`** shared read, write and delete, retries twice, and **never throws.**
- The journal is unaffected: it has its own write-through stream, shared for reading.
- **Gate `R134 install transaction`** gained a check for it (20 checks, 0 failed).
- `Add-Content` remains only for one line of the state file, which nobody reads during installation.

## For the Windows round, in order

1. **`tests/windows/test_oom_headroom.py`**, once with a v307 compiler and once with v308 (WS2).
2. **The v308 same-folder upgrade with Acronis on, unchanged** (WS3): is it suspended? If yes, the Acronis log line, and the engine log's last `START`/`DONE`/`PUBLISH` line. Then run the installer again with Acronis's permission: the journal should finish it.
3. **The v308 escape programs** (any of `tests/r134/escape/`): all refused (WS1).
4. The rest as in R134-00: the e2e test on a clean machine, `test_commit_oom.py`, the suite, the IDE.

Evidence: `Claude-to-Sarvam/evidence-r136/`.
