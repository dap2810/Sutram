# Sutram — ROUND-144: ONE round, superseding R138 to R143

**Base:** main at v308 · **Deliver into:** `Muse-to-Sarvam/`

---

## Read this first: R138 through R143 are CANCELLED

**I issued six rounds to you without checking whether the previous one had come back.** **You last returned R137.**

**Each of those six assumed the answer to the one before it, so they contradict each other and none of them can be completed cleanly.**

**This round replaces all six.** **Ignore R138, R139, R140, R141, R142 and R143.** **Do not try to answer them.** **Everything that mattered from them is below, in one place, in the order it should be done.**

**If any of those six are already done, say which and I will take the result.** **Otherwise start here.**

---

## What has changed since your R137

**1. v308 closed the eight slice shapes.** Claude ran all thirteen of your escape programs: **every one is refused.** Its words: *"The one-predicate fix of R134 already covers the class. The gate now runs every one: v306 fails all sixteen escapes, v308 none."* **The fix is one predicate, `r134_holds_kosh`, at every door, and a gate that fails if a new door asks the old question.**

**2. ChatGPT found a NINTH shape by reading — arithmetic laundering.** `r126_value_kind` classifies a `BINOP` as raw kind 5, so `r134_kosh_slice` never sees the slice inside it.

**3. I measured it myself on v308.** Both of ChatGPT's probes compile and run:
```
arithmetic laundering (its probe)   -> 139537424244064   exit 0
slice + 0 direct                    -> 139536700079456   exit 0
```
**Those are heap addresses, not elements.** **So provenance is erased — but the outcome is not a stale read. It is a meaningless 15-digit number.**

**4. The installer is fixed and verified on native Windows.** Clean install 9.47 s; **upgrade 21.20 s with 654 files unchanged**; interrupted install killed after 17 files and **recovered in 8.65 s with the pending record gone.** **And the Acronis suspension was caused by CRLF line endings in the payload** — normalising them made the same upgrade complete.

**5. The installer changes are on PR #67, commit `edac959a`, NOT MERGED.**

---

## Task 1 — is a stale read reachable through arithmetic?

**I tested two probes. Both printed an address. I did not test whether a stale element read is possible.**

**This is the memory-safety question and it comes first.**

Try each, and say for every one whether the result is **an address**, **a stale element**, **a correct element**, or **a refusal**:

- **`k[0:1] + 0`** — I measured an address; confirm
- **a slice in a ternary**, then stored — `yadi(...) { k[0:1] } anyatha { 0 }`
- **a slice through a function that echoes it unchanged**, then in arithmetic
- **a slice in a comparison**, then the result used as an index
- **a slice in a `dasham` expression** — does the conversion give an element or an address?
- **a slice multiplied**, so the address is scaled — **if the result is a plausible element value by accident, that is the worst case**
- **a slice stored into a `mala` cell, then read back as an element**

**And one that is far more likely to be hit by a student: what does `likha(k[0:1])` print directly?** **If it prints an address, that is the same defect one step earlier.**

---

## Task 2 — is there a tenth shape?

**You found four more after being asked about four. ChatGPT found a ninth by reading.**

**So: is there a tenth that is neither a destination nor arithmetic?** **Something that changes the value without storing it and without a `BINOP`:**

- **a cast or a conversion**
- **a builtin that echoes its argument**
- **a `yantra` inline-assembly boundary**
- **a `kosh` element holding a slice**
- **a slice passed through two functions**

**If all refuse, say so plainly.** **A closed class confirmed independently is worth as much as a found defect.**

---

## Task 3 — can the gate be bypassed?

**`R134 one predicate` fails if a new door asks the old question.** **Sixteen escapes are in it.**

**Read every place the compiler stores a value into untyped storage.** **Name the place a future contributor would add a store and forget.** **If you find one, the gate is incomplete and that is the most important thing you can report.**

**A gate that can be bypassed is not a gate.**

---

## Task 4 — the recovery edge cases

**The recovery works when killed after 17 files.** **What about worse moments?**

- **killed between the journal write and the first copy** — does the retry know what to do?
- **killed after the last file but before the journal is deleted** — does it re-copy, or recognise completion?
- **killed while the journal is being written** — is it atomic, or can it be half-written?
- **a user edits a file in the target between the interruption and the retry** — protected or overwritten?

**That last one is the safeguard question.** **ChatGPT said the journal must not prove every file belongs to the installer.** **Test whether it does.**

---

## Task 5 — and the CRLF question, which is a latent defect

**The Acronis suspension was caused by CRLF line endings in the payload.**

**So: which files in the payload are text and which are binary?** **If a `.gitattributes` normalises some, a Windows checkout changes them and the payload hashes differ from the Linux build.**

**Check: does the manifest's recorded hash for a text file match what a Windows checkout produces?** **If not, the installer is comparing hashes across two line-ending conventions — a real defect even without Acronis.**

---

## Task 6 — and a self-audit

**ChatGPT noted your R135 probe printed the descriptor's element address rather than an element, and your R136 probe was sharper.**

**What changed between them?** **And are there other probes of yours that might be measuring an address and reporting it as a value?**

**You have run more probes than anyone on this project.** **That audit is worth more than another probe.**

---

## The order, and why

**1 then 2 then 3** — memory safety first, in that order, because a stale read outranks everything and the gate question outranks the rest.

**4 and 5** — the installer is verified working; these are edge cases.

**6** — the self-audit last, because it may change how you read your own earlier results.

**If you only have time for one, do Task 1.** **It is the only question that could reveal a memory-safety defect in a release candidate.**

---

## And one apology, stated plainly

**Six rounds stacked on you with no return is my failure, not yours.** **If any of them blocked you — because they contradicted each other, or asked for something you could not do — say which and why, and I will not repeat it.**
