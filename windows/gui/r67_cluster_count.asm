; R67 Win64 ABI counter used by the GUI edit-notification wrapper.
; Counts the R66 helper's SCOPED clusters, not glyphs or screen columns.
; RCX=start UTF-8 byte, RDX=exclusive end; RAX=count or -1 on bad progress.
; Unicode rendering, selection and UTF-16 caret offsets remain in RichEdit.
bits 64
default rel
section .text
global r67_count_editor_clusters
extern r66_next_indic_cluster
r67_count_editor_clusters:
    push rbx
    push r12
    push r13
    sub rsp,32
    mov rbx,rcx
    mov r12,rdx
    xor r13d,r13d
    cmp rbx,r12
    ja .bad
.loop:
    cmp rbx,r12
    jae .done
    mov rcx,rbx
    mov rdx,r12
    call r66_next_indic_cluster
    cmp rax,rbx
    jbe .bad
    cmp rax,r12
    ja .bad
    mov rbx,rax
    inc r13
    jmp .loop
.done:
    mov rax,r13
    jmp .restore
.bad:
    mov rax,-1
.restore:
    add rsp,32
    pop r13
    pop r12
    pop rbx
    ret
