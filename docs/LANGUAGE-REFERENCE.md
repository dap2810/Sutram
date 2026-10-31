> **Status at v411, 29 October 2026 — read this before the page below.**
>
> **Compiler v261.** Suite **PASS=225** · crash corpus **227/0** · library proofs **226/226** · property proofs 86/86 · doc signatures PASS · layers 14/9/1 · alloc bounds 26 (13 bounded, 13 exempt) · built-in packs CURRENT · gates **48 PASS / 0 FAIL / 1 NOT-RUN**.
> **The NOT-RUN is Windows execution, and that is the owner's own test.**
>
> **`nivartanam` is the return keyword; `prati` is a legacy alias.** 235 files across compiler, `lib/`, `examples/`, `tests/` and `docs/` — **zero goldens changed**, and a program written either way compiles to a byte-identical binary.
> **Done and off every open list:** `likha` up to six values · 135 three-statement triples · the `lkhb` float bug · `arabhya ... paryantam` · **20 library names that described the wrong operation** · 7 wrong Devanagari words · 33 contract comments · Patch A's 12 variable names.
> **The authoritative page is `docs/WHATS-LEFT.md`.** Where this page disagrees with it, that page is right.
>
> **And the memory question is answered:** `nirmmita` emits **`mmap` per allocation** on Linux and **`VirtualAlloc`** on Windows, and there is **no `munmap` anywhere** — nothing ever returns memory. See `docs/MEMORY-MODEL.md`.

# Sutram — Language Reference

Generated from the compiler source and the language packs, so it cannot drift from the code.

**Compiler:** v29 source line · **Package:** v35 · patra extension `.sm`


## 1. Quick start

```sutram
mukhya()
    likha("Namaste, world!")
```

