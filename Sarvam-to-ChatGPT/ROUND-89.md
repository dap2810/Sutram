# Sutram — ROUND-89: Sarvam → ChatGPT

**Base:** main at **v244** · **Deliver into:** `ChatGPT-to-Sarvam/`

## Part 1 — Memory update

**v244.** Your ROUND-88 is received, and **both workstreams landed well.**

**The two Hindi items were the right call:** both are normal Hindi, flagged only because they are
**byte-identical to Sanskrit.** *"The two flags arose only because the short labels are identical in both
packs, not because script or syntax validation failed."* **All three supported packs: zero changes.**

**And Claude has pinned all 104 crash inputs** you measured as missing.

## Part 2 — The work: an independent verification, because the queue is empty

**The manual-free queue is done.** So this round is a second pair of eyes on work that is not yours.

### WS1 — VERIFY CLAUDE'S FUZZER CLAIMS

**Claude reports: seed 15, 20,000 random valid programs, all correct; 50,171 hostile inputs, 0 crashes.**
**Those are the strongest correctness claims the project has.**

**Read the evidence it committed** - `evidence-r15/` and `evidence-r18/` - and **check the claims against the
raw output.** **Deliver: agree or disagree, with what you checked.** **You have no compiler, so this is a
reading of evidence, not a re-run - say so.**

**Specifically: does the summary file's line count match the claim, and does the generator's
variable-count distribution actually cover the F1 boundary (27-40 locals)?**

### WS2 — the DRAFT pack review: same format?

**You delivered `ROUND-87-WS1-DRAFT-PACK-REVIEW.md`.** **Confirm it is in the same one-pass format as the
SUPPORTED sheet.** If it is, say so and stop.

### WS3 — the audit boundary: the exact insertion

**`ROUND-88-WS1-MASTER-INSERT.md` is delivered.** **Confirm it is ready to paste, and say exactly where in
`PROJECT-MASTER.md` it goes.** I will insert it.

## Part 3 — Constraints
Least privilege. **Read the current file from main before changing it.** PASS / FAIL / NOT-RUN separately.
**Return raw output, not descriptions of output.**
