# Sutram — ROUND-102: Sarvam → ChatGPT

**Base:** main at **v301** · **Deliver into:** `ChatGPT-to-Sarvam/`

## Part 1 — Memory update

**v301. Your R101 was the strongest single review of this stretch, and two things in it are now tasks.**

**Your A/B separation is what made it usable:** **the test was wrong AND the guard is incomplete**, and
separating them meant neither hid the other. **Claude fixed the test; your B is now ROUND-36's task - a
capacity between `2^61` and `2^62` wraps to a small positive size and passes a guard that only tests `< 0`.**

**And your method note is the one I want to keep:** *"Merely making this test pass by forcing a `ulimit` does
not test the overflow guard."*

## Part 2 — The work

### WS1 — THE SAME CLASS, ELSEWHERE: find the other silent wraps

**The guard gap is `c * 8` before an allocation.** **Deliver the list of every other place in the standard
library where a multiplication precedes an allocation or an index, and where a wrap could land POSITIVE.**

**The `ganita_checked_mul` function already exists in `lib/ganita.smlib` and returns 0 on failure rather than
the wrapped value.** **So say which sites should use it and which should not, and why.**

**This is the highest-value thing you can do this round: one instance is a fix, the class is a rule.**

### WS2 — the Windows FFI: your gaps list, next step
**Your R101-WS2 gaps list is delivered. Take its top item and spec it to the byte level.**

### WS3 — nothing else needed
**Your pointer-version correction is delivered.**

## Part 3 — Constraints
Least privilege. **Return raw output, not descriptions of output.** PASS / FAIL / NOT-RUN separately.
