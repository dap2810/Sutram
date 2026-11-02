# Sutram — ROUND-100: your FIXALL patch is received and it is the best delivery of the project

**Base:** main at v285 · **Deliver into:** `Muse-to-Sarvam/`

## Where the project is

**Compiler v285.** `mandapa parimita N` is built and refuses with `E_PARIMITA` in Sanskrit; a 1 MB budget admitted exactly 16,384 x 64-byte allocations then refused, peak 1,024 KB. Suite 273, gates 59 PASS / 1 FAIL (installer v243 vs v285). **0 DIFFER across 549 programs** for anything not writing `parimita`.
**Aliasing: closed below 8,388,603 elements** - each `kosh` reserves 64 MiB; ChatGPT read the source and found the relocate path still there (`cmp r11, R101A_MAXCAP; ja relocate`).
**A `kosh` made inside a `mandapa` outlives the block.** Claude gives the numbers and does not build the return unprompted.

## Your patch is with Claude and ChatGPT

**18 files, +757/-68, `git apply --check` clean, not pushed. That is exactly the discipline I have been asking every partner for: write it, verify it, do not merge it.**

**Claude is applying it and running the guard. ChatGPT is auditing whether refusal is the right answer for each of the five.**

## WS1 - and the one question I want from you
**For `s == "ab"` and `s + t`: you chose refusal.** **Was that a choice, or a constraint?**

**If strings could compare contents and concatenate with the current representation, say what it would cost.** **If they cannot - because a string is a bare pointer with no length - say that plainly, because then refusal is the only honest option and the reference must say why.**

**Do not defend the choice. Tell me which it was.**

## WS2 - and the census on v285, fifth run
**Three counts, same method: programs allocating in a loop, programs growing a `kosh` past 1,000, programs allocating without a `mandapa`.**

**And one more: how many of the 274 examples compare or concatenate a string?** **If any do, the patch changes their output and I want the list.**

## WS3 - and the traps you did not fix
**You found five.** **Are there others in the same family - an operation that silently does the wrong thing on a type it was not designed for?** **List them even if you cannot fix them.** **A named trap is better than an unnamed one.**
