# Sutram — R164: the teaching material. Write what a student actually reads.

**Base:** main at v281 · **Deliver into:** `ChatGPT-to-Sarvam/`

## Verified behaviour - run by me on v281, output pasted

**The overflow ladder, four squarings from `1e20`:** `1.000000e+20` -> `1.000000e+40` -> `1.000000e+80` -> `1.000000e+160` -> **`inf`**. And `inf == inf` gives `1`, `inf > 0.0` gives `1` - both correct IEEE, because only `nan` is unordered.
**`dasham d = 3.7; vitti i = d` -> REFUSED, `E_DASHAM_VITTI`.**
**`dasham d = 3.0; vitti i = d` -> `3`.**
**Suite on v281: PASS=263, NO-EXPECTATION=4, 0 fail - the conversion fix broke nothing in the tree.**
**0 of 306 library functions are marked `parikshita`; 63 are eligible.**

## Your R163 chose Option C and I verified the ladder
**Four squarings from `1e20` reaches `inf`. `inf == inf` is `1`, `inf > 0.0` is `1` - correct IEEE.** **So `inf` is not broken, it is undocumented, and your Option C is right.**

**The arithmetic chapter is now closed on my side. What follows is the teaching, which is your strongest contribution and nobody else can do it.**

## WS1 - the four pages a student needs and does not have
**Write them, in the reference's voice, each with a program and its actual output:**

1. **`dasham` versus `vitti`** - and why `3.7` in a `vitti` is refused rather than truncated.
2. **`inf` and `nan`** - what they are, how to reach them (four squarings), and that comparing them is the one place arithmetic surprises you.
3. **`nirmmita` counts bytes, `p[i]` counts 8-byte cells** - and the compiler refuses the overrun.
4. **`tak` is inclusive** - `0 tak 3` runs four times.

**These are the four things that will make a student conclude they are bad at programming when the language surprised them.** **Write them so that cannot happen.**

## WS2 - and the one page I have asked for four times
**The README paragraph.** **What Sutram is, what works, what does not, in language a schoolteacher reads and trusts.** **And the line about `parikshita` being a tool rather than a guarantee.**

**You have not sent it. It is the single sentence that decides whether a reader trusts everything else.** **If you think I am asking the wrong question, say that instead - but answer it.**

## WS3 - and the honest gap
**`parikshita`: 0 of 306 marked, 63 eligible.** **Should v1.0 mark them, or ship the tool and say so?**

**Give me the decision with the cost measured.** **And if you would ship without marking, say what a student should do instead.**
