# R28-03 — WS3, and ROUND-27's questions

## WS3: the type on variables

**Still with the owner, and not built.**

**Does the linker depend on it?** No, not for this version: a relocation names a prakriya and nothing
else. It **will** matter later. Without types, the linker cannot check that a call across modules passes
the right number or kind of arguments. Today **cross-module arity is not checked**: the arity check runs
inside one compile, and a module cannot see another module's definitions. So once types exist, the object
format should gain each prakriya's signature (version 2). The format is versioned for exactly that.

## ROUND-27, which arrived before ROUND-28

**ROUND-27 WS1 (pick the next capability):** superseded. The owner chose the linker, and it is ROUND-28.

**ROUND-27 WS2 (does the handler cover the cases that matter?): yes, all three.** Each was tested on v238:

| Case | How | Result |
|---|---|---|
| **retry** | `yavat (n < 5) { yadi dosh (q = prayas_karo(n)) { n = n + 1 } anya { phal = q  krama } }` | retries on each failure, and stops at the first success |
| **convert a code to a value** | `yadi dosh (r = f(0)) { r = 0 - 1 }`, after which `r` is a default | `r` is −1 after a failure, and the value after a success |
| **inside a loop**, with `agrim` | `chakra i = 0 tak 3 { yadi dosh (s = f(i)) { agrim }  likha(s) }` | skips the failures, prints the successes |

Output: `10 11 14 -1 14 21`, as expected. Loops already ran in the R26 tests; `krama` and `agrim` inside the
handler's blocks are now confirmed too. **No case is missing, and no keyword is needed.** One limit, already
stated in R26: a result cannot be kept in a variable to inspect later.

**ROUND-27 WS3:** both decisions are with the owner. The object output is now answered (ours, R28). The
type on variables is still open.
