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

# ROUND-167 - to Muse, read only

**Base:** main at v315 · **Deliver into:** `Muse-to-Sarvam/`

**Read only. Nothing to compile or run.**

**The lexer silently discards any character it does not recognise.** **Claude is being asked to refuse instead.** **You are being asked for the list, which is the thing that makes the refusal correct.**

## Task 1 - and this is the round: every character the lexer swallows
**Read the lexer and list every character that reaches the skip path at `src/sutram_compiler.asm:7420`.**

**For each, say:**

1. **The character and its code point.**
2. **Whether a normal keyboard, a phone keyboard, or a word processor produces it without asking.** **This is the test that decides whether it matters.**
3. **What a program containing it does today — compiles silently, compiles with a wrong parse, or fails somewhere confusing.**
4. **What the compiler should suggest instead, if anything.**

**The ones I would check first, because I measured two of them myself:**

- **the curly quotes `"` `"` `'` `'`** — measured: `likha("hello")` gives `E_UNDEFINED_NAME: 'hello'`
- **the en dash and em dash `–` `—`** — **measured: `5 – 2` compiles and prints `5`. A silent wrong answer.**
- **the rupee sign `₹`** — measured: vanishes harmlessly
- **the non-breaking space** — a word processor produces it, and it looks like a space
- **the zero-width joiner and non-joiner**
- **Devanagari digits `०` to `९`**
- **`©` `®` `°` `×` `÷`**
- **the backtick**

**And the one I would check first of all: is the skip path reached inside a comment or a string?** **A curly quote in a comment is prose, not code.** **If comments are not skipped before the skip path, a refusal would reject a student writing a comment in their own words — and that would make the fix worse than the defect.**

**Answer that before the list. It decides whether the fix is safe at all.**

## Task 2 - and what the error should say
**Claude will write the message.** **You have read how every other error in this language is written — 65 of them.**

**So: what does a good one look like, and which of the 65 is the closest model to copy?** **Give the shape, not the exact words.**

**And: is there an error code already in the 65 that fits, or does this need a new one?**

## Task 3 - and the second item, briefly
**The next thing after this is that a program cannot read text from the user.**

**Read the standard library and say: what is already there that a "read a line" function could be built from?** **Does the language read files?** **Does anything read from standard input?** **What is missing — a syscall, a buffer, or just the function?**

**One paragraph. It sets the size of the next round.**
