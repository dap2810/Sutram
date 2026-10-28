# Sutram — ROUND-130: the 33 comments, and a second look at the longest names

**Base:** main at **v408** · **Deliver into:** `ChatGPT-to-Sarvam/`

**Read first:** your own `ROUND-129-LIBRARY-NAMES.md`, sections WS3 and the N-row list.

## WS1 - the 33 surprising bodies, as comments
**Your WS3 lists 33 functions whose name is defensible and whose contract is a trap.** **`fnv1a` is a hash, not encryption.**
**`ganita_paripurna_bhaj` returns a sentinel zero on divide-by-zero and zero is also a legitimate quotient.**

**Muse is writing the 88 missing comments in ROUND-55.** **So for these 33, write the comment TEXT only** - **one line each, in the
form that goes above the function** - **and deliver it as a TSV: `file | function | comment_line`.**
**Do not edit the library; Muse is in it.**

## WS2 - the longest of the 20, reconsidered
**Several of your suggestions are much longer than what they replace:**
- **`mahattam` (8) -> `mahattam_samanya_bhajak` (22)**
- **`laghuttam` (8) -> `laghuttam_samanya_guna` (21)**
- **`sankhyiki.bindu` (5) -> `antar_gunana` (12)**
- **`asti_vilom` (10) -> `asti_viparyay_sam` (16)**

**These are called in code, often.** **So for each of those four: is there a SHORTER exact Sanskrit word?** **`mahattam` alone is
wrong because the relation is missing - but is there a two-word compound under 15 characters that carries GCD exactly?**
**If not, say so and I will take the long name.**

## WS3 - and the one I most want confirmed
**`sadish_yoga` computes a dot product.** **That is a wrong operation, not a vague name.** **Is there any reading of `sadish_yoga`
under which a dot product is correct?** **If the original author meant something defensible, say what.** **If it is simply wrong,
say that too - the fix is a rename and I want it on the record.**

## Return
`ROUND-130-COMMENTS.md` with the 33-line TSV, the four shorter-name answers, and the `sadish_yoga` verdict.
