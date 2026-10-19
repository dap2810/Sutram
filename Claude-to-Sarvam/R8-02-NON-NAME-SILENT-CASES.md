# R8-02 — WS2: the non-name silent cases, plainly, with cost and a recommendation

**Nothing is implemented.**

- Every result below was run on v183's compiler, on Linux.
- The probes are in `evidence-r8/probes/WS2_*`.
- The results are in `evidence-r8/logs/probes.txt`.

## The cases

| # | Case | What happens today | Class |
|---|---|---|---|
| 1a | **Top-level** `sutra K = 1`, then `K = 5` in a function | **The assignment is lost.** `likha(K)` prints **1**: reads are folded to the constant at compile time. | mutability |
| 1b | **Local** `sutra K = 1` inside a function, then `K = 5; K += 1` | **K is an ordinary variable:** it prints **6**. R7-01 said "K becomes 5". That is right for this form, and wrong for 1a. | mutability |
| 2 | `krama` / `agrim` outside any loop | **Ignored.** It is emitted as a jump to the next instruction and never patched (`WS2_c2*`: prints `1 2 3`). A later loop is not affected. | statement placement |
| 3 | Two `bhavana 1:` in one `guna` | **The first wins** (prints 10). The second is dead code. | constant values |
| 3b | **New:** `guna (f())` with three cases, matching the third | **`f` is called 3 times** (`calls = 3`). The `guna` becomes an if/else chain that re-evaluates the expression for every case. | evaluation order |
| 4 | `a.by`, where `by` is a field of another `rachana` at the **same** offset | **Reads that offset** (prints `a.ay`). | typing |
| 5 | `n[0]` or `n.x` on a plain number | **Segfault** at run time. | typing |

**One fact matters for case 3:**

- A case value can be **any expression**: `bhavana y + 1:` compiles.
- So a duplicate can only be detected when both values are constant (a literal, a `sutra` or a `ganana`).

## Are they the same class as the three the owner decided?

**No.**

**The three decisions** (undeclared assignment, block scope, re-declaration) were **name resolution.** They
asked: does this name refer to what the writer meant? All of them are answered from the name tables.

**These cases fall into four other classes:**

| Class | Cases | How it is checked | Cost |
|---|---|---|---|
| **Mutability** | 1a, 1b | A flag on the name: the same tables as R7, so the closest to the decided class | small |
| **Statement placement** | 2 | A counter of how deep in loops the parser is | small |
| **Constant values / evaluation order** | 3, 3b | Folding the case values; a hidden temporary for the `guna` value | small (3); small to medium (3b, it changes codegen) |
| **Typing** | 4, 5 | Needs to know, for every variable, whether it is a number or a pointer, and to which `rachana` | **large: a type system** |

## What each would cost

| # | Fix | Where | Size | Tests | Risk |
|---|---|---|---|---|---|
| 1 | **An error when assigning to a `sutra`** (top-level and local), in the `=`, `+=` and `++` paths. Uses the existing `ns_func_is_const` and one flag in `var_table`. | `r7_check_assign` and its siblings | about 30 lines | 2 goldens (1a, 1b) | **Measured: 0 of 638 tracked `.sm`/`.smlib` files assign to a `sutra`**, apart from my R7 probe |
| 2 | **An error for `krama` / `agrim` outside a loop.** The loop depth goes up and down around `yavat` / `chakra` bodies and is reset per function. | `.ps_krama`, `.ps_uddeshya`, the loop parsers | about 20 lines | 2 goldens | low. Not measured yet; measure the way block scope was |
| 3 | **An error for a duplicate constant `bhavana`.** Fold each case value; when it is a constant, keep it in a small list per `guna`. | `.ps_guna_case` | about 40 lines | 1 golden | low. A non-constant duplicate stays undetected, and the doc should say so |
| 3b | **Evaluate the `guna` value once,** into a hidden local, then compare. | `.ps_guna` | about 30 lines | 1 golden (`calls = 1`) | **This changes behaviour:** a program that relied on the re-evaluation would change. Measure first. |
| 4, 5 | **Not fixable without types.** Document them as limitations. A heuristic (guess a pointer's `rachana` from its first use) would be wrong as often as right. | — | — | — | — |

## Recommendation

1. **Do 1, 2 and 3 together as one small step.**
   - Each is an error where today there is silence.
   - Each is the owner's stated direction ("decided three times in favour of erroring").
   - Each is measured or measurable first.
   - **Total: about one round, with the goldens.**
2. **Do 3b in the same round, but measure first.** It is not an error message; it is a semantic fix. A `guna`
   over an expression with side effects is rare. The present behaviour is surprising: C's `switch` evaluates its
   value once.
3. **Document 4 and 5 as typing limitations** in the language reference, next to "a number and a pointer are
   one kind". Do not implement.
4. **F1 in R8-01 should come before all of these.** A function with more than 21 variables silently computes
   wrong values. That is far worse than any case here.
