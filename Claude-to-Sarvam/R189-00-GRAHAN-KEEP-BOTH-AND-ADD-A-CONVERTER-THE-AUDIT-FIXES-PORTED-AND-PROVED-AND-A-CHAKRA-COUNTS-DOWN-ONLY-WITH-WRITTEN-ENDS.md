# R189-00 — The `grahan` question: **keep both functions and add a text-to-number converter. Making `grahan` return text was simulated on the seven programs that use it: four are refused, one never ends, one prints something else.** The audit's fixes are ported onto the chain and proved again as v325. Two library defects are fixed, and every Tier 1 reference row is fixed or stated against a run. **One thing the audit did not find: a `chakra` counts down only when both its ends are written as numbers.** `chakra i = 5 tak e` with `e = 3` runs no times, silently. And two of the audit's own rows are wrong.

## Release line

```
main  (the commit carrying this file; SHA in my chat report)   Sutram 1.0 (v315) - sampurna sutra, unchanged
staged r189-audit-fixes 22466bda   Sutram 1.0 (v325) - sampurna sutra      (on r186-grahan-and-files e1f29f14 = v324)
     crash corpus: 227 cases + manifest, 0 failed
     suite: NO-EXPECTATION=4 PASS=331 (335 run) · contracts (R116): 139 checks, 0 failed
     gates: 92 PASS / 0 FAIL / 1 NOT-RUN  (Linux, Xvfb; NOT-RUN = Windows execution; evidence-r189/gates-v325.txt)
     installer (payload v325): 9af56fad6ed498be43c5597a549821d77df13e173f6ce7ef74a33c1288786596
     the guard, v325 against v324: 787 programs - 527 byte-identical, 196 refused identically, 64 DIFFER, 0 new
            (Linux and Windows executables, the same line). All 64 bring in `ganit` or `brihat`; all 64 print the
            same and exit the same on both compilers (evidence-r189/differ-run.txt)
     the compiler's code is v324's: before the version string was changed, both builds were byte-identical to v324
ported: chatgpt/r233-audit-fixes 55008b4e (it stands on v315; here it is on v324)
```

Sanskrit only; no pack touched; `backups/` untouched. `R159 no personal paths`: 0.

## WS1 - `grahan` and Python's `input()`. Nothing is built.

### Your four questions

1. **`grahan()` returns a `vitti` - a 64-bit whole number.** **`vartani_grahan()` returns a `vartani`: a string,
   the same kind a `"..."` literal is.** Not a `pankti`, not a `kosh` of bytes. The compiler knows it is a string:
   it prints as text, `==` and `+` work on it, arithmetic on it is refused.
2. **There is no text-to-number function. None.** No builtin, and nothing in the 310 library functions, takes a
   string and returns its number. `varna_tak_ank(buf, n, ok)` in `vakyank` is the nearest, and it parses a `mala`
   of character codes - one code per eight-byte cell - not a string. **So the Python model does not exist yet:
   `input()` does (`vartani_grahan`), `int()` does not.**
