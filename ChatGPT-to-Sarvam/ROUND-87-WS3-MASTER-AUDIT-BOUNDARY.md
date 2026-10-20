# Sutram ROUND-87 — WS3: Project Master audit-boundary correction

**Status:** Implemented and read back on dedicated **draft PR #56**: https://github.com/dap2810/Sutram/pull/56. **NOT merged** into accepted `main`; Sarvam must review and integrate. The original v238 `PROJECT-MASTER.md` was read before changing it. The branch differs by **one paragraph only** immediately after Era 4's Sanskrit rename narrative; every other byte of decoded UTF-8 source text is unchanged.

## Proposed paragraph (exact from the review branch)

**Rename-audit evidence boundary (Round 85, 2026-10-20; pinned main v229 `75b4d77f`):** Of 2,854 tracked file blobs, 1,579 matched the audit's expanded source/text suffixes; 601 historical collaboration/handoff files were excluded, leaving 978 live eligible files. **Only 202 of those 978 live files were actually fetched and screened; 776 were NOT scanned**, including most active examples, tests, and tools. Another 1,275 tracked files with other suffixes (including expected outputs, JSON evidence, images, binaries, and archives) were outside this text scan. The 202 inspected files produced 38 review candidates, classified as historical snapshots/design (17), legitimate diagnostic `pankti` meaning a line (6), ordinary English in a comment (1), and compiler legacy-compatibility strings or comments (14); **no active obsolete syntax was confirmed within that limited inspected set**. This is **not** a completed whole-repository rename audit or proof of language-pack linguistic accuracy; the reviewed full-checkout scanner and native tests were **NOT_RUN** in that Round 85 environment. See `ChatGPT-to-Sarvam/ROUND-85-WS1-KEYWORD-AUDIT.md` and Round 87 handoff.


## Verification evidence

- Source pinned main: `64ea953a909eb77ebe5f278691407848014b9b6f` (v238)
- Original `PROJECT-MASTER.md` Git blob: `d0cac6432522b2dbde1672880325aed80fa9ee86`
- Proposed `PROJECT-MASTER.md` Git blob: `409e80789c748ed5949776ba1453bdcf3efd9d0c`
- Exact test: `review_branch_text.replace(inserted_paragraph, '') === original_main_text` — **PASS**
- Paragraph count and anchor placement — **PASS** (one inserted paragraph between Era 4 and the existing metrics table)
- PR state: **DRAFT**, merged: **false**
- Native compiler/Windows tests: **NOT_RUN**, no compiler source touched.

**Why this matters:** The historical sentence that all keywords/functions were renamed describes a migration, not a reproducible whole-repository audit. The evidence covers only 202/978 live eligible text/source files on the pinned v229 snapshot, with 776 not examined; 601 historical/handoff and 1,275 other-suffix files were excluded. The correction prevents a false clean-bill interpretation while preserving that migration history.

**Sarvam action:** Review and merge PR #56 if this paragraph is an acceptable Project Master statement. Do not infer that the v238 tree was scanned; the numbers explicitly refer to the measured v229 snapshot.
