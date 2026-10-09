; ============================================================================
;  Sutram-Setup.exe  —  native Windows installer for Sutram (सूत्रम्)
;
;  Pure NASM x86-64.  No C runtime, no toolkit, no import libraries, no
;  external build tools beyond NASM and ld.  Builds to a PE32+ GUI-subsystem
;  executable that resolves every Win32 entry point at runtime by walking the
;  PEB to kernel32 and calling GetProcAddress — the same pure-NASM mechanism
;  the Sutram GUI IDE uses.  End users need no compiler, no NASM, no Python,
;  no MinGW, no NSIS.
;
;  What it does
;    1. Asks the user to confirm.
;    2. Writes three embedded artifacts to %TEMP%\Sutram-Setup:
;         payload.zip, install-core.ps1, uninstall-core.ps1
;    3. Runs install-core.ps1 through Windows PowerShell 5.1 (present on
;       every supported Windows 10/11) with -ExecutionPolicy Bypass.
;    4. Reports success or failure.
;
;  All installation work is per-user and unelevated.  Nothing requests UAC
;  elevation, disables a security feature, writes HKLM, or touches
;  Program Files.
;
;  Build:
;     nasm -f win64 windows/native-installer/sutram_setup.asm -o setup.obj
;     ld -mi386pep --subsystem windows --entry=_start -o Sutram-Setup.exe setup.obj
;  Requires payload.zip, install-core.ps1 and uninstall-core.ps1 in the
;  working directory at assembly time (pulled in with incbin).
; ============================================================================

bits 64
default rel

%define INFINITE 0xFFFFFFFF
%define MB_YESNO 0x00000004
%define MB_OK 0x00000000
%define MB_ICONQUESTION 0x00000020
%define MB_ICONINFORMATION 0x00000040
%define MB_ICONERROR 0x00000010
%define IDYES 6
%define CREATE_ALWAYS 2
%define FILE_ATTRIBUTE_NORMAL 0x80
%define GENERIC_WRITE 0x40000000
%define INVALID_HANDLE_VALUE -1
%define MAXP 1024

; ---------------------------------------------------------------------------
%macro PROLOG 1
    push rbp
    mov  rbp, rsp
    sub  rsp, %1
%endmacro
%macro EPILOG 0
    leave
    ret
%endmacro
%macro PTR 2
    lea  %1, [rel %2]
%endmacro
%macro API 1
    call qword [rel p_%1]
%endmacro
%macro IMPORTS 1
    dq n_%1, p_%1
%endmacro

; ---------------------------------------------------------------------------
section .data
; UTF-16 literal helper: ASCII characters, one 16-bit unit each, NUL-terminated.
%macro u16 1
    %strlen %%len %1
    %assign %%i 1
    %rep %%len
        db %substr(%1,%%i,1), 0
        %assign %%i %%i+1
    %endrep
    dw 0
%endmacro

name_kernel32 db 'kernel32.dll',0
name_user32   db 'user32.dll',0

n_LoadLibraryA          db 'LoadLibraryA',0
n_GetProcAddress        db 'GetProcAddress',0
n_ExitProcess           db 'ExitProcess',0
n_GetTempPathW          db 'GetTempPathW',0
n_GetEnvironmentVariableW db 'GetEnvironmentVariableW',0
n_GetModuleFileNameW    db 'GetModuleFileNameW',0
n_CreateDirectoryW      db 'CreateDirectoryW',0
n_CreateFileW           db 'CreateFileW',0
n_WriteFile             db 'WriteFile',0
n_CloseHandle           db 'CloseHandle',0
n_CreateProcessW        db 'CreateProcessW',0
n_WaitForSingleObject   db 'WaitForSingleObject',0
n_GetExitCodeProcess    db 'GetExitCodeProcess',0
n_lstrcpyW              db 'lstrcpyW',0
n_lstrcatW              db 'lstrcatW',0
n_MessageBoxW           db 'MessageBoxW',0
n_GetCommandLineW       db 'GetCommandLineW',0
n_RegisterClassExW      db 'RegisterClassExW',0
n_CreateWindowExW       db 'CreateWindowExW',0
n_ShowWindow            db 'ShowWindow',0
n_UpdateWindow          db 'UpdateWindow',0
n_GetMessageW           db 'GetMessageW',0
n_TranslateMessage      db 'TranslateMessage',0
n_DispatchMessageW      db 'DispatchMessageW',0
n_DefWindowProcW        db 'DefWindowProcW',0
n_PostQuitMessage       db 'PostQuitMessage',0
n_DestroyWindow         db 'DestroyWindow',0
n_SetWindowTextW        db 'SetWindowTextW',0
n_LoadImageW            db 'LoadImageW',0

