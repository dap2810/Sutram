# What is left - the live list

> **Live from R188 (11 November 2026), at compiler v326 on the staged chain; main is v315.** This is the page the
> briefs name. The copy at `docs/rounds/WHATS-LEFT.md` is history (last true at v258). **When this page and another
> disagree, check the code, then fix whichever is wrong.** Tiers are the audit's: **1** a silent wrong answer, or
> guidance that leads to one · **2** a wrong or unhelpful message · **3** invisible (a stale sentence, dead code, a
> missing test).

## 1. The one thing before a release

**One Windows run, then the merge.** v316 to v326 are one chain of branches; nothing above v315 can merge until
the owner runs `Claude-to-Sarvam/SUTRAM-WINDOWS-ACCEPTANCE.md` on a real Windows machine. Everything else on this
page can be done before or after; this cannot be done by anyone else. *(R167, R181, R187.)*

## 2. The nine-item plan, as it stands

| # | item | state | where |
|---|---|---|---|
| 1 | the file example and two `grahan` bugs | **done, staged** (v324) | `Claude-to-Sarvam/R186-00-*` |
| 2 | one Windows run, then merge | **OPEN - the owner's** | section 1 |
| 3 | the reference audit | **done**: 47 finding groups; the Tier 1 rows fixed or stated in v325 | `ChatGPT-to-Sarvam/ROUND-233-AUDIT.md`, `Claude-to-Sarvam/R189-00-*` |
| 4 | does every book program work | **done**: 46 complete-program checks pass | ChatGPT R233 |
| 5 | a block returning memory to the system | **closed - not built**: 0 of 347 programs would gain | `Muse-to-Sarvam/ROUND-169-*`; cost measured in `Claude-to-Sarvam/R179-00-*` |
| 6 | `kosh temp[n]` with a computed size | **confirmed** - already made once | `Muse-to-Sarvam/ROUND-169-*` |
| 7 | generics | **for 1.1** - designed for a single-pass compiler | `ChatGPT-to-Sarvam/ROUND-232-*`, `Muse-to-Sarvam/ROUND-170-*` |
| 8 | threads | **not in 1.0**, with the reasons | `ChatGPT-to-Sarvam/ROUND-231-REFERENCE-BOOK-AUDIT.md` |
| 9 | exceptions | **not in 1.0**: `phal` / `siddhi` / `dosh` / `prasar` is the error model | the same |

**So: all closed but two - the Windows run (2), which is the owner's, and generics (7), which is 1.1.**

## 3. Decisions waiting for the owner

| | tier | what | why it waits |
|---|---|---|---|
| **`grahan` and Python's `input()`** | - | the owner asked that one function read text as well as numbers | **answered in v326 without a breaking change:** `vartani_grahan()` reads the text and `vartani_tak_ank(s, ok)` converts it and says whether it was a number (reference §4d). `grahan` returning text was simulated: 6 of 7 programs break (`R189-00`). **Open only if the owner wants `grahan` itself changed** |
| **A word for counting down - an open design question (R191, R192)** | 1 | `chakra i = 5 tak e` with `e = 3`, and `chakra i = a tak b`, run no times in silence; v326 warns only for `chakra i = n tak 1` | **Proposed: `avaroha`** (अवरोह, "descent") - `chakra i = n avaroha 1`. **Everything a decision needs - what it would mean, what it costs, why it is not built, and how a student counts down today - is set out under this table, in "Counting down".** Not designed further, not built: a language addition is the owner's (`R190-00`, `R191-00`, `R192-00`) |
| **`grahan` accepts what is not a number** | 1 | `5abc` is 5, `12 34` is 1234, `abc` is 0, and a number past the largest `vitti` wraps | each is a decision about what a running program should do with bad input; all four are stated in reference §4d |
| **`nivesha_anta()` is set by `grahan` too** | - | from v324, so a typed `-1` can be told from the end | if it should belong to `vartani_grahan` alone, the books' end-of-input test must change instead (`R186-00`) |
| **v324's refusals and v322's** | - | five refusals added by AUDIT-01 fixes, and the unknown-character refusal (v321) | each refuses programs that compiled before |

### Counting down: `avaroha`, as a question with everything a decision needs (R192)

**How a student counts down today.** A `chakra` counts down only when both ends are written as numbers
(`chakra i = 5 tak 1`). With a variable at either end, use `yavat`. **Three lines make the loop** - copy them and
put the body between the second and the third:

```
vitti i = n                 # 1. start at the top
yavat (i >= 1) {            # 2. go on while i has not passed the bottom
    likha(i)                #    ... the body of your loop ...
    i = i - 1               # 3. step down - the last line of the body
}
```

Run with `n = 5` it prints 5 4 3 2 1; with `n = 0` it runs no times, which is right. **One thing to watch:** an
`agrim` (continue) written above line 3 skips the step and the loop never ends - step down before any `agrim`.
Both books teach this form in "Descending Loops", and the compiler's notice for `chakra i = n tak 1` names `yavat`.

**1. What `avaroha` would mean.** Three shapes are possible:

| shape | example | |
|---|---|---|
| **a word in the place of `tak`** | `chakra i = n avaroha 1 { ... }` | **proposed.** `i` is n, n-1, ... 1, both ends included, as with `tak`; **no passes when the start is below the end** |
| a modifier on the loop | `chakra avaroha i = n tak 1 { ... }` | `tak` then still reads "to" in both directions |
| a loop of its own | `avaroha i = n tak 1 { ... }` | a new statement: a new keyword in fact, and a second loop to teach |

