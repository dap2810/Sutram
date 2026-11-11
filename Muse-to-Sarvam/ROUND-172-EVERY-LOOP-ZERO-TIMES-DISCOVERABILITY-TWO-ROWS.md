# ROUND-172 — every loop form, for the same defect; is zero iterations ever right; the discoverability finding; the two audit rows that are wrong

**Base:** main at v315, tip commit `46bc76c7` · **Deliver into:** `Muse-to-Sarvam/`

**Read only. Nothing compiled or run.** "R:" = `docs/LANGUAGE-REFERENCE.md`,
"C:" = `src/sutram_compiler.asm`, "A:" = `src/r65_arena.inc`. Every line
number below was re-grepped on the tree cited; every count re-derived. The
audit is ChatGPT's ROUND-233 (`ChatGPT-to-Sarvam/ROUND-233-AUDIT.md`, 47
findings: Tier 1 = 14, Tier 2 = 7, Tier 3 = 26); R171 re-ranked it (10 stay
Tier 1, 4 demote to Tier 2, one promotion R09; re-ranked totals 11/11/25).
Claude's R189-00 handoff and its evidence programs
(`Claude-to-Sarvam/evidence-r189/programs/`) were read for what he measured;
every verdict below comes from my own reading of the code, and where his
reading and mine differ I say so. The staged v325 is commit `22466bda`
(branch `r189-audit-fixes`); v324 is `e1f29f14`. Where a behaviour or a
document differs between main and v325, both are stated.

The parent verified the decisive claims independently before writing this
report. One could-not-determine from the working notes is resolved here:
the v325 books' "Descending Loops" section was **not** corrected — the
English book still says the sentence at :400 (see Task 2). One line
number is corrected: the `kuru` "body start: executes at least once"
comment is at C:20886, not :20887.

The defect, from the brief: a `chakra` counts down only when both its ends
are written as numbers; `chakra i = 5 tak e` with `e = 3` runs NO times,
silently. This round reads every loop form for the same defect.

---

## Task 1 — every loop form, for the same defect

The language has exactly **three** loop forms. The AST enum (C:87–120)
defines three loop node types and no others — `AST_FOR` (20), `AST_WHILE`
(6), `AST_DO_WHILE` (28) — and the statement dispatch (C:14890–14940)
routes exactly three keywords to loop parsers: `chakra` (KW_PUNARAVARTANA,
whose word is `chakra`, C:1335) → `.ps_for`, `yavat` → `.ps_while`,
`kuru` → `.ps_do_while`. There is no fourth loop form: no step form, no
loop over a `kosh`/`mala`/slice, no loop with a condition only besides
`yavat`, no `for each`. `guna` is a switch (desugared to an if-elif chain),
`yadi dosh` is a handler, recursion is not a loop form. Every form below
was read from the parser and the codegen, not from a list in a brief or a
handoff.

### Form 1 — `chakra` with `tak` (AST_FOR)

**(1) The form and its syntax.** `chakra i = <start> tak <end> { <body> }`
(C:15416–15530, `.ps_for`). The parser accepts three spellings of the
middle word: `tak`, `arabhya … paryantam` (C:15455–15470, R52), and the
loaded language pack's native word for "to" (C:15480–15495). All three
build the same node: `[AST_FOR][var_name][start_expr][end_expr][body][0]`
(C:15519–15524), with `[rax+40]` set to 0 and the comment "no step yet".
Start and end are arbitrary expressions (`parse_expr`) — literals, variables, calls, arithmetic, `sutra` constants. The
counter is a `vitti` (whole number); a `dasham` counter, start, or end is
refused at codegen with `E_CHAKRA_DASHAM` (`r96_check_for_float`,
C:8863–8900 — the check that caught the pre-v283 bug where `3.0` was
compared as its IEEE-754 bits and the loop never stopped). The loop
variable is an ordinary variable (C:20299–20320: `lookup_var` or
`alloc_var`, bound as a number by `r126_bind`); the body may assign to it,
and a `chakra i` over an already-visible `i` reuses it (C:15430–15440).

