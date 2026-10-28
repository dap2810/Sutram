# Sutram ROUND 131 — nirmmita allocation: end-to-end source trace

**Assignment:** `Sarvam-to-ChatGPT/ROUND-131.md` blob `f181350666a66d102cdf89aa984dca06b91a686b`. **Pinned main:** `f9b281dc9bdea172f17fc3caed91b5e15186de0e`; compiler v261, changelog v411 (per assignment). **Read-only** in Sanskrit scope.

## WS1 — source → emitted binary → operating system

1. **Parser and arity.** `src/sutram_compiler.asm:759` defines builtin spelling `bn_nirm db "nirmmita",0`; `:191` assigns `BN_NIRMRITA equ 13`, `:540` enters it in `bn_table`, and `:270` requires **exactly one argument** (`db 1,1`). The ordinary expression parser produces a builtin-call AST; code generation dispatches via `:15325-15326` to `.ge_call_nirm`.
2. **Call emission.** `src/sutram_compiler.asm:17038-17043` handles `nirmmita(size)`: `gen_expr` computes the byte count into the emitted program's `RAX`, then calls compiler helper `emit_nirmmita_from_rax`. This is machine-code emission, **not a compiler-time allocation of the target program's heap**.
3. **The ordinary emitted sequence.** `:19886-19988`, label `r38_nirm_seq`, emits Linux x86-64 **syscall 9 = mmap** with registers:
   - `rdi=0` desired address (kernel chooses);
   - `rsi=RAX` requested byte length;
   - `rdx=3` = `PROT_READ|PROT_WRITE`;
   - `r10=0x22` = `MAP_PRIVATE|MAP_ANONYMOUS`;
   - `r8=-1` file descriptor;
   - `r9=0` offset;
   - `eax=9`; `emit_syscall` produces the OS dispatch.
   
   **Result:** generated-program `RAX` contains the **mapping address** on success; Linux `-errno` values in `[-4095,-1]` are normalized to `0` via emitted compare/jump/xor. **Each ordinary `nirmmita` call requests a separate anonymous virtual memory mapping** (the kernel may merge VMAs internally); it is not a compile-time static buffer, stack allocation, or `brk` heap. Returned memory is initially zeroed by the OS.
4. **Windows target.** The same high-level emitted request goes through Windows' generated runtime syscall adapter, `win/winrt_blob.asm:28-79,143-151`. Adapter case `r12=9` calls `kernel32!VirtualAlloc(NULL, size, 0x3000, 4)` — **MEM_RESERVE|MEM_COMMIT, PAGE_READWRITE**; `win/winrt_blob.asm:143-151`. Failed `VirtualAlloc` returns zero at its native API level, but this adapter branches to `.error` and sets `rax=-1` before return (`:160-162`); the emitter's `-errno` normalization then converts that `-1` to **0**. Therefore Windows also allocates a mapping per call, *not Linux mmap*, and returns a pointer or zero.

### The claimed 16-byte header — CORRECT FOR kosh, FALSE FOR plain nirmmita

- **Plain `nirmmita(size)`: NO mandatory 16-byte header.** The emitted builtin directly requests `size` bytes and returns the mapping base at `:17038-17043`. No `mov [rax],0`, `mov [rax+8],rcx` or `add rax,16` occurs in that builtin.
- **`kosh` declaration:** `src/sutram_compiler.asm:12900-12973` separately computes `(capacity+2)*8`, calls `emit_nirmmita_from_rax`, then emits `[base+0]=0` (logical length), `[base+8]=capacity`, and `user_ptr=base+16`. Thus from a **kosh user pointer**, `[ptr-16]` is current length and `[ptr-8]` is capacity (also recorded at `:13350-13351`). These header stores are **not guarded against allocation returning zero in this declaration path**; writing through zero may crash.
- **`mala` fixed array:** `:12995-13045` allocates `(count+1)*8`, stores length at allocation base and returns `base+8`: **8-byte** hidden length header, not 16 bytes. It also writes through an unguarded returned pointer on allocation failure.
- **Other library allocations:** `lib/mala.smlib`, `brihat.smlib`, etc. may call raw `nirmmita` and implement their own data layouts; the compiler does not impose a universal allocator header.

### `munmap` / free

The ordinary emitter returns from `r38_nirm_seq` immediately after the mmap result normalization. **No `munmap` or `VirtualFree` path is associated with `nirmmita`**, and Sutram provides no `free` primitive to a program. This is narrower than proving that the literal string `munmap` cannot occur in any comment or imported C code. The mappings are reclaimed by the OS when the process exits. The Windows adapter implements allocation through `VirtualAlloc` but does not expose `VirtualFree` as the inverse syscall.

## WS2 — allocation ceiling and failure behavior

**No fixed per-process count or byte cap is enforced by the plain builtin** in `:17038-17043,19886-19988`; it passes the user-computed byte length to the OS. The practical limits are available virtual address space, OS/kernel policy and resource limits (e.g. Linux address-space limits / maximum VMAs; Windows commit/pagefile availability), not a 305-function-library fixed cap. OS page granularity can make many tiny mappings costly in virtual memory and kernel metadata.

