# Round 66 — complete review source and patch index

Source commit: `b406802dc7d155f0ea6a0c72e17d08e6ce90ba8e`. Accepted parent: `9921cbf175b2fb7983e45305fdec963380532452`.
[Draft PR #24](https://github.com/dap2810/Sutram/pull/24) contains all **16** changed source/test/doc files.
The checked-out compiler itself is unchanged; prepare the lexical integration separately as described in `ROUND-66-HANDOFF.md`.

## Obtain the complete Git patch from the repository

```sh
git diff --binary --full-index 9921cbf175b2fb7983e45305fdec963380532452 b406802dc7d155f0ea6a0c72e17d08e6ce90ba8e > /tmp/ROUND-66-GIT-REVIEW.patch
```

The companion source supplement also contains `ChatGPT-to-Sarvam/ROUND-66-REVIEW.patch`, a full 16-file unified review diff generated locally from the exact touched baseline files. It passed `git apply --check`, actual application in a temporary touched-path reconstruction, and resulting-file byte comparisons.

Local review patch: **68,296 bytes**, SHA-256:
`f3a8b50c28bf7562467d56b4fdbb3d2b5e98b1bc13373733bfdb8ff53035aa52`.

The command above can emit different Git metadata/index headers, so its patch-file hash is not expected to equal the local unified patch hash. Both describe the same pinned source changes. Do not confuse either with `/tmp/sutram-r66.patch`, the compiler-only integration patch that the staging tool generates when it is actually run.

## Complete source-file list

- `docs/R65-LEGACY-NSIS-VS-NATIVE-INSTALLER.md`
- `docs/R66-INDIC-DEVICES.md`
- `docs/R66-SOURCE-REVIEW.md`
- `docs/R66-WINDOWS-SHAPING.md`
- `examples/r66/gujarati_native.sm`
- `examples/r66/native_digits.sm`
- `examples/r66/sanskrit_native.sm`
- `lang/gujarati.lang`
- `lang/sanskrit.lang`
- `src/r66_indic_lexer.inc`
- `tests/r66/baseline_packs.json`
- `tests/r66/test_native_helpers.py`
- `tests/r66/test_prepare_review.py`
- `tools/r66_native_acceptance.py`
- `tools/r66_prepare_review.py`
- `windows/gui/r66_indic_clusters.asm`

The handoff, observed test log and full source checksum manifest are on main in `ChatGPT-to-Sarvam/`. Source code remains unreviewed in the draft branch. All complete source files are accessible from the pinned commit; no missing background upload is implied.
