# Sutram — ROUND-104: APPLY MUSE'S FIXALL PATCH. It outranks everything.

**Base:** main at v285 · **Deliver into:** `Claude-to-Sarvam/`

## Where the project is

**Compiler v285.** `mandapa parimita N` is built and refuses with `E_PARIMITA` in Sanskrit; a 1 MB budget admitted exactly 16,384 x 64-byte allocations then refused, peak 1,024 KB. Suite 273, gates 59 PASS / 1 FAIL (installer v243 vs v285). **0 DIFFER across 549 programs** for anything not writing `parimita`.
**Aliasing: closed below 8,388,603 elements** - each `kosh` reserves 64 MiB; ChatGPT read the source and found the relocate path still there (`cmp r11, R101A_MAXCAP; ja relocate`).
**A `kosh` made inside a `mandapa` outlives the block.** Claude gives the numbers and does not build the return unprompted.

## Read this first: `Muse-to-Sarvam/FIXALL-R100-TRAPS.md` and `fixall_r100.patch`

**Muse wrote a patch, 18 files, +757/-68, verified with `git apply --check` onto origin/main, and did NOT push it.** **It fixes five silent wrong answers your own R100 found:**

| Trap | v283 behaviour |
|---|---|
| `likha(a, " ", b)` - variable first, 3 args | **prints nothing, exit 0** |
| `vitti s = "ab"; likha(s == "ab")` | **prints 0 - compares addresses, not contents** |
| `vitti u = s + t` on two strings | **address sum, then segfault 139** |
| `vitti x` with no value, called twice | **`0 99 99` - the previous call's leftover** |
| Recursion with no base case | **exit 139, no output** |

**`"ab" == "ab"` returning false is worse than any memory gap in this project.** **A student's first string comparison fails and nothing tells them why.**

## WS1 - apply it, then guard it
**Five silent wrong answers becoming refusals is a large behavioural change.** **Apply the patch, run the suite, run the guard.**

**For every DIFFER: run the old binary and the new, and say whether the old behaviour was a bug or the new refusal breaks something legitimate.** **549 programs will move; I want the count of each kind.**

**If any of the five is wrong - the refusal is too broad, or the Sanskrit is wrong - say so and fix it rather than accepting the patch.** **You are the one who runs the tests; that is the authority.**

## WS2 - and the recursion case
**A recursion with no base case currently exits 139 with no output.** **The patch makes it print `E_GAHANATA` and exit 1.** **Test a legitimate deep recursion - 500 levels, which we have measured before at exact answers - and confirm the new limit does not break it.**

## WS3 - and only after that: the region return
**Do not do this first.** **The five traps outrank it.** **If the patch lands cleanly, then answer: can a `kosh` made inside a `mandapa` die with the block, and what does the liveness table cost?**
