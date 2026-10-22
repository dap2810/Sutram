; ===================================================================
; ROUND-39: nirmmita_gun(count, size) - a checked allocation.
;
;   vitti a = nirmmita_gun(n, 8)      ; n cells, or 0
;
; The library's allocations multiply a count by an element size and then call
; nirmmita; every one of them needs a bound on the count first, or the product
; wraps to a small size and the caller writes past it (R35-R37). Two checkers
; look for those bounds. nirmmita_gun puts the multiply in the emitted code,
; next to the allocation, and checks it there:
;
;   count < 0                  -> 0
;   size <= 0                  -> 0
;   count * size > 2^63 - 1    -> 0   (imul's overflow flag)
;   otherwise                  -> nirmmita(count * size)
;
; so a wrapped size never reaches mmap, whatever the caller passed, and no
; bound is needed. count 0 gives nirmmita(0), which is 0, as before.
;
; At run time rcx = count and rax = size when this sequence starts:
;       test rcx, rcx ; js  .zero
;       test rax, rax ; jle .zero
;       imul rax, rcx ; jo  .zero
;       <the ordinary nirmmita sequence: emit_nirmmita_from_rax>
;       jmp .done
;   .zero: xor eax, eax
;   .done:
; The three forward jumps are patched once the allocation sequence's length is
; known (it differs on Windows and under --fail-alloc). The ordinary compile of a
; program that does not call nirmmita_gun is unchanged.
; ===================================================================

section .bss
    r39_fix1 resq 1
    r39_fix2 resq 1
    r39_fix3 resq 1

section .text
r39_emit_nirmgun:
    mov dil, 0x48               ; test rcx, rcx = 48 85 C9
    call emit_byte
    mov dil, 0x85
    call emit_byte
    mov dil, 0xC9
    call emit_byte
    mov dil, 0x78               ; js rel8
    call emit_byte
    mov rax, [rel code_sz]
    mov [rel r39_fix1], rax
    xor edi, edi
    call emit_byte
    mov dil, 0x48               ; test rax, rax = 48 85 C0
    call emit_byte
    mov dil, 0x85
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    mov dil, 0x7E               ; jle rel8
    call emit_byte
    mov rax, [rel code_sz]
    mov [rel r39_fix2], rax
    xor edi, edi
    call emit_byte
    mov dil, 0x48               ; imul rax, rcx = 48 0F AF C1
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0xAF
    call emit_byte
    mov dil, 0xC1
    call emit_byte
    mov dil, 0x70               ; jo rel8
    call emit_byte
    mov rax, [rel code_sz]
    mov [rel r39_fix3], rax
    xor edi, edi
    call emit_byte
    call emit_nirmmita_from_rax ; rax = count * size
    mov dil, 0xEB               ; jmp .done (+2)
    call emit_byte
    mov dil, 0x02
    call emit_byte
    ; .zero is here: patch the three rel8 fields to land on it
    mov rax, [rel code_sz]
    lea rdx, [rel code_buf]
    mov rcx, [rel r39_fix1]
    mov r8, rax
    sub r8, rcx
    dec r8
    cmp r8, 127
    ja .too_far
    mov [rdx + rcx], r8b
    mov rcx, [rel r39_fix2]
    mov r8, rax
    sub r8, rcx
    dec r8
    mov [rdx + rcx], r8b
    mov rcx, [rel r39_fix3]
    mov r8, rax
    sub r8, rcx
    dec r8
    mov [rdx + rcx], r8b
    mov dil, 0x31               ; .zero: xor eax, eax
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    ret                         ; .done
.too_far:
    ; cannot happen: the allocation sequence is under 100 bytes on every target
    ud2
