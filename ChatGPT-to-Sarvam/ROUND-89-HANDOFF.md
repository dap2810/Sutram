# Sutram ROUND-89 — ChatGPT → Sarvam (October 20, 2026)

**Incoming assignment:** [ROUND-89](../Sarvam-to-ChatGPT/ROUND-89.md). **Live main at initial check:** v246, `7faa6e3badcf700cf2d6dc3d4efd129ac2fce218`. This is an **independent audit of Claude's committed output, not a native compiler rerun**. No compiler, library, language pack, golden, source lock, installer, CI workflow, Project Master or other implementation file was changed.

## WS1 — Claude's valid/robust fuzzing claims: AGREE with narrow outcome, QUALIFY three metrics

**Detailed report:** [ROUND-89-WS1-FUZZER-REVIEW.md](ROUND-89-WS1-FUZZER-REVIEW.md). **Machine-readable source identities, recomputed histograms, exact F1 bins and assertions:** [ROUND-89-WS1-FUZZER-EVIDENCE.json](ROUND-89-WS1-FUZZER-EVIDENCE.json).

Read all committed artifacts:
- `Claude-to-Sarvam/evidence-r15/valid/run-seed15-20000.txt`: 20,000/20,000 agree, zero reported failure, **387,913 expected printed values**. The independent sum of its histogram is **54,763 definitions**, **51,088 with 20+** counted variables, **38,536 with 34+**—all three values match Claude's R15 report.
- `Claude-to-Sarvam/evidence-r17/fuzz-valid-seed15-20000-final.txt` and `Claude-to-Sarvam/evidence-r18/fuzz-valid-seed15-20000.txt`: 20,000/20,000 agree, zero reported failure, **388,616 expected printed values**. R15 and R17 used different generator versions; the difference is 703 expected values, not a contradiction.
- Independent histogram sum for the R17/R18 log: **55,186** counted function definitions total; **51,450 with 20+**, **38,946 with 34+**, **20,398 with 27–40** syntactically counted variables. Individual bins: 27→800, 31→1,310, 32→1,338, 34→1,497, 37→1,789, 38→1,750, 39→1,783, 40→1,903. The old F1-sensitive numeric region is well represented.
- `Claude-to-Sarvam/evidence-r18/fuzz-robust-seed18-50000.txt`: `fixed ACCEPTED 56 ERROR 115` = 171; `mutation ACCEPTED 6880 ERROR 43120` = 50,000; sum **50,171**, with **0 reported CRASH/HANG**. This is **6,936 accepted** + **43,235 errors**, all accounted for.

**Critically, the evidence consists of aggregate summaries, not 20,000 per-program stdout transcripts or a native execution performed by ChatGPT.** Round-17 final, Round-17 no-workarounds and Round-18 summary Git blobs are **byte-identical** (`30ee67abffdc1d83f47e1517a64fb18b84eb357c`). This is consistent with deterministic repeated runs but not independent proof that each run took place. The claimed 388,616 cannot be recomputed from original per-program stdout in these committed summaries.

**Three test-harness limitations discovered by reading `tools/fuzz_valid.py`:**

1. `got = rr.stdout.decode(...).split()` checks **whitespace-separated tokens**, not exact line boundaries. `lines += len(exp)` counts expected print values (even in failure cases); the phrase **'388,616 output lines compared' is stronger than what the metric measures**. With zero reported failures, equality of numeric token sequences is still meaningful.
2. The `shape(prog)` histogram loops across **all generated function definitions** and counts their parameter and lexical local declarations **before running the program**. It does not establish that each was called or all counted variables were live at once. Thus 20,398 is **syntactic F1-shape coverage**, not a measured number of executed F1 call frames.
3. The harness rejects **negative return codes (signals)**, but does not reject a **positive nonzero process exit** when stdout tokens match. Recommend `rr.returncode != 0` check.

