; ============================================================
; R163 (Sarvam R163 WS1; found R162): the output must not be an input.
; ============================================================
; Up to v315 `sutram hello.sm hello.sm` compiled, then wrote the binary over hello.sm - the program gone, exit 0 -
; and `--object b.sm b.sm` and `sutram-link a.smo a.smo` did the same. The compiler and the linker read every input
; before they write, but never asked whether the output was one of those files.
;
; Now every file opened for reading is noted by its identity: on Linux (st_dev, st_ino) from fstat of the open
; descriptor, on Windows (volume serial, file index) from GetFileInformationByHandle of the open handle. The output
; is opened WITHOUT truncating it (ChatGPT R225: checking a name and then reopening it with truncation leaves a
; window in which the name can change), the identity of THAT open file is compared with every input's, and only
; if it is none of them is it cut to length 0 and written. If it is an input - by any name: ./a.sm, a.sm, a hard
; link, a symbolic link, another case on Windows - it is closed untouched and the program stops, exit 1. If its
; identity cannot be read, the program stops too: uncertainty is not taken for "different".
; Identity, not the name, and not the contents: two names for one file are one file; two files with the same bytes
; are two. Up to R163_CAP different inputs are noted (a compile reads its source, its pack, its yoj modules and an FFI
; file; a file opened again is noted once); a program that reads more is refused rather than half-checked.
;
;   r163_note      rax = fd (Linux) / handle (Windows) just opened for reading. Every register is kept.
;   r163_open_out  rdi = path, rdx = mode (Linux) -> rax = the output, open for writing at length 0; or
;                  R163_SAME (it is an input), R163_UNSURE (its identity could not be read, or too many inputs),
;                  or a negative error (it could not be opened). rdi is kept.
R163_CAP    equ 256
R163_SAME   equ -7777
R163_UNSURE equ -7778

section .bss
    r163_ids   resq R163_CAP * 2
    r163_n     resq 1
    r163_full  resq 1                ; 1 once an input could not be noted
    r163_buf   resb 160              ; struct stat (144 bytes) / BY_HANDLE_FILE_INFORMATION (52)
section .text

; r163_match(r8 = volume/device, r9 = file id/inode) -> rax = 1 if an input has it. Uses rcx, rdx, rsi.
r163_match:
    xor ecx, ecx
    lea rdx, [rel r163_ids]
.next:
    cmp rcx, [rel r163_n]
    jae .no
    mov rsi, rcx
    shl rsi, 4
    cmp r8, [rdx + rsi]
    jne .skip
    cmp r9, [rdx + rsi + 8]
    jne .skip
    mov eax, 1
    ret
.skip:
    inc rcx
    jmp .next
.no:
    xor eax, eax
    ret

; r163_add(r8, r9): note one identity, once - a file opened again is not noted again (--debug opens a module once
; for each statement it traces: 542 opens of three files in examples/import_demo.sm). Uses rax, rcx, rdx, rsi.
r163_add:
    call r163_match
    test eax, eax
    jnz .have
    mov rcx, [rel r163_n]
    cmp rcx, R163_CAP
    jae .full
    lea rdx, [rel r163_ids]
    shl rcx, 4
    mov [rdx + rcx], r8
    mov [rdx + rcx + 8], r9
    inc qword [rel r163_n]
    ret
.full:
    mov qword [rel r163_full], 1
.have:
    ret

%ifndef WINDOWS
r163_note:
    push rax
    push rcx
    push rdx
    push rsi
    push rdi
    push r8
    push r9
    push r11
    mov rdi, rax
    lea rsi, [rel r163_buf]
    mov eax, 5                       ; fstat
    syscall
    test rax, rax
    js .unsure
    mov r8, [rel r163_buf]           ; st_dev
    mov r9, [rel r163_buf + 8]       ; st_ino
    call r163_add
    jmp .done
.unsure:
    mov qword [rel r163_full], 1     ; an input whose identity is unknown: no output may be trusted not to be it
.done:
    pop r11
    pop r9
    pop r8
    pop rdi
    pop rsi
    pop rdx
    pop rcx
    pop rax
    ret

r163_open_out:
    push rbx
    push rcx
    push rdx
    push rsi
    push rdi
    push r8
    push r9
    push r11
    mov rax, R163_UNSURE
    cmp qword [rel r163_full], 0
    jne .ret
    mov esi, 0x41                    ; O_WRONLY|O_CREAT - no O_TRUNC until it is known not to be an input
    mov eax, 2                       ; open (rdx = mode)
    syscall
    test rax, rax
    js .ret
    mov rbx, rax
    mov rdi, rbx
    lea rsi, [rel r163_buf]
    mov eax, 5                       ; fstat - of the file actually opened
    syscall
    test rax, rax
    js .close_unsure
    mov r8, [rel r163_buf]
    mov r9, [rel r163_buf + 8]
    call r163_match
    test eax, eax
    jnz .close_same
    mov eax, dword [rel r163_buf + 24]   ; st_mode
    and eax, 0o170000
    cmp eax, 0o100000                ; a regular file is cut; /dev/null, a pipe or a terminal is written as it is
    jne .keep
    mov rdi, rbx
    xor esi, esi
    mov eax, 77                      ; ftruncate(fd, 0): now it may be written
    syscall
    test rax, rax
    js .close_err