kernel_table:
    IMPORTS LoadLibraryA
    IMPORTS GetProcAddress
    IMPORTS ExitProcess
    IMPORTS GetTempPathW
    IMPORTS GetEnvironmentVariableW
    IMPORTS GetModuleFileNameW
    IMPORTS CreateDirectoryW
    IMPORTS CreateFileW
    IMPORTS WriteFile
    IMPORTS CloseHandle
    IMPORTS CreateProcessW
    IMPORTS WaitForSingleObject
    IMPORTS GetExitCodeProcess
    IMPORTS lstrcpyW
    IMPORTS lstrcatW
    IMPORTS GetCommandLineW
    dq 0, 0
user_table:
    IMPORTS MessageBoxW
    IMPORTS RegisterClassExW
    IMPORTS CreateWindowExW
    IMPORTS ShowWindow
    IMPORTS UpdateWindow
    IMPORTS GetMessageW
    IMPORTS TranslateMessage
    IMPORTS DispatchMessageW
    IMPORTS DefWindowProcW
    IMPORTS PostQuitMessage
    IMPORTS DestroyWindow
    IMPORTS SetWindowTextW
    IMPORTS LoadImageW
    dq 0, 0

msg_title:      u16 "Sutram Setup"
msg_welcome:    u16 "Install Sutram for this Windows user?"
                dw 13,0,10,0,13,0,10,0
                u16 "Sutram is the Sanskrit-keyword programming language with a native compiler and a GUI IDE."
                dw 13,0,10,0,13,0,10,0
                u16 "It installs for you alone, into your own AppData folder."
                dw 13,0,10,0,13,0,10,0
                u16 "No administrator rights are needed and Windows security is not changed."
                dw 13,0,10,0
                u16 "Click Yes to install, or No to cancel."
                dw 0
msg_done:       u16 "Sutram installed successfully."
                dw 13,0,10,0,13,0,10,0
                u16 "Open it from the Start Menu, or run:  sutram --version"
                dw 13,0,10,0,13,0,10,0
                u16 "A log was written to the setup folder in your temp directory."
                dw 0
msg_failed:     u16 "Sutram setup did not complete."
                dw 13,0,10,0,13,0,10,0
                u16 "The log file in your temp directory has the details."
                dw 13,0,10,0
                u16 "The script undoes its own work on failure, so nothing is left half-installed."
                dw 0
msg_nopower:    u16 "Sutram setup could not start Windows PowerShell."
                dw 13,0,10,0,13,0,10,0
                u16 "Windows PowerShell 5.1 is normally present on Windows 10 and 11."
                dw 13,0,10,0
                u16 "If it is missing, run the included install-core.ps1 manually."
                dw 0
msg_uninst_done: u16 "Sutram was removed from this user account."
                dw 13,0,10,0,13,0,10,0
                u16 "Your own files and any PATH entry you added by hand were left alone."
                dw 0
msg_uninst_failed: u16 "Sutram could not be fully removed."
                dw 13,0,10,0,13,0,10,0
                u16 "The log file in your temp directory has the details."
                dw 0

arg_uninstall:  u16 "--uninstall"
env_localappdata: u16 "LOCALAPPDATA"
setup_subdir:   u16 "Sutram-Setup"
fname_payload:  u16 "\payload.zip"
fname_install:  u16 "\install-core.ps1"
fname_uninst:   u16 "\uninstall-core.ps1"
fname_log:      u16 "\install.log"
sub_programs:   u16 "\Programs\Sutram"
ps_prefix:      u16 "powershell.exe -NoProfile -ExecutionPolicy Bypass -File "
flag_payloadzip: u16 " -PayloadZip "
flag_installdir: u16 " -InstallDir "
flag_setupexepath: u16 " -SetupExePath "
flag_logpath:   u16 " -LogPath "
flag_addpath:   u16 " -AddPath"
flag_desktop:   u16 " -DesktopShortcut"
flag_selfpath:  u16 " -SelfPath "
ps_uninst:      u16 "powershell.exe -NoProfile -ExecutionPolicy Bypass -File "
fname_ulog:     u16 "\uninstall.log"
quote:          dw '"',0

align 8
; --- installer window constants ---
%define WS_OVERLAPPEDWINDOW 0x00CF0000
%define WS_VISIBLE 0x10000000
%define WS_CHILD 0x40000000
%define CW_USEDEFAULT 0x80000000
%define SW_SHOW 5
%define WM_CREATE 1
%define WM_DESTROY 2
%define WM_CLOSE 0x10
%define WM_COMMAND 0x111
%define ID_INSTALL 1001
%define ID_CANCEL 1002
%define ID_STATUS 1003

cls_setup:      u16 "SutramSetupWindow"
cls_button:     u16 "BUTTON"
cls_static:     u16 "STATIC"
win_title:      u16 "Sutram Setup"
txt_head:       u16 "Install Sutram for this Windows user"
txt_body:       u16 "Sutram is the Sanskrit-keyword programming language."
                dw 13,0,10,0
                u16 "It will be installed into your own AppData folder."
                dw 13,0,10,0,13,0,10,0
                u16 "No administrator rights are needed."
                dw 13,0,10,0
                u16 "Windows security settings are not changed."
                dw 0
