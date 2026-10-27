# Sutram ROUND-117 WS1 — does a sixth independent documentation-error class exist?

**Verdict: NO SIXTH CLASS FOUND in the source evidence now reviewed.** This continues the R115-WS3 and R116-WS2 decisions. It does NOT mean there are no current documentation errors.

## Why the new evidence does not require a new class

| Current evidence on pinned main `fd02405aad986001c451ee5c5decb91346c7bb53` | Category already recognized | Distinct new class? |
|---|---|---|
| The R116 description-source comments were changed 35/35 but the generated `docs/sutram-stdlib.html` is still the **old** blob `212d6c97...` | Existing **generated/document publication provenance drift** and **fifth-class API copy/paste contract drift** | **No** — same failure chain, now observed after the underlying source fix |
| `varna_tak_ank(buf,n)` persists in the HTML description although correct source comment and callable require `ok` | Fifth-class **example/signature copied incorrectly into reader-facing prose** | **No** |
| `sadish_yoga` old matrix row/column description persists in generated HTML, current source comment correctly says two flat vectors | Fifth-class **semantic/API contract drift** | **No** |
| 100 empty per-function descriptions measured in R115, not yet authored | Known **documentation coverage/omission** | **No** |
| R41 alias guard tests/binaries exist in partner delivery but are not yet guaranteed on canonical main | Known **delivered vs merged vs tested provenance** | **No** |

## Improve checks rather than invent a taxonomy

1. Add a **generator reproducibility gate**: run `tools/gen_stdlib_ref.py` in a clean, isolated pinned checkout and compare its resulting `docs/sutram-stdlib.html` **bytes** with the committed HTML. A valid 305/305 signature comparison alone cannot detect out-of-date descriptions.
2. Compare function-row description lead signatures with first-column signatures. Already known source-independent errors on the old generated page include `brihat_shesh`, `brihat_shesh_tr`, `varna_tak_ank`.
3. Keep the 305-row description-presence inventory and a human contract/example acceptance process.
4. Record exact main source SHA, generator SHA, generated HTML SHA, audit date and executable acceptance separately. A successful generator run does not prove the prose's semantics, just synchronization.

## Measured basis

- The current `lib/` source has **35/35** R116 comments applied, confirmed by exact old/new matches. `docs/sutram-stdlib.html` still uses older descriptions in **18 function rows and seven module headers** across the 15 changed modules.
- Compiler version on current main is **v248**; whether a source candidate is included in a release cannot be inferred from a Muse outbox alone.

**PASS:** grounded classification. **Verdict:** **NO SIXTH CLASS FOUND**.  
**FAIL (documentation currency):** generated reference not synchronized.  
**NOT RUN - no toolchain:** compiler/native behavior/Windows, generator execution.  
**No protected-source writes.**
