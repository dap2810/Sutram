# Refusal message and exact boundary — new v312 baseline measurement

**This is pre-fix evidence from the installed v312 compiler. The v313 limit/message must be checked independently when available.** Compiler SHA-256: `7ac8347032b6d9f754b4706d48c20f32f1a43f58324e4432d5463751031b6f93`. No repeated-literal probe or suite was run.

## C1: whole message

For the first refusing count, 16,385 variable terms, compile exit is 1, stderr is empty, and no output executable exists. Exact stdout:

```text
Sutram truti [E_VAKYA_SEEMA]: ekam vakyam ati-vistritam - tasya parikshanam 65536 padeshu na samaptam, ato na sankalyate
Sanket: vakyam laghutareshu vibhaja (madhyamani mulyani namabhih rakshya)
```

## C2: is it actionable?

**Yes, for someone who understands the romanized Sanskrit wording.** The hint explicitly tells the reader to split the statement into smaller statements and keep intermediate values in named variables. It names a remedy, not just a diagnostic code and limit. In English, the practical instruction is “split the expression and store intermediate results.”

For example, replace one enormous sum with several smaller `vitti` assignments and combine their named results. The number 65536 denotes analysis visits, **not the number of source terms**; presenting it as a term allowance would mislead a beginner. A worked small example and a source location would make the remedy easier to apply. This is an editorial assessment by the same assistant that saw the v312 diagnostic, not a first-time-human usability test or proof that all beginners understand it.

## C3: exact adjacent counts

The exact generated shape follows the new brief:

```sutram
mukhya() {
    vitti x = 1
    vitti s = x+x+...  // exactly N occurrences of x
    likha(s)
}
```

| N | Compile | Runtime / diagnostic |
| ---: | --- | --- |
| **16,384** | Exit 0; output exists | Runs with exit 0 and prints `16384` |
| **16,385** | Exit 1; no output | E_VAKYA_SEEMA, number 65536, full hint above |

The bracket 8,200–16,400 from the Linux summary contains this transition. Fifteen probes were run by bisection. Every compiling probe was executed and printed its exact N; every refusal in this search had E_VAKYA_SEEMA and no executable. [Summary](boundary-summary.json), [all commands/exits/messages/timings](boundary-raw.json), [generator](budget-boundary.py). All 15 generated sources are retained.

This boundary is for this exact **local assignment** shape, not every syntax shape. Statement structure changes visit counts; a global initializer or direct `likha(sum)` can differ. No cross-platform reproduction was run in this round, and no v313 result is inferred from v312.