txt_idle:       u16 "Ready to install."
txt_working:    u16 "Installing... please wait."
txt_installed:  u16 "Installed. Look for Sutram IDE in your Start Menu."
btn_install:    u16 "Install"
btn_cancel:     u16 "Cancel"
icon_file:      u16 "sutram.ico"

blob_payload:   incbin "payload.zip"
blob_payload_end:
blob_install:   incbin "install-core.ps1"
blob_install_end:
blob_uninst:    incbin "uninstall-core.ps1"
blob_uninst_end:

; ---------------------------------------------------------------------------
section .bss
align 16
p_LoadLibraryA          resq 1
p_GetProcAddress        resq 1
p_ExitProcess           resq 1
p_GetTempPathW          resq 1
p_GetEnvironmentVariableW resq 1
p_GetModuleFileNameW    resq 1
p_CreateDirectoryW      resq 1
p_CreateFileW           resq 1
p_WriteFile             resq 1
p_CloseHandle           resq 1
p_CreateProcessW        resq 1
p_WaitForSingleObject   resq 1
p_GetExitCodeProcess    resq 1
p_lstrcpyW              resq 1
p_lstrcatW              resq 1
p_MessageBoxW           resq 1
p_GetCommandLineW       resq 1
p_RegisterClassExW      resq 1
p_CreateWindowExW       resq 1
p_ShowWindow            resq 1
p_UpdateWindow          resq 1
p_GetMessageW           resq 1
p_TranslateMessage      resq 1
p_DispatchMessageW      resq 1
p_DefWindowProcW        resq 1
p_PostQuitMessage       resq 1
p_DestroyWindow         resq 1
p_SetWindowTextW        resq 1
p_LoadImageW            resq 1

h_kernel:       resq 1
h_user:         resq 1
temp_path:      resw MAXP
setup_dir:      resw MAXP
local_appdata:  resw MAXP
install_dir:    resw MAXP
self_path:      resw MAXP
log_path:       resw MAXP
payload_path:   resw MAXP
install_ps1:    resw MAXP
uninst_ps1:     resw MAXP
cmdline:        resw 8192
written:        resd 1
startupinfo:    resb 104
procinfo:       resb 24
exit_code:      resd 1

; --- installer window state ---
wndclass:       resb 80
msg_struct:     resb 48
hwnd_main:      resq 1
hwnd_head:      resq 1
hwnd_body:      resq 1
hwnd_status:    resq 1
hwnd_install:   resq 1
hwnd_cancel:    resq 1
h_icon:         resq 1
install_done:   resd 1

; ---------------------------------------------------------------------------
section .text
global _start

; --- walk the PEB to kernel32's base address -------------------------------
win_kernel32:
    mov  rax, [gs:0x60]
    test rax, rax
    jz   .fail
    mov  rax, [rax+0x18]
    test rax, rax
    jz   .fail
    mov  rax, [rax+0x20]
    test rax, rax
    jz   .fail
    mov  rax, [rax]
    test rax, rax
    jz   .fail
    mov  rax, [rax]
    test rax, rax
    jz   .fail
    mov  rax, [rax+0x20]
    ret
.fail:
    xor  eax, eax
    ret

; --- rdi = export name, rax = address or 0 ---------------------------------
win_resolve:
    push rbx
    push rsi
    push rdi
    push r12
    push r13
    push r14
    push r15
    mov  r14, rdi
    call win_kernel32
    test rax, rax
    jz   .fail
    mov  rbx, rax
    mov  eax, [rbx+0x3c]
    add  rax, rbx
    mov  r12d, [rax+24+0x70]
    test r12d, r12d
    jz   .fail
    add  r12, rbx
    mov  r13d, [r12+0x20]
    add  r13, rbx
    mov  r15d, [r12+0x18]
    xor  ecx, ecx
.name:
    cmp  ecx, r15d
    jae  .fail
    mov  eax, [r13+rcx*4]
    add  rax, rbx
    mov  rsi, rax
    mov  rdi, r14
.cmp:
    mov  al, [rsi]
    cmp  al, [rdi]
    jne  .next
    test al, al
    jz   .found
    inc  rsi
    inc  rdi
    jmp  .cmp
.next:
    inc  ecx
    jmp  .name
.found:
    mov  r13d, [r12+0x24]
    add  r13, rbx
    movzx ecx, word [r13+rcx*2]
    mov  r13d, [r12+0x1c]
    add  r13, rbx
    mov  eax, [r13+rcx*4]
    add  rax, rbx
    jmp  .done
.fail:
    xor  eax, eax
.done:
    pop  r15
    pop  r14
    pop  r13
    pop  r12
    pop  rdi
    pop  rsi
    pop  rbx
    ret

