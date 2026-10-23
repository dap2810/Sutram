# Sutram ROUND-108 WS1 — Current P0 claims: corrected, still open, or patch pending

**Pinned main:** `4a25db6092bdad3de7139367c68d203960cd1b22` (v326, 23 Oct 2026). **Prior audit:** [R106 WS1](ROUND-106-WS1-ACTIONABLE-PROSE-CORRECTIONS.md), [R107 WS2](ROUND-107-WS2-P0-RECONCILIATION.md). **Owners' order:** `LANGUAGE-PRIORITY.md` (Sanskrit only) and `docs/PATH-TO-COMPLETION.md` (Windows acceptance/type decision before release). This is a **live-tree recheck**: a proposed Muse patch is *not* a main-branch fix until its content is present on main.

## Applied — CLOSED, DO NOT repeat

| Source | Live finding |
|---|---|
| `README.md` (blob `599f1cc5078e43530ddc572af4a5e84f851ce253`) | Known limits no longer deny separate compilation, function values or an actual Windows GUI test. |
| `docs/sutram-roadmap.html` (blob `235c68e63ad36d51243bd1c82b532d9a762dfbe4`) | Records real Windows acceptance (16 required checks) and native `SUTRAMO1/2` separate compilation. |
| `PROJECT-OVERVIEW.md` (blob `e8a890746e7b4092063dc158aaed9972550bf83e`) | Real Windows GUI/installer is acknowledged in `:153`; contradictory `Not implemented`/`No first-class functions`/`No collections beyond kosh` passage removed at `:156`. **Clean-up only:** `“**Not proven.** **Partly proven.**”` in the same header and duplicated “Still absent” sentence; *not* an old P0 failure. |
| `docs/sutram-project-status.html:181–182` (blob `40022601eeccce00d7c4d683999f3efd493656d8`) | Now states first-class functions, methods and slices landed. Other Windows/FFI cells remain stale. |
| `PROJECT-MASTER.md:267–275` (blob `480adad1ab5f0c209479e985d50c401497afd7ac`) | Performance verdict corrected to **2 wins, 2 losses, 1 tie** against Zig; do not reopen the old “4 of 5” error. |
| `docs/sutram-scorecard.html:206` (blob `8f8f537e6e801afcab75ba0333dbebbcf4029a36`) | Acknowledges first-class functions, methods and slices. **Not** proof the scorecard's `:150` FFI row is fixed. |

## P0 — still OPEN in actual current main

Each line below is exact/current source wording followed by the **minimum safe replacement**; Sarvam should re-fetch immediately before editing.

