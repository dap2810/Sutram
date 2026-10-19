# R7-01 — WS1 (Step 1): every name-resolution path, and what a wrong name does on each

**Branch `claude/round-07`. Base: main `05d8bdc8` (v180).** Compiler commit `5bd1acdf`; the test-generator
fixes are in `bedf2705`. **Environment for everything in this document: Linux.** The Windows compiler is
covered in R7-03.

## How the inventory was made

I did not start from the bugs we already knew. I read the parser for every place that **introduces** a name:

- `vitti` / `anka` / `sankhya` / `satya` / `mala` / `dasham` / `kosh`
- `sutra`, `ganana`
- `chakra` variables and parameters
- `prakriya`, `rachana` and its fields
- module-level `vitti`
- `yoj` with or without `@alias`

Then every place that **resolves** one:

- a bare read and an assignment target
- compound assignment and `++`
- `a[i]` as read and as target, and `p.f`
- `f(…)`, `alias__f(…)`, a builtin
- a `bhavana` label
- a `--lang` pack name

For each I wrote a program with a wrong name and ran it on v180 and on the branch. That is 50 probes, in
`evidence-r7/probes/`; raw results are in `logs/probes-v180.txt` and `logs/probes-branch.txt`. "Quietly
succeeds" means it compiled and then printed a wrong value or crashed, with no diagnostic.

## The inventory

| # | Path | Wrong-name probe | v180 | Branch |
|---|---|---|---|---|
| 1 | variable read | `likha(totl)` | error (R4) | error |
| 2 | **assignment target** | `totl = 10` (typo for `total`) | **quiet: declared `totl`, printed 3** | **error** `E_UNDEFINED_NAME` |
| 3 | compound / `++` | `k += 2`, `j++` | error (R4) | error |
| 4 | **read after its block** | `yadi(…){ vitti b = 7 }` then `likha(b)` | **quiet: printed 0** | **error**, with a block hint |
| 5 | **loop variable after the loop** | `chakra i …{}` then `likha(i)` | quiet: printed 3 | **error**, same hint |
| 6 | another function's local | `likha(q)` | error | error |
| 7 | parameter / argument | `f(y)` | error | error |
| 8 | module global, typo | `likha(gg)` | error | error |
| 9 | global initialiser, typo | `vitti a = zzq + 1` | error | error |
| 10 | `sutra` / `ganana` / `bhavana` label, typo | `MAXX`, `REDD` | error | error |
| 11 | **a second `vitti x` in the same scope** | `vitti x = 1 … vitti x = 2` | **quiet: x stayed 1** | **error** `E_DUPLICATE_NAME` |
| 12 | **a name declared again after its block** | `{vitti b = 7} … vitti b = 2; likha(b)` | **quiet: printed 7** | **correct: prints 2** |
| 13 | **duplicate parameter** | `prakriya f(a, a)` | quiet | **error** |
| 14 | **duplicate `sutra` / `ganana`** | `sutra K = 1; sutra K = 2` | **quiet: printed 1** | **error** |
| 15 | duplicate module global | `vitti g` twice at top level | error | error (now with a location) |
| 16 | array base, undeclared | `zz[0]`, `a[0] = 1` | error (R5) | error |
| 17 | field base, undeclared | `p.x`, undeclared `p` | error (R5) | error |
| 18 | field not in any `rachana` | `p.w` | error (R5) | error |
| 19 | **field name in two `rachana` at different offsets** | `rachana A{x,y}` and `B{y,x}`, then `b.x` | **quiet: used A's offset; printed `1 2` for `2 1`** | **error** `E_AMBIGUOUS_FIELD` |
| 20 | **duplicate field** | `rachana P = { x, x }` | **quiet** | **error** |
| 21 | field names longer than 8 bytes | `position_x` / `position_y` | fixed in R5 | fixed |
| 22 | function, typo | `jodaa(1, 2)` | error | error |
| 23 | **wrong number of arguments** | `f(1)` for `f(a, b)`; `f(1, 2)` for `f(a)` | **quiet: printed 1 both times** | **error** `E_ARITY` |
| 24 | builtin, typo | `likhaa(1)` | error | error |
| 25 | a variable called as a function | `vitti f = 1; f(2)` | error | error |
| 26 | a function used as a value | `vitti x = joda` | error | error |
| 27 | duplicate `prakriya`, or one clashing with a module's | `prakriya f` twice | error | error |
| 28 | **`yoj` of a module that does not exist** | `yoj ganitt` | **quiet: ignored, compiled** | **error** `E_MODULE_MISSING` |
| 29 | module function, typo | `vargg(3)` | error | error |
| 30 | `@alias`, typo | `h__varg(3)` | error | error |
| 31 | alias function, typo | `g__vargg(3)` | error | error |
| 32 | `--lang` pack that does not exist | `--lang klingon` | a warning (`Chetavani`), then the Sanskrit core | unchanged: the program text is still checked, so any pack word becomes a name error |
| 33 | old (pre-v157) keyword | `pratiyati` | error with the new keyword in the hint (R4) | error |
| 34 | Devanagari word without its pack | `वि॰` | error | error |