; --- rcx = dll handle, rdx = table of (name ptr, slot ptr) pairs, 0,0 ends --
fill_table:
    PROLOG 80
    mov  [rbp-8], rcx
    mov  [rbp-16], rdx
.loop:
    mov  r10, [rbp-16]
    mov  rdx, [r10]
    test rdx, rdx
    jz   .ok
    mov  rcx, [rbp-8]
    API  GetProcAddress
    test rax, rax
    jz   .fail
    mov  r10, [rbp-16]
    mov  r11, [r10+8]
    mov  [r11], rax
    add  qword [rbp-16], 16
    jmp  .loop
.ok:
    mov  eax, 1
    jmp  .done
.fail:
    xor  eax, eax
.done:
    EPILOG

; --- resolve every entry point we use --------------------------------------
init_apis:
    PROLOG 64
    PTR  rdi, n_LoadLibraryA
    call win_resolve
    mov  [rel p_LoadLibraryA], rax
    test rax, rax
    jz   .fail
    PTR  rdi, n_GetProcAddress
    call win_resolve
    mov  [rel p_GetProcAddress], rax
    test rax, rax
    jz   .fail

    PTR  rcx, name_kernel32
    API  LoadLibraryA
    test rax, rax
    jz   .fail
    mov  [rel h_kernel], rax
    mov  rcx, rax
    PTR  rdx, kernel_table
    call fill_table
    test eax, eax
    jz   .fail

    PTR  rcx, name_user32
    API  LoadLibraryA
    test rax, rax
    jz   .fail
    mov  [rel h_user], rax
    mov  rcx, rax
    PTR  rdx, user_table
    call fill_table
    test eax, eax
    jz   .fail

    mov  eax, 1
    jmp  .end
.fail:
    xor  eax, eax
.end:
    EPILOG

; --- write a file.  rcx = UTF-16 path, rdx = data, r8 = size ---------------
;     returns eax = 1 ok / 0 fail
write_file:
    PROLOG 96
    mov  [rbp-8], rdx
    mov  [rbp-16], r8
    mov  rdx, GENERIC_WRITE
    xor  r8d, r8d
    xor  r9d, r9d
    mov  qword [rsp+32], CREATE_ALWAYS
    mov  qword [rsp+40], FILE_ATTRIBUTE_NORMAL
    mov  qword [rsp+48], 0
    API  CreateFileW
    cmp  rax, INVALID_HANDLE_VALUE
    je   .fail
    mov  [rbp-24], rax
    mov  rcx, rax
    mov  rdx, [rbp-8]
    mov  r8d, dword [rbp-16]
    PTR  r9, written
    mov  qword [rsp+32], 0
    API  WriteFile
    mov  [rbp-28], eax
    mov  rcx, [rbp-24]
    API  CloseHandle
    mov  eax, [rbp-28]
    test eax, eax
    jz   .fail
    mov  eax, 1
    jmp  .done
.fail:
    xor  eax, eax
.done:
    EPILOG

; --- dest = base + suffix.  rcx = dest, rdx = base, r8 = suffix ------------
join:
    PROLOG 48
    mov  [rbp-8], rcx
    mov  [rbp-16], rdx
    mov  [rbp-24], r8
    mov  rdx, [rbp-16]
    API  lstrcpyW
    mov  rcx, [rbp-8]
    mov  rdx, [rbp-24]
    API  lstrcatW
    EPILOG

; --- append a literal to cmdline.  rcx = literal ---------------------------
app:
    PROLOG 48
    mov  rdx, rcx
    PTR  rcx, cmdline
    API  lstrcatW
    EPILOG

; --- rcx = haystack (UTF-16), rdx = needle (UTF-16) -> rax = ptr or 0 -----
find_w:
    PROLOG 64
    mov  [rbp-8], rcx
    mov  [rbp-16], rdx
.outer:
    mov  r10, [rbp-8]
    mov  ax, [r10]
    test ax, ax
    jz   .none
    mov  r11, [rbp-16]
    mov  rcx, r10
.inner:
    mov  ax, [r11]
    test ax, ax
    jz   .hit
    mov  dx, [rcx]
    cmp  dx, ax
    jne  .next
    add  r11, 2
    add  rcx, 2
    jmp  .inner
.next:
    add  qword [rbp-8], 2
    jmp  .outer
.hit:
    mov  rax, [rbp-8]
    jmp  .done
.none:
    xor  eax, eax
.done:
    EPILOG

; --- truncate rcx (UTF-16 path) after the last backslash -------------------
dirname:
    PROLOG 48
    mov  [rbp-8], rcx
    mov  r10, rcx
    xor  r11, r11            ; last separator pointer
.scan:
    mov  ax, [r10]
    test ax, ax
    jz   .end
    cmp  ax, 92              ; backslash
    jne  .fwd
    mov  r11, r10
    jmp  .cont
