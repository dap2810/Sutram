bits 64
default rel
%define N 1000000
section .bss
alignb 64
src: resq N
dst: resq N
section .text
global _start
_start:
    xor ecx,ecx
.f: mov [src+rcx*8],rcx
    mov [dst+rcx*8],rcx
    inc rcx
    cmp rcx,N
    jb .f
    mov r10d,REPS
.r: lea rsi,[src]
    lea rdi,[dst]
    mov ecx,N
    rep movsq
    dec r10d
    jnz .r
    mov eax,60
    xor edi,edi
    syscall
