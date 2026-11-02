# Sutram — ROUND-100: refusal was a choice for `==`, a constraint for `+`; census fifth run (one number moved); eight more silent traps

**Base:** `origin/main` at `106f2074` (compiler v285).
**Deliver into:** `Muse-to-Sarvam/`. **No tree changes by this round**
— read-only census, probes, and source audit. The FIXALL patch was
applied only to a scratch copy of the tree to verify WS2's
patch-change claims by running; the scratch tree was removed after
verification and nothing from it reached main.

## Three premise corrections, stated first

1. **The brief's "274 examples" is stale on v285.** The tree now has
   **277** examples: v285 added 303/304/305 (`mandapa parimita`
   examples, Claude's R103), and the suite moved 270 → 273 with their
   goldens. All counts below use 277; lib is unchanged at 306
   functions (583 combined).
2. **The FIXALL patch is not on main.** The three commits titled
   "APPLY THE FIXALL PATCH" each added only one inbox brief
   (ROUND-100/104/173) — they are the assignments, not the
   application. A marker grep over `src/` on main finds none of
   `dvaram_likha`, `E_LIKHA_TRAYA`, `E_VARTANI_TUL/CAT`,
   `E_MULYA_VINA`, `E_GAHANATA`. The patch is with Claude (applying)
   and ChatGPT (auditing), as the brief says. My WS2 verification
   below used a scratch tree, not main.
3. **R103's outcome confirms R99's WS2 verdict.** Regions stay: no
   block-end return was built ("Claude gives the numbers and does
   not build the return unprompted"). The ABA tripwire from R99 has
   therefore not triggered, and `samskara` stays saved.

## WS1 — `s == "ab"` and `s + t`: which was a choice, which a constraint

**Plainly, as asked, without defending the choice: for `==` it was a
choice; for `+` it was a constraint.** The evidence is the string
representation itself, read from `src/` on v285:

**A string is a bare pointer with no length, no header, and no type
tag — and two conventions share that pointer.** (a) NUL-terminated
strings: literals (the lexer pool stores terminators), `vartani_cat`
results (the terminator is copied), and everything `shabda`,
`vartani_tul`, and `vartani_aayam` touch — all three are byte-scan
loops that stop at NUL (`shabda`'s own comment: "print the
NUL-terminated string whose address is in s"). (b) (pointer, length)
pairs: the whole `khand` world takes `(ptr, n)` pairs, and the slice
idiom is a pointer plus an explicit length elsewhere
(`tests/r79_real/report_blocks.sm:188`: `likha(1, letters + offset,
1)` — one character, whose logical end is the `1`, not a NUL). A
bare pointer does not say which convention it follows.

**For `==`: content comparison already exists, so refusal was a
choice — for the shapes the compiler can identify.** `vartani_tul`
(src ~20988) is a byte-by-byte NUL-scan returning 0 if equal, 1 if
not. Wiring it into `==` would cost: (i) binop dispatch — today `==`
compiles to a single pointer `cmp`, with no type dispatch at all;
(ii) type knowledge for every shape — the FIXALL flags identify
local variables only, while parameters, globals, kosh elements, and
call results are untracked, and pointers carry no runtime tag, so for
those shapes the compiler cannot know a string from an address;
(iii) the NUL assumption, which is unsafe for convention-(b) values
(a scan on a slice overruns past its logical end); (iv) a convention
wart — `vartani_tul` returns 0 for equal, `==` must return 1. A `==`
that worked for locals and literals but silently compared addresses
for parameters would be worse than refusal. So: **implementable for
tracked shapes at moderate cost, impossible in general without a
type-system change — I chose consistency over a partial `==`.**

**For `+`: concatenation for variables cannot be done honestly with
the current machinery, so refusal was a constraint.** It needs (i) a
result buffer — and the language has no allocation/lifetime rule for
one: persistent arena means every `+` leaks until exit (and `+` in a
loop is unbounded growth, the very gap the census measures), scratch
means the result dies at block end (the escape check refuses
returning it, or it dangles); (ii) capacity — lengths via NUL scans
(O(n+m)) or stored lengths (which do not exist); (iii) the same
dispatch problem as `==`; (iv) the same NUL assumption. Even the
builtin does not allocate: `vartani_cat` (src ~21082) finds the
destination's NUL and copies the source including its terminator,
with **no capacity check and no allocation** — the caller must have
pre-allocated enough space. There is no concatenation primitive to
wire `+` into; building one is a language-level ownership decision,
not a patch.

**One refinement to my FIXALL report, stated because it changes the
picture.** The report said "string+int is pointer arithmetic." That
is true for **variable**+int (the slice idiom) but incomplete: the
parser folds `+` at compile time when a literal is involved
(`fold_const`: `"a"+"b"`, `"a"+42`, `42+"a"` all fold to a single
literal, with decimal conversion for the integer). So `+` is already
overloaded by literal-ness: literal-involved `+` concatenates at
compile time (which is why example 31 works — see WS2), variable
`+` adds addresses at runtime. The FIXALL patch is consistent with
both halves: folded nodes never reach its check, and variable+int
stays allowed as pointer arithmetic.

**What full `==`/`+` would cost, if the owners want them:** (1) type
tracking for all shapes, or declared string types (a type-system
change); (2) binop dispatch (call the `vartani_tul` loop for `==`,
alloc+copy for `+`); (3) an ownership/lifetime design for `+`
results; (4) NUL-vs-(pointer,length) disambiguation — require
NUL-termination for all "strings" (breaks the slice idiom) or carry
lengths (a representation change); (5) a convention fix (0=equal vs
1=equal).

**What the reference must say, and why:** "A string is a bare
pointer with no length. `==` and `+` on string variables compare and
add addresses; they do not compare or concatenate contents. For
contents, use `vartani_tul` (returns 0 if equal) and `vartani_cat`
(writes into the caller's buffer, which must already be large
enough, and does not allocate) — and only on NUL-terminated strings,
never on slices. Literal-involved `+` is concatenated at compile
time, which is why those forms work."

## WS2 — census fifth run on v285: one number moved, and the string count

| # | question | examples | lib | total | moved? |
|---|---|---|---|---|---|
| 1 | allocate inside a loop | 6 | 0 | **6** | **yes: 4 → 6** |
| 2 | grow a `kosh` more than 1,000 times | 0 definite, 1 potential | 0 | **0 definite, 1 potential** | no |
| 3 | allocate without a `mandapa` block at all | 57 | 26 | **83** | no |

Denominators: 277 examples, 306 lib functions, 583 combined.
Method: R96 scripts re-run against a pristine worktree of this base;
`lib_flags.json` is byte-identical to R99; `ex_flags.json` differs
only by the three new parimita examples.

**Q1 moved because v285 added two loop-allocating examples, both
bounded by construction.** 303 (`mandapa parimita 1048576` with a
1,000,000-pass loop allocating `nirmmita(64)` per pass) counts
textually (loop-body span confirmed) and actually allocates 16,384
times before the budget refuses with `E_PARIMITA` — the budget
working as designed, not a leak. 304 (the same shape with the block
entered once per pass, 64 bytes per pass given back at block end)
runs to the end with per-pass freeing, like 268. Q1a is now 3
(258, 303, 304), Q1c still 3 (217, 237, 268), Q1b still 0. **The risk
reading is unchanged: still zero unbounded loop allocations.** Q2 is
unchanged (the push-and-loop file list is identical; 286 still the
one potential, still bounded by caller n — re-verified on v284 in
R99, and v285 touches no kosh code). Q3 is unchanged (all three new
examples have `mandapa`, so none joins the 83).

**How many examples compare or concatenate a string? Two — and the
patch changes neither.** The scan (string literals stripped, then
`==`/`!=`/`+` outside literals, plus local string variables, plus
`vartani_*` calls; every candidate hand-read):

- **Compare by operators (`==`/`!=` on strings): 0 examples.** Every
  `==`/`!=` candidate in the tree is numeric (ints, dasham, kosh
  elements) — 291's NaN comparisons, 299's kosh comparisons, 297's
  `t == 0.3`. No example compares a string with `==` or `!=`.
- **Concatenate with `+`: 1 example — 31_strcat** (lines 4–7). But
  every one of its concatenations is a compile-time fold (see WS1):
  `"Hello " + "World\n"`, `"The answer is " + 42 + "\n"`,
  `3 + " + " + 4 + " = " + 7 + "\n"`, `"Year: " + 2026 + "\n"` all
  fold to single literals before codegen. **The patch does not
  change its output.**
- **Compare via the builtin: 1 example — 256** (calls
  `vartani_tul(b, "sutram")` and `vartani_tul(b, "sutra")`, plus
  `vartani_pratilip` and `vartani_aayam`). Builtin calls are
  untouched by the patch. **The patch does not change its output.**
- **Total: 2 examples compare or concatenate a string; 0 examples
  change output under the patch.**

**Proven by running, not just reasoned.** The FIXALL patch applies
cleanly onto v285 (`git apply --check`, exit 0 — it was generated
against v283, but v284/v285 changed no file it touches except
`src/`, and there without conflict). A patched v285 compiler was
built in a scratch tree and run: 31_strcat output byte-identical to
unpatched (Hello World / The answer is 42 / 3 + 4 = 7 / Year: 2026 /
Done!); 256 output byte-identical to unpatched (diff empty); traps
(a)/(b)/(c)/(d) refuse on patched v285 (`E_LIKHA_TRAYA`,
`E_VARTANI_TUL`, `E_VARTANI_CAT`, `E_MULYA_VINA`); `s + 1`
(string var + int) still compiles clean (the allowed slice idiom);
and the parameter residual below still prints (see WS3). The
scratch tree was removed afterwards.

## WS3 — traps I did not fix: eight verified, one residual class, one refuted

Same family as FIXALL's five: an operation that silently does the
wrong thing on a type it was not designed for. **Every item below
was run on v285 and prints a wrong answer with exit 0** (probes in
`~/workspace/r100/ws3/probes/`). None is fixed by the FIXALL patch
unless stated.

| # | trap (program shape) | v285 output (silent, exit 0) | patch status |
|---|---|---|---|
| 1 | SUB/MUL/DIV on string vars (`s - t`, `s * 2`, `s / 2`) | `-17` (address distance), `8388908` (address × 2), `2097227` (address / 2) | **not fixed** — FIXALL follow-up, stated then |
| 2 | string ordering (`a = "b"`, `b = "a"`, `a < b`) | `1` (true) — by pool address, not lexicographic; `a > b` → `0` | **not fixed** — ordering untouched by design |
| 3 | string truthiness (`yadi (e)` with `e = ""`, and `yadi ("")`) | both branches print — any pointer is nonzero, even the empty string's | **not fixed** — truthiness untouched |
| 4 | `kosh ==` (two koshes, both `[7]`) | `0` (unequal) while `a[0]` and `b[0]` both print `7` | **not fixed** — R83 finding, still true |
| 5 | `likha(kosh)` | prints a buffer address (`124653781647376`), not contents | **not fixed** — R83 finding, still true |
| 6 | string into `mala` (`a[0] = s`, then `likha(a[0])`) | prints the string's address (`4194674`) | **not fixed** — same family as dasham→mala |
| 7 | string + dasham literal (`"x" + 2.5`) | `4194456.500000` (address + 2.5 as a float; no fold for dasham) | **not fixed** — fold covers int literals only |
| 8 | `dasham` → `mala` raw store (R90's program, re-run) | `4615514078110652826` on v285, unchanged from v281/v283 | **not fixed** — fix would be a mala-store check (R98) |
| R | **residual class after the patch:** parameters, globals, kosh elements, and call results in var-vs-var (or var-vs-int) `==`/`+` | `g("ab","cd")`: `s + t` → `8388921`, `s == t` → `0` — and on the **patched** v285 compiler the same program still prints an address sum and `0` (address differs run to run; the refusal does not fire) | **not fixed by design** — untracked shapes; note the boundary precisely: a **literal** operand still refuses those shapes (so a parameter's `s == "ab"` WOULD refuse under the patch), but `s == t`, `s == 5`, and `s + t` on untracked variables do not |
| P | kosh aliasing on PE/Windows (Linux closed by v284 Option A) | cannot run here; 288's header documents Windows still moves | **not fixed** — platform limit, never to be claimed otherwise |

**One candidate refuted by its own probe, and reported as such:**
2-argument `likha` with a bad fd looked like a silent-failure trap
in the same family as FIXALL (a) — but the probe showed 2-argument
`likha` is multi-value print, not raw write (`likha(99, "hi\n")`
prints `99` and `hi`); the raw-write form is 3-argument only, which
FIXALL (a) already handles. There is no 2-argument bad-fd trap.

**Already named elsewhere, not counted as new:** integer overflow
wraps (§3a), dasham overflow to infinity (README sentence), kosh
aliasing on Linux (closed v284), and string+int pointer arithmetic
(the slice idiom, by design — with WS1's fold refinement: literal+int
folds to concatenation, variable+int is pointer arithmetic).

## What this round did NOT do (NOT RUN)

Windows (PE aliasing, installer rebuild, wizard), browser,
implementation (no code changes by this round; the scratch patch
application was verification only and was removed), native-speaker
review (WS1's reference sentence is best-effort Sanskrit-English
prose, not a language change). The full suite, proofs, gates, and
guard were not re-run: no `src/`/`lib/`/`examples/`/`tests/` file
changed in this round, and the brief's suite/gate numbers (273,
59 PASS / 1 FAIL / 1 NOT-RUN) are cited, not re-measured. RSS
measurement was not attempted.

## Deliverables

- `Muse-to-Sarvam/ROUND-100-CHOICE-CONSTRAINT-CENSUS-TRAPS.md` (this
  report)
- `Muse-to-Sarvam/r100_census.json` (WS1 verdict and cost list, WS2
  counts and string list, WS3 trap list with probe outputs)

Work staged in `~/workspace/r100/` (scripts in `ws2/`, probes in
`ws3/probes/`, worktree in `tree/` — read-only, removed after
delivery).
