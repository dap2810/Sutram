# Sutram — ROUND-145: one round, replacing R138 to R144

**Base:** main at v308 · **Deliver into:** `Muse-to-Sarvam/`

**This round is written in plain language on purpose. An earlier version used security terminology that may have been misread. The work is ordinary compiler verification: checking that a compiler correctly rejects programs it should not accept.**

---

## Please disregard R138 through R144

**I issued several rounds without waiting for the previous one to return. They contradict each other and cannot all be completed.**

**This single round replaces them.** **Everything that mattered is here, in order.** **If any earlier round is already done, say which and I will take the result.**

---

## Background

**Sutram is a programming language. A `kosh` is a growable list. A slice is a view into part of a `kosh`.**

**When a `kosh` grows, its contents move to a new memory location. A slice taken before the growth may still refer to the old location — so reading it can return an outdated value instead of the current one.**

**This is a correctness problem, and the compiler should reject programs where it can happen.**

**v308 added a single check, `r134_holds_kosh`, applied wherever a value is stored in a way that loses its type. Sixteen example programs are now correctly rejected.**

---

## Task 1 — does arithmetic preserve a slice's identity? (highest priority)

**The compiler currently classifies a binary operation as a plain integer, so a slice inside an arithmetic expression is not recognised as a slice.**

**I ran two small programs on v308. Both compiled and ran. Both printed a large number:**

```
(k[0:1] + 0) through a function   -> 139537424244064
(k[0:1] + 0) directly             -> 139536700079456
```

**Those look like memory addresses rather than element values.**

**Please determine, for each of these, whether the result is: an address, an outdated value, the correct value, or a compile-time rejection.**

- **`k[0:1] + 0`** — I observed an address; please confirm
- **a slice in a conditional expression**, then stored — `yadi(...) { k[0:1] } anyatha { 0 }`
- **a slice passed through a function that returns it unchanged**, then used in arithmetic
- **a slice in a comparison**, then the result used as an index
- **a slice in a decimal expression** — does the conversion give an element or an address?
- **a slice multiplied by a number**, so the value is scaled — if the result happens to look like a plausible element, that is the most confusing case
- **a slice stored in a fixed-size array cell, then read back as an element**

**And one that a student would hit far more easily: what does `likha(k[0:1])` print directly?** **If it prints an address, that is the same problem in a simpler form.**

---

## Task 2 — are there other ways the identity can be lost?

**The same question, one step wider. Please try:**

- **a type conversion**
- **a built-in function that returns its argument unchanged**
- **an inline-assembly boundary**
- **a slice stored inside a `kosh` element**
- **a slice passed through two functions in sequence**

**For each, report: rejected at compile time, correct value, outdated value, or an address.**

**If all of them are rejected, please say so plainly — an independently confirmed negative result is as useful as a found problem.**

---

## Task 3 — does the check cover every place a value can be stored?

**The new check runs wherever a value loses its type. Please read the compiler and identify any place where a value is stored that does not call `r134_holds_kosh`.**

**The goal is coverage: if a future contributor adds a new storage location and forgets the check, is there something that would notice?**

**If you find a location that is not covered, that is the most useful thing you can report.**

---

## Task 4 — installation recovery at less convenient moments

**The installer now recovers correctly when interrupted after 17 files: a retry completed in 8.65 seconds and the pending record was cleared.**

**What happens if the interruption occurs at a different moment?**

- **before the first file is copied** — does a retry behave sensibly?
- **after the last file but before the record is cleared** — does it re-copy everything, or recognise completion?
- **while the record itself is being written** — is it written atomically, or can it be incomplete?
- **if a person edits a file in the target folder between the interruption and the retry** — is that file preserved or overwritten?

**The last one matters most: an edited file is not the installer's file, and should not be treated as one.**

---

## Task 5 — line endings and file hashes

**An installation was suspended by a security product. The cause was CRLF line endings in the payload: the same installation completed in 21 seconds once the line endings were normalised.**

**So: which files in the payload are text and which are binary?** **If a `.gitattributes` rule normalises some of them, a Windows checkout produces different bytes from a Linux build.**

**Please check whether the manifest's recorded hash for a text file matches what a Windows checkout produces.**

**If they differ, the installer is comparing hashes across two different line-ending conventions — a real problem even without the security product involved.**

---

## Task 6 — a review of your own earlier probes

**One of your earlier probes printed a memory address where an element value was expected, and a later version of the same probe printed the correct kind of value.**

**What changed between them?** **And are there other probes of yours that might be reporting an address as if it were a value?**

**You have run more probes on this project than anyone. That review is worth more than another probe.**

---

## Order

**Task 1 first — it is the only one that could reveal a correctness problem in a release candidate.**

**Then 2, then 3. Then 4 and 5, which are about the installer and are lower priority because installation is already verified working.**

**Task 6 last, because it may change how you read your own earlier results.**

**If you only have time for one, do Task 1.**

---

## And a note on process

**Several rounds issued to you at once, with none returning, was my mistake. If any of them were unclear or impossible to complete, please say which and why.**
