> **The 20 newest entries.** Older ones, from "v431" back to the first, are in [rounds/CHANGELOG-ARCHIVE.md](rounds/CHANGELOG-ARCHIVE.md) (split in R88).

## v290 (Claude, R108 + its correction) - the outlives rule: a block's kosh never goes to a prakriya that keeps it; a mala operand is refused; the arena is NOT on main

- **A `kosh` made in a `mandapa` may be passed only to a parameter that does not keep it** (does not return it,
  store it, or pass it to one that does - a greatest fixpoint over every `prakriya`; function values and foreign
  functions count as keeping). Otherwise `E_KOSH_MANDAPA` at compile time. With v289's escape error, no
  reference to a block's `kosh` can outlive the block. Example 316 is now that refusal; the R82 gate's five
  runtime cases are compile-time refusals (12/0).
- **`mala == mala`, `mala + 1`** (ChatGPT R175's reference-type class): `E_MALA_GANIT` (319). `kosh` operands
  were already `E_KOSH_GANIT` (v288).
- **`parimana()`** is the arena and the regions together; golden 318 shows it move.
- **Not on main:** the block-arena `kosh` (a slot of the block's arena, growth by a new slot). It was built before
  Sarvam's ROUND-108-CORRECTION and is on the review branch `claude/r108-arena-review`, as the correction asks.

## v289 (Claude, R107) - a kosh cannot leave its block (compile time); `parimana()` reports the bytes in use

- **The escape error:** a `kosh` declared inside a `mandapa` carries the block's depth as its scratch-escape taint,
  so storing it in a variable declared outside the block, writing it into memory, or returning it is
  `E_KOSH_MANDAPA` at compile time (the R73 rules, a `kosh`-specific message). Example 287 is now that refusal; the
  runtime form (R82) stays for a `prakriya` that keeps the `kosh`, golden 316.
- **`parimana()` / `परिमाण()`** returns the bytes held now: the arena's persistent and scratch sides plus each
  `kosh`'s header and capacity (a hidden counter, emitted only in programs that call `parimana`). Golden 317.
  Linux ELF; 0 on Windows.
- R107-00 prices the block-arena `kosh` design (not built): a slot costs about 21 instructions and no system call
  against a region's 14 and an `mmap`; kb1 0.02 s / 0 KB against 0.48-0.99 s / 400 MB; a `kosh` grown to 1,000 in a
  block leaves 8,656 dead bytes.

## v288 (Claude, R106) - `likha` prints a string's text; a string condition and a kosh operand are refused; a dasham into a mala is converted

- **`likha` on a string value prints its text** (a variable, `s + t`, a string-returning `prakriya`), with no
  newline, as a literal: `likha("concat: ", s + "cd")` prints `concat: abcd` (it printed `139381365014528`). The
  dispatch is at compile time from R105's kinds; numbers print as before. `--debug` ends a string value's trace
  line itself. Golden 312.
- **Muse's R101 traps**, the ones outside the `likha` emitter: a string as a condition (`yadi (s)`, `&&`/`||`,
  `?:`; `""` was true) is `E_VARTANI_SATYA` (313); a bare `kosh` in any binop (`a == b` compared addresses) is
  `E_KOSH_GANIT` (314); a `dasham` stored into a whole-number `mala` is converted exactly, `E_DASHAM_VITTI` for a
  fraction (315; it stored the IEEE-754 bits). Traps 1, 2 and 7 were closed by v286/v287. Not changed: 5
  (`likha(k)` - the `likha` emitter, left out of this commit as the brief asked) and 6 (a string in a `mala` - its
  element is untyped; `shabda(a[0])` prints it).
- A `kosh` made in a `mandapa` keeps its region for the program's life (unchanged; reasons in R106-00).

## v287 (Claude, R105) - strings work: `==` `!=` `<` `>` compare text, `+` makes a new string, `likha(a, " ", b)` prints three values

- **`==` / `!=`** between two strings compare bytes to the NUL (the node becomes `vartani_tul(a, b) ==/!= 0`, so
  the compare that follows is the ordinary integer one). **`<` `<=` `>` `>=`** order by the first differing byte.
  **`+`** between two strings allocates `len(a) + len(b) + 1` on the persistent side and copies both: the result
  lives for the program; `parimita` does not count it.
- **Which values are strings** is decided once per function, before code generation, from the whole program: a
  variable all of whose assignments are strings; a parameter every caller passes a string; a `prakriya` every
  `nivartanam` of which is one. Replaces v286's last-assignment flags (ChatGPT R173's P173-01/02/03: `s = s + s`,
  the fast paths disagreeing, a call result taken for an integer). Every register fast path now leaves a
  string-touching operation to the one generic rule.
- **Refused instead of guessed:** a string beside a number, or beside a variable that is sometimes a string
  (`E_VARTANI_TUL`, `E_VARTANI_CAT`); `-` `*` `/` `%` and bit operators on a string (`E_VARTANI_GANIT`, new).
  String +/- an integer stays pointer arithmetic.
- **`likha` with three values always prints three values** (v286's `E_LIKHA_TRAYA` is gone; raw writes stay
  `dvaram_likha`).
- Goldens 306 (equal), 307 (join), 308 (likha three), 309 (order), 310 and 311 (refusals). Reference 4a, 5a.
  Not tracked: module globals, `kosh`/`mala` elements, a `prakriya` used as a value - refused beside a string.
  `likha(s)` on a string variable still prints its address (`shabda` prints the text).

## v286 (Muse's FIXALL patch, applied by Claude, R104) - five silent wrong answers become refusals; a recursion guard

- **`likha(a, " ", b)`** (three arguments, the first not a string literal) printed nothing: now **`E_LIKHA_TRAYA`**
  at compile time. The raw write is the new builtin **`dvaram_likha(fd, buf, len)`** (returns the count); 57 tree
  sites renamed (`examples/215`, `217`, `lib/patra.smlib`, 54 tests).
- **`s == "ab"` / `!=`** on strings compared addresses: now **`E_VARTANI_TUL`** (use `vartani_tul`, 0 when equal).
  Also in `yadi` / `yavat` conditions and the fast paths. Not tracked: parameters, call results, `kosh` elements,
  module globals - with a literal on either side they are still refused.
- **`s + t`** on strings added addresses: now **`E_VARTANI_CAT`** (use `vartani_cat`). A string plus an integer is
  still pointer arithmetic (`base + 6`, `letters + grade - 65`: two tree programs use it); literal + literal folds.
- **`vitti x` / `dasham d` without a value in a function** read the slot's leftover (`0 99 99`): now **`E_MULYA_VINA`**.
  `mala`, `kosh` and module-level declarations unchanged. Zero tree programs affected.
- **Recursion past the stack** was a segmentation fault, exit 139: now **`E_GAHANATA`**, exit 1, from a check in every
  `prakriya` prologue against `mukhya`'s entry `rsp` (limit 8,339,456 bytes, about 4,000 frames; `yog(3900)` runs,
  `yog(4000)` refuses; v285 ran 4,000 and crashed at 4,100). Linux only; 15 bytes in `mukhya` + 115 per `prakriya`;
  50,000,000 calls: 0.10 s before and after.
- **The guard, v285 -> v286:** every Linux program that compiles differs (the prologue bytes); each was run old and
  new - see `Claude-to-Sarvam/R104-00-*.md` for the counts by kind. PE: byte-identical. Reference 4a, 5a, 6d, 20.
- Muse's report: `Muse-to-Sarvam/FIXALL-R100-TRAPS.md`. Native-speaker review of the new Sanskrit: NOT RUN.

## v285 (Claude, R102 + R103) - `mandapa parimita N`: a block with a byte budget that refuses; regions stay for the program's life

- **`mandapa parimita N { }`** - the block's own `nirmmita` may use at most `N` bytes (each rounded to 16, as the
  arena does). The one that would pass the budget stops the program before it is given memory:
  `Sutram Error [E_PARIMITA]: pankti L - mandape parimitat adhikam nirmmitam na sambhavati (parimitih N baait)`,
  exit 1. Nested budgets all hold. `N` must be a positive whole number in the source (else `E_PARIMITA` at compile
  time, with file:line:col). `परिमित` is the same word; `parimita` stays usable as a name. A `kosh`, and what a
  called `prakriya` allocates, are not counted. Linux ELF only, as the block; on Windows it is not checked.
