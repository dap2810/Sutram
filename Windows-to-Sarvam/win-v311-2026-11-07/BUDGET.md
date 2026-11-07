# v311 nesting boundary

New native run: every integer depth 0 through 1023, adding one balanced parenthesis pair per probe inside `likha(...)`. Depths 0–1022 compile. Depth 1023 refuses, exit 1, no executable, empty stderr:

```text
Sutram truti: khand gahrai seema atikram
```

The depth-1022 binary exits 0 and prints 1. No crash or timeout in 1024 compiler invocations (15-second per-process deadline). This verifies the parser nesting boundary, not exhaustion of the analysis walk's node budget. No budget-exhaustion experiment was performed, as directed by the owner's brief.

[All source files and raw outputs](nesting/results.json); [last compiled](nesting/depth-1022.sm); [first refused](nesting/depth-1023.sm).
