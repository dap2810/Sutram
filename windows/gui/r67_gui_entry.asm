; R67 build entry: retain the accepted GUI, redirect only its highlight CALLS.
; NASM permits instruction-name macros; recursion inhibition emits real CALL.
; Other direct/indirect CALL operands pass through verbatim. No source rewrite.
; Link the original R66 cluster object and R67 count object (build-gui.ps1).
; R73: the cluster count now feeds the status line (akshara: N) instead of
; overwriting the window title, which the editor owns (patra name, * marker).
%macro call 1
    %ifidni %1,highlight_editor
        call r67_highlight_and_clusters
    %else
        call %1
    %endif
%endmacro
%include "windows/gui/sutram_gui.asm"
%unmacro call 1

extern r67_count_editor_clusters
section .data
r67_title: db 'Sutram IDE',0
r67_title_digits: times 24 db 0
r67_unavailable: db 'Sutram IDE',0
section .bss
r67_editor_wide: resw 65536
r67_editor_utf8: resb 196608
r67_decimal: resb 24
section .text

r67_highlight_and_clusters:
    PROLOG 64
    call highlight_editor
    mov [rbp-8],rax
    cmp dword [rel is_highlighting],0
    jne .done
    call r67_refresh_cluster_title
.done:
    mov rax,[rbp-8]
    EPILOG

r67_refresh_cluster_title:
    ; No edits, selection changes, pixel advances, or font operations here.
    PROLOG 128
    cmp qword [rel h_main],0
    je .done
    mov rcx,[rel h_editor]
    test rcx,rcx
    jz .done
    lea rdx,[rel r67_editor_wide]
    mov r8d,65536
    API GetWindowTextW
    test eax,eax
    jz .zero
    cmp eax,65535
    jae .unavailable            ; do not report a truncated count
    mov r9d,eax                 ; UTF-16 units; do not confuse with UTF-8 bytes
    mov ecx,65001               ; CP_UTF8
    mov edx,0x80                ; WC_ERR_INVALID_CHARS
    lea r8,[rel r67_editor_wide]
    lea rax,[rel r67_editor_utf8]
    mov [rsp+32],rax
    mov qword [rsp+40],196608
    mov qword [rsp+48],0
    mov qword [rsp+56],0
    API WideCharToMultiByte
    test eax,eax
    jz .unavailable
    lea rcx,[rel r67_editor_utf8]
    lea rdx,[rcx+rax]
    call r67_count_editor_clusters
    cmp rax,-1
    je .unavailable
    mov [rel cluster_count],eax
    jmp .show
.zero:
    mov dword [rel cluster_count],0
    jmp .show
.unavailable:
    mov dword [rel cluster_count],-1
.show:
    call update_status
.done:
    EPILOG
