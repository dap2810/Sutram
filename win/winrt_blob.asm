; Native Win64 adapter embedded in generated programs. NASM only.
; Loader-resolved IAT in RW/non-executable .data; no writes to RX code.
bits 64
default rel
%include "win/pe_layout.inc"
rt_init:
    push rbx
    push rbp
    mov rbp,rsp
    and rsp,-16
    sub rsp,32
    call rt_import_base
    call qword [rbx+RT_GetConsoleOutputCP]
    mov [rbx+RT_ORIGINAL_CP],eax
    mov ecx,65001
    call qword [rbx+RT_SetConsoleOutputCP]
    mov ecx,1                     ; R124: commit reserved pages when first touched (rt_veh)
    lea rdx,[rel rt_veh]
    call qword [rbx+RT_AddVectoredExceptionHandler]
    mov rsp,rbp
    pop rbp
    pop rbx
    ret
rt_import_base:
    ; ImageBase from PEB, then data RVA from the emitted section header.
    mov rbx,[gs:0x60]
    mov rbx,[rbx+0x10]
    mov eax,[rbx+0x17c]
    lea rbx,[rbx+rax+RT_GLOBAL_BYTES]
    ret
rt_syscall:
    push rbx
    push rbp
    push rsi
    push rdi
    push rdx
    push r8
    push r9
    push r10
    push r11
    push r12
    push r13
    push r14
    push r15
    mov r12,rax
    mov r13,rdi
    mov r14,rsi
    mov r15,rdx
    mov rbp,rsp
    and rsp,-16
    sub rsp,320
    movdqu [rsp+64],xmm0
    movdqu [rsp+80],xmm1
    movdqu [rsp+96],xmm2
    movdqu [rsp+112],xmm3
    movdqu [rsp+128],xmm4
    movdqu [rsp+144],xmm5
    movdqu [rsp+160],xmm6
    movdqu [rsp+176],xmm7
    movdqu [rsp+192],xmm8
    movdqu [rsp+208],xmm9
    movdqu [rsp+224],xmm10
    movdqu [rsp+240],xmm11
    movdqu [rsp+256],xmm12
    movdqu [rsp+272],xmm13
    movdqu [rsp+288],xmm14
    movdqu [rsp+304],xmm15
    call rt_import_base
    cmp r12,0
    je .read
    cmp r12,1
    je .write
    cmp r12,2
    je .open
    cmp r12,3
    je .close
    cmp r12,9
    je .alloc
    cmp r12,60
    je .exit
    mov rax,-38                   ; ENOSYS, never fake success.
    jmp .done
.write:
    call rt_touch
    mov rcx,r13
    cmp r13,1
    je .stdout
    cmp r13,2
    jne .write_handle
    mov ecx,-12
    jmp .std_write
.stdout:
    mov ecx,-11
.std_write:
    call qword [rbx+RT_GetStdHandle]
    mov rcx,rax
.write_handle:
    mov rdx,r14
    mov r8,r15
    lea r9,[rsp+56]
    mov dword [rsp+56],0
    mov qword [rsp+32],0
    call qword [rbx+RT_WriteFile]
    jmp .io_result
.read:
    call rt_touch
    mov rcx,r13
    test r13,r13
    jnz .read_handle
    mov ecx,-10
    call qword [rbx+RT_GetStdHandle]
    mov rcx,rax
.read_handle:
    mov rdx,r14
    mov r8,r15
    lea r9,[rsp+56]
    mov dword [rsp+56],0
    mov qword [rsp+32],0
    call qword [rbx+RT_ReadFile]
.io_result:
    test eax,eax
    jz .error
    mov eax,[rsp+56]
    jmp .done
.open:
    mov rcx,r13
    mov edx,0x80000000
    mov eax,3
    test r14,1
    jz .open_args
    mov edx,0x40000000
    mov eax,2
.open_args:
    mov r8d,3
    xor r9d,r9d
    mov [rsp+32],rax
    mov qword [rsp+40],0x80
    mov qword [rsp+48],0
    call qword [rbx+RT_CreateFileA]
    jmp .done
.close:
    mov rcx,r13
    call qword [rbx+RT_CloseHandle]
    test eax,eax
    jz .error
    xor eax,eax
    jmp .done
