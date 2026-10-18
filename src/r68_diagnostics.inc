; R68 compiler-host diagnostics. Does not emit instructions into user programs.
; Wrapper invokes prelex before lex and value guard before parse_primary.
; Source path is root compilation input; after imports, line is EXPANDED line.
; No claim of original imported-file provenance. UTF-8 strings/comments retain
; their old byte semantics; validation applies to source CODE only.
section .data
r68_utf8_prefix:
    db "Sutram Error [E_UTF8]: ",0
r68_utf8_tail:
    db ": srot me ashuddh ya khandit UTF-8",10,0
r68_value_prefix:
    db "Sutram Error [E_ABBREVIATION_VALUE]: ",0
r68_value_tail:
    db ": sankshep shabd mulya nahi: '",0
r68_quote_lf:
    db 39,10,0
r68_colon:
    db ":",0
section .text
r68_prelex_validate:
    push rbx
    push r12
    push r13
    push r14
    push r15
    xor ebx,ebx              ; 0 code, 1 line comment, 2 block, 3 quoted string
    mov r12d,1
    lea r13,[rel source_buf]
    mov r14,[rel source_len]
    add r14,r13
.loop:
    cmp r13,r14
    jae .done
    movzx eax,byte [r13]
    cmp eax,10
    jne .state
    inc r12
    cmp ebx,1
    jne .step
    xor ebx,ebx
    jmp .step
.state:
    cmp ebx,1
    je .step
    cmp ebx,2
    je .block
    cmp ebx,3
    je .string
    cmp eax,35
    je .line_comment
    cmp eax,34
    je .start_string
    cmp eax,47
    jne .code
    lea rax,[r13+1]
    cmp rax,r14
    jae .code
    cmp byte [rax],47
    je .line_comment
    cmp byte [rax],42
    jne .code
    mov ebx,2
    add r13,2
    jmp .loop
.line_comment:
    mov ebx,1
    jmp .step
.start_string:
    mov ebx,3
    jmp .step
.string:
    cmp eax,34
    jne .escape
    xor ebx,ebx
    jmp .step
.escape:
    cmp eax,92
    jne .step
    inc r13
    cmp r13,r14
    jae .done
    cmp byte [r13],10
    jne .step
    inc r12
    jmp .step
.block:
    cmp eax,42
    jne .step
    lea rax,[r13+1]
    cmp rax,r14
    jae .step
    cmp byte [rax],47
    jne .step
    xor ebx,ebx
    add r13,2
    jmp .loop
.code:
    mov rdi,r13
    mov rsi,r14
    call r68_utf8_width
    test eax,eax
    jz .bad
    add r13,rax
    jmp .loop
.step:
    inc r13
    jmp .loop
.bad:
    lea rdi,[rel r68_utf8_prefix]
    mov rsi,r12
    lea rdx,[rel r68_utf8_tail]
    xor ecx,ecx
    call r68_report_error
    ud2
.done:
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

r68_guard_value_start:
    ; Preserve ALL registers formerly supplied to parse_primary.
    push rax
    push rcx
    push rdx
    push rsi
    push rdi
    push r8
    push r9
    push r10
    push r11
    push rbx
    push r12
    call cur_tok
    cmp qword [rax],TOK_KEYWORD
    jne .done
    cmp qword [rax+16],KW_PURNA
    je .done
    cmp qword [rax+16],KW_SHUNYA
    je .done
    mov rbx,rax
    mov rdi,[rbx+8]
    call strlen
    mov rdi,[rbx+8]
    lea rsi,[rdi+rax]
    call r68_ends_abbreviation
    test eax,eax
    jz .done
    lea rdi,[rel r68_value_prefix]
    mov rsi,[rbx+24]           ; actual token line, NOT final lexer cur_line
    lea rdx,[rel r68_value_tail]
    mov rcx,[rbx+8]
    call r68_report_error
    ud2
.done:
    pop r12
    pop rbx
    pop r11
    pop r10
    pop r9
    pop r8
    pop rdi
    pop rsi
    pop rdx
    pop rcx
    pop rax
    ret

r68_report_error:
    ; RDI=prefix, RSI=line, RDX=tail, RCX=optional alias. Always exits 1.
    ; Called only by fatal branches, where caller frames need not unwind.
    push rbx
    push r12
    push r13
    push r14
    push r15
    mov r12,rdi
    mov r13,rsi
    mov r14,rdx
    mov r15,rcx
    mov rdi,r12
    call print_str_z
    mov rdi,[rel source_path_ptr]
    call print_str_z
    lea rdi,[rel r68_colon]
    call print_str_z
    mov rdi,r13
    call r68_print_line_number
    mov rdi,r14
    call print_str_z
    test r15,r15
    jz .exit
    mov rdi,r15
    call print_str_z
    lea rdi,[rel r68_quote_lf]
    call print_str_z
.exit:
    mov edi,1
    call os_exit
    ud2                       ; fail closed if a broken OS exit shim returns

r68_print_line_number:
    push rbx
    sub rsp,32
    mov rax,rdi
    lea rbx,[rsp+32]
    mov r10d,10
.digit:
    xor edx,edx
    div r10
    add dl,48
    dec rbx
    mov [rbx],dl
    test rax,rax
    jnz .digit
    mov edi,1
    mov rsi,rbx
    lea rdx,[rsp+32]
    sub rdx,rbx
    call os_write
    add rsp,32
    pop rbx
    ret
