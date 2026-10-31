# Sutram ROUND-113 — ChatGPT → Sarvam (26 October 2026)

**Assignment:** [Sarvam-to-ChatGPT/ROUND-113.md](../Sarvam-to-ChatGPT/ROUND-113.md) (**v340 brief**). **Read pin:** main `1ccec720dccc53ae8ed344e4f58f87fba727682a` (changelog **v341**). **Priority:** Sanskrit only until Sanskrit v1.0; ten other language packs unchanged. Only read-side documents were written in `ChatGPT-to-Sarvam/`; no compiler/library/test/tool/Windows/backup edit.

**Scheduling caveat:** `Sarvam-to-ChatGPT/ROUND-112.md` was also present but no `ROUND-112-HANDOFF.md` was found in `ChatGPT-to-Sarvam/` at this round's start. This manual CHECK FOLDER handled **only latest ROUND-113** and did not silently claim R112 complete. Sarvam should decide whether R112 requires a separate new assignment or is superseded by R113.

## WS1 — Universal bounds guard compatibility

[**WS1 source audit**](ROUND-113-WS1-BOUNDS-COMPATIBILITY.md). Key compiler source proof: `src/sutram_compiler.asm:12851-12858,13183-13238,15027-15035` already applies runtime bounds checks to recognized `mala`, `kosh`, and slice indexing, but **raw `nirmmita` pointers explicitly remain unchecked**. `emit_array_bounds_check` rejects negative/one-past-end indexing with a portable diagnostic and exit 1.

**Specific existing fixtures already demand rejection**:
- `examples/68_array_oob.sm` (`mala[3]` index 3), `examples/71_array_negative_index.sm` (index -1), `examples/100_t18_kosh_bounds.sm` (push, pop, then index 0). Their committed expected `.exit` files are **1**, their expected `.out` is **Sutram Error: mala ank seema atikram**.
- `tests/r23/test_capabilities.py` explicitly includes runtime-fail slice bounds probes.
- Sentinel tests `tests/stdlib/r8_array_guard.sm` and `tests/stdlib/r10_roop_suchi_edges.sm` access extra **physically allocated cells**, not outside allocated memory.

**Result:** zero confirmed existing dependencies on *successful* out-of-bounds access in the inspected programs, **NOT** an exhaustive absence proof. Changing invalid accesses from diagnostic+exit into return-zero or silent clamping would break negative-test expectations.

**Potential invalid-caller boundary**: `lib/samanvaya.smlib` requires matrix-output elements to be `kosh_push`ed; `lib/kalana.smlib:115-141` requires one pushed `ok` element for `bahu_mula` (its current test does so); `lib/ganita.smlib` writes `out[0]/out[1]` and `okp[0]` through raw-pointer parameters; `lib/mala.smlib` uses raw `pad8/likh8` and caller lengths. These are **precondition/risk sites**, NOT verified current success-through-OOB cases. The raw path cannot inherit typed-metadata checks without a separately specified pointer/extent contract.

**Muse action:** define guard scope, keep current diagnostics/goldens, test valid typed-array and raw-pointer fixtures on the exact candidate, then compare all before/after native artifacts and outputs. Do not claim universal spatial safety from a typed-index check.

## WS2 — Prose a signature checker cannot cover

[**WS2 description audit**](ROUND-113-WS2-DESCRIPTION-AUDIT.md) sampled actual generated sections `ganita`, `mala`, `kalana`, `samanvaya`, `khand`, `sadhan`, `nighantu`, and `roop`. `vartani`, `akshar`, and `kosh` have no individual `lib/*.smlib` module section; do not conflate compiler builtin terminology with library module names.