.fwd:
    cmp  ax, 47              ; forward slash
    jne  .cont
    mov  r11, r10
.cont:
    add  r10, 2
    jmp  .scan
.end:
    test r11, r11
    jz   .done
    mov  word [r11], 0
.done:
    EPILOG

; ---------------------------------------------------------------------------
_start:
    ; A PE entry point receives a 16-byte aligned stack with no return
    ; address.  Normalise it to look like a normal function entry
    ; (rsp % 16 == 8) so PROLOG keeps every subsequent call aligned.
    and  rsp, -16
    sub  rsp, 8
    PROLOG 96
    call init_apis
    test eax, eax
    jz   .quit

    ; Uninstall mode?  The Start Menu uninstaller is a copy of this exe
    ; invoked as "Sutram-Uninstall.exe --uninstall".
    API  GetCommandLineW
    mov  rcx, rax
    PTR  rdx, arg_uninstall
    call find_w
    test rax, rax
    jz   .do_install
    call do_uninstall
    jmp  .quit
.do_install:

    ; Prefer the graphical installer window; fall back to a dialog if
    ; the window cannot be created (no interactive desktop, policy).
    call create_window
    test eax, eax
    jnz  .run_gui

    ; ---- fallback: single confirmation dialog ----
    xor  ecx, ecx
    PTR  rdx, msg_welcome
    PTR  r8,  msg_title
    mov  r9d, MB_YESNO | MB_ICONQUESTION
    API  MessageBoxW
    cmp  eax, IDYES
    jne  .quit
    call do_install
    cmp  eax, 2
    je   .mb_nopw
    test eax, eax
    jnz  .mb_fail
    xor  ecx, ecx
    PTR  rdx, msg_done
    PTR  r8,  msg_title
    mov  r9d, MB_OK | MB_ICONINFORMATION
    API  MessageBoxW
    jmp  .quit
.mb_nopw:
    xor  ecx, ecx
    PTR  rdx, msg_nopower
    PTR  r8,  msg_title
    mov  r9d, MB_OK | MB_ICONERROR
    API  MessageBoxW
    jmp  .quit
.mb_fail:
    xor  ecx, ecx
    PTR  rdx, msg_failed
    PTR  r8,  msg_title
    mov  r9d, MB_OK | MB_ICONERROR
    API  MessageBoxW
    jmp  .quit

.run_gui:
    call gui_loop
    jmp  .quit

.quit:
    xor  ecx, ecx
    API  ExitProcess

; ---------------------------------------------------------------------------
; Uninstall mode.  Reached when the command line contains --uninstall.
; ---------------------------------------------------------------------------
do_uninstall:
    PROLOG 96

    ; self path, then its directory becomes the install directory
    xor  ecx, ecx
    PTR  rdx, self_path
    mov  r8d, MAXP
    API  GetModuleFileNameW
    PTR  rcx, install_dir
    PTR  rdx, self_path
    API  lstrcpyW
    PTR  rcx, install_dir
    call dirname

    ; scratch dir for the script and the log
    PTR  rcx, temp_path
    mov  edx, MAXP
    API  GetTempPathW
    PTR  rcx, setup_dir
    PTR  rdx, temp_path
    PTR  r8,  setup_subdir
    call join
    PTR  rcx, setup_dir
    xor  edx, edx
    API  CreateDirectoryW

    PTR  rcx, uninst_ps1
    PTR  rdx, setup_dir
    PTR  r8,  fname_uninst
    call join
    PTR  rcx, log_path
    PTR  rdx, setup_dir
    PTR  r8,  fname_ulog
    call join

    ; write the uninstall script
    PTR  rcx, uninst_ps1
    PTR  rdx, blob_uninst
    mov  r8,  blob_uninst_end - blob_uninst
    call write_file
    test eax, eax
    jz   .failed

    ; powershell ... -InstallDir <dir> -SelfPath <exe> -LogPath <log>
    PTR  rcx, ps_uninst
    call app
    PTR  rcx, quote
    call app
    PTR  rcx, uninst_ps1
    call app
    PTR  rcx, quote
    call app

    PTR  rcx, flag_installdir
    call app
    PTR  rcx, quote
    call app
    PTR  rcx, install_dir
    call app
    PTR  rcx, quote
    call app

    PTR  rcx, flag_selfpath
    call app
    PTR  rcx, quote
    call app
    PTR  rcx, self_path
    call app
    PTR  rcx, quote
    call app

    PTR  rcx, flag_logpath
    call app
    PTR  rcx, quote
    call app
    PTR  rcx, log_path
    call app
    PTR  rcx, quote
    call app

    PTR  rdi, startupinfo
    mov  ecx, 13
    xor  eax, eax
    rep  stosq
    PTR  rdi, procinfo
    mov  ecx, 3
    xor  eax, eax
    rep  stosq
    PTR  rax, startupinfo
    mov  dword [rax], 104

    xor  ecx, ecx
    PTR  rdx, cmdline
    xor  r8d, r8d
    xor  r9d, r9d
    mov  qword [rsp+32], 0
    mov  qword [rsp+40], 0
    mov  qword [rsp+48], 0
    mov  qword [rsp+56], 0
    PTR  rax, startupinfo
    mov  [rsp+64], rax
    PTR  rax, procinfo
    mov  [rsp+72], rax
    API  CreateProcessW
    test eax, eax
    jz   .failed

    mov  rcx, [rel procinfo]
    mov  edx, INFINITE
    API  WaitForSingleObject
    mov  rcx, [rel procinfo]
    PTR  rdx, exit_code
    API  GetExitCodeProcess

    cmp  dword [rel exit_code], 0
    jne  .failed
    xor  ecx, ecx
    PTR  rdx, msg_uninst_done
    PTR  r8,  msg_title
    mov  r9d, MB_OK | MB_ICONINFORMATION
    API  MessageBoxW
    jmp  .quit

