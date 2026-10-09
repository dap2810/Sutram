; ---------------------------------------------------------------------------
; winio.asm — Sutram Windows runtime shim  (port step 3)
;
; Self-contained Win64 I/O: no import libraries, no C runtime. It finds
; kernel32 through the PEB, parses its export table, and calls the handful
; of functions we need (GetStdHandle, WriteFile, ReadFile, CreateFileA,
; CloseHandle, VirtualAlloc, ExitProcess).
;
; This file is the seed of TWO things:
;   1. the compiler's own I/O on Windows (so sutram.exe can read .sm
;      sources and write binaries), and
;   2. the runtime embedded in every program the compiler emits for
;      Windows, so generated code calls kernel32 instead of `syscall`.
;
; Build:
;   nasm -f win64 winio.asm -o winio.obj
;   ld -mi386pep --entry=_start -o winio.exe winio.obj
;
; Verified here: assembles, links, valid PE32+ (file/objdump).
; Runtime behaviour needs a real Windows machine to confirm.
; ---------------------------------------------------------------------------

bits 64
default rel

global _start
global win_kernel32
global win_resolve
global rt_init
global rt_write
global rt_read_file
global rt_exit

section .text

; ---------------------------------------------------------------------------
; _start — demo: init, write a line to stdout, exit 0
; ---------------------------------------------------------------------------
_start:
    and rsp, -16                ; align (PE entry arrives 8-mod-16)
    sub rsp, 32
    call rt_init
    lea rcx, [rel msg_ok]
    mov rdx, msg_ok_len
    call rt_write
    xor ecx, ecx
    call rt_exit
    hlt

; ---------------------------------------------------------------------------
; rt_init — resolve the kernel32 functions we need into globals.
; ---------------------------------------------------------------------------
rt_init:
    push rbx
    sub rsp, 32
    lea rdi, [rel name_getstd]
    call win_resolve
    mov [rel p_getstd], rax
    lea rdi, [rel name_writefile]
    call win_resolve
    mov [rel p_writefile], rax
    lea rdi, [rel name_readfile]
    call win_resolve
    mov [rel p_readfile], rax
    lea rdi, [rel name_createfile]
    call win_resolve
    mov [rel p_createfile], rax
    lea rdi, [rel name_closehandle]
    call win_resolve
    mov [rel p_closehandle], rax
    lea rdi, [rel name_virtualalloc]
    call win_resolve
    mov [rel p_virtualalloc], rax
    lea rdi, [rel name_exitprocess]
    call win_resolve
    mov [rel p_exitprocess], rax
    add rsp, 32
    pop rbx
    ret

; ---------------------------------------------------------------------------
; rt_write — write a buffer to stdout
;   in: rcx = buffer, rdx = length
; ---------------------------------------------------------------------------
rt_write:
    push rbx
    push r12
    push r13
    sub rsp, 48                 ; 32 shadow + 8 (5th arg) + align
    mov r12, rcx                ; buffer
    mov r13, rdx                ; length
    mov rcx, -11                ; STD_OUTPUT_HANDLE
    call qword [rel p_getstd]
    mov rbx, rax                ; handle
    mov rcx, rbx
    mov rdx, r12
    mov r8, r13
    lea r9, [rel written]
    mov qword [rsp+32], 0       ; lpOverlapped = NULL
    call qword [rel p_writefile]
    add rsp, 48
    pop r13
    pop r12
    pop rbx
    ret

; ---------------------------------------------------------------------------
; rt_read_file — open a file, read up to max bytes into a buffer.
;   in : rcx = path (NUL-terminated), rdx = buffer, r8 = max bytes
;   out: rax = bytes read, or -1 on failure
; ---------------------------------------------------------------------------
rt_read_file:
    push rbx
    push r12
    push r13
    push r14
    sub rsp, 48
    mov r12, rdx                ; buffer
    mov r13, r8                 ; max
    ; CreateFileA(path, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, 0, NULL)
    mov rdx, 0x80000000         ; GENERIC_READ
    mov r8, 1                   ; FILE_SHARE_READ
    xor r9, r9                  ; lpSecurityAttributes
    mov qword [rsp+32], 3       ; OPEN_EXISTING
    mov qword [rsp+40], 0       ; hTemplateFile / attrs
    call qword [rel p_createfile]
    cmp rax, -1
    je .rf_fail
    mov rbx, rax                ; handle
    ; ReadFile(h, buf, max, &got, NULL)
    mov rcx, rbx
    mov rdx, r12
    mov r8, r13
    lea r9, [rel got]
    mov qword [rsp+32], 0
    call qword [rel p_readfile]
    ; CloseHandle(h)
    mov rcx, rbx
    call qword [rel p_closehandle]
    mov eax, [rel got]          ; bytes read
    jmp .rf_done
.rf_fail:
    mov rax, -1
.rf_done:
    add rsp, 48
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

; ---------------------------------------------------------------------------
; rt_exit — exit the process
;   in: ecx = exit code
; ---------------------------------------------------------------------------
rt_exit:
    sub rsp, 40
    call qword [rel p_exitprocess]
    add rsp, 40
    ret

; ---------------------------------------------------------------------------
; win_kernel32 — kernel32 base via PEB walk.  out: rax = DllBase
; ---------------------------------------------------------------------------
win_kernel32:
    mov rax, [gs:0x60]          ; PEB
    test rax, rax
    jz .k_fail
    mov rax, [rax+0x18]         ; PEB->Ldr
    test rax, rax
    jz .k_fail
    mov rax, [rax+0x20]         ; InMemoryOrderModuleList -> exe
    test rax, rax
    jz .k_fail
    mov rax, [rax]              ; -> ntdll
    test rax, rax
    jz .k_fail
    mov rax, [rax]              ; -> kernel32
    test rax, rax
    jz .k_fail
    mov rax, [rax+0x20]         ; DllBase
    ret
.k_fail:
    xor rax, rax
    ret

; ---------------------------------------------------------------------------
; win_resolve — address of an exported kernel32 function.
;   in : rdi = NUL-terminated name   out: rax = address (0 if not found)
; ---------------------------------------------------------------------------
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
    mov eax, [rbx+0x3C]         ; e_lfanew
    add rax, rbx
    mov r12d, [rax+24+0x70]     ; export dir RVA
    test r12d, r12d
    jz .r_fail
    add r12, rbx                ; IMAGE_EXPORT_DIRECTORY
    mov r13d, [r12+0x20]        ; AddressOfNames RVA
    add r13, rbx
    mov r15d, [r12+0x18]        ; NumberOfNames
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
    mov r13d, [r12+0x24]        ; AddressOfNameOrdinals RVA
    add r13, rbx
    movzx ecx, word [r13 + rcx*2]
    mov r13d, [r12+0x1C]        ; AddressOfFunctions RVA
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
name_getstd:     db "GetStdHandle", 0
name_writefile:  db "WriteFile", 0
name_readfile:   db "ReadFile", 0
name_createfile: db "CreateFileA", 0
name_closehandle:db "CloseHandle", 0
name_virtualalloc:db "VirtualAlloc", 0
name_exitprocess:db "ExitProcess", 0

msg_ok:      db "Sutram Win64 runtime OK", 10
msg_ok_len   equ $ - msg_ok

section .bss
p_getstd:       resq 1
p_writefile:    resq 1
p_readfile:     resq 1
p_createfile:   resq 1
p_closehandle:  resq 1
p_virtualalloc: resq 1
p_exitprocess:  resq 1
written:        resd 1
got:            resd 1