| Current location | Exact present claim (verbatim) | Source truth | Minimum replacement |
|---|---|---|---|
| `PROJECT-MASTER.md:80` | `“Partial — functions exist, but not first-class”` | R23 function values exist; closures/pattern matching remain unfinished. | `“Partial — first-class function values exist; closures, iterators and pattern matching remain incomplete.”` |
| `PROJECT-MASTER.md:82` | `“Partial — rachana gives structs; no methods or traits”` | Methods exist; traits remain absent. | `“Partial — structs and methods work; traits and general polymorphism are not implemented.”` |
| `PROJECT-MASTER.md:83` | `“Partial — mala/kosh are contiguous; no slices or SIMD”` | Slices exist. | `“Partial — contiguous arrays and slices exist; SIMD and broader layout controls remain incomplete.”` |
| `PROJECT-MASTER.md:107` | `“Linux x86-64 tested; **Windows never executed**”` | Real Windows owner run/installer/GUI passed 16 required checks for a pinned snapshot, **not** current release acceptance. | `“Linux tested; Windows compiler/installer/GUI executed on pinned native Windows 11 snapshot; current merged revision not yet reaccepted.”` |
| `PROJECT-MASTER.md:109` | `“IDE + installer + diagnostics; no formatter, LSP or debugger”` | `tools/sutram_fmt.py` implements a command-line formatter; no general LSP/debugger. | `“IDE, installer, diagnostics and CLI formatter exist; LSP/debugger incomplete.”` |
| `PROJECT-MASTER.md:110–111` | `“Not started | No C FFI”` / `“no fuzzing, no cross-platform run”` | Linux opt-in C FFI and project linker on main; Windows native FFI on unmerged v245 review branch, real Windows runs and fuzz already reported. | `“Interoperability partial — Linux C FFI implemented, Windows FFI branch native-tested; wider imports/ownership incomplete.”` / `“Fuzz and cross-platform tests exist; coverage/current release acceptance incomplete.”` |
| `PROJECT-MASTER.md:360–362` | `“Two of them — Windows execution and the freestanding boot — have never been performed by anyone”` | Windows executed; freestanding boot not demonstrated. | `“Windows has pinned real native acceptance; the freestanding boot remains not executed.”` |
| `docs/sutram-design-parameters.html:157–159` | `“functions exist and can be called, but they are **not first-class** — there are no function values”` | R23 first-class function values; closures/iterators/pattern matching still absent. | `“Function values exist and can be passed; closures, iterators and pattern matching remain absent.”` |
| `docs/sutram-design-parameters.html:178–180` | `“There are **no methods**, no traits and no polymorphism”` | Methods exist. | `“Methods on structures exist; traits and general polymorphism remain absent.”` |
| `docs/sutram-design-parameters.html:189–191` | `“there are no slices, alignment controls, SIMD or vector operations”` | R23 slices exist; other listed gaps remain. | `“Slices exist; general alignment controls, SIMD and vector operations remain incomplete.”` |
| `docs/sutram-design-parameters.html:304–305` | `“layers are not formally separated — nothing marks which modules are allocator-free”` | All 24 modules have `# layer` markers checked by `tools/check_layers.py`; reported 14 core/9 alloc/1 std. | `“Every library module declares core/alloc/std layer; a gate checks direct imports and builtins, not general memory safety.”` |
| `docs/sutram-design-parameters.html:315–316` | `“Windows x86-64 sources exist and **have never been executed by this project**”` | Owner tested Windows snapshot; current merge/installer acceptance pending. | `“Windows compiler, IDE and installer executed on a pinned real Windows 11 snapshot; current release acceptance pending.”` |
| `docs/sutram-design-parameters.html:327–329` | `“There is **no separate compilation**, no package manager, no lockfile.”` | `--separate`/`sutram-link` exist; last two gaps remain. | `“Separate compilation and native object linker exist; no package manager or lockfile yet.”` |
| `docs/sutram-design-parameters.html:364–366` | `“there is **no FFI**”` | Linux FFI implemented; Windows FFI v245 branch-tested. | `“Opt-in Linux C FFI exists; Windows C FFI was tested on unmerged review branch; generic C libraries/ownership remain limited.”` |
| `docs/sutram-design-parameters.html:377–381` | `“Missing: a formal written specification, fuzzing, and cross-platform execution.”` | A partial written specification, fuzzers and Windows test runs exist; formal completeness missing. | `“A partial written specification, fuzz and pinned cross-platform evidence exist; exhaustive formal coverage and current release validation remain open.”` |
| `docs/sutram-project-status.html:146–147` | `“Compiler (Windows x86-64) Unverified”` / `“Never executed by this project”` | 16 owner non-elevated Windows checks (old revision). | `“Executed on pinned Windows 11 revision; present merged release needs reacceptance.”` |
| `docs/sutram-project-status.html:154–155` | `“Installer Source only”` / `“installer itself untested on Windows”` | Owner actually used installer on tested snapshot. | `“Installer source and previously accepted Windows package; latest branch/revision not repackaged/reaccepted.”` |
| `docs/sutram-project-status.html:190–191` | `“Not started — Interoperability (FFI)”` / `“No C FFI”` | Linux FFI on main; native Windows FFI on review branch. | `“Partial — opt-in Linux FFI exists; Windows FFI branch-tested; advanced interop remains incomplete.”` |
| `docs/sutram-project-status.html:215–219` | `“ROUND-70 … Issued, awaiting”` / `“Windows acceptance — the one gate nobody has run”` | R107 delivered and Round108 active; Windows acceptance run. | Replace the **entire outdated open-items table** with a direct link to `docs/PATH-TO-COMPLETION.md` and the ordered Windows-merge/mixed-ABI/owner-type/Sanskrit-v1.0 tasks. |
| `docs/sutram-project-status.html:227–228` | `“no run has ever produced a verified executable”` | Pinned Windows native execution documented. | `“Windows native runs exist on pinned revisions; current merged installer acceptance remains open.”` |
| `docs/sutram-scorecard.html:150` | `“there is no C FFI and no calling convention for foreign code”` | SysV ABI/FFI on main; Microsoft x64 ABI written and Windows v245 branch tested. | `“C FFI exists for Linux; MS x64 FFI has branch-specific native tests. Cross-library imports/typed safety remain incomplete.”` |

