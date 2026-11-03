# Sutram — ROUND-111: build the 25 clean names. Decide the 3 blocked ones. Fix the 5 wrong ones.

**Base:** main at v291 · **Deliver into:** `Claude-to-Sarvam/`

## You stopped correctly and that is the right instinct
**Three rows cannot be built as written, and you reported instead of shipping a mixed vocabulary.** **That is exactly what the brief asked for.**

## WS1 - my decisions on your three collisions
**Collision 1, `to -> prati`: DROP THE ROW ENTIRELY.** `to` stays as it is; `prati` stays as the return alias. **ChatGPT R179 and you agree, and you are both right - I checked the builtin namespace and not the keyword namespace. My error.**
**Collision 2, `Error -> truti`: update the 11 `.sandesh` files in the same commit.** They are message strings, not language packs. **The frozen-pack rule is about the eleven languages, not about the English word inside a message.** **If you believe that crosses the rule, say so and leave `Error` alone - a mixed vocabulary is worse than an English word.**
**Collision 3, `vartani_yoj` and the scanner bug: use a different name.** **`vartani_sandhi`** (सन्धि, "junction") - a real Sanskrit word for joining, and it does not touch the scanner. **Verify it does not trip the same bug; if it does, report and leave `vartani_cat` alone.**

## WS2 - my decisions on Muse's five wrong names
1. **`kosh_dequeue`: `kosh_muc` is wrong - it removes, it does not release. Use `kosh_apanay`** (अपनय्, "take away"). **`kosh_pop` keeps `kosh_hri`** - pop takes from the end, dequeue removes from the front, and the two words distinguish that.
2. **`akshar_tas` is backwards and `tas` is a suffix, not a word. Use `anka_akshar`** - "number-to-letter", which is what the function does: `char_from(66)` gives a character from a code.
3. **`likha_bindu`: `bindu` names a point it does not print. Use `likha_santat`** (सन्तत, "continuous") - it prints without a break, which is the distinguishing feature.
4. **and the other two Muse flags - apply its recommendation and say which you applied.**

## WS3 - and then build the 25 that are clean
**Aliases only. Old names keep working, new names primary, deprecation warning names the replacement.** **Goldens: new name works, old name works, warning fires on old and not new.**

**`asti` and `nasti` for `==` and `!=` are in the clean set - four goldens, true and false each.**

## WS4 - and the guard
**699 programs. 0 DIFFER except where a deprecation warning now prints.** **If any program changes behaviour, stop and name it.**

**Do not merge the arena. Do not touch the reference-type class. Vocabulary only.**
