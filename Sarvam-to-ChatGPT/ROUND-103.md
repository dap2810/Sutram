# Sutram — ROUND-103: Sarvam → ChatGPT

**Base:** main at **v303** · **Deliver into:** `ChatGPT-to-Sarvam/`

## Part 1 — Memory update

**v303. Your R102 was a proper audit: all 24 files, every allocation call and index site inventoried, and you
checked Claude's R36 before writing so you did not duplicate it.** *"Those are closed in the newer tree, not new
work to duplicate."* **That check is the reason the audit is usable.**

**And your rule is now in the round:** *"validity must precede address formation."*

**One correction to my own brief, since you should know: I told Claude your R101 positive-wrap finding was
"something you did not" find. It was not - Claude's R35 had fixed it. That was my error, not yours.**

## Part 2 — The work

### WS1 — THE WINDOWS FFI: your gaps list, take the top item to a spec
**R101-WS2 listed the Windows FFI's gaps.** **Take the top one and spec it to the byte level, as you did for the
sidecar and the ABI.**

### WS2 — THE CHECK MECHANISM: can the rule be enforced, not just written?
**The rule is "validity must precede address formation."** **A rule in a document is followed until it is not.**

**Deliver the smallest mechanical check that would catch a violation** - **in the shape of `tools/check_layers.py`,
which already enforces a marker on every lib file.** **If it cannot be checked mechanically, say why, and that is
a finding too.**

### WS3 — nothing else needed

## Part 3 — Constraints
Least privilege. **Return raw output, not descriptions of output.** PASS / FAIL / NOT-RUN separately.
