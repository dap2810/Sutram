# ROUND-111 WS3 — caller-breaking old identifiers ONLY

Base for this verification: main 11b2d5dd7d3985d8a9d9ab56b102454b4c0a2874. This is after Muse R35 was applied.

| File:line | Old callable name | Correct/current name | Status |
|---|---|---|---|
| lib/chandas.smlib:82 | meru_pankti(a, n) | meru_mala(a, n) | FIXED on main; function declaration now meru_mala |
| tests/stdlib/chandas_meru_pankti.sm:4 | meru_pankti(a, 4) | meru_mala(a, 4) | FIXED on main, direct fetch confirms line 4 calls meru_mala |

Current callable-name mismatches between all 305 lib declarations and all 305 documented HTML signatures: **0** in the pinned direct source comparison. The HTML has meru_mala, not meru_pankti. Do NOT present the old name as an outstanding source defect.

Other caller-breaking old-token function identifiers from the independent R110 library sweep: **none corroborated**; Muse R35 independently found exactly one and fixed it. The legitimate still-existing lib/sadhan.smlib:40 util_chinha is NOT renamed: it is an existing public helper used by callers; the owner's contract decision would be required to change it.

EXCLUDED from this identifier-only action list: comments, old source filenames in headers, historic prose, keyword rejection fixtures, generated HTML description text, and generic English words. Separate content defect: lib/sadhan.smlib:4 still teaches ayojan util, but this does not constitute a function identifier.

Native compile/run in this read-side session: NOT RUN - no toolchain.
