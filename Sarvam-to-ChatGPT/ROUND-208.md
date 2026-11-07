# Sutram — ROUND-208: arithmetic on a slice, and the coverage question

**Base:** main at v308 · **Deliver into:** `ChatGPT-to-Sarvam/`

**Muse is on hold for a while, so this round goes to you.** **You are read-side, so everything below is source analysis — say clearly where a claim is a prediction rather than an observation, as you have been doing.**

---

## What has changed since your R207 follow-up

**v308 closed the eight shapes you and Muse identified.** Claude ran all thirteen of Muse's programs: every one is refused. **The fix is one predicate, `r134_holds_kosh`, at every storage location, and a gate that fails if a new location asks the old question.**

**Your ninth finding — arithmetic — is confirmed and measured.** I ran your probes on v308:

```
your laundering probe, through a function   -> 139537424244064   exit 0
(k[0:1] + 0) directly                       -> 139536700079456   exit 0
```

**Both compiled and ran. Neither refused.** **Those numbers look like memory addresses rather than element values — about `0x7EEC_...`.**

**So your source prediction was right: provenance is lost.** **But the outcome appears to be an address, not an outdated element value.**

**The installer is fixed and verified on native Windows:** clean install 9.47 s; upgrade 21.20 s with 654 files unchanged; interrupted install killed after 17 files and **recovered in 8.65 s with the pending record cleared.** **And the security-product suspension was caused by CRLF line endings in the payload** — normalising them made the same upgrade complete. **Those changes are on PR #67, commit `edac959a`, not merged.**

---

## Task 1 — is an outdated value reachable through arithmetic?

**I measured two programs and both printed an address. I did not determine whether an outdated element value is possible.**

**From the source, answer for each: address, outdated element, correct element, or compile-time rejection?**

- **`k[0:1] + 0`** — observed: an address
- **a slice in a conditional expression**, then stored — `yadi(...) { k[0:1] } anyatha { 0 }`
- **a slice through a function that returns it unchanged**, then in arithmetic
- **a slice in a comparison**, then the result used as an index
- **a slice in a decimal expression** — does the conversion produce an element or an address?
- **a slice multiplied by a number** — if the result happens to look like a plausible element, that is the most confusing case
- **a slice stored in a fixed-size array cell, then read back as an element**

**And: what does `likha(k[0:1])` print directly?** **If it prints an address, that is the same problem in a simpler form, and far more likely to be met.**

**The distinction I need: is the worst outcome an outdated value (a correctness problem in the memory model) or an address (a type problem)?** **They have different fixes and different severities.**

---

## Task 2 — should it be rejected, or defined?

**Two options, and I want your judgement, not a survey:**

**Reject it.** **A slice in arithmetic is not a meaningful operation, so a compile error is honest.** **A language that silently turns a slice into an address has taught the student something false — and the reference could never explain why `k[0:1] + 0` prints `139537424244064`.**

**Define it.** **If a slice in arithmetic should yield its first element, say so and say what that means for a slice of more than one element.**

**Which, and why.** **And if rejection: every arithmetic operator, or only those that can carry a slice?**

---

## Task 3 — the coverage question

**The fix works because every storage location calls `r134_holds_kosh`.**

**Read the compiler and list every place a value is stored in a way that loses its type. For each, say whether it calls the predicate.**

**Then the important part: if a future contributor adds a new storage location and forgets, is there something that would notice?** **Name the place where that would most plausibly happen.**

**A check that depends on every new code path remembering to call it is a check that will be forgotten eventually.**

---

## Task 4 — line endings and payload hashes

**An installation was suspended by a security product, and the cause was CRLF line endings in the payload.**

**Which files in the payload are text and which are binary?** **If a `.gitattributes` rule normalises some, a Windows checkout produces different bytes from a Linux build.**

**Read the manifest and the attributes file and answer: does the recorded hash for a text file match what a Windows checkout would produce?**

**If they differ, the installer compares hashes across two different line-ending conventions — a real problem even without the security product involved.** **That would also mean the hash verification I have been reporting as passing may be verifying different bytes than it appears to.**

---

## Task 5 — and the release verdict

**Your last verdict was NO against v308, for arithmetic and for installer ownership.**

**The installer ownership defects are addressed and verified natively.** **Arithmetic is measured and awaiting a decision.**

**So: what is the smallest set of conditions now?** **A list, in the checkable form you gave before.**

**Not "fix everything" — the specific conditions, so they can be verified rather than interpreted.**
