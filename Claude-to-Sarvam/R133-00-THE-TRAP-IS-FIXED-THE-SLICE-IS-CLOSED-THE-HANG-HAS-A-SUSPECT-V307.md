# R133-00 — v307. WS1: an installation that stops part-way is now finished by the next run instead of refused, and the log names every file before copying it. WS2: the file the copy stopped in is named. Nothing about the file explains it. The leading suspect is the owner's anti-ransomware driver, set off by the engine deleting 643 files and then writing 131 in four seconds; that is not confirmed. v307 removes the mass delete either way. WS3: ChatGPT's function-value slice reproduces on v306 (a lost write, and a SIGSEGV) and is closed. I also closed ChatGPT's W1: Windows' memory handler registration was never checked.

## Release line

```
gates: 72 PASS / 0 FAIL / 1 NOT-RUN   (sh tools/gates.sh, Linux, Xvfb; NOT-RUN = Windows execution)
suite: NO-EXPECTATION=4  PASS=327  (331 run)
Sutram 1.0 (v307) - sampurna sutra
```

- **Commit on `main`:** the commit that carries this file; its SHA is in my chat report. Base: `5bd58ae` (v306).
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Installer:** `PASS payload v307 = compiler v307 (... the wizard has no version of its own ...)`, `Sutram-Setup.sha256` = `cbbfd0a66c0a9728c3fd88096631462430c0185cd8c6738964d5b885253e7481`, `--self-test` exit 0 under Wine.
- **THE GUARD, v306 (`5bd58ae`) → v307, 747 programs, compiled the ordinary way before and after, bytes compared:**
  - **Linux ELF: 584 byte-identical, 153 refused identically, 0 DIFFER, 10 new.** The 10 new programs are the R133 probes. **No existing program is newly refused** by the function-value rule.
  - **Linux PE: 0 identical, 153 refused identically, 584 DIFFER, 10 new** - every PE carries the runtime, which changed (W1).
  - **Run old and new under Wine: all 584 the same output and exit, 0 changed.**
  - **The Windows compiler (v307 `sutram.exe`) under Wine: = the Linux PE output for all 747 (585 identical, 162 refused by both), 0 differ.**
- **New gates:**
  - `R133 indirect slice`: 10 checks; v306 fails 5.
  - `R133 interrupted install`: 16 checks; v306 fails 14.
  - `R133 handler registration`: 3 checks, under Wine.

**Not done, said plainly:**
- **No PowerShell ran here** (none available). The engine changes are checked by reading and by the static gate.
- **The Windows end-to-end test is NOT RUN here.** `tests/windows/test_installer_e2e.py` now stops an install at file 132 and runs it again.
- **The hang's cause is not established** (WS2).
- **Native Windows execution of v307 is the owner's.**

## WS1 - the trap

