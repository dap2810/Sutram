# ROUND-151: installer ownership, the mutant flags, and the fourth error (read-only, nothing run)

**Base read:** `origin/main` at `52d78435` ("v314 (R151-R152, R148-R150): the FFI door closed; --analysis-steps=N to the contract; the two limits named; the desktop collision; what is left"), 2026-11-08.
**Files read:** `windows/native-installer/install-core.ps1` (547+ lines), `windows/native-installer/uninstall-core.ps1`, `windows/native-installer/build-installer.ps1`, `windows/build-windows-setup.ps1`, `windows/build-windows-native.ps1`, `windows/r69-build-common.ps1`, `windows/native-installer/sutram_wizard.asm` (ownership-relevant lines only), `src/sutram_compiler.asm`, `src/r32_ffi.inc`, `src/r23_capabilities.inc`, `src/r25_phal.inc`, `tools/r69_build.py`, `tools/gates.sh`, `tools/cross_build_windows.py`, `tools/build_installer_linux.py`, `tests/r137/test_slice_number.py`, `tests/r143/test_walk_budget.py`, `tests/r152/test_analysis_steps.py`, `tests/r69/test_build_and_probe.py`, `.github/workflows/gates.yml`, `Sarvam-to-Muse/ROUND-151.md`, `Muse-to-Sarvam/ROUND-148-PAPER-REVIEW.md`, `Muse-to-Sarvam/ROUND-149-CLOSURE-ANSWER.md`, `Muse-to-Sarvam/ROUND-150-FIVE-GAPS-FFI-ADDRESS-RULE.md` (this batch), and, for context only and cited as such, ChatGPT's `ROUND-219-OWNERSHIP-INVENTORY-AND-MUTANT-PROVENANCE.md` (`9a931a22`) and `ROUND-218-V314-FOLLOWUP-OWNERSHIP-AND-CONTRACT.md` and the Claude brief `Sarvam-to-Claude/ROUND-151.md` (a different round, base v313).
**Method:** reading and grep only. Nothing compiled, assembled, run, or executed; nothing written into the repo; nothing uploaded. Every factual claim cites file + line at commit `52d78435` unless marked as a later document. Where a claim is a reading inference rather than a measured result, it says so. Where a question would need execution, the answer is "I could not determine this from source".

**One sourcing note.** `Sarvam-to-Muse/ROUND-151.md` is *not* in the v314 tree — it landed later (origin/main `4e2e0fae`). It was read from origin/main via `git show`; all verification below is against the v314 tree. Where a later document already states a trace found here, that is said rather than claiming a first discovery.

## Verdicts, first

| Question | Verdict |
|---|---|
| Task 1 — installer ownership | **The desktop defect is present in v314 exactly as briefed, and it is not the only pair of its shape.** Three live decide/record disagreements, one mitigated, one partial-check. |
| Task 2 — mutant flags | **NO — no checked-in build command defines either flag.** The only defining command is the R137 gate's own test harness, building into a temp dir. **But** both packagers stage a pre-existing `win/sutram.exe` on existence + PE-format checks only — a hand-built mutant placed there would be packaged. |
| Task 3 — the fourth error | **The invented `r23_check_call`.** Verified absent on v314 (zero hits in `src/` + `win/`). It *is* correction 4 in the R148 report (lines 37–38), so the ROUND-151 brief's premise — "I have not found it in your report" — is itself wrong. The brief repeats none of the four errors. |

## Task 1 — the installer ownership pattern

### The inventory — every `*Owned` record

"Decides" = the code that inspects the current state and judges ownership. "Records" = what is written to `install-state.ini`. "Uninstall trusts" = what `uninstall-core.ps1` consults when deleting.

