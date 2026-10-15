# Round 67 — complete source review index

Source commit: `25fe2bdbe13eb15e270a29626bb99c522691e1db`. Pinned source base: `76137658ddd8fe8f23810cd5b55deb98ac381248`.
[Draft PR #25](https://github.com/dap2810/Sutram/pull/25) contains all **25** changes.

```sh
git diff --binary --full-index 76137658ddd8fe8f23810cd5b55deb98ac381248 25fe2bdbe13eb15e270a29626bb99c522691e1db > ROUND-67-COMPLETE.patch
```

The pinned commit/PR diff is the complete authoritative patch. The companion
ZIP contains all 25 exact changed files plus handoff/evidence and is a source
supplement, not a full repository. No incomplete locally reconstructed patch
is presented as a full repository diff. The preparation tool's compiler-only
patch is a different artifact, produced only when preparation actually runs.

The same source commit preserves the accepted Gujarati example and golden,
and deliberately leaves the large compiler file unchanged pending staged
review. See the sync finding and integration steps in ROUND-67-HANDOFF.md.

## Complete file list

- `docs/R65-LEGACY-NSIS-VS-NATIVE-INSTALLER.md`
- `docs/R67-SOURCE-REVIEW.md`
- `examples/r67/bengali_native.exit`
- `examples/r67/bengali_native.out`
- `examples/r67/bengali_native.sm`
- `examples/r67/punjabi_native.exit`
- `examples/r67/punjabi_native.out`
- `examples/r67/punjabi_native.sm`
- `lang/bengali.lang`
- `lang/gujarati.lang`
- `lang/punjabi.lang`
- `src/r66_indic_lexer.inc`
- `src/r67_stack_pair.inc`
- `tests/r66/test_native_helpers.py`
- `tests/r66/test_prepare_review.py`
- `tests/r67/baseline_packs.json`
- `tests/r67/test_r67.py`
- `tools/r67_native_acceptance.py`
- `tools/r67_prepare_compiler.py`
- `windows/WINDOWS-README.md`
- `windows/build-windows-setup.ps1`
- `windows/gui/build-gui.ps1`
- `windows/gui/r66_indic_clusters.asm`
- `windows/gui/r67_cluster_count.asm`
- `windows/gui/r67_gui_entry.asm`
