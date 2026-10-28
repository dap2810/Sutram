# Sutram — ROUND-56: the 20 library names that describe the wrong operation

**Base:** main at **v408**, compiler **v258** · **Deliver into:** `Claude-to-Sarvam/`

**Read first:** `ChatGPT-to-Sarvam/ROUND-129-LIBRARY-NAMES.md` - **the section "Confirmed semantic mismatches and alternatives
(the N rows)" has all 20 with the exact suggested name.** **Do not work from my summary; work from that file.**

## The rubric the owner's naming rules give me, applied to every rename
1. **A complete Sanskrit word or compound, never a fragment.**
2. **The sense must match what the BODY does** - that is the whole point of these 20.
3. **Shorter is better, but a correct longer name beats a wrong short one.**
4. **No collision with a keyword, a builtin, another library function, or the same module.**
5. **Nothing that breaks a program.** **The guard must read 0 DIFFER except where a golden legitimately changes.**

**And a rule I am adding after being wrong all session: if a suggested name is longer than what it replaces, say so and give the
shorter correct alternative.** **`mahattam` -> `mahattam_samanya_bhajak` is 8 -> 22 characters on a function called often.** **If
`mahattam` is ambiguous and something shorter is exact, use that.**

---

## WS1 — the 20, and they are not equal

**ChatGPT read all 305 bodies and judged 285 accurate.** **These 20 are not.** **The worst of them, and why they matter:**

- **`sadish_yoga`** - the name says VECTOR ADDITION; the body multiplies corresponding coordinates and sums. **It is a dot product.** **Anyone calling it expecting addition gets a different answer of the same type - the worst kind of wrong.**
- **`chandas.dviguna`** - `dviguna` means DOUBLING; the body computes **2^n**. **Not 2n - a power.**
- **`ganit.mahattam` / `laghuttam`** - "greatest" and "least", but they return **GCD** and **LCM**. **The relation is missing.**
- **`sankhyiki.bindu`** - `bindu` is POINT; it computes an **inner product**.
- **`roop_varg_mool`** - says SQUARE ROOT; it formats **digit groups**.
- **`anukram_maap_ashtak` / `_khip_ashtak` / `_grah_ashtak`** - say "eight bytes"; they write and read an **eight-byte LENGTH PREFIX followed by a payload**.
- **`asti_vilom`** - says REVERSED; it tests for a **palindrome**.
- **`nirnaya2` / `nirnaya3`** - **determinants of order 2 and 3.** **The digit in the name is the order.**
- **`util_chinha`** - returns **signum -1/0/1**, so `ank_chihna`.

## WS2 - do them in three commits, smallest risk first
1. **The ones with no callers outside their own module.** **Renames inside `lib/` only.**
2. **The ones called from `examples/`.** **Rename and update the call sites.**
3. **`sadish_yoga` and `dviguna` LAST** - **they are the two where the sense is most wrong and the usage most likely to be wide.**
   **Count their call sites before you touch them, and if either has more than 30, report before changing it.**

## WS3 - the proof
**Library proofs must pass 226/226 after each commit.** **The suite 225.** **The guard 0 DIFFER - a rename inside `lib/` changes
no output, so any differ is a bug.**
**And one behavioural test per renamed function that the proofs already cover: state that the proof covers it, do not write a new one.**

## Return
`R56-00-HANDBACK.md` with: the 20 renames, in the three groups · **any name you did NOT take and why** · **the two call-site counts**
· the guard, suite and proof numbers.
