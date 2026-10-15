# Round 68 complete source-review index

[Draft PR #26](https://github.com/dap2810/Sutram/pull/26).
Source commit: `31b9e7c96db65c23d160e60f15864fb967910454`.
Pinned base: `a700bfd21a6af1c6d5efc275df1963585615ef67`.
All **55** changed files are included in this commit and the source supplement.

```sh
git diff --binary --full-index a700bfd21a6af1c6d5efc275df1963585615ef67 31b9e7c96db65c23d160e60f15864fb967910454 > ROUND-68-COMPLETE.patch
```

That pinned Git diff is authoritative. No partial reconstructed patch is
presented as a full repository diff. The supplement is not a full checkout or
installer. Use the complete repository and exact input pins before building
`src/r68_compiler_entry.asm`. The entry is a source wrapper, NOT an expanded
compiler or an already accepted runtime binary.

## Complete changed paths

- `INSTALL-WINDOWS.md`
- `README.md`
- `docs/INSTALLATION-ROUTES.md`
- `docs/R65-LEGACY-NSIS-VS-NATIVE-INSTALLER.md`
- `docs/R68-INDIC-DEVICES.md`
- `docs/R68-LEXICAL-DIAGNOSTICS.md`
- `docs/R68-PURE-PAIR-PROBE.md`
- `docs/R68-SOURCE-REVIEW.md`
- `docs/R68-WINDOWS-GUI-CHECKLIST.md`
- `docs/WINDOWS-SETUP.md`
- `examples/r68/hindi.exit`
- `examples/r68/hindi.out`
- `examples/r68/hindi.sm`
- `examples/r68/kannada.exit`
- `examples/r68/kannada.out`
- `examples/r68/kannada.sm`
- `examples/r68/marathi.exit`
- `examples/r68/marathi.out`
- `examples/r68/marathi.sm`
- `examples/r68/odia.exit`
- `examples/r68/odia.out`
- `examples/r68/odia.sm`
- `examples/r68/pairs/all_registers.exit`
- `examples/r68/pairs/all_registers.out`
- `examples/r68/pairs/all_registers.sm`
- `examples/r68/pairs/no_pairs.exit`
- `examples/r68/pairs/no_pairs.out`
- `examples/r68/pairs/no_pairs.sm`
- `examples/r68/pairs/nonmatching.exit`
- `examples/r68/pairs/nonmatching.out`
- `examples/r68/pairs/nonmatching.sm`
- `examples/r68/tamil.exit`
- `examples/r68/tamil.out`
- `examples/r68/tamil.sm`
- `examples/r68/telugu.exit`
- `examples/r68/telugu.out`
- `examples/r68/telugu.sm`
- `lang/hindi.lang`
- `lang/kannada.lang`
- `lang/marathi.lang`
- `lang/odia.lang`
- `lang/tamil.lang`
- `lang/telugu.lang`
- `src/r66_indic_lexer.inc`
- `src/r68_compiler_entry.asm`
- `src/r68_diagnostics.inc`
- `src/r68_unicode_helpers.inc`
- `tests/r66/test_native_helpers.py`
- `tests/r68/baseline_packs.json`
- `tests/r68/gui_title_cases.json`
- `tests/r68/test_r68.py`
- `tools/r68_native_acceptance.py`
- `tools/r68_prepare_review.py`
- `tools/r68_review.lock.json`
- `windows/WINDOWS-README.md`

The main handoff folder holds instructions, observed evidence and checksums.
Implementation remains on the draft branch for independent acceptance.