## P1 — real drift, but do NOT conflate with P0 claims

- `PROJECT-MASTER.md` still has the **2026-10-20 three-language active plan**, despite owner's 23 Oct `LANGUAGE-PRIORITY.md`: **SANSKRIT ONLY**, other ten packs frozen. Add a **SUPERSEDED** date banner; do not rewrite/develop the frozen pack files.
- `PROJECT-MASTER.md` charter numbering for items 17–20 diverges from `docs/sutram-design-parameters.html` and says `ROADMAP-TO-V1.0.md` is canonical; the owner set `docs/PATH-TO-COMPLETION.md` instead. Correct references and recompute tally only from actual rubric.
- `docs/sutram-scorecard.html:126,158,166,174,182,237` has stale formatter/undo/modules/tests/keyword/Result wording; keyword **32/28** definition awaits owner, so do NOT silently pick 28 or overwrite “32” in a formula by guess.
- `docs/sutram-stdlib-reference.html` overstates core modules “Safe anywhere, including a freestanding program”: layer independence does not certify boot/runtime or raw-pointer safety.
- `docs/PATH-TO-COMPLETION.md` reports 25/6/19 allocation checks as an **explicitly dated v315 measurement**, whereas R39 later reported 26/13/13; refresh only after Sarvam's new fresh-clone verification, preserving old receipt.
- A source-mode distinction matters: older Windows installed programs ≠ the v245 Windows FFI branch and ≠ the present v326 packaged release.

## Muse R33 proposed patch — NOT APPLIED on pinned main

Muse triaged **163 source-text absence hits: 16 false hits covering 13 distinct claims, 88 true and 57 historical**, with a **seven-file patch** at `Muse-to-Sarvam/2026-10-23-round33-triage-fixes.patch` (blob `a72ddc5a9c9a70deedcf2bff845c301ce2359def`). The later v326 changelog explicitly says **“the patch is delivered, not applied”**. Direct current GitHub source confirms the false sentences are **still present**. Do not call the proposed patch a main-branch fix merely because the changelog headline says “fixed”.

**Three precision corrections before Sarvam applies that patch:**

1. `docs/LIBRARY-BOUNDARY.md` patch proposes `“charter item 19, done”` because some opt-in C FFI exists. **“Done” overstates charter item 19**, which also targets broad interop and ecosystem. Prefer **“charter item 19: partial; opt-in FFI exists but the standard library intentionally remains self-contained.”**
2. `docs/sutram-scorecard.html` patch replaces “no calling convention for foreign code” with **“no calling convention documented for foreign code yet.”** **That is also false:** R100 Microsoft x64 ABI, documented SysV ABI, and `docs/OBJECT-FORMAT.md` already describe it. Say **“C FFI has documented SysV/MS ABI subsets; broader C interoperability remains limited.”**
3. `docs/sutram-stdlib.html` explicitly says **“Do not edit by hand”** and is generated from `lib/`. Do **not** apply textual patch hunks blindly over current source; regenerate it from the exact current library code after the approved comment fix and check drift.

Muse's `docs/LIBRARY-BOUNDARY.md` FFI/first-class corrections, `lib/kalana.smlib` outdated comment and the other proposal rows are currently **PATCH-PENDING**, not applied. The user explicitly forbids ChatGPT source edits, so leave `lib/kalana.smlib` unchanged.

## Truth table

**PASS — GitHub read-only comparison** of current v326 source, assigned Round108 and previous R107 P0 list; prepared exact current smallest prose replacements.

**NOT RUN - no toolchain:** Sutram compiler, library/proofs, GUI/native Windows, stale-claim scanner, patch application/test, HTML generator.

**NOT APPLIED:** Muse seven-file patch, all Sarvam prose corrections in this Round108 handoff. Sarvam/Muse own implementation. No `src/`, `lib/`, `tests/`, `tools/`, Windows channel, backups or frozen pack changed.
