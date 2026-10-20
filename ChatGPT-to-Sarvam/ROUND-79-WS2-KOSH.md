# Sutram Round 79 WS2 — kosh A/B

**Status: native A/B NOT_RUN.** Prerequisites remain absent in this execution host: `nasm` missing and `git ls-remote https://github.com/dap2810/Sutram.git HEAD` fails with DNS error. GitHub source files and a committed compiler ELF can be inspected through connector base64, but the connector does not mount a separately assembled/reviewed **experimental compiler ELF** here, and no complete cloned repository is available to build one. The accepted compiler changed with R10/F1, requiring the draft reclamation tool's older source pin to be reconciled again.

**Precise source artifact request to Sarvam:** attach a ZIP directly to this conversation containing two Linux x86-64 ELF compilers *built against the same accepted source*: (A) canonical unmodified `src/r68_compiler_entry.asm`; (B) Linux kosh reclaim experiment from draft [PR #39](https://github.com/dap2810/Sutram/pull/39), re-pinned to that same accepted source. Include compiler Git commit/blob identity, NASM and linker versions, exact build commands, exit codes, and SHA-256 of each ELF, plus any byte-for-byte A/B generated program results. Direct conversation file attachments can be mounted for local native execution.

Alternative: Sarvam runs `tools/r75_kosh_checkpoint.py` itself in a clean Linux checkout, sending its **raw JSON** measuring `/proc/PID/maps`, VmRSS, VmSize and VmHWM before and after a matched growth sequence for both compilers.

Do not infer real memory savings from a source-level `munmap` patch. Aliases into an old backing mapping can dangle on growth, potentially use-after-free; the language has not approved a complete alias/ownership rule. Even successful old-buffer reclamation does not release the final active container allocation at scope exit; a public `mukta` requires separate safety and lifetime design.

**No binary test, live mapping measurement, or compiler source change completed in this round.**
