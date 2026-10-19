# Round 72 — kosh growth reclamation profile and alias contract

**Status:** compiler-source integration on review branch based directly on v172 main; default-off opt-in. The exact profile is selected by NASM -DSUTRAM_R72_KOSH_MUKTI=1 with src/r68_compiler_entry.asm. No full NASM compiler or Sutram-produced executable was run by ChatGPT in R72.

The initial source is the accepted main compiler Git blob f4fefe6ca438bf2f76f68e6742bb71e8a836ccb6. The reviewed R71 native payload is e9a6f5d02f2b4c98343de6f85c3442ab8890d59a, copied inside the current one pure-NASM compiler source; hook sites are verified against the renamed v172 core, not patched from an old pre-v157 blob. Changed source blob: 9c41189e1bf30caf1dcc3b8eadc883b11b07f12b.

## Mechanism — Linux ELF only

Three new compiler-host emitter calls are guarded by the opt-in define. On the generated program's capacity-growth branch they:

1. Reject mismatched length/capacity and capacity arithmetic that would overflow the allocation length.
2. Reject null or raw error return from Linux mmap before header writes or copying.
3. After copying elements and publishing the new pointer, emit Linux munmap(old_payload - 16, old_capacity*8 + 16), preserve the machine registers/stack needed by the append path, and fail on release errors.

The no-growth append branch skips all three generated payloads. The compiler's default configuration (define omitted) should generate the former bytes unchanged; **exact byte equality is a native acceptance requirement, not a result observed here**. The emitted PE kosh-growth path deliberately fails closed when this Linux-only mode is enabled; there is no safe substitution of syscall 11 for Windows VirtualFree. The ordinary default source mode retains the accepted existing PE behavior (including its leak).

## Contract proposed for acceptance

**Completed growth invalidates all raw aliases to the previous kosh backing allocation.** An old address is not stable after growth, even if it still happened to be mapped. Callers must not dereference it after capacity-changing kosh_push or its FIFO alias. No borrow checker enforces this; therefore this behavior change remains **opt-in pending a compatibility decision**. Typed kosh parameter growth remains rejected, but that does not establish general ownership safety. No final-buffer release, scope cleanup, kosh_clear destructor, or public general free primitive was added.

Recommend a future typed owner-level disposal operation only after ownership, aliasing, platform allocator identity, repeat-disposal behavior and failure channels are specified; do not silently add raw munmap as a safe builtin. This feature does NOT make Sutram memory-safe.

## Native acceptance not yet observed

The R72 branch contains exact-output/exit fixtures in examples/r72_kosh_mukti and the reproducibility gate in tools/r72_baseline_gate.py. In a clean checkout of this review branch:

    python3 tools/r72_baseline_gate.py --source-only --report /tmp/r72-source-check.json
    python3 tools/r72_baseline_gate.py --mode default --report /tmp/r72-default-gates.json
    python3 tools/r72_baseline_gate.py --mode mukti --report /tmp/r72-mukti-gates.json

Use tools/r72_kosh_acceptance.py once present and accepted for exact integer and binary64 output, old/new unaffected binary identity, two-barrier Linux VmSize comparison, and PE refusal. Compare retained mappings at defined barriers, NOT peak RSS: old and new buffers necessarily coexist during copy. Additional aliases must be reviewed without dereferencing a deliberately unmapped old pointer.

The earlier R71 isolated payload was retested in this session (44/44 tests under uid=1000, Linux x86-64), but that is not a newly executed full compiler. Production NASM, generated program output, memory VmSize A/B, default parity, complete regression/proofs, and Windows VirtualFree are NOT_RUN.
