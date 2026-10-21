/* GNU x86-64 host control only. Not a Sutram object or generated Sutram code.
 * One root _start; external function called directly and by address. */
.text
.global _start
.extern sutram_r93_add
_start:
    movq $17, %rdi
    movq $25, %rsi
    call sutram_r93_add
    cmpq $42, %rax
    jne .Lfail
    leaq sutram_r93_add(%rip), %r10
    movq $17, %rdi
    movq $25, %rsi
    call *%r10
    cmpq $42, %rax
    jne .Lfail
    movq $1, %rax
    movq $1, %rdi
    leaq .Lmsg(%rip), %rsi
    movq $3, %rdx
    syscall
    movq $42, %rdi
    jmp .Lexit
.Lfail:
    movq $1, %rdi
.Lexit:
    movq $60, %rax
    syscall
.Lmsg:
    .ascii "42\n"
.section .note.GNU-stack,"",@progbits