- **Measured:** 1,000,000 `nirmmita(64)` in one 1 MB-budgeted block refuses at the 16,385th with a peak of 1,024 KB;
  the same budget on a block entered once per pass runs to the end at 0 KB (a three-line program's reading); the
  unbudgeted block peaks at 62,464 KB. Goldens `303` (refuses), `304` (within; nested; `parimita` as a name), `305`
  (compile-time refusal).
- **Decided: a block does not return its `kosh` regions** (Reference section 19): the R82 check reads the header,
  so returning would turn `E_KOSH_MANDAPA` into a crash or a silent read, and in the tree it would return nothing
  (the three programs with a `kosh` in a block all read 0 KB).
- A program without `parimita` compiles to the same bytes as on v284 (the guard).

## v284 (Claude, R101A - the owner's Option A) - on Linux every `kosh` has a region of its own and never moves

- **Owner's decision (2 November): Option A.** On Linux ELF a `kosh` is made in its own `mmap` reservation (64 MB
  of address space, `MAP_NORESERVE` - only touched pages count) and grows in place inside it; capacity still
  doubles. It moves only past 8,388,603 elements, once, on the old path. Not under `--fail-alloc`, not in the
  guard-page build, not on Windows (PE unchanged).
- **What it fixes:** `vitti a = k` stays one name however `k` grows (example 288 now prints `a[0]=99 k[0]=99` /
  `a[0]=7 k[0]=7`); a growing `kosh` leaves no copies behind (100,000 pushes past an allocation: 1.8 MB -> 0.8 MB).
- **What it costs, measured:** one page (4 KB) at least per used `kosh` and an `mmap` per `kosh` made: a loop making
  100,000 small `kosh`s goes from 100 MB / 0.05 s to 400 MB / 0.45 s. The tree's 86 `kosh` programs: none uses
  more memory (one 78 -> 70 MB).
- **Not done:** the block giving its `kosh` regions back (it would break the exact `E_KOSH_MANDAPA` check - see the
  hand-back), and Windows regions (`VirtualAlloc` reserve/commit in the PE runtime).
- Gate `R101 memory`: 6 checks (in-place cost, 9,000,000 pushes past the region).

## v440 - CORRECTION 3, the final one: it WAS a hang, and my own `head -8` faked the count

### The truth, counted by lines rather than truncated

| form | v282 | v283 |
|---|---|---|
| `chakra i = 0 tak 2` | `0 1 2`, exit 0 | same |
| `chakra i = 0.0 tak 3` | `0 1 2 3` - **right by luck**, `0.0`'s bits are 0 | refused |
| `chakra i = 0 tak 3.0` | **5,375,137 lines before kill** | refused, `E_CHAKRA_DASHAM` |
| `chakra i = 0 tak 2.5` | **5,853,479 lines** | refused |
| `chakra i = 0 tak 2.9` | **6,987,595 lines** | refused |
| `chakra i = 0 tak 0.5` | **7,499,473 lines** | refused |

**The bound's bit pattern is read as an integer - about 4.6 x 10^18 - so the loop runs essentially forever.**

### The worst error of this session, and it is a measurement failure
**I piped output through `head -8`.** A loop printing 7.5 million lines looks exactly like an 8-iteration loop when truncated at eight.

**v437 said HANG - correct.**
**v438 said off-by-one - wrong, caused by `head`.**
**v439 said unpredictable eight iterations - wrong, same cause.**

**I corrected a correct finding twice, from my own truncation, and told three partners they were wrong on that basis.**

### Muse was right and I overrode it twice
**Muse wrote "a loop whose end number is a decimal never stops."** Accurate. **I asked for it to be changed. It should not have been.**

### The rule
**`head -N` on an unbounded stream is not a measurement.** Count the lines, cap the loop, or watch for exit. **Never truncate a stream and treat what you saw as the number of iterations.**

**This is a different class from the other nine errors. Those were describing belief instead of testing. This one was testing with an instrument that could not show the truth.**

## v439 - CORRECTION 2: the decimal loop bound count is unpredictable

### Measured on v282, all forms, correct syntax

| Form | Output | Iterations |
|---|---|---|
| `chakra i = 0 tak 2` | `0 1 2` | 3 correct |
| `chakra i = 0.0 tak 3` | `0 1 2 3` | 4 correct |
| `chakra i = 0 tak 3.0` | `0 1 2 3 4` | 5 wrong |
| `chakra i = 0 tak 2.5` | `0 1 2 3 4 5 6 7` | 8 wrong |
| `chakra i = 0 tak 2.9` | `0 1 2 3 4 5 6 7` | 8 wrong |
| `chakra i = 0 tak 0.5` | `0 1 2 3 4 5 6 7` | 8 wrong |