.keep:
    mov rax, rbx
    jmp .ret
.close_err:
    push rax
    mov rdi, rbx
    mov eax, 3
    syscall
    pop rax
    jmp .ret
.close_same:
    mov rdi, rbx
    mov eax, 3
    syscall
    mov rax, R163_SAME
    jmp .ret
.close_unsure:
    mov rdi, rbx
    mov eax, 3
    syscall
    mov rax, R163_UNSURE
.ret:
    pop r11
    pop r9
    pop r8
    pop rdi
    pop rsi
    pop rdx
    pop rcx
    pop rbx
    ret
%else
; Windows: the same through kernel32 (Win64: rcx, rdx, r8, r9; 32 bytes of shadow space; rsp aligned).
; r163_winid(rbx = handle) -> rax = 1 with r8 = volume serial, r9 = file index; 0 if it could not be read.
r163_winid:
    push r12
    mov r12, rsp
    and rsp, -16
    sub rsp, 32
    mov rcx, rbx
    lea rdx, [rel r163_buf]
    call qword [rel p_getfileinfo]
    mov rsp, r12
    pop r12
    test eax, eax
    jz .no
    mov r8d, dword [rel r163_buf + 28]       ; dwVolumeSerialNumber
    mov r9d, dword [rel r163_buf + 44]       ; nFileIndexHigh
    shl r9, 32
    mov eax, dword [rel r163_buf + 48]       ; nFileIndexLow
    or r9, rax
    mov eax, 1
    ret
.no:
    xor eax, eax
    ret

r163_note:
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
    mov rbx, rax
    call r163_winid
    test eax, eax
    jz .unsure
    call r163_add
    jmp .done
.unsure:
    mov qword [rel r163_full], 1
.done:
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

; r163_close(rbx = handle): CloseHandle, registers other than rax kept by the caller's frame.
r163_close:
    push r12
    mov r12, rsp
    and rsp, -16
    sub rsp, 32
    mov rcx, rbx
    call qword [rel p_closehandle]
    mov rsp, r12
    pop r12
    ret

r163_open_out:
    push rbx
    push rcx
    push rdx
    push rsi
    push rdi
    push r8
    push r9
    push r10
    push r11
    push r12
    mov rax, R163_UNSURE
    cmp qword [rel r163_full], 0
    jne .ret
    mov r12, rsp
    and rsp, -16
    sub rsp, 64
    mov rcx, rdi                     ; the path
    mov edx, 0x40000000              ; GENERIC_WRITE
    mov r8d, 1                       ; FILE_SHARE_READ
    xor r9d, r9d
    mov qword [rsp + 32], 4          ; OPEN_ALWAYS: an existing file is opened, not emptied
    mov qword [rsp + 40], 0x80       ; FILE_ATTRIBUTE_NORMAL
    mov qword [rsp + 48], 0
    call qword [rel p_createfile]
    mov rsp, r12
    cmp rax, -1
    je .ret
    mov rbx, rax
    call r163_winid
    test eax, eax
    jnz .w_have
    mov r12, rsp                     ; no file identity: a device such as NUL is no input, and is written as it is;
    and rsp, -16                     ; a disk file whose identity cannot be read is refused
    sub rsp, 32
    mov rcx, rbx
    call qword [rel p_getfiletype]
    mov rsp, r12
    cmp eax, 1                       ; FILE_TYPE_DISK
    je .close_unsure
    mov rax, rbx
    jmp .ret
.w_have:
    call r163_match
    test eax, eax
    jnz .close_same
    mov r12, rsp                     ; the file pointer is at 0: SetEndOfFile cuts it there
    and rsp, -16
    sub rsp, 32
    mov rcx, rbx
    call qword [rel p_setendoffile]
    mov rsp, r12
    test eax, eax
    jz .close_err
    mov rax, rbx
    jmp .ret
.close_err:
    call r163_close
    mov rax, -1
    jmp .ret
.close_same:
    call r163_close
    mov rax, R163_SAME
    jmp .ret
.close_unsure:
    call r163_close
    mov rax, R163_UNSURE
.ret:
    pop r12
    pop r11
    pop r10
    pop r9
    pop r8
    pop rdi
    pop rsi
    pop rdx
    pop rcx
    pop rbx
    ret
%endif
