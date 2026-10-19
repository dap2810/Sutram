# Sutram R76 — WS1 Kosh: source work and native blocker

**Native kosh A/B: NOT_RUN.** No real compiler executable was available and NASM is absent from this session. No memory mapping counts, VmRSS, VmHWM, or VmSize A/B were invented.

## Raw measurement attempt
Command:
`python3 tools/r76_kosh_measure.py --legacy-compiler /mnt/data/sutram_r76/not-a-compiler --candidate-compiler /mnt/data/sutram_r76/not-another-compiler --items 1000000 --report /mnt/data/sutram_r76/evidence/measurement-blocker.json`

Exit 2, stdout/report:
```json
{
  "status": "FAIL",
  "reason": "nonregular executable: /mnt/data/sutram_r76/not-a-compiler"
}
```

This is a missing-binary prerequisite failure, NOT a Sutram-generated program's failure.

## Current source and work completed
main snapshot v183 commit `2d1d884a54faf94eccfcf6a050000ee881657188`; current compiler Git blob `cc5cfbe48ac3ea1360958cb8f203385744d094b8`; current build-lock blob `533cc61d0a1038d99c719fb2289e991aade1ada8`. Remote 14/14 lock pins MATCH actual tracked blobs. Actual compiler file has 23,335 lines; its kosh growth region has unique growth/allocation/publish markers in correct order, no reclaim hook (9/9 structural checks PASS).

Re-pinned existing experimental `tools/r75_reclaim_prepare.py` in [draft PR #39](https://github.com/dap2810/Sutram/pull/39) from obsolete R5 core blob `185b7f06...` to R7 current `cc5cfbe4...`. GitHub commit `c78f7e766a27e94710bc563697806bb0ca9d1a11`, updated Git blob `7f0111fea2a6b12a3cb85f9dd65a13a8921c3ce6`. Read back and confirmed. The explicit `--experimental-unsafe-alias` guard remains intact. Existing R71 Linux-only reclaim payload was NOT altered; production compiler and Windows source untouched.

Local independently developed R76 tooling, staging and measurement mock/fixture tests PASS 11/11. Module harness fixtures PASS 4/4, total 15/15. This local tool is not byte-identical to PR #39; do not claim PR #39's exact tests were run.

## Safety conclusions
(1) Does it reclaim? Unknown until native executable A/B JSON. The helper emits Linux munmap for the superseded mapping after successful copy + pointer publication, but this does not prove successful execution. Map counts can be misleading due to VMA coalescence; record retained VmSize and RSS too.
(2) Alias safety? Not established; raw aliases into the previous backing allocation can become dangling on growth, producing potential use-after-free.
(3) Public `mukta`/free? Not required strictly for internal release of a superseded Linux mmap buffer. However the final kosh allocation has no scoped release, and safe general release needs ownership, provenance and double-free safeguards. A raw public free primitive alone does not solve growth alias invalidation; owner must decide the lifetime contract before default merging.

## Native instructions to Sarvam
On a matching full checkout with PR #39:
`python3 -m unittest discover -s tests/r75 -p 'test_*.py' -v`
`python3 tools/r75_reclaim_prepare.py --stage /tmp/r76-stage --experimental-unsafe-alias`
`cd /tmp/r76-stage && nasm -f elf64 -I. src/r68_compiler_entry.asm -o /tmp/r76.o && ld -o /tmp/r76-reclaim-compiler /tmp/r76.o`

Build the legacy current compiler separately, record exact source and binary SHA-256, then run:
`python3 tools/r75_kosh_checkpoint.py --legacy-compiler /tmp/r76-legacy-compiler --reclaim-compiler /tmp/r76-reclaim-compiler --items 1000000 --report /tmp/r76-native-maps.json`

Return raw JSON and run real integer/float kosh growth, alias negatives and all accepted regression/proof gates before acceptance. Do not merge the experimental source as production.
