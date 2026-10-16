; R71 native separate-object linking primitives, NOT a second Sutram parser.
; This is the linker substrate. Production .sm -> .smo emission is not wired.
; Symbol record (64 bytes): namespace_ptr, namespace_len, name_ptr, name_len,
; code_offset, integer_arity, public_flag (0/1), owner_unit.
; Requests use the same layout; only name lengths/pointers and arity are read.
; Names use exact bytes, not a lossy concatenation or source textual inclusion.
; RDI=symbol table, RSI=count<=1024, RDX=request.
; Returns RAX=code offset and EDX=0; error RAX=-1, EDX:
; 1 unresolved, 2 private, 3 duplicate, 4 arity mismatch, 5 bad metadata.
; Pointers must refer to validated, readable object-loader allocations.
section .text
r71_resolve_export:
    push rbx
    push r12
    push r13
    push r14
    push r15
    mov rbx,rdi
    mov r12,rsi
    mov r13,rdx
    mov r15,-1
    xor r14d,r14d
    cmp r12,1024
    ja .invalid
    test r13,r13
    jz .invalid
    test r12,r12
    jz .missing
    test rbx,rbx
    jz .invalid
    mov rdi,r13
    call r71_valid_symbol
    test eax,eax
    jz .invalid
.loop:
    cmp r14,r12
    jae .finished
    mov rax,r14
    shl rax,6
    lea rdi,[rbx+rax]
    call r71_valid_symbol
    test eax,eax
    jz .invalid
    mov rax,r14
    shl rax,6
    lea r10,[rbx+rax]
    mov rcx,[r10+8]
    cmp rcx,[r13+8]
    jne .next
    mov rdi,[r10]
    mov rsi,[r13]
    call r71_equal_bytes
    test eax,eax
    jz .next
    mov rcx,[r10+24]
    cmp rcx,[r13+24]
    jne .next
    mov rdi,[r10+16]
    mov rsi,[r13+16]
    call r71_equal_bytes
    test eax,eax
    jz .next
    cmp r15,-1
    jne .duplicate
    mov r15,r14
.next:
    inc r14
    jmp .loop
.finished:
    cmp r15,-1
    je .missing
    mov rax,r15
    shl rax,6
    lea r10,[rbx+rax]
    cmp qword [r10+48],1
    jne .private
    mov rax,[r10+40]
    cmp rax,[r13+40]
    jne .arity
    mov rax,[r10+32]
    xor edx,edx
    jmp .done
.missing:
    mov edx,1
    jmp .error
.private:
    mov edx,2
    jmp .error
.duplicate:
    mov edx,3
    jmp .error
.arity:
    mov edx,4
    jmp .error
.invalid:
    mov edx,5
.error:
    mov rax,-1
.done:
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

r71_valid_symbol:
    xor eax,eax
    cmp qword [rdi],0
    je .done
    cmp qword [rdi+16],0
    je .done
    cmp qword [rdi+8],1
    jb .done
    cmp qword [rdi+8],63
    ja .done
    cmp qword [rdi+24],1
    jb .done
    cmp qword [rdi+24],128
    ja .done
    cmp qword [rdi+40],6
    ja .done
    cmp qword [rdi+48],1
    ja .done
    mov eax,1
.done:
    ret

r71_equal_bytes:
    ; RCX=already validated bounded length. Preserve R10 (record pointer).
    xor eax,eax
    xor r8d,r8d
.loop:
    cmp r8,rcx
    jae .yes
    mov r9b,[rdi+r8]
    cmp r9b,[rsi+r8]
    jne .done
    inc r8
    jmp .loop
.yes:
    mov eax,1
.done:
    ret

r71_patch_rel32:
    ; RDI=image, RSI=actual image size, RDX=CALL displacement field,
    ; RCX=resolved target offset. Only an E8 rel32 CALL may be patched.
    ; Returns EAX=0; 1 bounds, 2 opcode, 3 displacement overflow. No write on error.
    cmp rsi,5
    jb .bounds
    test rdx,rdx
    jz .bounds
    mov rax,rsi
    sub rax,4
    cmp rdx,rax
    ja .bounds
    cmp rcx,rsi
    jae .bounds
    cmp byte [rdi+rdx-1],0xE8
    jne .opcode
    mov rax,rcx
    sub rax,rdx
    sub rax,4
    movsxd r8,eax
    cmp r8,rax
    jne .range
    mov [rdi+rdx],eax
    xor eax,eax
    ret
.bounds:
    mov eax,1
    ret
.opcode:
    mov eax,2
    ret
.range:
    mov eax,3
    ret
