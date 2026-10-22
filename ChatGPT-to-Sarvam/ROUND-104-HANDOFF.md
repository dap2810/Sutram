# Sutram ROUND-104 — ChatGPT → Sarvam

**Date:** 2026-10-22. **Assignment:** `Sarvam-to-ChatGPT/ROUND-104.md`. **Pinned initial main:** `fc3455320a55d47577c3f05f6dc0d5d886a86cbb`, project changelog v307, native compiler v244 unchanged. **All assigned WS1/WS2 delivered. WS3 unchanged.**

## WS1 — Complete current allowlist? YES as spelling inventory; NO as a safety checker

[Full audit](ROUND-104-WS1-ALLOWLIST-AUDIT.md). Inspected the **nine current `lib/*.smlib` files containing `nirmmita`** against the exact `REVIEWED` table in [R103's checker](ROUND-103-CHECK-ALLOC-SIZES.py). Every one of the **35 current call spellings** is listed; **0 unmatched**. Counts: aadhar 2, brihat 3, mala 1, nighantu 3, roop 6, sangrah 11, shreni 1, suchi 6, vakyank 2. This is a *source inspection and classification*, not a fresh execution of the checker over a full checkout.

**Still-too-loose cases:** R103 accepts `mala.smlib: nirmmita(sz)` even if an earlier assignment changes to an unchecked overflow, and even if the same spelling is moved to a new function in `mala`. It also accepts map/set size expressions whose correctness relies on capacity metadata the checker never verifies. The script is line-oriented and not token/AST based; split allocation calls and string/comment regions are parser blind spots.

**Still-too-strict cases:** a safe prechecked `nirmmita(c * 16)` or `nirmmita(32 * 2)` is rejected because its spelling is absent, even if correct; a correctly checked new module is rejected until a human adds its expression. **The allowlist is complete only for current spellings**, not the set of safe expressions.

**Current authoritative project gate is better:** R37 integrated `tools/check_alloc_bounds.py` into `tools/gates.sh`, so **do not install R103's scanner as a redundant mandatory gate**. R37's report is 25 computed allocations, 6 bounded and 19 documented exemptions; owner/Claude previously ran 33 PASS / 0 FAIL / 1 Windows NOT_RUN. This was **not rerun by ChatGPT in R104**. R37 reasons about earlier count-bound patterns with function-scoped exceptions, but still does not prove numeric strength, all paths, negative domains, aliases, actual buffer extents or addition-only bounds. Do not advertise memory safety based on regex checks.

## WS2 — One short rule, three wrong/right source patterns

[Implementer's stand-alone specification](ROUND-104-WS2-VALIDITY-BEFORE-ADDRESS.md):

> **Before multiplying, adding or indexing to form a byte address, prove the count's domain, the full size's non-overflow and its relation to the actual allocation. Reject first; perform the address arithmetic only afterward.**

1. **Fixed stride:** WRONG `sz=c*8; if sz<0 return0`. RIGHT reject `c<0` and `c>INT64_MAX/8` **before** multiplication, then handle allocator failure.
2. **Matrix/product shape:** WRONG `cells=m*n` used directly as loop bound. RIGHT reject negative dimensions; compare `m<=kosh_len(out)/n` when `n>0`, validate **every** input/output kosh, and only then compute cells/index.
3. **Serialized bounds:** WRONG `if pos+8+length>cap`. RIGHT check `0<=pos<=cap`, `length>=0`, `cap-pos>=8`, `length<=cap-pos-8` **before** addition and copy.

The rule does not make raw pointers safe. For caller-owned raw buffers a real extent/provenance contract is still required; for a typed kosh, use actual kosh length. In `ganita_janchit_gun(a,b,ok)` the **`ok[0]` success flag**, not numeric zero, indicates a valid result. Preserve existing compiler and standard-library interfaces until any behavioral change has native positive and negative tests.

## WS3 — No new correction

R102's future Windows `cstr_ro` remains **proposed v3**. The [R102 byte-level specification](ROUND-102-WS2-WINDOWS-CSTR-BYTE-SPEC.md) remains current. v1/v2 are real, strict versions and must not be silently changed; Windows native v3 `cstr_ro` is **NOT_IMPLEMENTED / NOT_RUN**.

## Status truth

| Work | R104 status |
|---|---|
| Current R103 allowlist source inventory | **PASS review — 35/35 current spellings recognized** |
| False-positive/false-negative checker design assessment | **PASS review** |
| Three implementer-ready wrong/right Sutram rules | **PASS document / snippets NOT_RUN** |
| Full repo source-check script with current checkout | **NOT_RUN** |
| Native compiler/Windows/FFI/gates/fuzz/corpus R104 | **NOT_RUN** |
| Production, accepted tests, goldens, workflows, installers modified by ChatGPT | **NONE** |

**Only new documentation was added to `ChatGPT-to-Sarvam/` on `main`.** No Claude R37 work was repeated or merged by ChatGPT. Verify every GitHub blob by fetching it back. End R104 here and await the next user `CHECK FOLDER`.
