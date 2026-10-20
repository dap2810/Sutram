# R20-01 — WS1: F7, both options as diffs, neither applied

**Nothing of this is on the branch.** Both patches were applied to scratch copies of main `1b15330b`
(v242), built, and tested there; the diffs are in `evidence-r20/` and apply cleanly to main's
`src/sutram_compiler.asm`. Environment: **Linux**.

| Diff | What it is | Lines |
|---|---|---|
| `f7-A-optional-mala-parameters.diff` | **Option A, optional:** `prakriya f(mala a)` declares an address parameter; the call site refuses a value that is certainly not an address. An untyped parameter keeps today's meaning. | 270 |
| `f7-B-required-on-top-of-A.diff` | **Option B, required:** A, plus: indexing an untyped parameter (or a plain copy of one, `vitti lst = l`) is a compile error. Applied after A. | 185 |

## What each does, exactly

**A — the `mala` parameter (new type `PARAM_MALA`, beside the `kosh` ones that already exist):**

- **Parser:** `mala` is accepted as a parameter prefix, like `dasham` and `kosh` (`.ps_fd_param_mala`).
- **At the call site** (`gen_typed_call_arg`, `.gtca_mala`): the argument is refused if it is **certainly not
  an address**: a number or float literal, an arithmetic, comparison or logical expression, a ternary, **or a
  name declared with one of those** (`vitti x = 0`, `vitti y = a + b`; the declaration marks the name,
  `mark_scalar_var`; a later `mala x[n]` unmarks it). **Everything else is accepted:** a `mala`, a `kosh`, a
  raw `nirmmita` pointer, a record, another `mala` parameter passed on, a call's result.
- **The message:** `Sutram Error: mala tark: sankhya datta, mala apekshita` ("mala argument: a number was
  given, a mala was expected"). **One default; the eleven packs need a line each when this lands** (the
  `sandesh --check` gate will say so).
- **No code changes for a correct call.** The runtime ABI is one qword per argument, as before. **No bounds
  check is added inside the callee** (a `mala` parameter may be a raw pointer with no length header).

**B — on top of A, the requirement:**

- **At function entry** every untyped parameter is remembered (`mark_raw_param_var`); **a declaration
  `vitti copy = param` makes the copy untyped too** (the library's idiom, because the compiler faults on
  assignment to a parameter).
- **Indexing one, read or write (`p[i]`, `p[i] = v`), is a compile error** (`f7_refuse_raw_param_index`):
  `Sutram Error: anirdishta tark suchit; 'mala ' purvam likhatu: p` ("an untyped argument is indexed; write
  `mala` before it: p"). A local `mala`/`kosh` of the same name wins, as everywhere.
- **Field access `p.f` and the string builtins (`akshar(s, i)`) are not covered:** they also take addresses,
  and a scalar there crashes the same way. **B closes F7 for indexing only.** Covering them would be the same
  check at two more places.

## Tested in scratch

| Check | A | B |
|---|---|---|
| F7's reproduction (`f(x)` with `vitti x = 0`, untyped `f`) | **compiles, exit 139** (unchanged: untyped is untyped) | **compile error** (`ok` is indexed) |
| the same with `prakriya f(mala ok)` | **compile error** at the call | compile error at the call |
| `f(m)` with `mala m[2]`, `g(p)` with `vitti p = nirmmita(16)`, `f(nirmmita(8))`, `f(k)` with a `kosh`, `g(mala a) { prati f(a) }` | all compile and print `5 5 5 5` | the same |
| `f(1 + 2)` to a `mala` parameter | compile error | compile error |
| `vitti o = ok; o[0] = 5` in an untyped `f` | compiles (crashes at run time, as today) | **compile error** (`o`) |
| suite · library proofs · property proofs | **213 / 220 / 86, unchanged** | not run: 185 programs cannot compile (below) |

## The cost of B, measured, not estimated

**What stops compiling under B, from main as it is** (`evidence-r20/f7-required-form-cost-measured.txt`):

- **464 programs compile on main; 185 of them stop.** 7 because their own function indexes an untyped
  parameter; **178 only because a module they import does.**
- **15 of the 24 library modules stop compiling:** `aadhar`, `anukram`, `chandas`, `ganit`, `ganita`,
  `khand`, `nighantu`, `phal`, `roop`, `sangrah`, `sankhyiki`, `shreni`, `suchi`, `vakyank`, `varna`
  (`anukram`, `aadhar` and `roop` through the modules they import).

**What must be written to make them compile again** (`evidence-r20/f7-required-form-annotations-needed.txt`,
every function named with the parameters that need the word):

- **`lib/`: 100 functions in 13 modules** need `mala` on one or more parameters: `suchi` 31, `nighantu` 13,
  `ganita` 9, `phal` 9, `shreni` 9, `varna` 9, `khand` 4, `sangrah` 4, `sankhyiki` 4, `vakyank` 4,
  `aadhar` 2, `chandas` 1, `ganit` 1.
- **Programs: 16 functions in 9 files:** `examples/122_t18_kosh_param_devanagari.sm`, `215_r12_wordfreq.sm`,
  `216_r12_expr.sm` (5 functions), `80_b6_nested_call_loop.sm`, `82_b7_stack_spill.sm`,
  `89_b9_short_circuit.sm`, `examples/r71/evaluation_order.sm`, `tests/stdlib/r11_brihat_guards.sm`,
  `tests/stdlib/r8_split_model.sm`.
- **That is 116 one-word edits, in one change with B,** and nothing at any call site.

**Why this is smaller than R19's 236:** that count was every parameter used as a list, string or record,
including field access and the string builtins. **B as written checks indexing only,** which is F7's shape
(`ok[0] = 5`). The other 120 are the `p.f` and `akshar(s, i)` uses noted above.

## Which I would choose, and why

**A, then B as a follow-up once the 116 annotations are in — i.e. land A now.**

- **A closes F7 where it was found.** The crash came from a library function (`ganita_janchit_yuj`'s `ok`)
  called with a scalar; **with A, the library annotates its 100 functions (one word each, no call site
  changes), and every such call becomes a compile error.** User functions get the same protection the day
  they write `mala`.
- **A breaks nothing and changes no program's output.** It is the kosh mechanism the language already has,
  extended to arrays.
- **B is the right end state** (an untyped parameter that is indexed is a mistake waiting to happen), **but
  it is a flag day:** 15 modules and 185 programs stop compiling until the 116 words are written, and the
  books and the reference describe untyped parameters. **Landing A first makes B a one-line rule change
  later** (B's diff is 185 lines because it carries the machinery; the rule itself is the one `call`).
- **What A does not do, and should be said in the reference:** an untyped parameter is still unchecked.
  **"If you index a parameter, declare it `mala`"** becomes the documented rule, and the library follows it.

**If the owner wants B at once:** A + B + the 116 annotations is one round, and I have the list.
