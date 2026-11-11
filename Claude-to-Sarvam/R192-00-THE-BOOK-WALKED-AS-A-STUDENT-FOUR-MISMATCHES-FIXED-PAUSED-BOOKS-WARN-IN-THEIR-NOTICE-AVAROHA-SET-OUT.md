# R192-00 — Walking the book as a student found **four places where the book says one thing and the language does another**, all in the first two chapters and the input section, all fixed and gated. **The four paused books are NOT translated: the owner was asked and chose a warning in their notice instead.** `avaroha` is set out with what a decision needs and the lines a student copies today. **Guard: 0 DIFFER. The tree is ready to merge when the Windows run passes.**

## Release line

```
main  (the commit carrying this file; SHA in my chat report)   Sutram 1.0 (v315) - sampurna sutra, unchanged
staged r192-paused-books-and-avaroha 702d801c   Sutram 1.0 (v326) - sampurna sutra      (on r191-input-story ad24e23e)
     DOCUMENTS AND ONE TEST ONLY: the compiler, rebuilt from source, is byte-identical to ad24e23e's; lib/ is untouched
     crash corpus: 227 cases + manifest, 0 failed · suite: NO-EXPECTATION=4 PASS=332 · contracts 139
     gates: 93 PASS / 0 FAIL / 1 NOT-RUN  (Linux, Xvfb; NOT-RUN = Windows execution; evidence-r192/gates-v326-r192.txt)
     installer (payload v326, with this round's documents): c47936ca009e62c35503d64afd7d777ab9b22c26953335948ae698a93e7b8ef3
     the guard, against the v326 tip ad24e23e: 788 programs - 592 byte-identical, 196 refused identically, 0 DIFFER
```

Sanskrit only; no pack touched; `backups/` untouched. `R159 no personal paths`: 0. Not merged. No version step.

## 1. The four paused books

**The files and the sentence in each** (`evidence-r192/paused-books.txt`), all in the section "Descending Loops":

| file | line | the sentence |
|---|---|---|
| `docs/sutram-book-hindi.html` | 399 | प्रारंभ मान अंतिम मान से बड़ा हो, तो गणना स्वतः उलट जाती है: |
| `docs/sutram-book-gujarati.html` | 364 | શરૂઆતનું મૂલ્ય અંતિમ મૂલ્ય કરતાં મોટું હોય તો, ગણતરી આપોઆપ ઊતરે છે: |
| `docs/sutram-book-tamil.html` | 370 | தொடக்க மதிப்பு இறுதி மதிப்பை விட பெரியதாக இருந்தால், எண்ணிக்கை தானாகக் குறையும்: |
| `docs/sutram-book-telugu.html` | 398 | ప్రారంభ విలువ గరిష్ట విలువ కంటే పెద్దదైతే, లెక్క స్వయంగా తగ్గుతుంది: |

Each says: if the start is greater than the end, the count goes down by itself.

**The sentence is not rewritten - and that is a decision, not an omission.** Your brief says "fix the sentence in
all four ... translate". The standing rule says the other packs are frozen and a frozen defect is reported, not
fixed. **The two disagree, so I asked the owner. He chose: leave each book's text as it is, and put the warning in
the notice at the top.** I also cannot check a Tamil or Telugu sentence of my own, and nobody on this project reads
them back.

**What each book now says at its top** (line 63, the notice that has been there since R157; one line changed per
file, in English, as the notice already was):

> ... this edition has no chapter on memory (`kosh`, `mandapa`, slices) **and does not teach reading a line of text
> (`vartani_grahan`, `vartani_tak_ank`). One sentence in it is known to be false (R192, 11 November 2026):** the
> section "Descending Loops" says a `chakra` counts down by itself whenever the start is greater than the end. That
> is true only when both ends are written as numbers (`chakra i = 5 tak 1`); with a variable at either end the loop
> counts **up**, and runs no times at all, with no message, when the start is past the end. To count down from a
> variable use `yavat` - see "Descending Loops" in the English edition. The text of this edition is left as it was.

**Is each otherwise current? No - none of the four, and the same way:**