| Record | Who sets it (install) | What it records | Uninstall trusts it independently of the owned list? |
|---|---|---|---|
| `OwnedShortcuts` (list, base64) | `New-Shortcut`, `windows/native-installer/install-core.ps1:367-380`: adds the path only when it creates/overwrites; preserves (logs, returns, no add) when the path exists and is absent from `oldState.OwnedShortcuts` (`:371-376`). Serialized at `:786`. | Every shortcut this installer created or overwrote, by path. | **No.** `windows/native-installer/uninstall-core.ps1:153-165`: for each of 4 fixed Start-menu names, removes only if the encoded path is in the list **and** the target starts with `$InstallDir` (or, for Terminal, the arguments contain it). List + content check. Note the uninstall iterates only the 4 fixed names; any other list entry is never removed through this branch. |
| `PathOwned` | `Set-UserPathEntry` return value + caller, `install-core.ps1:664-678`: `$pathOwned = ($previousOwned -or $pathAddedNow)` (`:672`), where `$pathAddedNow` is `Set-UserPathEntry`'s `$changed` (`:240-267`, returns true only when it added the entry). Serialized at `:780-781`, `:787`. | Whether this installer's `bin` entry in the user PATH is installer-owned. | **Yes — and there is no list to cross-check.** `uninstall-core.ps1:151` removes the `bin` entry on the flag alone. No live disagreement found: on every path traced, the helper's return is actually consulted (`:672`), and a pre-existing manual entry is not adopted (helper returns false when the entry is already present). The trust is unmitigated in principle, the record correct as far as reading shows. |
| `DesktopOwned` (legacy alias `DesktopShortcut`, read-only in v314) | The desktop caller, `install-core.ps1:714-742` (detail below). Serialized at `:782-783`, `:788`. `DesktopShortcut` is never written by v314; it is read at `:714` and `uninstall-core.ps1:166` only. | Whether a desktop shortcut is installer-owned, plus `DesktopLink` (`:789`) naming which file. | **Yes — independently of `OwnedShortcuts`.** `uninstall-core.ps1:166-175` reads `DesktopOwned` (or legacy `DesktopShortcut`) + `DesktopLink`, and removes the link when its `TargetPath` equals this install's GUI. It never consults `OwnedShortcuts`. |
| `AssociationOwned` | The association block, `install-core.ps1:760-764`: initialized from the old state (`:760`); set to true only when the installer writes `Sutram.Source` as the `.sm` default because there was none (`:761-764`). Serialized at `:790`. | Whether this installer set the `.sm` default value. | **Partially.** `uninstall-core.ps1:183-188` deletes the `.sm` default only if the flag is 1 **and** the current default is still `Sutram.Source`. The flag is trusted, but the current value is re-checked. |

No other `*Owned` flag exists in the installer: a grep for `Owned` over `windows/` hits only `install-core.ps1` and `uninstall-core.ps1` (the wizard `.asm` contains no `Owned` string; it passes the `-DesktopShortcut` switch, `windows/native-installer/sutram_wizard.asm:476`, `:1267-1269`, from the checkbox at `:392`). `UninstallerSHA256` and `InstallLogSHA256` are hashes, not ownership flags; `Version` and `DesktopLink` are not ownership flags. `install-state.ini` is written only by `install-core.ps1` (`:443` read, `:785-796` write, `:808` appends the log hash) and read/deleted only by `uninstall-core.ps1` (`:142`, `:220`).

### Pair 1 — desktop preserve vs. record (the known defect, confirmed on v314)

The trace, line by line:

1. The user's desktop `Sutram IDE.lnk` targets this install's GUI, so `$isOurs` is true (`install-core.ps1:720`: TargetPath equality only). The rename branch at `:724` therefore does not fire, and `$desktopName` stays `Sutram IDE.lnk`.
2. The preserve branch at `:730` requires `-not (& $isOurs $desktopLink)`, so it is skipped too. Execution falls to the `else` at `:734-735`: `New-Shortcut $desktopLink …; $desktopOwned = $true`.
3. Inside `New-Shortcut` (`:367-380`): the path exists and its base64 is absent from `oldState.OwnedShortcuts`, so it logs `Preserved pre-existing user shortcut` (`:372`) and **returns without creating it or adding it to the new owned list** (`:376` is not reached).
4. The caller nevertheless records `$desktopOwned = $true` (`:735`), serialized as `DesktopOwned=1` and `DesktopLink=Sutram IDE.lnk` (`:782-783`, `:788-789`).
5. Uninstall (`uninstall-core.ps1:166-175`) trusts the flag plus the TargetPath match and removes the user's preserved link, never consulting `OwnedShortcuts`.

