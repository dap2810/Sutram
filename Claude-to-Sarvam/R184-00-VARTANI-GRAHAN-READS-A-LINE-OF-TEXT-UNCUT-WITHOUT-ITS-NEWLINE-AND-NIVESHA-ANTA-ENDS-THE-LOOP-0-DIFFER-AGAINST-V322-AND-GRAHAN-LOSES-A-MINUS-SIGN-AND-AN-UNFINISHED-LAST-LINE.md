# R184-00 — `vartani_grahan()` reads one line of text: **whole, without its newline, with no length limit.** An empty line and the end of the input both give `""`, and **`nivesha_anta()` tells them apart, so a loop that reads to the end stops.** Built as v323 on top of v322; **the guard against v322 is 0 DIFFER.** Against v321, which the brief names, it is 84 - exactly AUDIT-01's 84, because this branch stands on v322. **And reading `grahan` to answer WS1 found three things it does that are written nowhere: it drops a minus sign, it joins `12 34` into 1234, and it loses a last number that has no newline.** Reported, not fixed.

## Release line

```
main  (the commit carrying this file; SHA in my chat report)   Sutram 1.0 (v315) - sampurna sutra, unchanged
staged r184-read-a-line f05ddd7e   Sutram 1.0 (v323) - sampurna sutra      (on audit-01-fixes 602b1f10 = v322)
     crash corpus: 227 cases + manifest, 0 failed
     suite: NO-EXPECTATION=4 PASS=329 (333 run; two new examples, both with goldens)
     gates: 89 PASS / 0 FAIL / 1 NOT-RUN  (Linux, Xvfb; NOT-RUN = Windows execution; evidence-r184/gates-v323.txt)
     installer (payload v323): 709d560bdd74909ceedb95866f92997ceef7e374ab5f232fde81ceb80898ee97
     the guard, v323 against v322: 785 programs - 587 byte-identical, 196 refused identically, 0 DIFFER, 2 new
            (Linux executables, and the same line for Windows executables)
     the guard, v323 against v321: 503 identical, 196 refused, 84 DIFFER, 2 new - the 84 are AUDIT-01's list, to the line
staged v322 audit-01-fixes 602b1f10 · v321 c0fdebe8 · v320 fe90a9b1 · v319 4c1159be · v318 · v317 · v316 - unchanged
```

Sanskrit only; no pack touched; `backups/` untouched. `R159 no personal paths`: 0.

**Why v322 and not v321 underneath:** v322 was pushed before this round was read, and a builtin added to v321
would have had to be added again to v322. **If you want it on v321 without AUDIT-01, say so** - the change is
one block of the compiler and moves cleanly.

## WS1 - what `grahan` does (read in the source, then run: `evidence-r184/grahan-v322.txt`)

1. **A character loop, not a line read.** `grahan` is a block of machine code placed in the program where it is
   called. It asks the system for **one byte at a time** and builds the number as the bytes arrive: a digit is
   added, anything else is passed over. Counted: 8 `read` calls for the 8 bytes of `12345\n7\n`.
   **So the text read is a different path, not a wrapper** - there is no buffered line to hand back.
2. **It stops at the newline.** `hello world` then `7`: the first `grahan` gives 0 and takes the whole line; the
   second gives 7. **The second word is not left for the next read - and it is not kept either.**
3. **Enter alone gives 0.** It does not block and does not fail. **0 is also what `hello` gives and what `0`
   gives - the three cannot be told apart.**

**Three things it does that I did not find written down** (searched the tree by phrase, not round by round):

| input | `grahan()` gives | |
|---|---|---|
| `-5` | **5** | the minus sign is passed over like any non-digit |
| `12 34` | **1234** | the space is passed over; the digits join |
| `42` with no newline after it, then the end of the input | **-1** | **the number is lost**: the end is reported before the 42 |

**Not fixed - the round says nothing else.** The third is the one a student meets: a file whose last line has
no newline loses its last number. The reference's new table (below) states the first two; **it does not state
the third** - I found it after the documents were built and gated, and did not reopen them.

## WS2 - the name: `vartani_grahan` - वर्तनी_ग्रहण

**"String-taking". `vartani` is already this language's own word for a string** - six error codes carry it
(`E_VARTANI_GANIT`, `_CAT`, `_SATYA`, `_TUL`, `_STHIRA`, `_SMRITI`) and so do the library's string functions
(`vartani_aayam`, `vartani_sandhi`). **The function returns a `vartani`, and `grahan` is the word the student
already knows for reading.** Both halves are complete words.

| candidate | checked against the compiler's names and messages, `lib/`, the reference, `examples/` | |
|---|---|---|
| `akshara_grahan` | unused as a name - but `E_AGYAT_AKSHAR` and the library's `akshar_*` mean one character | **says "one letter"; it reads a line** |
| `pankti_grahan` | `pankti` is a keyword (a list), and in every error message it means "line" | **a collision, as you said** |
| `lekha_grahan` | unused anywhere | free, but `lekha` is a new word for something that already has one |
| `shabda_grahan` | `shabda` is a builtin (print a string) | **a collision; and it says "word" where a line is read** |
| `vakya_grahan` | **not unused:** `E_VAKYA_SEEMA`, and in the messages `vakya` means *statement* | **"statement-taking" in this compiler's own vocabulary** |
| **`vartani_grahan`** | **no function, keyword, error code, example or library name** | **chosen** |

**And a second name, which the brief did not ask for and WS3's fourth question needs: `nivesha_anta` -
निवेश_अन्त, "end of input".** `nivesha` is already the word for input (`E_NIRGAM_NIVESH`, the books' chapter
title); `anta` is a complete word. Unused anywhere. **Both names are accepted in Devanagari as written above.**

