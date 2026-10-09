; Sutram native Windows host layer (x86-64)
; ------------------------------------------------------------
; Runs the existing compiler/parser natively on Windows while preserving its
; internal Linux-style syscall calling convention at the OS boundary.
;
; Windows-facing guarantees in this layer:
; - real Windows command-line parsing via CommandLineToArgvW;
; - UTF-16 Windows paths converted to/from Sutram's UTF-8 byte strings;
; - Unicode source/output paths through CreateFileW;
; - UTF-8 console code pages;
; - environment variables converted to UTF-8 for SUTRAM_LANG;
; - dynamic Win64 stack alignment before every API call.
;
; This is the COMPILER HOST layer. Generated Sutram programs still use the
; transitional ELF/Linux runtime backend until the separate PE backend lands.

bits 64
default rel

global _start
global win_syscall
extern sutram_main

extern GetCommandLineW
extern CommandLineToArgvW
extern LocalFree
extern GetEnvironmentStringsW
extern FreeEnvironmentStringsW
extern WideCharToMultiByte
extern MultiByteToWideChar
extern GetStdHandle
extern ReadFile
extern WriteFile
extern CreateFileW
extern CloseHandle
extern ExitProcess
extern GetModuleFileNameW
extern SetConsoleCP
extern SetConsoleOutputCP

%define CP_UTF8              65001
%define STD_INPUT_HANDLE     -10
%define STD_OUTPUT_HANDLE    -11
%define STD_ERROR_HANDLE     -12
%define INVALID_HANDLE_VALUE -1

%define GENERIC_READ         0x80000000
%define GENERIC_WRITE        0x40000000
%define FILE_SHARE_READ      0x00000001
%define FILE_SHARE_WRITE     0x00000002
%define CREATE_ALWAYS        2
%define OPEN_EXISTING        3
%define FILE_ATTRIBUTE_NORMAL 0x00000080

section .text

; ------------------------------------------------------------
; _start
; Build the Linux-like initial stack image expected by sutram_main:
;   [argc][argv0]...[argvN][NULL][env0]...[envN][NULL]
; argv/environment strings are UTF-8.
; ------------------------------------------------------------
_start:
    and rsp, -16

    sub rsp, 32
    mov ecx, CP_UTF8
    call SetConsoleOutputCP
    add rsp, 32
    sub rsp, 32
    mov ecx, CP_UTF8
    call SetConsoleCP
    add rsp, 32

    ; Let Windows parse quoting/backslashes exactly as a native application.
    sub rsp, 32
    call GetCommandLineW
    add rsp, 32
    test rax, rax
    jz .fatal_start
    mov rcx, rax
    lea rdx, [rel argc_tmp]
    sub rsp, 32
    call CommandLineToArgvW
    add rsp, 32
    test rax, rax
    jz .fatal_start
    mov r15, rax                    ; LPWSTR* argv
    mov r12d, [rel argc_tmp]
    cmp r12d, 63
    jbe .argc_ok
    mov r12d, 63
.argc_ok:

    lea rbx, [rel argv_store]
    lea r14, [rel argv_utf8]
    xor esi, esi
.arg_loop:
    cmp rsi, r12
    jae .arg_done
    mov [rbx+rsi*8], r14

    lea rax, [rel argv_utf8_end]
    sub rax, r14
    cmp rax, 2
    jb .arg_truncated

    ; WideCharToMultiByte(CP_UTF8,0,argvW,-1,dst,remaining,NULL,NULL)
    mov r8, [r15+rsi*8]
    mov rcx, CP_UTF8
    xor edx, edx
    mov r9, -1
    sub rsp, 64
    mov [rsp+32], r14
    mov dword [rsp+40], eax
    mov qword [rsp+48], 0
    mov qword [rsp+56], 0
    call WideCharToMultiByte
    add rsp, 64
    test eax, eax
    jz .arg_truncated
    add r14, rax
    inc rsi
    jmp .arg_loop

.arg_truncated:
    ; Stop cleanly rather than writing past argv_utf8. argc becomes the
    ; number of arguments converted successfully so far.
    mov r12, rsi
    jmp .arg_done

.arg_done:
    mov qword [rbx+r12*8], 0
    mov rcx, r15
    sub rsp, 32
    call LocalFree
    add rsp, 32

    ; Convert the Windows UTF-16 environment block to UTF-8 pointers.
    sub rsp, 32
    call GetEnvironmentStringsW
    add rsp, 32
    mov r15, rax                    ; block start, freed after conversion
    lea rbx, [rel env_store]
    lea r14, [rel env_utf8]
    xor r13d, r13d
    test r15, r15
    jz .env_done
    mov rsi, r15