.failed:
    xor  ecx, ecx
    PTR  rdx, msg_uninst_failed
    PTR  r8,  msg_title
    mov  r9d, MB_OK | MB_ICONERROR
    API  MessageBoxW
.quit:
    xor  ecx, ecx
    API  ExitProcess

; ---------------------------------------------------------------------------
; Perform the installation.  Returns eax: 0 ok, 1 failed, 2 no PowerShell.
do_install:
    PROLOG 96
    ; 2. %TEMP%\Sutram-Setup
    PTR  rcx, temp_path
    mov  edx, MAXP
    API  GetTempPathW
    PTR  rcx, setup_dir
    PTR  rdx, temp_path
    PTR  r8,  setup_subdir
    call join
    PTR  rcx, setup_dir
    xor  edx, edx
    API  CreateDirectoryW

    ; 3. Paths.
    PTR  rcx, payload_path
    PTR  rdx, setup_dir
    PTR  r8,  fname_payload
    call join
    PTR  rcx, install_ps1
    PTR  rdx, setup_dir
    PTR  r8,  fname_install
    call join
    PTR  rcx, uninst_ps1
    PTR  rdx, setup_dir
    PTR  r8,  fname_uninst
    call join
    PTR  rcx, log_path
    PTR  rdx, setup_dir
    PTR  r8,  fname_log
    call join

    xor  ecx, ecx
    PTR  rdx, self_path
    mov  r8d, MAXP
    API  GetModuleFileNameW

    PTR  rcx, env_localappdata
    PTR  rdx, local_appdata
    mov  r8d, MAXP
    API  GetEnvironmentVariableW
    PTR  rcx, install_dir
    PTR  rdx, local_appdata
    PTR  r8,  sub_programs
    call join

    ; 4. Write the three artifacts.
    PTR  rcx, payload_path
    PTR  rdx, blob_payload
    mov  r8,  blob_payload_end - blob_payload
    call write_file
    test eax, eax
    jz   .dfail

    PTR  rcx, install_ps1
    PTR  rdx, blob_install
    mov  r8,  blob_install_end - blob_install
    call write_file
    test eax, eax
    jz   .dfail

    PTR  rcx, uninst_ps1
    PTR  rdx, blob_uninst
    mov  r8,  blob_uninst_end - blob_uninst
    call write_file
    test eax, eax
    jz   .dfail

    ; 5. Build the PowerShell command line.
    PTR  rcx, ps_prefix
    call app
    PTR  rcx, quote
    call app
    PTR  rcx, install_ps1
    call app
    PTR  rcx, quote
    call app

    PTR  rcx, flag_payloadzip
    call app
    PTR  rcx, quote
    call app
    PTR  rcx, payload_path
    call app
    PTR  rcx, quote
    call app

    PTR  rcx, flag_installdir
    call app
    PTR  rcx, quote
    call app
    PTR  rcx, install_dir
    call app
    PTR  rcx, quote
    call app

    PTR  rcx, flag_setupexepath
    call app
    PTR  rcx, quote
    call app
    PTR  rcx, self_path
    call app
    PTR  rcx, quote
    call app

    PTR  rcx, flag_logpath
    call app
    PTR  rcx, quote
    call app
    PTR  rcx, log_path
    call app
    PTR  rcx, quote
    call app

    PTR  rcx, flag_addpath
    call app
    PTR  rcx, flag_desktop
    call app

    ; 6. Zero STARTUPINFOW / PROCESS_INFORMATION.
    PTR  rdi, startupinfo
    mov  ecx, 13
    xor  eax, eax
    rep  stosq
    PTR  rdi, procinfo
    mov  ecx, 3
    xor  eax, eax
    rep  stosq
    PTR  rax, startupinfo
    mov  dword [rax], 104

    ; 7. CreateProcessW(NULL, cmdline, NULL, NULL, FALSE, 0, NULL, NULL, &si, &pi)
    xor  ecx, ecx
    PTR  rdx, cmdline
    xor  r8d, r8d
    xor  r9d, r9d
    mov  qword [rsp+32], 0
    mov  qword [rsp+40], 0
    mov  qword [rsp+48], 0
    mov  qword [rsp+56], 0
    PTR  rax, startupinfo
    mov  [rsp+64], rax
    PTR  rax, procinfo
    mov  [rsp+72], rax
    API  CreateProcessW
    test eax, eax
    jz   .dnopw


    ; wait for PowerShell, then return a status code
    mov  rcx, [rel procinfo]
    mov  edx, INFINITE
    API  WaitForSingleObject
    mov  rcx, [rel procinfo]
    PTR  rdx, exit_code
    API  GetExitCodeProcess
    cmp  dword [rel exit_code], 0
    jne  .dfail
    xor  eax, eax            ; 0 = installed
    EPILOG
