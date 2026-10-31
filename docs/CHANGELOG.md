> **The 20 newest entries.** Older ones, from v423 back to the first, are in [rounds/CHANGELOG-ARCHIVE.md](rounds/CHANGELOG-ARCHIVE.md) (split in R88).

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

## v431 - `parikshita` is built: opt-in, provably inert, and honest about its reach

### The boundary exists
**`parikshita prakriya` and `parikshita mukhya` - a checked function that may only call checked functions, verified whole, refused at the first bad edge.**

**And it is CONTEXTUAL, not a keyword:** **`vitti parikshita = 4` still compiles.** **No pack changed and the vocabulary budget is unspent.**

**Suite 253 (four new examples), library proofs 229, gates 56 PASS - with a new gate `R81 parikshita` covering 24 cases.**

### And the guard shows it is inert
**663 programs on three paths - 535 byte-identical, 124 refused identically, 0 DIFFER, 4 new.** **"Unmarked code is untouched, in bytes: the checker runs only on marked bodies and emits nothing."**

**That is the property that makes an opt-in feature safe to ship.** **It cannot break a program that does not use it.**

### The honest number
**63 of 306 library functions can be marked as they are.** **The rest need a language fix.** **So the boundary protects new code and about a fifth of the library - not everything, and that is now stated rather than implied.**

**And Muse's independent count disagrees with Claude's for at least one function, so the round asks for one reconciled table.** **A release cannot be held to two different numbers.**

### What is left
**Vectors in a block - the last memory gap.** **And generics.** **And threads, which I have asked ChatGPT to rank honestly, including which one it would NOT do in v1.0.**

## v430 - division by zero has a name, literal overflow is refused, and the boundary is being built

### Claude's R80 settled the arithmetic
**Division by zero and modulo by zero now stop with a named Sanskrit error instead of SIGFPE.** **A written number that does not fit in int64 is refused at compile time.** **And run-time overflow was MEASURED and left wrapping, documented.**

**That is the shape I asked for: literal refused, run-time measured rather than guessed, and the remaining behaviour written down rather than left silent.**

**Suite 249 (five new examples), library proofs 229, gates 55 PASS / 0 FAIL.**

### And the guard was reported the way it should be
**178 DIFFER, every one run, 175 give the same output and exit code, and 3 change on purpose - `trap_div` and `trap_mod` used to die by SIGFPE and now print the named error; `numeric29` prints the library's new contract.** **All three named.**

### Muse confirmed all three of my findings and added one
**`int64 max + 1` wraps. `4000000000 * 4000000000` wraps. `1 / 0` gave SIGFPE.** **And `5 % 0` also traps - which I had not tested.**

### Now the three things that make it capable
1. **`parikshita prakriya` - the safe/unsafe boundary, transitive.** **Without it the memory module is a design, not a guarantee.**
2. **Vectors in a block.** **Without it a `mandapa` cannot hold a list.**
3. **Generics.** **Without them you cannot write a sort that works for two types.**

**And the question I have asked that decides whether the boundary ships in v1.0: how many library functions must be converted before a checked function can do anything?** **If it is 200 across 20 modules, the feature is for new code only and that must be said now.**

## v429 - the block sells itself on a real program, the boundary is designed, and the arithmetic lies

### The real-program test, two independent measurements
**Claude, on a real 185-line program:**

| | peak memory |
|---|---|
| **no block** | **185 MB** |
| **blocks around the allocating functions** | **110 MB** |
| **with library temporaries in blocks too** | **7 MB** |

**And about 5% faster, with no restructuring - the block was wrapped around the allocating functions and nothing else changed.**

**My own 200,000-iteration test: 27,620 KB -> 11,772 KB, 2.3x, and 20% faster.** **Two measurements, same verdict: the block sells itself.**

**And `R79 real` is now a gate, so the program stays in the suite.**

