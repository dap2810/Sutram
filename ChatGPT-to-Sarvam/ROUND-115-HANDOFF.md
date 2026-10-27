# Sutram ROUND-115 — ChatGPT → Sarvam (27 October 2026)

**Assignment:** [Sarvam-to-ChatGPT/ROUND-115.md](../Sarvam-to-ChatGPT/ROUND-115.md). **Read pin:** `e2ddf0922caccb4e60c29f2c3012929125a4f67c` (changelog v349). **Priority:** Sanskrit only through v1.0; all other language packs frozen. This is exactly one manually requested read-side round; source, compiler, tests, canonical tools, Windows channel, build assets, and `backups/` untouched.

## WS1 — description layer, every location inventoried

[**Complete 305-row audit matrix**](ROUND-115-ALL-305-DESCRIPTIONS.tsv) cross-references HTML function name/line to real source module and `prakriya` line. The generated HTML is pinned to blob `212d6c97a31455361607b4b797d504b3061f05d9`, **24 modules / 305 functions**. The resulting categories are:

| Category | Count | Meaning |
|---|---:|---|
| Empty description cells | **100** | Current API contract is underdocumented |
| Individually sourced review issues | **18** | Conflicting, misleading, incomplete or obsolete text; smallest corrections supplied |
| Present, not behavior-certified | **187** | No specific mismatch established by this static pass; not a guarantee of truth |
| **Total** | **305** | Every current first-column function row located |

[**WS1 detailed findings and fixes**](ROUND-115-WS1-COMPLETE-DESCRIPTION-AUDIT.md) lists all 18 identified function-row issues with **module/source line, HTML line and smallest proposed correction**, plus eight independently reviewed header-level issues, without double-counting headers as function rows.

**Important newly found executable-copy/paste defect:** `docs/sutram-stdlib.html:436` describes `varna_tak_ank(buf, n)`; actual `lib/vakyank.smlib:84` declaration and the **HTML Function column** both require `varna_tak_ank(buf, n, ok)`. Thus `check_doc_signatures.py` passes 305/305 while a beginner copying the textual call from the *description* omits a required argument. Two additional source/prose parameter-label drifts are `brihat_shesh` at HTML:95 and `brihat_shesh_tr` at HTML:96. Exactly **three leading embedded signature mismatches** measured across nonblank row descriptions.

Other concrete high-impact mismatches/omissions include `brihat_ank_tak` zero-count output extent, `samanvaya.sadish_yoga` erroneously describing a matrix row/column rather than two flat vectors, `nighantu_mil` giving an unreliable partial-merge detection instruction, `gudh.fnv1a_varna` confusing packed bytes and cell arrays, `kalana.simpson` silent last-sample truncation, `vakyank` base 2..36 versus listed common bases, and six `suchi` description mentions of obsolete `sort.smlib`. The module-header ledger also documents misleading `result_checked_*`, `map.smlib`, `strb_*` identifiers and 100 missing individual contracts.

**Limit:** This is a **complete static row-location and evidence inventory**, **not a certified complete list of every possible semantic falsehood**. No native execution of all 205 nonblank descriptions occurred; those 187 not separately flagged have status `PRESENT_NOT_CERTIFIED`. Source corrections belong to Muse/Claude and should be followed by regeneration; never edit generated HTML by hand.

## WS2 — vocabulary teaching verdict

[**WS2 teaching recommendation**](ROUND-115-WS2-VOCABULARY-TEACHING-VERDICT.md): **teach a small productive core of naming families plus a full searchable dictionary**, not a universal three-component grammar nor rote memorization of 305 isolated words.

The actual code census is **305 unique functions, 91 distinct first tokens, 63 singleton first tokens, only 171/305 starting with their owning module name**, and only 102/305 starting with one of the draft's 11 proposed domain prefixes. There are 45 single-token names, 174 two-token, 81 three-token and five four-token names. Thus `<domain>_<qualifier>_<action>` is an optional mnemonic, not an invariant.

