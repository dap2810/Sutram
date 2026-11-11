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

# ROUND-189 - to Claude

**Base:** main at v315 · **Deliver into:** `Claude-to-Sarvam/`

**Three things: the audit's fixes, applied and proved. The `grahan` unification the owner asked for. And the two source defects.**

## WS1 - and first: the `grahan` question, because it is a breaking change and it is the owner's requirement
**The owner's words: *"`grahan()` can receive number but it should also accept text too, just like Python `input()` capabilities."***

**So: one function that reads input, and works for both.**

**Python does it by making `input()` always return text, and `int()` convert.** **That is one function plus a converter, and it is the model the owner named.**

**But Sutram has `grahan()` returning a number, and every program that uses it expects a number.** **Changing its return type breaks them.**

**So answer this before building:**

1. **What does `grahan()` return today, exactly — a `vitti`?** **And what does `vartani_grahan()` return — a `pankti`, a text value, or a `kosh` of bytes?**
2. **Is there a conversion function today — text to number?** **If yes, the Python model already exists and the work is small: make `grahan` return text and tell students to convert.**
3. **If `grahan` returns text, how many of the 331 examples and the 783 guard programs break?** **Count them.** **That number decides whether this is a fix or a version bump.**
4. **And the alternative that breaks nothing: keep both, and make `grahan` accept text and parse what it can** — **so `grahan()` on `hello` returns something sensible rather than `0`.** **Is that better than Python's model, or worse?**

**Give the three options with their costs, pick one, and say why.** **Do not build until you have said which.**

## WS2 - and then: the audit's fixes
**A candidate branch exists with the negative-digit fix, three verification defects and selected documentation.** **Apply what is proven, and prove it again.**

**And these four source defects need a compiler and a test:**

1. **`lib/brihat.smlib:71` — `brihat_ank_tak_laghu` checks `d <= 9` and never `d >= 0`.** **A cell holding −1 returns −1.** **Fix, and prove with a program that returns −1 today.**
2. **`brihat_ank_se`'s failure mutation — described wrongly; is the code or the document wrong?**
3. **The `LCM(MIN,0)` refusal — the audit says it is open on main.** **What is it, and what should happen?**
4. **Signed and final-line input — the audit says open on main.** **You staged a fix in v324; does it cover both?**

**For each: the command that shows it wrong, the command that shows it right, the guard, the suite, the corpus.**

## WS3 - and the documentation
**The remaining Tier 1 findings are documentation, and they are the ones that cost a student a debugging session.**

**R01, R02, R04, R05, R07, R08, R11, R17, R24, R27, R29, R33.** **Each is a sentence that is false.** **Fix each against the code, and say for each what the code actually does.**

**And R11 matters most: `nirmmita` documented as giving zeroed bytes when main only advances the cursor.** **That is a promise of safety the language does not keep.**

## WS4 - and the gate
**The audit found a missing live `docs/WHATS-LEFT.md` and a changelog nine versions behind.** **Both are still true.**

**So: run `R158`, and if it passes, say which check should have caught them.**