The helper decided "preserve"; the caller recorded "owned"; uninstall trusts the record. Present in v314 exactly as briefed.

### Pair 2 — previously-owned but user-retargeted link overwritten (R218 §1B)

On a later install, `$previousDesktopOwned` is true (`install-core.ps1:714`) and the old encoded path is still in `OwnedShortcuts`. If the user has retargeted that link (e.g. to Notepad):

- The preserve branch at `:730` is excluded by its own condition (`-and -not $previousDesktopOwned`).
- The `else` calls `New-Shortcut`, which authorizes replacement from historical list membership alone: at `:371-376`, a path that *is* in `oldState.OwnedShortcuts` falls through to `:376` (added to the new list) and `Save()`, with no comparison of the existing link's target, arguments, icon, or working directory against the new values. The user's retargeted link is overwritten.
- `$desktopOwned = $true` (`:735`) records the overwrite as owned.

The loss happens at install time, not uninstall time: uninstall's TargetPath check (`uninstall-core.ps1:170-174`) cannot protect a link the installer itself already rewrote. Same shape as pair 1, different branch of the same caller.

### Pair 3 — the registry class tree (found by reading v314)

No `*Owned` flag exists for the contents of `HKCU:\Software\Classes\Sutram.Source`. The decision and the record are:

- **Decision (install):** command equality. The preflight at `install-core.ps1:477-483` accepts an existing class whose open command already equals the wanted command; the registration block at `:745-757` writes the command and `DefaultIcon` with no per-value ownership record.
- **Record:** none. Nothing distinguishes pre-existing contents of the key from installer-written contents.
- **Trust (uninstall):** `uninstall-core.ps1:181-182` — if the command key exists and its value equals the expected command, `Remove-Item -LiteralPath $classKey -Recurse -Force` deletes the whole key.

Sequential counterexample, no racing process: a valid installation has the expected command; the user adds a value or another shell verb beneath `Sutram.Source` without changing the command; uninstall sees the expected command and deletes the added value/verb too. The same shape as pairs 1–2 (a check in one place, a record kept elsewhere that does not consult it — here the record is absent entirely), with the same consequence.

Two limbs of the same tree-identity shape:

- **`.sm\OpenWithProgids\Sutram.Source`**: install writes it at `install-core.ps1:765-766` without recording whether it pre-existed; uninstall removes it at `uninstall-core.ps1:188` under the matching-command branch, independently of `AssociationOwned`.
- **The Uninstall registry key** (`HKCU:\…\Uninstall\Sutram`): install writes product values at `install-core.ps1:767-777`; uninstall deletes the key at `uninstall-core.ps1:202-205` when `InstallLocation` matches — any user-added value under that key goes with it.

Disclosure: ChatGPT's R219 (origin/main `9a931a22`, later than v314) states this same trace as its "Third mismatch". It was reached independently by reading v314; R219 corroborates it rather than being its source.

### Adjacent findings (same class, not full pairs)

- **`AssociationOwned` drift — mitigated.** `install-core.ps1:760-764` carries the old flag forward when the current `.sm` default is the user's (the `if (-not $existingDefault)` at `:761` does not fire, so the flag is left at its old value of 1). The record then disagrees with the decision. Uninstall's re-check of the current value (`uninstall-core.ps1:183-188`) blocks the loss, so this is a latent record error, not a live data-loss path.
- **Start-menu parallel.** `New-Shortcut` can overwrite a user-retargeted formerly-owned Start-menu link for the same reason as pair 2 (`install-core.ps1:367-380`, old-list membership authorizes `Save()`). Uninstall (`uninstall-core.ps1:153-165`) removes a modified IDE link if its target still starts with `$InstallDir`, or a modified Terminal link if its arguments still contain `$InstallDir`; changes to arguments, icon, working directory, or other verbs are not captured by those partial checks.
- **Stale locator, harmless.** When no desktop shortcut is requested and none was previously owned, `DesktopLink` is still written as `Sutram IDE.lnk` (`install-core.ps1:715`, `:789`, with `$desktopOwned = $false` at `:742`). Uninstall reads the name (`uninstall-core.ps1:168`) but acts only when the flag is set, so the stale name is inert. Noted for completeness, not a defect.

