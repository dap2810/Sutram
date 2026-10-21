; R71 revised WS2: Linux x86-64 kosh growth reclamation.
; This is staged into the ONE existing compiler by r71_reclaim_prepare.py.
; Not a second compiler, public free builtin, or whole-language safety guarantee.
; GNU-as conversion in the tests applies ONLY to marked runtime payloads.
section .text

r71_emit_kosh_growth_guard:
    lea rdi,[rel r71_growth_guard_begin]
    lea rsi,[rel r71_growth_guard_end]
    jmp r71_emit_kosh_payload
r71_emit_kosh_allocation_guard:
    lea rdi,[rel r71_allocation_guard_begin]
    lea rsi,[rel r71_allocation_guard_end]
    jmp r71_emit_kosh_payload
r71_emit_kosh_reclaim:
    lea rdi,[rel r71_reclaim_begin]
    lea rsi,[rel r71_reclaim_end]
r71_emit_kosh_payload:
    ; Compiler-host code. Never embed a raw Linux syscall in generated PE.
    cmp qword [rel target_pe],0
    jne .unsupported_target
%ifdef SUTRAM_R71_KEEP_OLD_KOSH
    ; Explicit A/B-only legacy profile. No new instructions are emitted.
    ret
%else
    push rbx
    push r12
    mov rbx,rdi
    mov r12,rsi
.copy:
    cmp rbx,r12
    jae .done
    mov dil,[rbx]
    call emit_byte
    inc rbx
    jmp .copy
.done:
    pop r12
    pop rbx
    ret
%endif
.unsupported_target:
    lea rdi,[rel r71_reclaim_target_error]
    jmp capacity_fail
r71_reclaim_target_error:
    db "Sutram Error [E_KOSH_RECLAIM_TARGET]: reclamation profile requires Linux ELF output",10,0

; BEGIN PAYLOAD growth_guard
r71_growth_guard_begin:
    ; Runtime: R8=old user pointer, R9=len, R10=cap. Growth requires len==cap.
    ; (2*cap + 2)*8 must fit positive signed size before arithmetic/mmap.
    push rax
    cmp r9,r10
    jne .bad
    mov rax,0x07fffffffffffffe
    cmp r10,rax
    ja .bad
    pop rax
    jmp .end
.bad:
    mov eax,1
    mov edi,2
    lea rsi,[rel .message]
    mov edx,.message_end-.message
    syscall
    mov eax,60
    mov edi,1
    syscall
    ud2
.message:
    db "Sutram Error [E_KOSH_CAPACITY]: invalid length or growth capacity",10
.message_end:
.end:
r71_growth_guard_end:
; END PAYLOAD growth_guard

; BEGIN PAYLOAD allocation_guard
r71_allocation_guard_begin:
    ; Runtime RAX is mmap's raw return, not libc's errno-normalized return.
    ; Both raw -errno [-4095,-1] and null fail before header/copy/free.
    cmp rax,-4095
    jae .bad
    test rax,rax
    jz .bad
    jmp .end
.bad:
    mov eax,1
    mov edi,2
    lea rsi,[rel .message]
    mov edx,.message_end-.message
    syscall
    mov eax,60
    mov edi,1
    syscall
    ud2
.message:
    db "Sutram Error [E_KOSH_ALLOC]: growth allocation failed",10
.message_end:
.end:
r71_allocation_guard_end:
; END PAYLOAD allocation_guard

; BEGIN PAYLOAD reclaim
r71_reclaim_begin:
    ; Called ONLY after successful allocation, copy, and publishing new pointer.
    ; Runtime: R8=OLD user pointer, R9=len, R10=NEW user pointer, RAX=new pointer.
    ; Read old header before unmapping; original mmap base is old user - 16.
    ; munmap length is old capacity*8+16; Linux rounds length up to pages.
    ; Preserve RAX, RCX/R11 (syscall clobbers), RDI/RSI (arguments), stack depth.
    push rax
    push rcx
    push rdi
    push rsi
    push r11
    lea rdi,[r8-16]
    mov rsi,[r8-8]
    lea rsi,[rsi*8+16]
    mov eax,11
    syscall
    test rax,rax
    jnz .bad
    pop r11
    pop rsi
    pop rdi
    pop rcx
    pop rax
    jmp .end
.bad:
    ; A release failure must not silently turn back into an accepted leak.
    mov eax,1
    mov edi,2
    lea rsi,[rel .message]
    mov edx,.message_end-.message
    syscall
    mov eax,60
    mov edi,1
    syscall
    ud2
.message:
    db "Sutram Error [E_KOSH_RECLAIM]: old-buffer release failed",10
.message_end:
.end:
r71_reclaim_end:
; END PAYLOAD reclaim
