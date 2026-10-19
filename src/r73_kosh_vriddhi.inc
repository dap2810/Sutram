; R73 current-main port: Linux x86-64 kosh growth reclamation.
; This is staged into the ONE existing compiler by Round 73 opt-in core.
; Not a second compiler, public free builtin, or whole-language safety guarantee.
; GNU-as conversion in the tests applies ONLY to marked runtime payloads.
section .text

r73_kosh_vriddhi_raksha:
    lea rdi,[rel r73_vriddhi_adi]
    lea rsi,[rel r73_vriddhi_anta]
    jmp r73_kosh_ankit
r73_kosh_viniyog_raksha:
    lea rdi,[rel r73_viniyog_adi]
    lea rsi,[rel r73_viniyog_anta]
    jmp r73_kosh_ankit
r73_kosh_mukti:
    lea rdi,[rel r73_mukti_adi]
    lea rsi,[rel r73_mukti_anta]
r73_kosh_ankit:
    ; Compiler-host code. Never embed a raw Linux syscall in generated PE.
    cmp qword [rel target_pe],0
    jne .unsupported_target
%ifdef SUTRAM_R73_KOSH_PRACHIN
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
    lea rdi,[rel r73_kosh_lakshya_dosh]
    jmp capacity_fail
r73_kosh_lakshya_dosh:
    db "Sutram Error [E_KOSH_RECLAIM_TARGET]: kosh mukti ke liye Linux ELF avashyak",10,0

; BEGIN PAYLOAD growth_guard
r73_vriddhi_adi:
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
    db "Sutram Error [E_KOSH_CAPACITY]: kosh vriddhi parimana dosh",10
.message_end:
.end:
r73_vriddhi_anta:
; END PAYLOAD growth_guard

; BEGIN PAYLOAD allocation_guard
r73_viniyog_adi:
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
    db "Sutram Error [E_KOSH_ALLOC]: kosh vriddhi viniyog asafal",10
.message_end:
.end:
r73_viniyog_anta:
; END PAYLOAD allocation_guard

; BEGIN PAYLOAD reclaim
r73_mukti_adi:
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
    db "Sutram Error [E_KOSH_RECLAIM]: purana kosh smriti mukti asafal",10
.message_end:
.end:
r73_mukti_anta:
; END PAYLOAD reclaim