3. **If `grahan` returned text - simulated, not guessed** (`evidence-r189/grahan-option-a.txt`). 14 `.sm` files
   in the tree call `grahan(` (6 examples, 4 tests, 4 in partners' folders); **7 of them are programs the guard
   compiles** - the same seven R186's fix changed. In each of the 7, `grahan()` was replaced by `vartani_grahan()`
   and compiled:

   | | result |
   |---|---|
   | `23_grahan_input`, `26_calculator`, `report_blocks`, `report_plain` | **refused when compiled** (`E_VARTANI_GANIT`, `E_VARTANI_TUL`) |
   | `24_guess_game` | **compiles, and never ends** - `guess == -1` is never true for a text |
   | `59_windows_grahan_runtime` | **compiles, and prints `42` where it printed `42` and a newline** |
   | `46_language_reference` | unchanged - it reads the value and does not use it |

   **Six of seven break, and two of the six break without a message.** And every book passage that teaches
   `vitti n = grahan()` becomes wrong. **That is a version bump, not a fix.**
4. **"Keep both, and make `grahan` return something sensible for `hello`": worse than Python's model, and I
   would not do it alone.** A function that returns a number can only return a number. Whatever it returns for
   `hello` - 0 today - is also a number someone can type. The only honest signal is a second channel, and that
   is what a converter with a success flag gives.

### The three options

| | what changes | what it costs | what the student writes |
|---|---|---|---|
| **A. `grahan` returns text** (Python exactly) | `grahan`'s return kind | **6 of the 7 programs break, 2 silently**; both books; every program outside this tree. Needs the converter as well | `vitti n = ank(grahan())` |
| **B. Keep both; add the converter** | one new function, string to number, that says whether it was a number | **nothing breaks: 0 DIFFER.** One function, one reference row, one book paragraph | text: `vartani_grahan()` · number, checked: `ank(vartani_grahan())` · number, quick: `grahan()` |
| **C. `grahan` "accepts text"** | `grahan` reports what it could not parse through a flag | a second flag function beside `nivesha_anta()`; `grahan` still cannot hand the text back | `grahan()` then ask the flag |

### I pick B

**B is Python's model: it already has `input()` under the name `vartani_grahan`, and it lacks only `int()`.**
The owner's requirement - "it should also accept text, like `input()`" - is met by the function that exists
since v323. What is missing is the way from text to a number, and adding that changes no program.

**B also closes the open defect list on `grahan`** (`5abc` is 5, `12 34` is 1234, `abc` is 0, overflow wraps -
R186-00). A converter can do what `grahan` cannot: read the whole string, and say "this was not a number" without
inventing one. `grahan` stays as the short form for a program that trusts its input.

**What B needs decided before I build it - three things, each the owner's:**

- **The name.** A complete Sanskrit word or compound, checked against the names in use, as in R184.
- **How it says "not a number".** A library `prakriya` returns one value. Either a second function asks
  ("was the last conversion a number?" - the `nivesha_anta()` pattern), or it takes a one-cell `mala` for the
  flag (the pattern `varna_tak_ank` and `ganita_janchit_*` already use).
- **What counts as a number:** a sign, spaces around it, nothing else? Overflow refused?

**If the owner wants A all the same** - one function called `grahan` that returns text - it can be done as a
version step with the 7 programs and both books rewritten. I would still add the converter first.

## WS2 - the four source defects

Every program is in `evidence-r189/programs/`; `before-after.txt` has each one on v315, v324 and v325.

| | wrong (v315 and v324) | right (v325) | what was done |
|---|---|---|---|
| **1. `brihat_ank_tak_laghu`, a digit of -1** | `brihat_neg.sm` prints **-1**, exit 0 | **stops, exit 1, `E_MULYA_AYOGYA`** | `d <= 9` became `d >= 0 && d <= 9` (ChatGPT's fix, ported) |
| **2. `brihat_ank_se`'s failure** | - | - | **the document was wrong, not the code.** `ankse.sm`: a bad base returns 0 and leaves `x` as `777`; a bad digit returns 0 and clears it to `000` - exactly what the function's own comment says. The reference said "a bad digit or base ... the digits cleared". **Row split in two.** No code change |
| **3. `LCM(MIN, 0)`** | `lcm.sm` **stops the program** (`E_PHALA_SEEMA`, from the gcd it calls) at (0, MIN) | prints **0, 0, -1** for (0, MIN), (MIN, 0), (MIN, MIN) and ends | an lcm with 0 is 0, mathematically; (MIN, MIN) is 2^63, which does not fit, so -1 - the function's own rule for an lcm that does not fit. Two guards before the gcd call |
| **4. signed and final-line input** | on main: `-5` reads as 5; `42` with no newline is lost | **both fixed in v324** (R186) and still so in v325 | gate `R186 grahan and files`, 24 checks, runs in v325's gates |

**What should happen for `LCM(MIN, 0)`** - you asked. 0. The gcd of (MIN, 0) is 2^63 and cannot be returned, so
the gcd is right to stop; the lcm never needed it.

**The guard: 64 DIFFER, and it is the stated list.** A library function is compiled into every program that
brings its module in, so changing `ganit` and `brihat` changes those programs' bytes. **All 64 bring in one of
the two** (directly or through `aadhar`), **and all 64 print the same and exit the same on v324 and v325.**

**The verification fixes of R233 are ported too:** the stricter guard, `doc counts`, `R124 lazy commit`. Their
four tests were in the candidate and in no gate; **they are now gate `R233 verification`, 21 checks.**

## WS3 - the twelve Tier 1 documentation rows, each against the code

| | what the reference said | what the code does (run on v325) | now |
|---|---|---|---|
| **R01** | `likh8` / `pad8`: 8-bit | eight bytes: `likh8(p, 65)` over -1 leaves 65, not -191 | corrected (R186 + R233's wording) |
| **R02** | `likh8c` / `pad8c`: print / read a character | a store and a load that happen only when the address is below `bound`; no lower bound, no check of the eight bytes' end | corrected |
| **R04** | `grahan` reads a number | reads the line's digits; other bytes passed over; wraps past the largest `vitti` | the row and §4d say all of it |
| **R05** | `aksharank` ignores its index | uses it: `aksharank("ABC", 2)` is 67; default 0 | corrected |
| **R07** | "character", "varna", no unit | **bytes.** `akshar("आ", 0..2)` is 224, 164, 134; `anka_akshar(300)` is `,`; `akshar_guru(224)` is 224 | six rows say bytes and ASCII |
| **R08** | `vartani_tul`: "compare" | 0 equal, 1 different, no order | corrected |
| **R11** | `nirmmita` gives zeroed bytes | **true on v320 and after; false on main** | the row says since when, and points to §19 |
| **R17** | `purna_prasaran`: -1 when the answer does not fit | also -1 when one squared deviation does not fit: `[0, 0, 6000000000]` | stated, with the example |
| **R24** | `madhya`: the middle of three | the example returned `b` - its sort was a comment | **the example now sorts**; all six orders give 2 (in the gate) |
| **R27** | `ekanka_gan`: the 1-digits of `n` | every negative `n` gives 0 | stated |
| **R29** | `ganita_paripurna_*` saturate | an overflow saturates; `/ 0`, `% 0` and `kramgun(-1)` give 0 | stated |
| **R33** | inclusive `chakra`, no caveat | a loop up to the largest `vitti` never ends | stated in §6a |

**R11, the one you said matters most.** **On v324 and v325 the promise is kept.** A new ordinary `nirmmita` is
fresh memory, or memory a block cleared as it ended (v320); a large `kosh`'s old region goes back to the system
and comes back zeroed. **On main it is not kept**, and R172 measured it: 15,782,272 of 75,000,000 words stale.
**So the sentence is false exactly as long as v320 is not merged.**

**And two more of mine, which R233 corrects:** in R186 I wrote that `dvaram` and `paadh` return **-1** on
failure. **They return the system's negative error code: -2 for a missing file, -9 for a descriptor that is not
open** (measured). ChatGPT's row was right; mine is corrected.

### Where the audit is wrong

- **R19** says the sentence "an empty string is still true in `yadi (s)`" should be removed, because a string
  as a condition is refused. **It is true where it stands.** The sentence is about values the compiler does *not*
  know are strings. `vitti g = ""` at module level, then `yadi (g)`: **compiles, and the branch runs** (`r19b.sm`);
  the same for a `mala` element (`r19c.sm`). The refusal covers only known strings. **Made precise, not removed.**
- **R18** says the braces section is obsolete - **right, and worse than "obsolete".** The section said a
  three-line `prakriya` without braces "does NOT compile" and called that verified. **It compiles and prints 12.**
  The failure it quoted came from a file with no `mukhya`; a braced `prakriya` alone fails the same way.
  **Rewritten, with an example that is in the gate.**

### Found this round, in no audit: which way a `chakra` counts

```
chakra j = 5 tak 1 { ... }                  5 4 3 2 1
vitti e = 3
chakra i = 5 tak e { ... }                  runs no times. No message.        (v315, v324, v325)
```

**The direction is decided when the program is compiled, and only when both ends are numbers** (`0 - 5` counts:
it is folded). The compiler's own comment says so. With a variable or a call at either end the loop counts up.
**The reference showed `chakra j = 5 tak 1  # for (descending)` and never said the rest**, so a student who
writes `chakra i = n tak 1` gets a loop that does nothing. **Tier 1 by the audit's own definition.**

**I did not change it, and I would not without the owner.** Deciding the direction when the loop runs breaks the
most common loop there is: `chakra i = 0 tak n - 1` with `n = 0` runs no times today and would run twice (0, then
-1). **Stated in §6a, with `yavat` as the way to count down from a variable; pinned in the gate.** Not found in
any earlier record (searched by phrase).

## WS4 - the gate

**`R158` passes on main, and on the v324 tip. For the changelog that is correct; for `WHATS-LEFT` it is a gap.**
Both answers, the new check and its proof are in `R188-00`, where you asked for them in full.

**Gate `R189 audit fixes`: 13 checks, 0 failed; 2 of them fail on v324** (the two library fixes).

## Not done, and why

- **The `grahan` converter is not built** - you said not to until I had said which; three choices are the owner's.
- **Windows: not run.** Under Wine: a block's memory is given back in a Windows executable, and a computed
  negative size in a block stops there too (`evidence-r189/wine.txt`).
- **The `chakra` direction, the `chakra` to the largest `vitti`, `purna_prasaran`, `ekanka_gan`: stated, not
  changed.** Each changes what existing programs do.
- **The audit's Tier 2 and the rest of Tier 3 are open** - listed by ID in `docs/WHATS-LEFT.md`.
- **The first gate run failed: 91 / 1 / 1.** `R140 package`: `docs/sutram-stdlib.html` is generated from the
  library's comments, and I built the installer before regenerating it. Regenerated, installer rebuilt, second
  run 92 / 0 / 1. Both runs are in `evidence-r189/`.

## The Windows checklist is reissued for v325

`Claude-to-Sarvam/SUTRAM-WINDOWS-ACCEPTANCE.md` was pinned to v324. **It now pins v325:** commit `22466bda...`,
installer `9af56fad...`, compiler `F5EFD1F8...`, `lib\ganit.smlib` `ADEC4472...`. **Every pinned file was
downloaded from GitHub again and its hash matches** (`evidence-r189/checklist-v325/`). The expected outputs were
taken again with v325's Windows compiler under Wine: **all are v324's, except the version line.** The v316
script: 17 passed, 1 failed (step 01, as explained there). **Its PowerShell blocks are still NOT RUN.**