## WS3 - the behaviour (`evidence-r184/behaviour.txt`; gate `R184 read a line`)

1. **The newline is not in the result.** Nor is the CR of a CR LF line.
2. **The buffer grows.** It starts at 64 bytes and doubles. Lines of 63, 64, 65, 100,000 and 5,000,000 bytes
   come back at exactly those lengths.
3. **A line longer than the buffer: nothing is cut and nothing is left behind** - there is no limit to say.
4. **The end of the input: `""`, at once, every time - and `nivesha_anta()` becomes 1 and stays 1.**

**Why a second function and not a sentinel.** An empty line must also be `""` - WS1's third question - so `""`
alone cannot mean "ended". Any text sentinel is a line a user can type. An error would stop the beginner's
program on the most ordinary event there is. So the read never fails, and one question answers "was that the
end?":

```
yavat (1) {
    vitti s = vartani_grahan()
    yadi (nivesha_anta()) { krama }
    ...
}
```

**The loop that forgets the test still cannot hang on the read** - at the end every call returns immediately.
It can spin for ever on `""` if it has no other way out; that is the student's loop, not a blocked read.

- **A last line with no newline is returned whole**, and the call after it finds the end. (`grahan` loses it.)
- **`grahan()` and `vartani_grahan()` share the input, a line each:** a number's line, then a text line, works.
- **The result is a string to the compiler:** printed as text, `==` and `+` work, it can be returned from a
  `prakriya`; arithmetic on it is refused (`E_VARTANI_GANIT`), and so is using it as a condition.
- **UTF-8 passes through byte for byte** (`आशा पटेल` in, the same out).

**What it costs, measured, and not closed:**

- **A byte per system call, as `grahan`:** 2,000,000 lines (24.9 MB) took 5.1 s. Fine for a keyboard; slow for a
  big file. A buffered read would be faster, and would have to be shared with `grahan` - not done.
- **At least 64 bytes a call, kept until the program ends** - the same memory string `+` takes. 2,000,000 lines:
  `parimana()` 128,000,064, peak 124,928 KB. **A `mandapa` does not give it back** (measured, the same figures) -
  as for `+`, so that text read inside a block can be kept after it. **You said no memory work; this is the
  figure, not a change.**

## WS4 - where a student finds it

1. **`examples/360_r184_vartani_grahan.sm`** - asks a name and greets it, three lines of body.
   **`examples/361_r184_pankti_ganana.sm`** - reads every line to the end and counts them. Both have goldens and
   run in the suite (one fed a name; the other an empty line and a last line without a newline).
2. **Reference: section 4d, "Input: a number, a line of text, and the end of input"** - one table for `grahan`,
   `vartani_grahan` and `nivesha_anta` side by side (what each reads, gives, does on Enter alone, does at the
   end), the loop, and the costs above. Two rows in the built-in table; a line in the quick tour.
3. **Both books, directly after "`grahan()` and end of input"** - which is where `grahan` is taught: a section
   "Reading text: `vartani_grahan()`" with the name program and the loop, and two rows in the quick-reference
   table. English and Sanskrit. **The Gujarati and Hindi books are frozen and untouched.**
   **The Sanskrit passage is mine and unread by anyone who would catch an error in it.**
4. **Changelog: v323.** Release notes: Muse's item 2 struck through as closed, with what is not closed.

## WS5 - the tests

**Gate `R184 read a line`** - `tests/r184/test_read_line.py`, **17 checks, 0 failed.** Each feeds exact bytes and
compares exact bytes:

| the three asked for | |
|---|---|
| a known line | `Asha Patel\n` in, `Namaste, Asha Patel!` out; and `hello world` whole |
| the empty line | `\n` in: `""`, and the program goes on |
| the end of input | nothing in: `""` at once; the read loop runs zero times; a 60 s limit would catch a hang |

and: the loop ends at the end and not at an empty line; an unfinished last line; CR LF; the five lengths; the
flag stays 1; a number line then a text line; the string kind; Devanagari text; the Devanagari names; three
refusals.

**The guard: 0 DIFFER against v322** (587 identical, 196 refused identically, the 2 new are the examples), for
Linux and for Windows executables. **Against v321: 84 DIFFER** - `evidence-r184/differ-v321-list.txt` is
identical to AUDIT-01's list. **So "adding a builtin changes no existing program" is measured, against the
version it was added to.**

**One way it could have changed a program and did not:** a program that already had its own `prakriya` or
`vitti` named `vartani_grahan` or `nivesha_anta` would now be refused. None of the 785 has one.

## Not done, and why

- **Windows: not run.** Under Wine (`evidence-r184/wine.txt`, the final build): five programs - the name, the
  loop on CR LF input with an unfinished last line and on no input, a number line then a text line, the
  `prakriya` that returns the text, the Devanagari names, and lines of 100,000 and 5,000,000 bytes - print what
  Linux prints. **Wine is not Windows; a console's Ctrl-Z end of input has not been tried anywhere.**
- **`grahan` is unchanged** - the three behaviours above are reported.
- **No buffered read, no release of a line's memory** - both named above with their figures.
- **On Windows, running out of memory in `vartani_grahan` is not a message** - as for string `+` there
  (the Linux check is `E_VARTANI_SMRITI`). Not run on either system: I did not exhaust memory to see it.
- **Item 3 (the file example, the two reference rows) is not started** - WS6.
- **ROUND-183 (the baseline) is next and not started.**