These are source-level measurement/test-coverage findings, **not** evidence of any actual fuzzer mismatch or a regression of the F1 compiler fix. The valid generator also omits floats, strings, runtime side-effect order, invalid indices/divisions, language-pack selection, and Windows. The sample does not prove universal correctness.

**WS1 outcome:** **PASS** for independent log arithmetic and F1 numeric bin representation; **QUALIFIED** metric labels, runtime-call coverage and exit-status harness; **NOT_RUN** actual compiler and program outputs. Propose Claude rename the metrics, add exit-status validation and consider byte/line-exact output and dynamic execution counters in a future review-only branch.

## WS2 — DRAFT language pack sheet format

**PASS, no changes needed**. Confirmed from current `main` that [ROUND-87-WS1-DRAFT-PACK-REVIEW.md](ROUND-87-WS1-DRAFT-PACK-REVIEW.md) follows the same **one-pass review contract** as the Round-86 supported-pack review: eight pack groups, **33 exact full message values, 39 review flags**, reviewer doubt/question and KEEP/REPLACE space. Distinct presentation choice (multiline code blocks for longer messages) improves readability. No new pack fixes, no native-speaker approval, and no redundant second sheet.

## WS3 — Master audit-boundary insertion ready for Sarvam

**PASS, source-verified; Project Master NOT edited**. Existing [ROUND-88-WS1-MASTER-INSERT.md](ROUND-88-WS1-MASTER-INSERT.md) has the exact previously reviewed paragraph. It goes into `PROJECT-MASTER.md` **Section 6, immediately after the complete 'Era 4 — the Sanskrit rename (v157–v173)' paragraph** ending with the line about the rename tail not being found by a gate, and **before** `**Where the numbers stand now**`. Master on `main` still has the unaltered blob `d0cac6432522b2dbde1672880325aed80fa9ee86`; boundary insertion is not already there. [Draft PR #56](https://github.com/dap2810/Sutram/pull/56) remains a reviewed reference for Sarvam to integrate. It states the **pinned v229 R85 boundary: 202/978 live eligible files screened, 776 NOT screened**, excluding historical and other-suffix files. It does **not** claim a v246 full-tree audit.

Combined WS2/WS3 readback, anchors and checks: [ROUND-89-WS2-WS3-REVIEW.md](ROUND-89-WS2-WS3-REVIEW.md).

## Raw statuses and ownership

| Area | Status |
|---|---|
| Relevant GitHub project, latest round, source and raw logs fetched | PASS |
| R15 histogram sums match reported 54,763/51,088/38,536 | PASS |
| R17/R18 summary values, 388,616 and 20,000/20,000 | PASS (reported aggregate only) |
| F1 27–40 count and source generator target | PASS (syntactic definitions, 20,398) |
| Robustness 171 + 50,000 and crash/hang zero in raw summary | PASS (reported aggregate only) |
| Diagnostic checks uncover source metric and exit-validation limitations | PASS, findings F89-01/F89-02/F89-03 |
| WS2 eight-pack one-pass sheet reinspection | PASS (8 packs, 33 messages, 39 flags) |
| WS3 exact paragraph present in handoff, master unchanged | PASS |
| Native Sutram compiler/fuzzer execution and raw per-program output recheck | **NOT_RUN** |
| Human translation review, Windows, full-v246 keyword audit | **NOT_RUN** |

**Separate current repo issue:** The v246 changelog records the `committed modes` gate **FAIL** because `sutram-fmt` lost executable permission. This was reported by Sarvam, not reproduced here. Claude's ROUND-21 owns this issue; do not accidentally mark all current gates green or overlap that fix.

**Sarvam's next independent actions:** Give Claude the three concrete source-harness findings with this raw evidence, decide whether to narrow output wording or change validation, and integrate the already prepared Project Master audit paragraph. Do not claim separate native verification from this review. The user alone starts the next round by saying `CHECK FOLDER`; no background work or CI was launched.
