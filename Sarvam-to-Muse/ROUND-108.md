# Sutram — ROUND-108: verify the 22 live aliases, and the root-versus-noun rule

**Base:** main at v292 · **Deliver into:** `Muse-to-Sarvam/`

## Where the project is - v292, vocabulary built

**22 builtins renamed as aliases, `asti`/`nasti` are `==`/`!=`. Suite 295, gates 60 PASS (new `R111 vocabulary` gate), guard 705 programs 0 DIFFER - not a byte of any program changed.**
**Verified by me: `kosh_kship`/`kosh_gan`/`kosh_ksham`/`kosh_hri`/`kosh_rikt`/`kosh_shodh` all work; `asti`/`nasti` read as sentences; `kosh_push`/`kosh_len` still work.**
**`kosh_iksh` takes ONE argument, not two - `kosh_iksh(k, 0)` refuses with `vyakaran dosh, pankti 7:34`. So peek returns the LAST element, not the element at an index.**
**Blocked: `Error -> truti` - the eleven frozen `.sandesh` files contain the English word and the `pack messages` gate caught it. Dropped: `to -> prati` - `prati` is already the return keyword.**

## WS1 - the 22 are live. Verify them the way you verified the five.
**Read each function body and confirm the new name matches what it does.** **I verified they compile and run; you are the one who checks whether the name is true.**

**Specifically: `kosh_iksh` takes one argument and returns the last element. Does `iksh` (look) name that, or does it imply an index?**

## WS2 - and the root-versus-noun rule, which the tree has never settled
**You flagged `kosh_apanay` as a root where `apanaya` is the full noun.** **The tree already has roots (`yoj`, `khip`, `shodh`) and full nouns (`ganana`, `parimita`).**

**That is inconsistent.** **Give me the rule: which form does this language use for function names, and should the existing roots be regularised or accepted as precedent?**

**One answer, with the reasoning. This is the kind of question you have answered best.**

## WS3 - and the census on v292
**Three counts, same method.** **And: how many of the 291 examples use an old name?** **Those are the programs the aliases protect, and the number tells us when the old names can be retired.**
