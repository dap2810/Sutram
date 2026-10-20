# Round 81 — WS2 kosh A/B: precise artifact request and blocker

**Native compiler A/B and live memory results: NOT_RUN.** Local tool output: `command -v nasm` → no executable; `command -v ld` → `/usr/bin/ld`; `git ls-remote https://github.com/dap2810/Sutram.git HEAD` → `fatal: ... Could not resolve host: github.com`. Existing conversation ZIPs contain source/tooling, NOT two contemporary runnable compiler ELFs. GitHub connector can inspect binary base64 but cannot supply a current **source-matched experimental** compiler executable on this machine without a native NASM build.

**Requested from Sarvam now (explicit form):** attach directly to this ChatGPT conversation ONE ZIP with `compiler-baseline.elf`, `compiler-reclaim.elf` and `BUILD-EVIDENCE.json`. Build BOTH with canonical `src/r68_compiler_entry.asm` from the SAME **reviewed** v208-or-later source closure. The candidate must include only the independently reviewed Linux `kosh` reclaim experiment from draft [PR #39](https://github.com/dap2810/Sutram/pull/39). The older PR #39 pin points at a PRE-R11 compiler and MUST be reconciled against the latest 15-pin lock (including `src/r11_sandesh.inc`) before assembly. Report exact Git commit/source blobs, NASM/ld versions, build commands, exit/stdout/stderr and both compiler SHA-256s.

Then perform the strict same-input before/after `/proc/PID/maps`, VmRSS, VmSize, VmHWM measurement using `tools/r75_kosh_checkpoint.py`, integer/float growth outputs and independently isolate alias-related UAF tests. Alternative is for Sarvam to run the same comparison natively and send **raw JSON** into the handoff folder.

The internal Linux `munmap` candidate theoretically frees old backing allocations after copy, but aliases into the old buffer may dangle, and the final current buffer still lacks scope-based release. Neither a safe alias contract nor public `mukta` ownership/free semantics has been approved. **Do not merge an experimental reclaim patch by inference.**

No memory allocations were measured here. Clear **NOT_RUN**, no fabricated counts.
