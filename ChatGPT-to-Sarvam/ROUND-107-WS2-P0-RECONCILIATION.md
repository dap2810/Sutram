# Sutram ROUND-107 WS2 — Which previous false claims are now fixed?

**Initial live source pin:** `fd48619526f6dde6c2b21c7b37ee1bf56f2c505f` (23 Oct 2026, changelog v322). This page deliberately starts from [R106's actionable list](ROUND-106-WS1-ACTIONABLE-PROSE-CORRECTIONS.md) and reads the NEW tree again. `LANGUAGE-PRIORITY.md` and `docs/PATH-TO-COMPLETION.md` govern if older prose conflicts. Sarvam, not ChatGPT, is applying prose edits. Status values: **APPLIED**, **PARTIAL** or **STILL OPEN**; no compilation was performed.

## Applied — close these tickets, do not re-issue

| Prior finding | Current source evidence | Status |
|---|---|---|
| README said no separate compilation, no first-class functions, Windows GUI had never run | `README.md` blob `599f1cc5078e43530ddc572af4a5e84f851ce253`, known limits `:146–160` now discuss actual outstanding limits (no concurrency, manual memory, X11 Indic font, imperfect proofs); former false negatives absent. | **APPLIED before R107.** |
| Old Windows roadmap denied native Windows execution / separate compilation | `docs/sutram-roadmap.html` blob `235c68e63ad36d51243bd1c82b532d9a762dfbe4` now describes real Windows 16 required checks and object-based separate compilation near `:130–131`. | **APPLIED before R107.** |
| Scorecard denied first-class functions/methods/slices in one row | `docs/sutram-scorecard.html` `:206` says they landed. **But `:150` still says “no C FFI”**, so do not call the whole file fixed. | **PARTIAL.** |
| Master performance: memory “Sutram wins” despite Zig 120 KB lower; runtime “wins” despite tie; overall four of five wins | `PROJECT-MASTER.md` blob `480adad1ab5f0c209479e985d50c401497afd7ac` `:270–275` now says **“Zig wins by 120 KB,” “Sutram and Zig tie,” “two measured wins … two measured losses … one tie.”** Its historical measurement cells are preserved. | **APPLIED at v321 (`aafaed38`).** |
| Overview denied object compilation, function values, methods in its first line | `PROJECT-OVERVIEW.md` blob `3366312395ab9c23aff740176ecd57061c5ab0e2` `:159` now opens with acknowledgment of those features. **But the paragraph continues “No first-class functions.”** | **PARTIAL and still internally contradictory.** |
| Doc counts/overview build entry | Prior R39 updated measured numbers and changed `PROJECT-OVERVIEW.md` build input to `src/r68_compiler_entry.asm`. | **APPLIED**, do not reopen the older number/build-entry defect. |

## STILL OPEN — remaining P0 present-tense claims in the pinned R107 tree

These are current **file:line + actual quote**; the smallest replacement text is already in R106 WS1 and need not be expanded again.

| File / lines | Still present in v322 | Action |
|---|---|---|
| `PROJECT-OVERVIEW.md:153–155` | **“Nobody has run the Windows GUI on real Windows”**, **“Windows installer has never been executed on Windows”** | Replace absolutes with **owner's real native non-elevated acceptance on pinned older revision**, not current-release acceptance. |
| `PROJECT-OVERVIEW.md:159–160` | After its new “Separate compilation ... exists,” it still says **“No concurrency. No first-class functions. No collections beyond kosh and mala.”** | Replace **the complete mixed old/new paragraph**, not merely prepend another corrected sentence. |
| `PROJECT-MASTER.md:80,82–83` | **“functions exist, but not first-class”**, **“no methods or traits”**, **“no slices or SIMD”** | Acknowledge R23 function values, methods and slices; retain missing traits/closures/SIMD. |
| `PROJECT-MASTER.md:107,110–111` | **“Windows never executed”**; **“Not started | No C FFI”**; **“no fuzzing, no cross-platform run”** | Distinguish Linux-main FFI, native older Windows tests and unmerged v245 Windows FFI, and existing fuzz evidence. Fix charter row labels with the v1.0 rubric. |
| `PROJECT-MASTER.md:360–362` | **“Two of them — Windows execution and the freestanding boot — have never been performed by anyone”** | Windows execution was performed; **freestanding boot** remains unproven. The master itself acknowledges real Windows in `:306–311`. |
| `docs/sutram-design-parameters.html:157–159` | **“functions exist ... but they are not first-class”** | Current function values exist, closures/pattern matching remain incomplete. |
| `docs/sutram-design-parameters.html:178–180` and `:189–191` | **“no methods”**, **“there are no slices”** | Methods and slices exist; keep missing traits/layout/SIMD. |
| `docs/sutram-design-parameters.html:304–305` | **“layers are not formally separated — nothing marks which modules are allocator-free”** | Current `# layer` markers and `tools/check_layers.py` enforce 14 core/9 alloc/1 std as measured previously. |
| `docs/sutram-design-parameters.html:315–316` | **“Windows x86-64 ... never been executed”** | Real Windows owner acceptance recorded, not current merged-release proof. |
| `docs/sutram-design-parameters.html:327–329` | **“There is no separate compilation”** | Object mode and project-owned linker now exist; package manager/lockfile still absent. |
| `docs/sutram-design-parameters.html:364–366` and `:377–381` | **“there is no FFI”** and **“Missing ... fuzzing, and cross-platform execution”** | Linux FFI exists, branch Windows FFI tested, fuzz and real Windows tests reported. A fully formal/memory-safe ABI remains missing. |
| `docs/sutram-project-status.html:146–147` and `:154–155` | **“Windows ... Unverified / Never executed by this project,” “installer itself untested on Windows”** | Owner pinned acceptance exists. Keep tested-version vs current-release split. |
| `docs/sutram-project-status.html:181–182` and `:190–191` | **“No first-class functions ... methods ... slices”**; **“Not started Interoperability ... No C FFI”** | Function values/methods/slices and Linux FFI exist. Change categorical labels only with review; don't blindly recompute summary percentages. |
| `docs/sutram-project-status.html:212–219` and `:227–228` | “**Windows acceptance — the one gate nobody has run**” and **“no run has ever produced a verified executable.”** | The current “What's open” panel is years/rounds stale; point at `docs/PATH-TO-COMPLETION.md` instead and mention prior real acceptance. |
| `docs/sutram-scorecard.html:150` | **“there is no C FFI and no calling convention for foreign code.”** | SysV FFI exists on main, Microsoft x64 FFI tested on unmerged review branch. |
| `docs/sutram-scorecard.html:158,166,174` | “**21 modules**”; “**a 136-test suite**”; “**No ... phal types**” | Current counts are 24 modules, 218 pass+4 no expectation; `lib/phal.smlib` defines a library Result convention, not a language-enforced Result/propagation type. Preserve that difference. |

## Other priority/status contradictions — retain in review queue

- `PROJECT-MASTER.md:209–225` still tells developers to build **Sanskrit, Gujarati, Hindi in parallel**, with Gujarati first. **SUPERSEDED** by owner's 23 October **Sanskrit-only** directive. Keep as an explicitly labeled old policy, not active instruction. No frozen-pack edits.
- `PROJECT-MASTER.md:331–337` still says old `ROADMAP-TO-V1.0.md` is single source of truth and separate compilation belongs to a future v2. Current canonical owner path is `docs/PATH-TO-COMPLETION.md`, and object compilation exists.
- `docs/sutram-stdlib-reference.html:122–123` overstates **“Safe anywhere, including a freestanding program”**: core layer is OS/allocator-independent in source but no native freestanding boot or memory-safety proof exists.
- `docs/_newchapter_en.html:83,95–97` is an old draft saying the Windows IDE is unavailable and Windows never tested; archive/date-label it or correct its two claims.
- `docs/sutram-performance.html:60–63` is a dated performance discussion claiming speed is the top priority; current policy says Sanskrit-first release before performance.
- `docs/PATH-TO-COMPLETION.md` is dated v315 and retains the earlier allocation 25/6/19 measured snapshot; R39 subsequently reported 26/13/13. **Do not quietly overwrite Sarvam's pinned measurement without running a fresh check**.
- The *design charter's aspirations*, such as “memory safety by default,” remain clearly marked as goals; don't misclassify as present safety claims.

## Before applying, RECHECK

Sarvam says it is applying the claims while this round runs. This list is **not permission to overwrite a more recent correction.** For each row, fetch current main and compare the sentence: if absent, mark **APPLIED**, not a new error. Source proof at this pinned base: `README.md` `599f1cc5`, Overview `33663123`, Master `480adad1`, design HTML `81d46eab`, status HTML `40022601`, scorecard `8f8f537e` and roadmap `235c68e6`.

**Evidence:** PASS — actual current-source reads / earlier fixes explicitly classified. **NOT RUN - no toolchain:** native compiler/GUI/Windows/regression/HTML generator. ChatGPT did not alter any of the source prose; Sarvam applies it. 
