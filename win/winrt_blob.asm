; ---------------------------------------------------------------------------
; winrt_blob.asm — runtime embedded in every Windows program Sutram emits
;
; Assembled as a FLAT binary (nasm -f bin) so its bytes are copied verbatim
; into the generated executable. Everything is rip-relative, so it is
; position independent.
;
; Provides:
;   rt_init     — resolve kernel32, cache std handles (call once at start)
;   rt_syscall  — emulates the Linux syscall ABI on Windows:
;                   rax=0  read(fd,buf,len)   -> ReadFile
;                   rax=1  write(fd,buf,len)  -> WriteFile
;                   rax=3  close(fd)          -> CloseHandle
;                   rax=9  mmap(addr,len,..)  -> VirtualAlloc
;                   rax=60 exit(code)         -> ExitProcess
;                 args in rdi/rsi/rdx, result in rax. Preserves every
;                 register a Linux syscall preserves (only rcx/r11 clobbered).
;
; Build:  nasm -f bin win/winrt_blob.asm -o rtblob.bin
; ---------------------------------------------------------------------------

bits 64
default rel

; ---------------------------------------------------------------------------
rt_init:
    push rbx
    sub rsp, 32
    lea rdi, [rel nm_getstd]
    call rt_resolve
    mov [rel p_getstd], rax
    lea rdi, [rel nm_write]
    call rt_resolve
    mov [rel p_write], rax
    lea rdi, [rel nm_read]
    call rt_resolve
    mov [rel p_read], rax
    lea rdi, [rel nm_close]
    call rt_resolve
    mov [rel p_close], rax
    lea rdi, [rel nm_alloc]
    call rt_resolve
    mov [rel p_alloc], rax
    lea rdi, [rel nm_exit]
    call rt_resolve
    mov [rel p_exit], rax
    mov rcx, -11                 ; STD_OUTPUT_HANDLE
    call qword [rel p_getstd]
    mov [rel h_out], rax
    mov rcx, -12                 ; STD_ERROR_HANDLE
    call qword [rel p_getstd]
    mov [rel h_err], rax
    mov rcx, -10                 ; STD_INPUT_HANDLE
    call qword [rel p_getstd]
    mov [rel h_in], rax
    add rsp, 32
    pop rbx
    ret

; ---------------------------------------------------------------------------
rt_syscall:
    push rbx
    push rbp
    push rsi
    push rdi
    push rdx
    push r8
    push r9
    push r10
    push r11
    push r12
    push r13
    push r14
    push r15
    mov r12, rax                 ; syscall number
    mov r13, rdi                 ; arg0
    mov r14, rsi                 ; arg1
    mov r15, rdx                 ; arg2
    mov rbp, rsp                 ; remember stack (after pushes)
    and rsp, -16                 ; 16-byte align for Win64 calls
    sub rsp, 48                  ; shadow space + 5th arg slot
    cmp r12, 1
    je .sc_write
    cmp r12, 0
    je .sc_read
    cmp r12, 60
    je .sc_exit
    cmp r12, 9
    je .sc_mmap
    cmp r12, 3
    je .sc_close
    xor rax, rax
    jmp .sc_done

.sc_write:
    mov rcx, r13
    cmp rcx, 2
    jne .w_out
    mov rcx, [rel h_err]
    jmp .w_go
.w_out:
    cmp rcx, 1
    jne .w_go
    mov rcx, [rel h_out]
.w_go:
    mov rdx, r14
    mov r8, r15
    lea r9, [rel nwritten]
    mov qword [rsp+32], 0
    call qword [rel p_write]
    mov eax, [rel nwritten]
    jmp .sc_done

.sc_read:
    mov rcx, [rel h_in]
    mov rdx, r14
    mov r8, r15
    lea r9, [rel ngot]
    mov qword [rsp+32], 0
    call qword [rel p_read]
    mov eax, [rel ngot]
    jmp .sc_done

.sc_exit:
    mov rcx, r13
    call qword [rel p_exit]
    xor rax, rax
    jmp .sc_done

.sc_mmap:
    mov rcx, 0                   ; lpAddress = NULL
    mov rdx, r14                 ; length
    mov r8, 0x3000               ; MEM_COMMIT | MEM_RESERVE
    mov r9, 0x04                 ; PAGE_READWRITE
    call qword [rel p_alloc]
    jmp .sc_done

.sc_close:
    mov rcx, r13
    call qword [rel p_close]
    xor rax, rax
    jmp .sc_done

.sc_done:
    mov rsp, rbp                 ; undo alignment + shadow space
    pop r15
    pop r14
    pop r13
    pop r12
    pop r11
    pop r10
    pop r9
    pop r8
    pop rdx
    pop rdi
    pop rsi
    pop rbp
    pop rbx
    ret

; ---------------------------------------------------------------------------
rt_resolve:
    push rbx
    push r12
    push r13
    push r14
    push r15
    mov r14, rdi
    call rt_kernel32
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

rt_kernel32:
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

; ---------------------------------------------------------------------------
nm_getstd: db "GetStdHandle", 0
nm_write:  db "WriteFile", 0
nm_read:   db "ReadFile", 0
nm_close:  db "CloseHandle", 0
nm_alloc:  db "VirtualAlloc", 0
nm_exit:   db "ExitProcess", 0

p_getstd: dq 0
p_write:  dq 0
p_read:   dq 0
p_close:  dq 0
p_alloc:  dq 0
p_exit:   dq 0
h_out:    dq 0
h_err:    dq 0
h_in:     dq 0
nwritten: dd 0
ngot:     dd 0
