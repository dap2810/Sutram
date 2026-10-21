; ===================================================================
; ROUND-25: the error type, the smallest working version.
;
;   prati siddhi(v)    return success carrying v
;   prati dosh(c)      return failure carrying the code c
;   prasar f(...)      call f; on failure return that failure from here at
;                      once; on success the expression is f's value
;
; No heap, no new output format: a result travels in the call registers,
; the value (or the code) in rax and the status in rdx (0 = siddhi, 1 = dosh).
; A prakriya with a `prati siddhi` or `prati dosh` is a phal-prakriya. In one,
; every prati is siddhi or dosh, and falling off its end is siddhi(0). A call
; of a phal-prakriya must be under prasar, and prasar must be on a call of one,
; so a status is never read from a register that nobody set. prasar is
; allowed in a phal-prakriya (it propagates) and in mukhya (a failure ends the
; program with the code as its exit status).
; ===================================================================

section .bss
    r25_phal_names   resq R25_PHAL_CAP   ; every phal-prakriya, by name
    r25_phal_count   resq 1
    r25_parse_phal   resq 1              ; the prakriya being parsed has siddhi/dosh
    r25_cur_func     resq 1              ; name of the prakriya being generated (0 in mukhya)
    r25_prasar_pending resq 1            ; the next call generated is under prasar
section .text

; r25_mark_phal(rdi = name). Preserves every register.
r25_mark_phal:
    push rax
    push rcx
    mov rax, [rel r25_phal_count]
    cmp rax, R25_PHAL_CAP
    jae .full
    lea rcx, [rel r25_phal_names]
    mov [rcx + rax*8], rdi
    inc qword [rel r25_phal_count]
    pop rcx
    pop rax
    ret
.full:
    lea rdi, [rel msg_func_defs_overflow]
    jmp capacity_fail

; r25_is_phal(rdi = name) -> rax = 1 for a phal-prakriya. Preserves the rest.
r25_is_phal:
    push rbx
    push rcx
    push rdx
    push rsi
    push rdi
    push r12
    mov rbx, rdi
    xor eax, eax
    test rbx, rbx
    jz .out
    xor r12d, r12d
.l:
    cmp r12, [rel r25_phal_count]
    jae .no
    lea rdx, [rel r25_phal_names]
    mov rsi, [rdx + r12*8]
    mov rdi, rbx
    call strcmp
    test rax, rax
    jz .yes
    inc r12
    jmp .l
.yes:
    mov eax, 1
    jmp .out
.no:
    xor eax, eax
.out:
    pop r12
    pop rdi
    pop rsi
    pop rdx
    pop rcx
    pop rbx
    ret

; r25_check_call(rdi = callee name): at the start of every generated call.
; A phal-prakriya called without prasar, or prasar on anything else, is an
; error. Clears the prasar mark, so a call inside the arguments is judged on
; its own. Preserves every register.
r25_check_call:
    push rax
    push rcx
    mov rcx, [rel r25_prasar_pending]
    mov qword [rel r25_prasar_pending], 0
    call r23_call_is_indirect       ; through a variable: never a phal call
    test rax, rax
    jnz .not_phal
    call r25_is_phal
    test rax, rax
    jz .not_phal
    test rcx, rcx
    jz .unused
    pop rcx
    pop rax
    ret
.not_phal:
    test rcx, rcx
    jnz .not_a_phal_call
    pop rcx
    pop rax
    ret
.unused:
    lea rdi, [rel r25_msg_phal_unused]
    jmp capacity_fail
.not_a_phal_call:
    lea rdi, [rel r25_msg_prasar_call]
    jmp capacity_fail

; r25_check_plain_return(rbx = AST_RETURN): a plain `prati` in a phal-prakriya
; is an error. Preserves every register.
r25_check_plain_return:
    push rax
    push rdi
    cmp qword [rbx + 16], 0
    jne .ok                         ; siddhi or dosh
    cmp qword [rel in_function], 0
    je .ok                          ; mukhya
    mov rdi, [rel r25_cur_func]
    call r25_is_phal
    test rax, rax
    jnz .bad
