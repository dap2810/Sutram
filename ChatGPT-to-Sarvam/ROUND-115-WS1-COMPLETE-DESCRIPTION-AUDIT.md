# Sutram ROUND-115 WS1 — complete STATIC description-location review

**Starting main pin**: `e2ddf0922caccb4e60c29f2c3012929125a4f67c`; **generated HTML** blob `212d6c97a31455361607b4b797d504b3061f05d9`. Read all **24/24** library sources and **305/305** generated first-column signatures and description cells. Prior R114 findings were rechecked; new embedded-description-signature checks added. **Do not interpret a static scan as proof that every nonblank description is semantically correct**—no native compiler/behavior test executed.

## Coverage, with unambiguous status

- **305** functions: **100 EMPTY** individual HTML description cells; **18 REVIEW_ISSUE** function rows with a specific source-backed misleading/ambiguous/stale claim; **187 PRESENT_NOT_CERTIFIED** rows where no separate issue was established by this static pass. These categories are disjoint and total 305.
- The complete row-by-row status for all 305, with exact source and HTML lines, is [ROUND-115-ALL-305-DESCRIPTIONS.tsv](ROUND-115-ALL-305-DESCRIPTIONS.tsv). This is the exhaustive *location register*, not an exhaustive runtime proof of accuracy.
- For the 100 blank descriptions: the TSV is the full list with file:line; highest-concentration modules: `ank` 10/10, `chandas` 6/6, `mala` 8/8, `sadhan` 7/7, `ganit` 16/18, `shreni` 12/14, `varna` 16/27. These are **missing**, not assertions falsely proved.
- The checker `tools/check_doc_signatures.py` checks the Function column; all 305 can match while the DESCRIPTION column misstates arity or implementation.

## Confirmed misleading/incomplete individual function rows

| Function | Source line / HTML line | Defect | Smallest correction |
|---|---|---|---|
| `aadhar.brihat_ank_tak` | `lib/aadhar.smlib:20` / HTML:53 | P1: n<=0 writes out[0], >=4*n requirement permits zero cells | For accepted base 2–16, require out to hold at least one element when n <= 0; for positive n ensure room for 4*n; historical pre-R39 overflow aside should be dated. |
| `brihat.brihat_shesh` | `lib/brihat.smlib:257` / HTML:95 | P3: embedded description arg name num differs from declared ank; keep contract labels consistent | Use actual parameter label ank in prose; document num as descriptive role, not formal parameter name. |
| `brihat.brihat_shesh_tr` | `lib/brihat.smlib:270` / HTML:96 | P3: embedded description args num,tr differ from declared ank,scratch | Use actual parameter labels ank and scratch; label scratch as caller-provided. |
| `ganita.chakravala` | `lib/ganita.smlib:76` / HTML:140 | P2: underdocuments required two-cell raw output allocation | Require out to reference >=2 writable qword cells before calling; do not imply allocation. |
| `ganita.samasa` | `lib/ganita.smlib:160` / HTML:141 | P2: underdocuments required two-cell raw output allocation | Require out to reference >=2 writable qword cells before calling; do not imply allocation. |
| `gudh.fnv1a_varna` | `lib/gudh.smlib:29` / HTML:165 | P1: description says mala but implementation hashes NUL-terminated packed byte string | Say NUL-terminated byte-packed string pointer, not qword-cell mala. |
| `kalana.simpson` | `lib/kalana.smlib:34` / HTML:172 | P2: even common length >=4 drops final sample, not described | Uses min length of xs and ys; if usable n is even and >=4, discards last point; only n<3 falls back to trapezoid. |
| `nighantu.nighantu_mil` | `lib/nighantu.smlib:332` / HTML:245 | P1: dst map size alone cannot diagnose partial merge | Use return count versus source entry count to detect a short merge; dst length alone is not reliable on key updates; -1 is scratch allocation failure. |
| `roop.roop_pad_madhya` | `lib/roop.smlib:311` / HTML:293 | P3: confusing npad variable in user-facing text | Pad left and right to width; odd extra padding byte goes on right. |
| `samanvaya.sadish_yoga` | `lib/samanvaya.smlib:135` / HTML:330 | P1: actually flat-vector min-length dot, not matrix row/column | Dot product of two flat float vectors u and v through min(kosh_len(u),kosh_len(v)); not an indexed matrix row and column. |
| `suchi.suchi_laghu` | `lib/suchi.smlib:223` / HTML:407 | P3: historical sort.smlib reference without explicit historical-only label | If retaining historical aside, label sort.smlib as obsolete name of shreni.smlib; or remove historical portion. |
| `suchi.suchi_yog` | `lib/suchi.smlib:246` / HTML:409 | P3: historical sort.smlib reference without explicit historical-only label | Remove obsolete sort.smlib reference, or mark it historical (current module shreni). |
| `suchi.suchi_gan` | `lib/suchi.smlib:253` / HTML:410 | P3: historical sort.smlib reference without explicit historical-only label | Remove obsolete sort.smlib reference, or mark it historical (current module shreni). |
| `suchi.suchi_anwesh` | `lib/suchi.smlib:260` / HTML:411 | P3: historical sort.smlib reference without explicit historical-only label | Mark sort.smlib historical; use current shreni.smlib for present-day reference. |
| `suchi.suchi_asti_sorted` | `lib/suchi.smlib:267` / HTML:412 | P3: current description calls sort.smlib, old name of shreni module | Replace current-form sort.smlib reference with shreni.smlib. |
| `suchi.suchi_dwi_anwesh` | `lib/suchi.smlib:275` / HTML:413 | P3: current description calls sort.smlib, old name of shreni module | Replace current-form sort.smlib reference with shreni.smlib. |
| `vakyank.varna_tak_ank` | `lib/vakyank.smlib:84` / HTML:436 | P1: embedded description lists two args but declaration requires three incl ok | Write varna_tak_ank(buf, n, ok), and note ok is a caller-allocated output cell. |
| `vakyank.ank_tak_aadhar_varna` | `lib/vakyank.smlib:142` / HTML:437 | P2: source accepts every base 2..36, prose lists 2/8/10/16 | State allowed integer base 2..36, alphabetic digits for values 10..35; distinguish the typical 2/8/10/16 examples. |