| | Hindi | Gujarati | Tamil | Telugu |
|---|---|---|---|---|
| describes the language as of | v294 | v294 | v294 | v294 |
| chapters | 21 | 21 | 21 | 21 |
| the memory chapter (19 in the English book) | **no** | **no** | **no** | **no** |
| reading a line (`vartani_grahan`), the converter | **no** | **no** | **no** | **no** |
| a marker saying it is paused, naming the version | yes, since R157 | yes | yes | yes |

**So the marker existed; what it lacked was the warning.** Everything from v295 to v326 is missing from all four -
I have listed the two largest gaps and the one false sentence, not audited them line by line. **The other six
frozen packs have no book.**

## WS1 - `avaroha`, in `docs/WHATS-LEFT.md`

Section 3 ("Decisions waiting for the owner") now has **"Counting down: `avaroha`, as a question with everything a
decision needs"**. In short:

**What a student does today - it comes first there, as you said it matters most:**

```
vitti i = n                 # 1. start at the top
yavat (i >= 1) {            # 2. go on while i has not passed the bottom
    likha(i)                #    ... the body of your loop ...
    i = i - 1               # 3. step down - the last line of the body
}
```

Run: `n = 5` prints 5 4 3 2 1; `n = 0` runs no times. One trap is named with it: an `agrim` above line 3 skips the
step and the loop never ends.

1. **What it would mean:** a word in the place of `tak` - `chakra i = n avaroha 1` - both ends included, no passes
   when the start is below the end. The two other shapes (a modifier, a loop of its own) are listed with why not.
2. **What it would cost:** **no keyword if it is contextual**, as `arabhya` and `paryantam` are (the reference
   counts 25 core keywords, so a reserved word would be the 26th - I still do not find a count of 33); one parser
   branch where `tak` is read; a version step, §6a, both books, an example, a gate. **And `chakra i = 5 tak 3`:**
   either it keeps counting down (nothing breaks, `tak` keeps two meanings), or `tak` means "up" only and that line
   is **refused when compiled** - it cannot be left to run no times - which rewrites 18 loops in 12 files.
3. **Why not now, in one sentence:** a countdown and an empty range cannot be told apart at run time when an end is
   a variable, so only a word can say it, and a new word is the owner's to decide.

**One thing I wrote there as NOT TESTED:** the compiler's counting-down code is today only reached with two written
numbers. Whether it is right with a variable end is unknown until someone builds the branch.

## WS2 - the book, walked as a student (`evidence-r192/walk-before-r191-tip.txt`, `walk-after-r192.txt`)

The English book, from "What you need" to the end of the input section, typed exactly as printed.

| step | what the book said | what the student got | |
|---|---|---|---|
| **install** (ch. 1) | "a Linux x86-64 system (or WSL on Windows)" - and nothing on how to get the `sutram` command on Linux | on Windows, chapter 17 installs natively, "No WSL". On Linux, `sutram` is "command not found": the file is `sutram_compiler` | **mismatch 1 - fixed** |
| **first program** (ch. 2) | `Siddh: 97 baait sankalit`, "about 90 bytes" | `Siddh: 112 baait sankalit` (and 112 at v315 too: this was stale before the chain began) | **mismatch 2 - fixed** |
| run it | `Namaste, Sutram!` | `Namaste, Sutram!` | agrees |
| **`grahan()` example** | five lines, with `krama` in a `yadi` and no loop round it | typed inside `mukhya()`: **refused**, `E_AVARTAN_VINA` - "krama ... atra avartanam na asti" | **mismatch 3 - fixed** |
| read a name (`vartani_grahan`) | `Namaste, <name>!` | `hello` -> `Namaste, hello!` | agrees |
| read every line | echoes each line, ends at end of input | does | agrees |
| **the converter program, `hello`** | "hello is reported" | `sankhya na: hello` - **a named report, not a refusal and not a wrong answer** | agrees |
| **the converter program, `42`** | "42 gives 84" | `84` | agrees |

**Your question 4, answered exactly: typing `42` does not print 42, and the book does not say it will.** The
program the book teaches prints `n * 2`, so that the reader sees a number was really made, and its comment says
"42 gives 84". If you would rather it print 42, it is one character; I left it.

**And `hello` where `grahan()` expects a number: a wrong answer - 0, in silence.** That is `grahan`, it is unchanged,
and the book said so in the *next* section. **It now says so where `grahan` is taught.**

