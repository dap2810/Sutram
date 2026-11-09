# ROUND-226 follow-up 2 — R166 closure and evidence-verifier limits

9 November 2026. Reviewed main **a2268abd0cd6d01fe13c14c021a116aa20acf968**, the cross-partner update in Sarvam-to-ChatGPT/, Claude R164-02 and R166-00, and the changed privacy/normalization/verifier source.
Documentation-only return. **Runtime checks: NOT RUN — read-side role, no toolchain used.**

## Verified progress

The earlier failures to stop on unreadable input, invalid proposed JSON and duplicate keys have been addressed in source. The normalizer validates before the write loop, requires a record for --apply, and makes key changes explicit. R159 now inspects UTF-16 text, Unicode escapes, filenames, additional address/hardware forms and unreadable tracked files.

Claude's expanded scan found **36 previously missed files**, including **21 UTF-16 files**. Those are contributor scan results. They establish why the previous pass result was not a complete privacy guarantee; the return correctly withdraws the broader claim.

I independently read and linked the three committed normalization records:
- ChatGPT R226: 28 entries.
- Claude R164: 806 entries.
- Claude R166: 67 entries.
- **871 distinct paths** across the records.
- **No discontinuity** between successive recorded before/after digests for the same path.
- **870 current file digests match their final recorded after-digest.** PROJECT-MASTER.md differs because it was subsequently edited; a dated transformation record is not a perpetual current-tree manifest.

This is static blob hashing and JSON inspection, not execution of the project verifier or gates. No current broken normalization chain was found.

Committed setup SHA-256 independently computed:
**6f9cdbda02164cb521aa853ea920f60dd77d871eb2e70b32da3130b1ebb05018**.
This supersedes the 9011c8a5 candidate quoted in the earlier same-day cross-partner update. Compiler remains reported as v315; staged v316 is not accepted by this review.

## New verifier: useful explanation, but not yet a fail-closed integrity check

tools/verify_evidence_manifest.py addresses a real need: original evidence digests must stay historical while sanitized current bytes remain independently checkable. The privacy notes and screenshot-removal annotations are appropriate.

Three concrete source findings remain:

### 1. Unparsed entries can disappear and yield exit 0

entries() returns an empty list for invalid JSON. Unsupported JSON shapes and entries without recognized path/digest fields are silently ignored. Text lines not matching the checksum regex are also ignored. main() skips a manifest with no counts, and returns success if no recognized entry was MISMATCH/MISSING.

Consequently, a malformed or unsupported manifest can produce zero verified entries and a successful exit; a partly malformed manifest can check only the surviving recognized lines.

Fix: strict parsing with explicit manifest formats, duplicate-key detection for JSON, and a count of entries supplied versus entries verified. Invalid content, unsupported schema or a nonempty manifest with zero recognized entries must fail. Permit known blank/comment/header lines deliberately; do not classify arbitrary unparsed lines as harmless. No input manifests supplied should produce usage/error, not a verification success.

Acceptance fixtures: malformed JSON, unsupported object schema, missing digest, malformed digest, duplicate path with conflicting digests, a text manifest with one valid and one malformed entry, and an empty invocation. These are proposed fixtures, **not executed here**.

### 2. NORMALISED does not prove a connected transformation

The code accepts any recorded before-digest for a path if current bytes equal the last recorded after-digest. It does not verify that every intervening after equals the next before. Two unrelated transformations could therefore be accepted as one explanation.

Fix: follow a connected chain starting at the manifest's actual digest, validate record fields, reject ambiguous competing successors, and require the reached digest to equal the current file. COPY-KEPT should use the same connected-chain logic for the retained copy.

**The committed records examined here are contiguous.** This finding concerns the verifier's ability to reject a future broken record, not a claim that the current cleanup chain is broken.

### 3. REMOVED currently validates only a pathname

load_records() reduces screenshots-removed.tsv to a set of paths, discarding the recorded digest. Any manifest digest associated with that missing path receives REMOVED, even if it never described the removed image.

Fix: retain the removed digest and require a match or a connected, recorded image-redaction transition from the historical digest to the removed bytes. The screenshot-record.json is relevant for images changed before deletion. Preserve the distinction between “this pathname was removed under policy” and “this checksum is explained by recorded removal.”

A deliberately wrong digest for a removed screenshot must not receive integrity success. This correction must not restore screenshots or link readers to identifying historical images.

### Path resolution also needs an explicit convention

resolve() tries a manifest-relative existing path, then a repository-relative existing path, and tests containment with a string prefix. Missing entries fall back to the first base without the same validation. This makes interpretation depend on which files happen to exist.

Use a documented base for each manifest format, structural repository containment checks, and the same rule for present and missing entries. A look-alike prefix is not directory containment. Fail on ambiguous path interpretation rather than selecting a different file because it exists.

## Normalizer: closure is validation, not an all-or-nothing transaction

The new normalizer's pre-write validation resolves the main R226 finding. Its record is written before data edits, which improves recovery evidence. However, a failure during the later sequence of file writes can leave a partial application and a record listing all planned transformations. The final read-back loop only runs after every write returns.

Keep the record's intended after-digests, but describe partial application honestly and identify which files match before, after or neither on recovery. Do not call this a transactional all-or-nothing filesystem update.

One compatibility detail for the owner to address: JSON validation receives original encoded bytes while strict_json decodes UTF-8 only. A UTF-16 JSON file that requires normalization will therefore refuse rather than normalize successfully; this is conservative refusal, not silent corruption. Pass the already decoded text forms to JSON validation, then preserve/verify the original encoding on write-back. The present UTF-16 work primarily covered logs/transcripts/registry exports, so this is not evidence that those edits failed.

## Memory and release status

R166's book corrections distinguish the actual allocation kinds:
- Scratch nirmmita lexically within the block is reclaimed on its exits.
- Kosh backing storage is retained under the current model.
- Mala storage is not reclaimed by mandapa merely because its declaration occurs there.
- A block around a caller does not convert a callee's persistent allocation into scratch.
- Budget accounting includes alignment.

The return attaches programs and contributor results, including agrim and aligned-budget cases. These corrections strengthen teaching accuracy; they do not implement the proposed owner/handle ABI or establish general reclamation of live collections.

The cross-partner update asks contributors to run R159 before publication. I remain in the owner's established read-side role: **no project gates or toolchain execution were run**, and no run is implied. This return contains neutral placeholders and no personal system details.

Claude reports gates 80 PASS / 0 FAIL / 1 NOT-RUN, suite 327 PASS plus four without expectations. Final native installer acceptance remains pending. Current-tree cleanup, historical-object cleanup and outside copies remain separate claims; no history purge was performed here.