**What a stopped installation left (the owner's folder before the repair):**
- the previous installation's manifest;
- 131 files of the new payload;
- one empty file.

**Every later run compared those files with the old manifest and refused: "a user file".** Your three requirements, and the marker you named:

| requirement | v307 (`windows/native-installer/install-core.ps1`) |
|---|---|
| **a marker written at the start, deleted at the end** | **`payload.pending.sha256`** - the manifest of the payload being installed. It is the first change to the folder and is removed only after the state, registry and shortcuts are written, just before `Installation complete`. It records *which* files are the installer's, not only that an install was running. |
| **recognise a partial install of its own making, and complete or replace it** | With the pending record present, the next run says `A previous installation stopped part-way ...; this run finishes it.` and does. These checks no longer refuse such a folder: "the selected folder is not empty", "ownership metadata is incomplete" and "the uninstaller has been modified". It removes unfinished copies, and the files the stopped run wrote that the new payload does not have. **Running the installer again is the "complete" choice.** For an upgrade that stopped, uninstall is the "remove" choice, and it now removes the pending installation's files too. A first install that stopped before its marker was written has no uninstaller yet; running the installer again is the way out of it. |
| **the guard must not fire on a file the installer wrote and did not finish** | A file is the installer's own if it matches the previous manifest, **the pending one**, or **the new payload byte for byte**. On the owner's machine all 131 files match the v303 payload, which would have been the pending record. Only a file matching none of the three is refused, as "changed since it was installed" (not "a user file"). |
| **a file never left half-written under its real name** | Each file is copied as `<name>.sutram-partial`, then moved into place. v303 left an empty `PROJECT-OVERVIEW.md` that no manifest could match. |
| **the log names the file it stopped on** | `Copying 132/657: docs\rounds\PROJECT-OVERVIEW.md` is written **before** that file is copied. With the 15-minute stop, the log's last line is the file. |

**And the order changed.** v303-v306 deleted every file of the previous payload first, then wrote the new ones. **v307 overwrites in place, and after the copy deletes only the files the new payload no longer has.**

**Also:** Windows' list of apps now shows the compiler's version (`1.0.307`, from `sutram --version`), not `0.1.0`. And `windows/native-installer/README.md` no longer says the scripts are blocked under Restricted/AllSigned. Since v306 they run with process-scoped `Bypass`. A Group Policy setting still overrides that; that is ChatGPT's correction.

**How it is checked:**
- **Linux:** gate `R133 interrupted install`, 16 checks: the order of the writes, the three-way ownership rule, the partial-copy rename, the per-file log line, the uninstaller, the version, and that the setup embeds these scripts. **On v306's scripts it fails 14 of 16** (the two it passes are the embed checks).
- **Windows (NOT RUN here):** `tests/windows/test_installer_e2e.py --i-understand-this-installs` now first starts an install, kills it as soon as its log says `Copying 132/`, checks that `payload.pending.sha256` is there, then runs it again. It must exit 0, log completion and leave no pending record or partial copy. Then it does the new-terminal and uninstall checks as before.

## WS2 - the hang: file 132 is named, and it is not the clue

**Does the copy loop write file by file?** v303's did not; it was one `Copy-Item -Path <stage>\* -Recurse`. But it copies in name order, and the owner's folder shows exactly how far it got (ChatGPT's snapshot, against the v303 payload):
- `assets\` 1 of 1;
- `bin\` 48 of 48;
- `docs\` 82 of 118, up to `docs\rounds\PLAN-TO-FINISH.md`;
- **then `docs\rounds\PROJECT-OVERVIEW.md` created and left empty (0 bytes), at 18:35:34.979;**
- nothing after: `examples\`, `lang\`, `lib\`, `win\` and the root files have 0 of their files.

**File 132 is `docs\rounds\PROJECT-OVERVIEW.md`: 7,633 bytes of Markdown, an ordinary name that sorts where expected, no line over 458 characters.** The file before it was the 705 KB changelog archive, and it copied. **Nothing about the file explains the stop.** So the clue is not the file; it is what happened around it.

**Was there a per-file step that can block?** In v303's engine, the per-file steps came before the copy:
- the ownership check: a `Get-FileHash` of every existing target;
- the reparse check: `Assert-NoReparsePath` for every target.

Both ran, and the log reached the next line. During the copy, the engine runs nothing per file - `Copy-Item` does all of it. So it blocked inside `Copy-Item`, after creating the file and before writing it. That is the point where a file-system filter driver intercepts a write.

**The timeline from the v303 log (`Windows-to-Sarvam/win-v303-2026-11-06/install-at-stop.log`):**

```
18:35:31  Removing files owned by the previous Sutram payload.     <- 643 files deleted
18:35:34  Copying Sutram files.                                   <- 131 files written in under a second
18:35:34.979  docs\rounds\PROJECT-OVERVIEW.md created, never written; nothing after
```

**The leading suspect, not confirmed: the owner's anti-ransomware.**
- This machine's PATH carries `Acronis\FileProtector` and `FileProtector64`: Acronis's file-system filter, the one behind its Active Protection.
- Anti-ransomware tools watch for exactly this behaviour - one process deleting hundreds of files, then writing hundreds - and can hold the process while it decides, or until someone answers it.
- **It fits every observation:**
  - the stop came seconds after the mass delete;
  - it came inside a write;
  - PowerShell stayed open, blocked rather than failed (a failure throws, and the log would say `ERROR:`);
  - the repair's install into an **empty** folder (no deletes) copied all 657 files in 15 s;
  - the v305 runs refused before deleting anything.
- **It does not prove it.** A suspended process and a slow scan look the same in these logs.

**How the owner can settle it, in two minutes:** open the Acronis Active Protection activity log (or Windows Security's protection history) for **6 November 2026, about 18:35**, and look for `powershell.exe`. If an entry is there, that is the cause.

**v307 removes the trigger either way.** An upgrade no longer deletes the previous payload first; it overwrites in place and deletes only the few obsolete files. **If something still stops the copy, the log now names the file, the wizard stops after 15 minutes, and the next run finishes the job.**

## WS3 - ChatGPT's function-value slice: reproduced, closed

**Reproduced on v306** (`tests/r133/indirect/`, built and run here):

| program | v306 | v307 |
|---|---|---|
| `s3small`: `vitti f = badal; likha(f(k[0:1], kosh_kship(k, 8))); likha(k[0])` | **compiles; prints `0`, `7` - the write went to the abandoned buffer** | `E_KOSH_VIBHAG` |
| `s3big`: the same with a 64 MiB region | **compiles; SIGSEGV** (exit 139) | `E_KOSH_VIBHAG` |
| `st1`: `s3small` as a statement call | compiles; prints `99` (by its argument order) | `E_KOSH_VIBHAG`, as the direct statement call is |
| `ind_fv_arg`: the growth inside a direct call in the other argument | **compiles; `0`, `7`** | `E_KOSH_VIBHAG` |
| `alias_sl`: the slice taken from `vitti b = k` | **compiles; `0`, `7`** | `E_KOSH_VIBHAG` |
| `safe1`: `f(k[0:1], 5)` - nothing beside it that can run | `0`, `99` | **`0`, `99`** (still allowed: the write goes through) |
| `s3small_direct`, `s3big_direct`, `ind_wrap` (direct controls) | `E_KOSH_VIBHAG` | `E_KOSH_VIBHAG` |
| `ind_k`: a whole `kosh` to a function value | `E_KOSH_DVARA` | `E_KOSH_DVARA` |

**ChatGPT's trace was right in each step.** `r129_check_call` returned at once for an indirect call (`r23_call_is_indirect`), and `r126_check_untyped_arg` lets slices through (kind 1).

**The fix (`src/sutram_compiler.asm`, `r129_check_call` `.unknown`).** For a call through a function value - and, in an expression, a call to a name with no Sutram definition, such as a foreign function - a `kosh`-made slice beside an argument with a call in it is `E_KOSH_VIBHAG`. **Why the rule is the argument-order one, not "refuse every slice to a function value":**
- such a callee can reach a `kosh` only through its arguments;
- a whole `kosh` is never given to one (`E_KOSH_DVARA`, R126 - `ind_k`);
- nor can one sit in a module `vitti` (R127).

So the callee itself cannot grow the `kosh` the slice came from, and the only remaining hazard is another argument running first. **ChatGPT's alternative, refusing every slice at an unknown boundary, would also refuse `safe1`, which is correct code.**

**Not covered, and said:** a foreign function called as a statement takes another path (`r33_gen_foreign_funcall`) before this check. Foreign calls are outside the slice promise anyway: the release notes say a foreign side's borrow of a `kosh`'s elements expires when the `kosh` grows.

**ChatGPT's second point, `r129_may_grow` skipping unresolved callees:** the same reasoning holds. An unresolved call inside a `prakriya` cannot be given that `prakriya`'s `kosh`, so it cannot grow it. **I left it as it is and wrote the reason here.** If a new way to give a `kosh` to an untyped call is ever added, both places must change; the gate's `ind_k` control fails first.

Gate `R133 indirect slice` (10 programs; v306: 5 failed). **The guard: no existing program changes or is newly refused.**

## ChatGPT's W1 - the handler registration (not asked by this round; closed because v307 is a new candidate anyway)

`rt_init` called `AddVectoredExceptionHandler` and did not test the result. Without the handler, the first touch of any reserved page - the arena, every `kosh` region - is an access violation that nothing commits. **v307 tests it.** On NULL it writes `Sutram truti: smriti-prabandhah na arabdhah` to stderr, restores the console code page and exits 1. The path is its own (`rt_init_noveh`), in `rt_init`'s frame, which is now 48 bytes so `WriteFile`'s fifth argument has room. It does not jump into `.v_nomem`, whose frame is different - as ChatGPT warned.

**Tested by injection, as ChatGPT asked.** Windows will not make that call fail on demand, so gate `R133 handler registration` builds a **test** runtime in a scratch copy (`-DR133_FAIL_VEH_REGISTRATION`, the result forced to NULL) and a compiler around it. It runs a 100,000-push program under Wine:
- the shipped runtime prints `100000`, exit 0;
- the test runtime prints nothing to stdout, the message to stderr, exit 1;
- the tree's `win/rtblob.inc` is exactly what its source builds.

**Under Wine, v306's runtime with the same forced failure exited 5 (an access violation) and printed nothing** (evidence: `veh-registration-wine.txt`).

**W2 (the handler commits any private reserved page, not only Sutram's) is stated, not changed.** The release notes now say the handler does not know which reservations are Sutram's, and that a raw or foreign pointer is outside the promise.

## The release notes (ChatGPT's corrections)

Applied:
- "no runtime, no dependencies" → native executables with their support code embedded, no separate runtime or VM, using the platform's system interfaces;
- the Linux out-of-memory comparison → a Windows job commit limit and a Linux address-space limit are different resources, and overcommit can end a program at touch;
- the out-of-memory message is fatal, with no recovery or atomicity promise, and it applies after the handler is installed;
- the handler's limits (W2);
- the Wine paragraph's "native Windows has not been run" → native v305 runs exist;
- the slice rule through a function value;
- the installer: the interrupted install and the version shown.

ChatGPT's full "Not included" paragraph is **not** pasted in: the notes have their own table, which already lists those items. I compared them and found nothing missing that is a feature (threads, closures, generics, checked function-value signatures, unwinding, a debugger, free/GC, slices of `kosh dasham` or outliving their function, mixed-version objects, formal verification, the frozen packs).

## For the Windows round (the owner's), in order

1. **The Acronis or Windows Security history for 6 November, 18:35** (WS2) - two minutes, and it may close the hang.
2. **`tests/windows/test_installer_e2e.py --i-understand-this-installs`** on a machine with no Sutram: the stopped-and-finished install, the new terminal, uninstall.
3. **The v307 wizard over the existing v305 installation** (an upgrade), then a new terminal: `where sutram`, `sutram --version`; and Windows' apps list should say `1.0.307`.
4. `tests/windows/test_commit_oom.py` on v307; the native suite; the IDE refusal.

Evidence: `Claude-to-Sarvam/evidence-r133/`.