.dnopw:
    mov  eax, 2              ; 2 = PowerShell could not start
    EPILOG
.dfail:
    mov  eax, 1              ; 1 = install failed
    EPILOG

; ---------------------------------------------------------------------------
; Create the installer window.  eax = 1 on success, 0 if it could not be made.
; ---------------------------------------------------------------------------
create_window:
    PROLOG 128

    ; Icon from sutram.ico next to the exe; ignore failure (icon is cosmetic).
    xor  ecx, ecx
    PTR  rdx, icon_file
    mov  r8d, 1                 ; IMAGE_ICON
    xor  r9d, r9d
    mov  qword [rsp+32], 0
    mov  qword [rsp+40], 0x10   ; LR_LOADFROMFILE
    API  LoadImageW
    mov  [rel h_icon], rax

    ; WNDCLASSEXW
    PTR  rdi, wndclass
    mov  ecx, 10
    xor  eax, eax
    rep  stosq
    PTR  rax, wndclass
    mov  dword [rax+0], 80      ; cbSize
    PTR  r10, wndproc
    mov  [rax+8], r10           ; lpfnWndProc
    mov  r10, [rel h_icon]
    mov  [rax+32], r10          ; hIcon
    mov  [rax+72], r10          ; hIconSm
    mov  qword [rax+48], 16     ; hbrBackground = COLOR_BTNFACE+1
    PTR  r10, cls_setup
    mov  [rax+64], r10          ; lpszClassName

    PTR  rcx, wndclass
    API  RegisterClassExW

    ; CreateWindowExW
    xor  ecx, ecx
    PTR  rdx, cls_setup
    PTR  r8,  win_title
    mov  r9d, WS_OVERLAPPEDWINDOW
    mov  eax, CW_USEDEFAULT     ; zero-extend: must not sign-extend to 0xFFFFFFFF80000000
    mov  [rsp+32], rax
    mov  [rsp+40], rax
    mov  qword [rsp+48], 580
    mov  qword [rsp+56], 400
    mov  qword [rsp+64], 0
    mov  qword [rsp+72], 0
    mov  qword [rsp+80], 0
    mov  qword [rsp+88], 0
    API  CreateWindowExW
    test rax, rax
    jz   .fail
    mov  [rel hwnd_main], rax

    mov  rcx, rax
    mov  edx, SW_SHOW
    API  ShowWindow
    mov  rcx, [rel hwnd_main]
    API  UpdateWindow
    mov  eax, 1
    EPILOG
.fail:
    xor  eax, eax
    EPILOG

; ---------------------------------------------------------------------------
; Message loop.
; ---------------------------------------------------------------------------
gui_loop:
    PROLOG 64
.loop:
    PTR  rcx, msg_struct
    xor  edx, edx
    xor  r8d, r8d
    xor  r9d, r9d
    API  GetMessageW
    test eax, eax
    jz   .done
    cmp  eax, 0
    jl   .done
    PTR  rcx, msg_struct
    API  TranslateMessage
    PTR  rcx, msg_struct
    API  DispatchMessageW
    jmp  .loop
.done:
    EPILOG

; ---------------------------------------------------------------------------
; Window procedure.  rcx=hwnd, rdx=msg, r8=wParam, r9=lParam
; ---------------------------------------------------------------------------
wndproc:
    PROLOG 128
    mov  [rbp-8], rcx           ; hwnd
    mov  [rbp-16], rdx          ; msg
    mov  [rbp-24], r8           ; wParam
    mov  [rbp-32], r9           ; lParam
    cmp  edx, WM_CREATE
    je   .create
    cmp  edx, WM_COMMAND
    je   .command
    cmp  edx, WM_CLOSE
    je   .close
    cmp  edx, WM_DESTROY
    je   .destroy
.default:
    mov  rcx, [rbp-8]
    mov  rdx, [rbp-16]
    mov  r8,  [rbp-24]
    mov  r9,  [rbp-32]
    API  DefWindowProcW
    EPILOG

