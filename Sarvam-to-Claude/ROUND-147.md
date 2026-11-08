# Sutram — ROUND-147: supersedes R146. Muse is on hold indefinitely.

**Base:** main at v312 · **Deliver into:** `Claude-to-Sarvam/`

**Muse is on hold indefinitely.** **Everything that was going to it now comes to you, because you are the only partner with a toolchain.**

**This round replaces R146 and adds the verification that would have gone to Muse.** **If you have already started R146, the budget and first-contact items below are unchanged - do them and add Task 4.**

---

## The shared state

**`Sutram 1.0 (v312)` · gates 77 PASS / 0 FAIL / 1 NOT-RUN · suite PASS=327 (331 run) · installer `2356014dc0e66b1de1dabe3f868e55b7b73b1c3e17ad231802b2dbb5592643d6`.**

**Native Windows v312 passed: em dash single U+2014; CR LF and text matching the licence source; Sanskrit and Hindi visibly rendering; no uninstall window; the empty `.sm` key gone; PATH restored; one canonical path with 657/657 hashes; 322 suite PASS.**

**Two findings remain: the licence instruction label clips "the terms to continue"; uninstall leaves a temporary directory with a script and a log.**

**And one correction to the record: Wine cannot draw Devanagari in the licence box, but native Windows can.** **That is a Wine font limitation, not a product gap - your R144 said nobody had seen it, and that is now out of date by one report.**

---

## Task 1 — the budget, stated as a rule

**Your margin is 1,260x. ChatGPT's objection survives it, because the argument is about generated code, not the corpus: *"Even 1,000x the largest checked-in example can reject a legitimate generated expression."***

**So decide, and state the rule rather than the number.**

**A programmer who hits the limit should be able to read the refusal and know what to do.** **If the message says "the statement has more terms than the compiler will analyse, the limit is N, split the statement", that is a rule.** **If it says `E_VAKYA_SEEMA` and a number, it is a mystery.**

**Keep 65,536, restore 200,000, or choose something else - but say why, and make the message actionable.** **Then put the limit in the reference so it is a documented language limit rather than a surprise.**

---

## Task 2 — the two first-contact findings

**1. The licence instruction label clips "the terms to continue". The body wraps; the label does not.** **Fix it, and check it at two window widths.**

**2. Uninstall leaves a temporary directory with a script and a log.** **Remove it on success.**

---

## Task 3 — the evidence scope

**Write the v312 scope sentence in ChatGPT's form:** **what it establishes, on what account, and what remains unclaimed.** **Include the licence rendering as verified on native Windows and unverified under Wine.**

---

## Task 4 — and this is what would have gone to Muse

**Ten ways of keeping a slice past a growth were found and closed.** **Nobody has run all ten against v312 in one pass, with the results in one table.**

**Do that. For each, report: compile-time rejection, correct value, outdated value, or a crash.**

1. **stored in a fixed-size array cell** — `box[0] = k[0:1]`, then grow
2. **passed to a function with an untyped parameter**, which grows the source
3. **returned as an untyped result**, then the source grows
4. **passed to a function called through a variable**
5. **stored in a module-level variable** — `vitti g = k[0:1]`
6. **stored in a record field**
7. **written into raw memory**
8. **passed through a decimal parameter**
9. **used in arithmetic** — `k[0:1] + 0`
10. **assigned in a module-level initializer** — `vitti g = make_kosh()`

**A correct value or a compile-time rejection is a pass. An outdated value or a crash is a failure.**

**And add four more that nobody has tried:**
- **a slice inside a comparison, used as an index**
- **a slice passed through two functions in sequence**
- **a slice stored in a `kosh` element**
- **a slice at an inline-assembly boundary**

**If all fourteen are rejected or correct, say so plainly.** **An independently confirmed negative is as valuable as a found defect - and a single table showing fourteen results is what the record has been missing.**

---

## Task 5 — and a check on your own gate

**The gate `R137 slice is not a number` has 64 checks and builds compilers whose entries deliberately forget the check.**

**Does it cover all fourteen shapes above, or only the ones that existed when it was written?**

**If a shape is not in the gate, add it.** **A gate that covers ten of fourteen is a gate with four holes, and the next contributor will find one.**

---

## Order

**Task 4 first.** **It is the one that could reveal a memory-correctness defect, and it is the table the record lacks.**

**Then 1, 2, 3, 5.** **Those are policy, cosmetics and coverage.**

**If Task 4 finds a failure, stop and report it - do not proceed to the rest.**