**Result: every name-resolution path now errors on a wrong name.** That covers variables, functions,
fields, array bases, module names, aliases and builtins.

## What is *not* a name-resolution path, and still quietly succeeds

These are real, but they belong to other classes. I list them so they are not mistaken for done:

| Case | v180 and branch | Class | Why not fixed here |
|---|---|---|---|
| `a.by`, where `by` is a field of another `rachana` at the same offset | reads that offset | **typing** | Field access has no type: a pointer does not know its `rachana`. Only a type system can catch it. R7 catches the dangerous half, a name at a *different* offset (row 19). |
| `n[0]` or `n.x` on a plain number | crashes at run time | **typing** | A number and a pointer are one kind, by design (`nirmmita` returns a number). |
| `sutra K = 1` then `K = 5` | K becomes 5 | **mutability** | Assigning to a constant is not a wrong name. It is a one-check fix if you want it. |
| `agrim` / `krama` outside a loop | ignored | **statement placement** | Not a name. Also a small fix. |
| two `bhavana 1:` labels in one `guna` | the first wins | **constant values** | Not a name. |
| local or parameter shadowing a module global | allowed | **by design** (R56) | Documented: "a parameter or local … shadows a global". |

## The two decisions, and what I measured before implementing

**Case 1, an undeclared assignment, is now an error.** This was decided.

- **Measured:** 0 of the 530 `.sm` files rely on it; the only one that changed is my own R5 probe.
- The target is queued like an undeclared read, so a module global declared further down is still
  accepted.

**Case 2, block scope.** This was decided, with "measure first".

- **Measured precisely with the real compiler**, not the R6 heuristic:
  - the block-scope build against the build before it, over all 530 files: **0 programs read a block's
    name after the block**
  - the 13 pack programs (each with its `--lang`) and the R71-profile examples: 0
  - 34 doc and book samples that compile on v180: 0
  - **0 is below "a handful"**, so it is implemented
- **The rule:**
  - a `vitti` inside `{ }` ends at its `}`
  - a `chakra` loop variable ends with the loop
  - **a loop over a name already declared outside reuses that name and keeps it afterwards**, so
    `vitti i = 0` followed by `chakra i …` keeps working
- **I scoped the loop variable too,** because that is block scope for loops in C, Java and Rust. 0
  programs read a loop variable after the loop. **If you want the loop variable to stay visible after the
  loop, it is three lines to revert.**

**Block scope exposed a codegen bug that was already on main (row 12).** A name declared twice in one
function got two slots, but every later read used the first. So:

- `vitti x = 1; … vitti x = 2` kept 1
- `{ vitti b = 7 } … vitti b = 2` printed 7

With block scope users will *write* the second form, so it had to be right.

- **Re-declaring a visible name is now `E_DUPLICATE_NAME`** (same block, an enclosing block, or a
  parameter).
- **Re-declaring after the block closed reuses the slot** (`alloc_var`; the register fast path steps aside
  for it), so the new value is the one read.
- **Measured:** 0 programs in the tree, but **2 generated proof programs** declared `f` / `f14` again and
  again. That was a test-generator bug: in one of them a stale loop index made the same name repeat 12
  times. Fixed in `tools/proof_props.py` (`bedf2705`); **86/86 on both compilers.**