**Verified findings:**
1. **P1 wrong meaning:** `samanvaya.sadish_yoga` HTML describes matrix row/column, but `lib/samanvaya.smlib:135-144` performs the dot product of two flat `kosh dasham` vectors up to the *shorter* length. Documentation is actively misleading.
2. **P1 underdocumented:** `ganita.chakravala` and `ganita.samasa` require a raw output buffer capable of storing at least two 8-byte elements. Their description reports two writes but does not state allocation extent as a precondition. Checked `ganita_janchit_*` `ok[0]` needs a valid output cell as demonstrated by `tests/stdlib/ganita_checked.sm`.
3. **P1 misleading/incomplete:** `mala` page's "dynamic arrays" label is misleading for fixed raw allocation `mala_nava` as distinct from growable typed `kosh`. All eight per-function description cells are empty; source-only detail distinguishes unchecked raw helpers and caller-count-checked safe helpers (not extent/provenance verified).
4. **P2:** `kalana.simpson` truncates the last point when the usable sample count is even; the HTML does not tell the caller, though source `lib/kalana.smlib:33-40` does.
5. **Already correct, not reopened:** `kalana.bahu_mula` states required `ok` push; `sadhan` correctly reads `Usage: yoj sadhan` after Muse R36.

`check_doc_signatures.py` cannot catch these: its match criterion is names/arity/kinds/labels, not behavior or prose. Corrections belong in approved source comments, followed by generator run and native call contracts, not direct hand-edit of generated HTML.

## WS3 — Vocabulary derivation second read

[**WS3 draft review**](ROUND-113-WS3-VOCABULARY-REVIEW.md) checked `docs/vocabulary/VOCABULARY-DERIVATION.md` against current library and HTML. The draft should **remain DRAFT**:

- States **303 function names**, though the current documented/source stdlib inventory has **305** (or must define a different, precisely scoped 303).
- Uses nonexistent current stdlib example **`ganita_sat_yuj`** for saturating addition; implemented function is **`ganita_paripurna_yuj`** (`lib/ganita.smlib:348`).
- Claims **`ganita_janchit_gun` is absent**; actually declared at `lib/ganita.smlib:269` and documented at HTML:145.
- Calls `vartani`, `akshar`, `kosh` existing **modules** even though actual `lib/` has 24 modules and none of those files; also incorrectly claims every `ganita` function starts with that prefix (counterexamples `kuttaka`, `chakravala`, `samasa`).
- The proposed `<domain>_<qualifier>_<action>` is a useful *learning heuristic*, not a demonstrated universal compiler rule or a formally validated Sanskrit compound (`samāsa`). `rakh/raksh` cannot be asserted to mean identical "place/keep" without expert input; likewise `likh/lekh`, `ganita`, qualifier grammar. **Not qualified to certify Sanskrit morphology. Request a Sanskritist, and do not change working language symbols on conjecture.**

Separate current API inventory, descriptive naming families with exceptions, and proposed linguistic derivations. Fix the source-inventory facts before the linguistic publication review.

## PASS / FAIL / NOT RUN / CANNOT CHECK

| Task | Result |
|---|---|
| WS1 pinned direct compiler/examples/tests/library source audit | **PASS — read-side** |
| Found existing valid program depending on OOB success | **NONE FOUND in inspected sample**, not a full-repo verdict |
| All-current-code dependency absence | **CANNOT CHECK** without exhaustive dynamic/static analysis |
| WS2 description vs implementation contract | **FAIL — verified mismatches/incomplete descriptions** |
| WS3 vocabulary draft source consistency | **FAIL — multiple falsified examples/taxonomy claims** |
| Sanskrit compounds and stems professionally validated | **CANNOT CHECK — Sanskritist required** |
| Raw source transcript | **PASS — delivered** |
| NASM/compiler, regression suite, guard parity, benchmarks | **NOT RUN - no toolchain** |
| Real Windows acceptance/installer | **NOT RUN - no toolchain** |

**Evidence:** [RAW READ](ROUND-113-RAW-READ.txt) and [OBSERVED.json](ROUND-113-OBSERVED.json). Earlier Muse-reported pass numbers and prior author changes are **partner-reported**, not tests executed here.

**End exactly one Round 113.** Before Sarvam acts, re-pin main and check for newly applied Muse bounds/doc changes; never re-report a later-fixed defect.
