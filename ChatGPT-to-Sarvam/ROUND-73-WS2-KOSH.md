# Round 73 — WS2 kosh reclamation handoff (2026-10-19)

Review: [PR #36](https://github.com/dap2810/Sutram/pull/36). Source design/commands: [R73-KOSH-RECLAMATION.md](https://github.com/dap2810/Sutram/blob/review/r73-repin-and-lexical-audit-20261019/docs/R73-KOSH-RECLAMATION.md).

**Actual source validation: PASS:** renamed compiler core `4b137114d5b67aab0df61e356aad9af94056ae1b`; three unique exact anchors in `.ge_call_koshpush`; 13 input pins covered by source preparer; current blob checks succeeded. Reused the previously tested R71 Linux payload, staged in new paths `src/r73_kosh_reclaim.inc` and `tools/r73_reclaim_prepare.py`. Checked-in production core not modified. Explicit raw alias invalidation proposal is in the detail doc.

**NOT_RUN:** complete staging on full checkout, NASM compilation, integer/float program outputs, retained mmap/VmSize proof, regression gates, Windows VirtualFree. The Linux-only helper rejects PE kosh_push output. Reviewer stage with `python3 tools/r73_reclaim_prepare.py --stage /tmp/sutram-r73-reclaim` and run genuine native acceptance. Do not merge before alias compatibility review.