### Counts

- **Decision sites:** 7 — the five R219 names for the four current records (PATH helper return, PATH caller, shortcut helper, desktop caller, association-default block) plus 2 unrecorded registry decisions (class-command acceptance, `OpenWithProgids` write).
- **Record sites:** 1 serializer (`install-core.ps1:785-796`) writing 4 current records (`OwnedShortcuts`, `PathOwned`, `DesktopOwned`, `AssociationOwned`) + 1 locator (`DesktopLink`); 1 legacy key read-only (`DesktopShortcut`).
- **Disagreements:** 3 live (pairs 1–3) + 1 mitigated (`AssociationOwned` drift) + 1 partial-check (Start-menu). Uninstall trusts `DesktopOwned` and `PathOwned` independently; `AssociationOwned` only with a current-value re-check; `OwnedShortcuts` only with a content check; the class tree, `OpenWithProgids`, and Uninstall key on identity match alone, with no record at all.

## Task 2 — the mutant flags

### Verdict: NO — with one packaging gap

**No checked-in build command defines `R142_MUTANT_NO_STMT_CHECK` or `R142_MUTANT_NO_GLOBAL_CHECK`.** The only command in the tree that defines either flag is the R137 gate's own test harness, which builds into a temporary directory and never copies its outputs to a release path. **But the answer "impossible to ship a mutant" would exceed the evidence:** the two packaging paths stage a pre-existing `win/sutram.exe` after existence and PE-format checks only, with no rebuild and no comparison against a plain build. A mutant binary placed at `win/sutram.exe` by hand would be packaged. The only mechanism that would catch it is the R137 gate's plain-build identity check, which is skipped in `--compiler` mode and when `nasm`/`ld` are missing. Details and the exact skip conditions are below.

### Every occurrence of the flag names (whole tree, at `52d78435`)

| Location | Role |
|---|---|
| `src/sutram_compiler.asm:18396`, `:18410`, `:18414` | `%ifndef R142_MUTANT_NO_GLOBAL_CHECK` guards (the initializer entry forgets the walk). Guards, not definitions. |
| `src/sutram_compiler.asm:18905`, `:18915` | `%ifndef R142_MUTANT_NO_STMT_CHECK` guards (the statement entry forgets the walk). Guards, not definitions. |
| `tests/r137/test_slice_number.py:231-235` | **The only defining command in the tree.** `nasm -f elf64 -I. -D{define} src/r68_compiler_entry.asm` for each flag, outputs into `tempfile.mkdtemp(prefix='r137-')` (work dir, `:180`). Nothing copies them anywhere. |
| `tests/r137/test_slice_number.py:25` | Documentation of the two flags in the module docstring. |
| `docs/CHANGELOG.md:62-63`; `Muse-to-Sarvam/ROUND-148-PAPER-REVIEW.md:108`, `:274`, `:696-697`; `Claude-to-Sarvam/R142-00-THE-CHECK-IS-INSIDE-GEN-EXPR-AND-NOTHING-IS-DELETED-ON-A-NAME-V311.md:47`; `Sarvam-to-Claude/ROUND-151.md:44` | Mentions only. (The last is the Claude R151 brief, a different round.) |

No `%define R142_MUTANT…` exists anywhere in `src/`. No `NASMFLAGS` / `NASM_FLAGS` variable exists anywhere in the tree (grep over `*.py`, `*.sh`, `*.yml`, `*.ps1`: zero hits), and NASM takes no `-D` from the environment, so there is no env-var injection route in the checked-in scripts.