**Mismatch 4, same kind, outside the input path:** the `sutram -i` session printed 54 and 201 bytes (it is 69 and
216), and the `--lang gujarati` run showed Sanskrit messages and 228 bytes (the compiler answers in Gujarati, 243).

**The fixes, in the English and the Sanskrit book:**

- "What you need" names Windows 10/11 with chapter 17, and says that on Linux the compiler is `sutram_compiler`.
- The printed sizes are the sizes the compiler prints.
- **The `grahan()` example is a whole program** that adds the numbers it is given until the input ends:
  `5`, `-1`, `3` -> `yoga: 7`; a last number with no newline is counted; `hello` -> `yoga: 0`, and the paragraph
  under it says **"Type `hello` and it is counted as 0, with no message"** and points at the two sections after.
- **Gate `R190 chakra and converter`: 26 checks (was 20).** For each book it now compiles the first program and
  compares the printed size with the compiler's, compiles every whole program in the input section, and runs the
  `grahan` program on four inputs. A stale size or an uncompilable example now fails a gate.

**On Windows (Wine, not Windows):** `sutram.exe namaste.sm namaste.exe` -> `Siddh: 108 baait sankalit`, prints
`Namaste, Sutram!`; the converter as `.exe` prints `84` for `42` and `sankhya na: hello` for `hello`, with CRLF and
with LF line ends. Chapter 17 prints no size, so nothing to compare.

**A wider look, since the walk found four in three chapters:** every code block in both books that is a whole
program was compiled (`evidence-r192/every-whole-program-in-the-books.txt`). **English: 24, of which 23 compile;
Sanskrit: 23, of which 22 compile. The one refused in each is the Gujarati program, which needs `--lang gujarati`
and compiles with it.** That is "compiles", not "prints what the page says" - see below.

## WS3 - the guard

**0 DIFFER** against the v326 tip `ad24e23e`: 788 programs, 592 byte-identical, 196 refused identically, 0 source
files changed. The compiler rebuilt from source is the same file as R191's; `win/sutram.exe` has the same SHA-256.

## WS4 - the state, for the owner

**It is ready to merge when the Windows run passes.** The chain from v316 to v326 is eleven versions on main's
v315, each gated on Linux at 93 of 93 with the suite at 332, and it holds nothing I know to be wrong that main
does not also hold - main is the worse tree in every respect measured. **Nothing is waiting on me before you run
the checklist**, and the checklist is re-pinned to this commit. Two things you should know going in, neither a
reason to wait: **one known silent wrong answer goes in with the merge** - `chakra i = 5 tak e` runs no times -
documented in the reference and both books, with the `yavat` form beside it, and closing it is your decision on
`avaroha`, not a repair; and **the books have been checked only as far as "every whole program compiles"** - the
outputs printed beside them were compared with the language for three chapters, and those three chapters had four
errors, so the other chapters probably have some.

## Not done, and why

- **The four paused books' sentence is not translated** - the owner's choice, above.
- **The rest of the book was not walked.** Only chapters 1 and 2 and the input section were followed step by step.
- **The new Sanskrit sentences** (the paragraph under the `grahan` program, the size) **are mine and unread** by
  anyone who would catch an error in them.
- **Seen, not investigated:** in `sutram -i`, with input from a pipe, the banner's commands `nirgat` and `sahayata`
  were answered with `E_UNDEFINED_NAME`, at v315 as well. It may be different at a keyboard. Not in the input path.
- **`avaroha`: nothing designed past the page, nothing built.**
- **Windows: NOT RUN.** Wine only, and only for the two programs above. The checklist
  (`Claude-to-Sarvam/SUTRAM-WINDOWS-ACCEPTANCE.md`) is re-pinned: commit `702d801c...`, installer `c47936ca...`;
  the compiler in it is the same file (`F22FEA3F...`), so every expected output stands. All five pinned files were
  downloaded again and match (`evidence-r192/checklist-downloads-and-hashes.txt`). Its PowerShell blocks are still
  NOT RUN.
- **The guard was run for Linux executables only** - no executable-producing file changed.
- **ROUND-183 (the performance baseline) is still not started.**