.env_next:
    cmp word [rsi], 0
    je .env_release
    cmp r13d, 2047
    jae .env_release
    lea rax, [rel env_utf8_end]
    sub rax, r14
    cmp rax, 4
    jb .env_release

    mov [rbx+r13*8], r14
    ; WideCharToMultiByte(CP_UTF8,0,envW,-1,dst,remaining,NULL,NULL)
    mov rcx, CP_UTF8
    xor edx, edx
    mov r8, rsi
    mov r9, -1
    sub rsp, 64
    mov [rsp+32], r14
    mov dword [rsp+40], eax
    mov qword [rsp+48], 0
    mov qword [rsp+56], 0
    call WideCharToMultiByte
    add rsp, 64
    test eax, eax
    jz .env_release
    add r14, rax
    inc r13d

.env_scan_w:
    cmp word [rsi], 0
    je .env_advance_w
    add rsi, 2
    jmp .env_scan_w
.env_advance_w:
    add rsi, 2
    jmp .env_next

.env_release:
    mov rcx, r15
    sub rsp, 32
    call FreeEnvironmentStringsW
    add rsp, 32
.env_done:
    mov qword [rbx+r13*8], 0

    ; Allocate a synthetic initial stack. Count qwords:
    ; argc + argv + argvNULL + env + envNULL = argc+env+3.
    mov rax, r12
    add rax, r13
    add rax, 3
    shl rax, 3
    add rax, 15
    and rax, -16
    sub rsp, rax

    mov [rsp], r12
    xor ecx, ecx
    lea rdx, [rel argv_store]
.copy_argv:
    cmp rcx, r12
    jae .argv_complete
    mov rax, [rdx+rcx*8]
    mov [rsp+8+rcx*8], rax
    inc rcx
    jmp .copy_argv
.argv_complete:
    mov qword [rsp+8+rcx*8], 0
    inc rcx
    xor r8d, r8d
    lea rdx, [rel env_store]
.copy_env:
    cmp r8, r13
    jae .env_complete
    mov rax, [rdx+r8*8]
    mov [rsp+8+rcx*8], rax
    inc rcx
    inc r8
    jmp .copy_env
.env_complete:
    mov qword [rsp+8+rcx*8], 0
    jmp sutram_main

.fatal_start:
    mov ecx, 2
    sub rsp, 32
    call ExitProcess
    int3

; ---------------------------------------------------------------------------
; win_syscall
; Input follows the Linux register convention used by the existing compiler:
;   rax=syscall#, rdi,rsi,rdx,r10,r8,r9=args
; Output: rax result, negative on failure where practical.
;
; Compiler-host operations implemented:
;   0 read, 1 write, 2 open, 3 close, 60 exit, 89 self path, 90 chmod(no-op)
; fork/exec/wait intentionally return -1 while the Windows REPL is disabled.
; ---------------------------------------------------------------------------
win_syscall:
    cmp rax, 0
    je .read
    cmp rax, 1
    je .write
    cmp rax, 2
    je .open
    cmp rax, 3
    je .close
    cmp rax, 60
    je .exit
    cmp rax, 89
    je .selfpath
    cmp rax, 90
    je .chmod
    mov rax, -1
    ret

.read:
    ; rdi=fd/handle, rsi=buf, rdx=count
    push rbx
    push r12
    mov r12, rdx
    mov rbx, rsp

    test rdi, rdi
    jnz .read_have_handle
    and rsp, -16
    sub rsp, 32
    mov ecx, STD_INPUT_HANDLE
    call GetStdHandle
    mov rsp, rbx
    cmp rax, INVALID_HANDLE_VALUE
    je .read_fail
    test rax, rax
    jz .read_fail
    mov rdi, rax

.read_have_handle:
    and rsp, -16
    sub rsp, 48
    mov rcx, rdi
    mov rdx, rsi
    mov r8d, r12d
    lea r9, [rsp+40]
    mov qword [rsp+32], 0
    call ReadFile
    test eax, eax
    jz .read_fail_aligned
    mov eax, [rsp+40]
    mov rsp, rbx
    pop r12
    pop rbx
    ret
.read_fail_aligned:
    mov rsp, rbx
.read_fail:
    pop r12
    pop rbx
    mov rax, -1
    ret

.write:
    ; rdi=fd/handle, rsi=buf, rdx=count
    push rbx
    push r12
    mov r12, rdx
    mov rbx, rsp

    cmp rdi, 1
    je .write_stdout
    cmp rdi, 2
    jne .write_have_handle
    mov ecx, STD_ERROR_HANDLE
    jmp .write_get_std
