# ROUND-47 — the meaning check before any rename

**Base:** `origin/main` at `61d5f7b7` (v374; round written against
v372), compiler **v253**. Measured independently from the compiler
source and `lib/` on this base, not from Sarvam's audit doc — where
my measurements agree with `docs/LIBRARY-ENGLISH-AUDIT.md` I say so,
where they add to it I say that too. PASS / FAIL / NOT-RUN
separately. **No code changes made. No files added or modified in
the tree.**

## WS1 — for each identifier: what `lib/` does, what the Sanskrit builtin does, SAME or DIFFERENT

The brief's premise needs one correction up front: **most of the
English the owner scanned is not identifiers at all.** It is prose
in comments, internal assembler labels, and local variable names a
user never types. Renaming those changes nothing a learner sees.
The table below is only about what a user can actually call or
read as API.

### 1. `char` — NO `char` IDENTIFIER TO RENAME. The Sanskrit builtins already exist, and they are three different things.

**What `lib/` actually does:** lib code never calls `char_at`,
`set_char`, or `char_code`. Those strings appear only in comments
(e.g. `lib/varna.smlib:4` "Built on `vartani_aayam` and
`char_at`") and in compiler comments/labels. Verified: a program
calling `char_at(s, 1)` fails to compile —
`Sutram Error: agyat prakriya: char_at`. The one non-comment
`char` substring in lib code is `collatz_charan` (`lib/ank.smlib:103`),
and `charan` there is Sanskrit (step, as in Collatz steps), not
English `char` — a grep false positive.

**What the existing Sanskrit builtins do** (compiler builtin table,
`src/sutram_compiler.asm:754–763`, verified by running them):
- `akshar(s, i)` — byte at index `i` of string `s`, as an integer
  code. Tested: `akshar("abc", 1)` = 98.
- `aksharank(s)` — code of the first byte (1- or 2-argument form).
  Tested: `aksharank("abc")` = 97.
- `akshar_rakh(s, i, v)` — set byte `i` of `s` to `v`. Tested:
  after `akshar_rakh(s, 0, 120)`, `akshar(s, 0)` = 120.

Lib code already calls these three by their Sanskrit names
(`lib/anukram.smlib`, `lib/nighantu.smlib`, `lib/roop.smlib`
throughout).

**Verdict — DIFFERENT, and the brief's warning is exactly right:**
`lib/char` is not one thing, so it cannot be renamed to one
thing. If anyone renamed a hypothetical `char` to `akshar`, they
would be naming the *code* operation (`aksharank`) with the
*character* word (`akshar`) — a wrong name on a right function,
worse than English. **There is nothing to rename here. The
`char`→`akshar` rename must NOT proceed, because its target does
not exist as a user-visible identifier.** (Agrees with Sarvam's
audit §1.)

### 2. `int` — TWO REAL PUBLIC NAMES, and the proposed rename is right in meaning but wrong in context

**What `lib/` actually does** (`lib/brihat.smlib:24, 67`):
- `brihat_ank_se_int(val, arr, n)` — convert a native machine
  integer (`val`, int64, with explicit INT64_MIN handling) into a
  digit array, least-significant digit first. Returns 1 if it fit.
- `brihat_ank_tak_int(arr, n)` — convert a digit array back into a
  native machine integer (verification use only; correct only if
  the value fits).

In both, `ank` = **digit** (the array holds digits, as in
`ank_gan` = digit count, `ank_yog` = digit sum), and `int` =
**the native machine integer** on the other side of the
conversion. The pair is *big-number digits* against *machine
integer*.

**What the existing Sanskrit word does:** `anka` is a declaration
keyword (`src/sutram_compiler.asm:476, 511`; `lang/sanskrit.lang`:
अङ्क `anka`), an alternative to `vitti` for declaring an integer
variable. So `anka`'s referent IS the machine integer — the same
thing `int` means here.

**Verdict — SAME THING, but do NOT rename to `anka`.**
`brihat_ank_se_anka` would put `ank` (digit) and `anka`
(integer) — near-homonyms with different meanings — in one
identifier, and a reader will parse both as "number". The English
name accidentally preserves a distinction the Sanskrit rename
would destroy. This is Sarvam's `laghu` proposal, independently
confirmed: `brihat_ank_se_laghu` / `brihat_ank_tak_laghu` ("from a
big number, a small one") reads as a pair, avoids reusing `ank`,
and says what the conversion actually is — big representation to
small representation. **Recommendation: rename the two functions
to the `laghu` pair, not to `anka`.** All other `int` hits in
`lib/` are prose ("convert int to digit array", "fits in an
int"), not identifiers.

### 3. `div` — NO `div` IDENTIFIER TO RENAME. Division is already `bhaj` everywhere it matters.

**What `lib/` actually does:** there is no function, variable, or
parameter named `div` in `lib/`. The hits are: prose words
("division", "divisor", "divisible"), a comment shorthand list in
`lib/phal.smlib:81` (`phal_janchit_yuj/sub/mul/div/shesh` — where
the real function is `phal_janchit_bhaj`, see below), and a comment
in `lib/ganita.smlib:516` mentioning `sat_div` as a sentinel
comparison. `sat_div` itself is **not defined anywhere** in
`lib/`, `src/`, `examples/`, or `tests/` (tree-wide grep: zero
definitions; the only code-adjacent hit is that one comment) —
confirming Sarvam's correction that it appears only in old
evidence JSON, not as a name to rename.

**What the existing Sanskrit word does:** `bhaj` is already the
division word in every real division function:
`ganita_janchit_bhaj` (truncating divide),
`ganita_paripurna_bhaj` (saturating divide),
`bhaj_urdhva` (ceiling divide, `lib/sadhan.smlib:23`),
`brihat_bhajshesh` (big-number divide with remainder),
`phal_janchit_bhaj` (checked divide).

**Verdict — SAME THING, already done.** The `div`→`bhaj` rename
has nothing to rename in `lib/` except comment prose. Renaming
the prose is harmless; renaming identifiers is impossible because
there are none, and must not be attempted by renaming the
already-`bhaj` functions. **Do not issue a `div` rename.**

### 4. `len` — THE 30 USES ARE MOSTLY A BUILTIN, NOT A LIB IDENTIFIER. Bare `len` is 3 local names.

**What `lib/` actually does:** the 30-count is dominated by
`kosh_len`, which is **a compiler builtin** (`BN_KOSHLEN`,
`src/sutram_compiler.asm:767`, public name `kosh_len` itself),
called from `lib/sankhyiki.smlib`, `lib/kalana.smlib`,
`lib/samanvaya.smlib` and others. Tested: `kosh_len(k)` = 2 for a
2-element kosh, alongside `vartani_aayam("hi")` = 2 — the string
length function is already Sanskrit, the kosh length function is
still English-named. A `len`→`aayam` rename inside `lib/` cannot
touch `kosh_len`: it is a compiler name, and renaming it needs a
compiler change (to e.g. `kosh_aayam`), not a lib edit.

Bare `len` as an identifier appears in lib code at exactly three
sites, all invisible to users: a local in `lib/shreni.smlib:140`
(`vitti len = n`), a parameter in
`lib/samanvaya.smlib:23` (`samanvaya_akar_na(m, n, len)`), and a
parameter in `lib/gudh.smlib:14` (`fnv1a(s, len)`). The rest of
the `len` substrings are prefixed locals (`slen`, `rlen`,
`seglen`, `plen`, `flen`, `hlen`, `nlen`, `splen`, `sflen`,
`keylen`, `len0`, `len1`, `lens`) whose meaning lives in the
prefix ("source length", "pattern length") — renaming the suffix
alone would garble them, and renaming the whole local is a
readability change with zero user-visible effect.

**What the existing Sanskrit word does:** `aayam` as a standalone
word appears **nowhere** in `lib/`, `src/`, or `lang/` except
inside `vartani_aayam` (string length). It is a proposed word,
not an existing identifier. `vartani_aayam` and `kosh_len` are
different functions for different containers, so `aayam` alone
does not replace either.

**Verdict — DIFFERENT KINDS, and the rename as stated misses its
target.** Renaming bare `len`→`aayam` would change 3 local names
and nothing a user sees, while leaving the 30 `kosh_len` calls —
the actual English a user reads — untouched. **If the goal is a
user-visible Sanskrit length, the work is a compiler rename of
`kosh_len` (and a decision on whether `vartani_aayam` and it
should share a name at all), not a lib rename of `len`.**

### 5. `slice` (prose) — CORRECT WORD, PROSE ONLY

`slice` appears in `lib/` only in comments (`lib/khand.smlib` 9
hits, `lib/varna.smlib` 5, plus others: "SLICE-BOUNDARY RULES",
"a slice has no terminator"). No identifier, no function, no
parameter is named `slice`. `vibhag` is the keyword
(`src/sutram_compiler.asm:712`, `kw_vibhag db "vibhag"`), and it
is the right word for the prose concept (a slice is a section of
a larger buffer). **Verdict: SAME THING, prose-only rename —
safe, and the only one of the five that is exactly as the brief
states it.**

## WS1 summary — what Claude should and should not rename

| Brief word | User-visible identifier? | Rename? |
|---|---|---|
| `char` → `akshar` | No — builtins already Sanskrit, three distinct ones | **NO — nothing to rename; `akshar` ≠ `aksharank`** |
| `int` → `anka` | Yes — 2 functions, `brihat_ank_se_int` / `brihat_ank_tak_int` | **NOT to `anka` — to `laghu` pair instead** |
| `div` → `bhaj` | No — division already `bhaj` in all real functions | **NO — nothing to rename** |
| `len` → `aayam` | Bare `len`: 3 locals only. Real English: `kosh_len` builtin | **NO as stated — compiler work, not lib work** |
| `slice` → `vibhag` | No — prose only | **YES, prose only, safe** |

Net: of the five, **one prose rename is safe, one pair of
functions needs a different name than proposed, and three
renames have no target.** Issuing the four renames as stated
would either do nothing, rename invisible locals, or put a wrong
name (`akshar`) on a right function.

## WS2 — the `dasham` precision limitation (one paragraph)

The debug trap prints every `dasham` through `likha`, and `likha`
uses the compiler's fixed-six-decimal float printer
(`src/sutram_compiler.asm:641`, "T12 fixed-six-decimal float
printer"), so a trap shows exactly six digits after the decimal
point and no more: a developer loses everything beyond the sixth
decimal place, including floating-point representation errors
(`0.1 + 0.2` prints as `0.300000`, hiding its true
`0.30000000000000004`), small deltas between iterations, and the
ability to distinguish two values that agree to six places but
differ at the seventh (a buggy π of `3.1415926` and the true
`3.14159265…` both print as `3.141593`). The trap's values are
correct as far as they go; they are simply too coarse to debug
float arithmetic, and fixing that means changing `likha`'s float
format, not the trap.

## WS3 — the guard: this round's number

Method as in R40–R46: committed `./sutram_compiler` (from `HEAD`)
vs a fresh build from `src/r68_compiler_entry.asm`
(byte-identical to the committed binary), every `.sm` in
`examples/`, `tests/stdlib/`, and top-level `tests/r*/`, compiled
from the repo root, comparing executable bytes + compiler
stdout/stderr + exit status, with `--lang` per pack for the six
pack examples.

**Current main `61d5f7b7`: 577 programs, 489 byte-identical
executables, 88 refused identically, 0 DIFFER.** Unchanged from
R45/R46.

## Delivery

- This report: `Muse-to-Sarvam/2026-10-27-round47-rename-meaning-check.md`
- No other files. No tree changes.
- `git push` has no credentials here, as before; delivery via the
  GitHub API. The local tree was left at main, unmodified.
