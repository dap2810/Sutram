# R191-00 — The contradiction is settled by a fact: **Muse read v325, where the sentence is; the fix landed in v326, commit `c744fc98`. Both of us were right about the tree we read.** **But checking WS2 found a real fault, and it is mine: the three lines I taught for the new converter printed `n * 2` without looking at `ok[0]`, so `hello` printed 0.** That is the silent answer the function exists to prevent, in the example that teaches it. Fixed in the reference and both books, and now in the gate. **The word for counting down: `avaroha`.** And the four frozen books still say "counts down automatically".

## Release line

```
main  (the commit carrying this file; SHA in my chat report)   Sutram 1.0 (v315) - sampurna sutra, unchanged
staged r191-input-story ad24e23e   Sutram 1.0 (v326) - sampurna sutra      (on r190-chakra-and-converter c3b7b9ef)
     DOCUMENTS AND ONE TEST ONLY: the compiler, rebuilt from source, is byte-identical to c3b7b9ef's; lib/ is untouched
     crash corpus: 227 cases + manifest, 0 failed · suite: NO-EXPECTATION=4 PASS=332
     gates: 93 PASS / 0 FAIL / 1 NOT-RUN  (Linux, Xvfb; NOT-RUN = Windows execution; evidence-r191/gates-v326-r191.txt)
     installer (payload v326, with the corrected documents): 2a940c75bedd327dfdd3b1e9463ea179435d3aea11e76ae7ed84ec6b851e0f62
     the guard, against the v326 tip c3b7b9ef: 788 programs - 592 byte-identical, 196 refused identically, 0 DIFFER
     the guard, against v325 22466bda:        581 identical, 196 refused, 10 DIFFER, 1 new
            - the 10 are exactly R190's list: the programs that bring in `vakyank` (compared line for line)
```

Sanskrit only; no pack touched; `backups/` untouched. `R159 no personal paths`: 0. Not merged. **No version
step:** nothing a program can observe changed, so this is v326 with corrected documents, as R181 was v320's.

## WS1 - the check, with quotes (`evidence-r191/quotes.txt`, taken from git at each commit)

**1. The English book, `docs/sutram-book-english.html`, line 400:**

| commit | the sentence |
|---|---|
| `22466bda` - v325 | *"If the start value is greater than the end value, the loop counts down automatically:"* |
| `c3b7b9ef` - v326 | *"If both ends are **written as numbers** and the start is the greater, the loop counts down:"* |

followed, from v326, by a paragraph that begins *"**This works only with written numbers.**"* and says a loop
with a variable end counts up and may run no times, with the `yavat` form to count down.

**2. The Sanskrit book, `docs/sutram-book-sanskrit.html`, line 357:**

| commit | the sentence |
|---|---|
| `22466bda` - v325 | *"प्रारम्भिकमूल्यम् अन्तिमात् मूल्यात् बृहत्तरं भवति चेत्, गणना स्वतः अवरोहति:"* ("...the count descends by itself") |
| `c3b7b9ef` - v326 | *"यदि उभे सीमे **सङ्ख्यारूपेण लिखिते** स्तः, प्रारम्भिकमूल्यं च बृहत्तरम्, तर्हि गणना अवरोहति:"* ("if both ends are written as numbers...") |

**3. The reference, `docs/LANGUAGE-REFERENCE.md`** (it never had the sentence; it had a comment and no rule):

> `chakra j = 5 tak 1 {      # for (descending - both ends written as numbers: §6a)`
>
> **Which way a `chakra` counts is decided when it is compiled, not when it runs.** It counts **down only when both
> ends are written as numbers** ...

**4. Does any of the three still claim a `chakra` counts down automatically? No.** Searched on the tip for the
English phrase and the Sanskrit one: 0 files.

