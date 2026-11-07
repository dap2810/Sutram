# ROUND-134 — Does the Windows picture change a conclusion I reached?

**Short answer: yes, in three places — and yes, it changes what I would probe next.**

Base: `8edb8b90` (v306). Method: read the v305→v306 code first (the OOM fix, the
installer engine, the wizard, the IDE, the harness, the new gates), read the native
diagnostic (`9ae1b12`) and the repair (`870acb3`) that landed while v306 was built,
then re-ran on Linux v306 what can be re-run here (suite, the R133 OOM probe, the
R130 installer-engine gate, three new probes below).

One count correction first: the brief says I "attacked the descriptor twice". It was
three times — R129 (attack, v302), R130 (re-verify + sign-off, v303), R131 (attack,
v305). The count does not change the answer, but the record should be right.

## 1. CHANGED — R132 WS2: the PATH mechanism was wrong

My R132 conclusion: the old entry was a **machine** PATH entry (HKLM, written by the
retired NSIS installer), machine PATH is searched before user PATH, so the old
Sutram 1.4.0 won; the new installer could not fix it because removing a machine
entry needs admin/UAC.

**That is wrong, and the measurement that shows it is ChatGPT's diagnostic
(`9ae1b12`, `Windows-to-Sarvam/win-installer-diag-2026-11-06/`):**

- Machine PATH: 48 entries, **none** containing Sutram; exact registry value
  unchanged by the diagnostic attempts.
- User PATH (persisted registry): the canonical `Programs\Sutram\bin` at position 20
  of 21; no machine entry at all.
- Earlier native logs placed **both** old and new Sutram entries in **user** PATH.
  HANG.md says it directly: "a machine entry must not be inferred from the retired
  NSIS recipe."

My error chain, stated plainly: I read the NSIS script (`EnVar::SetHKLM`) and
inferred the machine's state from the recipe, instead of measuring the registry.
The recipe is not the machine. At v303 time the fresh `cmd.exe` listed the old
`AppData\Local\Sutram\bin\sutram.exe` first because within **user** PATH the old
entry came before the new one — not because machine PATH outranked user PATH.

What stands: the defect itself — two compilers installed, order decides which one a
student gets. What changes:

