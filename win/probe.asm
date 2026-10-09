; Toolchain probe: can we build a Windows PE x86-64 here?
bits 64
default rel
global _start
section .text
_start:
    mov rcx, 42
    mov rax, 1
    ret