```sh
sutram hello.sm hello.bin && ./hello.bin     # Linux target
sutram hello.sm hello.exe                     # Windows target (name decides)
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
| `abhava` | negation |
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
| `vitti` | variable |
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
that while the program runs, the answer wraps around to the other end without any warning — as in C or Java —
so `x * x` with `x = 4000000000` prints `-2446744073709551616`. Dividing by zero stops the program with an
error.** In detail:

| | what happens |
|---|---|
| `+` `-` `*` past the range, **at run time** | wraps around, silently (checking every operation measured +5% to +282% on the benchmarks, so it is not done) |
| the same with **numbers written in the program** — `4000000000 * 4000000000`, `9223372036854775807 + 1`, `-(0 - 9223372036854775808)` | **refused when compiled**: `prog.sm:2:22: Sutram Error [E_ATIPRAVAH]: sthira-gananayah phalam 64-bit purnanka-seemam atikramati`, with the line and a caret under the operator |
| a **written whole number** too large — `99999999999999999999`, `9223372036854775808`, `0x10000000000000000` | **refused when compiled**: `... [E_ATIPRAVAH]: ankah 64-bit purnanka-seemam atikramati`. (`0 - 9223372036854775808` and `-9223372036854775808` are allowed: they are the smallest `vitti`.) A `dasham` literal may be larger: `100000000000000000000.5` is that number. |
| `/` or `%` **by zero** | the program **stops**: `Sutram Error [E_SHUNYA_BHAJAN]: pankti 3 - shunye vibhajanam na sambhavati` (for `%`: `shunyena sheshah na sambhavati`), exit 1. The line is in your file; inside a module it is that module's line and name: `pankti 3 (r80_ausat.smlib)`. **Written as `/ 0`, it is refused when compiled.** |
| `/` and `%` by −1 | the smallest `vitti` divided by −1 wraps to itself; `% -1` is 0 (before v276 this crashed; written as numbers, `(0 - 9223372036854775808) / (0 - 1)` is refused) |
| when you need to know | the library's checked arithmetic says whether the answer fits: `ganita_janchit_yuj` / `_nyun` / `_gun` (`ok[0]` is 1 or 0); `ganita_paripurna_*` stops at the largest or smallest `vitti` instead of wrapping |

The library's number functions do not wrap on ordinary inputs (v276): `kramgun` (factorial), `fib`, `matra_meru`,
`varg`, `vargit`, `dwi_ghat`, `yog_tak`, `meru`, `laghuttam_samapavartya` (lcm) and `purna_prasaran` (integer
variance) return **−1** when the answer is too large to fit; `ghat` (power), `ghan` (cube) and `yog_seema` (range
sum) return the largest or smallest `vitti`.

**Not yet right:** `likha` of a `dasham` of about 9223372036854.775808 (9.2×10¹²) or more, or that far below
zero, prints `-9223372036854.775808`, whatever the value — the printer scales by 10⁶ into a `vitti`.

Internal operator ids: `OP_ADD`=1, `OP_SUB`=2, `OP_MUL`=3, `OP_DIV`=4, `OP_EQ`=5, `OP_LE`=6, `OP_LT`=7, `OP_GT`=8, `OP_GE`=9, `OP_NE`=10, `OP_MOD`=11, `OP_AND`=12, `OP_OR`=13, `OP_XOR`=14, `OP_LAND`=15, `OP_LOR`=16, `OP_SHL`=17, `OP_SHR`=18


## 4. Built-in functions

These are the **actual** builtin names the compiler accepts, taken from its table.
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
| `pankti_len` | length of a constant-length `mala` mala |
| `likha` | 1–6 arguments: value(s) or raw three-argument write; see §4a (string literals do not append LF, numeric final values do) |
| `lkhb` | numeric output without LF; includes `dasham` numeric printing since R52 |
| `likha_fmt` | literal prefix plus integer followed by LF (no placeholder substitution; see §4a) |
| `shabda` | print a string variable |
| `grahan` | read a number from input |
| `sthagita` | halt the program |
| `dvaram` | patra descriptor helper |
| `paadh` | open a file |
| `band` | close a handle |
| `nirmmita` | allocate memory: `nirmmita(n)` gives `n` **bytes**, zeroed — `nirmmita(count * 8)` for `count` cells. Checked only when the size is a number and the name is never reassigned; otherwise writing past `n` bytes is your mistake, as in C (§6c) |
| `smaran` | fill memory |
| `smaran_cp` | copy memory |
| `vartani_aayam` | varna length |
| `vartani_tul` | varna compare |
| `vartani_cat` | varna concatenate |
| `vartani_pratilip` | varna copy |
| `akshar` | character code at an index |
| `aksharank` | character code (note: index currently ignored) |
| `char_from` | character from a code |
| `char_upper` | uppercase a character |
| `char_lower` | lowercase a character |
| `sankhya_yog` | integer add |
| `sankhya_gunan` | integer multiply |
| `sankhya_dot` | dot product |
| `netsock` | create a socket |
| `netbind` | bind a socket |
| `netlisten` | listen |
| `netaccept` | accept a connection |

### 4a. Output: print values, raw bytes, and formatting (compiler v257)

`likha` is overloaded. **A string literal prints its bytes exactly as written** (there is no automatic newline); **a scalar integer or `dasham` prints a value followed by a newline**. A string *variable* passed to ordinary `likha` prints its pointer value, not its contents; use `shabda(s)` for a NUL-terminated string variable.

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

**Three to six values (R52):** when *exactly three* arguments are supplied, the first must be a **string literal** to select multi-value output. Four to six arguments always use multi-value output. Numeric intermediate values do not add newlines; the last numeric value adds one.
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

**Raw write — `likha(fd, buf, len)` is a different THREE-argument operation:**
```sutram
mukhya() {
    likha(1, "raw\n", 4)
}
```
**Exact expected stdout** (`raw` plus LF, four bytes):
```text
raw
```
Here `1` is stdout's file descriptor; the second value is a byte-buffer pointer and the third is its byte count. **Do not assume all three-argument `likha` calls print three values.** The first argument's syntax determines the mode: a string literal means multi-value print; a nonliteral first argument means raw write. Keep existing raw-write calls unchanged.

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

**`likha_fmt(fmt, v)` — literal prefix + integer, not placeholder substitution:**
```sutram
mukhya() {
    likha_fmt("x = ", 42)
}
```
**Exact expected stdout:**
```text
x = 42
```
`likha_fmt` currently outputs the literal format/prefix string and numeric value sequentially. It does **not** interpret `{0}` or other format placeholders; its integer number path **already writes a final LF**. Therefore an extra `likha("\n")` gives an unwanted blank line. The existing `examples/format_demo.sm` has this extra newline; its golden records the blank lines. Do not edit either without running and updating acceptance.

**Evidence:** `src/sutram_compiler.asm:15956-15964,16144-16242,18050-18183`; `tests/r52/test_r52.py:55-74`; `tests/expect/43_nested_likha.out` and `tests/expect/format_demo.out`. Exact outputs are source/committed-test expectations, **NOT RUN by ChatGPT**.
## 4b. Standard library (`lib/`)

`yoj <name>` inlines `lib/<name>.smlib` into your program at compile time —
no runtime dependency, the code becomes part of your binary. `lib/` ships:

| module | include with | functions |
|---|---|---|
| ganit | `yoj ganit` | 15 — `varg`, `vargit`, `ghan`, `dvigun`, `trigun`, `vardh`, `nirapeksh_mulya`, `laghu2`, `adhik2`, `mahattam_samapavartak`, `laghuttam_samapavartya`, `ghat`, `kramgun`, `asti_abhajya`, `yog_tak` |
| ank | `yoj ank` | 10 — `asti_yugm`, `asti_visham`, `ank_gan`, `ank_yog`, `viparyay_ank`, `asti_viparyay_sam`, `seemit`, `fib`, `asti_sampurna`, `collatz_charan` |
| shreni | `yoj shreni` | 11 — `vinimay`, `budbud_shreni`, `shankh_shreni`, `viparyay_mala`, `laghu`, `adhik`, `yog`, `anwesh_sarak`, `gan`, `asti_sorted`, `dwi_anwesh` |
| ganita | `yoj ganita` | 6 — `kuttaka` (linear indeterminate), `chakravala` (Pell's equation x^2-Ny^2=1), `samasa` (Brahmagupta's composition law), `brahmagupta_kshetr` (cyclic-quadrilateral area), `ganita_vargmool`, `ganita_nirapeksh` |
| madhava | `yoj madhava` | 5 — `madhava_pi`, `madhava_sin`, `madhava_cos`, `madhava_atan`, `madhava_vargmool` (Kerala school, T12 floats) |
| varna | `yoj varna` | 13 — `varna_maap`, `akshar_sanket`, `asti_ank_akshar`, `asti_unnat_akshar`, `asti_avanat_akshar`, `asti_akshar_akshar`, `asti_avakash_akshar`, `gan_swar`, `gan_akshar`, `anwesh_akshar`, `asti_sarv_ank`, `unnat_sanket`, `avanat_sanket` |

60 functions across six modules. `shankh_shreni` is markedly faster than `budbud_shreni` on real
arrays. **Limitation:** a program can currently include at most two modules — the inliner's
buffer overflows at three or more; this is a known compiler bug being fixed.

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
| constant | `sutra PI = 3` |
| boolean | `satya flag = purna` |
| mala | `mala a[10]` or `vitti a[10]`; index reads/stores are bounds-checked |
| struct | `rachana Name = { field1, field2 }` |
| enum | `ganana RED = 1` (declared inside a function) |

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
  `Sutram Error [E_ANTARAL_MISHRA]` at that line — because before v275 a tab counted as one column, and such a body
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
  `nirmmita(10)` then `p[9]` → `Sutram Error [E_NIRMMITA_SEEMA]: ... p[9] nirmmita(10) bahih` /
  `Sanket: nirmmita bhaita-sankhyam ganayati, p[i] ashta-bhaita-ekakaih: p[9] hetu nirmmita(80) avashyakam`;
- **a computed index is bounds-checked when the program runs**, like a `mala`'s: the loop
  `yavat (i < 10) p[i] = i` over `nirmmita(10)` stops at `p[1]` with `Sutram Error: mala ank seema atikram`.

**What it does not check:** a size computed at run time (`nirmmita(n)`), a name assigned again (`p = p + 8`), an
address computed from `p` (`p + 8`, `arr + (pos + 1) * 8`), a parameter, a `likh8`/`akshar_rakh` store. Those are
bare addresses: write past the bytes you asked for and the program may go on, crash, or change another buffer —
exactly as in C. (A header on every block, so that *any* address could be checked, was built and measured in R76;
it breaks the library's addresses into the middle of buffers. `mala` and `kosh` are always checked.)

To *find* such a mistake, build the compiler with guard pages (`nasm -dGUARD_PAGES`, as `tools/guard_page.py`
does): every `nirmmita` block then ends against memory that cannot be touched, and a write past its end stops
the program at once.

## 7. Command line

| command | purpose |
|---|---|
| `sutram in.sm out.bin` | compile to a Linux executable |
| `sutram in.sm out.exe` | compile to a Windows executable |
| `sutram --lang gujarati in.sm out.exe` | compile with a language pack |
| `sutram -i` | interactive shell (REPL) |
| `sutram --version` | version |

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
work, as do mixed integer/float `+ - * /`, float comparisons in `yadi`/`yavat`, and printing via
`likha` with six decimal places. Current boundaries: floats do not yet cross function
boundaries (parameters/returns), no scientific notation, no float arrays.


## 16. Growable arrays (T18) — `kosh`

`kosh name[capacity]` declares a growable mala (Devanagari `कोश`); capacity is optional and
defaults to 4. Logical length starts at 0 and `a[index]` reads/writes against that length.

| builtin | meaning |
|---|---|
| `kosh_push(k, v)` | append v; returns the new length |
| `kosh_pop(k)` | remove and return the last element |
| `kosh_len(k)` | logical length |
| `kosh_cap(k)` | current capacity |
| `kosh_clear(k)` | sangrah logical length to 0 (storage NOT erased); returns 0 |
| `kosh_empty(k)` | 1 if length is zero, else 0 |
| `kosh_peek(k)` | last element, not removed |
| `kosh_enqueue(k, v)` | append v; returns the new length (alias of push) |
| `kosh_dequeue(k)` | remove and return the first (oldest) element — FIFO, O(n) |

Full specification, measured behaviour, and the `kosh` vs `suchi`/`queue`
comparison: `docs/KOSH-BUILTINS.md`.

Capacity doubles on growth. Empty `kosh_pop` / `kosh_peek` / `kosh_dequeue`
abort with their own diagnostics — `rikta kosh se kosh_pop`,
`rikta kosh se kosh_peek`, `rikta kosh se kosh_dequeue` — and exit
1. Element types: integer (`kosh v`, the default) or binary64
(`kosh dasham d`). `push`/`pop`/the builtins take a direct kosh variable.

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
prakriya yog(vibhag s) { ... pankti_len(s) ... s[i] ... }
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
- `pankti_len(s)` is the slice's length.

### Not done in this version

Closures; calling an expression directly (`t[0](x)`, `p.f(x)` through a field:
store it in a variable first); a checked type for function values; methods
dispatched on the object's type, traits; slices of a `kosh dasham`; a slice that
outlives its function; a `kosh` that grows after a slice of it was made leaves the
slice pointing at the old storage.

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
address made in the block.** Putting one in directly (`kosh_push(k, buf)`, `k[i] = buf`) is refused; the one way
it gets in unseen is through a `prakriya` that hands the address back (below). A `kosh` of *numbers* used in a
block works; its storage is ordinary memory, which the block does not reclaim.

### Run time

- **Entry** remembers the scratch cursor. Each `nirmmita` inside takes memory from the scratch side of the
  program's 1 GiB field, zeroed, like any `nirmmita` buffer.
- **Every exit gives it all back:** reaching the end of the body, `nivartanam`, `krama`, `agrim`, and a failure
  passed on by `prasar`. A later block reuses the same memory, and sees zeros, never the earlier block's data.
- **A negative size** is an error: written as a number (`nirmmita(-1)`), the compiler refuses it —
  `E_NIRMMITA_RNA`; computed (`nirmmita(n)` with `n` below 0), the program stops, exit 1:
  `Sutram Error: nirmmita-parimanam rnatmakam - mandapa-madhye rnam parimanam na sambhavati`. (Outside a block, and in
  a Windows program, a computed negative size still gives 0.)
- **Measured (Linux x86-64, v270/v271):** 1,000,000 × `nirmmita(64)` in a loop — **264 KB** peak with the block,
  **62 MB** without it. A `kosh` outside the block filled with 1,000,000 numbers from inside it: **7.8 MB** (the
  `kosh` itself) against **78 MB** without the block. A block recursing 1,000 deep, 1,000 times: **2 MB**
  against 64 MB.
- **Pages are reused, not returned:** a block that touched 100 MB keeps those 100 MB resident; the next block
  uses them again.
- **More than the field holds** stops the program, exit 1:
  `Sutram Error: kshetra purnam - mandapa-smritih samapta` (*the field is full — the block's memory is used up*).
- **Linux only.** In a Windows (PE) program, and in the `GUARD_PAGES` diagnostic build, a `mandapa` is an
  ordinary block: everything works, nothing is reclaimed.

### What the compiler refuses — `E_SCRATCH_ESCAPE`

A scratch address — a `nirmmita` result inside the block, or that address plus or minus a number, or a copy of
it — must not outlive its block:

| | |
|---|---|
| **1. into a variable declared outside the block** — `outer = buf + 64`, and into a module `vitti` (`g = buf`), wherever in the file it is declared | refused |
| **2. into memory** — `bahar[i] = buf`, a raw buffer's cell, `likh`, `likh8`, `kosh_push` — wherever the call is written: a statement, an initializer, an argument, a condition | refused |
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
not, see `docs/MEMORY-DECISION.md`.

### A `kosh` made inside the block (v278)

**A `kosh` declared inside a `mandapa` lives as long as the block.** Inside it, use it as any `kosh` — push,
grow, index, pass it to a `prakriya` — and give back a value (`examples/286`). After the block, it is gone: a
`prakriya` that receives it then stops the program with

```
Sutram Error [E_KOSH_MANDAPA]: prakriya 'padh' - kosh 'k' pankti 10 mandape rachitah; sa mandapah samaptah
Sanket: mandape rachitah kosh mandapat bahih na jivati - mandape eva upayujyatam, mulyam nivartyatam
```

*(the kosh made in the block on line 10 — that block has ended; use it inside the block and return the value)*,
exit 1 (`examples/287`). That holds however the block ended — at its end, by `nivartanam`, or by `krama` /
`agrim` out of a loop — and for an inner block ended inside a running outer one; the same block entered again
(the next turn of a loop) makes a new `kosh`, and the old one stays dead.

How: each such block takes a fresh generation on entry and clears it on exit; each `kosh` it makes records it;
a `prakriya` with a `kosh` parameter compares them on entry. **A `kosh` made outside every block is unchanged**,
and a program with no `kosh` in a block compiles to the same bytes as before. In a program with one, every
`kosh` carries three more header words and each call with a `kosh` parameter one check (+11% on a call whose
whole body is one `kosh` read; +3.5% on `kosh_push`).

**Not yet:** the block does not take the `kosh`'s memory back — it is kept, so that the check is exact. Reading
the `kosh`'s address as raw memory (`x[i]` on a plain `vitti`) is not checked — as all raw memory (§6c). Under
`--separate`, a module compiled on its own checks its `kosh` parameters only if it has a `kosh` in a block itself:
the whole-program compile checks every `prakriya`.

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
| `likha` (not the `likha(fd, buffer, count)` form), `likha_fmt`, `grahan`, `nirmmita` | every other builtin: `likh8`, `pad8`, `akshar`, `akshar_rakh`, `smaran`, `shabda`, `kosh_*`, files … — `E_APARIKSHITA_KARYA` |
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

## Printing a string variable - READ THIS BEFORE YOU TRY IT

**`likha` prints a string LITERAL as a string. It prints a string VARIABLE as a pointer.**

```sm
mukhya() {
    likha("hello")        # prints:  hello
    vitti s = "ab"
    likha(s)              # prints:  4194454      <- the address, not the text
    s = s + "cd"
    likha(s)              # prints:  8388927
}
```

**Verified on the current compiler.** `likha("hello")` gives `hello`; `likha(s)` where `s` is a variable gives
a number.

**This is a real trap and it is not a defect** - it is how the language works today, recorded in the
CHANGELOG but until now in no reference. **A beginner writes `vitti s = "hello"` and then `likha(s)`, and gets
a seven-digit number with no explanation.**

**The workaround:** print a string with an explicit length - `likha(1, s, n)` - or print it as a literal.

*Open: should `likha` print a string variable as text? That would be a language change and it is the owner's
call. Documented here so nobody has to discover it by confusion.*

