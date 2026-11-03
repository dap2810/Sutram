# Sutram — ROUND-112: three small things, one commit.

**Base:** main at v292 · **Deliver into:** `Claude-to-Sarvam/`

## Where the project is - v292, vocabulary built

**22 builtins renamed as aliases, `asti`/`nasti` are `==`/`!=`. Suite 295, gates 60 PASS (new `R111 vocabulary` gate), guard 705 programs 0 DIFFER - not a byte of any program changed.**
**Verified by me: `kosh_kship`/`kosh_gan`/`kosh_ksham`/`kosh_hri`/`kosh_rikt`/`kosh_shodh` all work; `asti`/`nasti` read as sentences; `kosh_push`/`kosh_len` still work.**
**`kosh_iksh` takes ONE argument, not two - `kosh_iksh(k, 0)` refuses with `vyakaran dosh, pankti 7:34`. So peek returns the LAST element, not the element at an index.**
**Blocked: `Error -> truti` - the eleven frozen `.sandesh` files contain the English word and the `pack messages` gate caught it. Dropped: `to -> prati` - `prati` is already the return keyword.**

## WS1 - `kosh_iksh` takes one argument. Is that right?
**I tested it: `kosh_iksh(k)` returns the last element; `kosh_iksh(k, 0)` is a grammar error.**

**Two questions:**
1. **Is "peek the last element" the intended behaviour?** **If yes, the reference must say so, because every other language's `peek` means the top of a stack - which is the last element, so this may be correct and merely undocumented.**
2. **If it should take an index, that is a new capability and I want it costed before it is built.**

**Document it either way. A function whose arity surprises the maintainer will surprise a student.**

## WS2 - `Error -> truti`: settle it
**You left it alone because the `pack messages` gate caught the conflict with the eleven frozen `.sandesh` files. You were right to stop.**

**Answer this plainly: are the `.sandesh` files language packs, or are they message strings?** **If they are message strings, update them and the rename lands. If they are packs, `Error` stays and the reference must say why one English word remains.**

**That is a judgement about your own tree and I will take your answer.**

## WS3 - and the two Muse notes I did not act on
**`kosh_apanay` is the root form; the full noun is `apanaya`.** **Muse flagged it, not rejected it.** **The project already accepts roots - `yoj`, `khip`, `shodh` are roots.** **Say which rule you would apply and apply it consistently, or tell me the tree is inconsistent and leave it.**

**And the two other flags Muse raised in R106 that I never saw - apply its recommendation.**

## WS4 - and one more thing
**The reference and the vocabulary HTML both need the 22 new names with the old names as aliases.** **If that is not done, the docs now describe a language that no longer matches the compiler.**
