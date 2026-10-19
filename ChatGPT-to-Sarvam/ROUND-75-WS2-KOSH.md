# Sutram R75 WS2 — Linux kosh reclamation prototype, actual status

Owner: ChatGPT, Step 4 on ROADMAP-TO-V1.0.md.
Review artifacts: [draft PR #39](https://github.com/dap2810/Sutram/pull/39), branch `review/r75-kosh-reclamation-stage-20261019`.
Base main v180 `05d8bdc8b461080809cdcb1187cabf22c5691001`; compiler Git blob `185b7f06ad01b5b80f123b694b0025034698bd35`. Main advanced to v181 during work; all 14 input pins still match.

## What changed
1. `tools/r75_reclaim_prepare.py` ports the earlier R73 source-locked staging to the **current** 14-pin compiler and both new PE includes; requires explicit `--experimental-unsafe-alias`; refuses source drift, duplicate/missing/reordered anchors, existing reclamation, nonregular/symlink inputs and existing stage output.
2. `src/r75_kosh_reclaim.inc` carries the identical R71-reviewed (but **not** native-accepted) growth capacity guard, mmap allocation guard and post-copy+publication Linux munmap payload. This is NOT a new compiler or a general-purpose `mukta` builtin.
3. `tools/r75_kosh_checkpoint.py` compiles the same Sanskrit source with distinct legacy/reclaim compiler binaries, uses two emitted markers with blocking `grahan()`, samples each live child’s `/proc/PID/maps` count, VmRSS, VmHWM and VmSize at start and after growth, verifies reported `kosh_len`, and emits detailed JSON. Includes timeouts and process cleanup.
4. `tests/r75/test_reclaim_tools.py` exercises source-injection and measurement-tool fixtures. This GitHub review-branch suite was uploaded but **NOT_RUN** in this environment. Independently developed local equivalent implementation: 15/15 fixture tests PASS (see OBSERVED). Do not conflate that with the exact branch’s results.

## Exact live-source structural observations
Full actual current `src/sutram_compiler.asm`, 22,807 lines, fetched from main. Kosh push contains one scope, one new-capacity anchor, one allocation call, one publish anchor. Their order is growth → allocation → copy → publication → append. No existing release hook. A structural checklist of 11/11 checks PASS, including matching core pin and 14-lock entries. **Compiler assembly/execution NOT_RUN**.

Old pointer at growth is generated-program R8, len R9, cap R10. `emit_nirmmita_from_rax` clobbers R8 and R9 for Linux mmap syscall arguments; the existing growth emitter saves/restores R8, R9 and R11 across it. The payload reads header at old user pointer minus 16 and old capacity at minus 8, computes old mmap size, then performs Linux munmap only **after copy and publication**, preserving syscall-clobbered registers.

## Safety decision NOT YET APPROVED
**Does an old mapping ever become releasable?** Yes on Linux if it is a valid mapped backing buffer and its lifetime is ended; libc free is not necessary to call raw munmap. But **automatic safe lifetime termination is not established in the language**. Sutram supports raw allocation/address read-write and yantra, and does NOT track outstanding aliases into kosh. An existing raw pointer can become dangling after a successful grow+munmap (use-after-free). The kosh parameter growth rejection does not prove alias safety.

Even this experimental fix only releases **superseded growth buffers**, not the final live allocation of each kosh at scope exit. Repeated fresh scopes still retain storage until process exit without a destructor, scoped lifetime policy or explicit `mukta`/release contract. A generic user-facing free primitive by itself does NOT solve outstanding alias invalidation at growth.

**Owner decision needed**: specify that all kosh element/raw backing aliases become invalid after growth (versioned breaking rule with unsafe boundary), or prohibit incompatible aliases while growing via compiler analysis, or define scoped ownership/cleanup. Do not mark Sutram memory-safe or merge the experimental source as default until this is decided and exercised with negative alias tests.

## How Sarvam can perform native acceptance (all NOT_RUN here)
On a complete v180-compatible source checkout containing draft PR #39:
`python3 -m unittest discover -s tests/r75 -p 'test_*.py' -v`
`python3 tools/r75_reclaim_prepare.py --stage /tmp/r75-stage --experimental-unsafe-alias`
`cd /tmp/r75-stage`
`nasm -f elf64 -I. src/r68_compiler_entry.asm -o /tmp/r75-compiler.o`
`ld -o /tmp/r75-reclaim-compiler /tmp/r75-compiler.o`
Also build the **unmodified** baseline compiler through `tools/r69_build.py` using a clean matching main source.
Then from the checkout containing the measurement tool:
`python3 tools/r75_kosh_checkpoint.py --legacy-compiler /tmp/r75-legacy-compiler --reclaim-compiler /tmp/r75-reclaim-compiler --items 1000000 --report /tmp/r75-maps.json`

Compare exact JSON, real pointer alias negative cases, integer and floating kosh growth, and the full regression/proof gates. Linux may coalesce adjacent VMAs: maps_count alone is insufficient; capture VmRSS/VmSize too. Peak RSS contains the transient copy interval and can be higher than final retained memory.

**Status:** source review 11/11 PASS; local fixture tests 15/15 PASS (different local scripts); native assembly, generated Sutram growth, A/B retained-map measurements, alias regression and Windows PE **NOT_RUN**. PE kosh-push is explicitly refused by the experimental helper, not silently emitted with Linux syscall.
