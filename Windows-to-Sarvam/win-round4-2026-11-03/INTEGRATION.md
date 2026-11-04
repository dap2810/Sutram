# Integration update after publication

Draft PR: https://github.com/dap2810/Sutram/pull/65

Upstream advanced during this run from `8db98426` to `63079e5e`, including v298 compiler changes in `5357665c`. The verified Round 4 commit is `1b984b5c`, based on Round 3 `a01bd5bf`. **The results in FIXES.md describe that candidate, not current v298 main.**

Do not merge the entire branch over v298 without reconciliation. Claude's R121 handoff preserves `vartani_sandhi` in-place mutation, refuses literal destinations, and guards literal addresses at runtime. Round 3 (inherited here) instead allocates a new result. Main's R121 report identifies `tests/r54_check/raw_valid.sm` as an existing caller depending on mutation: its intended length is 4 after appending to the original buffer. This focused gate was not included in the Round 3/4 gate selection; the suite counts do not certify that compatibility contract. This known inherited semantic incompatibility remains a review blocker.

Recommended integration: retain v298's builtin semantics, independently port the Round 4 `r65_active` PE enablement and Windows harness corrections, reconcile the reference and tests, then rerun native Windows and Linux suites plus R121 and R54 contracts. The removed Round 3 refusal is not present on v298, so no corresponding removal is needed there. Resolve the measured eager-commit cost before general release. Claude remains the merger; no main push or merge was performed here.

The initial report's functional success is intentionally narrower than readiness to merge or ship. Alias bounds, memory cost, and this upstream semantic conflict remain explicit limitations.
