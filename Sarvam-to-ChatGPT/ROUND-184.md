# Sutram — R184: the WHOLE-TREE English audit. Every word, everywhere.

**Base:** main at v292 · **Deliver into:** `ChatGPT-to-Sarvam/`

## Why this round exists

**We audited the builtins and the error prefix.** **We never audited the rest of the tree.**

**The owner's rule is that this language is Sanskrit first.** **So: find every English word a user of this language can SEE, and give a Sanskrit replacement with a collision check.**

**This is reading-only work and it is the largest single piece of Sanskrit progress left.**

## WS1 - what a user sees, in four places
**Audit these four, and only these four - not the docs prose, which is written in English deliberately:**

1. **`examples/*.sm`** - every string literal and every identifier a student would read.
2. **`lib/*.smlib`** - every `prakriya` name, parameter name, and string literal. **306 functions.**
3. **`lang/*.lang`** - every keyword and every comment that a reader of a pack would see.
4. **`src/sutram_compiler.asm`** - every user-facing string not already audited. **`Sutram Error` is known (748 across packs) - exclude it and count the rest.**

**For each: the English word, where it appears, how many times, and a Sanskrit replacement.**

## WS2 - and the replacement, with the rules applied
**Complete word or compound, never a fragment.** **Roots are acceptable where the project already uses them (`yoj`, `khip`, `shodh`).** **No collision with any builtin, keyword, or `.lang` entry.** **Short enough to type.**

**Give two options per word where a good second exists, and say which you would take.**

## WS3 - and the count that decides whether this is a round or a project
**How many distinct English words are there in total, and how many occurrences?**

**If it is under 50 words, this is one round.** **If it is 300, it is a workstream and the owner needs to know that before we start.**

**Give me the number first, then the table.**

## WS4 - and the one thing not to touch
**Do not propose changing `Sutram` itself.** **It is the name of the project and it is a Sanskrit word already.**
