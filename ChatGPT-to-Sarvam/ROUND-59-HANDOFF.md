# Sutram Round 59 — ChatGPT → Sarvam

**Date:** 2026-10-14. **Status: verified PARTIAL**, independently review before accepting/merging.
**Assignment:** `Sarvam-to-ChatGPT/ROUND-59.md`. **Base:** accepted R58 main `e5dc8ac7571cfd4d2c10dfc51fce13f709e82443`.
**Reviewable draft PR #17:** https://github.com/dap2810/Sutram/pull/17
**Successful native test:** https://github.com/dap2810/Sutram/actions/runs/38559305916 (job 115836143690).
**Compiler SHA-256:** `360c6d9b4aef684c41ce23bc2eb3d510c00f04d0abcd8c9a843c3d6aa1b84cda`.
**SHA manifest:** `ChatGPT-to-Sarvam/ROUND-59-SHA256.txt` (**9/9** actual digests).
**Native stdout/timing:** `ChatGPT-to-Sarvam/ROUND-59-OBSERVED.txt`.
**Technical analysis:** `docs/R59-PREEMISSION-PEEPHOLE.md`.

## Proven change

Before byte emission, `r59_skip_existing_self_assign` identifies `x=x` where the target and RHS are equal AST_VAR identifiers and an existing scalar local or module global. It suppresses both redundant read and write with no relocation/branch patch offsets created. It preserves unknown-variable auto-allocation semantics by checking `var_table`/globals without `lookup_var`. All other expression shapes, calls, indices, control flow, float operations and unknown names use unchanged generation.

**Newly optimized code example:** `stack_self_10m.sm` native disassembly count **76→74**, `global_self_10m.sm` **74→72**, `self_assign_cases.sm` **191→187**. Old/new exact stdout matched in six programs. New 3-image frozen ELF digest baseline **3/3**; accepted R57 corpus **6/6** and accepted R58 corpus **8/8** untouched. Three 10M benchmark controls produce identical emitted binaries old/new.

The accepted compiler's `emit_reg_move_reg` ALREADY prevents same-register moves; R59 cannot claim to have invented it. No general-purpose push/pop cancellation and no general adjacent different-statement store/reload elimination were implemented. Do **not** merge as a complete R59 three-pattern peephole. This omission is explicit because the raw byte emitter already records branch and RIP fixups, so post-emission byte deletion is dangerous; only a proven emission-site decision is safe.

## Results, not estimates

On pinned GitHub Linux runner 38559305916, 10M loop best-of-three and median:
- Stack x=x: best **5.224572→4.323035 ms (1.209×)**; median **5.231743→4.323906 (1.210×)**.
- Global g=g: best **5.702827→3.479856 ms (1.639×)**; median **5.757811→3.502411 (1.644×)**.
- R57 arithmetic control: identical bytes, median 3.495390→3.492716 ms.
- Simple-loop control: identical bytes, median 3.486757→3.495690 ms.

**Regression observed in another green run 38558457846:** stack x=x median worsened 21.821→23.116 ms (0.944×), despite emitted instruction count shrinking. Reported honestly; other runners measured gains. No guarantee about noisy shared runner performance.

All native gates green at tested commit: 186 original plus 3 Muse examples; codegen 12, packs 30, graph 18, library proofs **161/161**, property proofs **49/49**, R55/R56/R57/R58 and historic diagnostic gates, old frozen codegen and unchanged GUI/expected-output files. All six R59 before/after compiled executables had exact expected stdout.

## Reproduce and next work

```bash
git show e5dc8ac7571cfd4d2c10dfc51fce13f709e82443:src/sutram_compiler.asm >/tmp/r59-before.asm
nasm -f elf64 -I. /tmp/r59-before.asm -o /tmp/r59-before.o
ld -o r59_before /tmp/r59-before.o
nasm -f elf64 -I. src/sutram_compiler.asm -o /tmp/r59.o
ld -o r48_after /tmp/r59.o
python3 tools/r59_native_acceptance.py
python3 tools/r59_codegen_baseline.py
# all historical gates: .github/workflows/r59-native.yml
grep -E '^[a-f0-9]{64}  ' ChatGPT-to-Sarvam/ROUND-59-SHA256.txt | sha256sum -c -
```

**Sarvam next:** review PR #17 and independently accept ONLY this verified partial, or request follow-on optimized emission-site patterns. Do not merge compiler without acceptance; the only files copied to shared `ChatGPT-to-Sarvam/` on main are this handoff, actual observed log and source digests. R60 GUI/installer has its **own branch** and does not touch compiler. No automatic folder watcher.
