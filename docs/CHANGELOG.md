> **The 20 newest entries.** Older ones, from "v436" back to the first, are in [rounds/CHANGELOG-ARCHIVE.md](rounds/CHANGELOG-ARCHIVE.md) (split in R88).

## v298 (Claude, R121) - `anka_akshar` and `vartani_sandhi` fixed: the two builtin defects Windows exposed

- **`anka_akshar(code)`** wrote its character **below the stack pointer** and returned that address, leaving
  `rsp` 8 bytes lower each call. Windows lost the character at once (the runtime's kernel32 call uses that
  stack: example 322 printed a garbage byte); Linux lost it as soon as the value was kept past a call. **Now two
  bytes from nirmmita's allocator**, as `s + t`; the result lives as long as the program.
- **`vartani_sandhi(s, t)`** appends in place, and **`s` was allowed to be a string literal** - part of the
  program's code. Windows: access violation (0xC0000005, example 322); Linux: it silently overwrote the code
  after the literal, and crashed the second time round a loop. **Now a literal `s` is refused when compiled,
  and a literal reached through a variable stops the program** (`E_VARTANI_STHIRA`, exit 1). In-place
  appending into writable memory is unchanged (R54's raw test).
- Examples 322/323 append into a `nirmmita` buffer instead of the literal; **their goldens are unchanged** - the
  golden was the right answer, Linux printed it by luck. Gate `R121 builtins` (14 checks, ELF and PE).

## v297 (Claude, R118) - the library's English names become aliases; three compiler hints name the R111 builtins

- **Ten library `prakriya` get Sanskrit names** (ChatGPT R191's bucket-1 words `bit`, `diff`, `pad`, `pre`,
  `sign`, `sorted`): `ekanka_gan` (was `bit_gan`), `rakh_ubhaya_bhed` (`rakh_samroop_diff`), `roop_purti_vam` /
  `_dakshin` / `_madhya` (`roop_pad_*`), `purti_vam` (`pad_vam`), `roop_ank_upasarga` (`roop_ank_pre`),
  `roop_chihna_akshar` (`roop_sign_akshar`), `asti_kramabaddha` (`asti_sorted`), `suchi_asti_kramabaddha`
  (`suchi_asti_sorted`). The library defines the new name; **a call written with the old one compiles to the same
  bytes** and prints R111's warning once (`Sutram suchana: 'asti_sorted' purana nama - 'asti_kramabaddha'
  likhatu`) - not for a program's own `prakriya` of that name, a variable, a `yoj`'d module or a `--lang` run.
  Reference section 4c; gate `R118 library names`.
- **Hints:** `kosh_gan(k)` (was `kosh_len(k)`) in the five `E_KOSH_*` hints, `likha_rup` in the `parikshita` hint,
  `dvaram_likha(dvara, ...)` (was `fd`). Eight refusal goldens re-recorded: that hint line, and the old-name
  warning gone because the examples now use the new names.
- **Examples and the library now write the R111 names** (257 replacements in 72 examples, 57 in `lib/`; outside
  string literals). Every changed program compiles to the bytes it did. `examples/323` keeps the old builtin
  names, `346`/`347` the old library names, on purpose.
- **Not changed, waiting for a decision:** the four pack-translated `kosh` messages (three compiled into
  programs) that name `kosh_pop` / `kosh_peek` / `kosh_dequeue` / `kosh_push`, and the shell help's `mala arr[5]`.

## v296 (Claude, R116) - fifteen of the sixteen library contracts (ChatGPT R189); long string literals work

- **The policy, in the library:** a mathematical library function gives the exact answer or fails through a
  declared channel. *Stops* (stderr `Sutram truti [CODE]: function: ...`, exit 1): `dvigun`, `trigun`, `vardh`
  (`E_ATIPRAVAH`); `nirapeksh_mulya`, `ganita_nirapeksh`, `mahattam_samapavartak`, `viparyay_ank`,
  `brihat_ank_tak_laghu` (`E_PHALA_SEEMA`; bad digits `E_MULYA_AYOGYA`); `brahmagupta_kshetr` (exact multiword
  formula; bad sides `E_MULYA_AYOGYA`, area past the range `E_ATIPRAVAH`); `adish_gunan`, `bindu_gunan` (unequal
  lengths, `E_AKARA_ASAMYA` - v295 used the shorter). *Status*, nothing printed: `brihat_ank_se` (0, digits
  cleared), `suchi_shreni` (0, list unchanged), `varna_tak_dashm` (leading zeros no longer spend digits: twenty
  characters `00000000000000000001` are 1, not 0). `yog_seema` saturates only the final sum
  (`yog_seema(2^62, 2^62)` is 2^62, was 2^63 - 1). Messages exactly as R189's matrix.
- **Not built: `patra_asti`** (row 11) - its contract needs an operating-system metadata query the compiler does
  not have; reported, not improvised.
- **`abhava(cond, "text")`:** the assertion takes an optional message, written to stderr before exit 1 - the
  compiler-emitted failure path the library uses (no OS call in a core module).
- **A compiler defect found on the way, fixed:** a string literal of 127 bytes or more was jumped over with a
  one-byte jump that wrapped backwards, so the program crashed (SIGSEGV or SIGILL), or ran on and printed
  nothing or the wrong text; `likha` and `likha_rup` of a literal also wrote only its length modulo 256. The R189
  messages are 88-151 bytes. Every literal of 126 bytes or fewer compiles to the same bytes as before.
- Examples 330-344 (one per row) and 207 (now the refusal); the suite checks a `<name>.err` when one is recorded.

## v295 (Claude, R115) - `sankhya_bindu` / `sankhya_dot` withdrawn; the arena branch's silent wrong answer found and fixed there

- **Withdrawn, not missing:** a call to `sankhya_bindu` or `sankhya_dot` is refused when compiled -
  `E_PRATYAHRITA`, with the name, the line and the library's working float dot product (`yoj sankhyiki`,
  `bindu_gunan(a, b)`). v293's integer loop was right for integer cells and **wrong for a `kosh dasham`**
  (it multiplied float bits: 2.5·2.5 + 1.5·1.5 gave 0) - my mistake in R113, found against Muse R111's shapes.
  No old-name warning first (ChatGPT R187). Example 329 is now that refusal.
- **The arena branch** (`claude/r108-arena-review`, not merged): its silent wrong answer - `chain40_reuse.sm`
  printing another block's 99 - was the outlives analysis stopping after 32 rounds; fixed on the branch (`3a6292e`)
  with main's v291 fix. Main changes only by the withdrawal.

## v294 (Claude, R114) - `Sutram Error` becomes `Sutram truti`, in the compiler and all eleven packs

- **The failure token is Sanskrit:** every message that stops a compile or a program begins `Sutram truti`
  (`Sutram truti [E_PARSE]: ...`). Bodies, `[E_CODE]` tags, punctuation, placeholders and exit codes unchanged;
  `Sutram suchana:` unchanged.
- **By the owner's written exception** (3 November; `docs/decisions/R114-SUTRAM-TRUTI.md`): the one token,
  identically in all eleven `lang/*.sandesh` files - 68 message values each, 748 in all - and nothing else in them.
  Each pack file differs from v293 by the token alone.
- `tools/sandesh.py` enforces the new token (a pack still carrying `Sutram Error` is refused - a new test); the
  Linux IDE's failure check matches `truti`; goldens, test scripts and current docs move with it.
- **Not changed:** the linker's own messages (`sutram-link`, `sutram-elf2smo`, `sutram-coff2smo`) - outside the
  permission. A program built by v293 or earlier still prints `Sutram Error` from its own bytes.

## v293 (Claude, R113) - a `rachana` reference beside an operator is refused; `sankhya_bindu` is an integer dot product

- **`E_RACHANA_GANIT`:** `p == q`, `p < q`, `p + q` (and every operator) on a `rachana` reference - a name whose
  field the `prakriya` reads or writes, or a method's first parameter - is refused, as a bare `kosh` or `mala`
  is. Up to v292 they compared, ordered and added two addresses. The reference states the meaning `==` will have
  on all three - the same object - and why it is refused until a `kosh` has a stable identity (ChatGPT R182).
  Example 328. No program in the tree changed (705 compiled, 0 differ).
- **`sankhya_bindu(a, b, n)`** (was `sankhya_dot`, Muse R108's one alias whose body was wrong): the integer dot
  product of n 8-byte cells. Up to v292 it took two pointers and returned the bits of four 32-bit float products,
  which no Sutram value holds. Example 329. `sankhya_yog` / `sankhya_gunan` are documented as what they are
  (four 32-bit float lanes), not fixed.
- The reference says what would remove `Sutram Error`, the one English word left.

## v292 (Claude, R111) - the vocabulary change, as aliases: 22 builtins get Sanskrit names, `asti` / `nasti` are `==` / `!=`, `tyaj` leaves the shell

- **22 builtins have a new, primary name; the old one still works and compiles to the same bytes.** An old name
  written in the program's own file prints one warning per name on stderr - `Sutram suchana: 'kosh_push' purana
  nama - 'kosh_kship' likhatu` - and none from a `yoj`'d module or in a `--lang` run (a pack run prints only its
  pack's language). Reference §4b has
  the table. `tests/r111/test_vocabulary.py` (a gate): every pair byte-identical, ELF and PE.
- **`asti` / अस्ति is `==`, `nasti` / नास्ति is `!=`** - the same token (examples 324-327).
- **The shell:** `tyaj` leaves; `exit`, `quit`, `help` still work, with the warning; `sahayata` is help.
- **Sarvam's decisions applied:** `to` dropped; `vartani_sandhi`, `kosh_apanay`, `anka_akshar`, `likha_santat`;
  Muse's two: `smaran_pratilip` and `sahayata`. **Not changed:** `Sutram Error` (R111-00 says why).

## v291 (Claude, R109) - the outlives rule follows a second name and a chain of any length; the installer gate names the payload; the suite's summary is its last line

- **ChatGPT R178's branch findings, checked on main:** two were open on v290. `vitti a = k` then `rakh(a)` gave a
  block's `kosh` to a `prakriya` that keeps it (only `k`'s own name was checked), and a chain of 33 or more
  keeping `prakriya`s passed it out (the fixpoint stopped after 32 rounds). Both are `E_KOSH_MANDAPA` now:
  an alias made by `vitti a = k` or `a = k` carries the block, and the fixpoint runs to convergence. Examples 320
  and 321. A full table of open block `kosh`s now refuses instead of leaving the next one unchecked, and a walk
  that overflows its stack counts the parameter as keeping (neither is reachable in the tree).
- **`installer version`** now says what it read: `payload v243 inside Sutram-Setup.exe (the wizard has no
  version of its own)`, the payload's packing date, and how many of its `lib`/`lang` files differ from the
  tree. `docs/INSTALLER-REBUILD.md` is the Windows procedure, with the payload compiler's expected SHA-256.
- **`tests/run_tests.py`** prints the failure details first and `suite: ... (N run)` last; a no-expectation
  program's output is indented and labelled. The gates read the last line.

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
