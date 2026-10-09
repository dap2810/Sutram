; ---------------------------------------------------------------------------
; winrt.inc — Windows implementation of the Sutram OS layer
;
; Included by the compiler when built with:  nasm -f win64 -dWINDOWS
; Provides os_write / os_read / os_open / os_close / os_exit / os_readlink
; on top of kernel32, located at runtime through the PEB (no import library).
;
; Call rt_init once at startup before any I/O.
; ---------------------------------------------------------------------------

section .text

; --- rt_init: resolve the kernel32 functions we need -----------------------
rt_init:
    push rbx
    sub rsp, 32
    lea rdi, [rel wn_getstd]
    call win_resolve
    mov [rel p_getstd], rax
    lea rdi, [rel wn_writefile]
    call win_resolve
    mov [rel p_writefile], rax
    lea rdi, [rel wn_readfile]
    call win_resolve
    mov [rel p_readfile], rax
    lea rdi, [rel wn_createfile]
    call win_resolve
    mov [rel p_createfile], rax
    lea rdi, [rel wn_closehandle]
    call win_resolve
    mov [rel p_closehandle], rax
    lea rdi, [rel wn_virtualalloc]
    call win_resolve
    mov [rel p_virtualalloc], rax
    lea rdi, [rel wn_exitprocess]
    call win_resolve
    mov [rel p_exitprocess], rax
    lea rdi, [rel wn_cmdline]
    call win_resolve
    mov [rel p_cmdline], rax
    add rsp, 32
    pop rbx
    ret

; --- os_write(rdi=fd, rsi=buf, rdx=len) ------------------------------------
os_write:
    push rbx
    push r12
    push r13
    sub rsp, 48
    mov r12, rsi
    mov r13, rdx
    mov rcx, -11                 ; STD_OUTPUT_HANDLE
    cmp rdi, 2
    jne .ow_go
    mov rcx, -12                 ; STD_ERROR_HANDLE
.ow_go:
    call qword [rel p_getstd]
    mov rcx, rax
    mov rdx, r12
    mov r8, r13
    lea r9, [rel wn_written]
    mov qword [rsp+32], 0
    call qword [rel p_writefile]
    add rsp, 48
    pop r13
    pop r12
    pop rbx
    ret

; --- os_read(rdi=fd, rsi=buf, rdx=len) -> rax = bytes read -----------------
os_read:
    push rbx
    push r12
    push r13
    sub rsp, 48
    mov r12, rsi
    mov r13, rdx
    mov rcx, -10                 ; STD_INPUT_HANDLE
    call qword [rel p_getstd]
    mov rcx, rax
    mov rdx, r12
    mov r8, r13
    lea r9, [rel wn_got]
    mov qword [rsp+32], 0
    call qword [rel p_readfile]
    mov eax, [rel wn_got]
    add rsp, 48
    pop r13
    pop r12
    pop rbx
    ret

; --- os_open(rdi=path, rsi=flags, rdx=mode) -> rax = handle (-1 on error) --
os_open:
    push rbx
    sub rsp, 48
    mov rbx, rdi                 ; path
    mov rdx, 0x80000000          ; GENERIC_READ
    mov r8, 1                    ; FILE_SHARE_READ
    xor r9, r9
    mov qword [rsp+32], 3        ; OPEN_EXISTING
    mov qword [rsp+40], 0
    test rsi, rsi
    jz .oo_go
    mov rdx, 0x40000000          ; GENERIC_WRITE
    mov qword [rsp+32], 2        ; CREATE_ALWAYS
.oo_go:
    mov rcx, rbx
    call qword [rel p_createfile]
    cmp rax, -1
    jne .oo_done
    mov rax, -1
.oo_done:
    add rsp, 48
    pop rbx
    ret

; --- os_close(rdi=handle) --------------------------------------------------
os_close:
    sub rsp, 40
    mov rcx, rdi
    call qword [rel p_closehandle]
    add rsp, 40
    ret

; --- os_exit(rdi=code) -----------------------------------------------------
os_exit:
    sub rsp, 40
    mov rcx, rdi
    call qword [rel p_exitprocess]
    add rsp, 40
    ret

; --- win_build_argv: parse GetCommandLineA into a stack-like argv[] ---------
; The compiler reads argc/argv from the stack (Linux layout). We build an
; equivalent array and point orig_rsp at it, so the rest of the code works.
win_build_argv:
    push rbx
    push r12
    push r13
    push r14
    push r15
    call qword [rel p_cmdline]
    test rax, rax
    jz .ba_done
    mov r12, rax                     ; r12 = source
    lea r13, [rel win_args]          ; token storage
    lea r14, [rel win_stack]         ; argv array (slot 0 = argc)
    xor r15, r15                     ; argc