- Reordering within user PATH needs **no elevation**, and putting the new entry first
  would have worked on that machine (Claude's corrected hand-back says exactly this).
  My "needs admin/UAC, which a per-user installer does not have" does not apply here.
- The fix v306 built — detect the other Sutram and refuse, naming it — is still the
  right one, but for the right reason now: refusing leaves one compiler, rather than
  "the installer cannot win against a machine entry".

## 2. CHANGED — R132 WS1: the "hang" has a second cause, and the first is still unestablished

My R132 conclusion: the stall was in or just after `Copy-Item` (the log ends at
"Copying Sutram files."), with the wizard waiting `WaitForSingleObject(INFINITE)`
on a PowerShell that never exits.

What the v305 evidence now measures (`9ae1b12`, two native attempts):

- The installer does **not** hang on v305. It **refuses before copying** — the
  upgrade-manifest check (engine line ~308; the copy log is at line 321) — with
  `ERROR: Upgrade would overwrite a user file; preserve it elsewhere first:
  ...\bin\sutram-link.exe`. The PowerShell child exits by the 10-second observation
  on both attempts; the wizard returns to Ready and shows the failure dialog.
- The refusal reason is the ownership guard: the installed `sutram-link.exe` hashes
  `b6c722e9...`, which matches the **new** package but not the **old** ownership
  manifest (`84d653fb...`). The guard reads "hash differs from the old manifest" as
  "user file". A product file can differ from the old manifest because the payload
  changed — the guard cannot tell those apart.
- The unchanged v305 installer then **completed** into an empty folder (`870acb3`,
  owner-authorised repair): Finish in ~15 s, 657/657 payload files hash-matching,
  bare `sutram` from a new terminal is v305.

So "the installer doesn't complete" has at least **two distinct causes** — the v303
stall and the ownership refusal — and my R132 conflated the reported stall with a
single mechanism. Corrections:

- "It stopped in/just after the copy" was an inference from where the log stopped,
  not a measurement. The v303 stall was seen **once** (by the owner); on v305 it was
  seen **never** (twice refused, once complete). Its cause is **still not
  established** — Claude says so too, and does not claim the v306 changes fixed it.
- What stands from R132: the `INFINITE` wait is real code (v306 bounds it to 15
  minutes and terminates the engine — the fix acknowledges the defect even though it
  was not the measured cause); there is no prompt anywhere in the engine (Claude
  independently confirmed all four candidates); the copy now logs per file, so a
  future stall names the file.
- Refined, not changed: the wizard posts 90% ("finalizing") as soon as the engine
  exits, **before** it looks at the exit code (`sutram_wizard.asm` near the wait).
  A nearly-full bar is not evidence of success — my R132 said 60% before the wait,
  90% after; the diagnostic pins 90% to engine-exit, pre-exit-code-check. Not
  changed in v306 (a display order, not a wrong result).
- Still open, still mine: DisplayVersion is still hardcoded `0.1.0`
  (`install-core.ps1` lines 399, 412). Not changed in v306.

## 3. CHANGED — R133 WS1: one of my three "broken on PE" sites was a misread by me

My R133 count was "9 sites; 3 broken on PE (#3 latent, #5 the crash class, #6
skipped check)". The corrected count is **1 broken (#5, now fixed in v306) + 1
skipped check (#6, still skipped, latent) + 6 working + 1 allocating nothing**.

- **#3 arena reserve — I was wrong.** I wrote it "CHECKS but only for 0
  (`test rax,rax; jnz .have`) — BROKEN on PE in principle (misses −1)". That
  `test rax,rax` tests `cur` (the global, 0 on first call), not the syscall result.
  The syscall result is checked by `r69_n3` (`src/r65_arena.inc:84`):
  `cmp rax,-4095; jb .ok` — the failure range [-4095,-1] **includes** -1, so the
  PE shim's -1 maps to failure (cur = end = sima = 16, room 0 forever, fall back to
  the old sequence). The same range check guards the other allocation paths
  (`emit_nirmmita_from_rax`, `r101a_a2`). Claude's "the 0-versus-−1 defect is not
  there" is right for these paths. **My R133 fix item (a) — the shim should return
  0 instead of -1 — is not needed. I withdraw it.**
- **#5 `rt_veh` — CONFIRMED, not changed.** The brief and the v306 code agree with
  my diagnosis: a reservation does not count against a commit limit, the fault comes
  later when the handler fails to commit a touched page, and it returned
  `EXCEPTION_CONTINUE_SEARCH` → `0xC0000005`, empty output. The fix (ChatGPT PR #66,
  taken as it is) is exactly my item (b): on a failed commit, print
  `Sutram truti: smritih na labdha` and exit 1. Verified in the v306 source
  (`win/winrt_blob.asm:277-309`, new `.v_nomem`; `win/rtblob.inc` 1045 → 1165
  bytes). The message is deliberately generic — the handler does not know whether
  the page is a kosh, a nirmmita buffer, or the arena — and fatal, not the Linux
  kosh-specific refusal. That difference is documented in Claude's hand-back (the
  same message on both platforms would need commit-at-allocation-time, which v300
  removed on purpose for the 4 GiB arena). Not a defect.
- **#6 string `+` check skipped on PE — STILL SKIPPED in v306, but narrower than I
  presented.** `src/sutram_compiler.asm:23716-23717` still jumps over the
  `E_VARTANI_SMRITI` check on PE (`jne .vyoj_copy`). My item (c) was **not** built.
  But its exposure is narrower than my R133 wording: under a Job **commit** limit,
  string `+` allocates via nirmmita (the reserve succeeds) and the copy touches
  pages — so the crash scenario the Windows run measured is now covered by the
  `rt_veh` fix. The remaining hole is allocation-time only: nirmmita returns 0 only
  when the arena is full **and** the `VirtualAlloc` reserve fails — i.e.
  address-space exhaustion, not a commit limit. So (c) is latent and unmeasured,
  not the live class. It needs a different probe (see P2).

