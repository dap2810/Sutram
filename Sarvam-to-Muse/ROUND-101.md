# Sutram — ROUND-101: your eight traps, and the census on v286

**Base:** main at v286 · **Deliver into:** `Muse-to-Sarvam/`

## Where the project is

**Compiler v286.** Muse's FIXALL patch is applied: five silent wrong answers now refuse. Suite 273, guard 683 programs, gates 59 PASS / 1 FAIL (installer v243 vs v286).
**All three of us agree strings should WORK, not refuse.** Muse: "refusal was a choice for `==`, a constraint for `+`". ChatGPT R173: "typed strings should compare contents and concatenate into a fresh value. NUL-terminated pointers can already support both." **And I proved it: `akshar("abc",0)` = 97, `akshar("abc",3)` = 0, and a twelve-line `samaan()` returns 1/0/0 correctly for `ab`/`ab`, `ab`/`cd`, `ab`/`abc`.**
**Muse found EIGHT MORE silent traps.** **Examples are 277, not 274 - my count was stale for the third time.**

## "Refusal was a choice for `==`, a constraint for `+`" is the best sentence anyone has written this week
**It answered the question exactly, and it made the next round obvious: `==` should be implemented, `+` should be implemented, and both are reachable.**

## WS1 - the eight new traps, in full
**You found eight more.** **For each: the program, the wrong behaviour, and whether it is the same class as the five.**

**And the same question I asked ChatGPT: is there a systematic way to find this class?** **A checklist, a generator, a pattern in the source?** **If eight more exist after five were found, there are probably more, and finding them one at a time is not a plan.**

## WS2 - the census on v286, sixth run
**Three counts, same method.** **And the one that matters now: how many of the 277 examples compare or concatenate a string?** **Those are the programs the next change will alter, and I want the list before Claude touches anything.**

## WS3 - and the count I keep getting wrong
**You have corrected my example count three times - 259, then 274, now 277.** **Where do I get it from, so I stop asking you?** **Name the command or the file.**
