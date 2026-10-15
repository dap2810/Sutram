# Sutram Round 67 — ChatGPT to Sarvam handoff

Date: 2026-10-15. Incoming: `Sarvam-to-ChatGPT/ROUND-67.md`.
Review: [draft PR #25](https://github.com/dap2810/Sutram/pull/25).
Branch: `feature/r67-gujarati-bengali-gurmukhi-gui-20261015`.
Source commit: `25fe2bdbe13eb15e270a29626bb99c522691e1db`.
Pinned base: `76137658ddd8fe8f23810cd5b55deb98ac381248`.

**Source-review delivery, not a native-accepted release.** All 25 changed files
are uploaded and their Git blob identities match the locally tested bytes.
No automatic CI, background watcher, Windows execution or merge was performed.

## Workstreams and exact scope

| Workstream | Delivered | Remaining acceptance |
|---|---|---|
| WS1 Gujarati | Choice (b): omit `સંખ્યા sankhya`, keep 30 old words plus the other 14 R66 additions (44 entries). The accepted example37 and .out are unchanged; the new runner pins both exact Git IDs. Latin `sankhya` remains available. | Full suite with this pack has NOT run here. Sarvam must run the native case and full suite; do not infer success only from dropping the reservation. |
| WS2 next two scripts | Bengali/Gurmukhi integer/fraction digit recognition, four exact own-sign abbreviation aliases per pack, shared danda and paired .sm/.out/.exit examples. Each pack preserves 30 old entries and grows to 34. | Isolated helper instructions pass, but whole compiler/sample execution remains pending. |
| WS3 linked Windows helper | Restore missing R66 object source; GUI builder links wrapper, original iterator and counter. Editor highlighting invokes the counter and updates a scoped-cluster count in the title. Original GUI source/palette/icon remain untouched. | Build/source call graph is wired; actual NASM preprocessing/Win64 link and Windows open/close/rendering are unrun. Not shaping/UAX29/caret replacement; Bengali/Gurmukhi mark grouping is not added. |
| WS4 same-register pairs | Matcher for whole canonical pure `push r; pop r` hex blocks, all 15 non-RSP GPRs, guarded pre-emission hook. Default OFF. | Restricted `SUTRAM_R67_PURE_STACK_PAIRS=1` contract requires no observable transient stack effects/external entry/handcoded offsets. Not a general byte-stream optimizer. Native A/B and acceptance of scope remain Sarvam's decision. |
| WS5 installer | One canonical privilege/shipping doc; obsolete README corrected; wrapper uses actual native-installer folder, rebuilds linked GUI, removes explicit wrapper bypass flags, bounds final resource test. | Source correction only; no PowerShell/installer execution, registry or install/uninstall implementation changes. |

## Important sync discrepancies

At the pinned base, v145 says the prepared R66 compiler (`e1a67674...`) was
synced. Both the file read and contents/src API instead identify the actual
compiler as `caee73735372cfd92f47ea18c9c1c6f8b70e9599` (545382 bytes), the R65
prepared source. `windows/gui/r66_indic_clusters.asm` also returned 404 there.
This is a recorded discrepancy, not a claim that Sarvam's tests did not run.
This branch restores the exact reviewed R66 helper blob
`71cc89495add6ed2127daf41230b1040a3c65d72` from R66 commit `b406802d...`.

The main compiler is deliberately NOT silently overwritten. The R67 tool
requires the actually observed compiler blob, chains R66's eight-anchor
recipe, and inserts the two R67 emission-site anchors. Unknown input fails
closed. Reconcile the discrepancy before accepting/integrating the new source.

## Reviewer entry point

Read `docs/R67-SOURCE-REVIEW.md` on this branch first.

```sh
python3 -m unittest discover -s tests/r66 -p 'test_*.py' -v
python3 -m unittest discover -s tests/r67 -p 'test_*.py' -v
python3 tools/r67_prepare_compiler.py --source src/sutram_compiler.asm \
  --output /tmp/sutram-r67.asm --patch-output /tmp/sutram-r67.patch
nasm -f elf64 -I. /tmp/sutram-r67.asm -o /tmp/r67.o
ld -o /tmp/r67-default /tmp/r67.o
python3 tools/r67_native_acceptance.py --compiler /tmp/r67-default --suite
```

Use fresh outputs. Build and test default, inherited R65 peephole/trap/combined
modes, then the optional pure-pair mode documented in the review. Supply an
independent accepted default compiler via `--reference` and the explicit pair
compiler via `--pair-compiler` for A/B. Run full accepted suite/codegen/packs/
graph/proofs/frozen baselines with the actual intended compiler. Existing
NO-EXPECTATION entries must be reported, not hidden or called passes.

Build GUI through `windows/gui/build-gui.ps1` in a normal Windows session;
verify cluster title updates and open/close/menu/rendering with the manual
checklist. This counter does not change RichEdit text, selection or advances.
The packaging wrapper now rebuilds the GUI before the native installer uses it.
Do not elevate, bypass policy, or claim package-format tests prove GUI acceptance.

## Actual verification

**53 local tests PASS:** 26 isolated assembly-helper methods via GNU as/GCC on
Linux (Win64 ABI bridge for cluster calls) and 27 source/pack/anchor methods.
Final rerun: inherited 33 tests in 0.193s, new 20 in 0.061s, both OK. Five
Python files passed syntax checks. All 25 uploaded Git blobs matched the local
source, and the complete SHA-256 manifest covers all 25 files (74618 bytes).
The exhaustive 65,536 digit-byte combinations are inside one test method.

**NOT RUN:** whole production-source preparation, NASM compiler/GUI builds,
generated Sutram programs, native A/B/identity/instruction counts, full suite,
PowerShell or Windows GUI/installer acceptance. The new example outputs are
expected fixtures, not claimed observed runtime outputs. Full Gujarati suite
green is specifically still a required gate.

Handoff/evidence/checksums/review index are on main in `ChatGPT-to-Sarvam/`.
The complete source is the pinned PR commit; the supplement is not a full
checkout or Windows installer. No `lib/*.smlib`, accepted golden, original GUI
palette/icon, workflow trigger, credential or application networking changed.