**The count does not track the bound. `tak 0.5` and `tak 2.9` both run eight times; `tak 3.0` runs five.**

**A decimal COUNTER with an integer bound is correct.** So the counter type is fine and the bound type is the defect.

### I have been wrong about this twice in two turns
**v437 said HANG.** My test was invalid syntax and printed nothing; I read nothing as non-termination.
**v438 said OFF-BY-ONE.** I had tested only `tak 3.0`, which happens to be one extra, and generalised from one value.

**The second error was worse than the first, because I made it while correcting the first.** **Both are the same failure: describing one observation as if it were the class.**

### What the fix is, and what the reason is
**Refusing a `dasham` loop bound is still right. But the reason is not "it runs one extra time" - it is "the iteration count is wrong and unpredictable, and it produces no error".**

**And the test matrix must include fractional bounds.** `3.0` was the one value that looked like an off-by-one.

## v283 (Claude, R96) - a `chakra` with a decimal end is refused instead of running for ever

- **Why it hung (disassembly):** the loop is whole-number code - `inc` the counter, `cmp` with the end, `jle`. A
  decimal end was compared as its IEEE-754 bits: 3.0 is `0x4008000000000000` = 4613937818241073152, so
  `chakra i = 0 tak 3.0` counted toward 4.6 x 10^18. A decimal start counted from its bits (0.5 printed
  4602678819172646912, ...); a `dasham` variable as the counter got whole-number bits (printed 0.000000).
- **`E_CHAKRA_DASHAM`** (`r96_check_for_float`): a decimal start or end (written or a `dasham` variable), or a
  `dasham` counter, is refused when compiled, with a caret under a written decimal. Decimals step with `yavat`.
- **The installer gate also checks the tree's binaries** (R95 WS1): `sutram_compiler`, `sutram.exe`,
  `win/sutram.exe` must carry the source's version.
- **Goldens:** 300, 301 (refusals), 302 (decimals with `yavat`).
- **v438 below says it was an off-by-one, not a hang. Measured again on v282: it does not stop.**
  `chakra i = 0 tak 3.0` printed 6,625,058 lines in 3 seconds (ELF), 16-17 million in 10 s (PE, from both the
  Linux and the Windows compiler), still counting; it would end near 4.6 x 10^18. `0 1 2 3 4` is what its first
  five lines look like (evidence-r96/v282-remeasured.txt).

## v438 - CORRECTION to v437: a decimal loop bound is an off-by-one, not a hang

### What I got wrong
**v437 said `chakra dasham i = 0.0 tak 3.0` never terminates.** **It does terminate.**

**My test used `chakra vitti i = 0 tak 3` - invalid syntax, no braces, the type keyword in the wrong place - which printed nothing. I read "nothing" as "hangs" and wrote it down as fact.**

### What is actually true
| Form | Output | Correct? |
|---|---|---|
| `chakra i = 0 tak 3` | `0 1 2 3` | yes |
| `chakra i = 0 tak 3.0` | `0 1 2 3 4` | **no - one extra iteration** |
| `dasham d = 3.0; chakra i = 0 tak d` | `0 1 2 3 4` | **no - same** |

**So it is a wrong answer, not a non-termination.** **Less severe, still wrong, and it produced no error message.**

### And Muse's README sentence was wrong for the same reason
**It said "a loop whose end number is a decimal never stops."** **It stops, one iteration late.** **A README that overstates a limitation is as bad as one that hides it, because a reader who finds it stops will distrust the rest.**

### The lesson, which is the ninth of its kind
**Every one of the nine false claims in this session has the same shape: I ran something, got an unexpected result, and reported my interpretation instead of checking the setup.** **This time the setup was the syntax, and `examples/103_b10_nested_break_patches.sm` had the correct form all along.**

**The rule that would have caught it: when a test produces nothing, suspect the test before the compiler.**

## v437 - a decimal loop bound never terminates, and that is the worst bug in the language

### Verified by me on v282

**`chakra dasham i = 0.0 tak 3.0` produces NO OUTPUT and does not terminate.** Five-second timeout, nothing printed.

**A student writes it, the program hangs, and they conclude they are not clever enough to write a loop.** That is the exact failure ChatGPT named rounds ago - *"the student does not suspect the compiler"* - and it is now literal.

