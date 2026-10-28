# Sutram — ROUND-56: the 108 English variables in `examples/`

**Base:** main at **v408** · **Deliver into:** `Muse-to-Sarvam/`

**Read first:** your own `ROUND-55-VARIABLES.tsv` - **108 distinct names, counted by your method.** **This round applies it.**

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

## WS1 - apply the table, but not blindly
**For each of the 108 names: rename the declaration and every use, then compile, run, and compare against the UNCHANGED golden.**
**The output must be byte-identical** - **a variable name never prints, so any differ is a bug.**

**Work in batches of about 20 names, and report after each batch.** **If a batch produces a differ, stop that batch and list it.**

## WS2 - the three that need care
**Your TSV marks some as colliding. Handle those explicitly:**
- **`xs` -> `pratham_suchi`** - **is `pratham` right for a collection of x-coordinates, or does `pratham` mean "first"?** **If it is wrong, say so and propose better.**
- **`st` -> `avastha`** - **your note says "state/condition", which is right for a parser state.** **Keep it.**
- **Any name where the count is 1 or 2** - **a rename of a variable used twice is churn.** **List those separately and I will decide whether to skip them.**

## WS3 - and the honest question
**108 variables renamed in 229 files is a large diff for no behaviour change.** **Is it worth it?**
**Say plainly whether a beginner reading `examples/01_hello.sm` meets an English word after this round.** **If the answer is no,
the round did its job. If the answer is "yes, but fewer", say which files still have one.**

## Return
`ROUND-56-VARIABLES-APPLIED.md` with: the batches · every differ and why · **the files skipped with the reason** · **the WS3
answer** · and the suite result, which must still be PASS=225.
