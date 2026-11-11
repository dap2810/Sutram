# ROUND-167 — the first hour, and every character the lexer swallows

**Base:** main at v315, tip commit `064b05ad` · **Deliver into:** `Muse-to-Sarvam/`

**Read only. Nothing compiled or run.** Every line number below was re-grepped
on this tree; every count re-derived from it. Paths are relative to the repo
root. Claude's v321 (R182, the lexer refusal) and v323 (R184, read-a-line)
were read only for comparison; the findings below are from main (v315).

Sources read: `src/sutram_compiler.asm` (33,704 lines),
`src/r66_indic_lexer.inc`, `docs/sutram-book-english.html`,
`docs/sutram-book-sanskrit.html`, `examples/` (331 `.sm` files at top level,
347 recursively), `lib/`, `lang/`, `docs/ERROR-CONVENTION.md`,
`docs/LANGUAGE-REFERENCE.md`.

---

## 0. Addendum — what a beginner is taught in their first hour

Read: English book chapters 1–3 (`docs/sutram-book-english.html:80–125`),
Sanskrit book chapters 1–3 (`docs/sutram-book-sanskrit.html:80–116`), and the
first ten examples sorted (`examples/01_hello.sm` … `examples/09_comparisons.sm`
plus `examples/100_t18_kosh_bounds.sm` — there is no `10_` file; sort order
puts `100_` tenth). The Sanskrit book is a faithful mirror: same programs,
same claims (same "~9000 lines", same "~90 bytes", same pack claim), so
nothing below differs by book.

### (1) What a beginner is taught to write, in order

Chapters 1–3 teach exactly three things, in this order:

1. **Print hello** (ch2): `mukhya()` + `likha("Namaste, Sutram!\n")` — one
   program, `namaste.sm`. Compile with `sutram namaste.sm namaste.bin`, run
   `./namaste.bin`.
2. **Variables and arithmetic** (ch3): `vitti x = 10`, `x = x + 5`, `likha(x)`
   (prints 15); `sutra pi = 314`, `likha(pi / 100)` (prints 3); `likha("\n")`.
   One program, in the chapter.
3. **Nothing else in the first hour.** No input, no files, no loops, no
   decisions — those are chapters 4 (operators), 5 (`yadi`/`anya`), 6
   (`chakra`/`yavat`), and input (`grahan`) first appears only in chapter 13
   (the reference table, `:346`) and chapter 14/18 (`:409–413`).

The first ten examples follow the same order, one step further: hello (01),
arithmetic (02), if/else (03), while loop (04), functions with parameters
(05), rachana (06), module include (07), combined demo (08), comparisons (09).
The tenth file by sort order, `100_t18_kosh_bounds.sm`, is not a beginner
program at all — it is a `kosh` bounds test.

### (2) Does every one of them work today?

Read against the language (not run). **Yes, all nine beginner programs work;
the tenth works as a test, not as a program.**

| # | Program | Verdict by reading |
|---|---|---|
| 01 | `likha("Namaste, Sutram!\n")` | Compiles, prints `Namaste, Sutram!` + newline. |
| 02 | `vitti x = 10; vitti y = 20; vitti z = x + y; likha("x + y = ", z)` | Compiles, prints `x + y = 30`. Two-argument `likha` is the print form. |
| 03 | `yadi (x > 5) { likha("big\n") }` | Compiles, prints `big`. No `anya` used. |
| 04 | `yavat (i < 5)` counting loop | Compiles, prints 0–4 each on its own line. |
| 05 | `prakriya yog(a, b)` / `gun_tray(a, b, c)` + `nivartanam` | Compiles, prints `yog(10, 32) = 42` and `gun_tray(3, 4, 5) = 60`. |
| 06 | `rachana Point = { x, y, z }` + `nirmmita(24)` + `p.x = 10` … | Compiles, prints `p.x = 10`, `p.y = 20`, `Sum = 60`. 24 bytes = 3 qwords, one per field. |
| 07 | `yoj ganit` + `vargit(7)` | Compiles, prints `vargit(7) = 49`. `vargit` exists (`lib/ganit.smlib:15`); the `yoj` pre-pass reads the module name from the raw line. |
| 08 | Demo (rachana + prakriya + yavat) | Compiles, prints the demo lines, `double(21) = 42`, `Age: 25`, `Score: 100`, `Loop: 1..3`, `=== Done ===`. |
| 09 | Comparisons `<= >= != ==` + two `yavat` loops | Compiles, prints all four `true` lines and both loops (`0 1 2 3 4 5`). |
| 10th | `100_t18_kosh_bounds.sm` | Compiles. At runtime `kosh_hri` pops the one element, then `a[0]` is out of bounds, so the program halts with the bounds refusal — that is the test's point ("dynamic length must drive normal `[]` bounds checks after pop"). It prints nothing; "works" here means it refuses as designed. |

