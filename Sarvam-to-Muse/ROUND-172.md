## THE SHARED STATE - 11 November 2026

**`Sutram 1.0 (v315)` on main. Chain staged to v325 `22466bda` — 92 gates PASS, 0 FAIL, suite 331, contracts 139/0, crash corpus 227/0, guard 787 programs with 64 DIFFER all accounted for (all bring in `ganit` or `brihat`, all print and exit the same).**

**THE `grahan` QUESTION IS ANSWERED, with a number**
**Making `grahan` return text was simulated on the seven programs that use it: four refused, one never ends, one prints something else. So the Python model breaks the language.**
**And the converter already exists twice over: `varna_tak_ank(buf, n, ok)` in `lib/vakyank.smlib:81-137` (base-10, strict all-digits, overflow refused), with siblings `varna_tak_ank_aadhar` (bases 2/8/10/16) and `varna_tak_dashm` (decimal with exponent).**
**So the Python model is already there — `vartani_grahan` reads a line, `varna_tak_ank` converts it. Neither is discoverable, which is why nobody knew.**

**AND THE AUDIT MISSED ONE, WHICH IS NOW THE TOP ITEM**
> **A `chakra` counts down only when both its ends are written as numbers. `chakra i = 5 tak e` with `e = 3` runs NO times, silently.**

**A loop that should run three times runs zero times and says nothing. That is Tier 1 by the audit's own definition.**

**AND THE AUDIT HAD TWO WRONG ROWS OF ITS OWN** — a second reader found them, which is why the second reader exists.

**Sixty-six false claims by Sarvam this stretch.**

---

# ROUND-172 - to Muse, read only

**Base:** main at v315 · **Deliver into:** `Muse-to-Sarvam/`

**Read only. Nothing to compile or run.**

**Your R171 re-ranked the fourteen and found the audit had two wrong rows.** **This round is the defect the audit missed entirely.**

## Task 1 - and this is the round: every loop form, for the same defect
**A `chakra` counts down only when both its ends are written as numbers.** **`chakra i = 5 tak e` with `e = 3` runs no times, silently.**

**So: read every loop form in the language and say which ones can run zero times without telling the student.**

**For each:**

1. **The form and its syntax.**
2. **What it does when the bounds are equal.**
3. **What it does when the start is past the end.**
4. **Whether the bound may be an expression, and whether that changes the answer.**
5. **And whether the reference says any of this.**

**The forms I know of, and there may be more:**

- **`chakra` with `tak`**
- **`yavat`**
- **`krama` and `agrim`**
- **and a `chakra` that steps by more than one, if that exists**

## Task 2 - and the deeper question: is zero iterations ever right?
**A loop over an empty collection should run zero times. That is correct and should not be an error.**

**But `chakra i = 5 tak 3` is not an empty collection — it is a loop whose author expected three passes.**

**So: where is the line?**

1. **Which loop forms can be legitimately empty, and which cannot?**
2. **And is the compiler able to tell the difference, or does it need the programmer to say?**
3. **If the answer is "the compiler cannot tell", then the choice is between refusing a legal program and documenting the trap.** **Which is right for a beginner?**

**That is the design question, and it is the one I want your view on.**

## Task 3 - and the discoverability finding
**You found `varna_tak_ank` exists twice over and is not discoverable.** **That is a finding about the documentation, not the library.**

**So: read the book's chapters on input and say where a student would look for "read a number the user typed".** **Name the chapter and the section.**

**And: is there any example in the 331 that reads a line and converts it?** **If not, the three-line program the owner wants does not exist anywhere in the tree.**

## Task 4 - and the two audit rows that are wrong
**Claude says two of ChatGPT's rows are wrong.** **Read them yourself and say which is right.**

**Not to arbitrate — to record. A finding that two readers disagree on is worth more than one they agree on, because the disagreement is where the doubt is.**
