> **Status at compiler v316, 9 November 2026 (R163) — read this before the page below.**
>
> **Compiler `Sutram 1.0 (v316) - sampurna sutra`.** Suite **PASS=327** (4 examples without a golden) · crash corpus **227/0** · library proofs **229 of 229** · property proofs **86 of 86** · gates **80 PASS / 0 FAIL / 1 NOT-RUN** (Linux, Xvfb). **The installer carries v316 (R163: the compiler, the linker and the two object readers never write over a file they read) and has not been run on Windows - a candidate, not a release; the NOT-RUN is Windows execution, the owner's own test.** Release notes: `docs/RELEASE-NOTES.md`.
>
> **The language today:**
> - **Sanskrit names are primary.** 22 builtins renamed in v292 (R111): `kosh_kship`, `kosh_gan`, `likha_rup`, `anka_akshar`, `vartani_sandhi`, ...; the old English names still compile, to the same bytes, with a `Sutram suchana` warning. Ten library names followed in v297 (R118): `asti_kramabaddha`, `ekanka_gan`, `roop_purti_vam`, ... (reference §4b, §4c).
> - **`asti` / `nasti` are `==` / `!=`**; `nivartanam` is return (`prati` a legacy alias).
> - **Every failure begins `Sutram truti`** (v294; `Sutram Error` up to v293).
> - **`sankhya_bindu` / `sankhya_dot` are withdrawn** (v295, `E_PRATYAHRITA`).
> - **Fifteen library contracts refuse instead of wrapping** (v296, R116); `patra_asti` is blocked on an OS query the compiler does not make.
> - **v298 fixed `anka_akshar` and `vartani_sandhi`**, which were wrong on both platforms; **v299 brought the Linux memory model to Windows** (R123), **v300 made Windows commit only what a program touches** (R124), **and v301 gives every name one kind for its whole `prakriya`** - a change of kind is `E_VITTI_PRAKAR`, a `kosh` that would become a raw number is `E_KOSH_DVARA` (R126; reference §16), **and v302 makes a `kosh` a descriptor** - two names stay one at any size, and there is no 64 MiB region per `kosh` (R127); **v303 fixes the three descriptor defects ChatGPT R203 found** (R128), **v304 lets a `kosh` parameter grow, and v305 settles `k[lo:]`** (R129, after ChatGPT R204); **v306 fixes the Windows out-of-memory crash, the installer's second-installation and endless-wait defects, and the IDE's stale screen** (R130-R131); **v307 closes the function-value slice (ChatGPT R205-206 S3), checks the Windows handler registration (W1), and finishes an interrupted installation** (R133); **v308 closes the slice's doors with one predicate (R207), keeps commit in hand for the Windows out-of-memory exit, and makes the installation a journaled transaction** (R134-R135); **v309 refuses a slice used as a number, and locks and re-checks the installation** (R137-R138); **v310 checks module-level initializers and locks before every installer read** (R141); **v311 puts the expression check inside expression code generation, gives it its own stack, and deletes nothing on a name** (R142); **v312 makes the check's budget reachable and fixes the licence page, the uninstall window and the empty `.sm` key** (R143); **v313 makes the budget a defensive stop no statement the tree holds can reach, fixes the licence label, and removes the uninstall staging folder** (R147); **v314 closes the foreign-function door to slices, adds `--analysis-steps=N` (default 200,000), names the two size limits apart, and fixes the desktop shortcut collision** (R152); **v315 gives the tree limit its own code, hardens the fold, and makes every installer ownership record a record of what was done** (R153-R154). How the defects were found - reading and testing catch different things: `docs/reports/HOW-DEFECTS-WERE-FOUND.md`.
>
> **Memory:** on Linux and, from v299 (R123), on Windows: `nirmmita` comes from an arena, a `mandapa` block returns what it allocated, `mandapa parimita N` refuses past a budget, a `kosh` is a descriptor whose elements may move but whose names always agree (v302; v299-v301: a 64 MiB region per `kosh`), and `parimana()` reports the bytes held. **On Windows it commits only the pages a program touches** (v300; in v299 the arena was 1 GiB of commit from the first allocation and each `kosh` 64 MiB) (reference §16, §19; `docs/MEMORY-MODEL.md`).
>
> **The open list is in the release notes:** "Not included in v1.0" and "Limitations of what is included" (`docs/RELEASE-NOTES.md`), revised with each release. (`WHATS-LEFT.md` and `OPEN-ISSUES.md`, last true at compiler v258, are archived in `docs/rounds/`; R156.)

# Sutram — Language Reference

Written by hand against the compiler source and the language packs, and checked by gates - so it **can** drift
from the code, and has (R152-R161: nineteen claims the code did not support, now corrected). Where this page and
the compiler disagree, the compiler is right and the page has a defect: report it. Gate `R158 doc currency`
checks its versions, symbols and the claims corrected so far; a paragraph that has quietly become false needs a
reader.

**Compiler:** v315 · patra extension `.sm`


## 1. Quick start

```sutram
mukhya()
    likha("Namaste, world!")
```

```sh
sutram hello.sm hello.bin && ./hello.bin     # Linux target
sutram hello.sm hello.exe                     # Windows target (on Linux the name decides; the Windows compiler always makes a Windows program)
```


## 2. Keywords

Sanskrit is the core. Devanagari spellings are accepted aliases. Each Indian
language has a pack of native words (see the `lang/` table at the end).

| keyword | meaning |
|---|---|
| `anka` | integer type |
| `anya` | else |
| `yoj` | include (module) |
| `bhavana` | condition |
| `guna` | multiply / switch |
| `krama` | break |
| `kuru` | do-while (with `yavat`) |
| `mukhya` | main / entry point |
| `abhava` | assertion: `abhava(cond)` stops the program, exit 1, when `cond` is 0; `abhava(cond, "text")` (v296) first writes the text to stderr |
| `yantra` | inline asm |
| `mala` | mala |
| `satya` | boolean type |
| `prakriya` | function (up to 6 arguments) |
| `nivartanam` (निवर्तनम्; legacy alias: `prati`) | return / returning / turning back (नि + √वृत्) |
| `chakra` | for |
| `purna` | true |
| `rachana` | struct |
| `sankhya` | number type |
| `shunya` | false / null |
| `ganana` | enum |
| `sutra` | constant |
| `agrim` | continue |
| `vitti` | whole-number (integer) variable; for a fraction use `dasham` (§15) |
| `vibhag` | slice parameter (R23; §17) |
| `siddhi` | return success: `nivartanam siddhi(v)` (R25; §18) |
| `dosh` | return failure: `nivartanam dosh(code)` (R25; §18) |
| `prasar` | call a phal-prakriya, propagating its failure (R25; §18) |
| `yadi` | if |
| `yavat` | while |
| `mandapa` (मण्डप) | a scratch block: temporary buffers of numbers for one piece of work (R72; §19) |
| `parikshita` | before `prakriya` / `mukhya` only: a checked function (R81; §20). Elsewhere an ordinary name |

## 3. Operators and precedence

Loosest to tightest (C-style ordering):

| level | operators |
|---|---|
| 0 | `? :` (ternary, right-associative) |
| 1 | `\|\|` |
| 2 | `&&` |
| 3 | `\|` |
| 4 | `^` |
| 5 | `&` |
| 6 | `==` `!=` |
| 7 | `<` `>` `<=` `>=` |
| 8 | `<<` `>>` |
| 9 | `+` `-` |
| 10 | `*` `/` `%` |
| 11 | unary `-` `!`, grouping `( )` |

### 3a. Integer arithmetic: what happens at the edges (v276)

**A `vitti` holds a whole number from −9223372036854775808 to 9223372036854775807. If `+`, `-` or `*` goes past
that while the program runs, the answer wraps around to the other end without any warning, so `x * x` with `x = 4000000000` prints `-2446744073709551616`. Dividing by zero stops the program with an
error.** In detail:

| | what happens |
|---|---|
| `+` `-` `*` past the range, **at run time** | wraps around, silently (checking every operation measured +5% to +282% on the benchmarks, so it is not done) |
| the same with **numbers written in the program** — `4000000000 * 4000000000`, `9223372036854775807 + 1`, `-(0 - 9223372036854775808)` | **refused when compiled**: `prog.sm:2:22: Sutram truti [E_ATIPRAVAH]: sthira-gananayah phalam 64-bit purnanka-seemam atikramati`, with the line and a caret under the operator |
| a **written whole number** too large — `99999999999999999999`, `9223372036854775808`, `0x10000000000000000` | **refused when compiled**: `... [E_ATIPRAVAH]: ankah 64-bit purnanka-seemam atikramati`. (`0 - 9223372036854775808` and `-9223372036854775808` are allowed: they are the smallest `vitti`.) A `dasham` literal may be larger, but it keeps only about 16 significant digits: `100000000000000000000.5` is `100000000000000000000.0` (the `.5` is lost; `==` between them is 1). |
| `/` or `%` **by zero** (also a `dasham` divided by `0.0`, v280 — §15) | the program **stops**: `Sutram truti [E_SHUNYA_BHAJAN]: pankti 3 - shunye vibhajanam na sambhavati` (for `%`: `shunyena sheshah na sambhavati`), exit 1. The line is in your file; inside a module it is that module's line and name: `pankti 3 (r80_ausat.smlib)`. **Written as `/ 0`, it is refused when compiled.** |
| `/` and `%` of negative numbers | `/` **truncates toward zero** and `%` **takes the sign of the left side**: `-7 / 2` is −3 and `-7 % 2` is −1; `-9 / 8` is −1 and `-9 % 8` is −1 (the same for a written divisor and a variable one). |
| `<<` and `>>` | the shift count is taken **modulo 64**: `1 << 64` is 1, `1 << 63` is the smallest `vitti`. **`>>` is a logical shift** - it fills with zeros, so a negative number becomes a large positive one: `-8 >> 1` is 9223372036854775804. To halve a negative number, use `/ 2`. |
| `/` and `%` by −1 | the smallest `vitti` divided by −1 wraps to itself; `% -1` is 0 (before v276 this crashed; written as numbers, `(0 - 9223372036854775808) / (0 - 1)` is refused) |
| when you need to know | the library's checked arithmetic says whether the answer fits: `ganita_janchit_yuj` / `_nyun` / `_gun` (`ok[0]` is 1 or 0); `ganita_paripurna_*` stops at the largest or smallest `vitti` instead of wrapping |

The library's number functions do not wrap on ordinary inputs (v276): `kramgun` (factorial), `fib`, `matra_meru`,
`varg`, `vargit`, `dwi_ghat`, `yog_tak`, `meru`, `laghuttam_samapavartya` (lcm) and `purna_prasaran` (integer
variance) return **−1** when the answer is too large to fit; `ghat` (power), `ghan` (cube) and `yog_seema` (range
sum) return the largest or smallest `vitti`.

**The policy (ChatGPT R189 WS3, accepted in R116; implemented in v296):**

> `vitti` stores a signed 64-bit integer from -9223372036854775808 to 9223372036854775807. In the default compiler build, ordinary runtime `+` and `*` keep the low 64 bits of the result and interpret them as a signed value: for example, adding 1 to the maximum produces the minimum, and multiplying the maximum by 2 produces -2. This is wrapping, not a mathematical answer, and it can happen even when you did not intend it; plain runtime operators do not report it. Written integer literals and constant expressions outside the supported range may instead be rejected during compilation, and the optional trapping compiler configuration has different behavior. Mathematical library functions must follow their individual documented contracts—exact result or declared failure, or explicit saturation where specified—so use the checked/status form when your program must detect a failure and continue. Neither a function's Sanskrit name nor a zero return value by itself proves that the computation succeeded.

**Where the sixteen library functions R188 found stand (v296).** *Stops* means one line on stderr,
`Sutram truti [CODE]: function: ...`, exit 1, nothing more printed, and `yadi dosh` cannot catch it. *Status*
means a return value says it failed and nothing is printed.

| function | when it fails | how | code |
|---|---|---|---|
| `dvigun`, `trigun`, `vardh` (`ganit`) | the result is past the range | stops | `E_ATIPRAVAH` |
| `nirapeksh_mulya` (`ganit`), `ganita_nirapeksh` (`ganita`) | `n` is −9223372036854775808 | stops | `E_PHALA_SEEMA` |
| `mahattam_samapavartak` (`ganit`) | the gcd is 2^63: `(MIN, 0)`, `(0, MIN)`, `(MIN, MIN)` only | stops | `E_PHALA_SEEMA` |
| `viparyay_ank` (`ank`) | the reversed number does not fit | stops | `E_PHALA_SEEMA` |
| `brahmagupta_kshetr` (`ganita`) | not the sides of a quadrilateral (or triangle, `d = 0`) / the area is past the range | stops | `E_MULYA_AYOGYA` / `E_ATIPRAVAH` |
| `brihat_ank_se` (`aadhar`) | a bad digit or base, or the number needs more than `n` digits | status 0, the digits cleared | — |
| `brihat_ank_tak_laghu` (`brihat`) | a digit outside 0..9, `n < 0` / the value is past the range | stops | `E_MULYA_AYOGYA` / `E_PHALA_SEEMA` |
| `patra_asti` (`patra`) | **not changed in v296** - the contract needs a new operating-system query (R116 report) | — | — |
| `yog_seema` (`sadhan`) | never: the exact sum, saturated only when the sum itself is past the range | — | — |
| `adish_gunan` (`samanvaya`), `bindu_gunan` (`sankhyiki`) | the two lengths differ (v295 used the shorter) | stops | `E_AKARA_ASAMYA` |
| `suchi_shreni` (`suchi`) | the sort's scratch cannot be had | status 0, the list unchanged | — |
| `varna_tak_dashm` (`vakyank`) | malformed text / past the `dasham` range (leading zeros never fail) | status: 0.0 and `ok[0] = 0` | — |

