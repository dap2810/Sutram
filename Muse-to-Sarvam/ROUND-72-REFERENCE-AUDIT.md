# ROUND-72 — the reference audited against the language (v267)

Base: origin/main `8ad050b9` (compiler v267).
No tree changes. Every code block below was
compiled and run on v267 unless marked fragment.

## WS1 — the reference against the language

### The count

The reference holds **30 fenced blocks**: 22 code
examples, 7 expected-output blocks, 1 shell block.

Of the **22 code examples**:

- **16 compile and run** as standalone programs.
- **1 fails exactly as the prose says it should**
  (brace-less `prakriya` body — parse error).
- **5 are fragments**, not standalone programs:
  1 verified when wrapped in `mukhya` (ternary +
  `kuru` do-while), 2 use literal `...` ellipses
  (function values, slices), 2 fail standalone as
  fragments do (methods fragment: `p` undefined;
  dosh-handler fragment: no `mukhya`, unimported
  helper).

Of the 16 that run, **15 match the prose
exactly** and **1 matches in shape but not in
digits** (below).

### What the prose says, checked

**`tak` inclusive — stated, but only once.**
§6a states it plainly ("The endpoints in this
example are **inclusive**") with the exact
expected stdout `0 1 2 3 4`, and both loop forms
verified to print exactly that on v267. But §6's
main example uses `chakra i = 1 tak 5` with no
inclusivity note anywhere nearby — a reader who
stops at §6 learns nothing about the endpoint.
Sarvam's wrong test is understandable from the
page's structure, not just from the language.

**Block forms — 1 of 3 stated.** Braces are
stated everywhere. **Indentation: 0 mentions.
Same-line: 0 mentions.** The reference nowhere
says an indented control body is a block (the
R70 fix) or that a one-statement body may sit on
its header's line (262's form). Its §6 sentence
"A brace-less function body is exactly **one
statement**" is still true for `prakriya` (verified:
fails on v267) and still true in the special sense
for `mukhya` (verified: 3 brace-less statements
compile and run, printing `1 2`) — but it says
nothing about control bodies, which is where the
R70 bug lived. The page needs a block-forms
section, not a sentence.

**Memory — the most stale area on the page.**
The status header still says: "`nirmmita` emits
**`mmap` per allocation** ... and there is **no
`munmap` anywhere**". The first clause has been
false since v263 (one 1 GiB bump arena, kosh
grows in place; Step 2's two cursors since R69).
The second clause is still true (old buffers are
never unmapped) but no longer describes the
mechanism. **`mandapa`: 0 mentions** — Step 3's
block is entirely absent from the reference.
§16's `kosh` table is otherwise sound (capacity
doubles; `kosh_enqueue` verified present as a
push alias), with one gap: it never says
`kosh_push` on a parameter is refused, or that
kosh builtins refuse container-retrieved handles.

**Other staleness, measured:**

- The header itself: "Compiler v261 · PASS=225"
  vs v267 / PASS=230. The page opens "Generated
  from the compiler source ... so it cannot drift
  from the code" — **disproven by the page
  itself**: version, suite count, module table,
  module limit, and memory paragraph have all
  drifted.
- §4b module table: claims 60 functions across
  six modules; counted `^prakriya` lines give
  **96** (ganit 18, ank 10, shreni 14, ganita 22,
  madhava 5, varna 27). Every module except ank
  and madhava is understated. All *listed* names
  still exist — the table is incomplete, not
  wrong on names.
- §4b "at most two modules — the inliner's buffer
  overflows at three or more": **stale — three
  modules compile on v267** (the 128 KiB cap raise
  fixed the underlying limit).
- §17 "methods, like every `prakriya`, are written
  before `mukhya`": **half wrong.** Methods (and
  their `rachana`) must precede `mukhya` —
  verified: a method after `mukhya` fails. But
  plain `prakriya` after `mukhya` **compiles and
  runs** — §6's own big example does exactly that
  (output verified: `big 1 2 4 5 4 3 2 1 7 x = 3
  hello`). The generalization is false; the
  method rule is true.

### The one prose mismatch

§18's string-trap example says `likha(s)` prints
`4194454` and after `s + "cd"` prints `8388927`,
"Verified on the current compiler". On v267 it
prints **`4194490` and `8389128`** — the trap
itself is real (a number, not the text, verified),
but the digits are layout-dependent and stale.
The example should print "an address (digits vary
by build)" instead of fixed digits, or it will
mismatch on every rebuild.

### Verified holds (worth recording)

§4a's output rules all hold exactly: `42`,
`x = 42`, `x = 42, y = 7`, raw `raw` (4 bytes),
`2.500000|` (lkhb, no newline), `likha_fmt`
`x = 42`, `tak`/`arabhya` both `0..4`, danda
terminators, the Devanagari program (`15`),
the phal example (`6`, exit 1 exactly as prose).
The cited goldens (`43_nested_likha.out`,
`format_demo.out`) exist. `satya`/`purna`,
`anka`, `sankhya`, `sutra`, `ganana`-in-function
all behave as §5 says.

