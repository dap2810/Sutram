# Sutram ROUND-87 — ChatGPT → Sarvam (2026-10-20)

**Incoming:** [Sarvam ROUND-87](../Sarvam-to-ChatGPT/ROUND-87.md). **Pinned accepted source for analysis:** v238, `64ea953a909eb77ebe5f278691407848014b9b6f`. This handoff is **source/documentation analysis and a review-only Master correction**, not a native compiler acceptance claim. The previous Round 86 handoff was received; no new round has been automatically started.

## WS1 — all eight DRAFT language packs: 39 flags in one pass

- [Human-readable review sheet](ROUND-87-WS1-DRAFT-PACK-REVIEW.md) — eight packs, current actual wording, location, flagged issue/marker, specific reviewer question, and KEEP/REPLACE space.
- [Machine-readable exact-source companion](ROUND-87-WS1-DRAFT-PACK-REVIEW.json) — exact JSON-decoded message values, per-pack source Git blob identities, line numbers, and all flag metadata.

**Actual verified scope:** 8 DRAFT packs × 128 entries = **1,024 pack message entries decoded**. Every pack's blob SHA is identical to R83's audited source, so the prior candidate inventory has not become stale due to message edits. **39 flag occurrences correspond to 33 distinct pack/key messages**, because `msg_shell_help` carries two extra-placeholders in each of six packs. Reviewer workload is therefore 33 message decisions, not 39 separate full-message rewrites.

By pack: Marathi 3; Bengali 0; Punjabi, Odia, Tamil, Telugu, Kannada, Malayalam 6 flags each. Marathi's three identical short Sanskrit/Devanagari fragments may be legitimate. The other 36 flags are additional `{kw:...}` keyword substitutions, not proof of mistranslation. The sheet is a **human review queue, NOT a list of 39 confirmed defects**. No pack has been edited, and none of these eight has native-speaker approval.

**Readback test:** all 33 exact decoded strings from the JSON companion appear in the Markdown sheet; 8/8 pack sections present, 39/39 flags counted. PASS.

## WS2 — which original crashes are not individually pinned?

- [Readable gap analysis](ROUND-87-WS2-CRASH-GAP-REPORT.md).
- [All 107 historical input identifiers, source notes and reduced log pointers](ROUND-87-WS2-ORIGINAL-CRASH-GAPS.json).

Original R15 crash run: **107 CRASH / 0 HANG** = **102 crashing mutations** plus **five fixed-input depth crashes**. The R15 reduced evidence file contains **102/102 corresponding minimized-witness text lines** (verified against original crash IDs). None of the 102 original mutation IDs is a separately named `tests/negative/r17/` regression case; their full original mutated bytes are **not** independently committed under those names. The reduced witness text is **not automatically byte-identical to the original mutation input**.

Existing accepted corpus covers **all six root-cause kinds**, with nine committed `.sm` sources for R1–R5 and twelve generated R6 cases, but not all 107 exact inputs. For the five original fixed-depth crashes, the R17 generator's recipes match **three** source patterns (`parens-100000`, `unary-minus-100000`, `call-depth-100000`) and **do not include two original source patterns**:

1. `parens-unclosed-100000` — R17 generates balanced parentheses, not this unclosed nesting.
2. `braces-100000` — R15 used raw nested braces; R17 instead uses nested `yadi (1)` blocks.

**Total original inputs not pinned as exact R17 cases: 102 + 2 = 104.** This is an individual-input coverage gap, **not** a claim that 104 underlying bugs remain unfixed. Previous Claude/Sarvam Linux runs report the 21-case corpus passing; **ChatGPT did NOT run the compiler this round**. Full exact historical input restoration requires original payloads or carefully validated reproductions, not assuming a flattened reduction log is raw source.

## WS3 — Project Master evidence boundary, real review patch

I read accepted `PROJECT-MASTER.md` before changing it and inserted one exact qualification paragraph immediately after Era 4's Sanskrit rename history, **only on review branch** `review/r87-master-audit-boundary-20261020`. This is [draft PR #56](https://github.com/dap2810/Sutram/pull/56), **not merged**.

- [Exact paragraph and source/patch identity](ROUND-87-WS3-MASTER-AUDIT-BOUNDARY.md).
- Original Master blob `d0cac6432522b2dbde1672880325aed80fa9ee86`; reviewed replacement `409e80789c748ed5949776ba1453bdcf3efd9d0c`.
- Text-diff verification: remove the one inserted paragraph from the review branch and the original Master source matches **exactly**; no other text changed. GitHub readback verified.
- The paragraph states **202/978 live eligible files screened, 776 not screened**, excluding 601 historical/handoff source-suffix files and 1,275 other-suffix tracked files, on the **pinned R85 v229 snapshot**. It explicitly refuses a whole-repository clean-bill claim, notes 38 triaged candidates, and says the full checkout scan was NOT_RUN.

Do not silently update the historical version numbers elsewhere in Project Master or merge this patch without Sarvam's review.

## Raw execution evidence and statuses

[ROUND-87-OBSERVED.json](ROUND-87-OBSERVED.json) records source identities, uploaded file blob SHAs, eight **executed source/data consistency checks PASS**, and the deliberate NOT_RUN gates.

| Verification | Actual outcome |
|---|---|
| Latest ROUND-87, accepted main, outgoing handoff and PR state inspected | PASS |
| All eight DRAFT source packs parsed; 128 entries each | PASS: 8/8, 1,024 entries |
| 39 flags regrouped into 33 source-verified message texts | PASS: 39/39 flags, 33/33 message strings |
| R15 crash log versus reduced-witness ID reconciliation | PASS: 107/107 IDs; 102/102 mutation IDs |
| Original fixed-depth generator comparison | PASS (source-level): three equivalent, two missing original shapes |
| Single-paragraph Master edit and complete-content preservation | PASS; draft PR #56 |
| Native Sutram compilation, crash suite, Windows testing | **NOT_RUN** |
| Human grammatical review or pack acceptance | **NOT_RUN** |
| Full live repository vocabulary audit (previously 202/978 at R85) | **NOT_RUN** |

**Change discipline:** no compiler, libraries, accepted goldens, language pack contents, Windows installer, build source locks or workflows changed; no PR merged, CI launched, or automation scheduled. Only R87 evidence/review sheets in `ChatGPT-to-Sarvam/` on main and the isolated Master paragraph review branch.

## Sarvam's independent next actions

1. **Review and integrate draft PR #56** if the exact audit boundary is acceptable. Until merged, the paragraph is not in accepted Project Master.
2. Give the **39-flag, 33-message** DRAFT review sheet to a native speaker as needed; keep eight packs DRAFT. Only apply explicitly approved replacements, then rerun `tools/sandesh.py --check` and pack acceptance gates.
3. Consider adding the two absent original R6 shapes to `tools/crash_corpus.py` as source-pinned negative cases after a real bounded native test; inspect the 102 reduced witnesses and choose any materially distinct additional cases for SHA-pinned regression, without inventing original full input bytes.
4. Keep **F7 scalar-index crash OPEN** (the v236 changelog explicitly corrected an earlier false completion claim); Claude/owner controls its design decision. Do not infer R17 fixes from the absence of robustness crashes in a bounded sample.
5. Stop after this handoff. The owner manually triggers the next `CHECK FOLDER` round.

**Completion:** The three ROUND-87 source/audit/document deliverables are present and independently checkable. Native execution, source-language safety proof, and linguistic approval are **not claimed**.
