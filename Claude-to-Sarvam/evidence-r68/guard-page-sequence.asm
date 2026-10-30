bits 64
start:
    push rbx
    mov rbx, rax
    test rax, rax
    jz .fail
    lea rsi, [rax+8191]
    and rsi, -4096
    xor edi, edi
    mov edx, 3
    mov r10d, 0x22
    mov r8, -1
    xor r9d, r9d
    mov eax, 9
    syscall
    cmp rax, -4095
    jae .fail
    lea rdi, [rax+rsi-4096]
    mov esi, 4096
    xor edx, edx
    mov eax, 10
    push rdi
    syscall
    pop rax
    sub rax, rbx
    pop rbx
    jmp .done
.fail:
    xor eax, eax
    pop rbx
.done:
