# R78 WS0 — F1 root cause; read-only compiler review

Source snapshot: main v195 `2e875ea729a252d537378cee6d944b1de790d0a3`; `src/sutram_compiler.asm` Git blob `5caa9b6ef260d75ddea65a44a8daed94237833cc` (23,459 lines). **No compiler source was edited.**

## Exact sites
- `alloc_var` at line **19957**, especially `.av_stack` lines **19979–19983**, increments `stack_dep` by 8 and negates it: the computed offset is a *signed negative rbp-relative* offset. The allocator itself is not truncating it.
- `gen_all_functions` at **11414**, `.gaf_no_params` near **11580–11584** initializes stack depth to `8 + 8*parameter_count` for saved RBX and parameters. Its function prologue reserves `FUNC_SPILL_BYTES` at **11586–11594**, defined as **2048** at line **101**. The failure at 34–40 variables is not spill-area exhaustion.
- `emit_load_named_var` at **19856**, `.elnv_stack` at **19875–19884**, always emits `48 8B 45 disp8`, even when the signed negative offset no longer fits one byte.
- `emit_store_named_var` at **19886**, `.esnv_stack` at **19905–19914**, always emits `48 89 45 disp8` for arbitrary negative offsets.
- Other relevant disp8-only emitter regions found in the current core: lines **12046, 12139, 12211, 12388, 12470, 12598, 12647, 13094, 14190, 14290, 14336, 17601, 19880, 19910**. This list includes a potentially unreachable legacy site at 12647; inspect control flow before editing. The `0x45` byte at line 18919 is an unrelated `xor r9d,r9d` instruction and must not be replaced.

## Root cause in two sentences
The allocator calculates a valid signed rbp-relative offset, but load/store emission unconditionally uses ModRM `0x45` (an *8-bit signed displacement*) and truncates the offset to its low byte. Offsets beyond -128 wrap into positive offsets or collide with previous negative slots, corrupting caller data, a return address or local values while the compiler still reports successful generation.

## Actual local x86 byte probe, separate from Sutram
```text
offset    -8 old 48 89 45 f8 -> rbp-8  [correct]
offset  -128 old 48 89 45 80 -> rbp-128 [correct]
offset  -136 old 48 89 45 78 -> rbp+120 [WRONG]
offset  -136 new 48 89 85 78 ff ff ff -> rbp-136 [correct]
offset  -248 old 48 89 45 08 -> rbp+8 [WRONG: return address]
offset  -248 new 48 89 85 08 ff ff ff -> rbp-248 [correct]
offset  -264 old 48 89 45 f8 -> rbp-8 [WRONG: local alias]
offset  -264 new 48 89 85 f8 fe ff ff -> rbp-264 [correct]

GNU objdump -D -b binary -m i386:x86-64 /tmp/r78-disp-probe.bin:
  0: 48 89 45 78            mov %rax,0x78(%rbp)
  4: 48 89 85 78 ff ff ff   mov %rax,-0x88(%rbp)
  b: 48 89 45 08            mov %rax,0x8(%rbp)
  f: 48 89 85 08 ff ff ff   mov %rax,-0xf8(%rbp)
```
This disassembly was executed here using GNU binutils. It proves instruction-byte decoding, not that any Sutram compiler was assembled or exercised here.

## 34 Windows versus 38 Linux?
The generated x86-64 disp8 displacement has the same meaning on both platforms, so there is **no verified platform-specific physical-stack threshold**. An example with one called-function parameter can overwrite `rbp+8` (return address) around 34 total variables; a larger `mukhya` example wraps around to `rbp-8` and overwrites an earlier local around 38–40 variables; whether the resulting memory corruption produces no output, wrong values or a crash depends on call-frame shape, parameters and accessed values.

**Critical evidence correcting ROUND-78's old Linux-34-untested assumption:** `Claude-to-Sarvam/R9-01-F1-REPRODUCTION.md` and `Claude-to-Sarvam/evidence-r9/F1/f1_c_return_address.sm` record the 34-variable *Linux* segmentation fault too. The F1b 40-variable case printed `151 38 39 39 40` instead of `55 6 7 39 40`; R9's objdump excerpt confirms the incorrect `48 89 45 78` instruction. These are Claude's historical executions, **not rerun by ChatGPT today**. Thus a guard-page/OS-ABI hypothesis is unnecessary to explain the threshold reports.

## Proposed NASM diff sketch — NOT APPLIED

```diff
@@ emit_load_named_var .elnv_stack
 .elnv_stack:
-    mov dil, 0x48
-    call emit_byte
-    mov dil, 0x8B
-    call emit_byte
-    mov dil, 0x45
-    call emit_byte
-    mov edi, eax
-    call emit_byte
+    mov rsi, rax
+    mov edi, 0x8B
+    call emit_rbp_rax_mem
     ret
@@ emit_store_named_var .esnv_stack
 .esnv_stack:
-    mov dil, 0x48
-    call emit_byte
-    mov dil, 0x89
-    call emit_byte
-    mov dil, 0x45
-    call emit_byte
-    mov edi, eax
-    call emit_byte
+    mov rsi, rax
+    mov edi, 0x89
+    call emit_rbp_rax_mem
     ret
+
+; Input: EDI=0x8B for load, 0x89 for store; RSI=signed RBP displacement.
+emit_rbp_rax_mem:
+    push rbx
+    push r12
+    mov ebx, edi
+    mov r12, rsi
+    mov dil, 0x48
+    call emit_byte
+    mov edi, ebx
+    call emit_byte
+    cmp r12, -128
+    jl .wide
+    cmp r12, 127
+    jg .wide
+    mov dil, 0x45        ; ModRM disp8 form
+    call emit_byte
+    mov rdi, r12
+    call emit_byte       ; low signed 8 bits
+    jmp .done
+.wide:
+    mov dil, 0x85        ; ModRM disp32 form
+    call emit_byte
+    mov rdi, r12
+    call emit_u32        ; low signed 32 bits
+.done:
+    pop r12
+    pop rbx
+    ret
```

This diff intentionally illustrates **only the two named-variable routines**. Claude must apply the same disp-width selection to **every reachable** inline stack load/store listed above; check stack-depth bounds and signed disp32 range, and preserve caller-saved registers and existing global/register paths. Do not edit unrelated `0x45` instructions or regenerate golden outputs merely to conceal a failed test.

After patching, run `sh Claude-to-Sarvam/evidence-r9/F1/run-f1.sh ./sutram_compiler` and current `sh tools/gates.sh`, verify Linux and real Windows behavior, compare exact expected/observed stdout, and disassemble generated binaries. Existing tests F1a–F1e include incorrect caller slots, return-address crash, infinite loop and library-text corruption.

**Actual status:** read-only source analysis PASS; independent x86 displacement disassembly PASS; F1 compiler patch NOT_APPLIED by instruction; native Sutram compiler build/behavior NOT_RUN in this session.
