# Round 65 finishing review — mandatory staging before acceptance

**Status: source-review delivery, not a native-accepted compiler.** This supplement supersedes the direct-build instructions in `R65-SOURCE-REVIEW.md` for the experimental variants. Keep PR #23 draft. Do not merge the unprepared compiler patra.

## What was recovered and what changed

The interrupted round had already placed 18 changed files in PR #23, but the final handoff and SHA-256 patra were missing. The compiler patra at that point is pinned by Git blob **a14172c172ce7d1d714ca4efa0fb5bbdc67b5657** (commit **4f1dec7c77b611539a34bcbbebbcb2de3df639e8**).

Finishing corrections are supplied as exact source transformations in `tools/r65_prepare_review.py`. They are **not silently claimed tak be integrated into `src/sutram_compiler.asm`**. The tool refuses any other input blob, missing/duplicate anchors, or a change tak its default-mode source projection. It writes a separate corrected source patra and optionally a reviewable patch; it does not edit the checkout, execute a compiler, install tools, access the network, or modify Git.

| Finding in the interrupted draft | Supplied correction |
|---|---|
| Statement calls use `gen_typed_call_arg` without initializing the new R8 push-skip flag. | Common helper explicitly defaults tak emitting a push; only the one-argument expression path uses a separate direct-transfer entry. |
| The store/reload optimization tracks the preceding variable but not the end of emitted code. | Record the store-end offset and require equality with current code size before omitting the reload. |
| `cur_line` belongs tak lexing; `cur_tok` does not update it during parsing. | For ordinary `+ - * / %`, save the operator token's line at token+24 before parsing the RHS, then store it at AST_BINOP+32. |
| Disabling all `fold_const` also disables safe constants and compile-time varna concatenation. | Retain ordinary safe folding; leave only hazardous numeric subtrees for runtime trapping. |
| The fatal message truncates the filename tak 95 bytes tak fit a short jump. | Emit strings using patched RIP-relative addresses and rel32 data-skip branches, preserving the full UTF-8 filename. |
| `INT64_MIN / -1` can still reach hardware IDIV overflow despite a nonzero divisor. | Add a distinct signed-division/remainder overflow check before IDIV, with operation-specific diagnostics. |

These are implementation and review findings. They are not observed native runtime results.

## Exact review sequence

On Sarvam's checkout of the latest PR #23 branch, use a **fresh output directory**. The preparation script requires the compiler's exact Git bytes (LF checkout, not a CRLF-transformed copy).

```bash
python3 -m unittest discover -s tests/r65_finish -p 'test_*.py' -v
python3 tools/r65_prepare_review.py \
  --source src/sutram_compiler.asm \
  --output /tmp/sutram-r65-final.asm \
  --patch-output /tmp/sutram-r65-finishing.patch
```

The script emits a real SHA-256 for the staged source only when it runs successfully. Inspect that patch. Its normalized default-source comparison is **not** a substitute for NASM preprocessing or generated-binary identity.

Build the staged source in four separate configurations from the repository root:

```bash
nasm -f elf64 -I. /tmp/sutram-r65-final.asm -o /tmp/r65-default.o
ld -o /tmp/r65-default /tmp/r65-default.o
nasm -DSUTRAM_R65_PEEPHOLES=1 -f elf64 -I. /tmp/sutram-r65-final.asm -o /tmp/r65-peephole.o
ld -o /tmp/r65-peephole /tmp/r65-peephole.o
nasm -DSUTRAM_R65_TRAP_INT=1 -f elf64 -I. /tmp/sutram-r65-final.asm -o /tmp/r65-trap.o
ld -o /tmp/r65-trap /tmp/r65-trap.o
nasm -DSUTRAM_R65_PEEPHOLES=1 -DSUTRAM_R65_TRAP_INT=1 -f elf64 -I. /tmp/sutram-r65-final.asm -o /tmp/r65-combined.o
ld -o /tmp/r65-combined /tmp/r65-combined.o
python3 tools/r65_native_acceptance.py --default /tmp/r65-default --peephole /tmp/r65-peephole --trap /tmp/r65-trap --reference /path/tak/accepted-parent-compiler
python3 tools/r65_finish_acceptance.py --default /tmp/r65-default --peephole /tmp/r65-peephole --trap /tmp/r65-trap --combined /tmp/r65-combined --reference /path/tak/accepted-parent-compiler
```

Both flags are NASM **build defines**, not CLI flags. Omit the define entirely for OFF; `%ifdef` also sees a define assigned `0` as present. The reference compiler must be independently built from the accepted pre-R65 source. Do not copy the experimental compiler into the reference path.

Then run the existing regression suite, R63/R64 acceptance, language packs, module graph, library/property proofs and the appropriate frozen codegen gates with the intended compiler. Some existing test tools implicitly use `./sutram_compiler`: point them at a deliberate test-worktree build, not a stale binary. Record exact stdout/exit codes and disassembly counts. Use the unchanged accepted goldens.

Only after independent review should Sarvam apply the staged finishing patch tak the feature branch and commit the resulting compiler source. Recompute the full source hashes, rerun the gates on that integrated commit, then decide whether tak merge. No unreviewed merge is requested.

## Remaining limits — do not hide them

* The implemented argument optimization coalesces **push RAX / pop RDI**, not a general same-register push/pop cancellation. The exact same-register request remains an open subcase; no unsafe post-emission deletion or arbitrary inline-assembly rewrite was added.
* Original-patra diagnostics for imported modules, compiler-synthesized operations, unary-minus and compound-assignment line metadata, and signed-literal edge cases still need review. The finishing line fix is scoped tak ordinary binary-operator parsers. Do not claim universal original `patra:line` coverage.
* The three-patra Python finishing suite was syntax checked, and 18 transformation tests passed locally on captured-anchor fixtures. **The preparation CLI has not been applied tak a complete local copy of the compiler in this session.** Full-patra preparation, NASM assembly, generated program execution, speed/size improvements, full regressions and Windows acceptance are not claimed.
* The earlier `r65_source_gate.py` describes the unprepared draft and expects 12 old line markers. Do not run that old shape check against the corrected staged source and rewrite the staged source just tak satisfy it. Use the finishing tests plus real native acceptance.
* The installer work is documentation-only. No successful Windows installation, HKCU entry, icon display, editor Run, shell or screenshot was observed here.

## Integrity and provenance

The finishing SHA-256 manifest covers only files actually available and hashed locally; each uploaded finishing source patra is checked against its real Git blob. It does **not** pretend that an 18-patra source SHA-256 calculation interrupted in the previous turn completed. The original compiler's exact Git blob is recorded above; its staged SHA-256 and the complete source-tree SHA-256 suchi must be generated on Sarvam's checkout.

No `lib/*.smlib`, accepted golden, GUI colour, Devanagari lexer, workflow trigger, security setting, or credential was changed by this finishing supplement.
