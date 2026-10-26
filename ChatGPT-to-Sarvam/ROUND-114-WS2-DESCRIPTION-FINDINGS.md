# Sutram ROUND-114 WS2 — complete generated-page description INVENTORY and verified corrections

**Pinned main:** `df4b5237b8962adda7f0693f1fc5bb1408567798`. **Generated input:** `docs/sutram-stdlib.html` Git blob `212d6c97a31455361607b4b797d504b3061f05d9`. All **24 module tables and 305 first-column function rows** inspected and recorded in [the full row inventory](ROUND-114-HTML-ROW-INVENTORY.tsv), including exact HTML line, module, function name, character count and presence/absence of a description.

## Measured documentation completeness — not behaviour proof

**305 total = 205 nonempty description cells + 100 empty description cells.** **Every missing individual function description** is separately located in the 305-row inventory; this is a complete missing-description inventory, not a hand-picked sample. Most notable:
- `lib/mala.smlib` **8/8 descriptions empty** (`docs/sutram-stdlib.html:219-226`).
- `lib/ank.smlib` **10/10 empty** (HTML:60-69); `lib/chandas.smlib` **6/6 empty** (HTML:103-108); `lib/sadhan.smlib` **7/7 empty** (HTML:309-315).
- `lib/ganit.smlib` 16/18 empty (HTML:114-131); `lib/shreni.smlib` 12/14 empty (HTML:377-390); `lib/varna.smlib` 16/27 empty (HTML:446-472).
- `samanvaya.samanvaya_akar_na` (HTML:321), `kalana.kalana_trapiz` (HTML:171), `ganita.kuttaka` (HTML:137) are missing individual descriptions even though some operational explanation is buried in header paragraphs.

**Important:** a blank cell is a missing contract, not necessarily a *false* assertion. `tools/check_doc_signatures.py` can report 305/305 PASS and still miss all 100 blank cells.

## Verified misleading, incorrect or materially incomplete reader-facing prose

The following is the **complete list of problems verified in this round's source/HTML review**, not an unfounded assertion that the other 195 nonempty descriptions have received native behavioral proof. Generated HTML must not be edited by hand; source comments below are the authoritative future edit locations for Muse/Claude.

