# Sutram Round 70 — ChatGPT to Sarvam handoff

Delivery/check date: **2026-10-15**. The incoming Round 70 heading is dated
2026-10-16; that is its supplied date, not the date of this execution.
Latest assignment read: `Sarvam-to-ChatGPT/ROUND-70.md`.
Review: [draft PR #28](https://github.com/dap2810/Sutram/pull/28).
Branch: `feature/r70-spec-memory-negative-corpus-20261015`.
Source commit: `61e7507b44f2687f3b7ff20f9acb5ef29df85db2`.
Pinned base: `dde0613ca16f3e41345b1b1055733151780ef9d7`.

**Source/documentation delivery, not a native-accepted compiler release.**
All 13 additive files are uploaded and their identities match the local files.
This work follows Round 70 rather than restarting the older Round 69 brief.
The separate clean-project PR #27 is not merged or modified by this round.
Newer main changes must be reconciled at review, not discarded.

## Four workstreams

| Workstream | Delivered | Exact remaining limit |
|---|---|---|
| WS1 specification | `docs/SPECIFICATION.md`: source/golden-grounded semantics, precedence inventory, order, integers/floats, strings, keywords and packs. Evidence-backed, source-observed, documented and unspecified rules are distinct. | Not a complete formal language specification. Untested associativity, ordinary side-effect order, conversion and pack-resolution cases remain unspecified. |
| WS2 negatives | Six categories in `tests/negative/r70/`, a pinned manifest, `tools/r70_negative_corpus.py`, unit tests and `docs/NEGATIVE-CORPUS.md`. Two cases copy existing source/golden identities; four expectations are new. | The actual six-case native run has NOT occurred here. Thirty-six Python harness tests are not thirty-six compiled Sutram tests. Full native acceptance is still required. |
| WS3 memory | `docs/MEMORY-MODEL.md`: current allocation/alias/reclamation observations, then an explicitly PROPOSED ownership design. | No ownership/borrow checker or runtime memory-safety feature implemented. No leak measurement or full allocator audit claimed. |
| WS4 freestanding | `docs/FREESTANDING.md`: concrete entry/startup/sections/relocation/volatile/atomic/interrupt/OS-dependency/output/repeatability gaps. | No boot image, kernel, emulator run or freestanding-readiness claim. |

The pinned charter has **20** items while the brief refers to an older 19-item
numbering. The documents preserve the charter's heading meanings and identify
the mismatch, without editing the charter or inventing new current semantics.

## Input and output source identities

Inherited compiler input AND unchanged branch output:
`64ea028a5ccf56117c132a7efd0673cbe2df3fc6` (545722 bytes).
Inherited R68 diagnostic entry remains:
`42389aaf73179726d91e23359aee2199734036e1` (713 bytes).

No staged replacement compiler and no compiler executable were produced. The
new output is documentation/corpus/runner source; its complete hashes are in
`ROUND-70-SHA256.txt`. Native mode verifies seven input Git blobs, records the
chosen binary hash and refuses unknown source drift. A source pin and binary
hash are not themselves proof that a binary was built from those sources.

## Important findings retained in the documents

- The existing short-circuit fixture pins conditional RHS effects, not every
  possible argument/operand evaluation order.
- `char_code("AZ",1)` has a concrete `90` golden, despite the older reference's
  claim that the index is ignored. This says nothing about grapheme indexing.
- The inspected kosh growth path copies to a new buffer without a matching old
  buffer reclaim in that path. Bounds checking is not ownership or lifetime safety.
- The negative unknown-identifier case is an undefined FUNCTION. The malformed
  literal is invalid digit-shaped UTF-8, not proof of all numeric grammar errors.
- The unterminated-string case also consumes intended delimiters; its expectation
  is for that exact invalid program, not a universal new lexical guarantee.

## Native reviewer entry point

Read all four documents, especially `docs/NEGATIVE-CORPUS.md`. In a complete
checkout matching the pinned source profile, using an existing Linux toolchain:

```sh
python3 -m unittest discover -s tests/r70 -p 'test_*.py' -v
python3 tools/r70_negative_corpus.py --validate-only
nasm -f elf64 -I. src/r68_compiler_entry.asm -o /tmp/r70-corpus.o
ld -o /tmp/r70-corpus-compiler /tmp/r70-corpus.o
python3 tools/r70_negative_corpus.py --compiler /tmp/r70-corpus-compiler \
  --report /tmp/r70-native-negative-report.json
```

Use fresh output/report paths. The six-category run must succeed before WS2 is
native-accepted. Successful default/Sanskrit positive controls are mandatory;
negative programs require exit 1, their expected diagnostic and no output path.
A crash, timeout, generic compiler failure, stale artifact or dangling symlink
fails. Unexpectedly accepted negative executables are never run. Existing
SUTRAM_* environment settings are removed from these child processes.

The four exact-message cases and two ordered-fragment cases are explicitly
labelled in the manifest. Do not weaken failures into xfails or auto-record new
goldens from a broken compiler. If a new expected rejection is not implemented,
report the actual result and review a minimal source fix separately. After the
new corpus, run the accepted suite/proofs/packs/codegen against the intended
compiler without rewriting accepted expectations.

## Actual evidence

**36 local Python unit tests passed** (final run: 0.061s, Python 3.13.5).
Native process outcomes in these tests are MOCKED. `--validate-only` validated
six categories/fixture hashes and explicitly returned `native_status: NOT_RUN`.
Both Python files passed syntax checking. The two inherited case-source copies
and their diagnostic bytes matched the actual source/golden Git blob identities.

All 13 local Git blob IDs reproduced the uploaded complete tree
`4266c599b1a62237c8468826a54926c4d33dd3f5` exactly. The source manifest covers
13/13 files, 76500 bytes. This is content-identity verification, not a native run.

**Not run:** the six-case native corpus, full compiler build/execution or full
regressions, memory leak measurement, kernel/boot proof, Windows GUI or installer.
No existing compiler, library, golden, palette/icon or workflow was changed;
no automatic CI, background monitoring, runtime network feature, credentials,
elevation or registry operation was introduced. Keep PR #28 draft until reviewed.
