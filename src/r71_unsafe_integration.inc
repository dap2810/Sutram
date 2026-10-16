; Included only with SUTRAM_R71_UNSAFE_BOUNDARY, after the inherited compiler
; and R68 diagnostics. r71_after_lex is called immediately after lex.
section .data
r71_boundary_prefix:
    db "Sutram Error [E_UNSAFE_BOUNDARY]: ",0
r71_boundary_outside:
    db ": unchecked operation requires asurakshit { ... }",10,0
r71_boundary_structure:
    db ": malformed or unsupported asurakshit boundary",10,0
section .text
r71_after_lex:
    push rbx
    push r12
    push r13
    push r14
    push r15
    lea rdi,[rel token_arr]
    mov rsi,[rel token_cnt]
    mov edx,TOKEN_CAP
    call r71_check_unsafe
    test edx,edx
    jnz .fail
    mov [rel token_cnt],rax
    mov qword [rel token_idx],0
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret
.fail:
    ; Keep the first failing original token location. Count can be zero, or
    ; an unmatched open brace can fail at the end; use line 1/last token then.
    mov r8d,edx
    mov rsi,1
    mov rax,[rel token_cnt]
    test rax,rax
    jz .location_ready
    cmp rcx,rax
    jb .location_index
    lea rcx,[rax-1]
.location_index:
    imul rcx,rcx,40
    lea rax,[rel token_arr]
    mov rsi,[rax+rcx+24]
.location_ready:
    lea rdi,[rel r71_boundary_prefix]
    lea rdx,[rel r71_boundary_structure]
    cmp r8d,1
    jne .report
    lea rdx,[rel r71_boundary_outside]
.report:
    xor ecx,ecx
    call r68_report_error
    ud2
