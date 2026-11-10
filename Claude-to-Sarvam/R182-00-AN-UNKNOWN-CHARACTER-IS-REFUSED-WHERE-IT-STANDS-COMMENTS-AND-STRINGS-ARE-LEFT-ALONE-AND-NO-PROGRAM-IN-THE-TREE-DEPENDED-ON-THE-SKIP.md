# R182-00 — A character the language does not know is now refused where it stands: named, with its code point, line and column, a caret under it, and a hint when the intention is plain. **Comments and strings are left alone - the lexer has left them before it reaches that point - so the case that would have made this wrong does not arise.** **No program in the tree depended on the skip: 0 of the 783 changes, and the 196 that were refused are refused with the same words.** Staged as v321. ROUND-183 is queued and not started.

## Release line

```
main  (the commit carrying this file; SHA in my chat report)   Sutram 1.0 (v315) - sampurna sutra, unchanged
staged r182-unknown-character c0fdebe8  Sutram 1.0 (v321) - sampurna sutra   (on the v320 tip fe90a9b1; NOT merged)
     crash corpus: 227 cases + manifest, 0 failed - AFTER a change to its runner: eight mutated inputs hold a NUL or
       another unknown character and are now refused at it, in the positioned form file:line:col: Sutram truti [E_..]:,
       which tools/crash_corpus.py did not count as a diagnostic (the first gate run read 8 failed; the runner now accepts it)
     suite: NO-EXPECTATION=4 PASS=327
     gates: 87 PASS / 0 FAIL / 1 NOT-RUN  (Linux, Xvfb; NOT-RUN = Windows execution; evidence-r182/gates-v321.txt)
     guard, the ordinary way, 783 programs, ELF and PE:
       against v320 (fe90a9b1): 587 byte-identical, 196 refused identically, 0 DIFFER
            - and the 196 refusals carry the same message and exit code from v320 and v321 (evidence-r182/refusals.txt)
       against v315 (main):     549 byte-identical, 196 refused identically, 38 DIFFER - v320's 38, the block programs;
                                this round adds none
     installer rebuilt (payload v321): 006ef2cbf0e1c51108914ca8e5ad91dc899a9e3325ae3a7b76d8431df38b45b5
staged v320 fe90a9b1 · v319 4c1159be · 12ef6329 · v318 · v317 · v316-ready - unchanged
```

**The guard is absolute: 0 DIFFER against the compiler this one is built on.** Sanskrit only; no pack touched;
`backups/` untouched. **Why on v320 and not on v315:** every staged change is one chain, and a compiler built
beside it would be a second v316.

## WS2, question 4 first - because it decides whether to build at all

**Does the lexer leave comments and strings before it reaches the skip? Yes - read, then tested.**

`src/sutram_compiler.asm`, `lex`, in the order the code runs for each character:

1. white space (`is_space`: space, tab, LF, CR);
2. **comments: `//` and `/* ... */`, then `#`** - each consumed to its end;
3. the danda, Devanagari digits, names, numbers;
4. at `.try_operator`: **a `"` goes to `.lex_string`, which consumes to the closing quote**;
5. operators and delimiters;
6. **and only then the line that said `; Unknown char - skip`.**

**So a curly quote in a comment or in a string never reaches it.** Gate case `in-comments-and-strings`: curly
quotes, an en dash, an em dash, a rupee sign, `$`, `@`, a no-break space and a zero-width space in a `#` comment,
a `//` comment, a two-line `/* */` comment, a trailing comment after code, and inside a string - **compiles, and
prints the string with every character in it.**

## WS1 - the refusal

```
endash.sm:2:17: Sutram truti [E_AGYAT_AKSHAR]: agyat akshar '–' (U+2013)
      vitti a = 5 – 2
                  ^
Sanket: vyavakalana-chihnam - (U+002D) likhyatam
```

- **It names the character** - the character itself between quotes, and its code point. A character that cannot
  be shown (a control, a no-break space, a zero-width character) is named by code point alone:
  `agyat akshar (U+00A0)`.
- **It names the line and the column** - in the form every other compile error of Sutram uses,
  `file:line:col:`, with the source line and a caret under the character. I did not add `pankti` / `stambh`
  words: one form for all errors is worth more than a second form for this one.
