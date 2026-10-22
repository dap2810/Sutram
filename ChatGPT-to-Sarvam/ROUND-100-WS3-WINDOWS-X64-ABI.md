# ROUND-100 WS3 — Microsoft x64 C ABI before Windows foreign linking (one-page working specification)

**Audience: owner working on Windows linker.** Grounded in `main` `6ed4d11a3f787de4d5791430c506c42f090ba1aa` (v294, compiler v242) and `claude/windows-linker` `dda81ad27a3dc441cc420108ddfa1ffab6b60093` (v243 branch). The branch has a native Windows PE **Sutram-object linker** using `SUTRAMO2` (separate from Linux `SUTRAMO1`). Real Windows 11 standard-user installation/linker acceptance **16 required PASS / 0 FAIL / 0 NOT_RUN**, from `Windows-to-Sarvam/WIN-ACCEPT-2026-10-21.md`; **this does NOT test Windows C FFI**, COFF ingestion, or this ABI. **Branch is NOT merged into main** as of initial R100 review. The test log also reports one advisory staging-cleanup FAIL and an optional keyboard check NOT_RUN; required acceptance still PASS.

## Calling convention — NOT SysV

| ABI rule | Linux x86-64 System V (current FFI) | **Microsoft x64** (needed for Windows C calls) |
|---|---|---|
| integer/pointer parameters in registers | first 6: **RDI RSI RDX RCX R8 R9** | first **4: RCX RDX R8 R9** |
| scalar `double` arguments | XMM0…XMM7 allocated **independently** from GP registers | first **4 positions**, float or int: XMM0…XMM3 by **overall ordinal position**, not independently counted |
| mixed signature `f(i64, f64, i64, f64)` | **RDI, XMM0, RSI, XMM1** | **RCX, XMM1, R8, XMM3** |
| 5th integer argument | register R8 (if all ints) | **stack**: caller `[rsp+32]` **just before CALL**, callee `[rsp+40]` **at entry** |
| shadow/home space | no mandatory 32-byte home slots | **caller reserves 32 bytes for EVERY call**, even zero-argument calls; slots exist at caller `[rsp+0..31]` before CALL |
| stack alignment | 16-byte alignment before CALL | **16-byte alignment before CALL**; callee entry is `rsp % 16=8` after return address is pushed |
| scalar return | integer/pointer **RAX**, `double` **XMM0** | integer/pointer **RAX**, `double` **XMM0**, `void` has no usable return value |
| nonvolatile registers | RBX RBP R12-R15 (RDI/RSI volatile), XMM registers volatile | **RBX RBP RDI RSI R12-R15, and XMM6–XMM15 lower 128 bits** nonvolatile |
| >8-byte aggregate result | SysV classification may use multiple registers | **most 16-byte user structs require a hidden return buffer pointer in RCX**; explicit args shift to RDX/R8/R9 |
| integer type width | Linux LP64: `long`=64 bits | Windows LLP64: **`long`=32 bits**, `long long` and pointers=64 bits |

**Minimal call-site byte/stack plan** for a non-leaf Windows foreign call with 5 integer arguments, assuming caller entered with `rsp % 16=8` and no other frame allocations:

```nasm
sub rsp, 40                   ; 48 83 EC 28   : 32-byte shadow + 8-byte stack arg
mov ecx, 17                   ; B9 11 00 00 00
mov edx, 25                   ; BA 19 00 00 00
mov r8d, 3                    ; 41 B8 03 00 00 00
mov r9d, 4                    ; 41 B9 04 00 00 00
mov qword [rsp + 32], 5       ; 48 C7 44 24 20 05 00 00 00
call foreign_target           ; E8 disp32, existing relative name resolution (target-specific COFF conversion needed)
add rsp, 40                   ; 48 83 C4 28
```

**Critical:** that `sub rsp,40` example assumes an entry alignment of `8 mod 16` and no existing prologue/alignment changes. A general compiler must compute padding from **its actual frame at each call**; adding a fixed 40 blindly can misalign existing stack layouts. Callee sees `[rsp+8..39]` as 32 shadow bytes and 5th argument at `[rsp+40]`. Shadow memory belongs to the caller and may be overwritten by the callee. **The Linux FFI's current `r32_gen_foreign_call` stack shim does NOT reserve MS 32-byte shadow space**, so reusing it unchanged on Windows is wrong.