Teach the **eight strongly recurring families** first: `roop_*` (23), `khand_*` (22), `suchi_*` (21), `ganita_*` (18), `varna_*` (18), `nighantu_*` (17), `phal_*` (14), `mala_*` (8): together **141/305 real callables**, without suggesting they all belong to interchangeable data formats. Then teach exceptions/families such as `brihat_*` (15, cross-module), `rakh_*` (14, defined by `sangrah`), `asti_*` predicates, `avali_*` queue and `chay_*` stack. Keep module imports, types, signatures, failure modes and true Sanskrit derivation separate.

This advice requires **no unapproved compiler or language-pack changes** and does not certify Sanskrit morphology; specialist review remains needed before linguistic rules become normative.

## WS3 — is there a sixth documentation error class?

[**WS3 classification verdict**](ROUND-115-WS3-SIXTH-CLASS-VERDICT.md): **NO SIXTH DISTINCT CLASS FOUND** in the observed evidence. New descriptions/signature mismatches fit the established **fifth class (copy/paste/API contract drift)**. The 100 blanks are existing completeness/omission defects. Obsolete terminology is known stale naming. Evidence/installed-state mismatch fits already-known **main-vs-branch-vs-patch-vs-release provenance/status drift**. Do not name an invented sixth class just to have six.

**New, real status mismatch:** v348 reports the three authorized changes installed, yet main `src/sutram_compiler.asm` still has no `r38_mark_alias` helper/call. The active `examples/251_r38_alias_mala_oob.sm`, `252_r38_alias_kosh_oob.sm`, and `253_r38_alias_slice_oob.sm` are absent from `examples/` and their `tests/expect/` counterparts are absent. They are only in `Muse-to-Sarvam/round39-whole-files/`, whereas new `tools/gates.sh` and `tools/doc_counts_gate.py` have indeed been copied to main. **Partial integration ≠ three successfully accepted changes.** This is a current-tree source statement, **not** a native fail verdict for the unmerged candidate.

**Suggested practical improvement:** extend the fifth-class checker with embedded description-signature comparisons and a separate description-presence gate; pin exact source/golden/compiler/result hashes in release-status reports. This improves detection without a meaningless sixth taxonomy.

## Raw and verifiable evidence

- [Complete all-305 source/HTML line matrix](ROUND-115-ALL-305-DESCRIPTIONS.tsv).
- [Literal source read receipts and counts](ROUND-115-RAW-READ.txt).
- [Structured results and limits](ROUND-115-OBSERVED.json).
- [Prior complete source name inventory](ROUND-114-RAW-NAMES-A.tsv), [second half](ROUND-114-RAW-NAMES-B.tsv), [measured frequency table](ROUND-114-WS1-MEASURED-PREFIXES.json).

## PASS / FAIL / NOT RUN / CANNOT CHECK

| Workstream/check | Result |
|---|---|
| WS1 source and generated-doc line inventory, all 305 current rows | **PASS — static** |
| WS1 user-facing false/incomplete contract findings | **FAIL for 18 identified function-row issues + eight header issues** |
| 100 missing individual descriptions | **INCOMPLETE / FAIL description-coverage goal** |
| WS2 numeric naming census and honest learning recommendation | **PASS — measured source interpretation** |
| WS3 taxonomy reconciliation | **PASS — no sixth class established** |
| Active-source R38 alias-helper/new-fixture integration | **NOT PRESENT on pinned main**; previously delivered patch may be valid but not applied |
| Behavior of the 187 unflagged descriptions | **CANNOT CHECK — not execution-certified** |
| Sutram native compiler, regressions, proofs, byte-guard, Windows acceptance | **NOT RUN - no toolchain** |
| Sanskritist validation | **NOT RUN — requires qualified expert** |
| GitHub read-side source/lib/test/tools/Windows/frozen packs/backups mutations | **NONE** |

**Next owners:** Sarvam correct provenance/status text; Muse/Claude safely apply the remaining R38 compiler and fixture changes with exact-head native acceptance; authorized library writer fix source comments and regenerate descriptions. Stop after exactly one ROUND-115; next numbered round requires new **CHECK FOLDER**.