- **It suggests the fix when one is plain** (`evidence-r182/messages.txt`):

| the character | the `Sanket` |
|---|---|
| curly double quotes, `„`, `«`, `»` | `saral uddharana-chihnam " (U+0022) likhyatam` |
| a curly or straight apostrophe, a backtick | `Sutram-bhashayam vakyam " " madhye likhyate - " (U+0022) likhyatam` |
| en dash, em dash, the minus sign U+2212, the two hyphens U+2010/2011 | `vyavakalana-chihnam - (U+002D) likhyatam` |
| no-break and other typographic spaces | `sadharanah avakashah (U+0020) likhyatam` |
| zero-width space, joiners, a byte-order mark inside a line | `adrishyam aksharam etat - apaniyatam` |
| `×` `÷` `≤` `≥` `≠` | `*`, `/`, `<=`, `>=`, `!=` |
| anything else (`$`, `@`, `₹`, an emoji) | no `Sanket` - there is no one obvious fix |

- **The code is `E_AGYAT_AKSHAR`** - beside the existing `agyat naam` of `E_UNDEFINED_NAME`.
- **The Sanskrit of the hints is mine**; nobody who would catch an error in it has read it.

**A correction to the brief: a Devanagari digit is not an unknown character and needs no suggestion.** The lexer
has recognised Devanagari digits since R66; `vitti a = ५ - २` compiles and prints 3 (gate case
`devanagari-digits`).

**Two things kept as they were, deliberately:**
- **A byte-order mark at the start of the file, or of a line, is still passed over.** Notepad writes one; it is
  an editor's mark, not something the student typed. Inside a line it is refused like any other invisible
  character.
- **A byte that is not UTF-8** was already refused before the lexer runs (`E_UTF8`), and still is.

## WS2 - it must not break anything

1. **The examples.** All of `examples/` is inside the guard's 783. **None contains a character that reached the
   skip path** - if one had, it would compile on v320 and be refused on v321, and the guard would show it as a
   DIFFER or a new refusal. It shows neither.
2. **The suite and the crash corpus:** in the release line.
3. **The guard: 0 of the 783 differ.** 587 compile to the same bytes; 196 are refused, **each with the same
   message and exit code as on v320** - so no program that was refused for another reason is now refused for a
   character instead.
4. **Comments and strings:** above.

**So no file in the tree compiled only because a character was swallowed.**

## WS3 - is the quote the right place?

**Yes.** `likha(“hello”)` is refused at 2:11, the opening quote. **The first thing wrong in the line is the
character, and it is the only thing the student can fix.** Up to v320 the quotes vanished, `hello` became a
name, and the message was `agyat naam 'hello'` - true of what the compiler was left with, and useless to the
student, who can see no name called `hello`, only a string. A message has to point at what was typed, not at
what remained after the compiler threw part of it away. And when a line has two such characters, the first is
named (gate case `first-of-two`); fixing it brings the second.

## The proof

**Gate `R182 unknown character`, `tests/r182/test_unknown_character.py`: 21 checks; 17 fail on v320.** Seventeen
refusals, each checked for the exact first line (file, line, column, character, code point), the caret, and the
`Sanket` line or its absence; four programs that must go on compiling. **Under Wine** the Windows compiler gives
the same messages as the Linux one for ten of them (`wine.txt`). **Not run on Windows.**

## One thing this round found and did not touch

**A zero-width joiner or non-joiner (U+200C, U+200D) is refused too.** Up to v320 it was skipped like the rest.
An Indic keyboard can produce one inside a word. Nothing in the tree has one outside a string or a comment (the
guard would show it), so nothing breaks today; **but if names written in Devanagari are meant to allow them, that
is a decision for the lexer's name rule, and I have not made it.** The message at least says what the invisible
thing is.

## Not done, and why

- **No reference change** beyond the status line: the reference has no table of error codes. The changelog and the
  release notes carry the change; the release notes' first limitation (Muse's ranking) is marked closed.
- **Windows** - Wine only.
- **ROUND-183 (queued)** - not started; it is next.