### Every build path that produces a compiler, and what `-D` it passes

| Path | Command | `-D` flags |
|---|---|---|
| `tools/r69_build.py`, `build_commands` (`:115-127`) — the canonical builder; `tools/build-sutram.sh:5` delegates to it | `nasm -f elf64\|win64 -I… src/r68_compiler_entry.asm`, `ld …` | `-DWINDOWS=1` on Windows only, plus `-D` + `MODES[mode]` (`:121-122`). `MODES` (`:26-32`) is `default ()`, `peepholes (SUTRAM_R65_PEEPHOLES=1)`, `trap (SUTRAM_R65_TRAP_INT=1)`, `combined`, `pairs (SUTRAM_R67_PURE_STACK_PAIRS=1)` — **no mutant mode**; an unknown mode/target raises `ValueError`. `verify_release` checks the git-blob source pins first (`COMPILER_BLOB 411450a4…`, v314, `:24`). |
| `tools/gates.sh`, build step (`:~60`) | `$NASM -f elf64 -I. src/r68_compiler_entry.asm -o /tmp/g_c.o`, `ld -o ./sutram_compiler` | None. Plain. Rebuilds `./sutram_compiler` fresh on every run. (`NASM` is the binary path only, `NASM=${NASM:-nasm}`.) |
| `tools/cross_build_windows.py:112-114` | `nasm -f win64 -dWINDOWS -I… src/r68_compiler_entry.asm`, `x86_64-w64-mingw32-ld … -o win/sutram.exe`, copied to `sutram.exe` | `-dWINDOWS` only. **No pin verification in this file** (grep for `verify_release`/`pins`/`lock`: none); it records git HEAD + a dirty flag in a report (`:159-165`). |
| `windows/build-windows-native.ps1` | `nasm -f win64 -dWINDOWS … src/r68_compiler_entry.asm`, `ld … -o win\sutram.exe`; then `--version` + a hello compile/run | `-dWINDOWS` only. |
| `windows/build-windows-setup.ps1` (7 lines) | Runs `preflight-windows.ps1`, `build-windows-native.ps1`, `gui\build-gui.ps1`, `native-installer\build-installer.ps1` | None itself. `preflight-windows.ps1` verifies every source file's SHA-256 against `windows/windows-build-integrity.sha256` (440 entries) — **source** provenance, not binary provenance. |
| `tools/build_installer_linux.py:103-111` (the release packager per `docs/BUILDING.md`) | Stages pre-existing `win/sutram.exe` as `bin/` and `win/` by `shutil.copy2` | None — and **no rebuild, no plain-build comparison**. The only checks are existence and `assert_pe64` (PE32+ AMD64 magic, `:49-51`). |
| `windows/native-installer/build-installer.ps1:9-18` | Stages pre-existing `win/sutram.exe` (existence + `Assert-Pe64`) | None — same gap as the Linux packager. Runs `--self-test` on the finished `Sutram-Setup.exe`, which is a functional check, not a provenance check. |
| `.github/workflows/gates.yml:23-24` | Runs `sh tools/gates.sh` | None in the workflow. CI therefore rebuilds plainly and runs the R137 gate. |

### The other `-D` users (not the compiler, or not shippable)

- `tools/build_xmm_variants.sh:18,26` — `-DSUTRAM_EXPERIMENTAL_XMM_CACHE=1`, outputs to a `$DEST` directory (experiment, not a release path).
- `tools/r65_native_acceptance.py:6,8` — `-DSUTRAM_R65_PEEPHOLES=1` / `-DSUTRAM_R65_TRAP_INT=1`, outputs to `/tmp`.
- `tools/r61_windows_compiler_diagnostics.ps1:98`, `.github/workflows/r49-r50-native.yml:54` — `-DR49_WIN_DIAG_$n`, old diagnostic probes into results/temp dirs.
- `tools/guard_page.py:48` — `-dGUARD_PAGES`, scratch dir.
- `tests/r133/test_veh_registration.py:68-70` — `-DR133_FAIL_VEH_REGISTRATION`, `-DR135_FAIL_COMMIT`, `-DR137_FAIL_RESERVE` (failure-injection test compilers).
- `tests/r143/test_walk_budget.py:102` — `-DR143_WALK_BUDGET=64` (test compiler in a temp dir).
- `docs/BUILDING.md:44,53` — `-DWINDOWS=1` only (manual commands).
- `tools/proof_lib.py:54`, `tools/proof_props.py:49`, `tools/peak_rss.py:28` — plain `nasm`, no `-D`.

