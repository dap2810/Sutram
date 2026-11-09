# ROUND-226 follow-up — cleanup verification and remaining gate limits

9 November 2026. Reviewed main **d6495b1c43fc2dc9dc6f8969f96f09494ebe86fa**, revised AGENTS.md, Claude's R163 and R164/R165 returns, and their committed evidence.
Documentation-only follow-up to the completed Round 226; no new compiler task inferred from the privacy-only edit to the historical Round 157 brief.
**Runtime checks: NOT RUN — read-side role, no toolchain used.**

## What is independently verified

- Claude's normalization record contains **806 entries**. **805 after-digests match current committed bytes**. PROJECT-MASTER.md was subsequently edited and no longer matches its recorded after-digest. This is a dated transformation record, not a current-tree manifest; do not silently treat the exception as corruption or overwrite its historical digest.
- All **363 JSON files** in that normalization record parse at the reviewed commit. This checks syntax, not duplicate-key preservation.
- The current tracked PNG/JPG/JPEG inventory contains **11 files, all under icons/**. The owner-directed screenshot removal is consistent with that inventory. This is not a scan of every possible image/archive encoding.
- The committed setup's independently computed SHA-256 is **9011c8a5c3595566aedfdbbf0820029616cb19bafaa4b5961e7af77854eee153**. It supersedes 36c3b5cc and the stale 84e36b59 still printed in the Round 226 brief.
- My previous 28-file normalization remains a dated transformation; Claude additionally normalized ROUND-60-OBSERVED.txt and windows-commit-oom-2026-11-06/linux-suite.json in this channel. The latter's temporary path was outside my earlier targeted home/workspace/drive scan. My earlier bounded scan was not a complete privacy guarantee.

These checks used committed blob reads, hashing and JSON parsing only. Claude reports **80 PASS / 0 FAIL / 1 NOT-RUN** gates and 327 passing examples plus four without expectations; those are contributor results, not executions by this review.

## 1. Normalizer must refuse unsafe output before writing

In tools/normalize_personal_paths.py, a changed file enters the changed dictionary **before** JSON validation. A JSON parse error appends a warning and continues, leaving the file in that dictionary. The --apply loop later writes every changed entry and the program returns 0. Thus “reported an error” does not currently mean “prevented the invalid write.”

Changed keys are similarly reported but not rejected. Default json.loads also collapses duplicate object keys: counting keys after parsing alone cannot detect every collision introduced by mapping distinct roots to the same placeholder.

Required fix by the tool owner:
- Validate all proposed bytes before any write.
- Parse JSON with duplicate-key detection on both original and proposed objects.
- Check key mapping per object, not just one flattened list of keys.
- Abort the apply operation with a nonzero result on invalid JSON, unapproved key collisions, unreadable required input or ambiguous transformation.
- Write the normalization record as a required part of a successful transformation; do not allow the evidence changes to succeed silently without their record.
- Test a synthetic replacement that creates invalid escaping and one that maps two distinct keys to the same key. Neither test needs real identifying text.

**No current invalid JSON was found in the 363 files checked.** This is a prospective fail-open defect in the reusable tool, not a claim that the completed cleanup lost those keys.

## 2. R159's coverage is narrower than the standing policy

Source inspection of tests/r159/test_no_personal_paths.py shows:
- No general IP or MAC-address pattern, although the standing policy prohibits them.
- The drive pattern covers uppercase D through Z, without a case-insensitive flag. Other drive letters and lowercase spellings are not generally covered; the explicit C-drive exemptions are broader than the policy's “no absolute path outside the repository.”
- Hardware matching covers a few CPU spelling families, not arbitrary GPU/hardware details.
- NUL-containing files skip the path/build/account patterns and use only ASCII word matching. UTF-16 strings are not decoded, and compressed payloads are not unpacked by this gate.
- JSON is scanned as raw bytes, so Unicode-escaped representations can evade word/path patterns.
- An OSError reading a tracked file is silently skipped. The final tracked-file total can therefore overstate inspected files.
- Filename checks only apply the known-name hashes, not the full path/system-detail policy. If a filename itself contains a detected name, printing that raw filename republishes it in the gate log.

These are source-established coverage limits, not proof that the current tree contains each omitted category. Do not manufacture a residual exposure claim from a missing detector.

Required improvement: decode supported text encodings and JSON strings, cover the policy's address/hardware/path forms with synthetic controls, sanitize diagnostic filenames, and fail closed on unreadable required files. Clearly report files skipped or formats not inspected. Separate a known-identifier scan from a broader policy scan so neither is advertised as universal.

The stored hashes of short identifying words are an obfuscation mechanism, not secrecy. The return already acknowledges this. Do not reverse them or reproduce the underlying strings in a report or test fixture.

## 3. Evidence after normalization and screenshot removal

Keeping historical product hashes unchanged is correct when the referenced executable is unchanged. Keeping a historical digest of an edited log also preserves the old evidence identity, but it no longer verifies the sanitized current log.

Claude explicitly says old EVIDENCE.sha256 verification now fails for normalized files by design. Provide a clear note beside each affected manifest and a current sanitized verification manifest or a verifier that follows the normalization record. A raw checksum failure without that context is indistinguishable to a reader from accidental damage.

Keep original and sanitized identities separate; never update historical product hashes merely to make a check green. My R226 record and Claude's record can form a chain where a file was normalized more than once. The R119 duplicate inventory must likewise remain explicitly historical until regenerated against current content.

The screenshot-removal list preserves path/size/digest provenance. Reports with removed screenshot links now need a short “removed under privacy policy; textual observation retained” annotation. Do not replace those links with historical image URLs that republish the removed material. The retained text is a historical observation; it no longer supplies present visual review evidence.

The owner-directed removal takes precedence over earlier screenshot-retention expectations. No screenshot restoration is proposed.

## 4. Memory evidence now settles the pattern distinction

The R163 return explicitly corrects its earlier 75-versus-55 run-count claim and adds a separate recorded remeasurement. The R164 placement log prints complete source programs and grouped outcomes:
- One block around all allocations and its no-block control: 49,920 KB in twenty runs each.
- Sequential short blocks: 264 KB in twenty runs; their no-block control: 49,920 KB.
- Allocation in a called procedure without its own block: 49,792 KB twice and 49,920 KB eighteen times. The return table rounds this to the common value; the log retains variation.
- The chapter's procedure with a block inside it is the repeated-short-lifetime case.

These are contributor measurements. They support the updated teaching distinction: allocation lifetime follows the lexical allocation/block relationship, not merely the presence of a block somewhere on the call stack.

They do not explain the different programs underlying Sarvam's original numbers; those source programs are still needed for that comparison. Nor do they show that every RSS change is reclaimed physical memory.

The concrete owner/handle design remains in R225. No new implementation is implied by the cleanup, and no reason to reintroduce global persistent-cursor rewind emerged.

## 5. Release and history boundaries

The installer lock preservation gap remains source-fixed; native acceptance of the final packaged candidate remains NOT RUN here. Do not select an older package merely because an earlier review named its hash: test the intended final candidate and identify it explicitly.

Claude reports a staged v316 output-collision change and additional unresolved write-failure/scratch-name issues. This follow-up did not independently inspect that branch's implementation and does not approve or merge it.

Current-tree normalization and screenshot deletion **do not purge Git history**. A normal full clone downloads prior objects, and historical installers can contain compressed old documents. The reports' wording about a “fresh clone” must distinguish its checked-out files from its historical object database. No claim of complete purge, cache removal or fork cleanup is supported by this review. No history operation was performed here.

All future handoffs must preserve the standing privacy rule: use neutral placeholders, omit personal system details, and never paste offending strings into diagnostics or remediation instructions.
