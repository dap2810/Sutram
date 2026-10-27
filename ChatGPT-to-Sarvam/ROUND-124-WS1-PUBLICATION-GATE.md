# Sutram R124 WS1 — debugger section: application gate and source truth

Pinned `main`: `87015a8fa9cd3b55f868ac49f517b3f657d2b443`, compiler blob `89495406b5b77258a9699ed5c8c2d51baead1474`, debugger include blob `cd46e83cda53572d96397bbd8e02228af4a10354`, Sanskrit book blob `b181c74f87543df7244624eae592d269d3b62862`.

## Exact delivery

[`ROUND-124-WS1-BOOK-EXACT.tsv`](ROUND-124-WS1-BOOK-EXACT.tsv) contains 22 contiguous, literal HTML lines with mode `PROPOSE_EXACT_CURRENT`, anchored **AFTER** the unique source line 279:

```
Sanket: asmin sthane shabdam vyakaranam cha pashyatu.</code></pre>
```

It also has 4 separately classified lines with `DEFER_UNTIL_IMPLEMENTED`: these must **NOT** be applied to the book as current feature documentation until Claude's separate flag is merged and executed. If that flag's syntax/semantics differs, rewrite those deferred lines from current code rather than forcing them in.

## Source-backed capability matrix (do not confuse assigned with implemented)

| Requested item | Observed at pin | Authoritative evidence | Publication status |
|---|---|---|---|
| `--debug` | **ALREADY IMPLEMENTED** compiler-time tracing switch | `src/r45_debug.inc:1-17`, `src/sutram_compiler.asm:2207-2239` | Document now |
| `--debug=<name>` | **ALREADY IMPLEMENTED** single arg with comma-separated watch names, max 32 | `src/r45_debug.inc:465-554`; 61,73-76 | Document now; multiple separate flags NOT verified |
| Start printing at line | **ALREADY IMPLEMENTED by different syntax**: `--debug=x@N`, `--debug=x@N-M`, `--debug=@N` | `src/r45_debug.inc:6-17,153-165,465-539` | Document existing syntax |
| `--debug-from=<line>` | **NOT IMPLEMENTED on this pin**: no exact token in compiler or included debugger flag parser | `src/sutram_compiler.asm:2207-2240` and `src/r45_debug.inc:465-554` | HOLD and recheck after Claude delivery |
| Summary at normal exit | **ALREADY PRESENT in source**: `[shodhan] samapti, vakya:`; counter and in-scope scalars; watch list does not filter summary | `src/r45_debug.inc:10-17,422-444,690-717` | Document with early-exit limitation |

**Execution model:** the instrumented *compiled program*, not the compiler, emits the trace and the summary; trace and program output share stdout. The watch filter suppresses trace records without a watched name in scope. Summary at `mukhya` normal end is not guaranteed on early `prati`, `sthagita`, or a runtime error; this is what the pinned include comments say. We **did not run** the code or certify the illustrative output snippet. No user-visible code or source changed.

**Potential drift warning:** Round 121's proposed original book text stated "watch lists do not exist"; that statement is now **obsolete** relative to the R46 source. Applying the old lines verbatim would manufacture a new documentation error. This Round 124 section deliberately supersedes that older wording.

**PASS** direct code parser/flag+HTML anchor inspection; **NOT RUN - no toolchain** native build and runtime; **NOT APPLIED** canonical book edits; **CANNOT CHECK** Claude's unmerged requested `--debug-from` implementation from this pinned main.