| Severity | HTML location / source | Finding / concrete smallest safe text correction |
|---|---|---|
| **P1** | `docs/sutram-stdlib.html:53`; `lib/aadhar.smlib:16-35` | `brihat_ank_tak` says caller needs **>=4*n** output cells, but source branch `n<1` writes `dst[0]`. For n=0 the published requirement allows zero cells, yet one is written. Say **out must have at least max(1,4*n) writable cells on accepted input**, with a valid pointer; or separately document n<=0 requires one cell. Existing historical n>=22 overflow aside is stale after R39 guard; remove or mark historical. |
| **P1** | HTML:330; `lib/samanvaya.smlib:135-144` | `sadish_yoga` is documented as a matrix row-i / column-j dot product, but implementation takes **two flat vectors u and v** and sums through **min(kosh_len(u),kosh_len(v))**. Replace with **"dot product of two flat `kosh dasham` vectors up to the shorter logical length"**. No row/column selection exists. |
| **P1** | HTML:161-164; `lib/gudh.smlib:10-25` | `fnv1a` describes input as a **"mala s" of character codes**, but source indexes bytes via `akshar(str,i)`, and `fnv1a_varna` measures the NUL-terminated **byte string** via `vartani_len`. Replace `mala s` with **byte-packed string pointer / byte count**. The comment that a bounded 0..2^32-1 hash "may print as negative via likha" is unsupported by current 64-bit integer arithmetic (multiplication < 2^63 then positive modulo); delete unless a native counterexample is demonstrated. |
| **P1** | HTML:245; `lib/nighantu.smlib:323-348` | `nighantu_mil` says "check `nighantu_maap(dst)` afterwards to detect partial merge". Destination size alone is **not a correct partial-merge detector**, as overwriting existing keys need not increase count. The function's `merged` increments on every successful insertion/update, returning early at failed `nighantu_khip`. Say **"a return value < nighantu_maap(src) indicates incomplete merge; -1 means scratch allocation failed without changing dst"**. Warn that a positive partial return may already have changed dst. |
| **P1** | HTML:216,219-226; `lib/mala.smlib:1-9,20-87` | Source `lib/mala.smlib:1` calls these **dynamic arrays**; the generated HTML section itself only describes raw memory and caller-tracked length. `mala_nava` actually returns a **fixed-size caller-managed raw qword buffer** (no growth), unlike language `kosh`. All eight function descriptions blank, hiding that `mala_grah/sangrah/purn/pratilip/yog` use unchecked raw `pad8/likh8`, while `*_surakshit` checks supplied count but not actual memory provenance. Correct header to **"fixed-size raw qword-array helpers"**, add per-function contracts and out-of-range return-value ambiguities. |
| **P1/P2** | HTML:134, `lib/ganita.smlib:76-84,151-152,160-167` | `chakravala` and `samasa` list `out[0]` and `out[1]` but **do not state required two allocated 8-byte output cells**. Add this explicit caller-owned pointer extent precondition, and for checked arithmetic `ok[0]` require a valid 8-byte cell (see `tests/stdlib/ganita_checked.sm`). This is incomplete rather than mathematically false. |
| **P2** | HTML:172; `lib/kalana.smlib:32-40` | `simpson` tells users odd point count is needed, but omits that **an even usable sample count >=4 silently drops its last point**, after computing min input lengths. State exactly that; only n<3 uses trapezoid fallback. |
| **P2** | HTML:437; `lib/vakyank.smlib:138-161` | `ank_tak_aadhar_varna` calls out "base (2/8/10/16)" while source permits **every integer base 2 through 36**, mapping values 10+ to lowercase alphabetic digits. Replace base examples with **"base 2..36"**; retain n>=0 and zero-terminator facts. |
| **P2** | HTML:179; `lib/khand.smlib:4-6,19-27` | Current `khand` module intro says "not inside string.smlib" and "Every `strb_*` function". Both are **legacy naming references**, not current API entry points. Say **"the `khand_*` explicit-length functions"**, and refer to the actual `lib/varna.smlib` boundary module. Retain warning that NUL-terminated forms do not respect slices. |
| **P2** | HTML:161-164; `lib/gudh.smlib:10-25` | `fnv1a_varna(s)` is also described as hashing a NUL-terminated `mala`—use **NUL-terminated byte string**, not a qword-cell character array. This is the same representation error as `fnv1a`, listed separately so both function comments get fixed. |
| **P2** | HTML:259; `lib/phal.smlib:7-10` | Header tells users the checked function group is `result_checked_*`, but actual definitions in this module are **`phal_janchit_*`**. Replace only that header claim; do not rename real callables. |
| **P2** | HTML:334; `lib/sangrah.smlib:9-12` | Header calls the dependent map module `map.smlib`; actual `lib/nighantu.smlib` exists and supplies the key machinery. Replace prose filename with **`nighantu.smlib`** without touching APIs. |
| **P3** | HTML:293; `lib/roop.smlib:309-313` | `roop_pad_madhya` says "**npad** on BOTH sides" using internal variable name rather than describing effect; replace with **"pad both sides to requested width; odd extra pad byte goes right"**. Clarity, not a demonstrated runtime defect. |

Historical caveat: source comments describing "the old code trapped" can be valid history; remove or date them only when likely to be read as a current behavior promise. Do not globally replace identifier substrings or erase intentional negative-test history.

## How to close mechanically

1. Authorized library owner edits only the relevant **source comments**, never the generated HTML manually.
2. Regenerate `docs/sutram-stdlib.html` with the exact reviewed generator, and verify all 305 names, 24 modules, and descriptions.
3. Add a **description presence gate** (`0 blank` or explicitly approved exceptions) and a **contract example gate** (compile and verify deterministic source snippets under a real compiler). Neither is implemented or run by ChatGPT.
4. Compile behavior and bounds tests through Muse/toolchain; full semantic proof remains out of scope of a source-read sweep.

**PASS** exact accounting 305 HTML function rows and 100 blank locations; **FAIL** documented reader-facing contract in identified rows; **NOT RUN - no toolchain** native execution; **CANNOT CERTIFY** full behavioral accuracy of 205 nonblank descriptions from static text alone.

