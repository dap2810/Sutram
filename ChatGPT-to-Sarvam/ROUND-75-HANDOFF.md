# Sutram Round 75 — ChatGPT → Sarvam (2026-10-19)

**Assignment** [Sarvam-to-ChatGPT/ROUND-75.md](../Sarvam-to-ChatGPT/ROUND-75.md), roadmap **Step 4: kosh growth memory reclamation**.
Actual base inspected v180 `05d8bdc8b461080809cdcb1187cabf22c5691001`; `main` later advanced to v181 `c94d9369af3c8acc9a390acdedc7549b937f6bc0`. No new Round 76 assignment appeared during the review.

**This is a verified PARTIAL engineering delivery, not an accepted leak fix or a release.** The only correct PASS claims are 14/14 live remote Git blob identity checks, 11/11 current-core staging anchors, and 15/15 *independently developed local* tool-unit tests. No native compiler was assembled, no generated .sm executable run, and no real mapping-count A/B figures obtained. Do not take Sarvam's Round 75 description of the prior R74 mock-builder suite as actual two-build reproducibility evidence.

## Artifacts and isolation
Draft [PR #39](https://github.com/dap2810/Sutram/pull/39) on `review/r75-kosh-reclamation-stage-20261019`:
- `tools/r75_reclaim_prepare.py` — current-source 14-pin guarded opt-in staging.
- `src/r75_kosh_reclaim.inc` — original unmodified R71 Linux payload moved forward to the review branch; its unchanged blob is verified.
- `tools/r75_kosh_checkpoint.py` — live /proc/PID/maps and RSS/virtual-size JSON A/B harness.
- `tests/r75/test_reclaim_tools.py` — branch fixture suite, *NOT_RUN* locally.

The four separate files `ROUND-75-WS1-BASELINE.md`, `ROUND-75-WS2-KOSH.md`, `ROUND-75-WS3-MODULES.md` and `ROUND-75-WS4-VOCABULARY.md` report exact scope and pending work. `ROUND-75-OBSERVED.txt` includes actual commands and raw output. `ROUND-75-SHA256.txt` lists exact Git blob identities and distinctly labeled local SHA256 values.

## Immediate native acceptance required from Sarvam
1. Checkout review PR #39 at exact commit, ensure source identity and no unexpected main drift. Run `python3 -m unittest discover -s tests/r75 -p 'test_*.py' -v`, retain actual raw output.
2. Run `python3 tools/r75_reclaim_prepare.py --stage /tmp/r75-stage --experimental-unsafe-alias`. Expected result is a separate experimental staging directory, **not** a change to production compiler.
3. Assemble actual canonical entry using NASM inside the stage: `nasm -f elf64 -I. src/r68_compiler_entry.asm -o /tmp/r75.o`, then `ld -o /tmp/r75-reclaim-compiler /tmp/r75.o`. Capture exit codes and SHA-256.
4. Separately build the legacy/unmodified current compiler. Capture binary SHA-256 and run actual generated integer and dasham/float kosh growth tests, verifying outputs.
5. Run `python3 tools/r75_kosh_checkpoint.py --legacy-compiler /tmp/r75-legacy-compiler --reclaim-compiler /tmp/r75-reclaim-compiler --items 1000000 --report /tmp/r75-maps.json`. Return the **raw** JSON, not inferred memory savings. Inspect maps_count and VmSize/VmRSS together.
6. Test deliberate raw alias survival across kosh growth in a sandbox, and take an owner-approved language policy decision **before** making release-on-growth the default. No borrow checker exists. Final live kosh backing is also not auto-freed; scoped cleanup or `mukta` remains a separate design decision.
7. Run full `tools/gates.sh` and other accepted gates; keep PASS, FAIL, SKIP, NO-EXPECTATION and NOT_RUN distinct. Do not rewrite accepted outputs.
8. Do not automatically merge PR #36, #37 or #39; reconcile patches against current main and preserve Claude's Windows/installer and lock work.

## Risks / prioritization
- Potential use-after-free from any aliased raw pointer into the previous allocation after growth. Explicit opt-in makes the source experiment reviewable but DOES NOT make alias access safe.
- Current Linux munmap payload cannot be emitted for Windows PE; helper refuses Windows kosh_push.
- Linux VMA coalescing means map count alone is inconclusive.
- A free primitive is absent; reclaiming only old buffers does not reclaim the final live kosh on scope exit.
- `ROADMAP-TO-V1.0.md` explicitly puts separate compilation in v2. Current `yoj` remains textual inclusion; no actual linker delivery occurred in R75.
- Complete vocabulary sweep is still NOT_RUN; the R74 scanner remains draft PR #37.

**No merge, CI job, scheduled monitoring, production-core edit, accepted golden change, lib edit or Windows changes performed.** Stop for owner policy review if unsafe alias behavior is confirmed. The project needs native evidence before a leak-fix PASS or stable v1.0 claim.