### The detection mechanism, and its skip conditions

The R137 gate (`tests/r137/test_slice_number.py:213-228`, identity check added in R152) builds a plain compiler (`nasm -f elf64 -I. src/r68_compiler_entry.asm`, no `-D`) and compares its bytes to the committed `./sutram_compiler`; when the mingw linker is present it also builds the plain PE (`nasm -f win64 -dWINDOWS …`) and compares it to both `sutram.exe` and `win/sutram.exe`. This runs **only** when testing the tree's own compiler (`own = '--compiler' not in sys.argv`, `:139`) **and** `nasm` and `ld` are installed; otherwise it prints `NOT RUN` (`:226-230`). The mutant builds run in the same gated branch (`:231-235`).

So the chain that protects a release is: (a) every checked-in build command is plain, (b) the R137 gate's identity check catches a substituted binary — **provided the gate is actually run on the exact bytes being packaged, in `own` mode, with `nasm`/`ld` (and the mingw linker for the PE half)**. What is *not* in the tree is any step that makes the packager itself refuse a `win/sutram.exe` that was not just built plainly: both packagers trust pre-existing bytes. A hand-built mutant (`nasm -DR142_MUTANT_…`) copied to `win/sutram.exe`, followed by `tools/build_installer_linux.py` without the R137 gate, would ship. That is a process gap, not evidence that today's package is a mutant — and the committed `win/sutram.exe` bytes are exactly what the R137 identity check is for.

### Side notes (reading determinations, not execution)

- `windows/r69-build-common.ps1` (the git-blob pin checker, `Assert-R69SourcePins`) is referenced by **no** build script in the tree — only by docs and by `tests/r69/test_build_and_probe.py:122`, which checks the file exists. The live pin mechanism on the Windows chain is the integrity manifest in `preflight-windows.ps1`, not this script.
- `tests/r69/test_build_and_probe.py:127-129` (`test_staged_payload_hash_gate`) asserts that `windows/build-windows-setup.ps1` contains `bin\sutram.exe`, `win\sutram.exe`, and `Installer staged a different`. The v314 file is 7 lines and contains none of those strings (grep count 0). The test's expectation is stale by reading; whether the test suite currently fails on it would need execution, which this round forbids.

## Task 3 — the fourth error in the brief

### Verdict: the invented `r23_check_call`

The fourth error is **the invented `r23_check_call`** — a call-side check that does not exist. It *is* correction 4 in the R148 report (`Muse-to-Sarvam/ROUND-148-PAPER-REVIEW.md:37-38`), so the ROUND-151 brief's premise — "I have not found it in your report" — is itself wrong. The ROUND-151 brief does **not** repeat any of the four errors. Two of the brief's own claims do not survive a reading check (see "The ROUND-151 brief's own numbers" below); the rest check out.

### Correction 4, verified on v314

Grep for `r23_check_call` over `src/` and `win/` at `52d78435` returns **zero hits**. The name occurs nowhere else in the tree except the R148 report itself. The actual call-side checks on v314 are:

