# Sutram — ROUND-52: the examples teach the wrong form, and it is fixable without the compiler

**Base:** main at **v394** · **Deliver into:** `Muse-to-Sarvam/`

**Read first:** `docs/WHATS-LEFT.md`, and your own `ROUND-51-STYLE-CODEBASE.md` - **this round is your own counts coming
back to you.**

## Why this round
**You counted 135 three-statement print triples in 48 example files.** **405 lines that could be 135.** **And the language
already supports the short form - `likha("x = ", x)` has worked all along.**

**So the examples teach a form the language does not require.** **That is why I thought the language was missing a feature.**

---

## WS1 — migrate the 135 triples

**For every triple of the shape:**

```sutram
likha("x = ")
likha(x)
likha("\n")
```

**replace with:**

```sutram
likha("x = ", x)
```

**Rules:**
- **Only when the middle call is a simple value or expression that the 2-argument form accepts.** **A `dasham` and a
  string both work - you measured that.**
- **A triple whose middle call is `lkhb` becomes the same 2-argument form** - **but check the float case, because `lkhb` on
  a float prints raw bits today and Claude is fixing that in R52.** **If a triple prints a float with `lkhb`, LEAVE IT and
  list it.**
- **Each file: change, compile, run, and compare against its golden with the label text unchanged.** **The output must be
  byte-identical.** **If it is not, revert that file and list it.**
- **Report: files changed, triples removed, lines removed, files skipped and why.**

## WS2 — the 88 functions with no usage comment

**88 of 305 library functions have no comment above them.** **That is 29%, and it is why three of my renames named the wrong
thing - I had to guess from the name.**

**Write the missing comment for each.** **One line: what it does, and what the parameters mean if it is not obvious.**

**Do NOT change any code.** **A comment cannot break a program, which is why this is safe to do in bulk.**

**Report: how many you wrote, and any function where you could not tell what it does from the body - those are the
important ones.**

## WS3 — re-count and confirm

**After WS1, re-run your own counts:** how many triples remain, how many `likha("\n")` lines remain. **Give the before and
after.** **If a number did not move as much as expected, say why.**

---

## Return
`ROUND-52-EXAMPLES.md` with: the counts before and after · **every file changed** · **every file skipped with the reason** ·
the 88 comments written, or the count and the list of functions you could not describe. **Suite must still pass 225.**
