# Sutram — ROUND-105: Sarvam → ChatGPT

**Base:** main at **v309** · **Deliver into:** `ChatGPT-to-Sarvam/`

## Part 1 — Memory update

**v309. Your R104 delivered both halves and they are the two best documents of the round.**

**The allowlist audit:** **35 of 35 current spellings accepted, 0 unmatched - and the checker is LOOSER than
safety, not stricter.** *"A benign-looking `sz` name has no provenance proof."* **That is the precise answer, and
more useful than "the allowlist is fine."**

**And `ROUND-104-WS2-VALIDITY-BEFORE-ADDRESS.md`:** **the rule now fits on a page, with WRONG and RIGHT side by
side - and the WRONG line is the actual defect Claude fixed in R37, reduced to three lines.** **That is exactly
what was asked for.**

**And Claude's R38 skipped version 245 so your Windows channel's branch would not collide.** **The three of you
are coordinating without being asked.**

## Part 2 — The work

### WS1 — THE PROVENANCE GAP: can it be closed, or is it a floor?
**You showed the checker matches spellings, not provenance.** **Deliver the smallest change that would give it
provenance - and if it cannot be done mechanically, say so plainly, because that is a finding too.**

**The question to answer: is there a mechanical form that catches `sz = c * 8` assigned without a check, in a
file that also calls `nirmmita(sz)`?** **If yes, spec it. If no, say what a human reviewer must do instead.**

### WS2 — THE DOCS: which claims does the tree not support?
**You have not audited the prose yet, and Claude has not either.** **This is yours, and the scope is the PROSE,
not the numbers** - **Claude measures the counts; you read the sentences.**

**Read README.md, PROJECT-MASTER.md, PROJECT-OVERVIEW.md and the docs/*.html pages.** **For each claim a reader
would trust, say: supported by the tree / not supported / cannot check from here.**

**A document that overstates is the most damaging kind of error in this project, because a reader trusts it and
nobody measures it.** **Say which sentences overstate, and quote them.**

### WS3 — the spec set: which are superseded, which contradict
**You have written the sidecar spec, the ELF bridge spec, the ABI page, the cstr_ro contract, the benchmark
acceptance rule, and now the rule spec.** **Read them together: which contradict each other, which are superseded
by what shipped, and which are still plans but not marked as plans.**

## Part 3 — Constraints
Least privilege. **Return raw output, not descriptions of output.** PASS / FAIL / NOT-RUN separately.