.create:
    ; heading
    xor  ecx, ecx
    PTR  rdx, cls_static
    PTR  r8,  txt_head
    mov  r9d, WS_CHILD | WS_VISIBLE
    mov  qword [rsp+32], 24
    mov  qword [rsp+40], 20
    mov  qword [rsp+48], 520
    mov  qword [rsp+56], 24
    mov  rax, [rbp-8]
    mov  [rsp+64], rax
    mov  qword [rsp+72], 0
    mov  qword [rsp+80], 0
    mov  qword [rsp+88], 0
    API  CreateWindowExW
    mov  [rel hwnd_head], rax

    ; body
    xor  ecx, ecx
    PTR  rdx, cls_static
    PTR  r8,  txt_body
    mov  r9d, WS_CHILD | WS_VISIBLE
    mov  qword [rsp+32], 24
    mov  qword [rsp+40], 56
    mov  qword [rsp+48], 520
    mov  qword [rsp+56], 110
    mov  rax, [rbp-8]
    mov  [rsp+64], rax
    mov  qword [rsp+72], 0
    mov  qword [rsp+80], 0
    mov  qword [rsp+88], 0
    API  CreateWindowExW
    mov  [rel hwnd_body], rax

    ; status line
    xor  ecx, ecx
    PTR  rdx, cls_static
    PTR  r8,  txt_idle
    mov  r9d, WS_CHILD | WS_VISIBLE
    mov  qword [rsp+32], 24
    mov  qword [rsp+40], 200
    mov  qword [rsp+48], 520
    mov  qword [rsp+56], 22
    mov  rax, [rbp-8]
    mov  [rsp+64], rax
    mov  qword [rsp+72], 0
    mov  qword [rsp+80], 0
    mov  qword [rsp+88], 0
    API  CreateWindowExW
    mov  [rel hwnd_status], rax

    ; Install button
    xor  ecx, ecx
    PTR  rdx, cls_button
    PTR  r8,  btn_install
    mov  r9d, WS_CHILD | WS_VISIBLE
    mov  qword [rsp+32], 300
    mov  qword [rsp+40], 300
    mov  qword [rsp+48], 120
    mov  qword [rsp+56], 34
    mov  rax, [rbp-8]
    mov  [rsp+64], rax
    mov  qword [rsp+72], ID_INSTALL
    mov  qword [rsp+80], 0
    mov  qword [rsp+88], 0
    API  CreateWindowExW
    mov  [rel hwnd_install], rax

    ; Cancel button
    xor  ecx, ecx
    PTR  rdx, cls_button
    PTR  r8,  btn_cancel
    mov  r9d, WS_CHILD | WS_VISIBLE
    mov  qword [rsp+32], 430
    mov  qword [rsp+40], 300
    mov  qword [rsp+48], 120
    mov  qword [rsp+56], 34
    mov  rax, [rbp-8]
    mov  [rsp+64], rax
    mov  qword [rsp+72], ID_CANCEL
    mov  qword [rsp+80], 0
    mov  qword [rsp+88], 0
    API  CreateWindowExW
    mov  [rel hwnd_cancel], rax

    xor  eax, eax
    EPILOG

.command:
    movzx eax, word [rbp-24]    ; LOWORD(wParam) = control id
    cmp  eax, ID_INSTALL
    je   .install
    cmp  eax, ID_CANCEL
    je   .close
    xor  eax, eax
    EPILOG

.install:
    cmp  dword [rel install_done], 0
    jne  .close
    mov  dword [rel install_done], 1
    mov  rcx, [rel hwnd_status]
    PTR  rdx, txt_working
    API  SetWindowTextW

    call do_install
    mov  [rbp-40], eax

    cmp  dword [rbp-40], 0
    jne  .install_bad
    mov  rcx, [rel hwnd_status]
    PTR  rdx, txt_installed
    API  SetWindowTextW
    xor  ecx, ecx
    PTR  rdx, msg_done
    PTR  r8,  msg_title
    mov  r9d, MB_OK | MB_ICONINFORMATION
    API  MessageBoxW
    jmp  .close

.install_bad:
    cmp  dword [rbp-40], 2
    jne  .install_fail
    xor  ecx, ecx
    PTR  rdx, msg_nopower
    PTR  r8,  msg_title
    mov  r9d, MB_OK | MB_ICONERROR
    API  MessageBoxW
    jmp  .close
.install_fail:
    xor  ecx, ecx
    PTR  rdx, msg_failed
    PTR  r8,  msg_title
    mov  r9d, MB_OK | MB_ICONERROR
    API  MessageBoxW

.close:
    mov  rcx, [rbp-8]
    API  DestroyWindow
    xor  eax, eax
    EPILOG

.destroy:
    xor  ecx, ecx
    API  PostQuitMessage
    xor  eax, eax
    EPILOG
