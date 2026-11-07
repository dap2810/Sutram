# v310 native nesting boundary

Balanced program: `mukhya() { likha(` + `(` repeated N + `1` + `)` repeated N + `) }`.
N counts **additional pairs inside `likha(...)`**, excluding the call's parentheses.

Tested every integer N from 0 through 1023, increasing exactly one level per compile: **1024 probes**.
N=0..1022 compile with exit 0. N=1023 refuses with exit 1, no executable, empty stderr, no timeout or crash:

```text
Sutram truti: khand gahrai seema atikram
```

The N=1022 executable runs with exit 0 and prints `1`. Each compiler process had a 15-second deadline.
This exercises the parser nesting guard; it does **not** trigger or prove the expression walk's 200,000-visit budget. No budget-exhaustion experiment was run, as requested.

[Every source and raw command/output](nesting/results.json), [last compiling source](nesting/depth-1022.sm), [first refusal](nesting/depth-1023.sm), [generator](compiler-probes.py).