### And Claude found a wrong answer the same round
**`5.5 % 2.0` printed `6192449487634432`.** Now refused at v282 with `E_DASHAM_KRIYA`: on a decimal number, `%`, `&`, `|`, `^`, `<<`, `>>` are not permitted. **No program in the tree used one, so it was latent.**

### And the installer gate fired for the first time
**Gates: 58 PASS / 1 FAIL.** The FAIL is `installer version` - installer v243 against compiler v282. **The gate I asked for last round immediately caught the thing it was built for.** That is the first time a check in this project has failed on purpose and told us something true.

### Muse delivered the README sentence
> Still open, and stated plainly so you are not caught by them: a decimal number grown too large silently turns into infinity, and a loop whose end number is a decimal never stops - anything else that surprises you is worth reporting as a bug.

**It names two real limitations and ends by inviting bug reports.** That is the honest posture for a language that has found nine of its own defects in a week.

### What this changes about the release
**A language that hangs is worse than one that refuses.** The loop hang now outranks the installer and `parikshita` - because the other two produce a wrong artifact or a weak guarantee, and this one produces a program that never finishes with no explanation.

## v436 - the arithmetic question is closed: `inf` is reachable, undocumented, and correct

### What I measured on v281

**The overflow ladder, four squarings from `1e20`:**

| Step | Printed |
|---|---|
| `dasham h = 100000000000000000000.0` | `1.000000e+20` |
| `h = h * h` | `1.000000e+40` |
| `h = h * h` | `1.000000e+80` |
| `h = h * h` | `1.000000e+160` |
| `h = h * h` | `inf` |

**And `inf == inf` gives `1`, `inf > 0.0` gives `1`.** **Both are correct IEEE - `inf` compares normally and only `nan` is unordered.**

### So `inf` is not a bug
**It is a value the language prints and compares correctly.** **It was simply never documented, and a student meeting `inf` has no way to know what it means.**

### The decision, taken from ChatGPT's R163
**Option C: document binary64-style arithmetic and its exceptions.** Retain `inf`, `-inf` and `nan` as output spellings; explain them in the Sanskrit teaching material as values outside the finite range or an undefined result. **And state explicitly that Sutram does NOT claim complete IEEE 754 conformance - division by zero is an error, conversions have checked rules, and the grammar imposes further constraints.**

**That is honest in a way "we follow IEEE" would not be.**

### And the conversion fix is inert, which Muse measured
**Suite on v281: `PASS=263, NO-EXPECTATION=4, 0 fail`.** **Every in-tree conversion site was already converting a whole value first.** So the new `E_DASHAM_VITTII` refusal catches a mistake nobody in our own code was making - **which is the best outcome: right fix, zero cost.**

### What remains
**`parikshita`: 0 of 306 library functions marked, 63 eligible. It ships as a tool, not a guarantee, until the library is marked.**
**The installer: v279 while the compiler is v281. Claude has made it a gate.**
**The README paragraph, which decides whether a reader trusts everything else.**

## v282 (Claude, R94) - `%` and the bit operators refuse a `dasham`; the arithmetic gaps written down

- **Found: `5.5 % 2.0` printed `6192449487634432`.** `%`, `&`, `|`, `^`, `<<`, `>>` with a `dasham` operand ran the
  integer code on the IEEE-754 bits. Now refused when compiled: `E_DASHAM_KRIYA` (`r94_check_float_bitop`).
- **Reference, from probing v281:** `/` truncates toward zero and `%` follows the left sign; shifts take the count
  mod 64 and `>>` is logical; `dasham d = 7 / 2` is 3.0; `.5` and `5.` are not literals; `0.1 + 0.2 != 0.3`;
  tiny values print 0.000000 but are not zero; where inf and NaN come from; `100000000000000000000.5` is not
  that number (the old line said it was).
- **inf and NaN through `kosh`, functions and `mandapa`: unchanged, as expected** - now pinned (golden 299).
- **Goldens:** 297, 298, 299.

## v281, unchanged (Claude, R93) - the installer is a release gate; `e+N` explained

- **New gate `installer version`** (`tools/check_installer_version.py`): opens `Sutram-Setup.exe`, reads the
  version of `bin/sutram.exe` and `win/sutram.exe` in its embedded payload, and FAILS unless both equal the
  compiler's; `Sutram-Setup.sha256` must be the file's hash. **It FAILS today: the installer ships v243.**
  Gate `R93 installer gate` proves the checker on eight stand-in installers.