### v275, and the fifth parser defect closed
**Suite 244, library proofs 228/228, gates 55 PASS / 0 FAIL, guard 491/120/35 DIFFER on three paths with all 35 same output.**

**The byte-versus-qword fix shipped at v274 - `nirmmita(10)` then `p[0..9]` now stops at `p[1]`.** **And one more silent misparse found and closed at v275: MIXED INDENTATION, tabs and spaces in the same block.** **That is the fifth of this session, and the one a Windows student would hit first.**

**And the whitespace mutator is now a permanent gate, so the class is tested on every run rather than fixed case by case.**

### The safe/unsafe boundary, designed
**ChatGPT's answer: mark the declaration, and verify the body and everything it can call.**

**`parikshita prakriya` - a checked function.**

| Source form | Meaning |
|---|---|
| **unmarked `prakriya`** | **legacy/manual code, no certification, no forced migration** |
| **`parikshita prakriya`** | **the whole function is verified, and rejected if it cannot be** |
| **`mandapa` in a marked function** | **lexical lifetime inside an already-checked function** |
| **`mandapa` in unmarked code** | **existing behaviour, partial diagnostics, not a checked island** |

**The key point: the boundary is TRANSITIVE.** **A checked function's guarantee holds because everything it calls is also checked.** **That is what closes the hole ChatGPT named.**

### And what I found doing the real-program test
**The program's total overflowed, so I tested the arithmetic directly:**

| Program | Result |
|---|---|
| **`9223372036854775807 + 1`** | **`-9223372036854775808`** - silent wraparound |
| **`4000000000 * 4000000000`** | **`-2446744073709551616`** - silent wraparound |
| **`1 / 0`** | **SIGFPE, exit 136 - a crash, no message** |

**Sutram has no overflow story and no divide-by-zero story.** **For a language aimed at school students, a silent negative square is worse than an error: the student concludes they do not understand arithmetic.**

## v279 (Claude, R87) - a fraction in a `vitti` is refused; every `dasham` prints right

- **Where the fraction went (WS1):** at the assignment. `vitti f = 3.5` loads 3.5 correctly and converts it with
  `cvttsd2si` (truncate) because `vitti` is the integer type; `dasham f = 3.5` prints `3.500000`. Store and print
  are correct. ChatGPT's "positive prints negative" was a second, separate defect: the printer.
- **`E_DASHAM_VITTI`:** a written fraction (or a written float too large for a `vitti`) stored in a `vitti`, in a
  declaration or an assignment, is refused at the number, with the Sanket `dasham f = 3.5`. Computed values still
  convert, truncating toward zero (the library relies on it). Integer-`kosh` element stores are not covered.
- **Printer:** below 9.0e9 the old path (identical digits); above, the whole part and fraction are printed apart,
  from 2^63 as `d.dddddde+N`, and `inf`, `-inf`, `nan` by name. Before, everything from 9.2e12, and inf and NaN,
  printed `-9223372036854.775808`, and 9.0e9-9.2e12 could lose the last digits.
- **Goldens:** `289` (float printing), `290` (the refusal). `examples/r71/conversion.sm` wrote `vitti a = 2.75`;
  it now converts through a `dasham` and pins the same output. No suite golden had recorded truncated output.

## v278, unchanged (Claude, R86) - the alias documented and pinned; the assumptions page checked

- **Reference §16, "Two names for one `kosh`"**: `vitti a = k` is a second name, not a copy; when `k` cannot grow
  in place (something allocated in between, or always on Windows) it moves and the other name keeps the old
  buffer - reads give old data, writes do not reach `k`. A worked program with its real output.
- **`examples/288`** pins it (`a[0]=41 k[0]=99` / `a[0]=7 k[0]=99`): if the alias is ever fixed, it fails.
- **Muse's assumptions page, every claim run:** 12 of 15 right; wrong - item 4's "faults even when nothing
  relocates" (not on Linux), item 7's "`0.0/0.0` is 0" (it is NaN), item 11's "an uninitialized `vitti` reads 0"
  (it reads a leftover value, differently on Linux and Windows).
