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

# ROUND-234 - to ChatGPT

**Base:** main at v315 · **Deliver into:** `ChatGPT-to-Sarvam/`

**Your R233 was the first whole-tree verdict this project has had, and it was a no.** **This round is the part of it you could not finish, and one thing it did not cover.**

## WS1 - and this is the round: the fourteen, separated
**Tier 1 has 14 findings.** **They are not the same kind of thing, and a fix list that treats them alike is not usable.**

**So: sort every Tier 1 finding into exactly one of three classes:**

1. **DOCUMENTATION ONLY** — the code is right, the document is wrong. **The fix is a sentence.**
2. **SOURCE ONLY** — the code is wrong, the document is right. **The fix needs a compiler and a test.**
3. **BOTH WRONG, OR THE INTENT IS UNCLEAR** — the code does something, the document says another thing, and nobody has said which was intended. **These are the dangerous ones: a fix could make the document match a bug.**

**For each of the 14, say which class, and for class 3 say what the intent should be.**

**And the count: how many are class 1, how many class 2, how many class 3?** **If most are class 1, the tree is in better shape than "not release-ready" suggests.** **If there are class 3 findings, the tree has an undefined behaviour and that is worse than either.**

## WS2 - and the memory and loop boundaries
**Your R233 says *"previously identified memory/loop boundaries"* are open on main.** **Name them.** **What was identified, by whom, and is it still true at v324?**

**Because the memory work is the biggest thing this project has done, and if the audit says there are open boundaries, they need to be named rather than referenced.**

## WS3 - and the `grahan` question, which the owner has now asked
**The owner: *"`grahan()` can receive number but it should also accept text too, just like Python `input()` capabilities."***

**Python's `input()` always returns text; `int()` converts.** **One function plus a converter.**

**Sutram has `grahan` returning a number and `vartani_grahan` returning a line.**

**So: what is the right answer for this language?**

1. **Is there a text-to-number conversion function today?** **Name it, or say there is none.**
2. **If there is one, the Python model costs nothing to adopt except breaking `grahan`'s return type.** **How many programs would break?**
3. **If there is none, adopting the Python model needs two new functions and breaks one.** **Is that better than keeping two input functions and making each do one thing well?**
4. **And the beginner question: does one function that returns text, plus a converter, teach better than two functions that each do what their name says?**

**Give a recommendation and the reason.** **And say which is more likely to give a beginner a silent wrong answer — because that is the standard this project has been using all week.**

## WS4 - and what you could not finish
**You said: *"No full control-flow reachability proof or native-speaker comparison of every Sanskrit paragraph was completed."***

**Do not attempt the full reachability proof — it is too large for one round.**

**But do this: name the ten routines in the compiler with the most complex control flow, and say for each whether you read every branch.** **That tells the project where the audit is thin, which is more useful than a claim of completeness.**
