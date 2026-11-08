# v312 walk budget — native compiler

The repository's variable-based shape meets the claim on Windows. The brief's illustrative literal sum reaches a different limit first, so “any 20,000-term sum produces E_VAKYA_SEEMA” is not established.

All six generated source files and their generator [budget.py](budget.py) are retained. Counts are exact: each expression joins precisely 10,000 or 20,000 terms with `+`. The three shapes are literal `1`, local variable `z = 1`, and a module-level initializer using `z = 1`. Each target path was absent before compilation. Tests used the installed compiler, SHA-256 `7ac8347032b6d9f754b4706d48c20f32f1a43f58324e4432d5463751031b6f93`.

| Shape | Terms | Compile exit | Output file | Observed result |
| --- | ---: | ---: | --- | --- |
| Literal `1+1+…` | 10,000 | 0 | Present | Runs, exit 0, prints `10000` |
| Literal `1+1+…` | 20,000 | 1 | Absent | `Sutram truti: vakya-vriksh seema atikram` — **different from brief's exact expected diagnostic** |
| Local `z+z+…` | 10,000 | 0 | Present | Runs, exit 0, prints `10000` |
| Local `z+z+…` | 20,000 | 1 | Absent | E_VAKYA_SEEMA, names 65536 |
| Global `z+z+…` initializer | 10,000 | 0 | Present | Runs, exit 0, prints `10000` |
| Global `z+z+…` initializer | 20,000 | 1 | Absent | E_VAKYA_SEEMA, names 65536 |

Exact local/global 20,000-term stdout (stderr empty):

```text
Sutram truti [E_VAKYA_SEEMA]: ekam vakyam ati-vistritam - tasya parikshanam 65536 padeshu na samaptam, ato na sankalyate
Sanket: vakyam laghutareshu vibhaja (madhyamani mulyani namabhih rakshya)
```

Literal 20,000-term stdout (stderr empty):

```text
Sutram truti: vakya-vriksh seema atikram
```

The literal diagnostic is the earlier syntax-tree capacity refusal; this probe does not reach the expression walk's diagnostic. The actual Linux gate `tests/r143/test_walk_budget.py` uses variables, not repeated integer literals. Its local and global shapes were reproduced here. No Linux literal comparison was run, so this report does **not** establish a platform discrepancy. No crash, hang or output file occurred on any refusal.

[Raw commands, source/output hashes, exits and timings](budget.json). The generator exits 1 because it deliberately retains the literal-20,000 expectation mismatch (five of six expectations pass); that is not hidden as a harness failure. No compiler, example or golden was modified.