The exact messages are in `ChatGPT-to-Sarvam/ROUND-189-IMPLEMENTATION-MATRIX.json`; `tests/r116/test_contracts.py` checks
each at its boundaries. `E_PHALA_SEEMA`, `E_MULYA_AYOGYA` and `E_AKARA_ASAMYA` are new in v296 and their Sanskrit needs
native-speaker review.

**Printing a large `dasham` (fixed in v279).** Up to v278, `likha` of a `dasham` of 9.2×10¹² or more (either
sign), and of `inf` and `nan`, printed `-9223372036854.775808`, and from 9.0×10⁹ the last digits could be
wrong. Every `dasham` now prints correctly — §15.

Internal operator ids: `OP_ADD`=1, `OP_SUB`=2, `OP_MUL`=3, `OP_DIV`=4, `OP_EQ`=5, `OP_LE`=6, `OP_LT`=7, `OP_GT`=8, `OP_GE`=9, `OP_NE`=10, `OP_MOD`=11, `OP_AND`=12, `OP_OR`=13, `OP_XOR`=14, `OP_LAND`=15, `OP_LOR`=16, `OP_SHL`=17, `OP_SHR`=18


## 4. Built-in functions

These are the **actual** builtin names the compiler accepts, taken from its table. **From v292 (R111) the
Sanskrit name is primary; the old name in brackets still works, compiles to the same bytes, and prints a
warning naming the new one** (§4b).
(Earlier editions of this file listed short aliases such as `vartlen`, `charat`,
`memcpy` that the compiler does not recognise.)

| name | purpose |
|---|---|
| `likh` | write to a memory location |
| `pad` | read memory |
| `likh8` | write 8-bit value |
| `pad8` | read 8-bit value |
| `likh8c` | print a character |
| `pad8c` | read a character |
| `pankti_gan` (was `pankti_len`) | length of a constant-length `mala` mala |
| `likha` | 1–6 arguments: value(s); see §4a (string literals do not append LF, numeric final values do). Three values always print (v287); raw writes are `dvaram_likha` |
| `parimana` | `parimana()`: the bytes the program's `nirmmita` and `kosh` hold now (v289; section 19) |
| `dvaram_likha` | `dvaram_likha(fd, buf, len)`: write `len` bytes of `buf` to file descriptor `fd`; returns the count written (v286; see §4a) |
| `likha_santat` (was `lkhb`) | numeric output without LF; includes `dasham` numeric printing since R52 |
| `likha_rup` (was `likha_fmt`) | literal prefix plus integer followed by LF (no placeholder substitution; see §4a) |
| `shabda` | print a string variable |
| `grahan` | read a number from input |
| `sthagita` | halt the program |
| `dvaram` | patra descriptor helper |
| `paadh` | open a file |
| `band` | close a handle |
| `nirmmita` | allocate memory: `nirmmita(n)` gives `n` **bytes**, zeroed — `nirmmita(count * 8)` for `count` cells. Checked only when the size is a number and the name is never reassigned; otherwise writing past `n` bytes is your mistake, as in C (§6c) |
| `smaran` | fill memory |
| `smaran_pratilip` (was `smaran_cp`) | copy memory |
| `vartani_aayam` | varna length |
| `vartani_tul` | varna compare |
| `vartani_sandhi` (was `vartani_cat`) | append `t` to `s` **in place** and return `s`: `vartani_sandhi(s, t)` - `s` must be writable memory with room (`b = nirmmita(n)`, `vartani_pratilip(b, "...")`), as C's `strcat`. **A string literal as `s` is refused when compiled, and stops the program at run time when it arrives through a variable** (`E_VARTANI_STHIRA`, v298): a literal is part of the program. For a new string, `s + t` |
| `vartani_pratilip` | varna copy |
| `akshar` | character code at an index |
| `aksharank` | character code (note: index currently ignored) |
| `anka_akshar` (was `char_from`) | a new one-character string from a code: `shabda(anka_akshar(66))` prints `B`. From v298 each call gets its own two bytes (as `s + t` does), so the result can be kept; up to v297 it pointed at stack memory the next call overwrote |
| `akshar_guru` (was `char_upper`) | uppercase a character |
| `akshar_laghu` (was `char_lower`) | lowercase a character |
| `sankhya_yog` | four 32-bit **float** lanes in raw memory, added: `sankhya_yog(dst, a, b)` (`addps`). No Sutram value holds 32-bit floats - `sankhya_bindu`, their dot-product sibling, is withdrawn (v295) |
| `sankhya_gunan` | four 32-bit **float** lanes in raw memory, multiplied: `sankhya_gunan(dst, a, b)` (`mulps`); the same limit |
| `sankhya_bindu` (was `sankhya_dot`) | **withdrawn (v295, R115):** refused when compiled - `E_PRATYAHRITA`, *"pratyahrita - asyah phalam ashuddham, sanshodhanam pratiksate"* (withdrawn: its result was wrong; awaiting repair). v292 read four 32-bit floats from each argument; v293 multiplied 8-byte cells as integers, which is wrong for a `kosh dasham`. **For two `kosh dasham`: `yoj sankhyiki`, then `bindu_gunan(a, b)`** (a `dasham`; the two lengths must be equal - unequal lengths stop the program with `E_AKARA_ASAMYA`, as in section 3a; until R162 this cell said it read the shorter length, which v295 did). |
| `jala` (was `netsock`) | create a socket |
| `jala_bandh` (was `netbind`) | bind a socket |
| `jala_shru` (was `netlisten`) | listen |
| `jala_grah` (was `netaccept`) | accept a connection |

### 4b. The vocabulary change (v292, R111): new names, old ones still accepted