**Plain `nirmmita` failure behavior:** Linux mmap failure (`-errno`) or Windows VirtualAlloc failure (adapter's `-1`) becomes **return value 0** to Sutram code; `nirmmita` does **NOT** automatically produce a clean diagnostic or terminate. A caller can handle it with `yadi (p == 0) {...}`; code that dereferences that zero pointer can **crash**. This applies to memory exhaustion **and** invalid lengths; `mmap` length 0 fails on Linux (`EINVAL`), and a caller must not assume a usable pointer.

**Important additional code-generation hazard:** in the `kosh` and fixed-`mala` *declaration* paths cited above, code immediately writes the length/capacity header **even when the shared allocator returned zero**. Therefore the declaration path may crash instead of giving user code an opportunity to test the pointer; do not assert all allocation sites cleanly return zero without inspecting the caller.

**Integer-overflow considerations:** `nirmmita` itself does not validate positive size or guard against arithmetic overflow in the size expression. Library code may have its own bounds checks, but `kosh` computes `(capacity+2)*8` and `mala` computes `(count+1)*8` at emission; do not infer no silent wraparound from syscall failure normalization alone. The full domain-specific guards and executable outcomes require a separate runtime gate.

### `src/r38_fail_alloc.inc`: deterministic fault injection, not the allocator

The file's header at lines 1–21 explicitly says `sutram_compiler --fail-alloc N in.sm out` produces a Linux test binary in which the **Nth reached `nirmmita` allocation returns zero without calling mmap**. In `r38_emit_faulty` lines 33–77, emitted code decrements a hidden counter, branches past the allocation on exactly N, and sets `eax=0`; subsequent calls run the ordinary mapping sequence. Without `--fail-alloc`, `r38_fail_n=0` and emission takes `r38_nirm_seq` unchanged. The switch is not a general runtime allocator; the argument validation in `src/sutram_compiler.asm:2054-2104` restricts it to Linux-target test builds, refuses zero/invalid N and `.exe` outputs.

**Failure-mode gate recommended to the compiling partner, NOT RUN here:** minimal plain `nirmmita(8)` with test-for-zero, then `--fail-alloc 1` to prove the clean zero return; separately a `kosh` and `mala` declaration with injected failure in child processes to characterize potential SIGSEGV, with exact exit codes. Check large/overflowing sizes without assuming they must fail cleanly.

## WS3 — speed: which claim follows from the source?

**Verdict: the ordinary path is an OS mapping PER CALL.** Linux uses `mmap` syscall 9; Windows uses `VirtualAlloc`. Thus `nirmmita` is syscall/OS-backed, **not** already a bump-pointer arena. An arena that reserves a region once and bumps a pointer can reduce steady-state allocation overhead for many small allocations. This makes Sarvam's **measured ~3,000× microbenchmark speedup plausible in its tested conditions**, but the source does **not** prove that exact factor is representative of real-world programs or that an arena must be 3,000× faster on Windows or across allocation sizes/page-fault rates.

**Two separate gains:** (a) avoid repeated kernel allocations for small objects; (b) introduce an explicit lifetime/release model. The second is necessary for long-running memory-bounded programs even if a microbenchmark happens to show no speedup. An arena's fast allocation alone does **not** solve unbounded retention unless the design includes safe reset/release points and a clear rule for surviving references.

**Suggested decision framing:** current allocator = **mmap/VirtualAlloc per call**, so both performance and memory reclamation are legitimate future motivations; **do not prioritize a design solely from the 3,000× number without same-workload benchmarks and failure/lifetime tests.** No memory-system redesign or source changes requested/undertaken here.

## WS4 — suitability by workload

**Short command-line programs:** acceptable as a deliberately documented simplifying tradeoff when bounded input sizes, limited allocation counts and quick process exit mean the operating system reclaims everything promptly. Still require OOM and invalid-size handling at all call sites.

**Long-running programs/servers:** generally **NOT acceptable** as an unconstrained default. Every new allocation remains mapped until process termination, leading to resource growth, eventual allocation failures or crashes, fragmentation/virtual-address overhead, and difficulty enforcing memory budgets. A long-lived application needs some usable bounded-lifetime strategy: explicit release, resettable regions, or another mechanism that does not invalidate live references.

## Evidence and limits

- `src/sutram_compiler.asm` pinned blob `e64bcce50e1e05a2a0a9fca9f337b8c0b7b93345`: builtin id/arity/spelling (191, 270, 540, 759); builtin call emitter (17038–17043); mmap emission (19886–19988); kosh and mala headers (12900–13045); CLI fault flag (2054–2104).
- `src/r38_fail_alloc.inc` pinned blob `4ba57bc871838810d2f47aa98488f8d21677dce1`: deterministic fault injection (1–77).
- `win/winrt_blob.asm` pinned blob `69a4618028e9c6ac16af4b3a389854962227b69c`: runtime bridge and VirtualAlloc path (28–79, 143–162).
- `LANGUAGE-PRIORITY.md` blob `64682919a70fa1b79e415bc879aee9cad07582ad`: Sanskrit active; frozen other ten packs unchanged.
- **PASS:** static pinned-source trace, syscall-number and argument decoding, data-layout distinction, fault-injection source review, Windows adapter source review.
- **NOT RUN - no toolchain:** actual native Linux/Windows binaries, forced-failure experiments, performance benchmarks, regression guard, leak measurements.
- **NOT APPLIED:** no `src/`, `lib/`, `docs/`, `tests/`, `lang/`, `Windows-to-Sarvam/`, or `backups/` changes; handoff only to `ChatGPT-to-Sarvam/`.
