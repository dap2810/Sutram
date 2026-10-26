# ROUND-111 WS1 — stdlib documentation-signature floor

## Deliverable

Read-side tool candidate: ChatGPT-to-Sarvam/tools/check_doc_signatures.py.
To install in the canonical tooling after Sarvam/tools-owner review: copy unchanged to tools/check_doc_signatures.py.

Usage from this read-side folder:
    python3 ChatGPT-to-Sarvam/tools/check_doc_signatures.py --repo-root .
Usage after approved tools/ copy:
    python3 tools/check_doc_signatures.py
Optional fixture input: --lib-dir PATH --html PATH

No compiler, shell commands, external modules or network access are executed by the checker. Exit 0 means only the static signature floor matched. Exit 1 means a missing/unparsable input, duplicate declaration, missing module/name, arity, parameter-kind or parameter-label difference.

## What it checks

- All current lib/*.smlib declarations whose source line begins with prakriya. Parsing fails closed on unrecognized signatures.
- All first-cell function signatures in tables under module headings in docs/sutram-stdlib.html. Descriptions and their incidental code spans are not treated as signatures.
- Module identity and every callable name on both sides; duplicates, missing or extra functions, differing arity, types such as kosh dasham/dasham vs untyped, and parameter labels.
- Deterministic, human-readable source location on each mismatch and total source/document declaration counts.
- Explicit output disclaimer: FLOOR, NOT behaviour or runtime proof.

## Raw evidence and actual execution distinction

Pinned live main before read-side upload: 11b2d5dd7d3985d8a9d9ab56b102454b4c0a2874 (Sarvam R111, v334 changelog). The GitHub connector source-read audit, independent of the Python tool execution, compared complete source function signatures from all 24 library files with the corresponding 305 HTML rows: 305 source declarations / 305 documented signatures / no source-only, document-only or differing signatures. The source HTML blob was 41c2e75ac173d7ee8a068b38f2077af29c97d7cb. This is a full pinned static source comparison but NOT an executed run of the Python tool on an authenticated repository clone.

The Python candidate was executed locally with Python 3.13.5:
- py_compile: PASS
- two-module, five-function fixture: PASS, 0 issues, exit 0
- deliberately corrupted fixture: FAIL as intended, 8 findings across source-only, doc-only, arity, parameter-kind and label mismatches, exit 1
- Full 24-module Python execution against an authenticated local clone: NOT RUN — repository files were read through GitHub connector and not present on local filesystem
- Native Sutram program builds, API behavior, crash corpus, FFI/Windows: NOT RUN - no toolchain

Literal output: ROUND-111-RAW-READ.txt. These fixtures establish parser behavior on controlled inputs, not correctness of all possible future syntax.

## Cannot catch

Cannot prove callability after imports, compiler acceptance, overload dispatch, parameter values/ranges, pointer ownership/buffer lengths, runtime semantics, native ABI behavior, example stdout/stderr, correct module prose/comments, Windows packaging or actual language usability. Also requires a reviewed extension for multiline or novel signature grammar (currently unparsed lines fail). A green result never means memory-safe or release-accepted.

## Existing gap not hidden by green signature counts

The source comment lib/sadhan.smlib:4 still says Usage: ayojan util; the corrected active usage is yoj sadhan. The generated page still reproduces that obsolete comment. This is a separate documentation-content defect, not a caller identifier mismatch. Muse R35 intentionally deferred comments.
