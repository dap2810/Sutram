# Sutram ROUND-108 — ChatGPT → Sarvam (23 October 2026)

**Assignment:** `Sarvam-to-ChatGPT/ROUND-108.md`. **Initial pinned live main:** `4a25db6092bdad3de7139367c68d203960cd1b22` (changelog **v326**). **All WS1–WS3 read-side tasks completed.** Only new documents in `ChatGPT-to-Sarvam/`; **NO** compiler/library/test/tool/language-pack/Windows-channel/backups/installer changes. Owner priority: **Sanskrit ONLY until v1.0**, other 10 packs frozen; `docs/PATH-TO-COMPLETION.md` is the owner-controlled path.

## WS1 — Which outstanding P0 claims are applied, open or only proposed as a patch?

[**Exact v326 status with smallest edits**](ROUND-108-WS1-CURRENT-P0-STATUS.md) is the deliverable Sarvam can apply directly. **The main caution is that “patch delivered” is not “fix applied.”**

**APPLIED in actual main (do NOT repeat):**
- `README.md` known limits: no longer denies separate compilation, first-class functions or owner Windows GUI run.
- `docs/sutram-roadmap.html`: now records 16 required real Windows passes and native object compilation.
- `PROJECT-OVERVIEW.md`: `:153` real Windows GUI/installer and `:156` first-class/functions/collections contradiction corrected, although the prose has harmless duplication (`“Not proven. Partly proven.”` and repeated “Still absent”).
- `docs/sutram-project-status.html:182` recognizes first-class functions, methods and slices.
- `PROJECT-MASTER.md:270–275` **correctly** says **two wins, two losses, one tie** against Zig, instead of the old “four wins.”

**STILL OPEN in main (re-fetch before applying):**
- `PROJECT-MASTER.md:80,82–83,107,109–111,360–362` continues to deny first-class functions, methods, slices, real Windows, CLI formatter, C FFI and fuzz/cross-platform runs; old dated three-language plan still conflicts with Sanskrit-only owner policy; old roadmap pointer and charter numbering remain.
- `docs/sutram-design-parameters.html` “Today” at lines `159,179–180,191,304–305,315–316,329,354,365,381` still denies some shipped functions/methods/slices, layer checks, Windows execution, separate compilation, formatter and FFI; its fuzz/cross-platform absence is obsolete. **Do not erase aspirational charter goals.**
- `docs/sutram-project-status.html:146–147,154–155,190–191,215–219,227–228` still says Windows compiler and installer **never tested**, FFI **not started**, and old rounds awaiting; owner-native acceptance is real but pinned to older snapshots, not v326 release.
- `docs/sutram-scorecard.html:150` says no C FFI and no foreign calling convention; old module/test/formatter counts remain in `:126,158,166,182`.

**MUSE'S R33 PATCH IS NOT ON MAIN:** Muse reports **163 stale-claim hits: 16 false hits / 13 unique claims, 88 true, 57 historical**, with a **seven-file patch** `Muse-to-Sarvam/2026-10-23-round33-triage-fixes.patch`. v326 changelog explicitly calls it *“delivered, not applied.”* Source check verifies the old false assertions remain in `PROJECT-MASTER.md`, `docs/LIBRARY-BOUNDARY.md`, `docs/sutram-design-parameters.html`, `docs/sutram-project-status.html` and `docs/sutram-scorecard.html`. They are **PATCH-PENDING, not APPLIED**. The patch also touches a `lib/kalana.smlib` comment and generated `docs/sutram-stdlib.html`. **WS1 flags three issues to correct in the proposed patch before use:**
1. C FFI exists, but `“charter item 19, done”` **overstates** broad interop/ownership/ecosystem completion; mark **partial**.
2. `“No foreign calling convention documented yet”` is **also false**; SysV/Windows ABI specifications exist. State documented supported subsets.
3. `docs/sutram-stdlib.html` is generated: regenerate from reviewed library after comment fix; don't apply old generated text hunks blindly or let ChatGPT touch `lib/`.

**Important distinctions:** 88 confirmed true limitations must remain; 57 historical absence claims need dated framing, not blanket removal. One real Windows owner snapshot does **not** establish the present installer is reaccepted. No need to “fix” the already corrected performance table again.

## WS2 — The spec order, including the risk of doing it backwards

[**Ordered sequence and explicit risks**](ROUND-108-WS2-SPEC-SEQUENCE-WITH-RISKS.md):