For mixed calls, a scalar float at argument **position 2** uses `xmm1`, not `xmm0`, even if it is the first floating parameter. At the ABI boundary the compiler must store exact float bits in the corresponding XMM register. C varargs/unprototyped calls require duplicated FP values in associated GP registers and other rules: **explicitly reject them** in first-stage Windows FFI, not silently invoke `printf`. `void` statement calls cannot be read as integers; foreign 16-byte struct return needs a checked hidden result pointer and struct layout; do not claim it works from `ptr` or `i64` alone. Alignment-sensitive arguments, callbacks, exception unwinding (`.pdata/.xdata`), nonvolatile SIMD saves, `__vectorcall`, and dynamically imported Windows DLLs are separate work.

## Actual ABI evidence (host compile control, NOT native Windows execution)

Compiled [`ROUND-100-WS3-MSABI-CONTROL.c`](ROUND-100-WS3-MSABI-CONTROL.c) on Linux x86-64 GCC 14.2 with `__attribute__((ms_abi,noinline))` into ELF **for instruction-level verification only**. [Exact disassembly and 7/7 host checks](ROUND-100-WS3-MSABI-OBSERVED.txt) show:
- `r100_int4`: uses **RCX RDX R8 R9**; `r100_int5`: reads `0x28(%rsp)` (5th at callee entry stack + 40).
- `r100_fp4`: uses **XMM0–XMM3**, `r100_mixed`: **RCX, XMM1, R8, XMM3**.
- `r100_store`: `mov %rdx,(%rcx)`; `r100_pair_return` (16-byte pair): writes into buffer pointed to by **RCX**, returns that pointer in RAX, and uses RDX/R8 as the explicit arguments.
- No ELF relocations for the simple control; executable code is a **host ABI witness**, **not** Windows COFF/PE and **not** a Sutram FFI test. 7/7 assertions PASS. Raw local source SHA256 `657ee140e1aa2bf5e24741266091a3bfd64317d649389be82ddd690cc8917386`; GCC ELF object SHA256 `28bc7f72b3ec095e5b64c9b3f7b772661ff5d807880056eb4c80dd06b580f3d0`. Source/raw Git blobs verified after upload: `76c97c590fa7acdf13899ed5235eea6dc6ce1fba`, `4330dd38c0f39099733afbdc5666cae8e8870768`.

## Actual Windows FFI acceptance gate — not yet satisfied

1. Use a **new target-specific** sidecar header (proposed `sutram-ffi-v2|windows-x86_64-ms`) and reject Linux `linux-x86_64-sysv` on Windows, with signed ABI/schema review. This is **NOT the same version as Windows object `SUTRAMO2`**. Require COFF x64 foreign `.obj` loader or an independently verified converter to the versioned Windows Sutram object; ELF x86-64 `.o` is not a Windows C object.
2. On a non-elevated real Windows machine, actual Sutram-generated caller must call one **foreign C** function with 0, 1, 4 and 5 integer args, mixed `i64/f64`, a pointer and a `void` statement; assert exact results, 32-byte shadow placement, arg5 stack offset, correct integer/XMM registers, RSP alignment and save/restore of RDI/RSI and XMM6–15. Unsupported struct/varargs/callback should **compile-fail with explicit diagnostic**, never silently link/execute incorrectly.
3. Run Windows installer/linker baseline and user acceptance against **the same exact branch/commit** used for FFI; preserve **all required** owner acceptance checks and no elevation, Windows native vs Wine clearly labeled. Also compare old ordinary compiler outputs byte-for-byte. **Existing 16/16 Windows acceptance is real, but branch-only and object-linker-only; Windows C FFI is NOT_IMPLEMENTED/NOT_RUN in R100.**

**WS3: PASS as spec + 7/7 Linux host compiler ABI evidence; NOT_RUN actual Windows FFI.** Windows linker code on `claude/windows-linker` was not edited or merged by ChatGPT.
