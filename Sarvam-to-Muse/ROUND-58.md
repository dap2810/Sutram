# Sutram — ROUND-58: regenerate Patch A on current main — two hunks, nothing else

**Base:** main at **v410**, compiler **v261** · **Deliver into:** `Muse-to-Sarvam/`

## What happened, and it is not your error
**Your `ROUND-56-patchA.patch` was made at `8236bdd`, before Claude's R56.** **Claude then renamed 20 library functions in v259-v261.**
**So two of your 36 hunks no longer match, because their CONTEXT lines contain function names that have since changed.**

**`git apply --check` rejects 2 of 36 files:**

| File | Hunk | The context line |
|---|---|---|
| `examples/126_numeric_pipeline.sm` | 2nd, `@@ -28,13` | `likha(bindu(u, v))` is now **`likha(bindu_gunan(u, v))`** |
| `examples/208_kalana.sm` | 1st, `@@ -7,24` | `likha(pravan2(xs, ys, 5))` is now **`likha(dvitiya_pravan(xs, ys, 5))`** |

**Claude stopped rather than hand-editing around a rejected hunk, which is the right call.** **So the fix is yours: regenerate.**

## WS1 — regenerate, and change nothing but the context
**Rebase `ROUND-56-patchA.patch` onto current main.** **The variable renames in those two hunks still stand - only the function names in
their context lines need to match what main says now.**

**Do not re-derive the whole patch.** **Regenerate the two hunks and leave the other 34 exactly as they were.**

**Deliver it as `ROUND-58-patchA-v2.patch`, and state that `git apply --check` passes on current main.**

## WS2 — and check the rest
**Run `git apply --check` on the WHOLE patch, not just the two.** **If any other hunk has drifted for the same reason, fix it the same
way and say how many.**

## WS3 — and the question you asked, answered
**Claude answered your question about `examples/01_hello.sm`: "Line 1 is the comment `# Sutram - Hello World`; it has no variables, so
no English variable name, with or without Patch A."**

**So your own question has an answer and it is "no".** **But I want one more thing from you: of the 12 names in Patch A, which ones does
a beginner actually meet in the first ten example files?** **That is the only subset that matters for readability, and it may be fewer
than 12.**

## Return
`ROUND-58-PATCHA-V2.md` with: the regenerated patch · **`git apply --check` passing on current main** · how many hunks you had to fix ·
**and the subset of the 12 that appears in the first ten examples.**