.alloc:
    ; R124: mmap with MAP_NORESERVE (0x4000: the arena, each kosh region) only reserves; rt_veh commits
    ; a page's 64 KiB when it is first touched, as Linux does. Anything else is reserved and committed.
    xor ecx,ecx
    mov rdx,r14
    mov r8d,0x3000
    test r10d,0x4000
    jz .alloc_go
    mov r8d,0x2000
.alloc_go:
    mov r9d,4
    call qword [rbx+RT_VirtualAlloc]
    test rax,rax
    jz .error
    jmp .done
.exit:
    mov ecx,[rbx+RT_ORIGINAL_CP]
    test ecx,ecx
    jz .exit_ready
    call qword [rbx+RT_SetConsoleOutputCP]
.exit_ready:
    mov rcx,r13
    call qword [rbx+RT_ExitProcess]
.error:
    mov rax,-1
.done:
    movdqu xmm0,[rsp+64]
    movdqu xmm1,[rsp+80]
    movdqu xmm2,[rsp+96]
    movdqu xmm3,[rsp+112]
    movdqu xmm4,[rsp+128]
    movdqu xmm5,[rsp+144]
    movdqu xmm6,[rsp+160]
    movdqu xmm7,[rsp+176]
    movdqu xmm8,[rsp+192]
    movdqu xmm9,[rsp+208]
    movdqu xmm10,[rsp+224]
    movdqu xmm11,[rsp+240]
    movdqu xmm12,[rsp+256]
    movdqu xmm13,[rsp+272]
    movdqu xmm14,[rsp+288]
    movdqu xmm15,[rsp+304]
    mov rsp,rbp
    pop r15
    pop r14
    pop r13
    pop r12
    pop r11
    pop r10
    pop r9
    pop r8
    pop rdx
    pop rdi
    pop rsi
    pop rbp
    pop rbx
    ret
; rt_touch: before ReadFile / WriteFile, read one byte of each page of [r14, r14+r15), so a page still only
; reserved is committed by rt_veh first (the kernel does not fault on the program's behalf; it would fail).
rt_touch:
    test r15,r15
    jz .t_done
    mov r10,r14
    and r10,-4096
    lea r11,[r14+r15]
.t_loop:
    cmp r10,r11
    jae .t_done
    mov al,[r10]
    add r10,4096
    jmp .t_loop
.t_done:
    ret

; rt_veh (a vectored exception handler, R124): an access violation inside memory this program only reserved
; (MEM_RESERVE, MEM_PRIVATE, not this thread's stack) commits up to 64 KiB there, read-write, and the faulting
; instruction runs again. Every other exception goes on to the next handler.
rt_veh:
    push rbx
    push rsi
    push rdi
    sub rsp,96
    mov rax,[rcx]
    cmp dword [rax],0xC0000005
    jne .v_search
    mov rsi,[rax+0x28]
    mov rax,[gs:0x08]             ; this thread's stack: never ours to commit
    cmp rsi,rax
    jae .v_notstack
    mov rax,[gs:0x1478]
    cmp rsi,rax
    jae .v_search
.v_notstack:
    call rt_import_base
    mov rcx,rsi
    lea rdx,[rsp+48]
    mov r8d,48
    call qword [rbx+RT_VirtualQuery]
    test rax,rax
    jz .v_search
    cmp dword [rsp+48+32],0x2000  ; State = MEM_RESERVE
    jne .v_search
    cmp dword [rsp+48+40],0x20000 ; Type = MEM_PRIVATE
    jne .v_search
    mov rdx,[rsp+48+24]           ; RegionSize from this page
    cmp rdx,0x10000
    jbe .v_size
    mov edx,0x10000
.v_size:
    mov rcx,rsi
    and rcx,-4096
    mov r8d,0x1000                ; MEM_COMMIT
    mov r9d,4
    call qword [rbx+RT_VirtualAlloc]
    test rax,rax
    jz .v_search
    mov eax,-1                    ; EXCEPTION_CONTINUE_EXECUTION
    jmp .v_ret
.v_search:
    xor eax,eax                   ; EXCEPTION_CONTINUE_SEARCH
.v_ret:
    add rsp,96
    pop rdi
    pop rsi
    pop rbx
    ret
rt_end:
db 'SUTRTV01'
dd rt_syscall-rt_init,rt_end-rt_init
