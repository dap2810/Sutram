## THE SHARED STATE - 11 November 2026

**`Sutram 1.0 (v315)` on main. Chain staged to v324. Nine plan items closed.**
**A whole-tree audit has now been done and its verdict is: THE TREE IS NOT RELEASE-READY. 47 finding groups - Tier 1 = 14 (silent wrong answer or guidance that induces one), Tier 2 = 7 (wrong message), Tier 3 = 26 (invisible). 11,361 files inventoried.**

**WHAT THE AUDIT FOUND, in its own words**
- **the Linux compiler rebuild is byte-identical to the committed binary**
- **suite 327 passes, four missing goldens; crash corpus 227/0**
- **the negative-digit silent-answer defect is fixed on a candidate branch, with three verification defects and selected misleading documentation**
- **open on main: signed/final-line input, the `LCM(MIN,0)` refusal, and the memory/loop boundaries**
- **the installer payload is stale relative to the source candidate**
- **and: *"Do not merge or release it on this report alone."***

**THE FOURTEEN TIER 1 FINDINGS, abbreviated**
**R01 `likh8`/`pad8` documented as eight-bit; they emit qword store/load - eight bytes.**
**R02 `likh8c`/`pad8c` documented as character I/O; they are guarded memory accesses with no lower-bound check.**
**R04 `grahan` documented as "reads a number"; it accumulates ASCII digits.**
**R05 `aksharank` documented as ignoring its index; it uses argument 2 when present.**
**R07 "varna"/"character" used without a unit - bytes or scalars.**
**R08 `vartani_tul` returns 0 for equal and 1 for greater; the reference says only "compare".**
**R11 `nirmmita` documented as giving zeroed bytes; main only advances the cursor.**
**R14 `lib/brihat.smlib:71` - `brihat_ank_tak_laghu` checks `d <= 9` and never `d >= 0`.**
**R15 `brihat_ank_se`'s failure mutation described wrongly.**
**R17 `purna_prasaran` variance contract too broad.**
**R24 `madhya` described as the middle of three; its actual behaviour differs.**
**R27 `ekanka_gan` negative bit-count domain omitted.**
**R29 `ganita_paripurna_*` grouped under endpoint saturation; saturation is not the only failure policy.**
**R33 inclusive `chakra` presented without an endpoint caveat.**

**THE OWNER HAS ADDED A REQUIREMENT, and it is a design question, not a bug fix**
> **"`grahan()` can receive number but it should also accept text too right, just like Python `input()` capabilities."**

**Python's `input()` always returns text; `int(input())` converts. One function plus a converter. Sutram today has two functions: `grahan` for a number, `vartani_grahan` for a line.**

---

# ROUND-171 - to Muse, read only

**Base:** main at v315 · **Deliver into:** `Muse-to-Sarvam/`

**Read only. Nothing to compile or run.**

**A whole-tree audit came back with 47 findings and the verdict "not release-ready".** **One reader produced that. You are the second reader, and the job is not to check the fixes — it is to check the ranking.**

## Task 1 - and this is the round: the fourteen Tier 1 findings, re-ranked
**The audit ranks 14 as Tier 1: silent wrong answer, or guidance that induces one.**

**Read each against the code and say whether it belongs there.**

**The question for each:**

> **Could a student, following this document or using this function as documented, get a wrong answer without being told?**

**And the reverse: is anything ranked Tier 2 or Tier 3 that is actually Tier 1?** **A documentation error that makes a student write a program with a buffer overrun is Tier 1, not Tier 3.**

**I would look hardest at these, and say if I am wrong:**

- **R01/R02 — `likh8`/`pad8` documented as eight-bit and as character I/O.** **A student following that writes one byte into an eight-byte operation. Is that a crash or a silent corruption?**
- **R11 — `nirmmita` documented as giving zeroed bytes when main only advances the cursor.** **A student who trusts that reads uninitialised memory. That is the same defect the memory work spent a week fixing.**
- **R14 — `brihat_ank_tak_laghu` returning −1.** **What does a student's program do with −1 that should have been refused?**
- **R33 — inclusive `chakra` without an endpoint caveat.** **Off-by-one in a loop is the most common beginner bug there is.**

## Task 2 - and the two the audit did not settle
**The audit says *"previously identified memory/loop boundaries"* are open on main, and names them only by reference.**

**Read the memory work as it stands at v324 and say what is actually open.**

**Specifically:**

1. **Does a `kosh` that escapes a loop still leak?** **Yes, by design — but is that documented?**
2. **Does a block still not return memory to the OS?** **Closed as zero of 347 — but is that written down anywhere a student would find it?**
3. **And the one the audit calls a boundary: is there any loop shape where the hoist is wrong?** **You checked direct, `yadi`, `mandapa` and `yavat`. Is there a fifth?**

## Task 3 - and the `grahan` question
**The owner wants one input function that handles both numbers and text, like Python's `input()`.**

**You have read the library and the books.**

1. **Is there a text-to-number conversion today?** **Name it or say there is none.**
2. **If a beginner types `hello` into `grahan()`, they get `0`.** **Is that a silent wrong answer, or is it documented?**
3. **And which shape teaches better: one function returning text plus a converter, or two functions that each do what their name says?**

**Answer as the reader of the books, not as a language designer. What would a student actually do with each?**