.ok:
    pop rdi
    pop rax
    ret
.bad:
    lea rdi, [rel r25_msg_phal_return]
    jmp capacity_fail

; r25_emit_return_status(rbx = AST_RETURN), in a prakriya, after the value is in rax.
r25_emit_return_status:
    cmp qword [rbx + 16], 1
    je .siddhi
    cmp qword [rbx + 16], 2
    jne .done
    R23_EMIT 0xBA,0x01,0x00,0x00,0x00     ; mov edx, 1   dosh
    ret
.siddhi:
    R23_EMIT 0x31,0xD2                    ; xor edx, edx siddhi
.done:
    ret

; r25_emit_main_dosh(rbx = AST_RETURN), in mukhya: `prati dosh(c)` exits with c.
r25_emit_main_dosh:
    cmp qword [rbx + 16], 2
    jne .done
    call r25_emit_exit_rax
.done:
    ret

; r25_emit_exit_rax: exit(rax) - the status is the low byte of the code.
r25_emit_exit_rax:
    R23_EMIT 0x48,0x89,0xC7               ; mov rdi, rax
    R23_EMIT 0xB8,0x3C,0x00,0x00,0x00     ; mov eax, 60
    call emit_syscall
    ret

; r25_emit_fall_off: the end of a phal-prakriya's body is siddhi(0).
r25_emit_fall_off:
    push rdi
    mov rdi, [rel r25_cur_func]
    call r25_is_phal
    pop rdi
    test rax, rax
    jz .done
    R23_EMIT 0x31,0xC0,0x31,0xD2          ; xor eax,eax; xor edx,edx
.done:
    ret

; r25_gen_prasar(rbx = AST_PRASAR [type][call]): the call, then
;   test rdx, rdx / jz over / <return the failure> / over:
r25_gen_prasar:
    push r12
    cmp qword [rel in_function], 0
    je .where_ok                    ; mukhya: a failure ends the program
    mov rdi, [rel r25_cur_func]
    call r25_is_phal
    test rax, rax
    jz .where_bad
.where_ok:
    mov qword [rel r25_prasar_pending], 1
    mov rax, [rbx + 8]
    call gen_expr                   ; the call (r25_check_call consumes the mark)
    R23_EMIT 0x48,0x85,0xD2               ; test rdx, rdx
    R23_EMIT 0x74,0x00                    ; jz over (patched)
    mov r12, [rel code_sz]          ; end of the jz
    cmp qword [rel in_function], 0
    je .main
    ; return the failure as it is: rax = code, rdx = 1
    R23_EMIT 0x48,0x8D,0x65,0xF8,0x5B,0x5D,0xC3   ; lea rsp,[rbp-8]; pop rbx; pop rbp; ret
    jmp .patch
.main:
    call r25_emit_exit_rax
.patch:
    mov rax, [rel code_sz]
    sub rax, r12
    cmp rax, 127
    ja .too_far
    lea rcx, [rel code_buf]
    mov [rcx + r12 - 1], al
    pop r12
    ret
.too_far:
    lea rdi, [rel msg_code_overflow]
    jmp capacity_fail
.where_bad:
    lea rdi, [rel r25_msg_prasar_where]
    jmp capacity_fail

; ------------------------------------------------------------------- R26
; The handler: catch a failure and continue.
;
;   yadi dosh (q = f(...)) {      the call failed: q is the code
;       ...
;   } anya {                      it succeeded: q is the value
;       ...
;   }
;
; f must be a phal-prakriya. q is declared by the handler if it is new, and
; stays visible after it. The anya part is optional. Allowed anywhere: a
; handled failure goes no further.

