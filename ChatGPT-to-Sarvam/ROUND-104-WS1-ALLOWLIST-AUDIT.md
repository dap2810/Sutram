# ROUND-104 WS1 — Allocation allowlist: acceptance is not proof

Pinned main: fc3455320a55d47577c3f05f6dc0d5d886a86cbb (v307). The R103 checker is ChatGPT-to-Sarvam/ROUND-103-CHECK-ALLOC-SIZES.py. The newer authoritative integrated gate is tools/check_alloc_bounds.py (R37). This is a review, not a change to either gate.

## Exhaustive currently written nirmmita expression scan

Read each current source file. All 35 actual calls in nine modules have a spelling in R103's REVIEWED set, with **0 unlisted current spellings**. Counts and exact spellings (repetitions represented by count):

| module | calls | accepted expressions |
|---|---:|---|
| aadhar | 2 | c * 8; c * 4 * 8 |
| brihat | 3 | c * 8 (twice); c * 2 * 8 |
| mala | 1 | sz |
| nighantu | 3 | sz; oldcap * 33 + 1; scap * 33 + 1 |
| roop | 6 | 22 * 8 (twice); 70 * 8; 32 (three times) |
| sangrah | 11 | cap * 33 + 1 (six times); bcap * 33 + 1 (twice); cap * 32 + 1; cap * 8 (twice) |
| shreni | 1 | n * 8 |
| suchi | 6 | 3 * 8; sz (twice); ncap * 8 (twice); 4 * 8 |
| vakyank | 2 | 22 * 8; 70 * 8 |
| **total** | **35** | **35 accepted, 0 unmatched** |

The list is complete **for current call-expression spellings**, not for safe formulas or future legal spellings. This audit read actual lines from current repository source. A complete run of the checker over a checkout was NOT_RUN in this response.

## False positives: allowlist accepts what it should reject

1. **Same token, unsafe origin:** `mala` has `nirmmita(sz)`. Changing the preceding assignment to `sz = c * 8` with no signed/domain check is still accepted by R103; the accepted spelling did not change. A benign-looking `sz` name has no provenance proof.
2. **Wrong function in same file:** any new function inside `mala.smlib` can use `nirmmita(sz)` and pass because the allowlist key is **filename only**. No count-domain/overflow proof or function provenance is required.
3. **`sangrah` accepts `nirmmita(cap * 33 + 1)` with an arbitrary or mismatched caller-supplied cap.** Its validity depends on the actual map/set invariant and metadata, not the expression string alone. The allowlist does not test whether that invariant holds.
4. **An earlier unchecked addition can already have wrapped before a whitelisted variable is supplied.** Nothing in the R103 parser builds a def-use graph or ensures validation dominates address formation.
5. **Parsing gaps:** the scanner works line-by-line, strips text after the first `#`, and searches allocation calls within that line. A call split across lines need not be recognized at all; `nirmmita` inside a string literal could be mistaken for executable code. Both are real limitations of the checker mechanism, not claims of existing source defects.

## False negatives: allowlist rejects safe code

A function that prechecks `c<0` and `c>MAX/16`, then legitimately uses `nirmmita(c * 16)`, is rejected because `c * 16` is absent. So is `nirmmita(32 * 2)`, though this is a safe constant expression; `nirmmita( (sz) )` has a different spelling from allowed `sz` and is also rejected. A new module that performs correct checked multiplication of two counts and verifies `ok[0]` fails until its spelling is added. These are **policy false negatives**, not proof of a broken program.

## The current gate is better, but not complete

`tools/check_alloc_bounds.py` (R37) checks computed allocation sites for an earlier constant upper bound on a variable that feeds the multiplication, with function-scoped exemptions, rather than exact expression spellings. Its handoff reports **25 computed allocations; 6 bounded, 19 exempt, 0 failures**, and the accepted R37 `tools/gates.sh` run reported **33 PASS / 0 FAIL / 1 NOT_RUN**. This is existing partner evidence, NOT rerun here.

The R37 gate still isn't a proof of arithmetic safety: it does not require all variables' nonnegative domains, prove the selected bound is *numerically strong enough*, prove bounds dominate through arbitrary branches/aliases, or verify capacity against real allocation. It explicitly does not mechanically certify addition-based serialization bounds. Its exemptions encode caller invariants that can be violated by untrusted handles. It is **more informative than R103's string allowlist** and should be the primary gate; do not install a duplicate mandatory R103 gate.

**Decision:** the current R103 allowlist is *complete as a spelling inventory* but is simultaneously **too loose as a safety check** and **too restrictive as a source-change gate**. Keep it as optional diagnostic/example until replaced by semantic proof or an acknowledged review-diff mechanism. Require new/all changed formulas to receive explicit review, not automatic claims of correctness; preserve R37 as authoritative. Tests should include deliberately unsafe same-spelling mutations, safe new arithmetic and a multiline parser case as check-the-check controls.