The first is proposed because the direction is then said at the one place it is decided, and because it is the shape
`arabhya ... paryantam` already has: a word that means something only inside a `chakra` header.

**2. What it would cost.**

- **Keywords: none, if it is contextual.** The reference counts 25 core keywords and 34 built-ins. `arabhya` and
  `paryantam` are neither: they are read only inside a `chakra` header and reserve nothing. `avaroha` the same way
  breaks no program that has a variable of that name (there is none in the tree; `avarohi` is a function in
  `examples/246`). **As a reserved word it would be the 26th**, and any program using the name would stop compiling.
- **One parser branch,** where the header reads `tak`: on `avaroha`, mark the loop as counting down whatever the
  ends are. The compiler already makes a counting-down loop - it is what `5 tak 1` compiles to. **Whether that code
  is right when the end is a variable is NOT TESTED: today it is only ever reached with two written numbers.**
- **Around it:** a version step; the reference's §6a; "Descending Loops" in both books; an example with a golden; a
  gate; the editor's word lists. **The ten frozen packs have no word for it** - a program written in a pack would
  have to use the Sanskrit word until a pack is resumed.
- **What happens to `chakra i = 5 tak 3`.** Two answers, and this is the real decision:

  | | `chakra i = 5 tak 3` | cost |
  |---|---|---|
  | **keep it** | counts 5 4 3, as today | nothing breaks; no program's bytes change. `tak` keeps two meanings when both ends are written numbers, and the rule in §6a stays |
  | **make `tak` mean "up" only** | **must be refused when compiled** ("start is past the end: write `avaroha`") - it cannot be left to run no times, or 18 loops go silent | **18 loops in 12 files** of the tree are rewritten, and every program outside the tree that counts down this way stops compiling until it is |

  With the second, the rule becomes one sentence - `tak` up, `avaroha` down, a start past the end is an empty range -
  and `chakra i = 5 tak e` stops being a trap, because the student who meant a countdown had a word for it. With the
  first, that trap is only made avoidable, not removed.

**3. Why it was not done now.** At run time a countdown and an empty range cannot be told apart when an end is a
variable (`chakra i = 1 tak n` with `n = 0` must run no times), so the compiler cannot guess the direction without
breaking loops that are right - only a word can say it, and a new word in the language is the owner's to decide,
not a repair (`R190-00`).

## 4. Open defects, worst first

| | tier | what | state |
|---|---|---|---|
| a `chakra` that counts up to the largest `vitti` never ends | 1 | the counter wraps and is never past the end | **stated** in reference §6a (v325); not changed |
| `purna_prasaran` gives -1 though the variance fits | 1 | `[0, 0, 6000000000]`: one squared deviation does not fit | **stated** in the reference (v325); not changed |
| `ekanka_gan` of a negative number is 0 | 1 | not the 64-bit count | **stated** (v325); not changed |
| eight messages that say only `vyakaran dosh` | 2 | an unclosed string, no `mukhya`, a `prakriya` after `mukhya`, seven parameters, seven `likha` values, `yadi a == 1`, `yadi (a = 1)`, `1e5` | open - `Claude-to-Sarvam/AUDIT-01-*` |
| a reference example calls `sankhya_padh`, which does not exist | 2 | ChatGPT R233, R22 | open |
| a failure token that is not always the first bytes; an error mode not stated | 2 | ChatGPT R233, R30, R31 | open |
| `accept_v316.cmd` fails its own step 01 on any version but v316 | 2 | it checks the text `(v316)` | stated in the checklist; script not changed (`R187-00`) |
| `grahan` reads one byte per system call | - | 5.1 s for a 24.9 MB file, and `vartani_grahan` the same | not a defect; a cost (`R184-00`) |

## 5. Tier 3 - the reference's remaining stale sentences

From `ChatGPT-to-Sarvam/ROUND-233-AUDIT.md`, still open after v325: **R06** a length claim too narrow · **R09**
`akshar_rakh` missing from the built-in table · **R10** the socket functions are Linux only, not said · **R13**
`parimana()`'s nouns · **R20** a stale reason beside a real refusal · **R21** "every `prakriya` before `mukhya`" is a
convention, not a rule · **R23** fragments with `...` counted as programs · **R25** "assignment to a parameter
faults" is obsolete · **R28** `roop_ank_upasarga`'s bases · **R32** a keyword label · **R34** an installer defect
described as current · **R35** a book-wide brace count. And the test-side rows: **C36**, **D04**, **D05**, **D06**,
**E03** (same file).

**Fixed in v325 and off this list:** R01, R02, R03, R04, R05, R07, R08, R11, R14, R15, R16, R17, R18, R24, R27,
R29, R33 (stated), D01, D02, D03, and R12, R19 (R19 made precise, not removed: for a value the compiler does not
know is a string, an empty string *is* true - measured), R26. **E02** (the stale installer payload) closes when
the installer is rebuilt with v325 - done in R189.

## 6. Not in 1.0, on purpose

Threads, exceptions, a garbage collector, generics (1.1), an optimiser (`Claude-to-Sarvam/R185-00-*`: Sutram runs
like C without optimisation; 4 to 17 times slower than optimised C on a hot loop), Windows networking (the socket
functions are Linux only), a line reader that takes a file name (read the file whole with `patra_path_sarv`, or
give it as input).
