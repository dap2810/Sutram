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
| `nirmmita` | allocate memory |
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
- `guna` needs `{ }`; its `bhavana` bodies may be indented.

### 6b. Is Sutram speakable Sanskrit?

**Yes, as Sanskrit-oriented technical instructions; no, not as complete Sanskrit prose.** Keywords such as `mukhya`, `vitti`, `chakra`, `yoj` and `nivartanam` are Sanskrit-origin vocabulary (some are modern technical metaphors or conventional forms). `chakra i = 0 arabhya 4 paryantam` is a speakable *range phrase*, but its identifiers, `=`, braces, and command sequence do not supply the Sanskrit cases, verb inflections, and agreement required of an ordinary grammatical sentence.

Read it aloud as **code** with Sanskrit vocabulary, not as poetry or automatically well-formed Sanskrit discourse. Pāṇini's `anuvṛtti` and `adhikāra` are useful formal-grammar analogies, **not mechanisms currently implemented merely because they have Sanskrit names**. No new parser feature or natural-language understanding is claimed.

**Teaching example:** `examples/11_forloop.sm` already teaches a loop, but only the legacy `tak` spelling. After separately verifying the new form, update or extend that example to show the equivalent Sanskrit-oriented range without removing legacy coverage.
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

## 19. The scratch block: `mandapa` (R72)

**A `mandapa` gives you a few temporary buffers of numbers for one piece of work; when the block ends, they are
gone. Use it for scratch arithmetic. It does not work with `kosh`.**

```sutram
prakriya madhya(a, b, c)
    mandapa
        vitti t = nirmmita(3 * 8)     # scratch: three numbers
        t[0] = a
        t[1] = b
        t[2] = c
        # ... sort t ...
        nivartanam t[1]               # return a VALUE read from scratch - allowed
    nivartanam 0
```

`mandapa` (Devanagari मण्डप) is a statement: the keyword, then an indented body (braces also work).

| In a `mandapa` block, v1.0 | |
|---|---|
| numbers: scalar variables and arithmetic, a result returned or assigned outward | allowed |
| `nirmmita(n)` buffers of numbers, used inside the block | allowed — this is what the block is for |
| nested blocks, and loops inside a block | allowed |
| `nivartanam` of a value | allowed |
| `nivartanam` of a buffer allocated inside the block (`nivartanam b`, `nivartanam nirmmita(n)`) | **refused**: `E_SCRATCH_ESCAPE` |
| any `kosh` | not supported in v1.0 |
| keeping a scratch buffer's address anywhere that outlives the block | not supported in v1.0 |

**What it is not.** It is not a way to manage the memory of code that uses `kosh` — most of a real program's
growing memory — and a block around a call does not reclaim what the called function allocates inside itself
(the block is lexical). For when it helps and when it does not, see `docs/MEMORY-DECISION.md`.

**Status in this version (v268): the block is inert.** It parses, scopes its variables like any block, and
refuses the scratch-address `nivartanam` — but it does not yet place its `nirmmita` on the scratch side or
reclaim them, so a program with a `mandapa` block compiles to exactly the same program as without it. The
memory is reclaimed from the release that turns the scratch side on; nothing you write changes then.

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