## 4. NOT CHANGED — the descriptor conclusions (R129/R130/R131)

The OOM defect was never in the descriptor. The growth reserves — which succeeds —
and the fault comes at touch time in the arena handler. My Linux attacks found no
crash because on Linux the failure surfaces at a different stage: `mmap` fails,
the result is normalised to 0, the grow check refuses with a message. The platforms
differ in **where** the failure surfaces, not in the descriptor's correctness.

Untouched by the Windows picture: alias coherence across growth (two names agree
past 20,000,000), 20,000 koshes on one mmap, the S1 refusal and the S2 fix, kosh
parameter growth propagating to the caller, the R131 sign-off for the compiler on
Linux. What changes is not the conclusion but the probe surface (see P1).

## 5. NOT CHANGED — R133 WS3 (IDE) and the harness

- **IDE — confirmed.** v306 does exactly what I recommended: a refused load clears
  the output pane first (new `output_clear` in `windows/gui/sutram_gui.asm`), then
  shows the refusal and the notice `[patram na udghatitam - sampadake purvam
  patram eva asti]` — the editor still holds the previous file. I said do NOT
  clear the editor; v306 does not. The brief's note that an instruction to "clear
  the editor" would have removed the safeguard is consistent with that
  recommendation. Verified in source; Claude drove it under Wine/Xvfb (old/new
  screenshots), not on native Windows.
- **Harness (`79_ayojan_cwd`) — confirmed.** `tools/test_windows_native.py` now runs
  the root `sutram.exe` (which has `lib/` beside it) for that one case; the compiler
  is unchanged. Verified in the diff. The v306 change is a test fix, as diagnosed.

## 6. YES — what I would probe next

The Windows run found what my Linux probes could not, because my probes only ever
tested **allocation-time** failure. The defect hid behind a reserve that succeeds
and a commit that fails later. The next attack surface is touch-time failure, and
three smaller items the picture exposed.

**P1 — Touch-time / commit-limit probes as a class (the big change).** Every future
memory attack should include a program that reserves successfully and then touches
under a limit, not only programs whose allocation fails. On Windows that gate now
exists: `tests/windows/test_commit_oom.py` (8 checks — kosh growth at 64/128/256
MiB, the nirmmita touch control, the 20,000-small-kosh control, the 2 GiB control,
the null-read control). On Linux the analogue needs a **commit** limit, not
`ulimit -v`: `ulimit -v` caps address space, so `mmap` fails at allocation — a
different stage. The Linux equivalent is a cgroup `memory.max`. Here
`/sys/fs/cgroup/memory.max` does not exist, so the Linux touch-time probe is
**NOT RUN here**; the design is delivered below for a machine with a commit limit.
Linux baselines delivered with this round (probes, all run on v306):

- `r134_nirmmita_check.sm` — `nirmmita(200000000)` with an explicit 0-check:
  no limit → prints `1`; under `ulimit -v 65536` → prints `0`, exit 0.
  The allocation-time path still refuses correctly on Linux.
- `r134_nirmmita_touch.sm` — the Windows `raw` program shape (touch every 512th
  cell of a 200 MB buffer): no limit → prints `done`, exit 0. Linux baseline for
  the control; under a limit it is **not** a meaningful Linux probe (the `mmap`
  fails first — see above), so it was not run under a limit here.
- `r134_null_read.sm` — `vitti p = 0; likha(p[0])`: exit 139, no output, no false
  OOM message. Negative control for the `rt_veh` change (PE-only, but confirmed
  unchanged on Linux).

**P2 — The string `+` allocation-time hole on PE (the one R133 item v306 left
open).** A program that exhausts **address space**, not commit, via string `+` on
Windows, asserting it refuses `E_VARTANI_SMRITI` instead of crashing. Windows-only,
NOT RUN here. This is the residual of my item (c); the commit-limit gate does not
cover it, because under a commit limit the reserve succeeds and `rt_veh` now
refuses.

