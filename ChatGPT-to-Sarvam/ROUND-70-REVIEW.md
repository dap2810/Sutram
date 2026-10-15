# Round 70 — complete source review index

[Draft PR #28](https://github.com/dap2810/Sutram/pull/28).
Source commit: `61e7507b44f2687f3b7ff20f9acb5ef29df85db2`.
Pinned base: `dde0613ca16f3e41345b1b1055733151780ef9d7`.
All **13** changes are additive; the compiler and accepted goldens are unchanged.

```sh
git diff --binary --full-index dde0613ca16f3e41345b1b1055733151780ef9d7 61e7507b44f2687f3b7ff20f9acb5ef29df85db2 > ROUND-70-COMPLETE.patch
```

That pinned repository diff is authoritative. The supplement contains the exact
13 files plus handoff/checksums/local test logs; it is not a full checkout,
compiler binary or Windows installer. The existing R68 entry and its dependencies
are required for actual native corpus execution. Unknown input drift is rejected.

## Complete changed files

```text
docs/FREESTANDING.md
docs/MEMORY-MODEL.md
docs/NEGATIVE-CORPUS.md
docs/SPECIFICATION.md
tests/negative/r70/cases/bad_arity.sm
tests/negative/r70/cases/bad_type.sm
tests/negative/r70/cases/malformed_literal.sm.hex
tests/negative/r70/cases/misplaced_keyword.sm
tests/negative/r70/cases/unknown_identifier.sm
tests/negative/r70/cases/unterminated_string.sm
tests/negative/r70/manifest.json
tests/r70/test_negative_corpus.py
tools/r70_negative_corpus.py
```

The malformed file is deliberately HEX TRANSPORT of invalid source bytes, not a
Sutram hex-literal example. The runner materializes the malformed program in a
private temporary file; do not repair or Unicode-normalize it.

The separate clean-project PR #27 and newer main changes are outside this patch.
Keep them intact when integrating. Round 69 is not claimed completed by this
Round 70 document/corpus delivery. The repository-native run and final document
review remain the acceptance decision; source-only tests are not a release gate.