The codegen (`.gs_for`, C:20255–20528) is test-at-bottom with one initial
jump to the test (C:20339–20347: "Zero-iteration correctness: skip the
body and test the bounds first"), then the body, then the increment or
decrement by exactly 1 (C:20355–20383: `OP_ADD`/`OP_SUB` with immediate 1;
no step is ever read), then the signed comparison and backward branch
(ascending `jle body_start`, C:20467; descending `jge body_start`,
C:20465–20470). **Direction is decided at compile time, and only when
both bounds are literal numbers**: C:20270–20287 — if the start node and
the end node are both `AST_NUM` and start > end, the global `for_descend`
is set to 1; otherwise the loop counts up. `for_descend` is read and
written nowhere else in the compiler (C:840, C:20272–20465), and no check
pass ever looks at a `chakra`'s bounds — the only bounds-related check in
the whole compiler is the `dasham` refusal above.

What counts as a "written number" for that test is wider than two
literals, and narrower than any value the compiler can see:

- A literal is `AST_NUM` (C:20272–20279 checks the node type directly).
- Arithmetic on literals folds to `AST_NUM`: `fold_const` (C:16802–16890)
  replaces a `BINOP` whose operands are both `AST_NUM` with the computed
  `AST_NUM`, and is called from the additive and multiplicative parse
  loops (C:16725–16728, C:16787–16789). So `0 - 5` is `AST_NUM(-5)`,
  and `chakra i = 5 tak 0 - 5` counts down. A constant expression past
  int64 is refused (R80, C:16883).
- A unary minus on a literal negates it in place to `AST_NUM`
  (C:17084–17125: "Negate constant"), so `chakra i = 5 tak -3` counts
  down. A unary minus on a non-constant becomes `BINOP(0 - expr)`, which
  `fold_const` then folds if the operand is constant.
- A top-level `sutra` constant is substituted by its initializer AST at
  the point of use (`.pp_ident`, C:17363–17377: "Resolve previously
  declared top-level sutra symbols before building an AST_VAR"). So
  `sutra E = 3` followed by `chakra i = 5 tak E` counts down, because the
  end node IS `AST_NUM(3)`; `sutra E = 0 - 3` likewise (the initializer
  was folded when parsed). A `sutra` whose initializer is a variable or
  a call does not count.
- A local variable never counts, even when its value is obvious:
  `vitti e = 3` on the previous line leaves the end node as `AST_VAR`,
  so `chakra i = 5 tak e` counts up. There is no constant propagation for
  locals anywhere in the compiler — the three mechanisms above are the
  whole list.

The trap is symmetric, and the brief's case is only half of it: direction
detection needs BOTH ends to be numbers. `chakra i = n tak 1` with `n = 5`
also runs zero times (start is a variable, so the loop is ascending, and
`5 <= 1` is false on entry), and so does `chakra i = 5 tak f()` where `f()`
returns 1 (a call end is not a number either).

**(2) What it does when the bounds are equal.** Exactly one pass, in
either direction. Ascending: the entry test `i <= end` is true, the body
runs, the increment makes `i = end + 1`, the test fails. Descending
(constant equal bounds): `jge` true once, then the decrement fails it.
`chakra i = n tak n` with a variable `n` also runs once.

**(3) What it does when the start is past the end.** Depends entirely on
how the bounds were written:

- Both bounds written as numbers and start > end: counts **down**,
  `start - end + 1` passes, inclusive at both ends. `chakra j = 5 tak 1`
  gives 5 4 3 2 1.
- Either bound a variable, a call, or any non-number expression, and
  start > end at run time: runs **zero times, silently**. The entry jump
  goes to the test, `start <= end` is false, the body never runs, no
  message, exit 0. This is the defect: `chakra i = 5 tak e` with `e = 3`
  (the brief's case; Claude's evidence program
  `chakra_var_end.sm` is exactly this, counting `n = 0` passes), and
  equally `chakra i = n tak 1` with `n = 5`.
- Start past the end at the int64 edge: an ascending loop ending at MAX
  never terminates (R171 R33 — after the body at MAX the increment wraps
  MAX to MIN, `MIN <= MAX` stays true); a constant descending loop ending
  at MIN likewise never terminates (the decrement wraps MIN to MAX).
  Claude's R189 gate pins the MAX case (`chakra-to-max`:
  `9223372036854775805 tak 9223372036854775807` "does not stop by itself",
  stopped at 11 passes in the test).

**(4) Whether the bound may be an expression, and whether that changes
the answer.** Yes — both bounds are arbitrary expressions, and it changes
the answer in three ways:

- **Direction:** only a bound that parses (after folding and `sutra`
  substitution) to `AST_NUM` participates in direction detection. A
  variable, a call, a field, an index — anything else — makes the loop
  ascend. So `chakra i = 5 tak n - 1` with `n = 3` ascends and runs zero
  times (end is `BINOP(n, -, 1)`, not `AST_NUM`), while `chakra i = 5 tak
  3 - 1` descends (folds to `AST_NUM(2)`) and runs 5 4 3 2.
- **Evaluation timing:** the start is evaluated **once**, before the loop
  (C:20299–20320: `gen_expr` on `[rbx+16]`, stored into the counter). The
  end is evaluated **every pass**: in the slow path (C:20418–20446) the
  end expression is re-generated at the bottom test on every iteration,
  and in the fast path (C:20400–20412, end is an `AST_VAR` with a register
  location) the variable's current value is compared each pass. So a call
  end such as `pankti_gan(s)` runs on every pass (the 0-to-`n-1` examples
  below use exactly this), and **the body can move the end**: `n = 5`
  inside `chakra i = 1 tak n` changes the end — Claude's v325 §6a says
  this, and the code agrees. The body can likewise move the counter
  itself (it is an ordinary variable), and the test reads the new value.
- **The start is frozen:** because the start is evaluated once and stored,
  a body assignment to the start variable does not restart the loop — only
  the counter and the end are live.

**(5) Whether the reference says any of this.** On main, **no**. The
reference §6a (R:578–627) states: the two spellings, the exact expected
output `0 1 2 3 4`, "counts in whole numbers (v283)", steps by 1, the
`E_CHAKRA_DASHAM` refusal with its history, "To step through decimals,
use `yavat`", and "The endpoints in this example are **inclusive**"
(R:625). It says nothing about how direction is decided, nothing about
variable bounds, nothing about zero iterations, nothing about the end
being re-read. The only descending example anywhere in the reference is
R:515, `chakra j = 5 tak 1 { # for (descending)` — both ends written as
numbers, with no comment that the form is what makes it descend. The
books say the same, and worse: both books have a "Descending Loops"
section (English book :397–398, Sanskrit :354) stating unconditionally,
"If the start value is greater than the end value, the loop counts down
automatically", illustrated only by `chakra i = 5 tak 1`. That sentence
is false as a general claim — it holds only when both ends are written as
numbers — and it is the sentence a student generalises from. On v325
Claude states the rule in §6a (v325 R:673–680): "Which way a `chakra`
counts is decided when it is compiled, not when it runs. It counts down
only when both ends are written as numbers (or as arithmetic on numbers,
such as `0 - 5`) and the start is the larger… If either end is a variable
or a call, it counts up — and when the start is already past the end it
runs no times, with no message… To count down from a variable, use
`yavat`." That paragraph matches the code exactly on all four points
(direction at compile time; numbers only; zero times silently; `yavat` as
the workaround), and it also states the end re-read ("Both ends are
included, and the end is read again on every pass") and the MAX wrap. The
books on v325 still carry the uncorrected "Descending Loops" sentence
(English book :400 — verified by the parent; see Task 2).

### Form 2 — `yavat` (AST_WHILE)

**(1) The form and its syntax.** `yavat (<condition>) { <body> }`
(C:15776–15810, `.ps_while`). The condition is an arbitrary expression
(`parse_expr`, C:15787); the node is `[AST_WHILE][cond][body]`
(C:15799–15803). No counter, no bounds, no step. The codegen
(`.gs_while`, C:20658–20875) is test-at-bottom with one initial jump to
the test (C:20670–20679: "One-time entry jump to the bottom test"), then
the body, then the condition re-evaluated (C:20682–20684: "the condition
runs every pass, so it is in the loop" — the parse comment at C:15783),
then a backward branch while the condition is true. A string as a whole
condition is refused when the compiler knows it is one
(`E_VARTANI_SATYA`, `rfx_check_truth`, C:9477–9493 — see Task 4, R19, for
the scope of that refusal: it covers only values the compiler knows are
strings).

**(2) What it does when the bounds are equal.** There are no bounds. The
analogous question is a condition that is true exactly once: the body runs
once, the condition is re-evaluated, it fails, the loop ends. One pass.

**(3) What it does when the start is past the end.** There is no start or
end. A condition that is false on entry runs **zero times, silently** —
and that is the correct, documented, expected behaviour of a while loop:
the entry jump goes to the test first. `yavat (0)` runs zero times;
`yavat (i < 0)` with `i = 0` runs zero times; `yavat (i < kosh_len(k))`
with an empty `kosh` runs zero times. No message, exit 0 — and no
surprise, because the form's entire meaning is "run while this is true".

**(4) Whether the bound may be an expression, and whether that changes
the answer.** The condition is an expression, evaluated **every pass** —
including the entry test. A call in the condition runs on every pass; a
variable is re-read on every pass; a body assignment to a variable in the
condition changes the next test. Constant conditions are not special-cased
in the codegen (there is no constant-condition branch in `.gs_while`):
`yavat (1)` loops for ever, `yavat (0)` runs zero times, exactly as the
values say. A `dasham` condition is allowed (`yavat (x <= 3.0)` is the
reference's own example for stepping through decimals, R:615–620) —
unlike `chakra`, where a `dasham` bound is refused.

**(5) Whether the reference says any of this.** The reference says
almost nothing about `yavat` as a form: it appears in the §6 example
(R:520, `yavat (k < 3)`), in §6a-2's indentation example (R:633–636), in
§6c (R:670, a `yavat` over raw memory), and in the §5a refusal table
(R:469: a string as a whole condition is refused). There is no §6
subsection for `yavat` at all — no statement that the condition is tested
before the first pass, no statement that a false condition means zero
passes. The books teach it in one sentence each (English ch. 6 :182:
"`yavat` (as long as) is the while loop"), with no example of a
zero-pass loop. That omission is harmless here: "as long as" states the
semantics, and zero passes on a false condition is what "as long as"
means. The reference's silence on `yavat` is not a defect of the same
kind as its silence on `chakra` — nothing in the reference or the books
misstates `yavat`'s behaviour.

### Form 3 — `kuru … yavat` (AST_DO_WHILE)

**(1) The form and its syntax.** `kuru { <body> } yavat (<condition>)`
(C:15805–15845, `.ps_do_while`): "Sanskrit-only do-while form: body
executes once before the test." The node is `[AST_DO_WHILE][body][cond]`
(C:15838–15841). The codegen (`.gs_do_while`, C:20875–20945) has **no
entry jump**: the body start is the entry point (C:20886: "body start:
executes at least once"), then the condition is evaluated and a `jne`
branches back to the body while it is true. A string condition is refused
the same way as in `yavat` (the same `rfx_check_truth` call path — the
condition node is generated by `gen_expr` at C:20892 with the truth check
applied in the statement walk).

**(2) What it does when the bounds are equal.** There are no bounds. The
body runs once and the condition is then tested; if it fails, exactly one
pass.

**(3) What it does when the start is past the end.** There is no start or
end, and the form **cannot run zero times**: the body executes at least
once by construction, whatever the condition is. `kuru { … } yavat (0)`
runs exactly once. This is the only loop form in the language with a
minimum of one pass, and the only one that can never exhibit the
zero-times defect.

**(4) Whether the bound may be an expression, and whether that changes
the answer.** The condition is an expression, evaluated after every pass
(including the first). A call in it runs after every pass; a variable is
re-read after every pass. Nothing about the condition can make the first
pass not happen.

**(5) Whether the reference says any of this.** The reference mentions
`kuru` in the keyword table (R:54: "`kuru` | do-while (with `yavat`)"),
in the §6 example (R:541–543), and in §6a-2's list of later additions —
but there is no section that states the body runs once before the test.
The books teach it only in the "Later additions" section (English
:419–430, Sanskrit equivalent), as a bare example with no explanation of
the once-before-the-test semantics. The code's comment says it plainly
(C:15809); neither book nor reference does. A student who has not read
the code cannot tell from the books whether `kuru` tests first or runs
first — but the failure mode is benign (one extra pass, not a silent
zero), so this is a documentation gap, not a Tier 1 defect.

### `krama` and `agrim`

`krama` (break) and `agrim` (continue) are statements, not loop forms
(C:15600–15624, `.ps_krama` / `.ps_uddeshya` — the continue keyword's
word is `agrim`, C:1340; the internal name `UDDESHYA` is a legacy label).
Both build a bare node (`AST_BREAK` / `AST_CONTINUE`, C:107–108) and call
`r73_wrap_jump`, which rewinds any `mandapa` blocks between the jump and
its loop (C:8438–8460). Codegen: `krama` emits `jmp rel32` patched to the
innermost loop's end (`.gs_break`, C:20529–20547); `agrim` emits
`jmp rel32` patched to the innermost loop's continue target
(`.gs_continue`, C:20551–20566). The continue target differs by form: in
a `chakra` it is the induction update (C:20348–20354: "continue in a
for-loop means perform the induction update, then test"), so `agrim` in a
`chakra` still increments and tests; in a `yavat` it is the bottom test
(C:20826–20866); in a `kuru` it is the condition evaluation (C:20917–
20933). Patch counts are saved and restored per loop, so each jump
targets the innermost enclosing loop only.

**Can they make a loop run zero times? No.** Neither executes before the
body has started: a `krama` or `agrim` on the first line of a body runs
after the body has begun, so the loop has already run at least a partial
pass. What they can do is end a loop early (`krama` on the first pass
with a condition true means the loop did one partial pass and no more) or
skip the rest of a pass (`agrim`). They cannot cause the zero-pass case,
and they change none of the answers above — except one interaction worth
recording: in a `chakra`, `krama` jumps to the loop end and **skips the
increment** (the jump target is past the update), while `agrim` jumps to
the update. Neither skips the test.

**Side finding, read from the code:** `krama`/`agrim` outside any loop
are **not refused anywhere** — there is no loop-depth check in the parser
(`r73_wrap_jump` returns at once with "not in a loop of this prakriya:
nothing to leave", C:8440–8442) and no error text for it exists in the
compiler. `.gs_break` emits its `jmp rel32` and records a patch position
that no enclosing loop ever patches, so the displacement stays 0 and the
jump falls through to the next instruction: a stray `krama` compiles
silently and does nothing. That is a silent no-op, not a silent wrong
answer, and it is outside this round's question; recorded here because the
reading surfaced it.

### A `chakra` that steps by more than one

**It does not exist.** There is no step syntax in the parser: the only
step-like token in the whole compiler is the AST node's `[rax+40]` slot,
which the parser sets to 0 with the comment "no step yet" (C:15524), and
which the codegen never reads — the increment is hardcoded as immediate 1
(C:20355–20383). There is no step word in the language: "kadam" appears
nowhere in the compiler, the reference, or the books (grep: 0 hits), and
no other candidate word (`padas`, `kram`) is a step keyword either. The
reference states the fact without quite saying it is the only fact:
"A `chakra` counts in whole numbers… Its counter is a `vitti` and steps
by 1" (R:604–605). A student who wants to step by 2 must write the step
by hand — typically `chakra i = 0 tak 2 * n` with `i * 2` inside, or a
`yavat` with an explicit increment — and the books never show that
either.

### Summary — which forms can run zero times silently

| Form | Can run zero times? | Silent? | The defect? |
|---|---|---|---|
| `chakra`, both bounds written as numbers, start > end | No — counts down | — | No |
| `chakra`, both bounds written as numbers, start == end | No — one pass | — | No |
| `chakra`, either bound a variable/call/expression, start > end at run time | **Yes** | **Yes — no message, exit 0** | **Yes — this is the defect** |
| `chakra`, either bound a variable/call, start <= end | No — runs normally | — | No |
| `chakra`, ascending to MAX | No — never terminates (worse) | N/A | R171 R33, separate |
| `yavat`, condition false on entry | Yes | Yes, but correct — the form means "while true" | No |
| `yavat`, condition true exactly once | No — one pass | — | No |
| `kuru … yavat`, any condition | No — at least one pass by construction | — | No |
| `krama` / `agrim` | Cannot cause zero passes | — | No (stray `krama` outside a loop is a silent no-op — side finding) |
| Step form | Does not exist | — | No |

**Agreement with Claude's R189-00:** his handoff states the same rule
("The direction is decided when the program is compiled, and only when
both ends are numbers (`0 - 5` counts: it is folded). With a variable or
a call at either end the loop counts up") and the same consequence
("`chakra i = 5 tak e` with `e = 3` runs no times. No message."). My
reading agrees on every point, with three additions he does not state:
(1) the trap is symmetric — a variable *start* with a constant end
(`chakra i = n tak 1`, `n = 5`) also runs zero times; (2) `sutra`
constants and unary-minus literals also count as "written numbers", via
substitution and negation-in-place; (3) the end is re-evaluated every
pass while the start is evaluated once, so the body can move the end but
not the start. His gate pins the three cases (written-ends-down,
variable-end, to-max) in `tests/r189/test_audit_fixes.py:37–43` on v325.

---

## Task 2 — is zero iterations ever right?

### (1) Which loop forms can be legitimately empty, and which cannot?

- **`yavat`: legitimately empty, by design.** The form's meaning is
  "run while this is true", and a false condition on entry is the normal
  empty case. The legitimate form in this language is a loop over a
  collection's length: `yavat (i < kosh_len(k))` runs zero times for an
  empty `kosh`, and that is correct — there is nothing to do. The same
  holds for a `yavat` guarding any count that may be zero.
- **`kuru … yavat`: never empty, by construction.** One pass minimum.
  There is no legitimate-empty case and no empty case at all.
- **`chakra`: both.** The legitimate-empty `chakra` is the 0-to-`n-1`
  shape, and it is the most common loop in the tree: `chakra i = 0 tak
  n - 1` (examples 246, 249, 250), `chakra i = 0 tak pankti_gan(s) - 1`
  (examples 248, and 246:50 — a *call* end, re-evaluated every pass).
  With `n = 0` or an empty collection, these run zero times, and that is
  correct — there are zero elements to visit. The illegitimate-empty
  `chakra` is the countdown shape: `chakra i = 5 tak e` with `e = 3`,
  `chakra i = n tak 1` with `n = 5` — the author expected passes
  (three, five) and got none. The two cases are the same shape at run
  time: start > end, variable end, ascending. The difference is only the
  author's intent, which is not in the program.

That last sentence is the whole answer to the next question. The
legitimate-empty `chakra` and the silent-zero `chakra` differ in
nothing the compiler can see: both are "start > end with a variable
end". The only visible difference is the *start value* — 0 in the
legitimate case, 5 in the broken one — and that is not a rule: a loop
from 5 to `n - 1` with `n = 3` is the same defect with a different start,
and a loop from 0 to `n - 1` with `n = 0` is legitimate with start 0.
No start-value rule separates them.

### (2) Is the compiler able to tell the difference, or does it need the programmer to say?

**It cannot tell, and it needs the programmer to say.** What the
compiler has at the point it emits the loop (`.gs_for`, C:20256):

- **The node types of the two bounds** — `AST_NUM` or not, after
  `fold_const`, unary-minus negation, and `sutra` substitution. That is
  all the static information there is. There is no constant propagation
  for locals: `vitti e = 3` on the previous line is still `AST_VAR` at
  the loop. There is no range analysis, no value tracking across
  statements, no knowledge of a collection's length (`kosh_len` is a
  runtime call; the hoist scan knows declarations, not lengths).
- **No existing refusal for a provably-empty loop.** There is no check
  on a `chakra`'s bounds anywhere except the `dasham` refusal
  (`r96_check_for_float`). `for_descend` is set and read only inside
  `.gs_for`. Nothing in the check passes (R7/R4/R96/R126) compares a
  start with an end, even when both are constants — and for constants
  there is nothing to refuse anyway, since constant bounds always count
  down or run once.
- **No warning machinery to use.** The only warning in the language is
  the R111 deprecation warning (`Sutram suchana: 'kosh_push' purana
  nama…`, C:980, C:33035, C:33315) — three hits, all about old names.
  There is no "this loop may run zero times" warning, no warning
  infrastructure for a new one to join, and no precedent for a
  compile-time warning that is not a renamed builtin.

What the compiler *could* decide statically is only the constant case,
and the constant case is already safe: both bounds constant and
start > end counts down; equal constants run once. Everything else is a
value known only at run time. And at run time the two cases are
indistinguishable too: `0 tak -1` (legitimate empty) and `5 tak 3`
(broken countdown) are both "start > end, ascending". A runtime check
"refuse when start > end" would refuse the legitimate empty loop; a
runtime rule "count down when start > end" would make `0 tak -1` run
twice (0, then -1) — which is Claude's stated reason for not changing
it, and he is right: the 0-to-`n-1` idiom is the most common loop in the
tree, and it would break on every empty collection. The compiler cannot
tell; the programmer has to say — and today the language gives the
programmer no way to say it: there is no step form, no direction word,
no "downto" spelling. The only way to count down from a variable today
is `yavat` with an explicit decrement, which the v325 reference now
states.

### (3) If the compiler cannot tell, refusing a legal program vs documenting the trap — which is right for a beginner?

**Document, and document it where the student is looking — but document
knowing it will not reach every student, and say so.** Refusing is the
wrong choice here, for three reasons that all come from the language's
own precedents:

- **A refusal would refuse a legal, common, correct program.** The
  0-to-`n-1` loop with `n = 0` is not an edge case; it is how every
  loop over a collection is written (examples 246, 248, 249, 250). A
  refusal on "start > end" would make empty collections a compile
  error, which is worse than the defect it fixes: it would teach the
  student that empty is an error, and it would break programs that are
  right. The R126/R82 doors are the precedent the brief names, and they
  cut the other way: they refuse programs that are *never* right (a
  `kosh` escaping its block, a slice passed where a number is expected).
  A `chakra` with start > end is *sometimes* right, and the compiler
  cannot tell when. A door that cannot tell right from wrong is not a
  door.
- **A refusal cannot say anything teachable.** For a refusal to teach,
  it would have to name the actual situation: "this `chakra` counts up
  because its end is a variable, and its start is already past its end —
  if you meant to count down, use `yavat`; if you meant zero passes,
  this is fine and you should say so". But the compiler cannot know
  which of those two the student meant, so any message it emits would be
  a guess, and a guessed error message on a correct program is the worst
  kind of teaching: it tells the student their right program is wrong.
  The language's existing refusals work because each names a definite
  fact (`E_KOSH_MANDAPA`, `E_VARTANI_SATYA`, `E_CHAKRA_DASHAM`); this
  one would name a suspicion.
- **The guard's DIFFER rules point the same way.** The guard refuses to
  silently re-baseline; it does not refuse programs. The precedent is
  that a behavioural trap gets stated, measured, and pinned in a gate —
  exactly what Claude did in v325 (stated in §6a, pinned in
  `tests/r189/test_audit_fixes.py`).

**What the documentation has to say to actually reach a student who has
not read it.** Three things, and the v325 §6a paragraph does the first
two but not the third:

1. **The rule, in the loop section, in one sentence:** "A `chakra`
   counts down only when both ends are written as numbers." (v325 §6a
   does this.)
2. **The failure, named as a failure:** "If either end is a variable or
   a call, it counts up — and when the start is already past the end it
   runs no times, with no message." (v325 §6a does this.)
3. **The correction of the sentence that teaches the opposite.** Both
   books' "Descending Loops" section says unconditionally, "If the
   start value is greater than the end value, the loop counts down
   automatically" (English :397–398, Sanskrit :354), illustrated only
   by `chakra i = 5 tak 1`. That sentence is what a student
   generalises from, and it is false as written. Until it says "when
   both ends are written as numbers", the documentation does not reach
   the student — it misleads them. The fix is one sentence in each
   book, in the section the student actually reads (ch. 13/14's
   reference material, not only §6a of the reference). **And it is
   still not done: the v325 English book still carries the sentence at
   :400, verbatim.** The v325 reference states the rule; the v325 books
   still teach the opposite. A student who has not read the reference
   will still hit the trap; that is the honest limit of documentation,
   and it is why the gate pins the behaviour — so the trap stays stated
   even when the student has not read it.

**My view, stated plainly:** document, do not refuse — and fix the
books' "Descending Loops" sentence, because that sentence is the trap's
carrier. If the owner ever wants more than documentation, the honest
shape is not a refusal but a way for the programmer to say the
direction: a step or direction spelling the language does not have.
That is a language change, not a fix, and it belongs to the owner, not
to a round.

---

## Task 3 — the discoverability finding

### Where a student would look for "read a number the user typed"

**The books (main, v315).** There is no input chapter. Input is taught
in ch. 14, "More of the language: comments, shortcuts, the library"
(English :361), and in ch. 13's reference table. What each place
contains:

- **Ch. 13 Complete Reference, the builtin table (English :346):** one
  row — "`grahan` | read input (-1 on EOF)". Nothing about text, nothing
  about conversion.
- **Ch. 14, "`grahan()` and end of input" (English :409–411):** "When
  input ends, `grahan()` now returns `-1`, so programs can exit cleanly",
  with a `yadi (a == -1)` loop-exit example. That is the whole of the
  input teaching on main.
- **Ch. 14, "The standard library" (English :436–437):** "Sutram ships
  a small standard library that you pull in with `yoj`. … Twelve modules
  ship today, and the full suchi is in `docs/sutram-stdlib.html`." Twelve
  is stale (24 modules, 310 functions — R170/R169), and no module is
  named here; `vakyank` is never named anywhere in either book (0 hits).
- **`vartani_grahan`: 0 hits in either book on main. `varna_tak_ank`:
  0 hits in either book on main.** On main the student cannot find
  either name in the books at all.
- **There is no index in either book** — "index" occurs only as CSS
  `z-index` and as the word "indexing" in prose. A student cannot look
  a function up; they can only read chapters in order.

**The reference (main).** One row: R:178, "`grahan` | read a number from
input". `vartani_grahan`: 0 hits on main (BN 48 was built in v323,
staged, not merged). `varna_tak_ank` appears twice, neither as an entry
a student could use: R:142 (a failure-contract row for
`varna_tak_dashm`) and R:263 (a rename-table row). The §4b table says
"60 functions across six modules" — stale against 24/310.

**The books and reference on v325** teach `vartani_grahan` but still not
the converter. Both v325 books have 6 mentions of `vartani_grahan` each:
the ch. 13/14 table row ("read a line of text from input", English
:347) and the section "Reading text: `vartani_grahan()`" (English
:419–430, Sanskrit :377–386) — a name example and a read-to-the-end loop
with `nivesha_anta()`, followed by a "Reading a file" section. The v325
reference gains §4d (v325 R:374), a table with `grahan()`,
`vartani_grahan()`, and `nivesha_anta()` side by side with exact
behaviour ("`hello` gives 0; `12 34` gives 1234"; "a new string: the
line without its newline"). `varna_tak_ank`: **still 0 hits in either
v325 book**, and no row in the v325 §4d table. The converter remains
undiscoverable even on v325.

### Is there any example in the 331 that reads a line and converts it?

**No — not in examples, tests, or the books, on main or on v325.**
Counts, re-derived on main (331 top-level `.sm`, 347 recursive):

- `vartani_grahan` in `examples/` and `tests/`: **0 hits** on main. It
  cannot appear — the builtin did not exist on main.
- `varna_tak_ank` in `examples/` and `tests/`: **4 hits, all in
  `tests/stdlib/`** (`r8_base_digits.sm`, `strconv_base.sm`,
  `strconv_int_str.sm`, `strconv_overflow.sm`). All four are proof files
  that build their input with `ank_tak_varna` (number-to-text) and
  convert it back — none reads from input. `strconv_int_str.sm` in full
  is: `yoj vakyank`, a `nirmmita(30 * 8)` buffer, an `ok` cell, and calls
  of `varna_tak_ank(buf, n, ok)` on buffers filled by `ank_tak_varna`.
  No `vartani_grahan`, no user input anywhere in the four.
- On v325, `vartani_grahan` appears in three examples —
  `360_r184_vartani_grahan.sm` (reads a name, greets it),
  `361_r184_pankti_ganana.sm` (counts lines), `363_r186_pankti_ganana_patra.sm`
  (counts a file's lines) — and in `tests/r184/test_read_line.py` and
  `tests/r186/test_grahan_and_files.py`. None of the three examples
  converts a line to a number; none calls `varna_tak_ank` or any
  converter. The three-line program the owner wants does not exist
  anywhere in the tree.

### The three-line program, written out (not run)

The owner wants: read a line with `vartani_grahan`, convert it with
`varna_tak_ank`, print the number. As the owner imagines it, that is
three lines. As the language actually is, it is not — because
`varna_tak_ank` does not take a string. It takes a `mala` of character
codes, one code per eight-byte cell (`lib/vakyank.smlib:81–137`:
`src[p]` reads cells; a string passed directly would be read eight
bytes at a time as "codes", which is wrong). There is no library
function that turns a string into a `mala` of codes (grep: none). So the
honest program is:

```sutram
yoj vakyank

mukhya() {
    vitti s = vartani_grahan()
    vitti n = vartani_aayam(s)
    vitti buf = nirmmita(n * 8)
    chakra i = 0 tak n - 1 {
        buf[i] = akshar(s, i)
    }
    vitti ok = nirmmita(1 * 8)
    vitti v = varna_tak_ank(buf, n, ok)
    yadi (ok[0] == 1) { likha(v) }
}
```

Fourteen lines, not three — and it converts ASCII digits only (a
Devanagari digit's bytes are continuation bytes, which `varna_tak_ank`
refuses via `ok[0] = 0`).

**What a student would need that the books do not teach — count the
untaught pieces (main; v325 in brackets):**

1. `yoj vakyank` — the module name. The books never name `vakyank`
   (0 hits on main and on v325); the ch. 14 library section names no
   module and points at a page that lists 24.
2. `vartani_grahan` itself — 0 hits in the main books [taught on v325,
   ch. 14 "Reading text"].
3. `vartani_aayam(s)` for the length in bytes — 0 hits in either book
   on main and on v325. (And its unit is bytes, which the reference
   does not state in the row — R171 R07.)
4. The `nirmmita(n * 8)` cell buffer — `nirmmita` is taught (20 hits
   main EN, 22 on v325), but only in the memory chapter (ch. 19); a
   student in ch. 14 has not met it as a tool for building a `mala`.
5. The `akshar(s, i)` copy loop — `akshar` appears once in the main EN
   book (3 times on v325), in a table, never as a loop that fills a
   buffer.
6. The `ok[0]` check — the one-cell-`mala`-as-flag pattern: 0 hits for
   `ok[0]` in either book on main or v325. No book teaches that a
   function answers through an argument.
7. The fact that `varna_tak_ank` wants codes-per-cell, not a string —
   stated only in the library header comment (`lib/vakyank.smlib:81–82`);
   0 hits in the books and no row in the reference §4b table.

**Seven untaught pieces on main; six on v325** (only `vartani_grahan`
itself is taught there). The three-line program the owner wants does
not exist because it cannot be written in three lines with the library
as it is — the string-to-codes step is missing, and every step of it is
untaught.

### What v325 adds

**No converter and no example.** Claude's R189-00 handoff title says
"ADD-A-CONVERTER", but its body says the opposite: "The `grahan`
converter is not built — you said not to until I had said which; three
choices are the owner's" (name; how it says "not a number"; what counts
as a number). On the v325 tree: the `lib/` file list is the same as
main's (no new module, no new function) — two files change, both audit
fixes (`lib/ganit.smlib`: the R16 LCM guard; `lib/brihat.smlib`: the R14
digit guard) — there is no `BN_ANK` or `ank(` converter builtin in the
compiler, and no example reads a line and converts it. What v325 does
add is the *discoverability* half: the §4d input table in the reference,
the "Reading text" section in both books, three `vartani_grahan`
examples (360, 361, 363), and the R189 gate. The title overstates the
branch; the branch itself does not build the converter. That is a
handoff-title correction, not a code finding: the title promises a
converter the branch does not contain.

---

## Task 4 — the two audit rows that are wrong

Claude disputes exactly two numbered audit rows, both in the "Where the
audit is wrong" section of his R189-00 handoff: **R19** and **R18**.
(His R188-00 handoff disputes one further audit claim — finding B, the
changelog — which is not a numbered row; it is recorded separately below.
Finding A in the same handoff he agrees with.)

### R19 — "an empty string is still true in `yadi (s)`" — CLAUDE RIGHT

**ChatGPT's claim (audit row R19, Tier 3):** "Contradictory condition
claim: R:490 says `yadi(s)` is true even for an empty string →
C:9477–9493 refuses inferred-string conditions with `E_VARTANI_SATYA`,
as R:469 already correctly says; remove the older claim rather than
weaken the refusal."

**Claude's counter-claim (R189-00, "Where the audit is wrong"):** "It is
true where it stands. The sentence is about values the compiler does
*not* know are strings. `vitti g = ""` at module level, then `yadi (g)`:
**compiles, and the branch runs** (`r19b.sm`); the same for a `mala`
element (`r19c.sm`). The refusal covers only known strings. **Made
precise, not removed.**"

**My reading of the code and the document.** The refusal,
`rfx_check_truth` (C:9477–9493), refuses when `rfx_kind` returns 1
(string). `rfx_kind` (C:9516–9595) returns 1 for a string literal, for a
variable every assignment of which is a string (via the per-function
flow table `rfx2_bits`, looked up by `rfx2_find`, C:10180 — a name
not in the table returns -1, and `rfx_kind` then returns 2, "anything
else"), and for a function call whose recorded return kind is a string.
It has **no case for `AST_INDEX`** — a `mala` element read falls through
to 2. So:

- A local variable holding a string (`vitti s = ""` then `yadi (s)`,
  Claude's `r19.sm`) is refused — the compiler knows it is a string.
- A module-level variable (`vitti g = ""`, `r19b.sm`) is not in the
  per-function flow table, so `rfx_kind` returns 2 and there is no
  refusal; the condition reads the string's address, which is non-zero,
  so the branch runs. Claude's program is consistent with the code as
  read.
- A `mala` element (`m[0] = ""` then `yadi (m[0])`, `r19c.sm`) is an
  index read, which `rfx_kind` does not classify at all, so there is no
  refusal; the element holds the string's address, non-zero, so the
  branch runs. Also consistent.

And the document itself scopes the sentence the way Claude says: R:490
("An empty string is still true in `yadi (s)`") is the last line of a
paragraph that begins at R:486, "**Not known to be strings, and so not
handled:** module-level variables, `kosh` and `mala` elements, and a
`prakriya` used as a value (`vitti g = f`). Compared with a string they
are refused, not guessed. Two of them compared with each other still
compare as numbers." The sentence is about exactly the values the
refusal does not cover. The audit's row reads it as an unscoped claim
and prescribes removing it.

**Verdict: Claude right.** The sentence is true in its stated scope, and
the audit's prescription (remove the claim) is wrong — the fix is
precision, which is what v325 did (v325 R:564–566: "**And one of them
holding an empty string is true in `yadi`** (measured v325: a
module-level `vitti g = ""`, and a `mala` element set to `\"\"`, both run
the branch) — the `E_VARTANI_SATYA` refusal applies only to a value the
compiler knows is a string; test `x != \"\"` instead"). The audit's
underlying observation is not baseless — R:469's table states the refusal
without the scope, and R:490 states the exception without pointing back,
so a student reading the two can be confused — but the row as written
("remove the older claim") would delete a true statement. Both readers
agree the section needs work; they disagree on whether the sentence is
false. It is not false.

### R18 — the braces section — BOTH RIGHT, CLAUDE'S IS THE FULLER ACCOUNT

**ChatGPT's claim (audit row R18, Tier 3):** "Braces section obsolete:
R:533/R:546–575 says a brace-free function is one statement and
multi-statement `prakriya` requires braces → C:15380–15383 calls
`parse_body`, whose C:8134–8267 indentation path accepts multiple
indented statements; R:558–562 is a valid function declaration fragment,
missing only an entry point if used as the entire executable source."

**Claude's counter-claim (R189-00, "Where the audit is wrong"):** "R18
says the braces section is obsolete — **right, and worse than
'obsolete'.** The section said a three-line `prakriya` without braces
'does NOT compile' and called that verified. **It compiles and prints
12.** The failure it quoted came from a file with no `mukhya`; a braced
`prakriya` alone fails the same way. **Rewritten, with an example that
is in the gate.**"

**My reading of the code and the document.** The section (R:533–575) says
"A brace-less function body is exactly **one statement**. For anything
longer, wrap the body in `{ }`", "`prakriya` requires the braces.
`mukhya` does not", and shows `prakriya f(n)` with three brace-less
statements annotated "this does NOT compile - parse error", adding
"**Verified:** `mukhya()` with three brace-less statements compiles and
runs; `prakriya f(n)` with three brace-less statements fails with
`vyakaran dosh, pankti 3:5, shabd 'nivartanam'`." Every part of that is
false on the current tree:

- A `prakriya` body is parsed by `parse_body` (C:15380–15383,
  `.r55_parse_real_body`), which calls `r70_indent_body` (C:8134–8267):
  when the body's first token is on a later line, indented deeper than
  the header, the body is every following statement at that indentation.
  That path has accepted multi-statement brace-less bodies since
  v265–v267 (the comment at C:8160–8175 states the rule and its history:
  "Before R70 a body without '{' was ONE statement, whatever the
  indentation said"). It applies to every `parse_body` user, `prakriya`
  included — there is no special case for `prakriya` anywhere in it.
- The quoted failure cannot come from the braces: a file containing only
  the `prakriya` (braced or not) fails at the top-level parse loop,
  which after the declarations expects `mukhya` (`.pf_expect_mukhya`,
  C:8012–8040: "Now expect mukhya" — if the current token is not the
  `mukhya` keyword, `parse_error`). At end of file the token is EOF
  ("patra-ant", C:373), so the error is at the end of the file, not at
  the `nivartanam` on line 3. The old quoted error (`pankti 3:5, shabd
  'nivartanam'`) is exactly the error the *pre-R70* one-statement parser
  would produce — after one statement the body ends, and `nivartanam`
  on line 3 is an unexpected token at top level. The section's
  "Verified" evidence is stale by the R70 change (v265–v267); the
  failure it attributes to braces is the missing-`mukhya` failure.
  v325's rewritten section states this directly (v325 R:636–640:
  "**Verified (v325, R189): it prints 12.** … The failure the section
  quoted came from a file with no `mukhya`… ends with `vyakaran dosh,
  pankti 4:1, shabd 'patra-ant'`, because every program needs a
  `mukhya`").

**Verdict: both right, Claude's is the fuller account.** The audit is
right that the section is obsolete — its rule does not describe the
parser. Claude is right that "obsolete" understates it: the section
does not merely describe old behaviour, it asserts a false rule *and*
cites as verification a failure that no longer occurs for the reason
given. The exact point of disagreement is severity and cause, not
direction: ChatGPT says the section is stale; Claude says it is false
and its evidence is misattributed. On the evidence, Claude's
characterisation is the accurate one. (The audit's row is Tier 3, and
neither reader proposes changing the tier — the finding is about a
documentation section, not a student program — so the disagreement does
not move the re-ranked totals.)

### The third dispute — R188 finding B, the changelog — CLAUDE RIGHT

For completeness: Claude's R188-00 handoff checks two audit claims
about the documents. Finding A ("`docs/WHATS-LEFT.md` does not exist")
he agrees with, and it is true: on main there is no
`docs/WHATS-LEFT.md` (only the archived copy at
`docs/rounds/WHATS-LEFT.md`), and `ROADMAP.md:14` itself says the live
path was last true at v258. Finding B ("The CHANGELOG stops at v315;
nine staged versions are in no document") he says is NOT TRUE, and he
is right: the v325 changelog has entries for v316 through v325
(v316 at :228, v317 :201, v318 :181, v319 :159, v320 :131, v321 :108,
v322 :86, v323 :64, v324 :33, v325 :3), each written in the commit that
made its version, on the branch that carries it. Main's changelog
correctly stops at v315 because main *is* v315; writing v316–v324 into
it would describe nine versions main's compiler is not. The audit's
underlying observation — "nobody reading main can see the week's work" —
is true, but that is the cost of an unmerged chain, not a missing
changelog, and its fix is the Windows run, not a document. This dispute
is not a numbered audit row (the WHATS-LEFT/CHANGELOG claims appear in
no row of `ROUND-233-AUDIT.md`), so it does not touch the re-ranked
totals either. The two substantive disputes are R18 and R19.

---

## Brief corrections

1. **"Sixty-six false claims by Sarvam this stretch" (not derivable
   here):** the R171 brief counted 64, and this brief says 66, with no
   derivation in either brief and no count in the tree that reproduces
   it in this round. The +2 is not accounted for by anything read here
   (the two wrong audit rows found this round are ChatGPT's, not
   Sarvam's). The count is carried, not verified.
2. **"92 gates PASS, 0 FAIL" (incomplete, not wrong):** the v325 gate
   run is 92 PASS / 0 FAIL / **1 NOT-RUN** (Windows execution, per the
   R189 handoff). The brief omits the NOT-RUN.
3. **"Four refused, one never ends, one prints something else" (right,
   but the seventh program is missing from the sentence):** the
   simulation covers seven programs — four refused, one never ends, one
   prints something else, and the seventh (`46_language_reference`) is
   unchanged because it reads the value and does not use it. The brief's
   sentence accounts for six of seven.
4. **"The converter already exists twice over" (overstates the shape):**
   `varna_tak_ank` exists, with two siblings — but none of the three
   takes a string, and no string-to-number function exists anywhere in
   the 310 (Claude's `grahan-option-a.txt` states this outright: "A
   text-to-number function: none"). What exists twice over is a
   mala-of-codes-to-number converter, not the `int()` the owner asked
   for. The three-line program needs a string-to-codes step that does
   not exist.
5. **The R189-00 handoff title (overstates the branch):** "ADD-A-
   CONVERTER" — the v325 branch adds no converter and no
   read-line-and-convert example (verified: same `lib/` file list as
   main, no converter builtin, no such example). The body of the
   handoff says so itself ("The `grahan` converter is not built"). The
   title is aspirational; the branch is the discoverability half only.
6. **"The forms I know of, and there may be more" (answered):** there
   are no more. The AST enum and the statement dispatch enumerate
   exactly three loop forms; the only other candidates (`guna`,
   `yadi dosh`, recursion) are not loops.

## Could not determine

- The `kuru` demonstrator's runtime behaviour for the hoist gap, and
  any runtime behaviour at all (read-only round; nothing run).
- Whether any gate outside `r172`/`r184`–`r186`/`r189` asserts hoist
  `parimana()` values that a future `kuru` entry call would disturb
  (carried from R171).
- Owner intent on R189 option 4 and on the converter's three open
  decisions (name; how it says "not a number"; what counts as a number)
  — no decision recorded anywhere in the tree.
- Whether the "sixty-six false claims" count has a derivation (see
  brief correction 1).

## Summary

Every loop form was read from the parser and the codegen, and the
language has exactly three: `chakra` counts down only when both ends
are written as numbers (after folding, unary-minus negation, and `sutra`
substitution) and otherwise counts up, running zero times silently when
the start is past a variable end — the trap is symmetric, a variable
start with a constant end runs zero times too; `yavat` runs zero times
on a false condition and that is correct, because the form means "while
true"; `kuru … yavat` cannot run zero times, by construction; `krama`
and `agrim` cannot cause zero passes (a stray `krama` outside a loop is
a silent no-op, a side finding); and no step form exists. Zero
iterations are legitimately right for `yavat` and for the 0-to-`n-1`
`chakra` over an empty collection, and the compiler cannot tell that
legitimate empty case from the broken countdown — both are "start past a
variable end" — so the right answer is documentation, not refusal, with
the books' "Descending Loops" sentence fixed because that sentence is
what teaches the trap (and it is still uncorrected on v325). On
discoverability, the three-line program the owner wants does not exist
anywhere in the tree: `vartani_grahan` is untaught on main and taught on
v325, but `varna_tak_ank` is undiscoverable on both (0 hits in either
book, no reference row), takes a `mala` of codes rather than a string,
and the honest program needs seven untaught pieces; v325 adds the §4d
table, the book section, and three examples, but no converter despite
its handoff title. And of the two audit rows Claude disputes, he is
right on R19 (the empty-string sentence is true in its stated scope —
the refusal covers only values the compiler knows are strings) and his
is the fuller account on R18 (the braces section is not merely obsolete,
its rule is false and its "verified" failure is the missing-`mukhya`
error, stale since v265–v267) — with the changelog dispute also going
his way.

---

*ROUND-172, read-only. Base: main at v315, tip `46bc76c7`. Nothing compiled
or run. Counts re-derived on this tree; line numbers re-grepped on this
tree. Claude's R189-00 handoff and evidence programs were read for what
he measured; every verdict above comes from my own reading of the code.*
