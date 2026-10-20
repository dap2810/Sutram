# Sutram R82 WS1 — decision: REQUEST THE BINARY

**Request Sarvam to supply a Linux ELF A/B pair**; do not drop the Step 4 leak work.

Please provide one directly attached ZIP (conversation attachment is usable) containing `compiler-baseline.elf`, `compiler-reclaim.elf`, and `BUILD-EVIDENCE.json`. The executables must be produced using the **same accepted current source snapshot and 15 source pins** plus only the experimental Linux reclamation difference. The old experimental staging in draft PR #39 predates the R11/R13 changes and must be rebased/re-pinned; do not compare unrelated compiler versions. Evidence must state current commit, core/include Git blobs, NASM/ld versions, commands, build exit, SHA-256s. An alternative is for Sarvam to run the A/B checkpoint on its Linux machine and upload raw `/proc` map/VmRSS/VmSize/VmHWM JSON.

**NATIVE A/B NOT_RUN:** no verified current patched ELF pair in this session; container execution remains unavailable. Do not infer pass/fail from source or mock tests.

Safety policy is unresolved. Releasing old backing via Linux `munmap` can create use-after-free for raw aliases; final live kosh buffers still lack scope cleanup. No compiler patch merged.
