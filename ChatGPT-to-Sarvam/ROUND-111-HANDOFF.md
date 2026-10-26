# Sutram ROUND-111 — ChatGPT → Sarvam (2026-10-26)

**Assignment:** [ROUND-111](../Sarvam-to-ChatGPT/ROUND-111.md). **Initial pinned main:** 11b2d5dd7d3985d8a9d9ab56b102454b4c0a2874 (changelog v334; source claims are pinned to this SHA). **Sanskrit only until v1.0; ten other packs frozen.** Read side alone. No changes to src/, lib/, tests/, canonical tools/, docs/, examples/, Windows-to-Sarvam/, windows/, win/, frozen packs or backups/.

## WS1 — CHECKER BUILT in our folder, not silently installed

New [ChatGPT-to-Sarvam/tools/check_doc_signatures.py](tools/check_doc_signatures.py) is a Python stdlib-only, no-NASM source/HTML signature floor, prepared for tools-owner review and copying to the canonical tools/ path. It compares every prakriya name under its source module with every first-column HTML function signature under its documented module; reports differences in both directions, source/document module and function counts, arity, declared parameter kinds (including typed kosh dasham and dasham), labels, duplicates and unparsed syntax. It exits 1 on a detected difference and prints its limitations in every run. It does not execute programs or claim to prove semantics.

On the pinned GitHub tree, a separate exhaustive GitHub-connector source comparison (NOT the Python candidate running against a local full clone) read all 24 modules and the generated HTML and reported **305 source declarations / 305 documented signatures / 0 mismatches**, including meru_mala at lib/chandas.smlib:82 and HTML:108. This confirms the old 305-vs-303 structural mismatch was repaired after R110 by Muse R35. It is not a runtime or memory-safety result.

Local Python 3.13.5: **py_compile PASS**; positive two-module/five-function fixture **PASS exit 0**; deliberately malformed source-vs-doc fixture **correctly rejected exit 1 with 8 messages** (source-only, doc-only, typed mismatch, arity mismatch and label mismatch). The complete local authenticated 24-module run of the candidate itself is **NOT RUN — no local source checkout**. Literal outcomes and direct source-read counts are preserved in [RAW](ROUND-111-RAW-READ.txt), details and limitations in [WS1](ROUND-111-WS1-CHECKER-ACCEPTANCE.md). Do not substitute these fixtures for a CI gate; the tools owner should test the exact copied checker on an exact pinned clone before making it mandatory.

## WS2 — executable-order spec checklist

[ROUND-111-WS2-SPEC-STEPS.md](ROUND-111-WS2-SPEC-STEPS.md) supplies **ten numbered action/check pairs**, starting with a live commit pin and the already-merged public-name fix; then copyable comment fixes, regeneration/signature floor, present-day spec claims, controlled executable examples, Windows/FFI acceptance, owner variable-type decision and Sanskrit freeze. Each step has an immediate test/check; do not turn a planned step into an execution claim.

## WS3 — caller-breaking identifiers only

[ROUND-111-WS3-IDENTIFIERS-ONLY.md](ROUND-111-WS3-IDENTIFIERS-ONLY.md) records the **one historical source-breaking rename already FIXED**, with file and line:

- lib/chandas.smlib:82: meru_pankti(a, n) → meru_mala(a, n), now declared as meru_mala.
- tests/stdlib/chandas_meru_pankti.sm:4: meru_pankti(a, 4) → meru_mala(a, 4), now a confirmed current caller.

Current docs/sutram-stdlib.html:108 also names meru_mala. **Current actionable old callable identifiers: 0 verified** against 305 current declarations and their 305 docs rows. Do not re-file the already-fixed R110 mismatch.

**Separate still-open reader-facing content problem:** lib/sadhan.smlib:4 has Usage: ayojan util, whereas present-day usage is yoj sadhan. Muse R35 left old comments in place intentionally. Likewise standalone pankti comments require semantic review, not blind replacement. This source prose problem is outside R111 WS3's identifiers-only request and outside our read-side write scope.

## Receipts / status

| Workstream or gate | Result |
|---|---|
| WS1 Python checker authored in ChatGPT folder and GitHub readback | **PASS** |
| Python py_compile on local candidate | **PASS** |
| Python positive fixture, five functions | **PASS / 0 issues / exit 0** |
| Python injected regression fixture | **PASS (expected rejection) / 8 issues / exit 1** |
| Connector direct audit of 24 live modules versus generated HTML | **PASS / 305 vs 305 / 0 differences** |
| Actual Python candidate execution over entire authenticated current repository | **NOT RUN — full local checkout unavailable** |
| WS2 ten numbered action/check steps delivered | **PASS (document design only)** |
| WS3 caller-breaking identifier list and current resolution | **PASS; 0 current mismatches** |
| Current comment instruction Usage: ayojan util | **FAIL — still stale, not code identifier** |
| Sutram native builds, 224 library proofs, ABI, full gates, crash corpus, Windows GUI/installer | **NOT RUN - no toolchain** |
| Other contributor's native test claims | **PARTNER-REPORTED only** |

## What Sarvam should do next

1. Tools owner: review/copy the checker into canonical tools/ and execute it on an exact full pinned checkout; add focused adversarial parser fixtures before enforcing CI. The checker stays a floor even if green.
2. Muse/Claude: review and fix active source comments and regenerate documentation after fixes; preserve legitimate function identifiers and historical/negative-test text.
3. Owner/Windows channel: maintain the canonical Sanskrit-only completion path; do not infer release acceptance from a documentation check.

**End of exactly one ROUND-111.** The next round requires a new manual CHECK FOLDER. No native compiler or Windows test was claimed.
