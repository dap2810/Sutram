/* GNU x86-64 host control only; freestanding integer function, no libc. */
.text
.global sutram_r93_add
sutram_r93_add:
    movq %rdi, %rax
    addq %rsi, %rax
    ret
.section .note.GNU-stack,"",@progbits
