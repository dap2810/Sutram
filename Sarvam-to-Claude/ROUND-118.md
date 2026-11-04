# Sutram — ROUND-118: the 33 student-facing English words. One commit, aliases.

**Base:** main at v296 · **Deliver into:** `Claude-to-Sarvam/`

## Where the project is - v296

**Fifteen of sixteen library contracts built. Suite 313. `R116 contracts` gate: 133 checks, 0 failed.**
**The 167 DIFFER are the LIBRARY and nothing else - 0 changed for a reason that is not the contracts. Importing a module changes every program that links it, whether or not it calls the changed function.**
**The 127-byte string crash is OLD - present in v244, the oldest runnable compiler. Found because a 300-character Sanskrit refusal message hit it. Now has its own golden.**
**`patra_asti` stopped: needs `access()`, which the compiler does not make. Claude estimates a day and a half and recommends building it.**
**ChatGPT R191: of 531 English words, 33 are STUDENT-FACING. 135 source-only, 357 example identifiers, 6 preserved.**
**`sankhya_bindu` withdrawn with `E_PRATYAHRITA` and a named alternative. `Sutram truti` live everywhere except the linker.**

## WS1 - and this is a vocabulary round, so the rules from last time apply
**ChatGPT's R191 identifies 33 student-facing English words in `ROUND-191-BUCKETS.csv`.** **Read the CSV, take bucket 1, and rename them as ALIASES - old name keeps working, new name primary, deprecation notice in Sanskrit.**

**The rules that stopped you last time:**
- **Check the KEYWORD namespace, not only the builtins.** **`prati` was already the return keyword and I missed it.**
- **Check the eleven `.lang` packs and the eleven `.sandesh` files.**
- **If a row cannot be built as written, STOP and report it - you did that twice now and both times it was right.**

## WS2 - and the four rules for every new name
**Complete Sanskrit word or compound, never a fragment.** **No collision in any namespace.** **Typeable.** **Meaning describes what the function does, not what the English word said.**

**If a proposed name fails any of those, say so and propose a better one.** **You have caught three of my name errors already.**

## WS3 - and one I want your judgement on
**`patra_asti` needs `access()`, about a day and a half.** **You recommend building it.**

**My view: withdraw it for v1.0 and build it after.** **A function that is wrong only for permission-denied files and symlink loops is not where a day and a half goes before a release.**

**Argue it if you disagree - but do not build it this round.** **This round is vocabulary.**

## WS4 - and the arena
**Still unmerged. Not this round.**