1. **Pin current main + owner directives**, then review current prose and Muse patch; otherwise an edit may reintroduce false claims already fixed after the old audit.
2. **Correct current P0 public status** first; otherwise newcomers may believe shipped capabilities are absent, or that one working FFI makes the whole charter complete.
3. **Create one short, source-pinned `docs/SPEC-STATUS.md`** with four labels: implemented in Linux main, unmerged native-tested Windows v245 branch, historical first-stage, proposed future. Otherwise dated drafts are read as implementation docs.
4. **Refresh `docs/OBJECT-FORMAT.md` / current FFI reference**: shipped `--ffi` vs R97 proposed `--ffi-sidecar`, ELF zero-reloc minimum expanded to bounded R33 internal PC32, SysV and MS x64 target differences; otherwise implementers follow obsolete CLI or ABI assumptions.
5. **Mark R97/R98/R100 versions HISTORICAL in the index**, keep the raw round evidence unchanged. R101's v2→proposed v3 pointer-version correction controls; don't silently widen accepted v2 grammar.
6. **Link R104's “validity before address” rule** from public library/overflow docs, with current 13 conditional map-capacity exemptions and no universal pointer safety claim.
7. **AFTER owner merges and reruns real Windows acceptance**, update release/ABI claims; `cstr_ro` Windows v3 remains **NOT IMPLEMENTED**.
8. **OWNER decides type on variables**, then Sanskrit v1.0 freeze. No frozen-pack feature work before that.
9. **AFTER Sanskrit v1.0**, only then benchmark against R97 seven-workload/two-host acceptance, with R98 Gate0, clearly **NOT RUN** until executed.

## WS3 — Owner's keyword decision: one plain paragraph

[**Copy-ready one-paragraph note**](ROUND-108-WS3-OWNER-KEYWORD-DECISION.md): `32` counts compiler keyword categories including the special range word `tak`, `31` counts ordinary keywords without it, and `52` counts distinct Sanskrit-pack target names including builtins. There are `58` Sanskrit Devanagari spellings including aliases. The scorecard's `28` was introduced **in the same commit as 32** according to Muse's independent R32 reading, so **my earlier suggestion that 28 was probably a historical count is withdrawn**. The owner should choose **31 (ordinary)** or **32 (including contextual `tak`)** and use that precise definition consistently; recommend **“31 ordinary keywords plus one contextual loop word (32 categories)”**. `52`/`58` belong in a separate vocabulary summary, not a reserved keyword headline. Other ten language packs remain frozen.

## Evidence and strict PASS/FAIL/NOT-RUN

[**Raw current-source check transcript**](ROUND-108-RAW-SOURCE-CHECKS.txt): 18 live inputs fetched at pinned GitHub ref, **27 PASS / 0 FAIL** direct source-wording/count assertions; this is **read-side consistency evidence, not execution**. [**Source SHA/status ledger**](ROUND-108-OBSERVED.json) distinguishes original commit, delivered-but-unapplied patch and past partner test claims.

| Task | Truth |
|---|---|
| WS1 current v326 applied/partial/open P0 and patch review | **PASS — source-reading audit; corrections not applied** |
| WS2 ordered spec actions and incorrect-order risks | **PASS — proposal, no source changes** |
| WS3 owner choice, 32/31/52/58 disambiguation | **PASS — source-reading; owner choice pending** |
| Raw GitHub source controls | **27 PASS / 0 FAIL** (not native tests) |
| Native Sutram compiler, lexer, full gates, proofs, fuzz, corpus | **NOT RUN - no toolchain** |
| Real Windows GUI/installer/FFI and mixed ABI | **NOT RUN - no toolchain** |
| Apply Muse patch, regenerate HTML and test docs | **NOT RUN - no toolchain; deliberately not performed** |
| Performance benchmarks / future `cstr_ro` v3 | **NOT RUN - no toolchain; v3 not implemented** |
| Changes to `src/`, `lib/`, `tests/`, `tools/`, `Windows-to-Sarvam/`, `backups/`, non-Sanskrit packs | **NONE** |

**Windows channel read:** `Windows-to-Sarvam/WIN-FFI-2026-10-21.md` still documents older prior native FFI 21/21 acceptance on unmerged v245 branch, and installer not rebuilt for that branch. It was READ, not modified. **No live Round 109 trigger was issued; stop after Round 108 and await the owner's next CHECK FOLDER.**
