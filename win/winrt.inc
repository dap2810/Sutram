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
    sub rsp, 40                ; Win64 16-byte alignment and shadow space
    ; Resolve modules by their Unicode basename, NEVER by ordinal position
    ; in PEB's loader chain. A no-import PE may have only ntdll loaded.
    lea rdi, [rel wn_kernel32_ascii]
    call win_find_module
    mov [rel p_win_kernel32], rax
    test rax, rax
    jnz .rt_kernel_ready
    lea rdi, [rel wn_ntdll_ascii]
    call win_find_module
    test rax, rax
    jz .rt_init_failed
    mov rsi, rax
    lea rdi, [rel wn_ldrloaddll]
    call win_resolve_from
    test rax, rax
    jz .rt_init_failed
    mov rbx, rax
    xor ecx, ecx                ; SearchPath = NULL
    xor edx, edx                ; DllCharacteristics = NULL
    lea r8, [rel wn_kernel32_us]
    lea r9, [rel p_win_kernel32]
    call rbx
    test eax, eax               ; signed NTSTATUS, negative indicates failure
    js .rt_init_failed
.rt_kernel_ready:
    cmp qword [rel p_win_kernel32], 0
    je .rt_init_failed
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
    add rsp, 40
    pop rbx
    ret
.rt_init_failed:
    ; Return to startup without usable WinAPI pointers. A later diagnostic
    ; guard in _start reports this failure via the normal Windows exit path.
    add rsp, 40
    pop rbx
    ret

; --- os_write(rdi=fd, rsi=buf, rdx=len) ------------------------------------
os_write:
    push rbx
    push r12
    push r13
    mov rbx, rsp
    and rsp, -16               ; WinAPI calls require 16-byte aligned RSP
    sub rsp, 48                ; 32-byte shadow + 5th argument
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
    mov rsp, rbx
    pop r13
    pop r12
    pop rbx
    ret

; --- os_read(rdi=fd, rsi=buf, rdx=len) -> rax = bytes read -----------------
os_read:
    push rbx
    push r12
    push r13
    mov rbx, rsp
    and rsp, -16
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
    mov rsp, rbx
    pop r13
    pop r12
    pop rbx
    ret

; --- os_open(rdi=path, rsi=flags, rdx=mode) -> rax = handle (-1 on error) --
os_open:
    push rbx
    push r14
    mov r14, rsp
    and rsp, -16
    sub rsp, 64                ; 32 shadow + 3 stack arguments, aligned
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
    mov rsp, r14
    pop r14
    pop rbx
    ret

; --- os_close(rdi=handle) --------------------------------------------------
os_close:
    push rbx
    mov rbx, rsp
    and rsp, -16
    sub rsp, 32
    mov rcx, rdi
    call qword [rel p_closehandle]
    mov rsp, rbx
    pop rbx
    ret

; --- os_exit(rdi=code) -----------------------------------------------------
os_exit:
    and rsp, -16
    sub rsp, 32
    mov rcx, rdi
    call qword [rel p_exitprocess]
    hlt

; --- win_build_argv: parse GetCommandLineA into a stack-like argv[] ---------
; The compiler reads argc/argv from the stack (Linux layout). We build an
; equivalent array and point orig_rsp at it, so the rest of the code works.
win_build_argv:
    push rbx
    push r12
    push r13
    push r14
    push r15
    sub rsp, 40                ; Win64 shadow and alignment
    call qword [rel p_cmdline]
    add rsp, 40
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

; --- win_find_module(rdi = lower-case ASCII DLL name) ---
; Walk InMemoryOrderModuleList and compare exact Unicode BaseDllName. This
; avoids guessing the number/order of loader modules on Windows versions.
win_find_module:
    push rbx
    push r12
    push r13
    push r14
    push r15
    mov rbx, rdi
    mov rax, [gs:0x60]
    test rax, rax
    jz .fm_fail
    mov rax, [rax+0x18]
    test rax, rax
    jz .fm_fail
    lea r12, [rax+0x20]      ; InMemoryOrderModuleList head
    mov r13, [r12]           ; first InMemoryOrderLinks
    mov r15d, 64             ; hard traversal bound
.fm_next:
    test r15, r15
    jz .fm_fail
    dec r15
    cmp r13, r12
    je .fm_fail
    test r13, r13
    jz .fm_fail
    mov r14, [r13+0x50]     ; BaseDllName.Buffer from InMemoryOrderLinks
    test r14, r14
    jz .fm_advance
    xor ecx, ecx
.fm_cmp:
    movzx edx, byte [rbx+rcx]
    movzx eax, word [r14+rcx*2]
    cmp edx, 'A'
    jb .fm_folded
    cmp edx, 'Z'
    ja .fm_folded
    or edx, 0x20
.fm_folded:
    cmp eax, 'A'
    jb .fm_check
    cmp eax, 'Z'
    ja .fm_check
    or eax, 0x20
.fm_check:
    cmp eax, edx
    jne .fm_advance
    test edx, edx
    jz .fm_found
    inc rcx
    cmp rcx, 60
    jb .fm_cmp
.fm_advance:
    mov r13, [r13]          ; LIST_ENTRY.Flink
    jmp .fm_next
.fm_found:
    mov rax, [r13+0x20]    ; DllBase from InMemoryOrderLinks
    jmp .fm_done
.fm_fail:
    xor eax, eax
.fm_done:
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

; --- win_kernel32: already loaded or loaded through ntdll ---
win_kernel32:
    mov rax, [rel p_win_kernel32]
    ret

; --- win_resolve(rdi=name) -> rax = address --------------------------------
win_resolve:
    mov rsi, [rel p_win_kernel32]
    jmp win_resolve_from

; win_resolve_from(rdi=ASCII export, rsi=module base)
win_resolve_from:
    push rbx
    push r12
    push r13
    push r14
    push r15
    mov r14, rdi
    mov rax, rsi
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
wn_ntdll_ascii:   db "ntdll.dll", 0
wn_kernel32_ascii: db "kernel32.dll", 0
wn_ldrloaddll:   db "LdrLoadDll", 0
; Unicode string "kernel32.dll" for ntdll loader (length excludes zero).
wn_kernel32_chars: dw 'k','e','r','n','e','l','3','2','.','d','l','l',0
align 8
wn_kernel32_us:    dw 24,26
                   dd 0
                   dq wn_kernel32_chars
wn_getstd:       db "GetStdHandle", 0
wn_writefile:    db "WriteFile", 0
wn_readfile:     db "ReadFile", 0
wn_createfile:   db "CreateFileA", 0
wn_closehandle:  db "CloseHandle", 0
wn_virtualalloc: db "VirtualAlloc", 0
wn_exitprocess:  db "ExitProcess", 0
wn_cmdline:      db "GetCommandLineA", 0

section .bss
p_win_kernel32:  resq 1
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