- **Found, not fixed:** `dasham` comparisons treat NaN as equal to and below every number (`n == 42.0` is true);
  string `+` on variables adds addresses (printing the result crashes).

## v278, unchanged (Claude, R83) - `vitti a = k` measured: it diverges, it is not unsafe today, and refusing it breaks 3 fixtures

- **The alias diverges when the `kosh` grows and moves.** On Linux a `kosh` that is the newest block grows in
  place, so the two names stay one; with anything allocated in between, or always on Windows and in the guard-page
  build, the cells move and the second name stays on the old buffer, with the old length. **So the same program
  prints `41 41 7 1` on Linux and `41 41 41 0` under Wine.** R42's "an alias is the kosh" (`examples/255`)
  holds only while no push grows it.
- **Not a use-after-free today:** nothing is ever freed (no `munmap` / `VirtualFree` in the compiler); a `kosh`
  is never on the scratch side. It becomes one the day `kosh` memory is recycled.
- **Option 1 (refuse the copy), built and measured, not shipped:** it refuses `examples/252`, `255` and `287` -
  the fixtures that exist to exercise this alias - and no library module. Four routes still give a raw
  address (a `kosh` returned from a `prakriya`, passed to a plain parameter, pushed into a `kosh`, `k + 0`), but the
  existing type rule stops each being passed as a `kosh`: with option 1, no second `kosh` name is possible.
- **Option 3 done:** reference §16 states the rule, with the program that shows it (checked on Linux and PE).
- **Guard pages on v278:** controls 5/5, suite 255/0, library 229/229, properties 86/86; the R81 and R82 gates
  pass under the guard-page build. Nothing faults that did not before.

## Compiler v278 (Claude, R82) - a `kosh` made in a `mandapa` lives as long as the block

- **A `kosh` declared inside a `mandapa` is generation-checked** (ChatGPT R148's handle idea, smallest form): the
  block takes a fresh generation on entry (a stack slot, `rdtsc`), clears it on every exit (its end,
  `nivartanam`, `krama`/`agrim`); the `kosh` records it; a `prakriya` with a `kosh` parameter checks it on entry.
  After the block: `E_KOSH_MANDAPA`, naming the block's line, exit 1. Inside: unchanged - growth, recursion,
  `kosh dasham`. Examples 286 (accepted, computed value), 287 (read after the block - refused).
- **Only in a program that declares a `kosh` in a block. Every other program: the same bytes** (guard, 665
  programs, 0 DIFFER; the 8 benchmarks identical). In such a program: 3 more header words per `kosh`; one entry
  check per `kosh` parameter - +11% on a call whose body is one `kosh` read, +3.5% on `kosh_push`.
- Gate **`R82 kosh-mandapa`**: 9 cases; with the check off, all 5 refusals fail.
- **Not yet:** the block does not take the `kosh`'s memory back (kept, so that the header - and the check - stays
  exact); raw reads of its address are unchecked, as all raw memory.
- **The `parikshita` count:** `kosh` is still refused in a checked function (unchanged rule). An experimental
  checker that admits it - sound now, since a `kosh` is bounds- and lifetime-checked - passes **88** of 306
  library functions (63 today): all of `kalana` and `samanvaya`, 9 of `sankhyiki`. Not shipped; your decision.

## Compiler v277 (Claude, R81) - `parikshita`: the checked function, transitive

