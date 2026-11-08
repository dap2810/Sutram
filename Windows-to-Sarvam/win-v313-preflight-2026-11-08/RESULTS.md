# Windows round — stopped at version preflight

The current package at `d935506a56190dded437317512ad0721fc87fd2f` contains **v312**. The brief requires **v313 or later** and explicitly says to stop if v312 is found. [Exact version output and all three artifact hashes](PREFLIGHT.md).

| Test | Expected | Actual | Pass? |
| --- | --- | --- | --- |
| P1 — embedded version | v313 or later | Sutram 1.0 (v312) - sampurna sutra | **FAIL — STOP** |
| A1 — walk-budget message | recorded | Stopped at P2 | NOT RUN |
| A2 — AST-capacity message | recorded | Stopped at P2 | NOT RUN |
| A3 — messages distinguishable? | yes | Stopped at P2 | NOT ASSESSED |
| A3 — remedy named? | yes | Stopped at P2 | NOT ASSESSED |
| A4 — --analysis-steps=64 | accepted | Stopped at P2; flag availability not probed | NOT RUN |
| A4 — zero, negative, non-number | refused | Stopped at P2 | NOT RUN |
| B1 — whole instruction visible | full text | Stopped at P2 | NOT RUN |
| C1 — no new temp directory | none | Stopped at P2 | NOT RUN |
| C2 — two uninstall runs | consistent | Stopped at P2 | NOT RUN |
| C3 — nothing survives | nothing | Stopped at P2 | NOT RUN |
| D — fresh-shell identity | one path, expected version | No installation performed | NOT RUN |
| D — native suite | 322 PASS, no FAIL | Stopped at P2 | NOT RUN |
| D — elapsed time | compare to 18.6 s | No suite run | NOT RUN |

Only extraction, hashing and the native `--version` invocation were performed. No results from the previous v312 runs are promoted to this round. The report, exact supplied brief, raw output and reproduction script are retained with EVIDENCE.sha256. No product code, workflow, installation, registry or earlier evidence was changed.