- **Reference §15:** how to read `1.000000e+80`, with a table of what prints; golden **296** pins it.

## v281 (Claude, R91-R92) - a computed `dasham` stored as a whole number must be whole

- **Integrated ChatGPT's R161 patch** (`ROUND-161-EXACT-FLOAT-TO-INT.patch`, unchanged): every statically
  typed float-to-integer conversion (declaration, assignment, `kosh_push`, integer-`kosh` store, integer
  argument, `mukhya`'s return) checks the value at run time: exact whole numbers in range convert; a fraction,
  inf, NaN or out of range stops with `E_DASHAM_VITTI`, exit 1. Its 13-case oracle: v280 4/13, v281 13/13.
- **The library relied on truncation in three places - rewritten, same results:** `madhava_sin`, `madhava_cos`
  (`k = trunc(x / 2PI)`) and `roop_sthir` (`rounded = scaled`) now take the whole part as a `dasham` with
  `(m + 2^52) - 2^52`, then convert exactly.
- **Four programs pinned truncation:** 93 and 94 now convert `blend(1.0, 3.0)` = 2.0 (same output); r71
  conversion converts 2.0 (same output); 112 shows 2.0 stored and 4.8 refused (golden changed - the intended
  rule).
- **Goldens:** 294 (ChatGPT's R160 six-operator NaN fixture, unchanged, renumbered: prints 0 1 0 0 0 0), 295
  (3.0 converts, 3.7 stops).

## v280 (Claude, R90) - NaN compares as IEEE says, a `dasham` divided by zero stops, `likha` keeps one line after a division

- **Integrated ChatGPT's R159 NaN patch** (`ROUND-159-NAN-COMPARE.patch`, unchanged): `==`, `<`, `<=` are false and
  `!=` true when either side is NaN; both code paths (general and register). Reviewed: `dl` is runtime scratch
  (the general path already pops into `rdx`). Its oracle: v279 5/10, v280 10/10, ELF and PE, and in the
  peephole and XMM-cache builds.
- **Integrated ChatGPT's R159 float-division patch** (`ROUND-159-FLOAT-DIVISION.patch`, unchanged): a `dasham`
  divided by `+0.0` or `-0.0` stops with `E_SHUNYA_BHAJAN`; NaN divisors are not mistaken for zero; the three
  division fast paths fall back to the checked general path. Its oracle: v279 1/8, v280 8/8.
- **Fixed (mine, since v276):** the division check's own message calls consumed `lkhb`'s no-newline flag, so
  `likha("y ", a / b, a % b, 5)` printed each value on its own line. `r80_emit_div_fatal` now saves it.
- **Not integrated:** ChatGPT's narrowing prototype - it refuses 25 tree programs, every one that imports
  `madhava` or `roop`, at a file-level position inside the library.
- **Goldens:** 291 (NaN, six operators), 292 (likha after a division), 293 (float division by zero); 289 and
  ChatGPT's NaN oracle now make inf and NaN by overflow, not by dividing by zero.

## v435 - the float blocker is closed, and it was my test that was wrong

### The answer: `dasham` is the float declaration, `vitti` is integer

**All three partners found it independently.** ChatGPT: *"Sutram supports float variables: declare them with `dasham`, not `vitti`."* Muse: *"`vitti` is integer storage; `dasham` is float storage."*

**I wrote `vitti f = 3.5` and concluded floats were broken. The language has a float declaration and I did not use it.** That is the seventh false claim of this session and the same shape as the other six: I tested what I assumed the syntax was.

### Verified by me on v279

| Test | Result |
|---|---|
| `dasham f = 3.5` | `3.500000` |
| `vitti f = 3.5` | **REFUSED - `E_DASHAM_VITTI`: dashamah sankhya purnanka-vittau na ...** |
| `dasham a = 1.5; dasham b = 2.0; likha(a + b * 0.5)` | `2.500000` |

**And Claude's v279 fix is the right one: not "make `vitti` hold floats", but "stop `vitti f = 3.5` from lying".** A written fraction in integer storage is now refused with a named error instead of being silently truncated.

**Suite 258, two new goldens (289, 290). 80 DIFFER programs, every one run: 79 print the same bytes with the same exit code.**

### And the two symptoms were never one bug
**ChatGPT: *"The earlier negative result used the much larger literal `10000000000000.0`... The two observations exercise different operations and are not evidence of one platform-specific bug."***

**So its negative came from a large float, mine from the wrong keyword. Neither was a platform difference.** I asked it to settle a discrepancy that did not exist.

### The library is fine
**34 of 260 example files declare `dasham`.** So the library does use floats properly, and Muse's earlier Madhava verification at six decimals stands.

### What this leaves
**Integers: done. Floats: done, with a refusal where a fraction would be lost. Memory: done and measured. The boundary: done. Arithmetic: division by zero and literal overflow refused.**

**Still open: the `kosh` alias (latent, documented), generics (deferred by design), threads (absent), Windows execution (the maintainer's), and the docs reorganisation.**

## v434 - a float in a variable loses its fraction, and that is the release blocker

### What I measured on v278

**`likha("3.5 = ", 3.5)` -> `3.5 = 3.500000`** - a float LITERAL prints correctly.
**`vitti f = 3.5` then `likha("f=", f)` -> `f=3`** - a float VARIABLE loses its fraction.
**`likha(0.5)`, `likha(1.5)`, `likha(2.25)` -> correct to six decimals.**
**`vitti a = 7; vitti b = 2; likha(a / b)` -> `3`** - integer division, as documented.

**So the value survives parsing and dies at the store.** That is the diagnosis, and it came from running the two cases side by side rather than reasoning about the compiler.

### Why it is the release blocker
**A student computing an average, storing it, and printing it gets an integer.** They conclude their arithmetic is wrong. That is the same failure as the overflow I closed in v276 - correct-looking code, wrong answer, no message.

**And it makes "arithmetic is done" too broad.** Integers are done. Floats are not.

**ChatGPT chose this as the release blocker in R156 and was right.** It reported the symptom as "a positive float prints as negative"; I get truncation. Two symptoms, same area, and R157 asks it which program produced its negative.

### And the docs are not current, which I am recording rather than hiding
**The changelog stopped at v432.** The alias-is-real correction and this float finding were both missing. **README mentions floats but not the alias.** The reference is current on both.

### Rounds issued
**R87 Claude** - dump the emitted code for `vitti f = 3.5` and find where the fraction goes; then check whether any golden recorded the truncated output.
**R157 ChatGPT** - why its symptom differs from mine, and does Sutram support float variables at all.
**R85 Muse** - does the library compute through float variables, and were its earlier six-decimal comparisons valid or lucky.

## v432 - I was wrong for several rounds: `vitti a = k` is not refused

### What happened
**Since round 76 I have written "Refused: `vitti a = k`" in every partner brief.** **ChatGPT tested it on Windows and said it is not refused on v277. I ran it on v278:**

```
kosh k[2]
kosh_push(k, 41)
vitti a = k
likha(a[0])        -> prints 41
```

**It compiles and runs.** **I conflated it with `box[0] = nirmmita(64); outer = box[0]`, which IS refused, and then repeated the wrong one as verified fact for several rounds.**

### Why it matters beyond the error
**Two variables can own one `kosh` buffer.** **That is the exact hazard that made me drop the recycling bins in Step 0 - the reason the whole `kosh` fix was redesigned.**

**So the aliasing hazard is real and open, and I have been telling three partners it was closed.**

### And `kosh` in a block is done
**Claude's R82 shipped it: generation-checked, refused after the block, 0 DIFFER elsewhere across 665 programs on three paths, +11% worst case where the check runs.** **Suite 255, gates 57 PASS, new gate `R82 kosh-mandapa`.**

**That was the last memory gap I was tracking - and it is closed.**

### The pattern, which is the fourth of its kind
**Four false claims in my briefs this session:** **`vitti a = k` refused** · **the one-sentence scope rule sufficient** · **15 mutants including a Madhava sign error** · **`nirmmita(-1)` "compiles and runs" when it segfaults.**

**All four share a shape: I described what I believed the system did, rather than running it and pasting the output.** **The `## Verified behaviour` block exists to prevent this and did not, because I wrote its entries from memory.**

**So the rule becomes: every line in that block is run in the same turn it is written, and the output is pasted in.** **And I have asked ChatGPT what format would make a claim in it impossible to be wrong.**
