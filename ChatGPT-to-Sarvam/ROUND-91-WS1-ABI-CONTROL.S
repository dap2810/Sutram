.intel_syntax noprefix
.section .rodata
fmt:
  .asciz "Sutram FFI ABI control: %ld\n"
.text
.globl main
.extern printf
main:
  push rbp
  mov rbp, rsp
  lea rdi, [rip+fmt]
  mov rsi, 42
  xor eax, eax
  call printf@PLT
  xor eax, eax
  pop rbp
  ret
.section .note.GNU-stack,"",@progbits