## Additional MODULE-HEADER errors/omissions (not counted a second time as function-row findings)

| Header/source | Reader-impact issue | Smallest correction |
|---|---|---|
| HTML:161, `lib/gudh.smlib:12-25` | `fnv1a` header calls input a qword-cell `mala`, while source reads bytes through `akshar`; also says nonnegative 32-bit hash may print negative | Say byte-packed input and explicit byte length; remove unsupported negative-print assertion (or provide tested counterexample). |
| HTML:179, `lib/khand.smlib:4-27` | Uses missing current `string.smlib` and `strb_*` filenames in current reference intro | Keep historical note explicitly labeled, or replace with current `khand_*` functions and `lib/varna.smlib`. |
| HTML:216, `lib/mala.smlib:1-9` | Function rows all blank; source title says dynamic arrays although `mala_nava` is fixed-size raw allocation | Describe fixed-size raw array helper, distinct from resizable typed `kosh`; add safe/unsafe per-function contracts. |
| HTML:229, `lib/nighantu.smlib:1-12` | Header calls byte-string API `strb_*`, stale after rename | Describe byte-packed `khand` surface, preserve history as dated note if needed. |
| HTML:259, `lib/phal.smlib:7-10` | Claims generated Result-producing helpers `result_checked_*`; declared names are `phal_janchit_*` | Replace with actual `phal_janchit_*` family. |
| HTML:334, `lib/sangrah.smlib:9-12` | Uses old `map.smlib` name in current text | Use `lib/nighantu.smlib`. |
| HTML:443, `lib/varna.smlib` header | Uses legacy `strb_*` vocabulary in historical comparison | Make historical status explicit; current use is `khand_*`. |
| HTML:134 & 140-145, `lib/ganita.smlib` | Checked-operation status uses `ok[0]` without a prominently stated caller-owned minimum extent | For all checked `ganita_janchit_*`, document `ok` as a writable one-qword cell; for `chakravala` and `samasa`, require two qwords. |

## Newly confirmed embedded description-signature mismatch

A mechanical scan compared every nonempty row description beginning with `name(...)` to the same row's real Function-column signature. **Three mismatches**:
- `docs/sutram-stdlib.html:95` `brihat_shesh`: actual `(ank, shesh, res, n)`, description `(num, shesh, res, n)` (same arity, different parameter label).
- HTML:96 `brihat_shesh_tr`: actual `(ank, shesh, res, n, scratch)`, description `(num, shesh, res, n, tr)` (label drift).
- **HTML:436 `varna_tak_ank`**: actual `(buf, n, ok)`, description **`(buf, n)`**, omitting the third mandatory output argument. Source declaration `lib/vakyank.smlib:84`. This is an executable-copy/paste trap that the 305/305 signature checker does NOT detect.

The `gudh.fnv1a` header's nonnegative hash claim is contradicted by the 64-bit signed arithmetic in `lib/gudh.smlib:14-25`: `h` is reduced modulo 2^32 and never needs signed 32-bit representation. Treat that interpretation as source-arithmetic reasoning, not a compiled runtime receipt.

## Integration/status discrepancy in CURRENT main

Changelog v348 calls R39 bounds tests installed. Exact active-tree reads on this pin find `tools/gates.sh` (19,620 bytes) and `tools/doc_counts_gate.py` (10,921 bytes) installed, **but no `r38_mark_alias` symbol/calls** in `src/sutram_compiler.asm`, and active `examples/251_r38_alias_mala_oob.sm`, `252_r38_alias_kosh_oob.sm`, `253_r38_alias_slice_oob.sm` **do not exist**. They remain in `Muse-to-Sarvam/round39-whole-files/`. The claimed three-part installation therefore is **not complete on this pinned main**. Do not claim the new alias guard passed current native acceptance. This is separate from WS1's *stdlib* prose issues and is handed off as a status correction.

## Safe correction order

1. Have authorized `lib/` owner fix source comments and per-function metadata, preserving callable names and tested semantics. Never hand-edit the generated HTML.
2. Regenerate reference on exact candidate and verify 305/305 current declarations, zero embedded first-signature mismatches, and zero unexplained empty description cells (if full descriptions approved).
3. Compiler-equipped Muse/Claude run both valid and negative execution fixtures for claimed return semantics. Keep the static gate separate from dynamic contract coverage; do not invent PASS for 187 remaining prose entries.
4. Sarvam correct status/provenance statements only after active-tree exact-sha integration of alias fix and fixtures.

**PASS** whole source/HTML row location inventory (305/305, 24 modules), 18 specifically evidenced function-row issues and eight module-header issues recorded. **FAIL** current documentation contracts on those lines. **NOT RUN - no toolchain** for native compilation, full behavior, Windows. **CANNOT CERTIFY** all remaining 187 entries from static checking alone.