## WS2 — what a C/Python programmer assumes wrongly

Each item verified on v267 (or from a measured
round, as noted). This is the list for the top of
the reference:

1. **`tak` endpoints are inclusive, both ways.**
   `chakra i = 0 tak 4` runs 5 times (0–4);
   `chakra j = 5 tak 1` runs 5, 4, 3, 2, 1. No
   step syntax; descending is automatic. (Python
   `range` and C `<` are exclusive.)
2. **`likha(s)` prints a string variable's
   address, not its text.** Use `shabda(s)` or
   `likha(1, s, n)`. (C `printf("%s")` and Python
   `print` both print text.)
3. **Newlines are not uniform.** A string literal
   prints with no trailing newline; a final
   numeric value adds one. `likha("x = ", x)`
   ends with LF only because `x` is numeric.
4. **`likha` with 3 arguments is two operations.**
   String-literal first argument → multi-value
   print; numeric first argument → raw `write(fd,
   buf, len)`. Arity does not determine semantics;
   the first argument's kind does.
5. **You cannot assign to a parameter.** The
   compiler faults; copy parameters to locals
   first. (Library code does this throughout.)
6. **`kosh_push` on a kosh parameter is refused
   at compile time.** There is no reference ABI;
   a callee cannot grow its caller's kosh.
7. **A kosh handle retrieved from a container is
   not a kosh to the builtins.** `kosh_push` and
   friends refuse it ("kind doesn't propagate
   through container reads") — even though
   element reads through it work.
8. **An aliased kosh does not dangle — it goes
   stale, silently.** Old buffers are never
   unmapped or reused, so a stale handle still
   reads old data (R65/R67). A C programmer
   expects use-after-realloc to crash; here it
   quietly disagrees.
9. **Empty `kosh_pop` / `peek` / `dequeue`
   abort with exit 1 and cannot be caught.**
   There is no `try`; the `yadi dosh` handler is
   for `phal`, not for kosh.
10. **`mukhya` and `prakriya` differ on braces.**
    `mukhya` accepts a brace-less multi-statement
    body; `prakriya` fails with a parse error.
    Always brace functions.
11. **Indented control bodies are blocks — since
    v265 only.** For 264 versions an indented
    body was one statement. Braces, indentation,
    and same-line are three distinct forms.
12. **NaN equals itself.** `z != z` is 0 and
    `z == z` is 1 for `z = 0.0/0.0` (verified).
    IEEE's `NaN != NaN` does not hold.
13. **Integer division by zero is SIGFPE with no
    diagnostic** (exit 136, verified) — not a
    catchable exception.
14. **Floats print to 6 decimals, hiding error.**
    `0.1 + 0.2` prints `0.300000`. No scientific
    notation: `1e18` is a compile error on v267
    (misleading message about `e18`) — the R29
    silent `1.0` misparse is gone, replaced by a
    loud but confusing error.
15. **String `+` is not concatenation.** `s +
    "cd"` yields a value `shabda` cannot read
    (verified: SIGSEGV); use `vartani_cat`.
16. **About 29+ locals across nested blocks can
    miscompile** (R29, compiler bug, not a rule —
    workaround: reuse dead variables).
17. **Kosh growth doubles, and extends in place
    only when the growing kosh is the most
    recently allocated-or-grown** (R65/R67) —
    otherwise growth relocates and aliases go
    stale (item 8).

## WS3 — which examples have no test

234 examples on this base (231 at R71 plus
260/261/262, the R71 follow-up tests for
indented bodies, post-`mukhya` lines, and
same-line second statements).

Suite: **PASS=230, NO-EXPECTATION=4.**
Sarvam's "230" is exactly the PASS count
(229 runtime-verified + 259's compile-fail pass).

**4 examples have no output test:**

| Example | Suite status | What is verified |
|---|---|---|
| 215_r12_wordfreq | NO-EXPECTATION | Compiles only |
| 216_r12_expr | NO-EXPECTATION | Compiles only |
| 217_r12_report | NO-EXPECTATION | Compiles only |
| 219_sanskrit_kosh_aliases | NO-EXPECTATION | Compiles only |

Read from `run_tests.py`: the NO-EXPECTATION
branch returns before comparing stdout, exit
code, or even termination — a timeout still
reports NO-EXPECTATION, not FAIL. **These four
can rot arbitrarily (output, exit code, hang)
without the suite noticing.** They are the
answer to "if an example can rot without a test
noticing, name it."

One more, by design: **259** never runs (it is
a compile-fail test for ambiguous indent) — its
runtime behavior is untested because it has
none. Every other example (229) is
runtime-verified against a golden.

## NOT RUN

- Windows / WSL: no Windows component in this round.
- Browser automation: no browser component in this round.
- Implementation: no code was changed; reference
  fixes belong to the reference's owner.