**The arity check found a real bug too.** `proof_props` "edge30 text" called
`varna_bhed(s, 2, s, 0 - 1, parts)` with **5 arguments; the function takes 6**, so `maxparts` read
whatever was in the register. It passed by luck. Fixed in the same commit.

## The diagnostics (new; please confirm the words, R7-04)

```
227_assign_undeclared.sm:6:5: Sutram Error [E_UNDEFINED_NAME]: agyat naam 'totl'
Sanket: prayog se purv ghoshana avashyak: vitti totl = ...
228_block_scope.sm:6:11: Sutram Error [E_UNDEFINED_NAME]: agyat naam 'b'
Sanket: 'b' ek khand { } ya chakra me ghoshit hai; uske bahar drishya nahi
231_duplicate_name.sm:6:11: Sutram Error [E_DUPLICATE_NAME]: punah ghoshana 'x'
Sanket: 'x' pahle se ghoshit hai; naya man dene ke liye: x = ...
232_arity.sm:5:11: Sutram Error [E_ARITY]: 'f' ko 1 tark diye; hastakshar me 2
Sanket: utne hi tark dein jitne prakriya ki paribhasha me hain
Sutram Error [E_MODULE_MISSING]: yoj patra aprapt: ganitt
Sanket: lib/ me ya srot patra ke folder me naam.smlib hona chahiye
234_ambiguous_field.sm:8:7: Sutram Error [E_AMBIGUOUS_FIELD]: kshetra 'x'
Sanket: 'x' do rachana me alag sthan par hai; har rachana me alag naam rakhein
235_duplicate_field.sm:3:18: Sutram Error [E_DUPLICATE_NAME]: punah ghoshana 'x'
Sanket: 'x' is rachana me pahle se hai
```

Each one points at the token, with the source line and a caret, except the module error, which has no
location to give (the `yoj` line is consumed before tokens exist).

## Tests (Linux)

**New goldens 227–235.** All nine **FAIL on v180** and **PASS on the branch**. 230 is a positive test:
re-declaration after a block, and a loop over an outer variable.

| Gate | Result |
|---|---|
| suite (`tests/run_tests.py`) | **PASS 203 / NO-EXPECTATION 4** (194 plus 9) |
| `gates.sh` | **PASS 8 / FAIL 1 / NOT-RUN 1**. The FAIL is X11 `edscroll`, the same pre-existing timeout in my container as every round; the X11 GUI is not touched. |
| proof_lib / proof_props / packs / codegen | 191/191 · 86/86 · 33/33 · 12/12 |
| R70 negative corpus | 6/6, `native_status` PASS |
| `r69_build --check-only` / `--output` | `SOURCE_PINS_CHECKED` / `BUILT_FORMAT_CHECKED` (re-pinned `185b7f06` → `cc5cfbe4`, reason recorded) |
| `tests/r66` 22 · `r67` 17 · `r68` 19 · `r72` 3 · `module_graph` 18 · `gui` 31 · `ci` 9 · `windows_accept` 7 | OK |
| `tests/r69` | 2 FAIL (ChatGPT's scripts; unchanged) |
| whole-tree audit, per change (`logs/tree-audit.txt`) | **0 real programs change.** The only files that went from OK to error are my own probes and the new goldens. |

One audit line needs explaining: `examples/70_module_collision.sm` appears once. It is **expected** to
fail (`punah prakriya paribhasha`), and from the repo root it does so on both compilers, so its golden
passes. The audit also tries each file from its own folder. From there v180 could not find `lib/ganit`,
**silently ignored the `yoj`**, and compiled: row 28 in action. The branch now says the module is
missing.

## Not done / not verified

- **Windows:** the Windows compiler is the same source, cross-built (R7-03). It ran under Wine only.
- **`--check` stops at the first duplicate, arity or field error.** Only undefined names are collected,
  up to 8.
- **The capacities are not exercised at the limit:** 1024 closed names (hint only), 8192 calls, 2048
  definitions.
  - **Past 8192 calls or 2048 definitions, the arity check skips the rest. That fails open, and the cap
    is the honest limit.**
  - No program in the tree is near any of these.
