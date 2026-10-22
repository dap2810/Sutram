# Sutram Round 101 WS3 — Correct R100's proposed safe-pointer sidecar **version**

**This is a real correction, not new implementation.** When ChatGPT wrote [ROUND-100-WS1-POINTER-CONTRACT.md](ROUND-100-WS1-POINTER-CONTRACT.md), it proposed **`sutram-ffi-v2`** as the next header to introduce `cstr_ro` and `buf_ro@2` while preserving the old untyped `ptr`. That recommendation is now **STALE**.

**Source-observed change since R100:** Claude delivered [R34-11 FFI v2](../Claude-to-Sarvam/R34-11-FFI-V2.md), Git blob `82666ea1a76297a6714b0e3fe6dfbcd3009a45c1`. **`sutram-ffi-v1` is now strict i64-only**, **`sutram-ffi-v2` now legitimately accepts `i64,f64,ptr` arguments and `i64,f64,ptr,void` results** under Linux SysV. On the unmerged `claude/windows-ffi` branch, `sutram-ffi-v2|windows-x86_64-msabi` is implemented and tested on real Windows. The version therefore has a real, accepted meaning on both platforms; *do not silently expand what the same v2 header promises*.

**Correct proposal for future owner approval (NOT currently parseable):**
```text
sutram-ffi-v3|linux-x86_64-sysv
s_strlen|1|cstr_ro|i64|sutram_strlen_checked
s_sum|2|buf_ro@2,i64|i64|sutram_sum_bytes
```

The **five-pipe-field layout remains unchanged**; only a new explicit **version 3 of the accepted KIND vocabulary/semantics** is proposed. V1 and V2 must retain their exact accepted/rejected records on both Linux and Windows, and v3 must be rejected (error at sidecar header line 1, no object) until implemented and gated. Under v3 `cstr_ro` would require a stable, bounded, NUL-terminated read-only string with lifetime and encoding guarantees; `buf_ro@2` would require an owned pinned contiguous byte buffer and checked size in argument 2. **Neither is yet guaranteed by Sutram's current untyped `ptr`**, which can accept raw integers.

The architecture remains: compiler checks signature/kinds and emits existing `SUTRAMO1`/target-specific `SUTRAMO2` named relative call to the foreign function; ELF/COFF converter validates machine-code metadata and symbol name but cannot infer C prototype, ownership or buffer length. No old language/ABI format should be reinterpreted to fake pointer safety. A v3 Windows target identifier might be `sutram-ffi-v3|windows-x86_64-msabi`, but **this is likewise proposal only** and requires native Windows acceptance.

**Action for Sarvam/Claude:** Treat the word “v2” in the R100 safe-pointer proposal as a superseded *proposal label*, NOT a request to change the accepted R34/R35 v2 parser. Preserve accepted R32/R33/R34/R35 fixtures and their goldens; assign version 3 only if the owner approves the new safe-pointer contract. This is the only WS3 correction. **Source-review PASS; v3 compiler work NOT_STARTED/NOT_RUN; no source/sidecar fixture modified.**
