# Round 221 follow-up — documentation briefs and evidence retention

Reviewed main: `0932f5537c8ed79b23fcb4001e50ebe07541ee75`.
Method: static source and handoff reads only.
Own execution: **NOT RUN — read-side role, no toolchain used.**

## Change since the R221 response

Only Muse R153 and Sarvam-to-Claude R157–159 arrived. No new product implementation or Sarvam-to-ChatGPT assignment arrived. R221's installer preservation and retry findings remain open; this note does not take over Claude's assigned book, gate, or cleanup implementation.

## Correct the memory chapter brief before copying it into both books

R157 item 5 names the wrong diagnostic for its explanation. At the reviewed base, `src/sutram_compiler.asm` defines:
- `r129_vb_hdr`, `r134_vb_hdr`, and `r127_vb_hdr`: **E_KOSH_VIBHAG**, for the kosh-slice storage/call restrictions.
- `r137_hdr`: **E_VIBHAG_ANKA**, for treating a slice as a number.

The r137 checker commentary explicitly distinguishes these cases. Teach the conservative permitted uses and the particular rejected construct, rather than suggesting the compiler waits to observe actual growth. Include separate, labelled negative examples with the expected diagnostic.

Also qualify the requested prose: mandapa reclaims its managed memory, not every external effect performed inside a block; the cited memory figures are a particular measurement, not a universal guarantee; unchanged kosh state on failed allocation does not imply recoverable execution; “no manual free” describes the language-facing interface, not absence of internal munmap/VirtualFree. These are teaching constraints, not new runtime measurements.

## Make the currency gate discriminate

R158's five checks need explicit input categories:
- Current guidance versus intentionally historical records.
- Runnable complete examples versus fragments and deliberate refusals. Negative examples must fail with the expected diagnostic; accepting all examples would invalidate this coverage.
- Compiler commands versus shell/build commands, placeholders, and deliberately invalid syntax. Do not execute arbitrary extracted documentation commands.
- Defined symbols in their declared source scope, including lib/tools where relevant, rather than a blanket src-only search.

Use known bad fixtures or controlled mutations to demonstrate rejection, and known good fixtures to demonstrate acceptance. Passing the current tree on the first run alone is neither proof of correctness nor proof of an untested gate. Version and symbol checks cannot establish semantic truth; retain source review of the narrative.

## Cleanup must retain a recoverable evidence trail

R159's statement that a hash plus a reported number is as verifiable as the full JSON is incorrect. A hash authenticates bytes that remain obtainable; it does not reconstruct the file or allow independent recalculation of its claimed result.

Before removing evidence from the working tree, record its exact immutable commit/path, SHA-256, and the report links that depend on it; verify that the original bytes remain retrievable. Keep inputs, scripts, expected results, and relevant surrounding evidence needed to interpret or reproduce the claim. Update references to the retained version. A quoted screenshot caption is not equivalent to the screenshot's corroboration.

Duplicate basenames do not prove duplicate contents. Compare bytes and dependencies before consolidating probes; preserve intentional version-specific fixtures. Resolve the conflict between “keep every cited file” and “prune raw evidence” conservatively through an explicit retention manifest. This review performs no deletion and recommends no history rewrite.

## Reconcile Muse R153 with the newer base

Muse R153 explicitly audited `308c2161`. Its “legacy shortcut LIVE” finding describes that older code. Commit `d8e5b55d759b8b7720702f3d40c57dad83c0063a`, already covered in our R221, removed the four-field adoption fallback; do not reopen it as a current source defect. Native verification remains separate.

The class-tree fix preserves extra keys/verbs, but matching current values do not record prior presence or prior values. The before-state objections in R221 still apply. Likewise, an empty OpenWithProgids value can have preexisted: empty content does not establish absence of prior state.

Muse revises its earlier twenty findings to nineteen locatable claims plus one misquote. Attribute that count to Muse; this pass does not independently certify all nineteen. Historical memory-model passages need clear historical framing rather than being silently rewritten as if they were current runtime claims.

## Remaining work

Carry forward R221's concrete registry/PATH preservation and uninstall retry-metadata issues, investigate the recorded unexplained Wine failure, and obtain the final native checks against the exact candidate artifact. Complete the English/Sanskrit chapters and documentation gate with the corrections above, then perform evidence-preserving cleanup. No new execution results or release closure are claimed here.
