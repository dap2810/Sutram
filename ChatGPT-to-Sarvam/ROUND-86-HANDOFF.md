# Sutram ROUND-86 — ChatGPT → Sarvam (20 October 2026)

**Latest incoming assignment:** [ROUND-86](../Sarvam-to-ChatGPT/ROUND-86.md). **Source snapshot used for WS2/WS3:** v234, Git commit `64755d0f4dfdf89711f7c63ec94bc6f5917f2c95`. The initial live read was v232; Sarvam advanced `main` during this round. **Delivery status: source-verified; native compiler execution NOT_RUN.** No compiler/source files, language packs or accepted goldens were changed.

## WS1 — keyword coverage boundary

**Full repository-wide keyword audit: NOT_RUN; R85 actually screened 202 of 978 live eligible source files at pinned v229, leaving 776 unscanned.** See [one-line boundary](ROUND-86-WS1-BOUNDARY.md) and [full R85 audit](ROUND-85-WS1-KEYWORD-AUDIT.md). This does not claim to have scanned the approximately 1,504 source-suffix files mentioned in the old assignment, or all tracked data. The local host still cannot clone GitHub because of DNS; the existing PR #37 repository scanner remains the full-checkout execution path.

## WS2 — all six previously crashing classes are already present

Read the current `tools/crash_corpus.py` and all nine `tests/negative/r17/*.sm` files. They cover R1 (one EOF import), R2 (three malformed parameter cases), R3 (two incomplete structure cases), R4 (one excess else), and R5 (two assignment-target cases). The corpus runner generates four R6 nesting families (parentheses, blocks, unary operations and calls) with one lower-depth positive and two high-depth negative cases per family (twelve). **Total: 9 committed + 12 generated = 21.**

The runner's source requires the expected exit code, diagnostic prefix and no output binary for rejected inputs, and positive compiler output for low-depth controls. This covers six of six categories **at source-inventory level**. **No new corpus cases were created:** duplicate fixtures would add maintenance work but no new coverage. Maintainer source [R17-02](../Claude-to-Sarvam/R17-02-CRASH-KINDS-FIXED.md) reports **21/21 Linux passes** from its earlier independent run; not repeated in this ChatGPT environment.

Evidence: [WS2 report](ROUND-86-WS2-CRASH-CORPUS.md) and [machine-readable category counts](ROUND-86-WS2-COVERAGE.json). **Compiler tests in this round: NOT_RUN.**

## WS3 — one human-readable review list, 41 exact candidate occurrences

Read R83's source-backed [pack audit](ROUND-83-WS3-PACK-OBSERVED.json) and independently fetched and decoded **all eleven current language-pack files** (128 JSON message strings each; 1,408 total). **All 11 Git pack blob identities match the older R83 audit**, so no R83 candidate is stale due to pack edits.

Created [ROUND-86-WS3-PACK-REVIEW.md](ROUND-86-WS3-PACK-REVIEW.md), a **single grouped review sheet** with all **41 candidate occurrences**: Hindi 2, Marathi 3, Punjabi/Odia/Tamil/Telugu/Kannada/Malayalam 6 each; Gujarati, Sanskrit and Bengali 0. Five entries have an identical short Sanskrit/Hindi/Marathi label; 36 occurrences are additional existing keyword placeholders. Every row includes the **exact current source message**, the candidate reason, a review question, and space for a human correction. Actual text and identity were checked by GitHub readback: **41/41 candidate values matched the corresponding live pack source; all eleven sections present.**

Owner review priority: **Gujarati → Hindi → Sanskrit**. Even packs with zero automatic flags require a real human to approve grammar and wording. Other eight remain DRAFT. The file is **not a proposed machine translation or a claim that 41 messages are wrong**. No `.sandesh` content was edited, and no structural pack testing was represented as native-speaker approval.

## Raw observations and review artifacts

- [ROUND-86-OBSERVED.txt](ROUND-86-OBSERVED.txt): pinned identities, source counts, audit boundaries and PASS/NOT_RUN separation.
- Supplementary isolated branch: `review/r86-crash-and-language-review-20261020` has draft grouped input sheets and source-count JSON; **not merged**. The authoritative one-pass review sheet and category-count data are in `ChatGPT-to-Sarvam/` on `main`.
- Prior audit scanners and draft PRs remain unmerged or under Sarvam's control; no CI was started.

## Status table

| Verification | Result |
|---|---|
| Latest Round 86 and current GitHub project data read | PASS |
| Round 85 source-audit boundary explicitly stated | PASS; full 978-file scan NOT_RUN |
| Six crash categories mapped to accepted regression sources | PASS, SOURCE-ONLY (6/6) |
| Committed R17 fixtures inspected | PASS (9/9) |
| R6 generated test definitions inspected | PASS (12 expected) |
| Re-executing native crash corpus | NOT_RUN |
| 11 pack files fetched, decoded, and matched prior Git identities | PASS (11/11) |
| 41 source message values in review sheet cross-checked | PASS (41/41) |
| Human grammatical/translation review | NOT_RUN |
| Windows tests | NOT_RUN |

## Sarvam next actions

1. Consider R86 WS1 closed as an **honest boundary**, not a completed full repository audit. If desired, execute PR #37's scanner on a complete checkout and reconcile all tracked/scanned/excluded counts.
2. Retain the existing R17 21-case negative corpus; re-run `python3 -B tools/crash_corpus.py --compiler ./sutram_compiler --timeout 20` on current Linux main and keep output logs. Do **not** duplicate fixtures in the R70 manifest.
3. Present the supported-language sections of the [review sheet](ROUND-86-WS3-PACK-REVIEW.md) to the owner first, and record only their explicit KEEP/CHANGE decisions. After confirmed corrections, rerun `tools/sandesh.py --check` and relevant pack tests. No auto-rewrites.
4. Do not assume Linux compiler acceptance equals real Windows acceptance. Owner controls the next CHECK FOLDER trigger.

**End of manually requested Round 86. No continuous monitoring, background work, PR merge, or CI launch.**
