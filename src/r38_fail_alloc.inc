; ===================================================================
; ROUND-38: an allocation-failure switch, for tests. Linux only.
;
;   sutram_compiler --fail-alloc N <in.sm> <out>
;
; The same compile as `sutram_compiler <in.sm> <out>`, except that in the program
; it writes, the Nth allocation made through the nirmmita sequence returns 0
; without calling mmap; every other allocation is made as usual. N counts from 1,
; in the order the program runs them, over every nirmmita the program reaches
; (a library's included). It is how a test reaches the "allocation failed" path
; of a library function, which no ordinary machine reaches on demand.
;
; How: the first allocation site emitted also emits a counter cell, N, inside the
; code (the program's one segment is read-write-execute) behind a short jump.
; Every site then runs
;       dec qword [rip -> cell]  ; jnz .alloc ; xor eax, eax ; jmp .done
;   .alloc: <the ordinary mmap sequence> .done:
; so the cell reaches 0 at the Nth allocation only, and goes on below 0 after it.
;
; Without the flag r38_fail_n is 0 and emit_nirmmita_from_rax emits exactly the
; bytes it emitted before: the ordinary compile is byte-identical.
; The flag is refused with --object/--separate/--ffi after it, with N = 0, with a
; non-decimal N, and with a .exe output.
; ===================================================================

section .bss
    r38_fail_n    resq 1        ; 0: no fault (the ordinary compile)
    r38_cell_set  resq 1
    r38_cell_off  resq 1        ; code offset of the counter cell
    r38_patch_at  resq 1

section .text
; r38_emit_faulty: rax (at run time) = the size; emitted instead of the plain sequence.
r38_emit_faulty:
    cmp qword [rel r38_cell_set], 0
    jne .have_cell
    mov dil, 0xEB                  ; jmp +8 over the cell
    call emit_byte
    mov dil, 0x08
    call emit_byte
    mov rax, [rel code_sz]
    mov [rel r38_cell_off], rax
    mov qword [rel r38_cell_set], 1
    mov rax, [rel r38_fail_n]
    call r38_emit_q
.have_cell:
    mov dil, 0x48                  ; dec qword [rip + disp32] = 48 FF 0D disp32
    call emit_byte
    mov dil, 0xFF
    call emit_byte
    mov dil, 0x0D
    call emit_byte
    mov rax, [rel r38_cell_off]
    sub rax, [rel code_sz]
    sub rax, 4                     ; relative to the end of the instruction
    call r38_emit_d
    mov dil, 0x75                  ; jnz +7 (xor eax,eax; jmp rel32)
    call emit_byte
    mov dil, 0x07
    call emit_byte
    mov dil, 0x31                  ; xor eax, eax
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    mov dil, 0xE9                  ; jmp .done, rel32 (patched below; R65: the arena sequence is ~196 bytes)
    call emit_byte
    mov rax, [rel code_sz]
    mov [rel r38_patch_at], rax
    xor edi, edi
    call emit_u32
    call r38_nirm_seq              ; the ordinary sequence
    mov rax, [rel code_sz]
    mov rcx, [rel r38_patch_at]
    sub rax, rcx
    sub rax, 4                     ; bytes after the rel32 field
    lea rdx, [rel code_buf]
    mov [rdx + rcx], eax
    ret

r38_emit_d:                        ; emit eax, low byte first
    push rbx
    mov rbx, rax
    mov ecx, 4
.d:
    push rcx
    mov dil, bl
    call emit_byte
    pop rcx
    shr rbx, 8
    dec ecx
    jnz .d
    pop rbx
    ret

r38_emit_q:                        ; emit rax, low byte first
    push rbx
    mov rbx, rax
    mov ecx, 8
.q:
    push rcx
    mov dil, bl
    call emit_byte
    pop rcx
    shr rbx, 8
    dec ecx
    jnz .q
    pop rbx
    ret
