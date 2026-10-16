; R71 experimental explicit unchecked-operation boundary, compiler-host code.
; Input RDI=40-byte token array, RSI=count, RDX=capacity (at most 65537).
; Tokens/names come from the existing lexer, not arbitrary untrusted pointers.
; Returns RAX=new count and EDX=0; on failure RAX=-1, EDX=error, RCX=input index.
; Validation is read-only. No token writes occur on any validation failure.
; `asurakshit { ... }` lowers to `yadi (1) { ... }` only after validation.
; Braces are retained: control flow is not accidentally flattened.
; Errors: 1 unchecked operation outside boundary, 2 malformed marker,
; 3 unmatched/too-deep braces, 4 top-level marker, 5 function inside marker,
; 6 bad capacity or insufficient expansion space. This is NOT memory safety.
section .text
r71_is_boundary:
    xor eax,eax
    cmp qword [rdi],2
    jne .done
    mov r8,[rdi+8]
    ; Byte-wise comparison stops at the first mismatch/terminator.
    cmp byte [r8+0],97
    jne .done
    cmp byte [r8+1],115
    jne .done
    cmp byte [r8+2],117
    jne .done
    cmp byte [r8+3],114
    jne .done
    cmp byte [r8+4],97
    jne .done
    cmp byte [r8+5],107
    jne .done
    cmp byte [r8+6],115
    jne .done
    cmp byte [r8+7],104
    jne .done
    cmp byte [r8+8],105
    jne .done
    cmp byte [r8+9],116
    jne .done
    cmp byte [r8+10],0
    jne .done
    mov eax,1
.done:
    ret

r71_check_unsafe:
    push rbx
    push r12
    push r13
    push r14
    push r15
    sub rsp,288
    mov rbx,rdi
    mov r12,rsi
    xor r13d,r13d
    cmp rdx,65537
    ja .capacity
    cmp rsi,rdx
    ja .capacity
    mov [rsp+256],rdx           ; actual caller capacity
    mov [rsp+264],rsi           ; projected output count
    mov qword [rsp+272],0       ; pending boundary opening brace
    xor r14d,r14d              ; all brace depth
    xor r15d,r15d              ; active boundary depth
.validate:
    cmp r13,r12
    jae .validated
    imul rax,r13,40
    lea rdi,[rbx+rax]
    call r71_is_boundary
    test eax,eax
    jz .not_marker
    test r14,r14
    jz .top_level
    lea rax,[r13+1]
    cmp rax,r12
    jae .marker_error
    imul rax,rax,40
    cmp qword [rbx+rax],5
    jne .marker_error
    cmp qword [rbx+rax+8],123
    jne .marker_error
    add qword [rsp+264],3
    mov rax,[rsp+264]
    cmp rax,[rsp+256]
    ja .capacity
    mov qword [rsp+272],1
    jmp .next
.not_marker:
    imul rax,r13,40
    lea rdi,[rbx+rax]
    cmp qword [rdi],5
    jne .check_operation
    cmp qword [rdi+8],123
    je .opening
    cmp qword [rdi+8],125
    je .closing
    jmp .next
.opening:
    cmp r14,256
    jae .brace_error
    mov rax,[rsp+272]
    mov [rsp+r14],al
    add r15,rax
    mov qword [rsp+272],0
    inc r14
    jmp .next
.closing:
    test r14,r14
    jz .brace_error
    dec r14
    movzx eax,byte [rsp+r14]
    sub r15,rax
    jmp .next
.check_operation:
    cmp qword [rdi],1
    jne .builtin
    cmp qword [rdi+16],12       ; prakriya definition in an unsafe region
    jne .inline
    test r15,r15
    jnz .definition
.inline:
    cmp qword [rdi+16],27       ; nishkriya
    je .raw
    jmp .next
.builtin:
    cmp qword [rdi],6
    jne .next
    mov rax,[rdi+16]
    cmp rax,1                  ; likh
    je .raw
    cmp rax,4                  ; pad
    je .raw
    cmp rax,14                 ; likh8
    je .raw
    cmp rax,15                 ; pad8
    je .raw
    cmp rax,28                 ; likh8c (raw indexed byte write)
    je .raw
    cmp rax,29                 ; pad8c (raw indexed byte read)
    je .raw
    cmp rax,30                 ; smaran
    je .raw
    cmp rax,31                 ; smaran_cp
    jne .next
.raw:
    test r15,r15
    jz .outside
.next:
    inc r13
    jmp .validate
.validated:
    test r14,r14
    jnz .brace_error
    ; Expand backwards, preserving source line and source-pointer fields.
    mov r14,[rsp+264]
    mov r13,r12
.expand:
    test r13,r13
    jz .success
    dec r13
    imul rax,r13,40
    lea rdi,[rbx+rax]
    call r71_is_boundary
    mov r15,rax
    imul rax,r13,40
    lea rsi,[rbx+rax]
    test r15,r15
    jnz .expand_boundary
    dec r14
    imul rax,r14,40
    lea rdi,[rbx+rax]
    call r71_copy_token
    jmp .expand
.expand_boundary:
    ; Preserve marker's original source metadata before any overlapping write.
    mov r8,[rsi+24]
    mov r9,[rsi+32]
    sub r14,4
    imul rax,r14,40
    lea rdi,[rbx+rax]
    ; yadi token uses the original identifier spelling solely for diagnostics.
    mov r10,[rsi+8]
    mov qword [rdi],1
    mov [rdi+8],r10
    mov qword [rdi+16],6
    mov [rdi+24],r8
    mov [rdi+32],r9
    add rdi,40
    mov qword [rdi],5
    mov qword [rdi+8],40
    mov qword [rdi+16],0
    mov [rdi+24],r8
    mov [rdi+32],r9
    add rdi,40
    mov qword [rdi],3
    mov qword [rdi+8],1
    mov qword [rdi+16],0
    mov [rdi+24],r8
    mov [rdi+32],r9
    add rdi,40
    mov qword [rdi],5
    mov qword [rdi+8],41
    mov qword [rdi+16],0
    mov [rdi+24],r8
    mov [rdi+32],r9
    jmp .expand
.success:
    mov rax,[rsp+264]
    xor edx,edx
    xor ecx,ecx
    jmp .return
.outside:
    mov edx,1
    jmp .error
.marker_error:
    mov edx,2
    jmp .error
.brace_error:
    mov edx,3
    jmp .error
.top_level:
    mov edx,4
    jmp .error
.definition:
    mov edx,5
    jmp .error
.capacity:
    mov edx,6
.error:
    mov rax,-1
    mov rcx,r13
.return:
    add rsp,288
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

r71_copy_token:
    ; Dest is at/above source and aligned to whole records. Load each field
    ; before store; different records never overlap in a partial record.
    mov rax,[rsi]
    mov [rdi],rax
    mov rax,[rsi+8]
    mov [rdi+8],rax
    mov rax,[rsi+16]
    mov [rdi+16],rax
    mov rax,[rsi+24]
    mov [rdi+24],rax
    mov rax,[rsi+32]
    mov [rdi+32],rax
    ret