.write_stdout:
    mov ecx, STD_OUTPUT_HANDLE
.write_get_std:
    and rsp, -16
    sub rsp, 32
    call GetStdHandle
    mov rsp, rbx
    cmp rax, INVALID_HANDLE_VALUE
    je .write_fail
    test rax, rax
    jz .write_fail
    mov rdi, rax

.write_have_handle:
    and rsp, -16
    sub rsp, 48
    mov rcx, rdi
    mov rdx, rsi
    mov r8d, r12d
    lea r9, [rsp+40]
    mov qword [rsp+32], 0
    call WriteFile
    test eax, eax
    jz .write_fail_aligned
    mov eax, [rsp+40]
    mov rsp, rbx
    pop r12
    pop rbx
    ret
.write_fail_aligned:
    mov rsp, rbx
.write_fail:
    pop r12
    pop rbx
    mov rax, -1
    ret

.open:
    ; rdi=UTF-8 path, rsi=Linux-like flags used by the compiler host.
    push rbx
    push r12
    mov r12, rsi
    mov rbx, rsp

    ; Convert path UTF-8 -> UTF-16.
    and rsp, -16
    sub rsp, 48
    mov ecx, CP_UTF8
    xor edx, edx
    mov r8, rdi
    mov r9, -1
    lea rax, [rel path_wbuf]
    mov [rsp+32], rax
    mov dword [rsp+40], 32768
    call MultiByteToWideChar
    mov rsp, rbx
    test eax, eax
    jz .open_fail

    test r12, r12
    jz .open_read
    mov edx, GENERIC_READ | GENERIC_WRITE
    mov r10d, CREATE_ALWAYS
    jmp .open_call
.open_read:
    mov edx, GENERIC_READ
    mov r10d, OPEN_EXISTING
.open_call:
    and rsp, -16
    sub rsp, 64
    lea rcx, [rel path_wbuf]
    mov r8d, FILE_SHARE_READ | FILE_SHARE_WRITE
    xor r9d, r9d
    mov dword [rsp+32], r10d
    mov dword [rsp+40], FILE_ATTRIBUTE_NORMAL
    mov qword [rsp+48], 0
    call CreateFileW
    mov rsp, rbx
    pop r12
    pop rbx
    cmp rax, INVALID_HANDLE_VALUE
    jne .open_ret
    mov rax, -1
.open_ret:
    ret
.open_fail:
    pop r12
    pop rbx
    mov rax, -1
    ret

.close:
    cmp rdi, 2
    jbe .close_ok
    push rbx
    mov rbx, rsp
    and rsp, -16
    sub rsp, 32
    mov rcx, rdi
    call CloseHandle
    mov rsp, rbx
    pop rbx
    test eax, eax
    jz .close_fail
.close_ok:
    xor eax, eax
    ret
.close_fail:
    mov rax, -1
    ret

.exit:
    and rsp, -16
    sub rsp, 32
    mov ecx, edi
    call ExitProcess
    int3

.selfpath:
    ; Linux readlink(path, buf, size) compatibility. Return UTF-8 bytes excluding NUL.
    push rbx
    push r12
    push r13
    mov r12, rsi                    ; destination UTF-8 buffer
    mov r13, rdx                    ; capacity
    mov rbx, rsp

    and rsp, -16
    sub rsp, 32
    xor ecx, ecx
    lea rdx, [rel module_wbuf]
    mov r8d, 32768
    call GetModuleFileNameW
    mov rsp, rbx
    test eax, eax
    jz .self_fail
    cmp eax, 32767
    jae .self_fail

    and rsp, -16
    sub rsp, 64
    mov ecx, CP_UTF8
    xor edx, edx
    lea r8, [rel module_wbuf]
    mov r9, -1
    mov [rsp+32], r12
    mov dword [rsp+40], r13d
    mov qword [rsp+48], 0
    mov qword [rsp+56], 0
    call WideCharToMultiByte
    mov rsp, rbx
    test eax, eax
    jz .self_fail
    dec eax                         ; exclude terminating NUL
    pop r13
    pop r12
    pop rbx
    ret
.self_fail:
    pop r13
    pop r12
    pop rbx
    mov rax, -1
    ret

.chmod:
    xor eax, eax
    ret

section .bss
alignb 16
argc_tmp:       resd 1
alignb 8
argv_store:     resq 64
env_store:      resq 2048
argv_utf8:      resb 32768
argv_utf8_end:
env_utf8:       resb 131072
env_utf8_end:
path_wbuf:      resw 32768
module_wbuf:    resw 32768