Every builtin below has a Sanskrit name; the old one is an alias of the same builtin, so a program written either
way compiles to **the same bytes**. An old name written in the program's own file prints one warning per name,
on stderr, when it is compiled without `--lang` (not in a module it `yoj`s, and never in a pack run, which prints only
its pack's language):

```
Sutram suchana: 'kosh_push' purana nama - 'kosh_kship' likhatu
```

| new | old | new | old |
|---|---|---|---|
| `kosh_kship` | `kosh_push` | `pankti_gan` | `pankti_len` |
| `kosh_hri` | `kosh_pop` | `jala` | `netsock` |
| `kosh_gan` | `kosh_len` | `jala_bandh` | `netbind` |
| `kosh_ksham` | `kosh_cap` | `jala_shru` | `netlisten` |
| `kosh_iksh` | `kosh_peek` | `jala_grah` | `netaccept` |
| `kosh_rikt` | `kosh_empty` | `akshar_laghu` | `char_lower` |
| `kosh_shodh` | `kosh_clear` | `akshar_guru` | `char_upper` |
| `kosh_yuj` | `kosh_enqueue` | `anka_akshar` | `char_from` |
| `kosh_apanay` | `kosh_dequeue` | `vartani_sandhi` | `vartani_cat` |
| `likha_santat` | `lkhb` | `likha_rup` | `likha_fmt` |
| ~~`sankhya_bindu`~~ | ~~`sankhya_dot`~~ (both withdrawn, v295) | `smaran_pratilip` | `smaran_cp` |

**`asti` / अस्ति is `==` and `nasti` / नास्ति is `!=`** - the same token: `yadi (a asti b)` is `yadi (a == b)`, byte
for byte (`examples/324`-`327`). `==` and `!=` remain. In the shell (`sutram -i`) **`tyaj`** leaves (`exit` and
`quit` still do, with the warning) and `sahayata` is help (`help` still is, with the warning).

**`Sutram truti` (v294, R114): the failure token, in Sanskrit.** Every message that stops a compile or a
program begins `Sutram truti` (त्रुटि), often followed by an `[E_CODE]` tag: `Sutram truti [E_PARSE]: ...`. Up to
v293 it was `Sutram Error`, the last English word a program could print. The token is fixed: every language pack
keeps it word for word around its own translation, so a failure looks the same, and can be searched for, in any
language. **`truti` is the severity, not a verdict on the program** - a syntax error, a safety refusal
(`E_APARIKSHITA_AHVAN`) and a resource limit all stop what was asked, for the reasons their codes and text give.
A notice that stops nothing begins `Sutram suchana:` (the deprecation warning, §4b).

The change was made by the owner's narrow exception to the pack freeze, written down in
`docs/decisions/R114-SUTRAM-TRUTI.md`: one token, in the compiler and all eleven packs, nothing else in them.
A program built by v293 or earlier still prints `Sutram Error` from its own bytes; rebuild it.

`to` is not a word either (`tak` is the loop's "up to"; `prati` stays the return alias).

### 4c. The library's English names (v297, R118): new names, old ones still accepted

Ten library `prakriya` had an English word in their names. **The library now defines the Sanskrit name; a
call written with the old name still compiles - to the same bytes - and prints the §4b warning once**, when it
is in the program's own file (not in a `yoj`'d module; never in a `--lang` run):

```
Sutram suchana: 'asti_sorted' purana nama - 'asti_kramabaddha' likhatu
```

| new | old | module | what it does |
|---|---|---|---|
| `ekanka_gan` | `bit_gan` | `ganit` | the count of 1-digits (एकाङ्क) in `n`'s binary form |
| `rakh_ubhaya_bhed` | `rakh_samroop_diff` | `sangrah` | the difference both ways (उभय-भेद): `(a - b)` with `(b - a)` |
| `roop_purti_vam` | `roop_pad_vam` | `roop` | fill (पूर्ति) on the left to `width` |
| `roop_purti_dakshin` | `roop_pad_dakshin` | `roop` | fill on the right |
| `roop_purti_madhya` | `roop_pad_madhya` | `roop` | fill both sides |
| `purti_vam` | `pad_vam` | `vakyank` | fill a `mala` of character codes on the left, in place |
| `roop_ank_upasarga` | `roop_ank_pre` | `roop` | a number in any base, with its prefix (उपसर्ग) `0b` / `0o` / `0x` |
| `roop_chihna_akshar` | `roop_sign_akshar` | `roop` | a number with the sign character (चिह्न) you give for `+` |
| `asti_kramabaddha` | `asti_sorted` | `shreni` | 1 if the array is in order (क्रमबद्ध), non-decreasing |
| `suchi_asti_kramabaddha` | `suchi_asti_sorted` | `suchi` | the same for a `suchi` |

**What counts as the old name:** an identifier followed by `(` - a call. A `prakriya` your program defines with
an old name is yours: it is not renamed and not warned about. A variable of that name is not touched.

**Three compiler hints named old builtins, and now name the new ones** (`kosh_gan(k)` for `kosh_len(k)` in the
five `E_KOSH_*` hints, `likha_rup` for `likha_fmt` in the `parikshita` hint, and `dvaram_likha(dvara, smriti,
sankhya)` for `fd`). **Four run-time messages still name `kosh_pop`, `kosh_peek`, `kosh_dequeue` and
`kosh_push`**, and the shell's help still writes `mala arr[5]`: the ten frozen packs translate those messages
and keep those words, so changing them waits for the owner's decision (`Claude-to-Sarvam/R118-00-*.md`).

### 4a. Output: print values, raw bytes, and formatting (compiler v257)

`likha` is overloaded. **A string literal prints its bytes exactly as written** (there is no automatic newline); **a scalar integer or `dasham` prints a value followed by a newline**. **From v288 a string value - a variable, `s + t`, a string a `prakriya` returns - prints its text, like a literal, with no newline** (up to v287 it printed its address). A number last on the line ends it with a newline: `likha("name: ", s, " age ", 30)`. `shabda(s)` still prints a string, and a raw buffer is still `dvaram_likha`.

**One scalar value — `likha(x)` (newline included):**
```sutram
mukhya() {
    vitti x = 42
    likha(x)
}
```
**Exact expected stdout:**
```text
42
```

**One labelled line — `likha("label", x)` (already works):**
```sutram
mukhya() {
    vitti x = 42
    likha("x = ", x)
}
```
**Exact expected stdout:**
```text
x = 42
```
Both examples above end with one LF byte (`0A`), because printing the final numeric value adds it. Existing `examples/43_nested_likha.sm` uses this two-argument form, with an exact output golden.

**Three to six values (R52; v287):** three to six arguments always print each value in turn, whatever comes first -
`likha(a, b, a)` with `a = 7`, `b = 9` prints `797` (up to v285 a three-argument `likha` whose first argument was
not a string literal wrote raw bytes; see below). Numeric intermediate values do not add newlines; the last numeric value adds one.
```sutram
mukhya() {
    vitti x = 42
    vitti y = 7
    likha("x = ", x, ", y = ", y)
}
```
**Exact expected stdout:**
```text
x = 42, y = 7
```

**Raw write — `dvaram_likha(fd, buf, len)` (v286; it was the three-argument `likha`):**
```sutram
mukhya() {
    dvaram_likha(1, "raw\n", 4)
}
```
**Exact expected stdout** (`raw` plus LF, four bytes):
```text
raw
```
Here `1` is stdout's file descriptor; the second value is a byte-buffer pointer and the third is its byte count;
the result is the number of bytes written. `dvaram` (an opening) is the fd family's word, with `dvaram`/`band`/`grahan`.

**Up to v285 this was `likha(fd, buf, len)`:** a three-argument `likha` whose first argument was not a string
literal wrote raw bytes, so `likha(a, " ", b)` printed nothing. v286 refused that form (`E_LIKHA_TRAYA`); **from
v287 `likha` with three values prints three values**, whatever comes first: `likha(a, " ", b)` prints `7 9`
(`examples/308`). Old raw-write calls must be `dvaram_likha`.

**`lkhb(x)` — numeric output without a newline (R52 also fixes `dasham`):**
```sutram
mukhya() {
    dasham d = 2.5
    lkhb(d)
    likha("|\n")
}
```
**Exact expected stdout:**
```text
2.500000|
```
`lkhb(2.5)` prints **`2.500000`**, not the raw IEEE-754 integer bits on compiler v257. It contributes no newline; the explicit string literal contributes the trailing `|` and LF.

**`likha_rup(fmt, v)` — literal prefix + integer, not placeholder substitution:**
```sutram
mukhya() {
    likha_rup("x = ", 42)
}
```
**Exact expected stdout:**
```text
x = 42
```
`likha_rup` currently outputs the literal format/prefix string and numeric value sequentially. It does **not** interpret `{0}` or other format placeholders; its integer number path **already writes a final LF**. Therefore an extra `likha("\n")` gives an unwanted blank line. The existing `examples/format_demo.sm` has this extra newline; its golden records the blank lines. Do not edit either without running and updating acceptance.

**Evidence:** `src/sutram_compiler.asm:15956-15964,16144-16242,18050-18183`; `tests/r52/test_r52.py:55-74`; `tests/expect/43_nested_likha.out` and `tests/expect/format_demo.out`. Exact outputs are source/committed-test expectations, **NOT RUN by ChatGPT**.
## 4b. Standard library (`lib/`)

`yoj <name>` inlines `lib/<name>.smlib` into your program at compile time —
no runtime dependency, the code becomes part of your binary. `lib/` ships:

| module | include with | functions |
|---|---|---|
| ganit | `yoj ganit` | 15 — `varg`, `vargit`, `ghan`, `dvigun`, `trigun`, `vardh`, `nirapeksh_mulya`, `laghu2`, `adhik2`, `mahattam_samapavartak`, `laghuttam_samapavartya`, `ghat`, `kramgun`, `asti_abhajya`, `yog_tak` |
| ank | `yoj ank` | 10 — `asti_yugm`, `asti_visham`, `ank_gan`, `ank_yog`, `viparyay_ank`, `asti_viparyay_sam`, `seemit`, `fib`, `asti_sampurna`, `collatz_charan` |
| shreni | `yoj shreni` | 11 — `vinimay`, `budbud_shreni`, `shankh_shreni`, `viparyay_mala`, `laghu`, `adhik`, `yog`, `anwesh_sarak`, `gan`, `asti_kramabaddha` (was `asti_sorted`), `dwi_anwesh` |
| ganita | `yoj ganita` | 6 — `kuttaka` (linear indeterminate), `chakravala` (Pell's equation x^2-Ny^2=1), `samasa` (Brahmagupta's composition law), `brahmagupta_kshetr` (cyclic-quadrilateral area), `ganita_vargmool`, `ganita_nirapeksh` |
| madhava | `yoj madhava` | 5 — `madhava_pi`, `madhava_sin`, `madhava_cos`, `madhava_atan`, `madhava_vargmool` (Kerala school, T12 floats) |
| varna | `yoj varna` | 13 — `varna_maap`, `akshar_sanket`, `asti_ank_akshar`, `asti_unnat_akshar`, `asti_avanat_akshar`, `asti_akshar_akshar`, `asti_avakash_akshar`, `gan_swar`, `gan_akshar`, `anwesh_akshar`, `asti_sarv_ank`, `unnat_sanket`, `avanat_sanket` |

60 functions across six modules. `shankh_shreni` is markedly faster than `budbud_shreni` on real
arrays. **How many modules a program can bring in:** there is no count. `examples/99_ast_multimodule_capacity.sm`
brings in seven. The limits are sizes: the program and everything it brings in, expanded, at most 128 KiB
(`IMPORT_BUF_CAP`), and the syntax tree, 3 MiB (`E_VRIKSHA_SEEMA`, "Size limits" below). (Until R161 this page
said a program could bring in only two modules, a limit fixed in R54; the sentence stayed.)

Example:

```sm
yoj ganit

mukhya()
    likha(mahattam_samapavartak(48, 36))     # 12
    likha("\n")
    likha(kramgun(5))         # 120
    likha("\n")
```

Written in Sutram itself. Every library function copies its parameters into
locals before changing them, because the compiler currently faults on
assignment to a parameter.

### Big-integer digit order (`brihat`)

`lib/brihat.smlib` represents a nonnegative base-10 big integer in **least-significant-digit-first (LSB-first)** order, not ordinary printed digit order.
Each digit occupies one 8-byte cell; callers allocate an array of `n` cells (for example with `nirmmita(n * 8)`).
After `brihat_ank_se_laghu(1234, digits, 4)`, `pad8(digits + 0 * 8)` is `4`, `pad8(digits + 1 * 8)` is `3`, `pad8(digits + 2 * 8)` is `2`, and `pad8(digits + 3 * 8)` is `1`.
`brihat_ank_tak_laghu(digits, 4)` reads that same LSB-first representation back as `1234`. Do not reverse the cells when passing them to other `brihat_*` functions.

## 5. Types

| type | declared with |
|---|---|
| integer | `vitti x = 5` / `anka x = 5` / `sankhya x = 5` |
| float (binary64) | `dasham x = 3.5` / `दशम x = 3.5` — §15 |
| constant | `sutra PI = 3` |
| boolean | `satya flag = purna` |
| mala | `mala a[10]` or `vitti a[10]`; index reads/stores are bounds-checked |
| struct | `rachana Name = { field1, field2 }` |
| enum | `ganana RED = 1` (declared inside a function) |

### 5a. Strings: `==`, `<`, `+` work on their text (v287)

**A string is a NUL-terminated run of bytes** - a literal, or what `+` builds. From v287 the operators work on
the text, not on where it is stored:

| you write | means | example |
|---|---|---|
| `a == b`, `a != b` | the same bytes, to the NUL | `"ab" == "ab"` is 1; `"ab" == "abc"` is 0; `"" == ""` is 1 |
| `a < b`, `<=`, `>`, `>=` | byte order: the first byte that differs decides, a prefix comes first | `"apple" < "banana"` is 1; `"ab" < "abc"` is 1 |
| `a + b` | a **new** string: `a`'s bytes, then `b`'s; `a` and `b` are unchanged | `"rama" + " " + "sita"` is `rama sita` |

All of these work in `yadi` and `yavat` conditions, on literals, variables, what a `prakriya` returns, and
parameters (`examples/306`, `307`, `309`). **`likha` prints a string's text** (v288, section 4a; `examples/312`).

**Which values are strings.** The compiler decides, before it generates a function, from the whole program:
a variable is a string when **every** value it is given in that function is one (a literal, another string
variable, `s + t`, a string-returning `prakriya`); a parameter is a string when **every** call passes one; a
`prakriya` returns a string when **every** `nivartanam` does. Anything else is a number, as before.

**What the compiler refuses**, each at compile time, instead of guessing:

| you write | refused with |
|---|---|
| a string beside a number - `s == 5`, `s < n`; or a variable that is a string in one place and a number in another (`s = "ab"` ... `s = 5`), compared with a string | **`E_VARTANI_TUL`** `'==' ekatah vartani anyatah na - ubhau vartani, athava ubhau sankhye, bhavetam` (*a string on one side and not on the other - both strings, or both numbers*) |
| `s + 2.5`, or a sometimes-string `+` a string | **`E_VARTANI_CAT`** |
| `s + k` (a `kosh` in arithmetic, a string or not) | **`E_KOSH_GANIT`** `kosh-upari ganitam tulana va na sambhavati` - the `kosh` check comes first (until R161 this row said `E_VARTANI_CAT`) |
| `s - t`, `s * 2`, `s / 2`, `s % 2`, a bit operator on a string | **`E_VARTANI_GANIT`** `vartanya saha '-' '*' '/' '%' (bit-kriyah api) na sambhavanti` |
| `vitti x` with no value, in a function | **`E_MULYA_VINA`** (v286) - write `vitti x = 0`; a `mala`, a `kosh` and a module-level `vitti` are unchanged |

**Still allowed, as before:** a string plus or minus a whole number is pointer arithmetic (`s + 1` is `s`
without its first byte; `base + 6` for a slice). A variable that is sometimes a string, used with numbers only,
keeps its integer meaning.

**Where `+`'s string lives, and what it costs.** On the persistent side, as a `nirmmita` outside a `mandapa`:
**for the rest of the program.** It does not die with a block, so it can be kept anywhere; and `mandapa parimita`
does not count it. Each `+` costs its length + 1 bytes (rounded up to 16) and two `strlen` loops (4 instructions
a byte) and a `rep movsb`. Measured: 1,000,000 joins of two 8-byte strings in a loop - about 31 MB (31,104 and 31,232 KB in two runs), under 0.1 s. Join
in a loop only what you keep; `s = s + piece` repeated copies the growing prefix each time.

**Comparison costs** 9 instructions a byte (two loads, compare, two tests, two increments, the loop) to the
first difference or the NUL, and allocates nothing: 1,000,000 comparisons of two equal 64-byte strings - 0.04 s.
A program with no string comparison compiles to the same bytes as before (the guard).

**Also refused from v288** (Muse's R101 traps 3 and 4):

| you write | refused with |
|---|---|
| a string as a whole condition: `yadi (s)`, `yavat (s)`, `s && x`, `s ? a : b` - every string, even `""`, was true | **`E_VARTANI_SATYA`** `vartani satyam asatyam va na bhavati` - write `yadi (s != "")` |
| a `kosh` as an operand: `a == b` on two koshes (0 for two equal ones), `k + 1` | **`E_KOSH_GANIT`** `kosh-upari ganitam tulana va na sambhavati` - compare `k[i]` or `kosh_len(k)` |
| a `mala` as an operand (v290): `a == b` on two mala, `a + 1` | **`E_MALA_GANIT`** `mala-upari ganitam tulana va na sambhavati` - compare `a[i]` (`examples/319`) |
| a `rachana` reference as an operand (v293): `p == q`, `p != q`, `p < q`, `p + q`, `p asti q` - a name whose field the `prakriya` reads or writes (`p.x`), or a method's first parameter | **`E_RACHANA_GANIT`** `rachana-upari ganitam tulana va na sambhavati` - compare `p.x` (`examples/328`) |

**What `==` on a `kosh`, a `mala` or a `rachana` will mean: the same object (R113, ChatGPT R182).** Two names
for one `kosh`, `mala` or record are equal; two that were made separately are not, even when every element or
field matches. Ordering (`<`, `<=`, `>`, `>=`) and arithmetic (`+` and the rest) will stay refused: an address
order is not an order of collections, and adding two references means nothing. **Today all of them are refused**
- `E_KOSH_GANIT`, `E_MALA_GANIT`, `E_RACHANA_GANIT` - because identity needs a stable identity for a `kosh` that
grows (R178's descriptor), and a refusal is safe until then. To compare contents, compare the elements or fields.

**How a `rachana` reference is recognised (v293).** Variables carry no type: `vitti p = nirmmita(24)` is an address
in an ordinary `vitti`, and `p.x` finds `x` by its name. So the compiler knows `p` is a record by its use: **a name
whose field the `prakriya` reads or writes, anywhere in its body, or the first parameter of a method
(`prakriya Bindu.chal(swa, ...)`)**. Such a name beside an operator is refused. A copy that never touches a field
(`vitti q = p`, then `q == r`) is not recognised - the same limit as a `kosh` or `mala` given a second name.
Up to v292 `p == q` compared the two addresses (1 only for one record), `p < q` ordered them and `p + q` added them.

**Not known to be strings, and so not handled:** module-level variables, `kosh` and `mala` elements, and a
`prakriya` used as a value (`vitti g = f`). Compared with a string they are refused, not guessed. Two of them
compared with each other still compare as numbers. An empty string is still true in `yadi (s)`.

## 6. Syntax by example

```sutram
# comments:  # ...   or  // ...   or  /* block */

mukhya()
    vitti count = 3                 # variable
    sutra LIMIT = 10                # constant

    yadi (count > 2) {              # if / else if / else
        likha("big")
    } anya yadi (count == 2) {
        likha("two")
    } anya {
        likha("small")
    }

    chakra i = 1 tak 5 {      # for (ascending)
        yadi (i == 3) { agrim }   # continue
        yadi (i == 5) { krama }      # break
        likha(i)
    }

    chakra j = 5 tak 1 {      # for (descending)
        likha(j)
    }

    vitti k = 0
    yavat (k < 3) {                 # while
        k = k + 1
    }

    likha(joda(3, 4))               # function call
    likha("x = ", k)                # two-argument print
    vitti s = "hello"
    shabda(s)                       # print a string variable
    vitti n = grahan()              # read a number

prakriya joda(a, b)                 # function (up to 6 arguments)
    nivartanam a + b                 # return

prakriya fib(n) {                   # braces are required for a body of >1 statement
    yadi (n < 2) { nivartanam n }
    nivartanam fib(n - 1) + fib(n - 2)
}
```

```sm
vitti m = x > 5 ? 100 : 200      # ternary, right-associative
kuru {                            # do-while (kuru ... yavat)
    i = i + 1
} yavat (i < 10)
```

A brace-less function body is exactly **one statement**. For anything longer,
wrap the body in `{ }`.

**`prakriya` requires the braces. `mukhya` does not.** They behave differently:

```sm
mukhya()
    vitti x = 1        # this compiles - mukhya accepts a brace-less body
    likha(x)
    likha(x + 1)
```

```sm
prakriya f(n)
    vitti x = n        # this does NOT compile - parse error
    nivartanam x
```

**Verified:** `mukhya()` with three brace-less statements compiles and runs; `prakriya f(n)` with
three brace-less statements fails with `vyakaran dosh, pankti 3:5, shabd 'nivartanam'`.

**This is an inconsistency, not a rule**, and it is recorded rather than resolved. **Every example in every
book writes `mukhya()` without braces** - 84 complete book programs, all of which compile - **so a beginner
learns the brace-less form from the first page and then hits the wall on their first `prakriya`.**

**If you are writing a function with more than one statement, always use braces.** It works for both, and it
is what the books should show.

*Open question for the owner: should `mukhya` and `prakriya` be made consistent? Documenting it is what this
section does; unifying them would be a language change.*


### 6a. Counted loops: `tak` and `arabhya … paryantam` (R52)

**Legacy spelling** (accepted, but `tak` is Hindi/Urdu, not a Sanskrit particle):
```sutram
mukhya() {
    chakra i = 0 tak 4 {
        likha(i)
    }
}
```
**Sanskrit-oriented alternative — already implemented, same loop and binary in the R52 test:**
```sutram
mukhya() {
    chakra i = 0 arabhya 4 paryantam {
        likha(i)
    }
}
```
**Exact expected stdout for EACH form:**
```text
0
1
2
3
4
```
**A `chakra` counts in whole numbers (v283).** Its counter is a `vitti` and steps by 1, so both ends must be
whole numbers: `chakra i = 0 tak 3.0`, `chakra i = 0.5 tak 2.5`, a `dasham` variable as an end
(`chakra i = 0 tak n` with `dasham n`), or a `dasham` variable as the counter are refused when compiled:
`Sutram truti [E_CHAKRA_DASHAM]: chakra purnankaih eva gananam karoti - dashama-sankhya na sambhavati`, with
a caret under a written decimal. **Up to v282 such a loop compared the decimal's bits as a whole number** -
3.0 is 4613937818241073152 - so `chakra i = 0 tak 3.0` printed 0, 1, 2, ... and never stopped, and a
decimal start counted from its bits. To step through decimals, use `yavat`:

```sutram
mukhya() {
    dasham x = 0.0
    yavat (x <= 3.0) {
        likha(x)          # 0.000000 1.000000 2.000000 3.000000
        x = x + 1.0
    }
}
```

Adding `0.1` ten times does not give exactly `1.0` (§15), so a `yavat` on decimals should compare with `<`
or `<=` against a bound, never `==`.

The endpoints in this example are **inclusive**; `arabhya` means 'starting from' and `paryantam` means 'up to'. Both are contextual words in the `chakra` grammar, **not reserved keywords**: they can still name variables. `arabhya` without the closing `paryantam` is invalid. `chakra` means wheel/cycle and is a technical loop marker; neither spelling makes the whole code a classical Sanskrit sentence.

**Evidence:** `src/sutram_compiler.asm:9361-9415`, `tests/r52/test_r52.py:89-99`, `examples/11_forloop.sm` (legacy `tak` form). Test assertions are partner-maintained, not re-executed here.
### 6a-2. Bodies without braces (v265–v267)

Braces are optional on every body. Without them, **indentation decides**:

```sutram
yavat (i < 3)
    likha("i=", i)      # these three lines are the loop body,
    vitti p = nirmmita(64)
    i = i + 1           # because they are indented deeper than `yavat`
likha("done")           # back at the header's indentation: after the loop
```

- The body is every following line indented deeper than the header, at the body's indentation; it ends at the
  first line indented less. A line indented between the header and the body is an error.
- A body on the header's own line is one statement: `yadi (x == 0) likha("zero")`. A second statement on that
  line (`yadi (c) a = 1; b = 2`) is an error — it would otherwise run outside the `yadi` (v267).
- Nothing may follow `mukhya`'s closing `}` (v266). A `mukhya()` written without braces runs to the end of the file.
- **Indent a body with tabs or with spaces, not both** (v275). Indentation is compared only when one line's
  leading whitespace begins with the other's; a tab-indented body under a space-indented header is refused —
  `Sutram truti [E_ANTARAL_MISHRA]` at that line — because before v275 a tab counted as one column, and such a body
  silently ran its second line outside the `yadi` (`examples/276`).
- `guna` needs `{ }`; its `bhavana` bodies may be indented.

### 6b. Is Sutram speakable Sanskrit?

**Yes, as Sanskrit-oriented technical instructions; no, not as complete Sanskrit prose.** Keywords such as `mukhya`, `vitti`, `chakra`, `yoj` and `nivartanam` are Sanskrit-origin vocabulary (some are modern technical metaphors or conventional forms). `chakra i = 0 arabhya 4 paryantam` is a speakable *range phrase*, but its identifiers, `=`, braces, and command sequence do not supply the Sanskrit cases, verb inflections, and agreement required of an ordinary grammatical sentence.

Read it aloud as **code** with Sanskrit vocabulary, not as poetry or automatically well-formed Sanskrit discourse. Pāṇini's `anuvṛtti` and `adhikāra` are useful formal-grammar analogies, **not mechanisms currently implemented merely because they have Sanskrit names**. No new parser feature or natural-language understanding is claimed.

**Teaching example:** `examples/11_forloop.sm` already teaches a loop, but only the legacy `tak` spelling. After separately verifying the new form, update or extend that example to show the equivalent Sanskrit-oriented range without removing legacy coverage.
### 6c. Raw memory: `nirmmita` counts bytes, `p[i]` counts 8-byte cells

**`nirmmita(n)` gives you `n` BYTES. `p[i]` is the 8 bytes at `p + 8*i`.** So `nirmmita(10)` holds one whole
cell, not ten: for `count` cells, write **`nirmmita(count * 8)`**.

**What the compiler checks (v274):** when a name is declared `vitti p = nirmmita(SIZE)` with SIZE a number (or
`+ - *` of numbers) and is **never assigned again in that function**, `p` is known to point at the start of SIZE
bytes, and
- **a constant index past the end is a compile error**:
  `nirmmita(10)` then `p[9]` → `Sutram truti [E_NIRMMITA_SEEMA]: ... p[9] nirmmita(10) bahih` /
  `Sanket: nirmmita bhaita-sankhyam ganayati, p[i] ashta-bhaita-ekakaih: p[9] hetu nirmmita(80) avashyakam`;
- **a computed index is bounds-checked when the program runs**, like a `mala`'s: the loop
  `yavat (i < 10) p[i] = i` over `nirmmita(10)` stops at `p[1]` with `Sutram truti: mala ank seema atikram`.

**What it does not check:** a size computed at run time (`nirmmita(n)`), a name assigned again (`p = p + 8`), an
address computed from `p` (`p + 8`, `arr + (pos + 1) * 8`), a parameter, a `likh8`/`akshar_rakh` store. Those are
bare addresses: write past the bytes you asked for and the program may go on, crash, or change another buffer —
exactly as in C. (A header on every block, so that *any* address could be checked, was built and measured in R76;
it breaks the library's addresses into the middle of buffers. `mala` and `kosh` are always checked.)

To *find* such a mistake, build the compiler with guard pages (`nasm -dGUARD_PAGES`, as `tools/guard_page.py`
does): every `nirmmita` block then ends against memory that cannot be touched, and a write past its end stops
the program at once.

**A `dasham` stored into a whole-number `mala` is converted exactly (v288)**, as one stored into a `vitti`: `a[0] = 3.0`
stores `3`, and a value with a fraction (or too large for 64 bits) stops the program with `E_DASHAM_VITTI`
(`examples/315`). Up to v287 it stored the IEEE-754 bits (`3.0` read back as `4613937818241073152`). A raw
`nirmmita` buffer (`p[i] = d`) is unchanged: it holds whatever 8 bytes it is given. Use `kosh dasham` for a list
of `dasham`.

### 6d. Recursion depth: `E_GAHANATA` (v286)

A function that never reaches its base case used to end the program with a segmentation fault, exit 139, no
output. From v286 every `prakriya` checks the stack on entry (Linux); past **8,339,456 bytes below `mukhya`'s
entry** (8 MiB less 48 KiB, under the default 8 MiB stack) it prints

```
Sutram truti [E_GAHANATA]: aahvan-gahanata seema atikram
```

*(call depth: limit exceeded)*, exit 1. Each call frame is 2,048 bytes plus the saved registers, so the limit is
about **4,000 nested calls** - `yog(3900)` runs, `yog(4000)` is refused; up to v285 `yog(4000)` ran and `yog(4100)`
crashed. 500 levels, and the tree's deepest recursion (single digits), are far inside it. The check is `mov rax,
[entry_rsp]; sub rax, rsp; cmp rax, LIMIT; jb ok` in each prologue; the cost in the binary is 15 bytes in `mukhya` and
115 per `prakriya` (the check and its message are emitted with each); a 50,000,000-call loop ran in the same 0.10 s. Windows: not checked (PE output is unchanged).

## 7. Command line

| command | purpose |
|---|---|
| `sutram in.sm out.bin` | compile to a Linux executable (with the Linux compiler: a name ending `.exe` gives a Windows one; the Windows compiler, `sutram.exe`, makes a Windows program whatever the name) |
| `sutram in.sm out.exe` | compile to a Windows executable |
| `sutram --lang gujarati in.sm out.exe` | compile with a language pack |
| `sutram -i` | interactive shell (REPL) |
| `sutram --version` | version |

**The output is never a file the compile read (v316, R163).** Every file the compiler opens to read - the program,
each `yoj` module, the `--lang` pack, the `--ffi` file, `--separate`'s root - is noted by its identity (Linux: device
and inode; Windows: volume serial and file index). The output is opened **without** being emptied, its identity is
compared with each of them, and only if it is none is it cut to nothing and written. Otherwise nothing is written,
the file stays as it was, and the compile stops, exit 1:

```
Sutram truti [E_NIRGAM_NIVESH]: nirgam-patram 'hello.sm' nivesha-patram eva (pathitam) - tasmin na likhitam, tat yatha asit tatha eva
```

Identity, not the name: `./hello.sm`, `HELLO.SM` on Windows, a hard link and a symbolic link are the same file;
two files with the same bytes are two. If an output's identity cannot be read it is refused the same way
(`... nivesha-patrebhyah bhinnam iti na nishchitam ...`): not knowing is not taken for "different". A device such
as `/dev/null` or `NUL` is written as before. `sutram-link`, `sutram-elf2smo` and `sutram-coff2smo` do the same for
their objects (`Sutram Error [E_NIRGAM_NIVESH]: ... na likhitam: <output>`), and `tools/sutram_build.py` refuses a
`-o` that is the program, one of its modules, the `--ffi` file or a `--foreign` object before it compiles anything
(`sutram-build [E_NIRGAM_NIVESH]: ...`; the linker cannot see those - its inputs are the objects). An output that cannot be opened - a
folder that does not exist, the running compiler itself - stops the compile, exit 1 (up to v315 it said `Siddh`,
exit 0, and wrote nothing):

```
Sutram truti [E_NIRGAM_PATRA]: nirgam-patram 'out/hello' na udghatitam (lekhanaya) - kimapi na likhitam
```

Not covered, and why: the shell empties a file before the compiler starts (`sutram a.sm /dev/stdout > a.sm` has lost
the program before anything runs; with `>>` the compiler refuses, and its message - printed on standard output - is
what the shell appends). The REPL (`sutram -i`) and the Linux IDEs write fixed scratch files
(`/tmp/.sutram_repl.sm`, `/tmp/.sutram_ide.sm`, `/tmp/.sutram_gui_run.sm`; on Windows the REPL's
`.sutram_repl.sm` / `.sutram_repl.exe` in the current folder) and replace a file of that name without asking. A
write that fails part-way (a full disk) is not reported.

## 7b. Danda — Sanskrit sentence punctuation as the terminator

Semicolons and newlines already separate statements. A **danda** `।` (U+0964) does the same,
and a **dvigun danda** `॥` (U+0965) as well — so a program can be punctuated the way Sanskrit
prose is. Both are exactly equivalent to `;`; existing code is unaffected.

```sutram
mukhya()
    vitti a = 5।
    likha("नमस्ते")॥
```

The danda is common punctuation across all nine major Indic scripts (Unicode encodes it once,
in the Devanagari block, for Bengali, Gurmukhi, Gujarati, Oriya, Tamil, Telugu, Kannada and
Malayalam as well).

## 7c. Writing Sutram in Devanagari

The core keywords are already Sanskrit, in Latin transliteration. The **`sanskrit` pack** gives
the same words in their own script, so a whole program can be written in Devanagari:

```sutram
मुख्य()
    वित्ति योग = 0।
    वित्ति इ = 1।
    यावत् (इ <= 5) {
        योग = योग + इ।
        इ = इ + 1।
    }
    लिख(योग)।
```

    sutram --lang sanskrit program.sm out.bin

No new keyword is introduced — every line of the pack is a script variant of an existing core
keyword, and it compiles to the same native machine code.

## 8. Language packs — the same keyword in each language

| Sanskrit | sanskrit | bengali | gujarati | hindi | kannada | malayalam | marathi | odia | punjabi | tamil | telugu |
|---|---|---|---|---|---|---|---|---|---|---|---|
| anka | अङ्क | সংখ্যা | અંક | अंक | ಸಂಖ್ಯೆ | സംഖ്യ | अंक | ଅଙ୍କ | ਅੰਕ | எண் | సంఖ్య |
| anya | अन्यत्र | অন্যথা | નહિંતર | अन्यथा | ಇಲ್ಲದಿದ್ದರೆ | അല്ലെങ്കിൽ | नाहीतर | ନଚେତ୍ | ਨਹੀਂਤਾਂ | இல்லையெனில் | లేకపోతే |
| yoj | आयोजन | সমাবেশ | સમાવેશ | समावेश | ಸೇರಿಸು | ഉൾപ്പെടുത്തുക | समावेश | ସମାବେଶ | ਸ਼ਾਮਲ | இணைப்பு | చేర్చు |
| bhavana | भावना | ভাবনা | ભાવના | भावना | ಭಾವನೆ | ഭാവന | भावना | ଭାବନା | ਭਾਵਨਾ | நிலை | — |
| grahan | ग्रहण | পড়ো | વાંચો | पढ़ो | ಓದು | വായിക്കു | वाचा | ପଢ଼ | ਪੜ੍ਹੋ | படி | చదువు |
| guna | गुण | গুণ | ગુણ | गुण | ಗುಣ | ഗുണം | गुण | ଗୁଣ | ਗੁਣ | குணம் | గుణం |
| krama | क्रम | ক্রম | ક્રમ | क्रम | ಕ್ರಮ | ക്രമം | क्रम | କ୍ରମ | ਕ੍ਰਮ | வரிசை | క్రమం |
| likha | लिख | লিখো | લખો | लिखो | ಬರೆ | എഴുതു | लिहा | ଲେଖ | ਲਿਖੋ | எழுது | లేఖ |
| mukhya | मुख्य | মুখ্য | મુખ્ય | मुख्य | ಮುಖ್ಯ | പ്രധാനം | मुख्य | ମୁଖ୍ୟ | ਮੁੱਖ | முக்கியம் | ముఖ్యం |
| abhava | निषेध | নিষেধ | નિષેધ | निषेध | ನಿಷೇಧ | വിലക്ക് | निषेध | ନିଷେଧ | ਰੋਕ | தடை | నిషేధం |
| mala | पङ्क्ति | পঙক্তি | પંક્તિ | पंक्ति | ಸಾಲು | വരി | रांग | ଧାଡ଼ି | ਕਤਾਰ | வரிசைப்பட | వరుస |
| satya | परिग्रह | ধারণ | ધારણ | धारण | ಧಾರಣೆ | ധാരണ | धारण | ଧାରଣ | ਧਾਰਨ | உரிமை | కలిగివుండు |
| prakriya | प्रक्रिया | ফলন | ફલન | फलन | ಕ್ರಿಯೆ | ക്രിയ | कार्य | କାର୍ଯ୍ୟ | ਕਾਰਜ | சார்பு | ప్రమేయం |
| nivartanam | निवर्तनम् | ফেরত | પાછા | वापस | ಹಿಂತಿರುಗು | മടങ്ങുക | परत | ଫେରସ | ਵਾਪਸ | திரும்ப | తిరిగి |
| chakra | पुनरावर्तन | পুনরাবৃত্তি | પુનરાવર્તન | पुनरावृत्ति | ಪುನರಾವರ್ತನೆ | പുനരാവൃത്തി | पुनरावृत्ति | ପୁନରାବୃତ୍ତି | ਦੁਹਰਾਓ | மடக்கு | పునరావృతం |
| purna | पूर्ण | সত্য | સાચું | सत्य | ನಿಜ | സത്യം | खरे | ସତ୍ୟ | ਸੱਚ | பூரணம் | నిజం |
| rachana | रचना | সংরচনা | રચના | संरचना | ರಚನೆ | ഘടന | रचना | ସଂରଚନା | ਢਾਂਚਾ | அமைப்பு | నిర్మాణం |
| shabda | शब्द | শব্দ | શબ્દ | शब्द | ಶಬ್ದ | ശബ്ദം | शब्द | ଶବ୍ଦ | ਸ਼ਬਦ | சொல் | శబ్దం |
| shunya | शून्य | মিথ্যা | ખોટું | असत्य | ಸುಳ್ಳು | അസത്യം | खोटे | ମିଥ୍ୟା | ਝੂਠ | பொய் | అబద్ధం |
| ganana | सृजन | সৃজন | સર્જન | सृजन | ಸೃಷ್ಟಿ | സൃഷ്ടി | सृजन | ସୃଷ୍ଟି | ਸਿਰਜਣ | படைப்பு | సృష్టి |
| sutra | सूत्र | স্থির | કૂટશબ્દ | स्थिर | ಸ್ಥಿರ | സ്ഥിരം | स्थिर | ସ୍ଥିର | ਸਥਿਰ | சூத்திரம் | స్థిరం |
| tak | पर्यन्त | থেকে | થી | से | ರಿಂದ | മുതൽ | पासून | ଠାରୁ | ਤੋਂ | முதல் | నుండి |
| agrim | उद्देश्य | এগিয়ে | આગળ | आगे | ಮುಂದುವರಿಸು | തുടരുക | पुढे | ଆଗକୁ | ਅੱਗੇ | தொடர் | కొనసాగు |
| vitti | वित्ति | চল | ચલ | चर | ಚರ | ചരം | चल | ଚଳ | ਵੇਰੀਏਬਲ | மாறி | చరరాశి |
| vibhag | विभाग | বিভাগ | વિભાગ | विभाग | ವಿಭಾಗ | വിഭാഗം | विभाग | ବିଭାଗ | ਵਿਭਾਗ | பிரிவு | విభాగం |
| siddhi | सिद्धि | সিদ্ধি | સિદ્ધિ | सिद्धि | ಸಿದ್ಧಿ | സിദ്ധി | सिद्धि | ସିଦ୍ଧି | ਸਿੱਧੀ | வெற்றி | సిద్ధి |
| dosh | दोष | দোষ | દોષ | दोष | ದೋಷ | ദോഷം | दोष | ଦୋଷ | ਦੋਸ਼ | பிழை | దోషం |
| prasar | प्रसार | প্রসার | પ્રસાર | प्रसार | ಪ್ರಸಾರ | പ്രസാരം | प्रसार | ପ୍ରସାର | ਪ੍ਰਸਾਰ | பரப்பு | ప్రసారం |
| yadi | यदि | যদি | જો | यदि | ಒಂದುವೇಳೆ | എങ്കിൽ | जर | ଯଦି | ਜੇ | எனின் | ఒకవేళ |
| yavat | यावत् | যতক্ষণ | જ્યાંસુધી | जबतक | ಯಾವವರೆಗೂ | എത്രത്തോളം | जोपर्यंत | ଯେତେବେଳେ | ਜਦੋਂਤਕ | வரை | ఎంతవరకు |

25 core keywords, 34 built-ins, 11 language packs.



## 13. Philosophy

Sutram's keywords are Sanskrit by design, not decoration — in three layers: the **words**
(the keywords are the language's own vocabulary), the **name** (सूत्रम्, after Pāṇini's sūtra
tradition), and the **methods** (the standard library is the Indian mathematical tradition made
executable — Pingala, Āryabhaṭa, Brahmagupta, Bhāskara, the Kerala school, Kaṭapayādi).

See `docs/sutram-philosophy.html` for the full statement and the library roadmap.


## 14. Security & Permissions (project principle)

Every part of Sutram — compiler, toolchain, installer, tooling — must work at the **lowest
practical permission level**. A normal Windows or Linux user account, with no administrator or
root rights, must be able to install and use the whole project.

**Required:** standard-user permissions · portable / project-local dependencies · user-space
applications · files inside the project or normal user-data directories · relative paths ·
read-only access where possible · local/offline processing · sandboxed processes · no background
services unless genuinely required · no system-wide configuration changes unless there is no
reasonable alternative.

**Forbidden:** administrator/root · disabling or weakening OS security (antivirus, firewall, UAC,
Secure Boot, Gatekeeper, SELinux) · changing system security policy · kernel drivers · protected
system folders or registry areas (HKLM, Program Files, /etc, /usr) · opening unnecessary firewall
ports · SYSTEM/root services · asking users to weaken permissions · credentials in source ·
broad account permissions when read-only suffices.

**Tie-breaker:** if two designs give similar functionality, choose the one needing fewer
permissions and less system access.

**If elevation is genuinely unavoidable**, do not silently build around it — report: (1) the exact
operation, (2) why it is technically necessary, (3) the permission required, (4) lower-permission
alternatives, (5) what is lost by taking the safer option.

**Known violation to fix:** the Windows installer self-elevates via UAC and writes to
`HKLM` + `Program Files`. It should install **per-user** (`%LOCALAPPDATA%`, `HKCU`) with no
elevation.


## 15. Floating point (T12)

`dasham` (दशम) declares a scalar IEEE-754 binary64 float. Decimal literals (`1.5`, `0.05`)
work, as do mixed integer/float `+ - * /`, float comparisons in `yadi`/`yavat`, typed `dasham`
parameters and float returns (`examples/93_t12_float_functions.sm`), `kosh dasham` (§16), and
printing via `likha` with six decimal places. There is no scientific notation in literals (`1e5`
is refused), and a literal needs digits on both sides of the point: write `0.5` and `5.0` - `.5` and `5.`
are syntax errors (reported at the next line).

**Whole numbers stay whole until a `dasham` is involved.** `dasham d = 7 / 2` is `3.000000`: `7 / 2` is
integer division (3), then the 3 is stored. Write `7.0 / 2` or `7 / 2.0` for 3.5. The same with variables:
`vitti i = 7; dasham d = i / 2` is 3.000000, `i / 2.0` is 3.500000. One `dasham` operand makes `+ - * /`
and the comparisons work in `dasham`: `2 + 0.5` is 2.5, and `vitti i = 3; dasham d = 3.0; d == i` is 1.

**`%`, `&`, `|`, `^`, `<<` and `>>` are whole-number operators (v282).** With a `dasham` operand they are
refused: `Sutram truti [E_DASHAM_KRIYA]: dashama-sankhyayam % & | ^ << >> kriyah na sambhavanti`. Up to
v281 they ran on the number's bits: `5.5 % 2.0` printed `6192449487634432`. (For `%` and `%=` the error gives the line and a
caret; for `& | ^ << >>` only the file - those operators carry no position yet.)

**A `dasham` is binary, not decimal.** `0.1 + 0.2` prints `0.300000`, but `0.1 + 0.2 == 0.3` is 0: neither is
exactly representable, and the sums differ in the 17th digit. Compare with a tolerance. A whole number up to
2⁵³ (9007199254740992) is exact; a `vitti` larger than that rounds when stored in a `dasham`, and
`9223372036854775807` becomes 2⁶³ - which no longer fits a `vitti`, so storing it back stops the program
(`E_DASHAM_VITTI`).

**A fraction needs `dasham`, not `vitti` (v279).** `vitti` holds whole numbers only:

```sutram
mukhya() {
    vitti f = 3.5        # refused: E_DASHAM_VITTI - the .5 would be lost
    dasham g = 3.5       # right: likha(g) prints 3.500000
}
```

A **written** fraction (or a written float too large for a `vitti`) stored in a `vitti` — in a declaration
or an assignment — is refused with `E_DASHAM_VITTI` at the number. Up to v278 `vitti f = 3.5` silently held 3.

**A computed `dasham` stored as a whole number must be whole (v281).** When the program runs, a `dasham`
value stored in a `vitti`, pushed into or stored in an integer `kosh`, passed as an integer argument, or
returned from `mukhya` is checked: a whole number that fits converts exactly (`dasham x = 2.0; vitti a = x`
is 2, and `-0.0` is 0); anything else — a fraction, `inf`, `-inf`, NaN, or a value beyond the `vitti`
range — stops the program:

```
Sutram truti [E_DASHAM_VITTI]: dashama-phalam purnanka-seemayam na bhavati
```

exit 1, before the value is stored (`examples/112_t18_kosh_integer_conversion.sm`,
`examples/295_r92_computed_fraction_into_vitti.sm`). Up to v280 the value was truncated toward zero,
silently (`dasham d = 3.7; vitti i = d` gave 3). The message does not yet give the line. To take the whole
part of a `dasham` on purpose, round it yourself first — the library does: `madhava_sin` computes
`trunc(x / 2PI)` as a `dasham` with `(m + 2^52) - 2^52`, and `roop_sthir` the same way.

**How `likha` prints a `dasham` (v279).** Six decimal places, rounded, for every value below 2⁶³
(9.2×10¹⁸) — `10000000000000.0` prints `10000000000000.000000`. From 2⁶³ up it prints
`d.dddddde+N` (`1.234568e+22`). Infinities print `inf` and `-inf`; NaN prints `nan`.
`examples/289_r87_float_print.sm` pins the printer.

**Reading `e+N`.** `1.000000e+80` means 1.000000 × 10⁸⁰: a 1 followed by 80 zeros. `1.234568e+22` is
1.234568 × 10²², about 12 345 680 000 000 000 000 000. The seven digits shown are the number's first seven,
rounded; the rest are not printed (a `dasham` holds only about 16 significant digits anyway). A negative value
keeps its sign: `-1.500000e+19`. So squaring `100000000000000000000.0` (10²⁰) twice prints `1.000000e+80`.

| value | prints |
|---|---|
| `3.5` | `3.500000` |
| `10000000000000.0` (10¹³) | `10000000000000.000000` |
| `9000000000000000000.0` (just below 2⁶³) | `9000000000000000000.000000` |
| 10²⁰ squared twice (10⁸⁰) | `1.000000e+80` |
| `0.0 - 15000000000000000000.0` | `-1.500000e+19` |
| `0.0000001` (below half of the sixth decimal) | `0.000000` |
| overflow past the largest `dasham` (about 1.8 × 10³⁰⁸) | `inf` |
| `0.0 - 0.0`, and a tiny negative such as `0.0 - 0.0000001` | `0.000000` (no minus sign) |

**A tiny number prints as `0.000000` but is not zero.** `0.000000001` squared five times is about 10⁻²⁸⁸:
`likha` prints `0.000000`, `s == 0.0` is 0, and `1.0 / s` is `1.000000e+288`. Six decimals show the value
to the nearest millionth, no more.

**Where `inf` and NaN come from (v280).** Not from division by zero, which stops the program. `inf` comes from
overflow: `100000000000000000000.0` squared four times is `inf` (1.0 × 10²⁰ → 10⁴⁰ → 10⁸⁰ → 10¹⁶⁰ → `inf`).
NaN comes from `inf - inf`, `inf * 0.0` and `inf / inf`. `1.0 / inf` is 0. `inf` compares as an ordinary
number - `inf == inf` and `inf > 0.0` are 1 - and `-inf` is below every number. `inf` and NaN are 8 bytes like any
`dasham`: they go into and out of a `kosh dasham`, a function and a `mandapa` block unchanged (R94,
`evidence-r94`). Stored in a `vitti` they stop the program (`E_DASHAM_VITTI`).

**Dividing a `dasham` by zero stops the program (v280)** — `0.0` or `-0.0`, written or computed — with
the same message as for `vitti`: `Sutram truti [E_SHUNYA_BHAJAN]: pankti 8 - shunye vibhajanam na
sambhavati`, exit 1 (`examples/293_r90_float_divide_by_zero.sm`). Up to v279 it gave `inf`, `-inf` or
`nan` and carried on. A `dasham` can still become `inf` by overflow (`x * 10.0` repeated) and NaN from
`inf - inf`.

**Comparisons with NaN follow IEEE 754 (v280):** every comparison with NaN is false except `!=`, which is
true — so `n != n` is true exactly when `n` is NaN. Up to v279, NaN compared equal to every number and below
it (`n == 5.0` was 1). `examples/291_r90_nan_compare.sm` pins all six operators.


## 16. Growable arrays (T18) — `kosh`

`kosh name[capacity]` declares a growable mala (Devanagari `कोश`); capacity is optional and
defaults to 4. Logical length starts at 0 and `a[index]` reads/writes against that length.

| builtin | meaning |
|---|---|
| `kosh_kship(k, v)` (was `kosh_push`) | append v; returns the new length |
| `kosh_hri(k)` (was `kosh_pop`) | remove and return the last element |
| `kosh_gan(k)` (was `kosh_len`) | logical length |
| `kosh_ksham(k)` (was `kosh_cap`) | current capacity |
| `kosh_shodh(k)` (was `kosh_clear`) | set the logical length to 0 (storage NOT erased); returns 0 |
| `kosh_rikt(k)` (was `kosh_empty`) | 1 if length is zero, else 0 |
| `kosh_iksh(k)` (was `kosh_peek`) | **one argument:** the last element - the one `kosh_hri` would take next - **not removed**. A stack's *peek*: the top |
| `kosh_yuj(k, v)` (was `kosh_enqueue`) | append v; returns the new length (the same builtin as `kosh_kship`) |
| `kosh_apanay(k)` (was `kosh_dequeue`) | remove and return the first (oldest) element — FIFO, O(n) |

The old names still work and compile to the same bytes (§4b). **`kosh_iksh` takes no index** (`kosh_iksh(k, 0)` is a
grammar error, `vyakaran dosh`): **the element at any position is `k[i]`**, bounds-checked like every `kosh` read
(past the length it stops with `mala ank seema atikram`). So the top of a stack is `kosh_iksh(k)` and the front of a
queue - what `kosh_apanay` would take - is `k[0]`. On an empty `kosh`, `kosh_iksh` stops the program with
`Sutram truti: riktat koshat kosh_peek` (that run-time message still names the old spelling: it is compiled into
the program, R111-00). Measured on v292: `evidence-r112/kosh-iksh-v292.txt`.

Full specification, measured behaviour, and the `kosh` vs `suchi`/`queue`
comparison: `docs/reports/KOSH-BUILTINS.md`.

Capacity doubles on growth. Empty `kosh_pop` / `kosh_peek` / `kosh_dequeue` (`kosh_hri` / `kosh_iksh` /
`kosh_apanay`) abort with their own diagnostics — `Sutram truti: riktat koshat kosh_pop`,
`Sutram truti: riktat koshat kosh_peek`, `Sutram truti: riktat koshat kosh_dequeue` — and exit
1. Element types: integer (`kosh v`, the default) or binary64
(`kosh dasham d`). `push`/`pop`/the builtins take a direct kosh variable.

### Two names for one `kosh`: `vitti a = k` is not a copy (v278; the names stay one from v302)

**`vitti a = k` (or `a = k`) makes a second name for the same `kosh`, not a copy.** Both names read and write
the same cells, however the `kosh` grows.

**From v302 (R127) a `kosh` is a descriptor that never moves.** It holds the length, the capacity and the
address of the elements; every name of the `kosh` holds the descriptor. When the `kosh` grows past its capacity
its elements may move - into the arena while they are small, into a region of their own past 64 KiB - and the
descriptor is updated, so every name sees the move. A region is reserved, not committed (only the pages used
cost, on Linux and on Windows), and when a `kosh` outgrows it the elements move to a larger one and the old
region is given back.

```
mukhya() {
    kosh k[1]
    kosh_kship(k, 41)
    vitti a = k
    vitti obstacle = nirmmita(64)     # something allocated in between
    kosh_kship(k, 42)                  # k grows - its elements move, the descriptor does not
    k[0] = 99
    likha("a[0]=", a[0], " k[0]=", k[0])
    a[0] = 7
    likha("a[0]=", a[0], " k[0]=", k[0])
}
```

prints, on Linux and Windows (`examples/288`, which pins it):

```
a[0]=99 k[0]=99
a[0]=7 k[0]=7
```

- **No count limit any more:** up to v301 each `kosh` took a 64 MiB region; from v302 a small `kosh` is a 32-byte descriptor in the arena and its elements (20,000 koshes: one `mmap`). **The descriptor:** four 8-byte words - `[d-16]` length, `[d-8]` capacity, `[d]` the elements' address, `[d+8]` the size of the region they are in (0: the arena); a program that makes a `kosh` inside a `mandapa` puts three more words before them in every `kosh` (R82's line, slot and generation): **56 bytes** (`src/r65_arena.inc`; measured by `parimana()`, gate `R158 doc currency`). How many a program can make is still bounded by memory and by the compiler's own capacities.
  Up to v301 each `kosh` was a 64 MiB region of its own, so a program under a 1 GiB address limit could make about
  15, and a second name parted from the `kosh` at 4,194,305 numbers; up to v283 it parted whenever something had
  been allocated after the `kosh`.
- **What it costs:** a `kosh` that grows past something allocated after it leaves its old (small) elements in the
  arena, which is never reused - at most about as much again as the `kosh`, under 64 KiB; `parimana()` counts them.
  A read is one more load, from the same cache line (200 million `k[i]`: 552 ms, 601 ms on v301).
- **When memory runs out**, making or growing a `kosh` stops the program with `Sutram truti: kosh rachayitum
  smritih na labdha` / `kosh vardhayitum smritih na labdha` (exit 1); the `kosh` is not left half-grown.
- **A slice of a `kosh` is not kept in a name** (`vitti s = k[1:4]` is `E_KOSH_VIBHAG`): its element address is
  the elements' address when it was made, and a later `kosh_kship` may move them. Pass the slice on directly -
  `f(k[1:4])` - as before. **A slice is not given to a foreign function** (`--ffi`; v314, `E_KOSH_VIBHAG`): v313
  passed the address of the slice's descriptor - two words, its elements' address and its length - not its elements,
  so the C side summed those words (it printed `139676486729762`), and given as an `i64` count it crashed
  (segmentation fault, exit 139; Muse's reading, R151; run in R152, `Claude-to-Sarvam/evidence-r152/ffi-shape.txt`). Pass the `kosh` itself - its elements' address,
  valid until it next grows - and the bounds as numbers. Earlier versions of this page said a slice's elements went
  to a `ptr` parameter; that was not what the compiler did.

### A `kosh` parameter can grow (v304, R129)

**A `prakriya` may `kosh_kship` onto its `kosh` parameter, and the caller sees the growth:**

```
prakriya jod(kosh k, v) {
    kosh_kship(k, v)
    nivartanam kosh_gan(k)
}
mukhya() {
    kosh kk[1]
    chakra i = 1 tak 10 {
        jod(kk, i)
    }
    likha(kosh_gan(kk))        # 10
}
```

Up to v303 this was refused (`kosh-tarke kosh_push asamarthitam`): before v302 a parameter held the elements'
address, which a growth could move, leaving the caller on the old ones. From v302 every name of a `kosh` - a
parameter too - holds its descriptor, so the growth is the caller's, as it is an alias's.

**One thing it rules out: a slice of a `kosh` given to a `prakriya` that may grow a `kosh`** (it, or a `prakriya`
it calls, runs `kosh_kship`), or given beside another argument that has a call in it. A slice holds the
elements' address as they were when it was made; a growth would leave it behind. Both are `E_KOSH_VIBHAG`. Give
such a `prakriya` the `kosh` itself; give a slice to one that only reads. **The same holds through a function
value** (v307, R133): `vitti f = badal` then `f(k[0:1], kosh_kship(k, 8))` is `E_KOSH_VIBHAG`. A function value's
target is not known when compiling, but it can reach a `kosh` only through its arguments (a whole `kosh` is never
given to one, `E_KOSH_DVARA`), so the rule for it is the argument-order one: no argument with a call beside the slice.
`f(k[0:1], 5)` was allowed in v307. **From v308 (R134) a slice of a `kosh` goes through no door a `kosh` may not:**
a cell or field, a module `vitti`, another `kosh`, a raw store, an untyped parameter - and so no function value,
whose parameters are untyped. A `vibhag` parameter keeps the kind: `prakriya rakh(vibhag s, m) { m[0] = s }` is
refused. All are `E_KOSH_VIBHAG`. To keep values, copy them; to share them, pass the `kosh`.

**A slice is not a number** (v309, R137). Its value is the address of a two-word descriptor, so no operator takes
one - `+ - * / % == != < <= > >= & | ^ << >> && ||`, unary `-` and `!` - nor a condition (`yadi`, `yavat`, `?:`),
a loop bound, an index, a builtin other than `pankti_gan`, a cell or raw store, or an untyped or function-value
parameter: `E_VIBHAG_ANKA`, for a `mala`'s slice as for a `kosh`'s. A slice is used as the argument for a `vibhag`
parameter, in `pankti_gan(s)`, as the base of `s[i]` and `s[a:b]`, and (a `mala`'s) as a name's value. A `kosh`
made a number by a call or `?:` (`dek(k) + 1`) is `E_KOSH_GANIT`, as `k + 1` is. The same holds in a module-level `vitti` initializer (v310), and
a `kosh` cannot be a module `vitti`'s initial value there either (`E_KOSH_DVARA`). From v311 the check is part of
expression code generation itself: an expression reached by any other path is checked there, its own value as a number.
**Size limits (v315, R154).** Two limits are about size, and from v315 each has its own code and names the other
(they are not the only capacities - block nesting, the walk's own stack and others have theirs; v314 claimed both
named themselves, but the tree limit had no code):
- **the syntax tree**, 3 MiB - at most 43,690 nodes for the whole program, the libraries `yoj` brings in included.
  When it is full: `Sutram truti: vakya-vriksh seema atikram` (the line the language packs translate), then
  `Sutram truti [E_VRIKSHA_SEEMA]: ... iyam vakya-vriksha-seema, na parikshana-seema (E_VAKYA_SEEMA)` - the syntax
  tree's limit, not the analysis limit; `--analysis-steps` does not help. **Make the program smaller:** bring in
  fewer modules, or split the program into separate programs. Splitting a statement does not help - it does not
  make the tree smaller (v314 advised it; that was wrong). One `z + z + ...` expression of 21,829 terms fits.
- **the expression check's budget**: the steps the check may take on one statement or initializer (one step per
  node and per field of a node that is not one). **Default 200,000**; for one compile, **`--analysis-steps=N`**,
  `N` from 1 to 2147483647, written as one argument with `=` (leading zeros are decimal; a sign, a unit, a
  fraction, a space, a second `--analysis-steps` or the value in the next argument are refused,
  `E_PARIKSHA_PADANI`). The count starts again at `N` for every statement and initializer. When it runs out:
  `Sutram truti [E_VAKYA_SEEMA]: vakyasya parikshanam N padeshu na samaptam (parikshana-seema) - prakriya 'f'`
  (or *mukhya athava vaishvika-arambhah*), with the advice to split the statement (keeping intermediate values in
  names) or raise `--analysis-steps`, and that the syntax tree's limit (`E_VRIKSHA_SEEMA`) is separate. There is no source line: the
  check sees the statement after parsing, where positions are not kept (only `--debug` keeps them).
- **How many steps a statement takes** depends on its shape, not only its terms: `z + z + ...` takes 4 a term
  plus a few, `(z < z) + ...` 8. The widest measured shape - one `z + z + ...` of 21,829 terms, the most the tree holds of that shape (`tests/r143/test_walk_budget.py`) - takes exactly 87,316 (`--analysis-steps=87315`
  refuses it, `87316` compiles it); no measured statement reaches the default. 349,521 is an upper bound for any
  statement the tree holds, not a statement anyone has built: whether a shape above 200,000 can be written is not
  established (if one is, raise the flag for it). The largest statement in
  the example programs (`examples/*.sm` and `examples/*/*.sm`: 344 files, the set gate `R143 walk budget` compiles)
  and the 310 library functions takes 52 steps (`lib/brihat.smlib`, line 174; measured at v312, R144).
- **History:** v311 200,000 fixed; v312 65,536 (16,384 terms of `x + x + ...` compile and 16,385 refuse - measured natively on Windows against the
  v312 baseline, `Windows-to-Sarvam/win-v313-2026-11-08/BUDGET.md`, and relayed in Sarvam's ROUND-148); v313 349,521;
  v314 200,000 and the flag (ChatGPT R214-R217's contract). Gates `R143 walk budget` and `R152 analysis steps`.

**In `k[lo:]` the end is the length after `lo` is evaluated** (v305): `k[kosh_kship(k, 8) - 1:]` runs to the new end.
An explicit end is evaluated once, where it is written.

### A name keeps one kind (v301, R126) — `E_VITTI_PRAKAR`, `E_KOSH_DVARA`

**Inside a `prakriya` (or `mukhya`), a name keeps the kind its first binding gave it:** a `kosh`, a `kosh dasham`,
a `mala`, a `vibhag`, or a number / raw address (`vitti n = 3`, `vitti p = nirmmita(64)`, an untyped parameter, a
`chakra` counter). The compiler checks every `k[i]` by that kind - a `kosh` against its length at `[k-16]`, a
`mala` against `[m-8]`, a raw address not at all - so a name that could hold two kinds would be checked wrongly
on one of them. **Every later declaration or assignment of the name must give it the same kind:**

```
vitti a = k            # a is a kosh
a = nirmmita(64)       # E_VITTI_PRAKAR: 'a' kosh asti; sankhya ... tasyam na sthapyate
```

- **The rule ignores control flow on purpose.** `vitti a = p` and then `yadi (x == 1) { a = k }` is refused even
  if the branch never runs: no path decides a name's kind, so the kind is the same at every point of the
  `prakriya`. A `vitti` declared with a number (`vitti w = 0`) is a number; declare it from a collection of the
  kind it will hold (`vitti w = u`), or use another name. Two `prakriya` may use one name for two kinds.
- **A `kosh` goes only where its kind goes with it:** by its own name (`vitti b = k`, `vitti b = (k)`, `b = k`,
  chains of these), to a `kosh` parameter (`prakriya f(kosh k)`), as the first argument of a `kosh_*` builtin, and
  back from a `prakriya` that returns a `kosh` parameter or a `kosh` it declares, **by its own name, on every
  `nivartanam`** - then `vitti a = f(k)` makes `a` a `kosh` and `a[i]` is bounds-checked. Everything else would
  turn it into a raw number and is **`E_KOSH_DVARA`**: a `kosh` stored in a `mala` cell, a field or a module
  `vitti`; passed to an untyped parameter or through a function value; given to a raw builtin (`likha(k)`,
  `pad8(k)`, `likh8(p, k)`, `kosh_kship(j, k)`); in `?:`; as a `siddhi` / `dosh` value; or returned by a second name or on only some paths.
  `k + 0`, `k - 0` and `k * 1` are `E_KOSH_GANIT`, as `k + 8` is.
- **Not covered:** a foreign function (`--ffi`, a `ptr` parameter) receives a `kosh` as its raw address, by
  design; and a `prakriya` compiled in another object (`--object`, `--separate`) is assumed to return a number.

Up to v300 the compiler marked a name only from a bare variable, never cleared the mark and did not see control
flow: `examples/348`-`350` crashed (SIGSEGV) or read past a `kosh`'s length; they are refused now.

## 17. Function values, methods and slices (R23)

The smallest working version of each; what is not done is listed at the end.
Examples: `examples/246_r23_comparator_sort.sm`, `247_r23_methods.sm`, `248_r23_slices.sm`.

### Function values

A `prakriya` name used as a value is the function: it can be stored in a
variable, passed as an argument, returned, kept in a `mala`, compared with `==`.
A variable that holds one is called like a function.

```
prakriya aarohi(a, b) { nivartanam a - b }
prakriya shreni(vibhag s, tulana) { ... yadi (tulana(s[j], v) > 0) { ... } ... }
shreni(x, aarohi)          # pass it
vitti f = aarohi           # store it
likha(f(10, 3))            # call through it: 7
```

- **A call `name(...)` calls the `prakriya` called `name` if there is one;** only
  otherwise does it call through a variable `name`. So a parameter that has the
  name of a function does not hide it: name such parameters differently.
- **A call through a value is not checked:** not its number of arguments, not that
  the value is a function. A function returning `dasham` must not be called
  through a value (its result is read from the integer register).
- **No closures:** a function value is a code address. Nothing is captured.

### Methods

`prakriya Rachana.naam(swa, ...)` declares a method of a `rachana`; `x.naam(...)`
calls it with `x` as the first argument (`swa` is a name like any other).

```
rachana Bindu = { x, y }
prakriya Bindu.chal(swa, dx, dy) { swa.x = swa.x + dx  swa.y = swa.y + dy  nivartanam 0 }
p.chal(3, 4)               # Bindu.chal(p, 3, 4)
```

- **A method is found by its name, as a field is** (variables carry no type): a
  method name must belong to one `rachana` only. `x.naam()` with no such method is
  `[E_UNKNOWN_FIELD]`; with two is `[E_AMBIGUOUS_FIELD]`; the wrong number of
  arguments is `[E_ARITY]` on `Rachana.naam`.
- The `rachana` must be declared before its methods; methods, like every
  `prakriya`, are written before `mukhya`.
- **No traits, interfaces or overriding.** A call `x.naam()` does not check that x
  is a `Rachana`.

### Slices

`a[lo:hi]` is a view of the elements `lo .. hi-1` of a `mala`, an integer `kosh`
or another slice. **Nothing is copied:** a write through the slice changes the
array. `a[lo:]` runs to the end, `a[:hi]` starts at 0, `a[:]` is all of it.

```
prakriya yog(vibhag s) { ... pankti_gan(s) ... s[i] ... }
likha(yog(a[2:5]))         # elements 2, 3, 4
vitti s = a[1:7]           # s is a slice: s[0] is a[1]
likha(yog(a))              # a whole mala or kosh is passed as a[:]
```

- **Checked twice at run time:** when made (`0 <= lo <= hi <= length`) and when
  indexed (`s[i]`, `s[i] = v` against the slice's own length), with the array
  bounds diagnostic, exit 1.
- **`vibhag` (Devanagari `विभाग`, and a word in each pack) declares a slice
  parameter.** It takes a slice, or a whole `mala` or integer `kosh`; anything
  else is a compile error (`vibhag: mala, kosh va vibhag apekshita`), as is
  slicing a raw pointer (an untyped parameter, a `nirmmita` result).
- **A variable is a slice when it is declared from one** (`vitti s = a[1:3]`,
  `vitti t = s`) or is a `vibhag` parameter.
- **A slice lives in the frame of the function that makes it:** returning one is a
  compile error (`vibhag prakriyayah na pratyarpaniyah`). A slice made at one place
  in a loop is the same slice each time round (the next iteration remakes it).
- `pankti_gan(s)` is the slice's length.

### Not done in this version

Closures; calling an expression directly (`t[0](x)`, `p.f(x)` through a field:
store it in a variable first); a checked type for function values; methods
dispatched on the object's type, traits; slices of a `kosh dasham`; a slice that
outlives its function. (Up to v301 a `kosh` that grew after a slice of it was made left the
slice pointing at the old storage; from v302 a slice of a `kosh` cannot be kept in a name,
`E_KOSH_VIBHAG` - pass it on directly.)

## 18. The error type: `siddhi`, `dosh`, `prasar` (R25)

The smallest working version. Example: `examples/249_r25_phal.sm`.

```
prakriya bhaj(a, b) {
    yadi (b == 0) {
        nivartanam dosh(1)            # failure, carrying the code 1
    }
    nivartanam siddhi(a / b)          # success, carrying the value
}
prakriya ek_adhik(a, b) {
    vitti q = prasar bhaj(a, b)  # failure: returned from here at once; success: q is the value
    nivartanam siddhi(q + 1)
}
mukhya() {
    likha(prasar ek_adhik(10, 2))    # 6
    likha(prasar ek_adhik(10, 0))    # the failure reaches mukhya: the program exits with status 1
}
```

- **A prakriya with a `nivartanam siddhi(...)` or `nivartanam dosh(...)` is a phal-prakriya.** In one, every `nivartanam` is
  `siddhi` or `dosh` (a plain `nivartanam` is a compile error), and falling off its end is `siddhi(0)`.
- **A phal-prakriya must be called under `prasar`**, and `prasar` must be on a call of one: a failure cannot
  be ignored, and a status is never read where none was set. Both are compile errors otherwise.
- **`prasar` is allowed in a phal-prakriya (it propagates) and in `mukhya`**, where a failure ends the
  program with the code as its exit status (the low 8 bits). `nivartanam dosh(c)` in `mukhya` exits with `c`.
- **No heap:** the value or the code travels in `rax`, the status in `rdx`.
- Methods can be phal-prakriyas (`prasar p.ghata(4)`).

**Catching a failure (R26):** `yadi dosh (q = f(...)) { ... } anya { ... }` calls the phal-prakriya `f`.
On failure the first block runs with `q` = the code; on success the `anya` block (optional) runs with `q` =
the value. The failure goes no further, so recovery is possible anywhere, in any prakriya or in `mukhya`.
`q` is declared by the handler if it is new and stays visible after it. Example: `examples/250_r26_dosh_handler.sm`.

```
prakriya padh_ya(s, mool) {          # never fails: a bad number counts as the default
    yadi dosh (q = sankhya_padh(s)) {
        nivartanam mool
    }
    nivartanam q
}
```

**Not in this version:** keeping a
result in a variable (it is consumed by `prasar` where it arrives); typed results (`phal<T>`); calling a
phal-prakriya through a function value (the status is not checked there); `dasham` values in a result.

## 19. `mandapa` — the scratch block

**What it is for:** *a `mandapa` holds the temporary buffers of one piece of work. Every `nirmmita` written inside
it is given back, all at once, when the block ends — so work that allocates in a loop does not grow the program.*

### Form

```sutram
mandapa                      # the keyword, then an indented body
    vitti t = nirmmita(3 * 8)
    ...

mandapa {                    # braces are allowed
    ...
}

mandapa likha(x)             # one statement on the keyword's line
```

The Devanagari spelling is `मण्डप`. The body follows the same rules as every other body (§6a-2). A `mandapa` is a
statement; its variables are scoped to it, as in any block. Blocks nest, and may sit in loops, in `prakriya`
bodies and in recursion.

### Example

```sutram
prakriya madhya(a, b, c)            # the middle of three numbers
    mandapa
        vitti t = nirmmita(3 * 8)   # scratch: three numbers
        t[0] = a
        t[1] = b
        t[2] = c
        # ... sort t ...
        nivartanam t[1]             # a NUMBER read from scratch: allowed
    nivartanam 0
```

### What it holds in v1.0

**Scalar scratch: `nirmmita` buffers of numbers, used inside the block.** Read the numbers out freely — into a
variable, a `mala`, a `kosh`, a buffer made outside, a return value. That is how results leave a block.

**Not a `kosh` of pointers.** **A `kosh` — made inside the block or outside it — cannot be relied on to hold an
address made in the block.** Putting one in directly (`kosh_kship(k, buf)`, `k[i] = buf`) is refused; the one way
it gets in unseen is through a `prakriya` that hands the address back (below). A `kosh` of *numbers* used in a
block works; its storage is ordinary memory, which the block does not reclaim.

### Run time

- **Entry** remembers the scratch cursor. Each `nirmmita` inside takes memory from the scratch side of the
  program's 1 GiB field, zeroed, like any `nirmmita` buffer.
- **Every exit gives it all back:** reaching the end of the body, `nivartanam`, `krama`, `agrim`, and a failure
  passed on by `prasar`. A later block reuses the same memory, and sees zeros, never the earlier block's data.
- **A negative size** is an error: written as a number (`nirmmita(-1)`), the compiler refuses it —
  `E_NIRMMITA_RNA`; computed (`nirmmita(n)` with `n` below 0), the program stops, exit 1:
  `Sutram truti: nirmmita-parimanam rnatmakam - mandapa-madhye rnam parimanam na sambhavati`. (Outside a block, and in
  a Windows program, a computed negative size still gives 0.)
- **Measured (Linux x86-64, v270/v271):** 1,000,000 × `nirmmita(64)` in a loop — **264 KB** peak with the block,
  **62 MB** without it. A `kosh` outside the block filled with 1,000,000 numbers from inside it: **7.8 MB** (the
  `kosh` itself) against **78 MB** without the block. A block recursing 1,000 deep, 1,000 times: **2 MB**
  against 64 MB.
- **Pages are reused, not returned:** a block that touched 100 MB keeps those 100 MB resident; the next block
  uses them again.
- **More than the field holds** stops the program, exit 1:
  `Sutram truti: kshetra purnam - mandapa-smritih samapta` (*the field is full — the block's memory is used up*).
- **Linux and Windows** (Windows from v299, R123). In the `GUARD_PAGES` diagnostic build a `mandapa` is an
  ordinary block: everything works, nothing is reclaimed. **On Windows, from v300 (R124), it commits only what it touches,** as Linux does: the runtime reserves the arena and each `kosh` region, and commits 64 KiB at a time where the program first touches it (one `nirmmita(64)`: about 0 MB; it was 1 GiB in v299, and 64 MiB per `kosh`).

### What the compiler refuses — `E_SCRATCH_ESCAPE`

A scratch address — a `nirmmita` result inside the block, or that address plus or minus a number, or a copy of
it — must not outlive its block:

| | |
|---|---|
| **1. into a variable declared outside the block** — `outer = buf + 64`, and into a module `vitti` (`g = buf`), wherever in the file it is declared | refused |
| **2. into memory** — `bahar[i] = buf`, a raw buffer's cell, `likh`, `likh8`, `kosh_kship` — wherever the call is written: a statement, an initializer, an argument, a condition | refused |
| and out by `nivartanam` — plain, `siddhi(...)`, `dosh(...)` | refused |
| into a variable of the same block or a deeper one | allowed |
| a number read from scratch (`buf[i]`, `akshar(buf, i)`), anywhere | allowed |

A name that has held a scratch address keeps that mark until its block ends, even after `q = 7`: the compiler
does not work out which branch ran. Use a fresh name for the number. **Loops are checked as loops:** a value
that only becomes an address on a later pass (`outside = q` written above `q = buf` in the same loop) is
refused too.

### What it does not see

**An address passed to a `prakriya` that keeps it** — stores it somewhere, or returns it, so that the caller
can put it in a `kosh` or a variable. Those programs compile and are wrong: they read memory a later block reuses. Every
`E_SCRATCH_ESCAPE` message ends with a `Sanket` line that says so. **So a program that compiles is not proved
safe: the check refuses the escapes above, and no more.**

**Rule: pass a scratch buffer to a `prakriya` to be read or written, never to be kept.** A `prakriya` that
returns a number computed from the buffer (`yoga(buf, n)`) is fine.

### What it is not

Not a way to manage memory that a `kosh` grows into, and not a way to reclaim what a called `prakriya` allocates:
the block covers the `nirmmita` written inside it, in its own text. For when the block helps and when it does
not, see `docs/decisions/MEMORY-DECISION.md`.

### A `kosh` made inside the block (v278)

**A `kosh` declared inside a `mandapa` lives as long as the block.** Inside it, use it as any `kosh` — push,
grow, index, pass it to a `prakriya` — and give back a value (`examples/286`).

**From v289 the compiler refuses a `kosh` that would leave its block** - stored in a variable declared outside
it, written into memory (`kosh_kship(outer, k)`, `m[i] = k`), or returned - with the compile-time form of the same
error (`examples/287`):

```
Sutram truti [E_KOSH_MANDAPA]: mandape rachitah kosh mandapat bahih na gacchati - bahya-vittau na sthapyate
Sanket: kosh mandape eva upayujyatam (k[i], kosh_gan(k)), mulyam nivartyatam; bahih avashyakah cet mandapat purvam rachyatam
```

*(a kosh made in a block does not go outside it - it is not put in an outer variable; use it inside, return the
value; if it is needed outside, make it before the block)*. These are the scratch-escape rules (`E_SCRATCH_ESCAPE`,
above) applied to the `kosh` itself.

**From v290 a block's `kosh` may be given only to a `prakriya` that does not keep it** - one that reads its `kosh`
parameter (`k[i]`, `kosh_gan(k)`, passing it on to another such `prakriya`) but does not return it, store it, or
pass it to one that does. The compiler works this out for every `prakriya` and parameter of the program; a
function value or a foreign function counts as keeping. Otherwise (`examples/316`):

```
Sutram truti [E_KOSH_MANDAPA]: mandape rachitah kosh tam prakriyam na gacchati ya tam rakshati (nivartayati, sthapayati, anyatra preshayati)
```

**v291 (R109) closed two ways round it that v290 missed:** a second name - `vitti a = k` or `a = k`, then `rakh(a)` -
is the block's `kosh` too (`examples/320`); and the "keeps" analysis runs to the end however long the chain of
`prakriya`s is (v290 stopped after 32 rounds, so 33 keeping `prakriya`s, each passing it on, let it out:
`examples/321`).

So no reference to a block's `kosh` outlives the block. The runtime check below stays as a second line; no program
in the tree, and none written for its gate, can reach it any more. If one ever does, it stops the program with

```
Sutram truti [E_KOSH_MANDAPA]: prakriya 'padh' - kosh 'k' pankti 10 mandape rachitah; sa mandapah samaptah
Sanket: mandape rachitah kosh mandapat bahih na jivati - mandape eva upayujyatam, mulyam nivartyatam
```

*(the kosh made in the block on line 10 — that block has ended; use it inside the block and return the value)*,
exit 1. That holds however the block ended — at its end, by `nivartanam`, or by `krama` /
`agrim` out of a loop — and for an inner block ended inside a running outer one; the same block entered again
(the next turn of a loop) makes a new `kosh`, and the old one stays dead.

How: each such block takes a fresh generation on entry and clears it on exit; each `kosh` it makes records it;
a `prakriya` with a `kosh` parameter compares them on entry. **A `kosh` made outside every block is unchanged**,
and a program with no `kosh` in a block compiles to the same bytes as before. In a program with one, every
`kosh` carries three more header words and each call with a `kosh` parameter one check (+11% on a call whose
whole body is one `kosh` read; +3.5% on `kosh_kship`).

**Decided (R103, v285): the block does not take a `kosh`'s memory back; the `kosh` keeps it for the program's
life.** That is what keeps the check above exact: the check reads the `kosh`'s header, so the header must still
be there after the block. Giving the region back would make a dead `kosh` reaching a `prakriya` a crash (or,
if the address were reused, a silent read of another `kosh`) instead of `E_KOSH_MANDAPA` with its line - and
in the tree it would give back nothing: the three programs that make a `kosh` in a block (`286`, `287`, `299`)
peak at the same reading as a three-line program. **Measured (`tools/peak_rss.py`):** a block run 100,000
times that makes a `kosh` of 100 numbers peaked at **about 100 MB** on v283, at **400 MB** on Linux from v284 to
v301 (each `kosh` then had its own region, one 4 KB page at least), and at **106,240 KB** on v315 (`/usr/bin/time`;
from v302 a small `kosh` is a 32-byte descriptor in the arena with its first elements after it - section 16) - the
same as without the block.
The block bounds `nirmmita` (10,000,000 `nirmmita(64)`, one block per pass: under 1 MB; without blocks: 625 MB),
not `kosh` storage. Make a `kosh` that is reused once, outside the loop, and empty it with `kosh_clear` each
pass: 0 MB. Reading
the `kosh`'s address as raw memory (`x[i]` on a plain `vitti`) is not checked — as all raw memory (§6c). Under
`--separate`, a module compiled on its own checks its `kosh` parameters only if it has a `kosh` in a block itself:
the whole-program compile checks every `prakriya`.

### How much is in use: `parimana()` (v289)

**`parimana()` (*measure*; `परिमाण`) returns the bytes the program's allocations hold right now**, so a program -
and a test - can ask without a harness (`examples/317`):

```
start 0
after nirmmita(64) 64
in a block, nirmmita(1000) 1072
after the block 64
a kosh of 1000 8288
```

- **What it counts:** the arena's persistent side (`nirmmita` outside a block; each rounded up to 16), its scratch
  side (what the open blocks hold - it falls when a block ends), and each `kosh`'s header and capacity, 8 bytes a
  number (`kosh k[1]` grown to 1,000 has capacity 1,024: its 32-byte descriptor + 8,192 bytes = 8,224, so the last
  line is 64 + 8,224; until R161 this page said 16 + 8,192 and 8272, the figures before v302's descriptor). A `kosh` keeps its bytes for the
  program's life, so they never fall.
- **It is not the resident memory** the kernel reports: pages, the program's code and its stack are not in it, and
  a `kosh`'s capacity counts whether or not every page has been touched. It is what the program asked for.
- **Not counted:** a `nirmmita` that the arena could not hold (past 1 GiB it falls back to its own `mmap`).
- **Cost:** a program without `parimana` compiles to the same bytes; with it, each `kosh` allocation and growth
  adds one counter update. **Linux and Windows** (up to v298 a Windows program got 0).

**One number, moving (`examples/318`):** `parimana()` is the arena and the `kosh` regions together, so it answers
"how much am I holding" the same way for a program and for a test. A block's `nirmmita` comes back at its end; a
`kosh`'s bytes do not, even one made in the block - its storage is kept for the program's life (§16). The descriptor is stable from v302, so a second name can no
longer be left behind; what is still not done is giving a `kosh`'s storage back when its block ends - the check above reads
its header after the block, so the header must stay. (Until R162 this sentence said reclaiming waited for a stable
descriptor, which v302 delivered.)

### A budget: `mandapa parimita N` (v285)

**`parimita` (*measured, limited*) gives a block a byte budget.** The block's own `nirmmita` may use at most `N`
bytes in all; the one that would pass the budget stops the program **before it is given memory**:

```
mukhya() {
    mandapa parimita 1048576 {
        vitti i = 0
        yavat (i < 1000000) {
            vitti b = nirmmita(64)
            i = i + 1
        }
    }
}
```

```
Sutram truti [E_PARIMITA]: pankti 2 - mandape parimitat adhikam nirmmitam na sambhavati (parimitih 1048576 baait)
```

*(more than the budget cannot be made in the block; budget 1,048,576 bytes)*, exit 1 (`examples/303`). The
block refuses; it never grows. A block entered once per pass of a loop gets its budget each time, because it
gives its memory back at its end (`examples/304`).

- **`N` is a positive whole number written in the source**, in bytes. `mandapa parimita 0`, or a variable or an
  expression, is refused at compile time (`E_PARIMITA`, `examples/305`). `परिमित` is the same word.
- **What counts:** each `nirmmita` written inside the block, rounded up to 16 bytes as the arena does - so
  `nirmmita(32)` and `nirmmita(33)` together are 32 + 48 = 80 bytes. **Nested budgets all hold:** an inner
  block's `nirmmita` counts against every budgeted block around it, and an inner block that ends gives its bytes
  back to the outer one.
- **What does not count:** a `kosh` (its storage is the `kosh`'s, not a `nirmmita` written in the block - a small
  one is in the arena, a large one in a region, section 16), and what a called `prakriya`
  allocates - as the block itself covers only what is written inside it. `parimana()` (above) shows both.
- **`parimita` is not reserved.** It is a budget only between `mandapa` and a number; `vitti parimita = 7`
  still works.
- **Cost:** a program without `parimita` compiles to the same bytes as before. In a budgeted block each
  `nirmmita` gains one compare per budget around it.
- **Linux and Windows, as the block** (up to v298 a Windows program's budget was not checked).

**Measured (R103, `tools/peak_rss.py`, Linux):** 1,000,000 `nirmmita(64)` in one block -

| | peak memory | result |
|---|---|---|
| `mandapa parimita 1048576` (`examples/303`) | **1,024 KB** | `E_PARIMITA` at the 16,385th, exit 1 |
| the same budget, one block per pass (`examples/304`) | **0 KB** (the reading of a three-line program) | runs to the end, exit 0 |
| the same loop, `mandapa` without a budget | **62,464 KB** | runs to the end, exit 0 |

## 20. `parikshita` — a checked function (v277)

**Write `parikshita` before `prakriya` or `mukhya` and the compiler verifies the whole function: if it cannot
show that every memory access stays inside its block, the program is refused — not warned.**

```
parikshita prakriya agla(x) {
    nivartanam (x * 1103515245 + 12345) % 2147483648
}
parikshita mukhya() {
    mandapa {
        vitti p = nirmmita(12 * 8)
        ...                         # p[i] = agla(...) ; sort p ; likha(p[i])
    }
}
```

(`examples/282`.) In a checked function:

| allowed | refused |
|---|---|
| numbers, `dasham`, `yadi`, `yavat`, `kuru`, `chakra`, `mandapa`, `nivartanam`, module `vitti` | `kosh`, `rachana` fields (`p.x`), slices, function values, `prasar`, `yadi dosh`, inline assembly |
| calls to **other `parikshita` functions** | a call to any other `prakriya` — `E_APARIKSHITA_AHVAN`, at the call, naming it |
| `likha`, `likha_rup`, `grahan`, `nirmmita` | every other builtin: `dvaram_likha`, `likh8`, `pad8`, `akshar`, `akshar_rakh`, `smaran`, `shabda`, `kosh_*`, files … — `E_APARIKSHITA_KARYA` |
| `a[i]` on a `mala` declared in the function; `p[i]` where `vitti p = nirmmita(NUMBER)` and `p` is never assigned again — both checked against their size | `x[i]` on anything else — a parameter, `p + 8`, a size computed at run time — `E_APARIKSHITA_SMRITI` |

**The rule is transitive:** a checked function calls only checked functions, and each of those is checked
too, so everything a checked `mukhya` can reach has been verified. A refusal is reported at the first bad
edge (`examples/284`). An unmarked `prakriya` keeps today's behaviour exactly; an unmarked caller may call a
checked function with numbers. Under `--separate` the verdict is the same. A refused program writes no file.

**What it does not do yet.** A checked function cannot take a buffer as a parameter (nothing says how long the
block behind an address is), so a checked sort is one function. Run-time `+ - *` still wrap (§3a). A
`parikshita` prototype does not mark the definition; mark the definition. The library: **63 of its 306
functions** could be marked as they are (all of `ank`, `madhava`, `sadhan`; most of `ganit`, `chandas`,
`ganita`); none is marked yet, so a checked program calls none of them (`examples/283`).

## Printing a string variable (changed in v288)

**`likha` prints a string as its text - a literal, a variable, a concatenation, a string a `prakriya` returns.**

```sm
mukhya() {
    likha("hello\n")       # prints:  hello
    vitti s = "ab"
    likha(s, "\n")         # prints:  ab
    likha(s + "cd", "\n")  # prints:  abcd
}
```

**Up to v287 this was a trap:** `likha(s)` on a string variable printed its address (`4194454`), and a beginner
got a seven-digit number with no explanation. From v288 `likha` looks at what it is given: the compiler knows
which values are strings (section 5a), and prints those with the same code as `shabda`. A value that is not
known to be a string - a `mala` or `kosh` element holding one, a module-level variable - still prints as a
number; print it with `shabda(m[0])`.

