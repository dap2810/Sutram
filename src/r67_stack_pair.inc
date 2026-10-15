; R67 bounded pre-emission identity matcher for an ENTIRE pure hex block.
; RDI=first byte, RSI=exclusive end. EAX=1 only for a canonical PUSH r / POP r
; pair with identical 64-bit GPR, excluding RSP; else EAX=0. No emitted bytes.
; Scope contract: caller explicitly opts into pure stack-pair blocks, with
; no external entry/relative targets or observable transient stack writes.
; Not a scan of arbitrary x86 bytes and not a rewrite of general inline ASM.
section .text
r67_is_pure_stack_pair:
    push rbx
    mov rbx,rdi
    xor r8d,r8d               ; at most four decoded bytes
    xor r9d,r9d               ; packed big-endian bytes
.space:
    cmp rbx,rsi
    jae .complete
    cmp byte [rbx],32
    jne .byte
    inc rbx
    jmp .space
.byte:
    cmp r8d,4
    jae .no
    mov rax,rsi
    sub rax,rbx
    cmp rax,2
    jb .no
    movzx eax,byte [rbx]
    call .hex
    cmp eax,15
    ja .no
    mov r10d,eax
    shl r10d,4
    movzx eax,byte [rbx+1]
    call .hex
    cmp eax,15
    ja .no
    or r10d,eax
    shl r9d,8
    or r9d,r10d
    add rbx,2
    inc r8d
    jmp .space
.complete:
    cmp r8d,2
    je .low
    cmp r8d,4
    jne .no
    mov eax,r9d
    and eax,0xFF00FF00
    cmp eax,0x41004100         ; 41 5x 41 5y
    jne .no
    mov eax,r9d
    shr eax,16
    and eax,255
    cmp eax,0x50
    jb .no
    cmp eax,0x57
    ja .no
    add eax,8
    movzx edx,r9b
    cmp eax,edx
    jne .no
    jmp .yes
.low:
    mov eax,r9d
    shr eax,8
    cmp eax,0x50
    jb .no
    cmp eax,0x57
    ja .no
    cmp eax,0x54              ; no RSP semantics assumptions
    je .no
    add eax,8
    movzx edx,r9b
    cmp eax,edx
    jne .no
.yes:
    mov eax,1
    pop rbx
    ret
.no:
    xor eax,eax
    pop rbx
    ret
.hex:
    cmp eax,48
    jb .invalid
    cmp eax,57
    jbe .decimal
    or eax,32
    cmp eax,97
    jb .invalid
    cmp eax,102
    ja .invalid
    sub eax,87
    ret
.decimal:
    sub eax,48
    ret
.invalid:
    mov eax,-1
    ret
