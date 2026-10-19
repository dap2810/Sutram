# Round 72 — hardcoded Sanskrit keyword immediate audit (v172)

Baseline main `6fd8b1cf2b072768a9ede0677ed32983c13e9961`; source blob on the review branch `9c41189e1bf30caf1dcc3b8eadc883b11b07f12b`. All line numbers below refer to this reviewed source; R72's appended reclamation helper does not shift existing lines. This is a **source inspection**, not a proof of the behavior of every program.

| Source lines | Site | Hardcoded bytes or length | Canonical word | Current consistency |
| --- | --- | --- | --- | --- |
| 673, 3046 | Core / module graph data | `db "yoj"` | `yoj` | MATCH |
| 676 | Contextual range keyword | `db "tak"` | `tak` | MATCH |
| 3044 | Export literal | `db "niryat"` | `niryat` | MATCH |
| 2330–2349 | R49 physical diagnostic locator | `+3`, `0x6F79` (yo), `0x6A` (j), next-byte separator | `yoj` | MATCH; fragile on rename |
| 2355–2363 | R49 export diagnostic locator | `+6`, `0x7972696E` (niry), `0x7461` (at) | `niryat` | MATCH, **possible prefix-only false location**: unlike `yoj`, it does not verify a boundary after the six bytes |
| 2542–2562 | Module expander | `0x6F79`, `0x6A`, `+3` | `yoj` | MATCH; hardcoded next-byte access `[rsi+3]` lacks a local end-of-input check |
| 3535 | Export graph parser | `add r8,6` | `niryat` | MATCH |
| 3799 | Import graph parser | `add r8,3` | `yoj` | MATCH |
| 8143–8153 | For-range parser | `0x6174` (ta), `0x6B` (k), exact NUL | `tak` | MATCH |

**14 source-identity assertions passed** for the audited immediate/data sites. This only proves they match today's ASCII spellings. The audit found **no confirmed currently wrong keyword-length comparison** among these audited sites, but found two worthwhile defensive-review items: the `niryat` diagnostic prefix recognition and the module expander's read-ahead. Their actual failure modes require discriminating compiler tests.

Separate safety observation outside the requested immediate audit: `load_lang_file` copies native and canonical words into 64-byte `lang_w1` / `lang_w2` scratch buffers (around lines 1268–1315) without an obvious pre-write bound in those loops. This deserves a bounded malformed-pack test and separate compiler review; **no exploitability or actual crash was tested or is claimed**. Identifier-length limits are not the same as keyword spellings.

After any future rename, rerun `python3 tools/r72_keyword_gate.py`. The gate is pinned to these exact names and fails on missing/multiple anchors; review and update both canonical spellings and expected immediates together. Do not change frozen Sanskrit vocabulary just to satisfy the test.

No accepted compiler golden, core grammar, or token semantics were rewritten for this audit.
