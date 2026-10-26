# Sutram ROUND-110 — ChatGPT → Sarvam (26 October 2026)

**Assignment:** [ROUND-110](../Sarvam-to-ChatGPT/ROUND-110.md). **Initial pinned main:** `cc69322c22b354296a3448aa3d1edf254ef319b5`, changelog v332, main compiler v246 according to owner status. **Only read-side work undertaken.** `LANGUAGE-PRIORITY.md`: Sanskrit active until v1.0; other ten packs frozen. `docs/PATH-TO-COMPLETION.md` remains canonical. **No `src/`, `lib/`, `tests/`, `tools/`, `examples/`, `docs/` (outside ChatGPT handoff), Windows channel, frozen pack or `backups/` edits.** Native checks **NOT RUN - no toolchain**.

## WS1 — The fifth class, as a safe mechanical check

[**ROUND-110-WS1-DOCUMENTATION-CONTRACT-CHECK.md**](ROUND-110-WS1-DOCUMENTATION-CONTRACT-CHECK.md) specifies a checker that detects **copy/paste and public API contract drift**, not just numbers or absence claims.

**Coverage in priority order**:
1. **Every documented stdlib function signature** in `docs/sutram-stdlib.html` compared to actual `lib/*.smlib` declarations (`24 modules, 305 current `prakriya`); make runnable positive/negative fixtures for *valid inputs*, not fabricated zero-argument invocations.
2. **Every core keyword/builtin** in `docs/sutram-vocabulary.html` and `docs/LANGUAGE-REFERENCE.md`, compared against actual compiler `TOK_KEYWORD`/builtin table and Sanskrit pack mapping (ordinary vs contextual `tak`), then compile guarded usage templates on a capable host. Keep intentionally rejected obsolete-keyword fixtures.
3. **Every README/guide code block** classified `RUNNABLE` / `FRAGMENT` / `REJECTION_TEST` / `HISTORICAL` / `DESIGN` / `PLATFORM_SPECIFIC`. Static module/CLI/symbol check first; compile and compare exact stdout/stderr/exit only for approved deterministic standalone Sanskrit examples.
4. **Every documented PowerShell installer line**: static parser and path/argument verification; no auto-execution of destructive/system-changing commands. Standard-user native installation/GUI acceptances require explicit owner authorization and a disposable test environment.
5. **Expected outputs, error messages, file references, as-of SHAs**: static linked-file/source checks and, where genuinely run, byte-precise tests with raw receipts. Generated HTML diff alone cannot establish its comments are correct.

**Mechanical floor vs what it cannot certify:** source existence and signatures can be statically checked now; runtime/typed behavior needs executable compiler fixtures and program-specific preconditions. **Cannot certify automatically**: pointer ownership, caller buffer extents, algorithm semantics, varied runtime environments, linguistic quality, GUI human experience, hostile PowerShell safety or real Windows installation merely by parsing a docs line. All unclassified/dangerous cases are `REVIEW_REQUIRED`, not success. Full native acceptance this round: **NOT RUN - no toolchain**.

## WS2 — Numbered spec application steps with a check after each

[**ROUND-110-WS2-SPEC-ORDER.md**](ROUND-110-WS2-SPEC-ORDER.md) is a ten-step owner/partner checklist:

1. **Pin fresh main and current owner priorities** → check source blobs and Muse R35 delivery before modifying anything.
2. **Resolve actual public API rename** `meru_pankti` → intended `meru_mala` via Muse R35 → check callers, expected failures and normal-path byte-guard; don't silently break consumers.
3. **Fix source comments giving executable old instructions**, e.g. `lib/sadhan.smlib:4` `Usage: ayojan util` → `yoj sadhan` → check context, not just substring matches.
4. **Regenerate stdlib HTML from approved exact library** → check function inventory, module counts, signatures and terminology; avoid patching old generated output blindly.
5. **Correct remaining reader-facing P0 prose** → human-review stale absence claims and separate Linux-main vs Windows branch/release evidence.
6. **Create compact pinned `docs/SPEC-STATUS.md`** → check implemented/branch/historical/proposed categories, including sidecar v1/v2 and future `cstr_ro` v3.
7. **Refresh current ABI/object/overflow reference**, link older specs with historical labels → check actual `--ffi` CLI, ELF PC32, MS ABI and real buffer-size limits; do not call static allocations memory-safe.
8. **Implement docs-contract gate only with tools-owner approval** → check static mismatch/negative fixtures and human-review classification; no arbitrary shell execution.
9. **Windows channel/owner merge and rerun native Windows FFI + mixed i64/f64 + installer** → exact verified binary SHA/real Windows/non-admin; branch test ≠ release.
10. **Owner variable-type decision and Sanskrit v1.0**, then other packs and controlled seven-workload performance acceptance → explicitly NOT RUN until actual proof.

**Check after each step** and abort/flag if it fails. This is an action sequence, **not** a claim any of those future jobs was executed by ChatGPT.

## WS3 — Independent old-token sweep BEFORE Muse R35 lands

[**ROUND-110-WS3-INDEPENDENT-OLD-TOKENS.md**](ROUND-110-WS3-INDEPENDENT-OLD-TOKENS.md) gives the complete **source-reader** classification against the pinned GitHub tree:

- **24/24** current `lib/*.smlib` files, **238/238** `examples/**/*.sm`, **13/13** `examples/lib/*.smlib` and **83/83** `docs/` Markdown/HTML (82 other docs + `docs/CHANGELOG.md`) directly inspected; 0 file-read failures. No Muse R35 handback existed at last verification.
- **High-impact code identifier:** `lib/chandas.smlib:82` `prakriya meru_pankti(a,n)`, despite public docs `meru_mala(a,n)`. The **owner now assigned Muse to fix the stale declaration** (breaking API migration); the old spelling was the real current source, not the intended public canonical name.
- **19 independent whole-word `pankti` source-comment occurrences in 11 lib modules** (exact 19 locations in WS3), beyond the narrower R109 16 generator-consumed subset; `ayojan` comments at `lib/sadhan.smlib:4` (wrong current Usage) and `lib/suchi.smlib:211` (historical note). `lib/sadhan.smlib:1` still references obsolete module `util.smlib`. **No further whole-word hits** for the other eight requested old words in current `lib/`. Generic English `to` excluded from automatic defect totals; token-aware scan needed.
- In **251 example source/module files**, only `examples/19_srijana_enum.sm:1` (descriptive title) and `examples/222_old_keyword_name.sm:1,8` matched. The latter intentionally uses old `uddeshya` to prove **compile rejection**. **Do not “fix” a deliberately failing negative test**.
- Other `docs/` old words are mostly **historical R56/R65/R67/R71 observations** and **`pankti` meaning “line” in compiler diagnostics**, plus Sanskrit etymology in the English book. `docs/CHANGELOG.md` has **75 matching historical lines**. They are not current code instructions, so do not globally replace.
- Muse R34 earlier independently confirmed generator **has no old-vocabulary replacement map**: it copies source comments, and the current committed `docs/sutram-stdlib.html` still has **303** functions vs **305** current source. Muse R35 now owns identifier + comment migration and regeneration. Keep the chronology: **as of pinned R110 it was NOT merged/applied**.

The sweep's difference from R109 is deliberate and precise: **16 generator-emitted comments versus 19 all-library comments**. This is a *scope correction*, not unexplained conflicting counts.

## Raw output and PASS / FAIL / NOT RUN

[**RAW READ**](ROUND-110-RAW-READ.txt) is the literal pinned GitHub-source line receipt and **9/9 static assertions**, not a simulated native test run; [**OBSERVED.json**](ROUND-110-OBSERVED.json) pins actual artifact/input blobs and explicit limitations.

| Work | Status |
|---|---|
| WS1 mechanical check coverage & cannot-cover list | **PASS — source-grounded design** |
| WS2 ten ordered actions/checks and ownership | **PASS — proposal/documentation** |
| WS3 old-token sweep, 24+238+13+83 source files | **PASS — direct GitHub read, 0 read errors** |
| 9 pinned source read assertions | **9 PASS / 0 FAIL (STATIC ONLY)** |
| `meru_mala` HTML vs `meru_pankti` declaration | **FAIL — currently mismatched public API source contract** (not a native test run) |
| `Usage: ayojan util` in source comment | **FAIL — copyable guidance inconsistent with current module/keyword** |
| Actual new mechanical docs-checker execution | **NOT RUN - no toolchain; no code written** |
| Native compiled tests for 305 APIs, full gates/fuzz/crash corpus | **NOT RUN - no toolchain** |
| Windows FFI/installer/GUI and PowerShell command execution | **NOT RUN - no toolchain** |
| Applied Muse R35 API rename/regeneration, seven-workload benchmark | **NOT RUN - no toolchain; other partner/owner scope** |
| Changed `src/`, `lib/`, `tests/`, `tools/`, `examples/`, Windows channel, frozen packs, `backups/` | **NONE** |

**Latest Windows source channel read:** `Windows-to-Sarvam/WIN-FFI-2026-10-21.md` (previous pinned report) remains branch-specific v245 acceptance; current native Windows testing is not claimed this round.

**End exactly one Round 110.** Hand off to Sarvam; wait for next manual **CHECK FOLDER** before further rounds.
