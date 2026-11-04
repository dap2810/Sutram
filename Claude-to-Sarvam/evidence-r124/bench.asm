; R124 WS1: one kosh read, today's layout vs a descriptor. N elements, summed REPS times, each read the way the
; compiler emits it: reload the variable from the frame, bounds-check against the length, load the element.
; MODE 0 (today): the variable holds the data pointer; length at [p-16].
; MODE 1 (descriptor): the variable holds a descriptor address; [d] = data pointer, [d+8] = length.
bits 64
default rel
%ifndef N
%define N 1000000
%endif
%ifndef REPS
%define REPS 200
%endif
section .bss
alignb 64
hdr: resq 2
data: resq N
desc: resq 3
section .text
global _start
_start:
    push rbp
    mov rbp, rsp
    sub rsp, 16
    mov qword [hdr], N              ; [data-16] = length
    lea rax, [data]
    mov [desc], rax
    mov qword [desc+8], N
    mov qword [desc+16], N
    xor ecx, ecx
.fill: mov [data+rcx*8], rcx
    inc rcx
    cmp rcx, N
    jb .fill
%if MODE == 0
    lea rax, [data+16-16]
    lea rax, [data]
%else
    lea rax, [desc]
%endif
    mov [rbp-8], rax
    xor r9d, r9d                    ; sum
    mov r10d, REPS
.rep:
    xor r8d, r8d                    ; i
.loop:
    mov rax, [rbp-8]
%if MODE == 0
    mov rcx, [rax-16]
    cmp r8, rcx
    jae .fail
    add r9, [rax+r8*8]
%else
    mov rdx, [rax]
    mov rcx, [rax+8]
    cmp r8, rcx
    jae .fail
    add r9, [rdx+r8*8]
%endif
    inc r8
    cmp r8, N
    jb .loop
    dec r10d
    jnz .rep
    mov rdi, r9
    and edi, 0x7f
    mov eax, 60
    syscall
.fail:
    mov edi, 99
    mov eax, 60
    syscall
