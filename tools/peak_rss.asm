; tools/peak_rss.asm - run a program and print the kernel's peak resident memory for it (R101).
;
;   nasm -f elf64 tools/peak_rss.asm -o peak_rss.o && ld -o peak_rss peak_rss.o
;   ./peak_rss PROGRAM [ARGS...]     ->  "peak_rss_kb 264 exit 0"
;
; fork; the child sends stdout to /dev/null and execve()s the program; the parent wait4()s for it and prints
; rusage.ru_maxrss (KB) and the exit status (a signal is printed as minus its number). Written in NASM, like
; the rest of the project, so that the measurer adds nothing to what it measures: a Python fork carries the
; interpreter's ~5 MB into the child's peak (ru_maxrss survives execve), this carries about 4 KB.

    section .bss
status:     resq 1
rusage:     resb 144
numbuf:     resb 32

    section .data
devnull:    db "/dev/null", 0
msg_kb:     db "peak_rss_kb "
msg_kb_len  equ $ - msg_kb
msg_exit:   db " exit "
msg_exit_len equ $ - msg_exit
usage:      db "usage: peak_rss PROGRAM [ARGS...]", 10
usage_len   equ $ - usage

    section .text
    global _start
_start:
    mov r12, [rsp]               ; argc
    cmp r12, 2
    jb .usage
    lea r13, [rsp + 16]          ; &argv[1]
    lea r14, [rsp + 8 + r12*8 + 8] ; envp
    mov eax, 57                  ; fork
    syscall
    test rax, rax
    js .fail
    jz .child
    mov r15, rax                 ; the child's pid
.wait:
    mov eax, 61                  ; wait4(pid, &status, 0, &rusage)
    mov rdi, r15
    lea rsi, [rel status]
    xor edx, edx
    lea r10, [rel rusage]
    syscall
    cmp rax, -4                  ; EINTR
    je .wait
    test rax, rax
    js .fail
    lea rsi, [rel msg_kb]
    mov edx, msg_kb_len
    call write_out
    mov rax, [rel rusage + 32]   ; ru_maxrss
    call write_num
    lea rsi, [rel msg_exit]
    mov edx, msg_exit_len
    call write_out
    mov eax, [rel status]
    mov ecx, eax
    and ecx, 0x7f
    jz .exited
    neg rcx                      ; killed by a signal: print minus the signal number
    mov rax, rcx
    jmp .print_code
.exited:
    shr eax, 8
    and eax, 0xff
.print_code:
    call write_num
    lea rsi, [rel numbuf]
    mov byte [rsi], 10
    mov edx, 1
    call write_out
    mov eax, 60
    xor edi, edi
    syscall

.child:
    mov eax, 2                   ; open("/dev/null", O_WRONLY)
    lea rdi, [rel devnull]
    mov esi, 1
    xor edx, edx
    syscall
    test rax, rax
    js .exec
    mov rdi, rax
    mov eax, 33                  ; dup2(fd, 1)
    mov esi, 1
    syscall
.exec:
    mov eax, 59                  ; execve(argv[1], &argv[1], envp)
    mov rdi, [r13]
    mov rsi, r13
    mov rdx, r14
    syscall
    mov eax, 60
    mov edi, 127
    syscall

.usage:
    lea rsi, [rel usage]
    mov edx, usage_len
    call write_out
    mov eax, 60
    mov edi, 2
    syscall
.fail:
    mov eax, 60
    mov edi, 1
    syscall

; write_out(rsi = bytes, rdx = length) to stdout
write_out:
    mov eax, 1
    mov edi, 1
    syscall
    ret

; write_num(rax = signed integer) in decimal to stdout
write_num:
    lea rsi, [rel numbuf + 31]
    xor ecx, ecx                 ; digit count
    mov r8, rax
    test rax, rax
    jns .digits
    neg rax
.digits:
    xor edx, edx
    mov r9, 10
    div r9
    add dl, '0'
    mov [rsi], dl
    dec rsi
    inc ecx
    test rax, rax
    jnz .digits
    test r8, r8
    jns .out
    mov byte [rsi], '-'
    dec rsi
    inc ecx
.out:
    inc rsi
    mov edx, ecx
    jmp write_out