.ba_skip:
    mov al, [r12]
    test al, al
    jz .ba_finish
    cmp al, ' '
    je .ba_adv
    cmp al, 9
    je .ba_adv
    mov [r14 + 8 + r15*8], r13       ; argv[argc] = this token
    inc r15
.ba_tok:
    mov al, [r12]
    test al, al
    jz .ba_end
    cmp al, ' '
    je .ba_end
    cmp al, 9
    je .ba_end
    cmp al, '"'
    je .ba_open
    mov [r13], al
    inc r13
    inc r12
    jmp .ba_tok
.ba_open:
    inc r12                          ; skip opening quote
.ba_qloop:
    mov al, [r12]
    test al, al
    jz .ba_end
    cmp al, '"'
    je .ba_qend
    mov [r13], al
    inc r13
    inc r12
    jmp .ba_qloop
.ba_qend:
    inc r12                          ; skip closing quote
    jmp .ba_tok
.ba_end:
    mov byte [r13], 0
    inc r13
    jmp .ba_skip
.ba_adv:
    inc r12
    jmp .ba_skip
.ba_finish:
    mov [r14], r15                   ; argc
.ba_done:
    lea rax, [rel win_stack]
    mov [rel orig_rsp], rax
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

; --- os_readlink: not supported on Windows (REPL self-path only) -----------
os_readlink:
    mov rax, -1
    ret

; --- win_kernel32: kernel32 base via PEB walk ------------------------------
win_kernel32:
    mov rax, [gs:0x60]
    test rax, rax
    jz .k_fail
    mov rax, [rax+0x18]
    test rax, rax
    jz .k_fail
    mov rax, [rax+0x20]
    test rax, rax
    jz .k_fail
    mov rax, [rax]
    test rax, rax
    jz .k_fail
    mov rax, [rax]
    test rax, rax
    jz .k_fail
    mov rax, [rax+0x20]
    ret
.k_fail:
    xor rax, rax
    ret

; --- win_resolve(rdi=name) -> rax = address --------------------------------
win_resolve:
    push rbx
    push r12
    push r13
    push r14
    push r15
    mov r14, rdi
    call win_kernel32
    test rax, rax
    jz .r_fail
    mov rbx, rax
    mov eax, [rbx+0x3C]
    add rax, rbx
    mov r12d, [rax+24+0x70]
    test r12d, r12d
    jz .r_fail
    add r12, rbx
    mov r13d, [r12+0x20]
    add r13, rbx
    mov r15d, [r12+0x18]
    test r15d, r15d
    jz .r_fail
    xor rcx, rcx
.r_loop:
    cmp rcx, r15
    jae .r_fail
    mov eax, [r13 + rcx*4]
    add rax, rbx
    push rcx
    push rax
    mov rsi, rax
    mov rdi, r14
.r_cmp:
    mov al, [rsi]
    mov dl, [rdi]
    cmp al, dl
    jne .r_next
    test al, al
    jz .r_found
    inc rsi
    inc rdi
    jmp .r_cmp
.r_next:
    pop rax
    pop rcx
    inc rcx
    jmp .r_loop
.r_found:
    pop rax
    pop rcx
    mov r13d, [r12+0x24]
    add r13, rbx
    movzx ecx, word [r13 + rcx*2]
    mov r13d, [r12+0x1C]
    add r13, rbx
    mov eax, [r13 + rcx*4]
    add rax, rbx
    jmp .r_done
.r_fail:
    xor rax, rax
.r_done:
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

section .data
wn_getstd:       db "GetStdHandle", 0
wn_writefile:    db "WriteFile", 0
wn_readfile:     db "ReadFile", 0
wn_createfile:   db "CreateFileA", 0
wn_closehandle:  db "CloseHandle", 0
wn_virtualalloc: db "VirtualAlloc", 0
wn_exitprocess:  db "ExitProcess", 0
wn_cmdline:      db "GetCommandLineA", 0

section .bss
p_getstd:       resq 1
p_writefile:    resq 1
p_readfile:     resq 1
p_createfile:   resq 1
p_closehandle:  resq 1
p_virtualalloc: resq 1
p_exitprocess:  resq 1
wn_written:     resd 1
wn_got:         resd 1
p_cmdline:      resq 1
win_args:       resb 2048
win_stack:      resq 16