| Check | Label (v314) | Called from | What it does |
|---|---|---|---|
| `r129_check_call` | `src/sutram_compiler.asm:28908` | `:19044` (expression calls), `:21552` (statement calls) | Refuses a kosh-made slice beside a growing/call argument (`E_KOSH_VIBHAG`); the `.unknown` path for indirect/unknown callees is at `:28966`. |
| `r126_check_untyped_arg` | `src/sutram_compiler.asm:29341` | `:27331` (`gen_typed_call_arg`) | Refuses kosh kinds 2, 3, 6 to an untyped parameter (`E_KOSH_DVARA`). |
| `r108_check_call` | `src/sutram_compiler.asm:12765` | `:21554` | Refuses a kosh of an open `mandapa` block as an argument. |
| `r23_check_return` | `src/r23_capabilities.inc:510` | `:20960` (`src/sutram_compiler.asm`) | Checks what `nivartanam` returns; a slice return is refused. |
| `r73_check_call` (not listed in the R148 report) | `src/sutram_compiler.asm:8700` | `:17807` | Checks `kosh_push`, `likh8`, `likh8c`, `setchar` argument shapes at the call site. |
| `r25_check_call` (not listed in the R148 report) | `src/r25_phal.inc:86` | `:19046`, `:21575` | `phal`/`prasar` discipline at the start of every generated call. |

The R148 report's line numbers were for `0fb61357`; on v314 they have drifted (`r129` 28771→28908, `r126` 29204→29341, `r108` 12715→12765, `r23_check_return` 508–513→510). Labels and roles are unchanged. The other three corrections also hold on v314: no `r157` in `src/`; `call gen_expr` sites are 133 in `src/sutram_compiler.asm` + 13 in the `%include`d files (`r23_capabilities.inc` 4, `r25_phal.inc` 2, `r32_ffi.inc` 3, `r65_arena.inc` 4) = **146**; one `jmp gen_expr` at `:9085`.

One honest gap: the R148 brief itself (`Sarvam-to-Muse/ROUND-148-PAPER-REVIEW.md`) never contains the string `r23_check_call` — a grep over `Sarvam-to-Muse/`, `ChatGPT-to-Sarvam/`, `Claude-to-Sarvam/`, and `docs/` finds it only in the R148 report. So *which* document first cited the invented name could not be established from the tree; the R148 report corrects it without a citable source line. That does not affect the correction — the label does not exist — but the provenance is undetermined from source.

### Does the ROUND-151 brief repeat any of the four errors?

No. The brief's text contains no `r157`, no `133`, no `64`-checks figure, and no `r23_check_call`. It repeats none of the four.

### The ROUND-151 brief's own numbers, checked by reading