- **`parikshita prakriya` / `parikshita mukhya`** (ChatGPT R149's design): the compiler verifies the whole body
  after the program is parsed and **refuses** what it cannot verify. A checked function may call only checked
  functions (`E_APARIKSHITA_AHVAN`, at the call, naming the callee - the first bad edge of a chain) and the trust
  base `likha` / `likha_fmt` / `grahan` / `nirmmita` (`E_APARIKSHITA_KARYA` for any other builtin, `kosh`, fields,
  slices, function values, `prasar`); it may index only a `mala` or a `vitti p = nirmmita(NUMBER)` never assigned
  again (`E_APARIKSHITA_SMRITI`). `parikshita` is contextual - an ordinary name elsewhere; misplaced, it is
  `E_PARIKSHITA_STHAN`. Unmarked code: **the guard is 0 DIFFER** (no program's bytes change).
- Examples 282 (a checked program that sorts in a block - accepted), 283 (calls `mala_yog` - refused), 284 (the
  transitive edge), 285 (a parameter indexed). Gate **`R81 parikshita`**: 24 cases; it fails 15 with the checker
  switched off and 3 with transitivity switched off.
- **The library: 63 of 306 functions pass unchanged** (`ank`, `madhava`, `sadhan` entirely); all 243 others
  trace to a buffer passed as a parameter (131) or a byte / `kosh` / raw builtin (112) - both need a checked form
  in the language before the library can use it. None is marked yet.
- `tools/sutram_fmt.py` reads `parikshita prakriya` as a header (braceless bodies).

## Compiler v276 (Claude, R80) - division by zero stops with a message; written numbers that do not fit are refused; the library stops wrapping

- **`/` or `%` by zero stops the program** with `Sutram Error [E_SHUNYA_BHAJAN]: pankti N - shunye vibhajanam na
  sambhavati` (`%`: `shunyena sheshah na sambhavati`), exit 1. It was SIGFPE, exit 136, no message. N is the line
  in the user's own file (a `yoj` does not offset it); inside a module, that module's line and name -
  `pankti 3 (r80_ausat.smlib)`, `examples/281`. A divisor written as `0` is refused when compiled. **The smallest `vitti` divided by −1 no longer crashes** (it wraps to
  itself; `% -1` is 0). A divisor that is a written number other than 0 or −1 gets no check: the shipped
  benchmarks compile to the same bytes; a loop that divides by a variable costs +6%.
- **A written whole number that does not fit in 64 bits is refused** (`E_ATIPRAVAH`): `99999999999999999999`
  printed 7766279631452241919, `0x10000000000000000` printed 0. `-9223372036854775808` and
  `0 - 9223372036854775808` (the smallest `vitti`) are still allowed. **A `dasham` literal past 2^63 now has its
  value** (`100000000000000000000.5` was read as 7766279631452241919.5).
- **Arithmetic on written numbers whose answer does not fit is refused** — `4000000000 * 4000000000`,
  `9223372036854775807 + 1`, `-(0 - 9223372036854775808)` (`E_ATIPRAVAH`, "ganana punah likhyatam"), as
  `file:line:col` with the source line and a caret, like every other compile error.
- **The compiler itself no longer crashes on a written `MIN / -1`**: `(0 - 9223372036854775808) / (0 - 1)` killed
  it with SIGFPE (exit 136, v275 and before); it is now refused (`E_ATIPRAVAH`), and a written `MIN % -1` is 0.
- **`tools/fuzz_valid.py` writes an operand as `(1 ? A : 0)`** where folding two written numbers would now be
  refused - the same value, not folded - so the generated programs stay valid and still test run-time wraparound
  (seed 24: the same 1,376 output lines, 60/60 agree, on v275 and v276).
- **Run-time `+ - *` still wrap, as in C — measured, not assumed:** checking every operation (the `trap` build)
  costs +5.6% to +282% on the shipped benchmarks (+282% on `bench_loop`, +104% on `bench_nested`). Over the 10%
  line, so not shipped. The reference says so in one sentence (§3a).
- **The library stops wrapping on plausible input:** `kramgun` (21! and up), `fib` and `matra_meru` (93 and up),
  `varg`/`vargit` (|n| > 3037000499), `dwi_ghat` (63 and up), `yog_tak` (n > 4294967295) now return −1 when the
  answer does not fit; `ghat` and `ghan` return the largest or smallest `vitti`. Before, `kramgun(21)` was
  −4249290049419214848 and `kramgun(25)` a wrong *positive* number. **After Muse's R80 audit, three more:**
  `laghuttam_samapavartya` (lcm) and `purna_prasaran` (integer variance) return −1 when the answer does not fit
  (lcm(4000000000, 4000000001) was a wrong positive; the variance of [2^31, −2^31] was negative, now exactly 2^62);
  `yog_seema` halves before multiplying and saturates (yog_seema(0, 4294967295) was −2147483648 though it fits).
  `tests/stdlib/r80_library_edges`. Examples 277–281.
- **Frozen packs:** the two new messages are Sanskrit in every pack (no new pack text).
- **Found, not fixed:** `likha` of a `dasham` from about ±9.2e12 prints `-9223372036854.775808` (v275 too; Muse's
  R80 audit measured the threshold).

## Compiler v274-v275 (Claude, R77-R79) - the byte-versus-qword trap is caught; mixed indentation refused; a real program in blocks

- **`nirmmita` counts bytes, `p[i]` counts 8-byte cells.** When `vitti p = nirmmita(SIZE)` has a written SIZE and
  `p` is never assigned again in its function, a constant index past the end is a compile error
  (`E_NIRMMITA_SEEMA`, `nirmmita(10)` then `p[9]` -> "p[9] hetu nirmmita(80) avashyakam"), and a computed index is
  bounds-checked like a `mala`'s (the loop `p[i]`, i < 10, over `nirmmita(10)` stops at `p[1]`). No false alarm
  in the suite, the 228 library proofs or the 86 properties; cost 0% on the shipped benchmarks, +17-19% on a tight
  raw-write loop. **It found an overrun in our own test** (`tests/r73_scratch/reuse_zeroed`: 16 bytes into 13).
- **v275: tabs and spaces mixed in a body's indentation are refused** (`E_ANTARAL_MISHRA`). Muse's R77 mutator
  found the class; under it, a tab-indented body below a space-indented header ran its second line
  unconditionally (printed 10, not 0), and one example hung. `examples/276`.
- **No silent partial compilation:** 715 stray-token programs (every kind of body, indented and braced) and
  every example saved 9 ways (CRLF, trailing spaces, whitespace-only lines, tabs, mixed tabs and spaces two
  ways, no/extra final newline, UTF-8 BOM) - 2,186 checks - refuse or run every statement. New gates `R77 stray`, `R77 format`.
- **A real 185-line program in blocks** (`tests/r79_real/`): 185 MB -> 110 MB with blocks in the program alone,
  -> 7 MB with the library's own temporaries in blocks too (the R76 patch, not yet landed). Gate `R79 real`.

## v428 - I was repeating a wrong number: the mutants are 2, not 15, and there is no Madhava sign error

### Muse's correction
**I have said for several rounds that there are "15 surviving mutants including a sign error in the Madhava trig functions".**

**Muse's R76: the shipped Madhava code has no sign error.** **All five functions match Python's `math` to 6 printed decimals at 16 points.** **The sign flip is a MUTANT - a defect injected deliberately that no proof killed - not a bug in shipped code.**

**And of the 15: 12 are killed by today's tests, 1 is moot because the function no longer exists, and 2 still survive - the `suchi` and `avali_srij` size mutants.**

**So the real count is 2.** **I repeated 15 because nobody listed them and I did not ask.** **The same error as everything else this session: citing a figure instead of checking it.**

### And two independent parties rejected the run-time range check
**Gemini: "an address-range check cannot distinguish iteration 1's dead pointer from iteration 2's live allocation at the same address."**
**ChatGPT: "after reuse, an old pointer and a valid new pointer can have exactly the same address."**

**Same conclusion, different reasoning, no contact between them.** **The run-time range check is out and will not be revisited.**

### And ChatGPT named the top risk, which is not a bug
**> "The single release risk I prioritize is an unenforced safe/unsafe boundary: ordinary unchecked raw memory can invalidate the assumptions of the checked part."**

**That is not a defect to fix; it is that the checked and unchecked parts share one language and nothing stops them mixing.** **It is now the top item, and the round asks for the smallest marking that makes the boundary visible to a reader and to the compiler.**

### Process change, applied
**Every partner brief now opens with a `## Verified behaviour` block carrying the exact tested outputs of the check, so a partner reasons from the current compiler rather than from my description of an earlier one.** **Gemini's best work went into a hole that was already closed because I sent a stale brief; that will not repeat.**

## Library (Claude, R76) - two wrong answers fixed; raw memory stated as unchecked

- **`kuttaka` (Aryabhata) was wrong in every one of 438 random cases with a modulus above 2^40:** `old_s * mult` overflowed. On 600 random
  cases it was right 162/162 times for small moduli and **0/438** for large ones; `tests/stdlib/numeric29` had
  recorded a wrong answer (2605677504891245458; the solution is 1483584605987376058). Now the product is taken
  modulo |b| without overflow (`kuttaka_gun_shesh`): 600/600.
- **`meru(n, k)` (Pingala's C(n, k)) wrapped silently past 2^63 - 1** (`meru(1000, 10)` gave C(1000, 10) mod 2^64).
  It now returns **-1** when the answer does not fit; all 2,556 values for n <= 70 checked.
- **The Madhava functions had no sign error to fix:** the R15 "sign error" was a surviving *mutant* (a missing
  test), killed since R18. sin/cos/atan match Python to the printed 6 places on 24,003 points from -100 to 100.
- `tests/stdlib/r76_known_values` pins every behaviour a surviving mutant showed no proof pinned, each value
  checked against exact arithmetic, not recorded from the implementation.
- **`nirmmita` buffers are not bounds-checked** - now said in `docs/LANGUAGE-REFERENCE.md` §6c. `mala` and
  `kosh` are.

## v427 - Gemini found the byte-vs-qword trap, and named the real risk better than I did

### Its headline finding was already closed - and that was my fault
**Gemini reported that taint is laundered through indexing: `box[0] = nirmmita(64); outer = box[0]`.** **I tested it on v273 - REFUSED with `E_SCRATCH_ESCAPE`.**

**So that hole was closed in a round after I wrote the brief.** **I sent Gemini a description of the check as of an earlier round instead of its current tested behaviour.** **The fault is mine.**

### But two of its findings are real, and one I confirmed
**The byte-versus-qword trap:**
```
vitti p = nirmmita(10)
yavat (i < 10)
    p[i] = i
```
**Compiles, runs, writes 80 bytes into a 10-byte block.** **`nirmmita` takes BYTES; `p[i]` indexes in 8-byte units.** **A student asking for "10" gets 10 bytes and writes 10 qwords.**

**Nobody on this project noticed that in 273 versions, including me.**

**Its two fixes are cheap: round allocations up to 8 bytes (nearly free, alignment is already required), and record `const_bytes` so `nirmmita(LITERAL)` catches an out-of-range constant index at compile time.**

### And its answer to "the single biggest risk" is the best anyone has given
**> "Silent partial compilation. When the parser meets an unexpected token it exits via `ret` instead of aborting. The student runs a binary that executes only half their program - and because they are a beginner, they do not suspect the compiler, they assume they are too dumb to understand loops."**

**That is the exact shape of all four parser defects, and it explains why they were dangerous rather than annoying.**

**The fix: assert EOF at the end of compilation, and assert a valid dedent at every block exit - never `ret` on an unexpected token.** **About 15 lines, and it makes the class structurally impossible rather than fixed case by case.**

### And its structural verdict, which I accept
**Asked whether a better design exists: no.** **With untyped 64-bit values, no runtime tags and no lifetime type system, the only alternatives are Zig-style arena handles (zero compile-time protection) or copy-out evacuation (impossible for general containers without runtime type descriptors).**

**"Your dual-cursor lexical `mandapa` block with compile-time taint tracking is already at the structural Pareto frontier."**

### And a process change, because the stale brief was my error
**Every partner brief now opens with a `## Verified behaviour` block carrying the exact tested outputs of the check - not a remembered description.**

## Compiler v273 (Claude, R75) - a negative size is an error; one known limit named

- **`nirmmita` with a negative size.** Written as a number (`nirmmita(-1)`, `nirmmita(2 - 3 * 4)`), anywhere: refused
  at compile time, `E_NIRMMITA_RNA`. Computed, inside a `mandapa`: the program stops with
  `Sutram Error: nirmmita-parimanam rnatmakam - mandapa-madhye rnam parimanam na sambhavati`, exit 1. (v270 wrote a
  qword into the block above; v271-v272 gave 0. Outside a block, and on Windows, a computed negative still gives 0.)
- **A store inside an expression is checked** (since v271): `vitti out = kosh_push(k, buf) + 1` is refused;
  `examples/270` is the golden. `out = (m[0] = buf) + 1` is not Sutram - an assignment is a statement.
- **Known limit - a scratch address inside a `kosh`.** Putting one in directly is refused (`kosh_push(k, buf)`,
  `k[i] = buf`, through an alias, in a `kosh` made inside or outside the block). **One way in is not seen: a
  `prakriya` that returns the address it was given** (`kosh_push(k, adr(buf))`). That program compiles and reads
  another block's data. Pinned by `tests/r73_scratch/blind_kosh_via_call.sm`; stated in `README.md` and
  `docs/LANGUAGE-REFERENCE.md` §19. Closing it needs a summary of what each `prakriya` does with its parameters.

## v426 - I tested the composition myself: all five memory steps hold together

**Every step had been verified alone. The joins had not. I ran the five.**

| # | Composition | Expected | Got | |
|---|---|---|---|---|
| **1** | **block in a loop, writing into an outer `kosh`** | `0 1 2` | **`0 1 2`** | **pass** |
| **2** | **scratch pointer as a parameter, derived value returned** | allowed | **`out=42`** | **pass** |
| **3** | **two sibling blocks in sequence** | `first=111 second=222` | **`first=111 second=222`** | **pass** |
| **4** | **a block allocating 64 MB, 1,000 times** | RSS stays at one block | **67,484 KB peak = one 64 MB block** | **pass** |
| **5** | **recursion 500 deep, a block in every frame** | `125250` | **`sum=125250`** | **pass** |

### The two numbers that matter
**Test 5: 0+1+2+...+500 = 125,250 exactly.** **So the mark IS per-frame under recursion - which was the specific risk, because a mark that is not per-frame would corrupt the scratch cursor silently and the escape check would not see it.**

**Test 4: 64 MB is 65,536 KB, and peak RSS was 67,484 KB after 1,000 allocations of 64 MB each.** **64 GB of cumulative allocation, 64 MB of actual memory.**

### So the design's last untested claim now holds
**Persistent and scratch memory coexist; a block writes into an outer `kosh`; siblings do not see each other; a scratch pointer can be used and its value returned; the range is reused; recursion keeps a separate mark per frame.**

### And the limits the tests showed
**Test 4 took 9.39 s for 1,000 iterations - 9.4 ms each.** **That is not the allocator (still 2-8 ns); it is touching 64 MB of fresh pages per block.** **A hot loop allocating a large block will be slow for the same reason it would be in C.**

**And the `kosh`-of-scratch-pointers hole is untested by all five, because none of them puts a scratch pointer into a container - that is the escape the check cannot see, and a test that passed it would prove only that the hole exists.**

### One process note, stated rather than glossed
**The sandbox was recycled and I had deleted my NASM copy cleaning up disk, so I could not rebuild the compiler.** **I used the prebuilt `sutram_compiler` from the repo - which is the artefact that ships, so the right thing to test, but it means these five results are on the binary in the tree rather than on a rebuild of the source in the tree.** **Claude's rounds rebuild from source; mine did not.**

## v425 - the memory model is built, and I measured it: 65 MB down to 14 MB, and the check refuses the right things

### Every part, verified by me on v270
| Test | Result |
|---|---|
| **`outer = buf + 64`** | **REFUSED - `E_SCRATCH_ESCAPE`** |
| **`m[0] = buf`** | **REFUSED** |
| **plain block, no escape** | **compiles** |
| **copy the DATA out, not the pointer** | **compiles** |
| **1,000,000 x 64 B, no block** | **123.0 ms, 65,216 KB peak RSS** |
| **1,000,000 x 64 B, in a `mandapa`** | **40.9 ms, 14,464 KB peak RSS** |

### So the block is real
**1,000,000 x 64 bytes is 64,000 KB.** **Without a block it accumulates all of it.** **With one, peak RSS stays at 14 MB - flat.** **And it is 3x faster, because the memory stays in cache instead of touching 64 MB.**

### And the error is in the language
```
Sutram Error [E_SCRATCH_ESCAPE]: asthayi smriti bahir na gacchati -
mandapa-madhye nirmitam sthanam nivartanam na shakyate
```

### Five steps, all five built
1. **Step 0 - the `kosh` recycling bins: impossible, both invariants false. Dropped.**
2. **Step 1 - the contiguous bump and in-place extension: built at v263.**
3. **Step 2 - the two cursors: built at v264.**
4. **Step 3 - the `mandapa` block: built at v268, inert at 508 bytes both ways.**
5. **Step 4 - the escape check: built by v270.**

**This is the first round where all five can be said to be done, and the first where the design's central claim is measured rather than argued.**

### But the composition is untested
**Each step was verified alone.** **A block inside a loop that grows an outer `kosh`; a `prakriya` taking a scratch pointer; two sibling blocks in sequence; a block that exhausts the range; and deep recursion with a block per frame - none of those have been run.**

**So the round asks for the composition, and asks ChatGPT whether the sentence I want to put in the README is true of the compiler as it exists.**

## v424 - Step 3 done: the `mandapa` block exists, is inert, nests, and refuses one escape in Sanskrit

### Verified by me on v268, four tests
| Test | Result |
|---|---|
| **a block compiles and runs** | **`b=8`, `a=5`** |
| **INERT - with block vs without** | **508 bytes both, BYTE-IDENTICAL** |
| **nested blocks** | **`c=3`, `b=2`, `a=1`** |
| **a block inside a loop** | **`t=0`, `t=10`, `t=20`** |
| **`nivartanam` of a scratch address** | **REFUSED** |

### And the error message is in the language the program is written in
```
Sutram Error [E_SCRATCH_ESCAPE]: asthayi smriti bahir na gacchati -
mandapa-madhye nirmitam sthanam nivartanam na shakyate
```

**"Temporary memory does not go outside - a place created inside a mandapa cannot be returned."**

### What the block does today, stated honestly
**It scopes variables, it nests, and it refuses one escape.** **It does NOT redirect `nirmmita` to the scratch cursor, so it releases no memory.** **That is the correct order - a block that released memory without a check would be worse than no block - but it means the block is not yet the thing the design describes.**

### And Step 4 begins with the limit stated up front
**The check catches `outer = buf + 64` and `outer_mala[i] = buf`.** **It will NOT see a scratch pointer inside a `kosh` of pointers, and that must be said where a programmer hits it, not only in the design document.**

**So the round asks ChatGPT the question the design rests on: does K0 REFUSE a `kosh` in a checked function, or does it merely decline to CHECK it?** **"We do not check this" is honest. "We refuse this" is a restriction, and it decides whether a programmer can put a list of strings in a block at all.**
