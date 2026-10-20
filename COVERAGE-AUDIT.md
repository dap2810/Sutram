# The coverage audit, done mechanically

**Item 7 of `PLAN-TO-FINISH.md`.** Measured 2026-10-20 at v221.

## Why this exists

**I claimed twice that a construct was "covered by nothing but a book", and I was wrong** - it was covered by
four tests. **I had searched `examples/` and the test goldens, not `tests/`.**

**A negative result from a search I designed badly is not a negative result.** So this audit is mechanical:
**every identifier the books use, compared against every identifier the tests use, by set difference.**

## Result 1 - the books are covered

**184 identifiers in the books; 2,380 in the tests and examples.** 71 identifiers appear in a book and
nowhere in a test - **and every one is either a sample name (`Somvaar`, `Mangalvaar`, `Budhvaar`,
`Aadeshah`), an English word in a comment, or the compiler's own output text (`Siddh`, `Sanket`, `baait`,
`dosh`).**

**Not one is a language construct.** So the books teach nothing the tests do not exercise - **which is what I
claimed the first time, and it happens to be true, but I had not measured it correctly.**

## Result 2 - the real gap is in the BUILTINS

**Thirty builtins exist in the compiler. Five are used by no test, no example and no benchmark:**

| Builtin | What it is |
|---|---|
| **`sthagita`** | a builtin with no test at all |
| `kosh_var_cnt` | the growable array's variable count |
| `kosh_vars` | its variable table |
| `kosh_param_var_cnt` | the parameter variable count |
| `kosh_param_vars` | its parameter variable table |

**`sthagita` is the significant one** - it is a **user-facing builtin**, not an internal, and **nothing
exercises it.** The four `kosh_*` ones may be internals that no user can reach, which would be fine - **but
nobody has established that either way.**

## Result 3 - the network builtins have no test

**`netsock`, `netbind`, `netlisten` and `netaccept` appear in the compiler and in no test.** The security audit
already recorded that the language can open sockets; **this adds that nothing has ever opened one.**

**A security-relevant surface with zero coverage is worth naming** - not because it is wrong, but because
**the project cannot say it works.**

## What to do

1. **`sthagita`** - a test, or a statement that it cannot be reached from source. **It is a builtin with no
   coverage and no note.**
2. **The four `kosh_*` internals** - establish whether a user can reach them. **If not, say so and close it;
   if so, test them.**
3. **The four network builtins** - either a test that binds and accepts on loopback, **or a stated decision
   that they are untested and why.**

**Three items, all small, all mechanical. This is the shape item 7 should have had from the start.**