| Brief claim | Check |
|---|---|
| "gates 78 PASS / 0 FAIL / 1 NOT-RUN" | **Denominator verified; split not checkable by reading.** `tools/gates.sh` has 75 `run_gate` invocations plus 4 direct gates (`committed modes`, `X11 GUI protocol`, `Windows execution`, `doc counts`) = **79 total**. 78 + 1 = 79, arithmetically consistent. Whether all 78 passed is a runtime result. |
| "suite NO-EXPECTATION=4 PASS=327 (331 run)" | **Not checkable by reading.** A runtime result. |
| "Guard v313 → v314: 783 programs… 587 identical / 195 refused identically / 0 DIFFER, plus one new" | **Corroborated in-tree.** `docs/CHANGELOG.md:17` states the same figures; `Claude-to-Sarvam/evidence-r152/guard-elf.txt` and `guard-pe.txt` each contain 587 `IDENTICAL` lines and end with the summary `783 programs: 587 byte-identical, 195 refused identically, 0 DIFFER, 1 new` (785 lines each = 783 programs + 2 summary lines). The guard run itself is execution evidence; the files' contents match the brief. |
| Installer `a0e786e44d26780ef5f20f4103eaefdd7b33474762ebd41611499144cc4e03eb` | **Verified.** `Sutram-Setup.sha256` in the tree contains exactly that hash for `Sutram-Setup.exe`. |
| "`--analysis-steps=N` built to the contract, 40 cases tested" | **Verified by counting, not by running.** `tests/r152/test_analysis_steps.py` contains exactly 40 `check()` calls: 3 accepted values + 1 budget-1 + 1 leading-zeros + 25 `REJECT` entries + 1 separate-token + 2 second-occurrence + 1 after-files accept + 1 after-files refuse + 1 module-initializer + 1 `--check` + 1 `--lang` + 1 `--ffi … --object` + 1 usage = 40. |
| "The budget arithmetic — 3,145,728 / 72 = 43,690 nodes, x 8 + 1 = 349,521, and gate R143 reads the sizes and the loop and recomputes it" | **Verified in substance.** `src/sutram_compiler.asm:34` `AST_NODE_SIZE equ 72`, `:38` `AST_HEAP_CAP equ 3145728`. 3145728 / 72 = 43690.67, so 43,690 is the floor — exactly what the gate computes (`tests/r143/test_walk_budget.py:83`: `bound = 8 * (cap // size) + 1`, checked equal to 349521, with `len(fields) <= 8` read from the walk loop's field range and the spend-before-entry ordering checked). The brief does not say "floor", but the number is the one the gate uses. Qualification (stated in the R218 follow-up, not re-derived here): the gate does not prove the no-revisited-nodes premise behind the universal bound. |
| "The two limits now name themselves" | **Overstated.** `E_VRIKSHA_SEEMA` does not exist in `src/` (zero hits). The analysis limit names itself (`E_VAKYA_SEEMA`, `src/sutram_compiler.asm:636`); the AST limit's hint (`:642`) borrows that code only to say the AST limit is *not* the analysis limit. The AST limit has no distinct code of its own. This matches the R218 follow-up §3. |
| "Thirty-five false claims by Sarvam this stretch" | **Not checkable by reading.** A historical tally, not a tree fact. |
| Line anchors cited in the Claude R151 brief (same round family): `r33_gen_foreign_funcall` (`src/r32_ffi.inc:666`), `.funcall` 28474–28505, `.num` 28590–28620, `func_param_type` 26945–26980, `r129` `.unknown` 28771–28880, `r137_check_stmt` 28402, `r142_wstack` 1565, `r142_push` 28677, `jmp gen_expr` 9035 | **Labels confirmed, lines drifted** (expected between bases): on v314, `r33_gen_foreign_funcall` is at `:666` (exact); `.funcall` `:28530`, `.num` `:28637`, `func_param_type` `:26995`, `.unknown` `:28966`, `r137_check_stmt` `:28452`, `r142_wstack` `:1574`, `r142_push` `:28814`, `jmp gen_expr` `:9085`. The FFI fix itself is visible: `r32_ffi.inc` now calls `r134_holds_kosh` at `:699` and `is_kosh_var` at `:693`, `:717`, `:746`. |
| R148 correction 3 ("R137 gate has 87 checks, not 64") on v314 | **Stale on v314.** Counted from `tests/r137/test_slice_number.py`: 6 source/list checks + 84 programs (59 `cases()` + 1 ChatGPT probe + 5 `GLOBALS` + 4 `STACK` + 15 R147 shapes) = **90 base, 91 with the R152 identity check, 93 with both mutants**. The 87/89 figure was for `0fb61357`; the gate has grown since (15th R147 shape, the identity check). |

## What would need execution (could not determine from source)

- Whether the committed `sutram_compiler`, `sutram.exe`, and `win/sutram.exe` bytes are in fact the plain builds (that is the R137 gate's identity check; it must be *run*).
- Whether the 78/0/1 gate split and the 327 suite passes actually hold on v314.
- Whether the R137 gate's mutant builds behave as described.
- Whether any of the installer traces above reproduce natively (all are static source traces; the desktop defect's preconditions — a user link targeting the installed GUI, a previous install's state — are straightforward to stage, but staging them is execution).
- Whether `tests/r69/test_build_and_probe.py::test_staged_payload_hash_gate` currently fails (its assertions contradict the v314 file by reading, but the test run itself is execution).

## NOT RUN

Windows execution, Wine, the full suite, the gates, any probe program, any build, any installer run — all of it, by the brief's own direction ("Read only. Nothing to compile, nothing to run, no escape tests."). The v314 gate/suite/guard figures quoted above are other agents' execution evidence, cited as such, not re-run here.
