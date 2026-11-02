# Sutram — ROUND-101: the eight traps in full, a systematic way to find the class, the census (sixth run), and where the count comes from

**Base:** `origin/main` at `208209a2` (compiler v286).
**Deliver into:** `Muse-to-Sarvam/`. **No tree changes by this round,
and no `==`/`+` implementation** — the brief asks for the list
*before* Claude touches anything, and the implementation is his next
change, not mine. The generator below only reads behaviour; it changes
nothing.

## Where the project is (premise notes)

v286 is Claude's R104: the FIXALL patch applied (including his change
making the patch's slot a module global, so `--object`/`--separate`
linking stays byte-identical). Suite 273, guard 683 programs, gates
59 PASS / 1 FAIL (installer v243 vs v286) — cited from the brief, not
re-measured. Sarvam's `samaan()` proof (a twelve-line function
returning 1/0/0 for `ab`/`ab`, `ab`/`cd`, `ab`/`abc`, on
`akshar("abc",0) = 97` and `akshar("abc",3) = 0`) is noted because it
settles the reachability question from R100 WS1: content comparison
is expressible in the language today, on NUL-terminated pointers.

## WS1 — the eight traps, in full, on v286

**The five, classified first, because "same class" needs a
definition.** FIXALL's five split three ways: (a) `likha` variable-first,
(b) string `==`, (c) string `+` are **the class** — an operation (or
an argument/store slot) that silently does the wrong thing on a type
it was not designed for, because no check stands at the use site.
(d) uninitialised scalar is the same *family* (silent wrong answer)
but a different mechanism (absence of a value, not a wrong-typed
value). (rec) runaway recursion is a different class entirely
(resource exhaustion, and loud — SIGSEGV — not silent). **All eight
below are the same class as (a)(b)(c).** Each was re-run on v286
(all still exit 0 unless stated); addresses vary run to run, shapes
do not.

| # | program (condensed) | wrong behaviour on v286 | same class? |
|---|---|---|---|
| 1 | `s = "abcd"`, `t = "wxyz"`: `likha(s - t)`, `likha(s * 2)`, `likha(s / 2)` | `-17` (address distance), `8388922` (address × 2), `2097230` (address / 2) | **yes** — canonical: SUB/MUL/DIV on strings |
| 2 | `a = "b"`, `b = "a"`: `likha(a < b)`, `likha(a > b)` | `1`, `0` — by pool address ("b" sits lower), not lexicographic | **yes** — ordering on strings |
| 3 | `e = ""`: `yadi (e) { ... }`, and `yadi ("") { ... }` | both branches print — any pointer is nonzero, even the empty string's | **yes** — condition slot expects bool/int, gets a pointer (like (a), for conditions) |
| 4 | `kosh a[2]`, `kosh b[2]`, both pushed `7`: `likha(a == b)` | `0` (unequal) while `a[0]` and `b[0]` both print `7` | **yes** — `==` on a composite, like (b) for kosh |
| 5 | `kosh k[2]`, pushed `7`: `likha(k)` | prints a buffer address (`124647762821136`), not contents | **yes** — print slot expects a scalar, gets a composite (like (a), for printing) |
| 6 | `mala a[2]`, `s = "hi"`: `a[0] = s`, `likha(a[0])` | prints the string's address (`4194681`) | **yes** — store slot expects an int, gets a pointer (sibling of dasham→mala) |
| 7 | `likha("x" + 2.5)` | **closed on v286**: refuses `E_VARTANI_CAT` (no binary). On v285 it printed `4194456.500000` (address + 2.5 as a float; no fold for dasham) | **yes, was** — a FIXALL side-effect: the patch's string+non-int rule catches literal+dasham |
| 8 | R90's program: `dasham d = 3.7` into `mala a[0]` | `4615514078110652826` on v286, unchanged from v281/v283/v285 | **yes** — store slot expects an int, gets dasham bits (the original store-type trap) |

