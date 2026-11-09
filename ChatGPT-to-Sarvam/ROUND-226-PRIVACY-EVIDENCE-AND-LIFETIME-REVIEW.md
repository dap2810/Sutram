# ROUND-226 — privacy normalization, evidence integrity and memory lifetime

9 November 2026. Reviewed the Round 226 brief and privacy standing instruction at main 8bb4219, plus the R163 source/documentation changes. Own normalization commits end at ed92f4b; the companion provenance manifest records the changed files.
**Own runtime checks: NOT RUN — read-side role, no toolchain used.**

## Delivered

Normalized **28 existing files in ChatGPT-to-Sarvam/**, including three JSON evidence files. No source, test, tool, binary or Windows-to-Sarvam file was changed. JSON key structure and embedded 64-hex compiler/package digests were preserved; all 28 exact returned commits were fetched and compared against the intended complete text.

[ROUND-226-PRIVACY-NORMALIZATION.json](ROUND-226-PRIVACY-NORMALIZATION.json) records each changed path and before/after SHA-256. These are sanitized historical records, not freshly executed results. The manifest contains no original personal strings.

## WS1 — memory measurements describe different lifetimes

The design does not change. It targets **repeated owner lifetimes whose temporary collections die at each exit**, including a block inside each loop iteration or a block entered by each function call. It does not reclaim still-live allocations merely because another iteration began.

| Pattern | Reclamation opportunity |
|---|---|
| One block surrounding the whole allocating loop | At the end of the whole loop |
| Block inside each iteration | At each iteration's block exit |
| Function called repeatedly, with its temporary allocation inside a block | At each call's block exit/return |
| Sequential batches, each with its own block | At each batch exit |
| Outer kosh intentionally accumulating results | Its contents remain live across inner exits |

A suitable teaching sentence is: “Put the block around the temporary work that finishes each time. Wrapping one block around the entire loop keeps all its allocations live until that loop finishes.”

“Returns memory” needs precision: current scratch rewind makes arena space reusable. It does not itself promise the same number of resident pages returned to the operating system. Peak RSS, logical allocation accounting and reserved virtual memory measure different things.

### New evidence already on main

Claude-to-Sarvam/evidence-r163/peak-memory.txt includes both complete source programs. In the block version, kaam(i) enters mandapa, allocates 256 bytes, touches the buffer, returns a scalar and exits the block; main calls it 200,000 times. The other version removes the block. Thus it is repeated block lifetimes, not Sarvam's single enclosing block.

That contributor log shows:
- five initial runs each: block peak 308 KB; no-block peak 49,920 KB;
- another fifty each: block 308 KB fourteen times and 436 KB thirty-six times; no-block 49,920 KB fifty times.

These are contributor measurements read from the log, not my runs. The current book already uses 308/436 versus 49,920 and explains capacity. Its sentence “in 75 runs” is not fully supported by this particular log, which exposes **55 per variant**. Supply the missing twenty runs or qualify the count to the evidence actually attached. The old fixed 392 KB statement is superseded by this new record; disagreement between different programs did not by itself disprove the old measurement.

Sarvam's four numbers in the brief are insufficient to identify why the one-block version was 580 KB higher. Exact programs, generated artifact identities, touch patterns, measurement method and repeated paired runs are needed. Possible contributors include different page touching/zeroing and measurement variation; I do not assign the difference to any one of them. A scratch allocator may zero reused storage that an otherwise sparsely touched persistent allocation did not touch, so overhead is plausible. That is an explanation to test, not a measured cause.

Alternate the two program variants, report their distributions with identical useful work/output, and separate compilation from execution. Do not infer a stable per-block bookkeeping cost from one difference. No demand to rerun unrelated suites is implied.

## WS2 — the concrete design was delivered in R225

[ROUND-225-HANDLE-DESIGN-OUTPUT-IDENTITY-AND-LOCK-GAP.md](ROUND-225-HANDLE-DESIGN-OUTPUT-IDENTITY-AND-LOCK-GAP.md), commit 2aa15fe, already supplies the representation, allocation policy, cleanup algorithm, costs and acceptance cases. It is a design, not an implementation or an accepted ABI.

Its essential decisions:
- Owner selected at kosh creation; growth always charges that owner, even inside another scope.
- One-word generational handles shared by aliases; reusable, stable metadata slots resolve to the current elements.
- 64-byte slots, lazy metadata pages, small chunks shared per owner, and separately sized large mappings. No fixed 64 MiB mapping for each small kosh.
- On owner exit invalidate slots, release its large mappings/chunks, then reuse slots with new generations; never wrap into a stale generation.
- Per-access cost includes handle decoding, page lookup/validation and generation validation in addition to element bounds. An owner pointer does not eliminate those checks.
- The explicit prototype handle split caps simultaneous handles; this is a proposed new limit and ABI tradeoff, not a hidden constraint on current Sutram. Twenty million elements are independently supported subject to memory and safe growth.
- Build a separate prototype after the current native candidate work. Close the proposal if unchanged raw descriptor ABI and no extra dynamic checks are also absolute requirements.

“No runtime” must mean no external runtime dependency, not no emitted allocator/check instructions. No GC or new static borrow checker is required; raw/foreign retained pointers remain outside the checked guarantee unless an explicit persistent-copy/pinning contract is added.

The lifetime measurements reinforce that design's intended workload. They do not justify arbitrary persistent-cursor rewind or freeing a growing outer collection. A long-lived root owner can still accumulate memory; this is not general reclamation inside every live scope.

## WS3 — normalization plan: preserve evidence without preserving identity

The brief's counts were not a complete inventory. My targeted home/repository-prefix scan found six files in my channel; adding absolute path examples, build numbers and hardware details raised my cleanup to 28. Text scans are scoped evidence, not a claim that all images, archives, binaries and historical commits are clean.

### What changed in my channel

Home prefixes became %USERPROFILE%, repository roots became <repo>, generic drive examples became <drive>, scratch patch locations became <scratch>, and platform/hardware details were redacted without inventing a replacement machine or changing the historical execution date. Existing relative evidence links and filenames were retained.

Three JSON files were parsed before and after replacement. Their recursive key structure matched. Path values and system-detail prose changed; result booleans, numbers, exit statuses, timings and embedded product digests were not intentionally changed. The two OOM records' compiler_sha256 values identify compiler executables, not the JSON files themselves, so those values must remain unchanged.

A post-update scan over my channel's Markdown/JSON/text/log/CSV/TSV evidence found no remaining matches for the targeted absolute-home/workspace/drive-path and exact-build patterns. This is not a universal privacy certification. No screenshot or binary content was modified here.

### A real hash dependency found

The old full-file SHA-256 of ChatGPT-to-Sarvam/ROUND-154-RECYCLING-AND-ALIAS-EVIDENCE.md appears as a JSON **key** in Muse-to-Sarvam/r119_duplicates.json, with paths to both my report and a Claude-channel copy.

- Historical digest: 114069f396e2bf801e896f496f26546cf700cb81edd8b17a77c480f494b4029d
- Sanitized report digest: 65198edbbd7909c41ef55eab47f99f6a0d94f6241086a9f28b7c83195d342052

The historical duplicate grouping no longer proves equality against my current bytes. It remains a historical inventory and must not silently be treated as a current deletion manifest. I have not rewritten Muse's inventory or Claude's copy. Its owner should date/pin the historical inventory explicitly and generate a separate current inventory if needed, or normalize both copies and record the new relationship. The companion manifest here records the transition.

A tracked-tree search for all 28 original full-file SHA-256 strings found this one referencing file. That is a bounded exact-digest search, not proof that no external archive, signed record, truncated digest or dynamically generated manifest depends on these files.

### Wider replacement hazards and required handling

| Location | Risk | Correct treatment |
|---|---|---|
| JSON string value | Incorrect backslash escaping; accidental alteration of command output | Parse before/after, replace decoded strings or narrowly verified serialized spans, preserve non-sensitive results |
| JSON key | Two distinct absolute keys may collapse to one placeholder and silently lose an entry | Detect collisions before serialization; use distinct neutral root labels or a record list |
| Hash of edited evidence | Old digest no longer verifies sanitized bytes | Record old/new digests and transformation; update only current integrity manifests with a declared new evidence version |
| Hash of a binary mentioned by edited evidence | Hash still describes unchanged binary | Preserve it; do not rehash the JSON and substitute that value |
| Hash preimage stored as a command/string | Sanitization changes the reconstructible preimage | Label digest as historical or create a separate sanitized-preimage digest; never claim both are byte-identical |
| Historical transcript | Normalized command was not literally executed in that form | Label as normalized historical transcript; retain outcomes and provenance |
| Executable command/script | %USERPROFILE% is not universal shell syntax; <repo> is a placeholder | Keep transcript placeholders distinct from runnable instructions; actual scripts resolve environment/repository roots in their own language |
| Filename/link | Renaming can break reports, manifests and scripts | Inventory every reference and rename/update together; preserve neutral relative names when possible |
| Signed artifact or packaged payload | Any content edit can invalidate signature or payload hash | Do not edit executable/archive bytes blindly; rebuild/re-sign through the product owner if required |
| Screenshots/embedded metadata | Text scan does not inspect visible paths or metadata | Review separately and retain an explicitly sanitized derivative with new hash |
| Multiple source roots/users | Normalization can create false equality claims | Use stable neutral labels for distinct roles when that distinction matters |

CRLF/LF and Unicode normalization also affect digests. Hash the exact committed bytes, not a text-mode reserialization unless the reserialization is part of the declared transformation.

### Other owners need follow-up

Examples identified for the owning partners, without copying sensitive strings:
- Windows-to-Sarvam/win-installer-diag-2026-11-06/HANG.md, left-behind.md, path-scopes.json and COMMANDS.md are linked from my normalized diagnostic. Claude now owns the Windows cleanup per Round 165; I did not edit that channel.
- Muse-to-Sarvam/ROUND-132-INSTALLER-READ.md and ROUND-156-REST-OF-CHAPTER-FIGURES-OVERWRITE.md, plus older helper/evidence files, matched path patterns.
- Claude-to-Sarvam/04-REAL-PROGRAM.md and numerous evidence logs matched home/build-root patterns. The brief's “none in Claude's” does not hold for the wider home-path scan.
- Sarvam-to-ChatGPT/ROUND-226.md and corresponding partner briefs repeat original identifiers in the cleanup instructions. Normalize the instructions too; do not reproduce the exposure while describing its removal.
- Claude-to-Sarvam/evidence-r163/peak-memory.txt contains exact host details that should be normalized under the standing rule while preserving measured values.

A whole-tree gate must cover all tracked relevant text, decoded JSON, encoded path variants and filenames rather than only the two originally reported spellings or only Markdown/JSON. Negative fixtures should be synthetic and nonidentifying; distinguish policy violations from literal regex syntax, URLs and legitimate relative paths.

### History limit

These changes sanitize current file contents. Ordinary full clones still download history containing previous versions. Even a clean working tree does not mean the clone contains no old identifiers. No history rewrite was performed or authorized here. Removing repository history would also not retract copies already obtained elsewhere; do not claim the exposure has been undone.

## Installer follow-up

The R163 Open-SutramLock changes address both R225 findings in source: occupied paths are refused, the read/close/delete stale-lock path is gone, and marker-write failure disposes the newly created stream. Both installer engines carry the change. This is source closure of the identified loss/race path, not proof of native behavior.

Minor diagnostic limitation: failure to open a probe also occurs for access denial or a directory, not just a held installer lock. “Another installer is working” is therefore an inference, not certain diagnosis. This does not reopen the preservation defect; the occupied path is still left in place.

Independently hashed current committed setup:
**36c3b5cc256e02becb76430c5a8da8cc721e051a4ff2e942d72d40c64b85f3ce**.
The Round 226 brief's 84e36b59 candidate is superseded. Use the actual final packaged hash for native acceptance.

No compiler, suite, gate, PowerShell, Wine, installer or native test was run in this review. Hashing, text/JSON inspection and exact published-content comparisons were performed. The compiler self-overwrite work remains assigned for the agreed post-native-run sequence.
