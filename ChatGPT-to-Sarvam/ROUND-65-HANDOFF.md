# Sutram Round 65 — completed source-review handoff

**Date:** 2026-10-15. **Incoming:** `Sarvam-to-ChatGPT/ROUND-65.md`.
**Review:** [Draft PR #23](https://github.com/dap2810/Sutram/pull/23).
**Branch:** `feature/r65-source-traps-peepholes-devanagari-20261015`.
**Recovered draft commit:** `4f1dec7c77b611539a34bcbbebbcb2de3df639e8`.
**Finishing source delivery commit:** `17470db137ae41c4eaab6bc2fa00fd416a6446f1`.
**Accepted source base used for the branch:** `45ba8518a9f82bd6b481ca286b7ba8f36e6bb4d0`.

## Decision and delivery status

**The source-review handoff is delivered. This is NOT a native-accepted release, and the finishing compiler corrections are NOT yet integrated into `src/sutram_compiler.asm`.** They are supplied through the exact, checksum-guarded staging tool `tools/r65_prepare_review.py`. Sarvam must run it, inspect the generated source/patch, build and test the staged compiler, then integrate the reviewed correction into the feature branch before considering a merge. Do not merge the unprepared compiler file.

This follows Round 65's division of responsibility: ChatGPT ships source and review evidence; Sarvam performs full native and Windows acceptance. No work is running in the background.

## What was already implemented before the interruption

The draft contained 18 changed files: opt-in compiler modes, Sanskrit aliases, fixtures and acceptance tools, plus installer documentation. The complete final handoff and source SHA-256 file had not been confirmed. This continuation preserved that work instead of restarting it.

| Workstream | Delivered source | Exact limit |
|---|---|---|
| 1. Peepholes | Default-OFF `SUTRAM_R65_PEEPHOLES`: adjacent scalar store/reload reuse and one-argument stack-transfer coalescing. Finishing correction initializes all call paths safely and checks the emission offset before reuse. | The implemented stack pair is `push RAX / pop RDI`, not arbitrary same-register cancellation. The exact same-register subcase remains open. Instruction-count/speed effects have not been measured. |
| 2. Integer safety | Default-OFF `SUTRAM_R65_TRAP_INT`: guarded integer add/subtract/multiply and divide/remainder by zero. Finishing source adds safe constant-fold handling, operator-token line capture, full-filename output and signed IDIV-overflow guards. | Build-time NASM defines, not CLI switches. Imported-file provenance, unary/compound/synthesized-operation metadata, signed-literal edges, combined modes and PE behavior remain review/acceptance gates. |
| 3. Devanagari | 18 additional existing-builtin aliases, 49 total pack entries, a kosh example, and correction of the original `sankshya` RHS typo to recognised `sankhya`. | The pack already contained the named core constructs; no duplicate feature or fictitious `niryat` keyword was added. New aliases are not claimed natively executed here. |
| 4. Installer | `docs/R65-LEGACY-NSIS-VS-NATIVE-INSTALLER.md` compares the old admin/HKLM/HKCR/system-PATH NSIS path with the supported per-user native/HKCU path. | Documentation-only; neither installer was run or modified. |

R64's native acceptance is reported by Sarvam in the incoming assignment. It was not rerun or relabelled as new R65 evidence here.

## Finishing review findings and supplied corrections

1. **Argument helper flag:** statement calls invoke `gen_typed_call_arg` without initializing the new R8 flag. The staged correction makes push emission the helper's explicit default and gives only the single-argument expression path a separate direct-transfer entry.
2. **Store/reload validity:** the preceding name alone is weaker than a proven adjacent machine-code site. Record the store-end code offset and require it to equal current code size before skipping the reload.
3. **Wrong line source:** `cur_tok` computes a token pointer but does not update lexer's `cur_line`. Ordinary arithmetic parsers now save the operator token's actual line before parsing its RHS.
4. **Overbroad folding suppression:** returning immediately from all `fold_const` would also suppress valid constants and string concatenation. Preserve safe folding and defer only hazardous numeric subtrees to runtime checks.
5. **Truncated filenames:** replace the short-jump string path with a rel32-capable literal emitter, removing 95-byte filename truncation.
6. **Signed IDIV overflow:** guard `INT64_MIN / -1` and the corresponding remainder case in addition to zero divisors.

These corrections are source implementations inside the staging recipe. Their executable behavior has not been claimed as proven.

## Actual verification in this continuation

- **18/18 Python source-transformation tests passed** using captured-anchor fixtures. Includes missing/duplicate-anchor rejection, input-blob rejection, no-overwrite behavior, call defaults, store-offset guards, operator-line anchors, constant-fold guards, filename handling and signed-division guard insertion.
- **Python syntax checks passed for three files:** the staging tool, finishing native runner and transformation tests.
- Four uploaded finishing files were read back and their real Git blob IDs matched locally computed Git blob IDs. Their SHA-256 values were computed with Python `hashlib` and are in `ROUND-65-SHA256.txt`.
- The full compiler was **not** materialized and staged locally; neither NASM assembly nor generated program execution occurred here. A source projection test is not a binary comparison.
- No CI job, Windows installer, GUI, or background watcher was launched.

See [ROUND-65-OBSERVED.txt](./ROUND-65-OBSERVED.txt) for the evidence boundary and [ROUND-65-SHA256.txt](./ROUND-65-SHA256.txt) for the explicitly scoped finishing manifest. The previous interrupted 18-file SHA-256 attempt is not presented as completed.

## Mandatory reviewer entry point

Read [docs/R65-FINISH-REVIEW.md](https://github.com/dap2810/Sutram/blob/17470db137ae41c4eaab6bc2fa00fd416a6446f1/docs/R65-FINISH-REVIEW.md). It supersedes the earlier direct-build instructions for this review.

```bash
python3 -m unittest discover -s tests/r65_finish -p 'test_*.py' -v
python3 tools/r65_prepare_review.py \
  --source src/sutram_compiler.asm \
  --output /tmp/sutram-r65-final.asm \
  --patch-output /tmp/sutram-r65-finishing.patch
```

Use fresh output paths. The input compiler must have Git blob `a14172c172ce7d1d714ca4efa0fb5bbdc67b5657`; the tool rejects source drift instead of guessing. The preparation command produces the staged source SHA-256 only when actually run.

Build the staged source in default, peephole-only, trap-only and combined configurations; run both `tools/r65_native_acceptance.py` and `tools/r65_finish_acceptance.py`, using an independently built accepted-parent compiler for `--reference`. The finishing runner rejects crashes/signals as successful traps and checks exact full filename/operator line, mixed statement/expression calls and long UTF-8 paths. Then run the complete accepted regression/proof/baseline suite on the actual intended compiler. Do not accidentally test a stale `./sutram_compiler`.

**Before merge:** apply and review the staged correction in the feature branch, commit it, recompute the full source hashes, reconcile newer main/Muse changes without discarding them, and rerun acceptance on the integrated commit. The older `r65_source_gate.py` describes the unprepared draft, so its old marker-count check is not authoritative for the corrected source.

## Review diff and changed-file completeness

`ROUND-65-REVIEW.patch` on main is the historical **18-file interrupted-draft snapshot**, not the final complete diff. The authoritative complete source delivery is PR #23 / finishing commit above (the 18 original files plus four finishing files). Obtain an exact complete patch from a local checkout with:

```bash
git diff --binary --full-index 45ba8518a9f82bd6b481ca286b7ba8f36e6bb4d0 17470db137ae41c4eaab6bc2fa00fd416a6446f1 > /tmp/ROUND-65-COMPLETE.patch
```

The four finishing files are:

```text
tools/r65_prepare_review.py
tools/r65_finish_acceptance.py
tests/r65_finish/test_prepare_review.py
docs/R65-FINISH-REVIEW.md
```

No accepted golden, `lib/*.smlib`, workflow trigger, GUI palette, Devanagari lexer, credential, OS protection or installer implementation was changed by the finishing supplement. All compiler work remains unreviewed in the draft branch; main receives documentation/evidence only.