**So: Muse was reading v325, and was right about v325.** R172's words, as your brief quotes them, are "the **v325** books' 'Descending
Loops' section was not corrected" - true: the R189 round that found the defect put the rule in the reference
and did not touch the books. **The books were corrected one version later, in `c744fc98` ("v326 (R190): a
chakra shaped like a countdown is warned about...").** My R190-00 sentence was about v326 and was also true.
**Neither of us read the wrong file; we read two commits.**

**What was missed, and it is not one of the three: the four frozen books still say it.**

| book | the sentence at the same place |
|---|---|
| Hindi, line 399 | "...गणना स्वतः ..." (the count ... by itself) |
| Gujarati, line 364 | "...ગણતરી આપોઆપ ઊતરે છે" (the count descends automatically) |
| Tamil, line 370 | "...எண்ணிக்கை தானாக..." (the count ... by itself) |
| Telugu, line 398 | "...లెక్క స్వయంగా తగ్గుతుంది" (the count decreases by itself) |

**Frozen, so reported and not fixed.** **A student reading any of the four is still taught the false rule.**

## WS2 - the input story: one of my own lines was the defect

**1. What it is.** `vartani_tak_ank(s, ok)`, in `lib/vakyank.smlib`; a program brings it in with `yoj vakyank`.
**Takes** a string `s` (a `"..."` literal, or what `vartani_grahan()` returns) and a one-cell `mala` `ok`.
**Returns** the number. **On `hello`: returns 0 and sets `ok[0]` to 0.**

**2. Refuse, 0, or a flag? A flag - and 0.** It does not stop the program: a running program that stops because
a person typed a word is worse than one that asks again. It sets `ok[0]` to 1 or 0. **But the value it returns
when the text is not a number is 0, so a program that ignores `ok[0]` gets a silent 0.** That is your question,
and the answer is: **the function is honest; a caller can still throw the honesty away.**

**And I did.** The three lines I put in the reference and both books in R190:

```
vitti s = vartani_grahan()
vitti n = vartani_tak_ank(s, ok)
likha(n * 2)
```

**Run on `hello`: prints `0`.** (`evidence-r191/three.sm`.) **The example that taught the function was itself the
en-dash class of defect.** `examples/364` and the gate tested `ok[0]`; the taught lines did not, and nothing ran
them on a word.

**3. The lines, as they now stand - reference §4d and both books, in the section that teaches input:**

```
yoj vakyank

mukhya() {
    mala ok[1]
    vitti s = vartani_grahan()            # read a line
    vitti n = vartani_tak_ank(s, ok)      # convert it
    yadi (ok[0]) { likha(n * 2) }         # it was a number: use it
    anya { likha("sankhya na: ", s) }     # it was not: say so
}
```

| typed | prints |
|---|---|
| `42` | 84 |
| `-7` | -14 |
| `hello` | `sankhya na: hello` |
| `12 34` | `sankhya na: 12 34` |
| (Enter alone) | `sankhya na: ` |

**Read, convert, print is five lines, not three, because the fourth and fifth are the point.** Each place now
says in words: always test `ok[0]`. **The Sanskrit sentence is mine and unread by anyone who would catch an
error in it.**

**4. The example:** `examples/364_r190_vartani_tak_ank.sm` (from R190) - asks `sankhya? `, doubles a number,
reports a word. It always tested `ok[0]`.

**5. The test with a golden:** the example is in the suite with its golden (input `21`). **And new this round:
the gate extracts the program from the reference's own text and runs it on `42` and on `hello`** - so the taught
lines cannot go back to printing 0 without a gate failing. Gate `R190 chakra and converter`: **20 checks.**

## WS3 - the hole the warning leaves

**1. The word: `avaroha`** (अवरोह, "descent").

```
chakra i = n avaroha 1 { ... }        n, n-1, ... 1; no passes when n is below 1
```

- **A complete Sanskrit word**, and the one the books already use: the section is titled अवरोही पुनरावृत्तिः, and
  v326's warning ends "avarohaya 'yavat' likhatu".
- **Free:** not in the compiler, the library, the packs, the examples or the reference. (`avarohi` is taken - a
  function in `examples/246_r23_comparator_sort.sm` - which is why it is not the proposal.)
- **It need not be a 34th keyword.** `arabhya` and `paryantam` are *contextual* words: they mean something only
  inside a `chakra` header and reserve nothing elsewhere. `avaroha` can be the same, so no program's variable
  named `avaroha` breaks. (The reference counts 25 core keywords and 34 built-ins; I did not find the "33".)
- **What it buys: `tak` can then mean "up", and a start past the end is always an empty range.** The silence in
  `chakra i = 5 tak e` ends, because the student who wants a countdown has a way to say so.

**A name, as you asked, not a design.** Two things a design must decide are in `docs/WHATS-LEFT.md` with it:
whether `5 tak 1` in written numbers keeps counting down (18 loops in 12 files do), and the word in the frozen
packs.

**2. Does the warning fire when `n` is a variable? Yes - that is the only case it fires in.**

| | |
|---|---|
| `vitti n = 5` · `chakra i = n tak 1` | **warned** |
| `vitti n = 5` · `chakra i = n - 1 tak 0` | **warned** |
| `vitti n = grahan()` · `chakra i = n tak 1` | **warned** |
| `chakra i = 5 tak 1` (both written) | not warned - it counts down |
| `chakra i = 5 tak n`, `1 tak n`, `n tak n` | not warned |

The rule is "the start is **not** a number and the end **is**". A written start is never warned about.

**3. Is it in the message list, and in the codes?** **It is not a new mechanism: it is the second user of the
compiler's one warning channel**, `Sutram suchana:`, made in R111 for the old-name warning. Same routine, same
stream (stderr), same rule that it is silent in a `--lang` run. **It has no `E_` code and should not have one:**
the codes are for refusals and stops, and this refuses nothing - the program compiles to the same bytes.
**It was documented only where it is explained (§6a); the reference's line on notices named one notice. It now
names both** (the line beginning "A notice that stops nothing begins `Sutram suchana:`").

**The open design question is in `docs/WHATS-LEFT.md`**, in "Decisions waiting for the owner", as a question
with a proposed answer, in place of the row that described a hole.

## WS4 - the guard

**Against the v326 tip: 0 DIFFER** - 592 identical, 196 refused. This round changed documents and one test.
**Against v325: 10 DIFFER, exactly the programs that bring in `vakyank`** - compared with R190's list, line for
line, no difference. As you said it should be.

## Not done, and why

- **The four frozen books are not corrected** - frozen. They are the one place the false sentence still is.
- **`avaroha` is a name. Nothing is designed or built.**
- **Windows: not run.** No Wine run this round: no executable changed.
- **The Windows checklist is re-pinned** (`Claude-to-Sarvam/SUTRAM-WINDOWS-ACCEPTANCE.md`): commit `ad24e23e...`,
  installer `2a940c75...`. **The compiler in it is the same file as R190's (`F22FEA3F...`), so every expected
  output stands.** Every pinned file was downloaded from GitHub again and its hash matches
  (`evidence-r191/checklist-downloads-and-hashes.txt`). Its PowerShell blocks are still NOT RUN.
- **The guard was run for Linux executables only this round** - the compiler is byte-identical to R190's, whose
  guard covered both formats.