**Count after v286:** the class has 11 members (3 from the five +
8 here). Closed on v286: 4 ((a)(b)(c) + #7). **Live: 7** (#1–#6, #8)
**plus** the residual class from R100 (parameters, globals, kosh
elements, and call results in var-vs-var or var-vs-int `==`/`+` —
re-verified on v286: `g("ab","cd")` still prints an address sum and
`0`, not a refusal) **plus** kosh aliasing on PE/Windows (Linux
closed by v284; unrunnable here).

## WS1 — a systematic way to find this class (not one at a time)

**The checklist: a type × operation matrix.** Value kinds on one
axis — int, dasham, string (NUL-terminated pointer), buffer pointer
(`nirmmita`/`khand`), mala, kosh, patra, function value. Use sites
on the other — binops (`==`, `!=`, `<`, `>`, `<=`, `>=`, `+`, `-`,
`*`, `/`, `%`, `&`, `|`, `^`, `<<`, `>>`), conditions (`yadi`),
prints (`likha`, `shabda`), stores (variable, mala element, kosh
push), loads (reading a slot as another kind), and builtins that
take `vitti`. For each cell ask one question: *what does this
compile to, and is that the type-correct meaning?* The five and the
eight fill 13 cells; the matrix predicts the rest. It is finite
(8 kinds × ~25 sites ≈ 200 cells), and each cell is decidable by one
probe.

**The pattern in the source (why the matrix is so full).** The
binop codegen emits **one raw operation per operator with no
operand-type dispatch** — except the parser's literal fold
(`"a"+"b"`, `"a"+42`, `42+"a"`) and FIXALL's `str_flags` for `==`/`+`
on tracked locals. Values are untyped 64-bit words (`vitti` holds
anything), and pointers carry no tag and no length. So **every
codegen site that consumes a value without checking its kind is a
candidate**: `.ge_binop` (all binops), `.ge_call_*` builtins taking
`vitti`, store emitters (no slot-type check), and load sites. That
is grep-able: the trap class is exactly "unchecked use site +
representation-level operation."

**The generator (delivered, working).** `trap_matrix.py` (in this
delivery) turns the matrix into probes: for each ordered kind-pair
and each operator, it emits a minimal program (two locals of the
given kinds, one operation, one `likha`), compiles and runs it on a
supplied compiler binary (`python3 trap_matrix.py [compiler]`,
default `./sutram_compiler`), and records refused / crash / output
to `trap_matrix.json`. Its first run on v286 (4 kinds × 4 kinds ×
7 ops = **112 cells**):

- **28 correct** — int×int, int×dasham, dasham×int, dasham×dasham
  all compute real arithmetic (including float promotion). The
  method does not flag everything; it validates against the correct
  cells.
- **19 refused** — every `==`/`!=`/`+` cell involving a string
  operand (FIXALL working exactly as designed on v286). Note the
  asymmetry the run exposes: int+string is allowed (pointer
  arithmetic, the slice idiom) while dasham+string is refused.
- **2 by design** — string+int and int+string (pointer arithmetic,
  claimed by the slice idiom, proven by r79's single-character
  output).
- **63 silent-wrong candidate cells** — every other ran cell
  computes address/word garbage: int×kosh (7 cells), kosh×int (7),
  kosh×dasham (7), dasham×kosh (7), kosh×kosh (7 — including
  `kosh == kosh` → 0 and kosh−kosh → 67108864, which is exactly
  `R101A_REGION`, independently confirming the region layout),
  int×string, dasham×string, string×int, string×dasham,
  string×string, string×kosh, kosh×string (4–7 cells each).

**How to use it, and its limits (stated, not oversold).** The 63 are
*candidates*, not all traps: each needs a use-case check, and the
burden flips — an address-semantics cell needs a documented idiom
to be legitimate, and only string+int has one. The prototype covers
binops on 4 kinds only; the full matrix adds mala, patra, and
function values, plus stores, prints, conditions, and builtins (WS1's
#3, #5, #6, #8 live in those columns, not in binops). Re-run per
release and the matrix becomes regression detection: a cell moving
from silent-wrong to refused (like #7 did on v286) is progress you
can see. Multi-step programs (a mistyped value carried through two
operations) are the next extension; the one-step matrix finds the
class, it does not exhaust it.

## WS2 — census sixth run on v286: no number moved; the next change alters zero examples

| # | question | examples | lib | total | moved? |
|---|---|---|---|---|---|
| 1 | allocate inside a loop | 6 | 0 | **6** | no |
| 2 | grow a `kosh` more than 1,000 times | 0 definite, 1 potential | 0 | **0 definite, 1 potential** | no |
| 3 | allocate without a `mandapa` block at all | 57 | 26 | **83** | no |

Denominators: 277 examples, 306 lib functions, 583 combined.
Method: R96 scripts re-run against a pristine worktree of this base;
`ex_flags.json` and `lib_flags.json` are **byte-identical to R100**
— v286 changed only three lines of text (215, 217, `lib/patra`:
`likha` → `dvaram_likha`), which move no flag. The sixth run is
identical because the tree's allocation text did not move.

**The list Sarvam asked for before Claude touches anything: the
programs the next change (content `==`/`+`) will alter is empty.**
Evidence, not assertion:

- **Compare by operators (`==`/`!=` on strings): 0 examples.** Full
  review of all 96 `==`/`!=` lines in examples: every operand is
  numeric (ints, dasham, booleans, kosh elements, `akshar` character
  codes — 216's `akshar(...) != 32` compares a code to 32, not a
  string).
- **Concatenate/add on strings: 1 example — 31_strcat** (lines
  4–7), and every one of its concatenations is a compile-time fold
  (R100 WS1), which happens before any `==`/`+` dispatch — **content
  `==`/`+` cannot change it**.
- **Compare via the builtin: 1 example — 256** (`vartani_tul`,
  plus `vartani_pratilip`/`vartani_aayam`) — builtin calls are
  untouched by an operator change — **cannot change it**.
- **Param-aware check:** no example passes a string literal to a
  `prakriya` that then applies `==`/`!=`/`+` to the parameter
  (the one heuristic hit, 05's `yog`/`gun_tray`, takes ints; the
  literals on those lines are `likha` labels). **No string
  ordering and no string truthiness in any example** (both scans
  empty).
- **No example currently refuses under FIXALL** (suite 273 passes),
  so the next change un-refuses nothing either.

**Complete list of string compare/concat programs: 31_strcat,
256_r44_vartani_sanskrit_names — and neither is altered.** One
design constraint for Claude, stated because it bounds his change:
**string+int must stay pointer arithmetic.** r79's single-character
output (`likha(1, letters + offset, 1)`) and buffer arithmetic like
`mem_safe`'s `koshtha + 64` depend on it; if content-`+` changed
string+int, those break. Content-`+` is for string+string; the
slice idiom keeps string+int.

## WS3 — the count I keep getting wrong: the command, not a file

**The command** (in a checkout): `ls examples/*.sm | wc -l`.
**At a commit:** `git ls-tree --name-only <commit> -- examples/ |
grep -c '\.sm$'`. **The file: there isn't one that states it
authoritatively — that is the root cause.** No doc, table, or
manifest in the tree records the example count, so every number in
circulation was copied from an old report at a moment when it was
true, then reused after examples were added.

**The history, measured at commits (top-level `examples/*.sm`):**
259 at `aaf79e40` (2026-10-31), 274 at `dedb7058` (2026-10-31, the
R95 base), 277 at `48eb7faa` (2026-11-02, v285) and still 277 at
v286. The count grew 257 → 277 across 2026-10-31 → 2026-11-02 as
examples were added. **Each of Sarvam's three numbers was right at
its commit and stale when reused** — that is the whole mechanism,
not a miscount.

**Three adjacent numbers that are not the example count** (the
confusion chain): the suite PASS count is 273 (277 minus the 4
NO-EXPECTATION items 215, 216, 217, 219); 267, the R95 brief's
number, was the pre-300-302 PASS count reused as an example total;
and a recursive count is 293 — 16 more `.sm` files live in
`examples/r67`, `examples/r68`, and `examples/r71` (native-language
fixtures, pairs fixtures, indented-body fixtures: round harnesses,
not the main example set). **The definition that makes 277 the
answer is: top-level `examples/*.sm` only.** (The stray `.out`/`.exit`
files sitting in `examples/` for 215/216/217 are run artifacts, not
examples, and do not affect the `.sm` count.)

**The rule that stops it happening a fourth time:** never copy a
denominator from an old report; count at the base commit with the
command above. The closest thing to a file is the latest
`r*_census.json`'s denominators field (this round's says 277) — but
it goes stale at the next example-adding commit, so the command is
the authority, and the JSON is the receipt.

## What this round did NOT do (NOT RUN)

Windows (PE aliasing, installer rebuild, wizard), browser,
implementation (no `==`/`+` built — that is Claude's next change;
the generator only reads behaviour), native-speaker review. The
full suite, proofs, gates, and guard were not re-run: no
`src/`/`lib/`/`examples/`/`tests/` file changed in this round, and
the brief's suite/guard/gate numbers (273, 683, 59 PASS / 1 FAIL /
1 NOT-RUN) are cited, not re-measured. RSS measurement was not
attempted.

## Deliverables

- `Muse-to-Sarvam/ROUND-101-EIGHT-TRAPS-SYSTEMATIC-CENSUS-COUNT.md`
  (this report)
- `Muse-to-Sarvam/r101_census.json` (WS1 trap table + matrix
  summary, WS2 counts and string list, WS3 count history and
  command)
- `Muse-to-Sarvam/trap_matrix.py` (the generator: run it as
  `python3 trap_matrix.py [compiler]`, default `./sutram_compiler`;
  writes `trap_matrix.json` beside itself)
- `Muse-to-Sarvam/trap_matrix.json` (the generator's first run on
  v286: all 112 cells)

Work staged in `~/workspace/r101/` (scripts in `ws1/`/`ws2/`,
worktree in `tree/` — read-only, removed after delivery).