; r26_parse_handler: the current token is `dosh` after `yadi`.
; -> rax = AST_HANDLE [type][name][call][fail block][ok block or 0]
r26_parse_handler:
    push rbx
    push r12
    push r13
    call advance_tok                ; dosh
    call cur_tok
    cmp qword [rax], TOK_DELIMITER
    jne parse_error
    cmp qword [rax + 8], '('
    jne parse_error
    call advance_tok
    call cur_tok
    cmp qword [rax], TOK_IDENT
    jne parse_error
    mov r12, [rax + 8]              ; the name
    call advance_tok
    call cur_tok
    cmp qword [rax], TOK_OPERATOR
    jne parse_error
    cmp qword [rax + 8], '='
    jne parse_error
    call advance_tok
    call parse_expr
    cmp qword [rax], AST_FUNCALL
    jne .not_call
    mov r13, rax                    ; the call
    call cur_tok
    cmp qword [rax], TOK_DELIMITER
    jne parse_error
    cmp qword [rax + 8], ')'
    jne parse_error
    call advance_tok
    mov rdi, r12                    ; a new name is declared here, in this scope
    call r4_is_seen
    test rax, rax
    jnz .seen
    mov rdi, r12
    call r4_declare
.seen:
    call parse_body                 ; the failure block
    push rax
    xor ebx, ebx                    ; no anya
    call cur_tok
    cmp qword [rax], TOK_KEYWORD
    jne .build
    cmp qword [rax + 16], KW_ANYATRA
    jne .build
    call advance_tok
    call parse_body                 ; the success block
    mov rbx, rax
.build:
    call alloc_ast
    pop rcx
    mov qword [rax], AST_HANDLE
    mov [rax + 8], r12
    mov [rax + 16], r13
    mov [rax + 24], rcx
    mov [rax + 32], rbx
    pop r13
    pop r12
    pop rbx
    ret
.not_call:
    lea rdi, [rel r26_msg_handle_call]
    jmp capacity_fail

; r26_emit_store_rax(rdi = name): the variable = rax. Writes only the variable.
r26_emit_store_rax:
    push rbx
    mov rbx, rdi
    call r56_global_index
    test rax, rax
    jz .local
    dec rax
    mov rdi, rax
    call r56_emit_global_store
    pop rbx
    ret
.local:
    mov rdi, rbx
    call lookup_var                 ; allocates it if it is new
    test rax, rax
    jle .stack
    mov rdi, rax
    call emit_store_reg
    pop rbx
    ret
.stack:
    push rax
    R23_EMIT 0x48,0x89              ; mov [rbp+disp], rax
    pop rax
    push rsi
    mov esi, eax
    mov dil, 0x45
    call emit_rbp_modrm_disp
    pop rsi
    pop rbx
    ret

; r26_gen_handle(rbx = AST_HANDLE)
r26_gen_handle:
    push r12
    push r13
    mov rax, [rbx + 16]
    mov rdi, [rax + 8]              ; the callee
    call r23_call_is_indirect
    test rax, rax
    jnz .not_phal
    mov rax, [rbx + 16]
    mov rdi, [rax + 8]
    call r25_is_phal
    test rax, rax
    jz .not_phal
    mov qword [rel r25_prasar_pending], 1   ; the call is handled here
    mov rax, [rbx + 16]
    call gen_expr                   ; rax = value or code, rdx = status
    mov rdi, [rbx + 8]
    call r26_emit_store_rax         ; q = rax (rdx is kept)
    R23_EMIT 0x48,0x85,0xD2         ; test rdx, rdx
    R23_EMIT 0x0F,0x84              ; jz success (patched)
    mov r12, [rel code_sz]
    xor edi, edi
    call emit_u32
    mov rax, [rbx + 24]
    call gen_block                  ; the failure block
    xor r13d, r13d
    cmp qword [rbx + 32], 0
    je .no_ok
    R23_EMIT 0xE9                   ; jmp end (patched)
    mov r13, [rel code_sz]
    xor edi, edi
    call emit_u32
.no_ok:
    mov rax, [rel code_sz]          ; success: here
    sub rax, r12
    sub rax, 4
    lea rcx, [rel code_buf]
    mov [rcx + r12], eax
    test r13, r13
    jz .done
    mov rax, [rbx + 32]
    call gen_block                  ; the success block
    mov rax, [rel code_sz]
    sub rax, r13
    sub rax, 4
    lea rcx, [rel code_buf]
    mov [rcx + r13], eax
.done:
    pop r13
    pop r12
    ret
.not_phal:
    lea rdi, [rel r26_msg_handle_call]
    jmp capacity_fail