The book's own chapter 2 and 3 programs also work as written, with two numbers
unverifiable by reading (see Could-not-determine): the compiler's success message
shape is confirmed (`Siddh: N baait sankalit`, `src/sutram_compiler.asm:836–837`),
but the exact `97` and "about 90 bytes" are measured outputs, not readable facts.
Chapter 3's register claim holds: user variables may live in `r12`–`r15`
(`:19117`, "B6: user variables may live in r12-r15"), plus `rbx` makes five.

### (3) Where the book promises something the language cannot do

One place in chapters 1–3, and it is in chapter 1, not in any program:

> "With language packs you can write every keyword in Hindi, Telugu, Bengali,
> Tamil, and nine other Indian languages." (`:92–94`; same claim in the Sanskrit
> book, `:89–91`.)

That is **not true as written**. Counted from the tree: the Sanskrit keyword
table has 34 distinct words (`kw_table`, `:844-898`, excluding the 17 Devanagari
alias rows and the `prati` alias row); every one of the ten non-Sanskrit packs
is missing exactly the same three — **`mandapa`, `nivartanam`, `sankhya`**. The
Hindi pack has `कोश kosh` and `पढ़ो grahan`, but no word for `mandapa` and no
word for `nivartanam` (it maps only the alias, `वापस prati`, `lang/hindi.lang:12`).
`mandapa` and `sankhya` have no spelling at all in any non-Sanskrit pack. (The
eleventh `.lang` file is `sanskrit.lang` itself, which has all three; the one
`gujarati.lang` hit for `sankhya` is a comment — "# The vector type remains
available as Latin sankhya" — not a mapping.) Pack keywords are additive
(`lookup_keyword` scans the Sanskrit table first, then the loaded pack table,
`:32929–32955`), so a pack user can still write `mandapa` — in Sanskrit — but
the claim is "write every keyword **in** Hindi", and for those three there is
no Hindi (or Tamil, Telugu, Bengali, Gujarati, Kannada, Malayalam, Odia, Marathi,
Punjabi) word. And `LANGUAGE-PRIORITY.md` (owner, 2026-10-23) freezes all
non-Sanskrit packs — no new work goes into them — so the gap can only grow as
Sanskrit gains keywords.

Two smaller chapter 1–3 imprecisions, neither a broken promise:

- Chapter 2 says "comments start with `//`" — but the lexer also accepts `#`
  comments (`:5720`, "Skips # and // comments"; the `#` check is in `.lex_loop`
  at `:7046`), and the book's own first example file (`01_hello.sm`) opens with
  a `#` comment. `//` is not the only form; the book never says it is, but a
  beginner copying the example and reading the chapter could reasonably conclude
  `#` is wrong.
- Chapter 2's `Siddh: 97 baait sankalit` and "about 90 bytes" are stated as fact;
  the message shape is right, the numbers are not checkable by reading.

### (4) Which of the three known gaps does a beginner hit first?

**The lexer — and the answer does not reorder the work.**

The book's first hour is "print hello, add two numbers, loop" — there is no
"ask my name" in it. Input is never taught in chapters 1–3, so the beginner
cannot hit the input gap *by following the book*. What they can hit, in the
very first program, is the lexer: `likha("Namaste, Sutram!\n")` typed on a
phone (smart punctuation turns the quotes curly) fails with
`E_UNDEFINED_NAME: agyat naam 'hello'`, and `vitti a = 5 – 2` pasted from a
document (spaced hyphen autocorrected to an en dash) compiles and prints `5`.
Both break programs the book itself teaches, on the exact devices the brief
names. The input gap is the first *felt absence* — it is the most natural third
program ("ask my name") after hello and arithmetic, and the language has no way
to do it at all (`grahan` reads numbers only) — but the book does not prompt it
in hour one, so it is second. The file example is last: no example reads a file,
no chapter asks for one, and the capability exists (`patra.smlib`) even if no
example shows it.

**Ranking stands: lexer first, input second, file example third.** The one
correction to the addendum's hypothesis: its "print hello, add two numbers, ask
my name" first hour is not the book's first hour — the book's is "print hello,
add two numbers, loop", and on that curriculum the lexer is the only one of the
three that can corrupt a taught program.

---

## 1. Task 1 — every character the lexer swallows

### The comment/string question first

**The fix is safe on this point: comments and strings are consumed before the
skip path is ever reached, so a refusal placed where the skip sits cannot fire
inside them.**

The dispatch order in `.lex_loop` (`src/sutram_compiler.asm:6991`):

1. Whitespace (`is_space`: space, tab, LF, CR only — `:32883`).
2. **Comments, skipped whole** — `//` to end of line and `/* … */`
   (`:7005–7036`), and `#` to end of line (`:7044–7046`, via `.skip_comment`).
   The comment skippers advance byte by byte looking only for the terminator
   (newline, or `*/`); every byte inside — curly quotes, dashes, rupee signs,
   anything — is consumed as comment text and never tokenised.
3. Danda (`r66_is_danda_at`) and Indic decimal digits (`r66_decimal_digit_at`).
4. Identifier collection (`is_alpha`: A–Z, a–z, `_`, and the byte `0xE0` —
   `:32810`), with multi-byte scalars validated and copied by
   `r66_indic_scalar_width`.
5. Numbers (`.try_number`).
6. `.try_operator`: the **string check comes first** — a `0x22` byte opens
   `.lex_string` (`:7363`), which copies bytes raw into the string pool until
   the closing quote, handling `\` escapes. Any character inside a string
   literal is string content, never lexed. Then operators and delimiters. Only
   if none of those match does control reach the skip:
   `; Unknown char — skip / inc r13 / jmp .lex_loop` (`:7420–7422`).

Two related leniencies, found while reading, not part of the question:

- An **unterminated string at end of file is silently accepted**: `.str_done`
  (`:7511`) is reached both on the closing quote and on EOF, and emits the
  `TOK_STRING` either way. No error.
- A **truncated or malformed `0xE0` sequence is a hard error, not a skip**:
  `.store_multibyte` calls `r66_indic_scalar_width`, and on failure jumps to
  `capacity_fail` with `E_UTF8` (`r66_msg_bad_utf8`, `src/r66_indic_lexer.inc`).
  So a Devanagari character cut off at end of file, or an overlong `E0 80 80`,
  stops the compile — it does not vanish.

Also: the `@` in `yoj ghatak@upanaam` never reaches the lexer at all — the
import pre-pass reads the raw line and consumes `@` itself (`.ei_alias_start`,
`:3704`). The lexer's skip of `@` affects only `@` anywhere else in a program.

### The list

How to read the table: "today" is the token-level effect (the character vanishes;
the tokens either side are what the parser then sees). The downstream effect
depends on position — a vanished infix operator between two complete expressions
leaves two adjacent expressions, and the parser takes the first and compiles the
second as a discarded expression statement (`.ps_check_expr` → `.ps_expr_done`,
`:16026` / `:16182`, and `gen_stmt`'s default is `gen_expr`, `:19065`); the same
vanished character inside parentheses leaves a token the parser does not expect,
which is a confusing parse error. Both are stated where they differ.

**Non-ASCII first (the ones that matter):**

| Character | Code point (UTF-8 bytes) | Produced without asking by | What a program containing it does today | Suggest instead |
|---|---|---|---|---|
| “ left double quote | U+201C (E2 80 9C) | Phone keyboard (smart punctuation); word processor (autocorrect); pasted text | Vanishes. `likha(“hello”)` becomes `likha(hello)` → `E_UNDEFINED_NAME: agyat naam 'hello'` — the error names the wrong thing (brief's measured case). | `"` (U+0022) |
| ” right double quote | U+201D (E2 80 9D) | Same as U+201C | Same as U+201C. | `"` (U+0022) |
| ‘ left single quote | U+2018 (E2 80 98) | Phone keyboard; word processor | Vanishes. `likha(‘hello’)` becomes `likha(hello)` → `E_UNDEFINED_NAME 'hello'`. | `"` (U+0022) — the language has no single-quoted strings |
| ’ right single quote / apostrophe | U+2019 (E2 80 99) | Phone keyboard; word processor (every possessive/contraction in pasted prose) | Same as U+2018. | `"` (U+0022) |
| – en dash | U+2013 (E2 80 93) | Word processor (spaced hyphen → en dash); phone keyboard (long-press hyphen); pasted text | **Silent wrong answer.** `vitti a = 5 – 2` lexes as `vitti a = 5` followed by a discarded `2` → compiles, prints `5` (brief's measured case). Inside parentheses (`yadi (x > 5 – 2)`) it is a confusing parse error near `2` instead. | `-` (U+002D) |
| — em dash | U+2014 (E2 80 94) | Word processor; phone keyboard | Same as en dash. | `-` (U+002D) |
| − minus sign | U+2212 (E2 88 92) | Maths/phone symbol keyboards; pasted maths | Same as en dash: `5 − 2` prints `5`. | `-` (U+002D) |
| ‐ hyphen, ‑ non-breaking hyphen | U+2010 (E2 80 90), U+2011 (E2 80 91) | Word processor; pasted text | Same as en dash. | `-` (U+002D) |
| ₹ rupee sign | U+20B9 (E2 82 B9) | Phone keyboard (Indian layouts); pasted text | Vanishes harmlessly in the measured position: `likha(100 ₹)` → `likha(100)`, prints `100`. Between tokens it is inert; inside an identifier it splits it. | Nothing — there is no operator it stands for |
| NBSP | U+00A0 (C2 A0) | Word processor (keeps words together); phone keyboard (long-press space on some); pasted text | Vanishes, and **acts like a space for token separation** (the identifier collector stops at `0xC2`), so `vitti<NBSP>x` lexes as `vitti x`. But it does **not** count as indentation: `.nc_indent` (`:6383`) counts only space and tab, so a line indented with NBSPs measures as indent 0 and the block rule misfires — a confusing indentation error, not a silent space. | Space (U+0020) |
| ZWSP | U+200B (E2 80 8B) | Word processor; pasted text; some Indic input | Vanishes invisibly. Between tokens, inert. Inside a Devanagari identifier it splits it into two identifiers. | Remove it (invisible) |
| ZWNJ | U+200C (E2 80 8C) | Phone Indic keyboards (needed for correct rendering of some words); pasted Indic text | Vanishes. **Inside a Devanagari identifier it splits it**: the collector stops at `0xE2`, the three bytes are skipped, the next Devanagari scalar starts a new identifier — a name the user typed as one word becomes two tokens, then an `E_UNDEFINED_NAME` or a parse error. This is the one zero-width character that can break correct Indic input. | Remove it (invisible) — but note the rendering cost: deleting it changes how the word displays |
| ZWJ | U+200D (E2 80 8D) | Phone Indic keyboards (needed for correct rendering, e.g. conjuncts); pasted Indic text | Same as ZWNJ: splits a Devanagari identifier into two tokens. | Remove it (invisible) — same rendering caveat |
| © copyright | U+00A9 (C2 A9) | Phone symbol keyboard; pasted text | Vanishes. Inert between tokens; splits an identifier if inside one. | Nothing |
| ® registered | U+00AE (C2 AE) | Same as © | Same as ©. | Nothing |
| ° degree | U+00B0 (C2 B0) | Phone symbol keyboard; pasted text | Vanishes. Inert between tokens (`5° + 2` → `5 + 2` = 7). | Nothing |
| × multiplication sign | U+00D7 (C3 97) | Phone symbol keyboard; word processor (autocorrect `x` in maths); pasted maths | **Silent wrong answer.** `5 × 2` lexes as `5` followed by a discarded `2` → compiles, prints `5`. Same class as the en dash. | `*` (U+002A) |
| ÷ division sign | U+00F7 (C3 B7) | Same as × | Same as ×: `8 ÷ 2` prints `8`. | `/` (U+002F) |
| ≤ less-or-equal | U+2264 (E2 89 A4) | Maths/phone symbol keyboards; pasted maths | Vanishes. `yadi (a ≤ b)` lexes as `yadi (a b)` → parse error near `b` (the condition parser expects `)` after `a`). Confusing, not silent. | `<=` |
| ≥ greater-or-equal | U+2265 (E2 89 A5) | Same as ≤ | Same as ≤. | `>=` |
| ≠ not-equal | U+2260 (E2 89 A0) | Same as ≤ | Same as ≤. | `!=` |
| « » guillemets | U+00AB (C2 AB), U+00BB (C2 BB) | Word processor (some locales); pasted text | Vanish. `«hello»` becomes `hello` → `E_UNDEFINED_NAME 'hello'` if used as a string. | `"` (U+0022) |
| BOM | U+FEFF (EF BB BF) | Editors that save UTF-8 with BOM; pasted text | Vanishes harmlessly — all three bytes are skipped. A BOM at file start costs nothing. (v321 carves this out explicitly; on main it is just three skipped bytes.) | Nothing (remove silently) |
| Any other non-ASCII scalar outside U+0800–U+0FFF | e.g. U+00E9 é (C3 A9), U+4E2D (E4 B8 AD), emoji U+1F600 (F0 9F 98 80) | Phone keyboards (accented letters, CJK, emoji); pasted text | Vanishes, byte by byte — the lexer sees bytes, not code points, so a 2-, 3- or 4-byte scalar is skipped one byte at a time. An accented letter in an identifier splits it; an emoji between statements is inert. | Nothing in general (no mapping exists) |

**NOT swallowed — the brief's "check first" items that do not reach the skip path:**

| Character | Code point | Why it is safe |
|---|---|---|
| Devanagari digits ०–९ | U+0966–U+096F (E0 A5 A6–AF) | Recognised as numbers by `r66_decimal_digit_at` (`src/r66_indic_lexer.inc:15`), at token start and inside number literals — including mixed with ASCII digits and after the decimal point. They never reach the skip path. Same for Gujarati U+0AE6–0AEF, Bengali U+09E6–09EF, Gurmukhi U+0A66–0A6F, Odia U+0B66–0B6F, Tamil U+0BE6–0BEF, Telugu U+0C66–0C6F, Kannada U+0CE6–0CEF. |
| Devanagari (and other Indic) letters | U+0900–U+097F etc. (E0-led) | `is_alpha` returns true for the byte `0xE0`, and `.store_multibyte` copies any valid E0 scalar into the identifier. They are identifier characters. |
| Danda । ॥ | U+0964/U+0965 (E0 A5 A4/A5) | Recognised by `r66_is_danda_at` and emitted as a token. |

**ASCII (the complete class — every byte not in the recognised sets):**

Recognised ASCII: letters, digits, `_`, space/tab/LF/CR, `"` (string), `#` (comment),
`(` `)` `{` `}` `;` `,` `[` `]` `.` `:` `?` (delimiters),
`+` `-` `*` `/` `%` `&` `|` `^` `=` `<` `>` `!` (operators, with two-character forms).
Everything else reaches the skip path:

| Bytes | Characters | Produced without asking by | What a program containing it does today | Suggest instead |
|---|---|---|---|---|
| `0x24` | `$` | Normal keyboard (shift-4); shell habits | Vanishes. `vitti $total = 0` lexes as `vitti total = 0` — compiles (R160's case). Inside a name it splits it: `my$var` becomes two identifiers `my` `var`, so the program no longer means what was written. | Remove it |
| `0x27` | `'` (apostrophe) | Normal keyboard; every shell/JS/Python habit | Vanishes. `likha('hello')` becomes `likha(hello)` → `E_UNDEFINED_NAME 'hello'`. | `"` (U+0022) |
| `0x40` | `@` | Normal keyboard; email/decorator habits | Vanishes everywhere except `yoj` lines (handled raw by the pre-pass). `vitti @x = 1` lexes as `vitti x = 1` — compiles, silently renamed. | Remove it |
| `0x5C` | `\` backslash | Normal keyboard; Windows-path habits | Vanishes outside strings (inside a string it is the escape introducer). `5\2` lexes as `5` + discarded `2` → prints `5`. | Remove it (outside a string) |
| `0x60` | `` ` `` backtick | Normal keyboard; shell/JS habits | Vanishes. `` likha(`hello`) `` becomes `likha(hello)` → `E_UNDEFINED_NAME 'hello'`. | `"` (U+0022) |
| `0x7E` | `~` | Normal keyboard | Vanishes. `5 ~ 2` lexes as `5` + discarded `2` → prints `5`. Note: `~` is a *proposed* region marker (R160: the three rules do not decide it), not a current operator — today it is simply swallowed. | Nothing (it is not an operator yet) |
| `0x00–0x08` | NUL and C0 controls | Paste only (never typed) | Vanish, byte by byte. NUL is not an end-of-file marker to the lexer (it compares against the end pointer, not the byte), so an embedded NUL just disappears. Invisible; between tokens inert. | Remove them (invisible) |
| `0x0B, 0x0C` | Vertical tab, form feed | Paste only | Vanish. Note `is_space` does **not** include them, but they still separate tokens (the identifier collector stops at any non-alpha byte), so they act like spaces for tokenisation — and like NBSP they do **not** count as indentation. | Space (U+0020) |
| `0x0E–0x1F` | C0 controls | Paste only | Vanish, inert between tokens. | Remove them (invisible) |
| `0x7F` | DEL | Paste only | Vanishes. | Remove it (invisible) |

**The derived class, stated once:** the lexer is byte-oriented. A byte reaches the
skip path unless it is whitespace (space/tab/LF/CR), a comment starter, the
opening quote of a string, part of a `0xE0`-led scalar (U+0800–U+0FFF: identifier
character, Indic digit, or danda), an ASCII letter/digit/`_`, or a listed
operator/delimiter. So the skipped class is exactly: **`$ ' @ \ ` ~`, control
bytes 00–08/0B–0C/0E–1F, DEL, and every UTF-8 scalar outside U+0800–U+0FFF**
(each skipped byte by byte), plus stray continuation bytes (0x80–0xBF) and
invalid bytes. A malformed or truncated `0xE0` sequence is the one exception:
it is a hard `E_UTF8` error, not a skip.

### Comparison with the ROUND-169 header class

The header (`Sarvam-to-Muse/ROUND-169.md`) states the class as: "`$ ' @ \ backtick
~`, control bytes 00-08/0B-0C/0E-1F, DEL, and every non-Indic UTF-8 scalar."

**Confirmed on the ASCII half, and on the measured example** (`vitti a = 5 $ 2`
compiled and printed `5` — consistent with the code: `$` vanishes, `2` becomes a
discarded expression statement).

**Corrected on the non-ASCII half — one imprecision, not a wrong class.** The
boundary the lexer actually enforces is the byte `0xE0`, i.e. the scalar range
**U+0800–U+0FFF**, not any script list. That range contains all the Indic scripts
(Devanagari, Bengali, Gurmukhi, Gujarati, Odia, Tamil, Telugu, Kannada, Malayalam),
so "non-Indic" is right about what is skipped — but the accepted set is wider
than Indic: **Thai (U+0E00–U+0E7F), Lao (U+0E80–U+0EFF), Tibetan (U+0F00–U+0FFF),
Sinhala (U+0D80–U+0DFF), and Samaritan/Mandaic/Syriac (U+0800–U+08FF) scalars are
also accepted as identifier characters**, because `is_alpha` and
`r66_indic_scalar_width` test the byte range, never the script. A Thai word as a
variable name lexes today. The precise statement is "every UTF-8 scalar outside
U+0800–U+0FFF". Two qualifications the header omits: a malformed/truncated `0xE0`
sequence is an `E_UTF8` error rather than a skip, and the BOM (U+FEFF) is skipped
harmlessly.

### What v321 already refuses (comparison only)

Claude's R182 (v321, staged, not merged) replaces the skip with a refusal at the
same place: the old skip at the end of `.try_operator` is now `jmp
r182_unknown_char`, with a BOM carve-out just before it (a BOM at file start, or
after a newline, is skipped; anywhere else it is refused). The new error is
`E_AGYAT_AKSHAR`: `file:line:col: Sutram truti [E_AGYAT_AKSHAR]: agyat akshar
'<the character>' (U+XXXX)`, with the source line, a caret, and a `Sanket:` hint
from a code-point table (curly quotes → `"` U+0022; apostrophe/backtick → `"`;
dashes incl. U+2212, U+2010, U+2011 → `-` U+002D; NBSP and other spaces → space
U+0020; zero-width/ZWJ/ZWNJ/U+FEFF/U+2060 → "remove it"; × → `*`; ÷ → `/`;
≤ → `<=`; ≥ → `>=`; ≠ → `!=`). A byte that is not valid UTF-8 is named as a byte
(`agyat baait (0x..) - UTF-8 na asti`). Comments and strings are untouched,
because the refusal sits exactly where the skip sat — after comment skipping and
after the string check. My list above is derived from main (v315), not from v321;
the two agree on the class, and v321's hint table agrees with the "suggest
instead" column of my table on every row it covers (it adds U+201E/U+201F quotes,
U+00AB/U+00BB guillemets, U+202F/U+2007/U+3000/U+2002/U+2003/U+2009 spaces, and
U+2060 — all in my class too).

---

## 2. Task 2 — what the error should say

**The count first: the brief's "65" does not reproduce.** Counted from the tree
(`src/`):

- **56 distinct `[E_CODE]` tags** in compiler-emitted messages
  (`Sutram truti [E_...]`; digits allowed — this catches `E_UTF8` and
  `E_MODULE_V1_ALIAS`, which a letters-only pattern truncates/misses).
- **57 distinct unbracketed messages** (`Sutram truti: ...` with no code — mostly
  capacity limits, e.g. `vitti-suchi seema atikram`, and runtime refusals baked
  into generated code, e.g. `mala ank seema atikram`).
- 97 distinct `db "Sutram truti...` string literals — an overcount, because
  multi-part messages are built from several `db` lines (prefix, name, suffix).

No counting method I can state gives 65. If the brief meant coded errors, the
number is **56, not 65**. (Note also that `docs/ERROR-CONVENTION.md` is not the
compiler's error convention at all — it states the *library* `ok`-parameter
convention for checked functions. The compiler's message shape is stated in the
reference §4b, `docs/LANGUAGE-REFERENCE.md:233`, and in the code.)

**The shape of a good message** (from the code, not invented): every compile
error that can point at source is printed as

```
file:line:col: Sutram truti [E_CODE]: <sanskrit message> '<the offending thing>'
<the source line>
^
Sanket: <what to write instead>
```

The `file:line:col` prefix comes from `r51_print_origin` (the token carries its
exact source position, `[r15+32]`); the source line and caret from
`r51_print_original_context` / `msg_diag_caret` (`:380`); the hint is a `Sanket:`
line in Sanskrit. The message itself is Sanskrit, names the offending thing in
quotes, and the hint names the correction — it never explains the lexer, never
prints a byte dump, and never blames the user.

**Closest existing model: `E_UNDEFINED_NAME`** (`r4_msg_undef`,
`src/sutram_compiler.asm:332`: `": Sutram truti [E_UNDEFINED_NAME]: agyat naam '"`,
emitted by `r4_report`, `:14328`, with origin + message + context + a hint that
suggests the declaration). It is the closest in two ways: it is the error the
curly-quote case actually produces today (the wrong name for the wrong reason),
and its shape — name the thing, show where it stands, hint the fix — is exactly
the shape an unknown-character error needs, with the character in place of the
name. Family-closest is `E_UTF8` (a character the lexer cannot use), but it is a
weaker model: it is raised through `capacity_fail` (`:7731`), which prints the
bare message and exits — no `file:line:col`, no source line, no caret, no hint.

**Does an existing code fit? No — this needs a new one.** `E_UTF8` is a
malformed-encoding error (the bytes are not a complete, valid scalar); the
unknown character is well-formed UTF-8 — or plain ASCII — that the language
simply has no token for. `E_PARSE` is a token-*sequence* error (the tokens are
fine, their order is not). Neither describes a single character with no meaning
in the language. (v321's choice, for the record, is the new code
`E_AGYAT_AKSHAR` — "unknown character" — which is the right shape of name.)

---

## 3. Task 3 — what a "read a line" function could be built from

The language already reads both files and standard input; what is missing is
just the function. Files: `lib/patra.smlib` reads a whole file (`patra_path_sarv`
opens with `dvaram`, reads with `paadh`, closes with `band`, looping until the
count is met or EOF), writes one (`patra_likh_sarv`), and tests existence
(`patra_asti`) — genuine OS services, via the file builtins. Standard input:
`grahan` (builtin 33) already reads a line from fd 0 byte by byte — `sys_read`,
one byte at a time, stopping at LF, returning −1 on EOF — on Linux and on PE
(`ReadFile` on the cached stdin handle), but it parses digits and throws the
bytes away, returning only the number. And the generic read already exists as a
builtin: `paadh(fd, buf, count)` emits a plain `sys_read` (`:22751`), so
`paadh(0, …)` can read stdin from library code — nothing in the library does.
Nor is a buffer missing: `nirmmita` allocates, `akshar_rakh` writes bytes into a
string buffer, and NUL-terminated strings are the language's string form. So
neither a syscall nor a buffer is missing — only the byte-keeping loop, the
return-as-a-string decision, and the EOF signal (an empty line and the end of
input both look like `""`). That is what Claude's v323 build added, and it
confirms the size: two new builtins, BN 48 `vartani_grahan` (a line of text,
without its newline, uncut — buffer starts at 64 bytes and doubles) and BN 49
`nivesha_anta` (a flag that tells an empty line from the end of input),
generated inline, 0 DIFFER against v322 — everything it needed already existed
on main except the two decisions.

---

## Brief corrections (with numbers)

1. **"65 errors" — not reproduced.** 56 distinct `[E_CODE]` tags in
   compiler-emitted messages; 57 distinct unbracketed messages. No stated
   counting method gives 65.
2. **Devanagari digits ०–९ are not swallowed.** They are recognised numbers
   (`r66_decimal_digit_at`), as are the Gujarati, Bengali, Gurmukhi, Odia,
   Tamil, Telugu and Kannada digits. The brief lists them among the "check
   first" items; the answer is that they never reach the skip path.
3. **The ROUND-169 header class is imprecise on the non-ASCII half.** The
   boundary is the byte `0xE0` (U+0800–U+0FFF), not a script list: Thai, Lao,
   Tibetan, Sinhala and Samaritan/Mandaic/Syriac scalars are accepted as
   identifier characters too. The precise class is "every UTF-8 scalar outside
   U+0800–U+0FFF". A malformed/truncated `0xE0` sequence is an `E_UTF8` error,
   not a skip.
4. **`docs/ERROR-CONVENTION.md` is not the compiler error convention.** It
   states the library `ok`-parameter convention. The compiler message shape
   lives in the reference §4b and in `r4_report`/`r51_print_origin`.
5. **The book's chapter 1 pack claim is not true as written.** `mandapa`,
   `nivartanam` and `sankhya` have no spelling in any of the ten non-Sanskrit
   packs (counted: 34 Sanskrit keyword words; every non-Sanskrit pack missing
   exactly those three). `nivartanam` is expressible via the alias `prati`;
   `mandapa` and `sankhya` are not expressible in any pack language at all.
6. **Chapter 2's "comments start with `//`" omits `#`**, which the lexer
   accepts and the first example file uses.
7. **The addendum's "ask my name" first hour is not the book's first hour.**
   Chapters 1–3 teach print, variables and arithmetic only; `grahan` first
   appears in chapter 13. The ranking does not reorder on the book's evidence.
8. **There is no `tree_v323` directory.** The v323 read-a-line build lives in
   the v322 worktree (HEAD `f05ddd7e`; the build itself is commit `25b247b3`).
   (A worktree-naming note from this round's own staging, not a tree fact.)

One correction to the working notes, verified before this report was written:
the notes said "every one of the eleven packs" is missing the three keywords.
The tree has eleven `.lang` files, but one of them is `sanskrit.lang` itself,
which has all three — the accurate statement is the **ten non-Sanskrit packs**.
The one `gujarati.lang` hit is a comment, not a mapping.

## Could-not-determine

- Whether the book's "97 baait" and "about 90 bytes" (ch2) are exact — the
  message shape is confirmed, the numbers are measured outputs.
- Whether `vitti my$var = 1` ends as two declarations or an error — the `$`
  certainly splits the name into two identifiers (`my` `var`); the downstream
  depends on `r7_check_assign`'s treatment of assignment to an undeclared name,
  which the reading did not settle.
- The exact downstream of a vanished character in every syntactic position —
  the table gives the token-level effect and the two main downstream shapes
  (discarded expression statement vs confusing parse error); rarer positions
  (inside a `yoj` line, inside a `nishkriya` string) were not traced.
- Whether any gate outside `tests/expect/` asserts the book's 97-byte figure.
- Whether a Thai/Lao/Tibetan word as a variable name survives the *whole*
  compiler (it lexes as an identifier; later stages were not traced for it).
- Whether the brief's "65" counts something else entirely (e.g. including
  runtime-only messages, or per-site rather than per-code) — the methods tried
  are stated above.
- The exact per-allocation cost of any lexer fix (no fix was built here; v321
  is Claude's).

---

## Summary

The addendum's question is answered by the book, not by the defect list: a
beginner's first hour is print hello, variables and arithmetic — no input, no
files — so the ranking does not reorder (lexer first, input second, file example
third), though the book's chapter 1 does promise something the language cannot
keep, namely that every keyword can be written in every pack language
(`mandapa`, `nivartanam` and `sankhya` have no spelling in any of the ten
non-Sanskrit packs). On the lexer itself: comments and strings are consumed
before the skip path, so a refusal placed there is safe; the swallowed class is
exactly `$ ' @ \ ` ~`, control bytes 00–08/0B–0C/0E–1F, DEL, and every UTF-8
scalar outside U+0800–U+0FFF (byte by byte), with Devanagari digits and letters
never swallowed at all — the ROUND-169 header's "non-Indic" is right about what
is skipped but the boundary is the byte `0xE0`, which also accepts Thai, Lao,
Tibetan, Sinhala and Samaritan as identifier characters; the silent-wrong-answer
cases are the en/em dash, minus sign, `×` and `÷` (and `~`, `\`, `$` in the
operator's place), while curly quotes produce the misleading
`E_UNDEFINED_NAME`. The error to copy is `E_UNDEFINED_NAME` (name the thing,
show the line and caret, hint the fix); no existing code fits, so the refusal
needs a new one. And reading text is a small job, not a missing primitive: files
are already read by `patra.smlib`, stdin is already read byte-by-byte by
`grahan` and generically by `paadh`, buffers already exist — only the function
was missing, which is what v323 built as two builtins with 0 DIFFER.

---

*Read-only round. Nothing compiled or run. All v321/v323 statements are
comparisons against Claude's staged branches, read from the tree, not
re-measured here.*
