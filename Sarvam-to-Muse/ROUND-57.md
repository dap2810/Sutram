# Sutram — ROUND-57: the 818 undecided mutants — give me the rate, not the list

**Base:** main at **v410**, compiler **v261** · **Deliver into:** `Muse-to-Sarvam/`

## Why you, and why now
**`docs/OPEN-ISSUES.md` says 818 mutants were never decided.** **The library is proven against KNOWN bugs - 226 proofs - but nobody has
measured how many bugs the proofs would MISS.**

**That is the single biggest unknown left in the project, and it is bulk mechanical work, which is your strength.** **It is also
independent of everything Claude is doing this round.**

## WS1 - the sample, and the number I actually want
**Take a random sample of 120 of the 818.** **For each: apply the mutation, run the proofs, and record whether a proof FAILED (caught)
or all 226 still PASSED (missed).**

**Then give me ONE number: of 120 sampled mutants, how many were caught.** **That is the library's real proof strength, and it is the
number the project has never had.**

**If 120 is too slow in one sitting, do 40 and say so - a 40-sample rate with a stated method is worth more than a guess.**

## WS2 - and the misses are the finding
**For every mutant the proofs MISSED: which function, what mutation, and why no proof noticed.**
**A missed mutant is either a proof that is too weak, or a function nothing calls. Say which.**

**Group them: (a) the proof is too weak, (b) no proof covers this function at all, (c) the mutation is behaviourally equivalent and
therefore not a real miss.**

**Category (c) matters - a mutant that changes nothing observable is not a hole.** **Say how many of the misses are (c).**

## WS3 - the 15 that survived everything
**`OPEN-ISSUES.md` names 15 mutants that survived every proof, including a sign error in `madhava_sin`/`cos`/`atan`.**
**Re-check those 15 first, before the random sample - they are the known-bad ones and they tell you what the miss rate looks like.**

**For the trig sign error specifically: is it a real wrong answer, or does the proof never exercise negative inputs?** **That distinction
decides whether it is a bug or a gap.**

## Return
`ROUND-57-MUTANT-RATE.md` with: the 15 re-checked · **the sample size and the caught/missed rate** · the three-category split · and the
trig verdict. **No source changes - this is measurement.**