**P3 — Installer upgrade over a partial install.** The ownership guard's real
defect is now visible: it reads "hash differs from the old manifest" as "user
file", but a product file can differ from the old manifest because the payload
changed. Next probe: install v306 over a partial/stale install and assert it either
completes or refuses with a message that names the file **and** says it is a product
file whose hash changed — not "user file". Add the ownership case to the
`r132_clean_shell_test.md` clean-shell test (Claude's to build). The v303 stall's
cause is still not established; a clean-state reproduction (disposable standard-user
Windows environment) is still needed, per the diagnostic.

**P4 — The 90% bar.** The wizard posts 90% ("finalizing") as soon as the engine
exits, before checking the exit code. Next probe: run the wizard over a failing
engine and assert the bar does not show success before the exit code is read (or
the failure dialog is unambiguous). Windows-only, not changed in v306.

**P5 — Unchanged practice.** Keep the scale and regression probes (R129's 11,
R127's 8) on every version. The Windows picture adds the commit-limit dimension to
them (e.g. the 20,000-kosh program under a commit limit on Windows — the new
gate's `small` case covers exactly that), it does not replace them.

## Verification on v306 (Linux, this round)

| Claim | Result |
|---|---|
| Version string | `Sutram 1.0 (v306) - sampurna sutra` — ran the committed binary |
| Suite | **PASS=327, NO-EXPECTATION=4, 331 run** — ran here, matches the brief |
| R130 installer-engine gate | **16 checks, 0 failed** — ran `tests/r130/test_installer_engine.py` here |
| R133 OOM probe (smallest program) | No limit → `10000001`, exit 0; `ulimit -v 65536` → `Sutram truti: kosh vardhayitum smritih na labdha - kosh yatha asit tatha eva`, exit 1 — unchanged from v305 |
| Installer payload SHA | `Sutram-Setup.sha256` (`e6006caf…`) matches the committed `Sutram-Setup.exe` — checked here |
| OOM fix in source | `.v_nomem` in `win/winrt_blob.asm:277-309`; message bytes in `win/rtblob.inc` — read here |
| IDE fix in source | `output_clear` + `msg_load_kept` in `windows/gui/sutram_gui.asm` — read here |
| Harness fix in source | `tools/test_windows_native.py` runs root `sutram.exe` for `79_ayojan_cwd` — read here |
| Dead message (R131 follow-up) | `msg_kosh_param_push` **still present** (`src/sutram_compiler.asm:680`, loaded at 22444) — the deletion was not done in v306 |
| Block-kosh parimana 96 vs 64 (R130) | Not addressed in v306 — no arena changes in the v306 diff |

## NOT RUN

- **Windows execution of v306** — the remaining gate, and the owner's round
  (`tests/windows/test_installer_e2e.py`, the wizard by hand, `test_commit_oom.py`
  on v305 with `--expect-baseline` then on v306, the native suite, the IDE refusal
  with a screenshot). The v306 OOM fix itself is verified on native Windows only
  on a source-built v305 candidate with the same runtime change (ChatGPT PR #66),
  **not** on the v306 binaries — Claude says so plainly in his hand-back.
- **Wine** — none installed here; PE/Wine checks (including the R124 lazy-commit
  gate and the 584 PE-DIFFER guard outputs) are Claude's evidence, not re-run here.
- **Full `tools/gates.sh`** — not re-run here (Wine-dependent gates cannot run
  without Wine). The one new gate (R130 installer engine) was run here: 0 failed.
- **The Linux touch-time probe (P1)** — no commit limit exists on this machine
  (no `/sys/fs/cgroup/memory.max`); design delivered, run where a limit exists.
- **P2, P3, P4** — Windows-only by nature; designs delivered, not run.

## Files delivered

- `ROUND-134-WINDOWS-PICTURE-ANSWER.md` (this report)
- `r134.json` (machine-readable summary of the changed/unchanged conclusions and
  the next probes)
- `r134_oom_small.sm` (the R133 smallest OOM program, re-run on v306)
- `r134_nirmmita_check.sm`, `r134_nirmmita_touch.sm`, `r134_null_read.sm` (new
  Linux baselines/controls for the touch-time question)
