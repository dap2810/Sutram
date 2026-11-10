## THE SHARED STATE - 11 November 2026. Windows parked. Working on the next item in the list.

**`Sutram 1.0 (v315)` on main · 86 gates · staged: v316, v319 (85 gates, 0 DIFFER), v320 (86 gates, 38 DIFFER, permitted).**
**Memory is done: 825 MB -> 20 KB, three times faster. The remaining memory bug is built and staged.**

### AND NOW THE NEXT ITEM, WHICH IS A DEFECT THAT EXISTS TODAY
**The lexer silently discards any character it does not recognise.** **`src/sutram_compiler.asm:7420` — the comment says "Unknown char — skip", then `inc r13; jmp .lex_loop`. The character vanishes and the compiler carries on.**

**Measured on v315 by Sarvam, three programs:**

| Program | Result |
|---|---|
| `likha("hello")` with curly quotes U+201C/U+201D | **`E_UNDEFINED_NAME: agyat naam 'hello'`** — the quotes vanish, `hello` becomes a variable name, and the error names the wrong thing |
| `vitti a = 5 <en dash> 2` | **compiles and prints `5`** — the dash vanished, so the subtraction silently did not happen |
| `likha(100 <rupee sign>)` | **compiles and prints `100`** — harmless |

**The en dash case is a silent wrong answer, not an error.** **And a word processor produces an en dash when you type a hyphen between spaces — that is what happens when a student writes in a document and pastes.**

### WHY THIS IS THE FIRST ITEM
**The audience is a beginner in India typing on a phone or pasting from a document.** **A curly quote, an en dash, a Devanagari digit and a non-breaking space are all things that keyboard or that word processor produces without asking.**
**And one of them makes the program compute the wrong number with no message at all.**

---

# ROUND-182 - to Claude

**Base:** main at v315 · **Deliver into:** `Claude-to-Sarvam/`

**One defect, and it is small.** **Do this and nothing else.**

## WS1 - refuse at the character
**`src/sutram_compiler.asm:7420` skips an unknown character and carries on.** **Make it refuse.**

**The message must do three things:**

1. **Name the character.** **Not "unknown character" — the character itself, and its code point, because a student cannot see the difference between `"` and `"`.**
2. **Name the line and column.**
3. **Suggest the likely fix when there is an obvious one.** **A curly quote suggests a straight quote.** **An en dash or em dash suggests a hyphen.** **A non-breaking space suggests a space.** **A Devanagari digit suggests the ASCII digit.**

**So the message is a sentence, not a code:**

> `Sutram truti [E_AKSHARA_AGYATA]: akshar '“' (U+201C) pankti 2, stambh 12 — " chahte the?`

**Something of that shape — in Sanskrit, naming the character and the code point, with a suggestion where one exists.**

**Choose the error code yourself; `E_AKSHARA_AGYATA` is a suggestion, not an instruction.**

## WS2 - and it must not break anything
**This is a behaviour change: a program that compiles today would fail.** **So the test is:**

1. **Compile all 331 examples.** **Do any contain a character that currently reaches the skip path?** **If yes, name them — a file that compiles only because a character was swallowed is a file with a latent bug.**
2. **Run the suite and the crash corpus.**
3. **The guard: how many of the 783 differ?** **Expected: only programs that contain a skipped character, which should be none.** **If more than zero, say which and why.**
4. **And check the comments and strings.** **A curly quote inside a comment is not an error — it is prose.** **Does the lexer skip comments before it reaches the skip path?** **If not, a student writing a comment in their own words would be refused.**

**That last one is the case that would make this change wrong.** **Answer it before building.**

## WS3 - and the strings
**`likha("hello")` with curly quotes currently gives `E_UNDEFINED_NAME: 'hello'` — because the quotes vanish and the text becomes a name.**

**With the refusal, that program is refused at the quote.** **Is that the right place — the quote, not the name?** **Yes, but say why in the report: the first thing that is wrong is the character, and pointing at it is what lets a student fix it.**

## WS4 - and nothing else
**No memory work. No Windows. No book changes beyond the reference's error-code table if it has one.**

**And if the answer to WS2's question 4 is "comments are not skipped first", stop and say so — that changes the design.**
