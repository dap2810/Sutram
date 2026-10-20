# ROUND-80 WS2 — kosh A/B

**Native A/B: NOT_RUN.** The active Linux container was checked again: NASM is absent; GNU ld/as/objcopy are available; direct GitHub DNS/clone access fails. The conversation contains previous source/tooling ZIPs, not a current baseline/reclamation ELF pair. No successful transfer or build of that pair occurred, and no memory readings were invented.

Precise artifact needed from Sarvam: one directly attached ZIP containing `compiler-baseline.elf`, `compiler-reclaim.elf`, and `BUILD-EVIDENCE.json`. Both executables must come from the SAME reviewed current source snapshot, using the canonical NASM entry, with the experimental reclamation being the stated difference. Record Git commit, every source/include identity, NASM/ld versions, commands, exits, and each binary SHA-256. A mounted attachment or a downloadable connector artifact file reference is usable; no credentials are requested.

The inspected current source lock includes `src/r11_sandesh.inc` and 15 entries. Do not blindly run the older PR #39 staging pins against it. Reconcile the experiment with current accepted source first, then run its checkpoint tool on identical generated programs and return raw maps_count, VmSize, VmRSS and VmHWM before/after, along with exit/stdout. No such JSON exists from this session.

The alias/lifetime question remains open: successful internal munmap would not prove old raw aliases are safe, and freeing superseded buffers would not release the final live container at scope exit. No public free primitive, compiler patch or native memory-safety claim was introduced here.
