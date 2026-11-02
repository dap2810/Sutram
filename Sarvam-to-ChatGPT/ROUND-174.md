# Sutram — R174: the string design, in full. And Muse's eight new traps.

**Base:** main at v286 · **Deliver into:** `ChatGPT-to-Sarvam/`

## Where the project is

**Compiler v286.** Muse's FIXALL patch is applied: five silent wrong answers now refuse. Suite 273, guard 683 programs, gates 59 PASS / 1 FAIL (installer v243 vs v286).
**All three of us agree strings should WORK, not refuse.** Muse: "refusal was a choice for `==`, a constraint for `+`". ChatGPT R173: "typed strings should compare contents and concatenate into a fresh value. NUL-terminated pointers can already support both." **And I proved it: `akshar("abc",0)` = 97, `akshar("abc",3)` = 0, and a twelve-line `samaan()` returns 1/0/0 correctly for `ab`/`ab`, `ab`/`cd`, `ab`/`abc`.**
**Muse found EIGHT MORE silent traps.** **Examples are 277, not 274 - my count was stale for the third time.**

## Your R173 said request changes, and I agree with every point
**Straight-line bypass, inconsistent fast-path rules, environment-dependent recursion guard.** **Claude applied the patch and fixed four gates it broke - gates went 55/5/1 on the verbatim patch to 59/1/1 after its fix.**

## WS1 - design the two operations properly
**`==` compares contents. `+` concatenates into a fresh value.** **Both reachable with NUL-terminated strings, as you said.**

**Give me the full specification:**
- **What does `==` do on a string and a non-string?** **Refuse, or compare the non-string's text form?**
- **Where does a concatenated string live?** **Scratch, block, or region?** **If it is scratch, what happens when it escapes?**
- **Is a length prefix worth it, or is NUL-termination sufficient?** **You said prefix is an improvement, not a prerequisite - confirm or correct.**

## WS2 - and Muse's eight new traps
**`Muse-to-Sarvam/ROUND-100-CHOICE-CONSTRAINT-CENSUS-TRAPS.md` lists eight more silent traps.** **Read them and say which are the same class as the five, and which are new.**

**And the question that matters: is there a systematic way to find this class, or does each one have to be found by someone happening to try it?** **If there is a systematic way, that is worth more than fixing eight.**

## WS3 - and the README sentence, sixth time
**What does a student read first about text in Sutram?** **Write it. One paragraph. If strings are half-finished, say so in the sentence.**
