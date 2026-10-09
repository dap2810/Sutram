; ============================================================================
;  Sutram-Setup-Wizard.exe — Guided Split wizard installer for Sutram (सूत्रम्)
;
;  Pure NASM x86-64 Win32.  No C runtime, no toolkit, no import libraries, no
;  external build tools beyond NASM and ld.  Builds to a PE32+ GUI-subsystem
;  executable that resolves every Win32 entry point at runtime by walking the
;  PEB to kernel32 and calling GetProcAddress — the same pure-NASM mechanism
;  used by sutram_setup.asm in this directory.
;
;  Layout: "Guided Split" — a branded left sidebar (project thread icon,
;  सूत्रम् dominant, the Sutram word in the ten language-pack scripts below
;  it) and a wizard page area on the right with Back / Next / Cancel.
;
;  Pages:  Welcome -> License -> Install location -> Components ->
;          Ready -> Installing -> Finish.
;
;  The install engine (payload extraction + install-core.ps1) is adapted from
;  sutram_setup.asm in this directory; the wizard adds a directory picker,
;  component checkboxes, staged progress on a worker thread, and a finish
;  page.  Everything remains per-user and unelevated: no UAC, no HKLM, no
;  Program Files.
;
;  The transliterations of "Sutram" in the sidebar are best-effort and MUST
;  be verified by native speakers before release (see VERIFY note below).
;
;  Build (from the repository root):
;     nasm -f win64 windows/native-installer/sutram_wizard.asm -o wiz.obj
;     ld -mi386pep --subsystem windows --entry=_start -o Sutram-Setup-Wizard.exe wiz.obj
;  Requires payload.zip, install-core.ps1, uninstall-core.ps1 and LICENSE.txt
;  in the working directory at assembly time (pulled in with incbin).
; ============================================================================

bits 64
default rel

; --- window messages -------------------------------------------------------
%define WM_CREATE        0x0001
%define WM_DESTROY       0x0002
%define WM_PAINT         0x000F
%define WM_CLOSE         0x0010
%define WM_COMMAND       0x0111
%define WM_SETFONT       0x0030
%define WM_APP           0x8000
%define WM_WIZ_PROGRESS (WM_APP+1)
%define WM_WIZ_DONE     (WM_APP+2)

; --- window styles ----------------------------------------------------------
%define WS_OVERLAPPED    0x00000000
%define WS_CAPTION       0x00C00000
%define WS_SYSMENU       0x00080000
%define WS_MINIMIZEBOX   0x00020000
%define WS_CHILD         0x40000000
%define WS_VISIBLE       0x10000000
%define WS_TABSTOP       0x00010000
%define WS_BORDER        0x00800000
%define WS_VSCROLL       0x00200000
%define WS_GROUP         0x00020000
%define ES_MULTILINE     0x0004
%define ES_AUTOVSCROLL   0x0040
%define ES_READONLY      0x0800
%define BS_PUSHBUTTON    0x0000
%define BS_DEFPUSHBUTTON 0x0001
%define BS_AUTOCHECKBOX  0x0003
%define BS_AUTORADIOBUTTON 0x0009
%define SS_LEFT          0x0000
%define SS_CENTER        0x0001
%define BM_GETCHECK      0x00F0
%define BM_SETCHECK      0x00F1
%define BST_CHECKED      1
%define BST_UNCHECKED    0
%define BN_CLICKED       0
%define PBM_SETRANGE32   0x0406
%define PBM_SETPOS       0x0402
%define SW_SHOW          5
%define SW_HIDE          0
%define SW_SHOWNORMAL    1
%define DT_CENTER        0x0001
%define DT_VCENTER       0x0004
%define DT_SINGLELINE    0x0020
%define TRANSPARENT      1
%define FW_NORMAL        400
%define FW_SEMIBOLD      600
%define FW_BOLD          700
%define DEFAULT_CHARSET  1
%define PS_SOLID         0
%define ICC_PROGRESS_CLASS 0x0020

; --- misc -------------------------------------------------------------------
%define INFINITE              0xFFFFFFFF
%define MB_YESNO              0x00000004
%define MB_OK                 0x00000000
%define MB_ICONQUESTION       0x00000020
%define MB_ICONINFORMATION    0x00000040
%define MB_ICONERROR          0x00000010
%define IDYES                 6
%define CREATE_ALWAYS         2
%define FILE_ATTRIBUTE_NORMAL 0x80
%define GENERIC_WRITE         0x40000000
%define INVALID_HANDLE_VALUE  -1
%define MAXP                  1024
%define BIF_RETURNONLYFSDIRS  0x0001
%define BIF_NEWDIALOGSTYLE    0x0040

; --- control ids -------------------------------------------------------------
%define IDC_BACK      2001
%define IDC_NEXT      2002
%define IDC_CANCEL    2003
%define IDC_ACCEPT    2010
%define IDC_DECLINE   2011
%define IDC_LICEDIT   2012
%define IDC_DIREDIT   2020
%define IDC_BROWSE    2021
%define IDC_CKPATH    2030
%define IDC_CKDESK    2031
%define IDC_PBAR      2050

; --- sidebar geometry ---------------------------------------------------------
%define SIDE_W        230

; --- colours (0x00BBGGRR) ------------------------------------------------------
%define COL_TEAL      0x005C5C0B
%define COL_TEAL_DK   0x00454508
%define COL_ORANGE    0x003296FF
%define COL_CREAM     0x00BEE1FF
%define COL_SIDE_DIM  0x00D7D7AA
%define COL_WHITE     0x00FFFFFF

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

; --- dll names -----------------------------------------------------------------
name_kernel32 db 'kernel32.dll',0
name_user32   db 'user32.dll',0
name_gdi32    db 'gdi32.dll',0
name_comctl32 db 'comctl32.dll',0
name_shell32  db 'shell32.dll',0
name_ole32    db 'ole32.dll',0

; --- kernel32 --------------------------------------------------------------------
n_LoadLibraryA       db 'LoadLibraryA',0
n_GetProcAddress     db 'GetProcAddress',0
n_ExitProcess        db 'ExitProcess',0
n_GetTempPathW       db 'GetTempPathW',0
n_GetEnvironmentVariableW db 'GetEnvironmentVariableW',0
n_GetModuleFileNameW db 'GetModuleFileNameW',0
n_CreateDirectoryW   db 'CreateDirectoryW',0
n_CreateFileW        db 'CreateFileW',0
n_WriteFile          db 'WriteFile',0
n_CloseHandle        db 'CloseHandle',0
n_CreateProcessW     db 'CreateProcessW',0
n_WaitForSingleObject db 'WaitForSingleObject',0
n_GetExitCodeProcess db 'GetExitCodeProcess',0
n_lstrcpyW           db 'lstrcpyW',0
n_lstrcatW           db 'lstrcatW',0
n_GetCommandLineW    db 'GetCommandLineW',0
n_CreateThread       db 'CreateThread',0
n_Sleep              db 'Sleep',0
n_GetModuleHandleW   db 'GetModuleHandleW',0
; --- user32 -----------------------------------------------------------------------
n_MessageBoxW        db 'MessageBoxW',0
n_RegisterClassExW   db 'RegisterClassExW',0
n_CreateWindowExW    db 'CreateWindowExW',0
n_ShowWindow         db 'ShowWindow',0
n_UpdateWindow       db 'UpdateWindow',0
n_GetMessageW        db 'GetMessageW',0
n_TranslateMessage   db 'TranslateMessage',0
n_DispatchMessageW   db 'DispatchMessageW',0
n_DefWindowProcW     db 'DefWindowProcW',0
n_PostQuitMessage    db 'PostQuitMessage',0
n_DestroyWindow      db 'DestroyWindow',0
n_SetWindowTextW     db 'SetWindowTextW',0
n_GetWindowTextW     db 'GetWindowTextW',0
n_EnableWindow       db 'EnableWindow',0
n_SetFocus           db 'SetFocus',0
n_SendMessageW       db 'SendMessageW',0
n_PostMessageW       db 'PostMessageW',0
n_BeginPaint         db 'BeginPaint',0
n_EndPaint           db 'EndPaint',0
n_GetClientRect      db 'GetClientRect',0
n_InvalidateRect     db 'InvalidateRect',0
n_FillRect           db 'FillRect',0
n_LoadCursorW        db 'LoadCursorW',0
; --- gdi32 -------------------------------------------------------------------------
n_CreateFontW        db 'CreateFontW',0
n_SelectObject       db 'SelectObject',0
n_DeleteObject       db 'DeleteObject',0
n_SetBkMode          db 'SetBkMode',0
n_SetTextColor       db 'SetTextColor',0
n_CreateSolidBrush   db 'CreateSolidBrush',0
n_CreatePen          db 'CreatePen',0
n_Ellipse            db 'Ellipse',0
n_PolyBezier         db 'PolyBezier',0
n_DrawTextW          db 'DrawTextW',0
; --- comctl32 / shell32 / ole32 -------------------------------------------------------
n_InitCommonControlsEx db 'InitCommonControlsEx',0
n_SHBrowseForFolderW db 'SHBrowseForFolderW',0
n_SHGetPathFromIDListW db 'SHGetPathFromIDListW',0
n_CoTaskMemFree      db 'CoTaskMemFree',0

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
    IMPORTS CreateThread
    IMPORTS Sleep
    IMPORTS GetModuleHandleW
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
    IMPORTS GetWindowTextW
    IMPORTS EnableWindow
    IMPORTS SetFocus
    IMPORTS SendMessageW
    IMPORTS PostMessageW
    IMPORTS BeginPaint
    IMPORTS EndPaint
    IMPORTS GetClientRect
    IMPORTS InvalidateRect
    IMPORTS FillRect
    IMPORTS LoadCursorW
    dq 0, 0
gdi_table:
    IMPORTS CreateFontW
    IMPORTS SelectObject
    IMPORTS DeleteObject
    IMPORTS SetBkMode
    IMPORTS SetTextColor
    IMPORTS CreateSolidBrush
    IMPORTS CreatePen
    IMPORTS Ellipse
    IMPORTS PolyBezier
    IMPORTS DrawTextW
    dq 0, 0
comctl_table:
    IMPORTS InitCommonControlsEx
    dq 0, 0
shell_table:
    IMPORTS SHBrowseForFolderW
    IMPORTS SHGetPathFromIDListW
    dq 0, 0
ole_table:
    IMPORTS CoTaskMemFree
    dq 0, 0

; --- window chrome --------------------------------------------------------------------
wiz_title:    u16 "Sutram Setup"
cls_wiz:      u16 "SutramWizardWindow"
cls_button:   u16 "BUTTON"
cls_static:   u16 "STATIC"
cls_edit:     u16 "EDIT"
cls_pbar:     u16 "msctls_progress32"
face_segoe:   u16 "Segoe UI"

btn_back:     u16 "< Back"
btn_next:     u16 "Next >"
btn_install:  u16 "Install"
btn_finish:   u16 "Finish"
btn_cancel:   u16 "Cancel"
btn_browse:   u16 "Browse..."

; --- page titles -----------------------------------------------------------------------
t_welcome:  u16 "Welcome to Sutram Setup"
t_license:  u16 "License Agreement"
t_dir:      u16 "Choose Install Location"
t_comp:     u16 "Select Components"
t_ready:    u16 "Ready to Install"
t_prog:    u16 "Installing Sutram"
t_done:    u16 "Completing the Sutram Setup Wizard"

; --- page bodies --------------------------------------------------------------------------
b_welcome:  u16 "This wizard will install Sutram, the Sanskrit-keyword programming language, on your computer."
b_welcome2: u16 "Sutram installs for the current Windows user only. No administrator rights are needed, and nothing is written outside your own account."
b_welcome3: u16 "Click Next to continue."
b_lichead:  u16 "Please read the following license agreement. You must accept the terms to continue."
b_accept:   u16 "I &accept the terms of the license agreement"
b_decline:  u16 "I do &not accept the terms of the license agreement"
b_dirlabel: u16 "&Install location:"
b_dirnote:  u16 "Setup will install Sutram in the folder below. The installer needs write access to this folder."
b_complbl:  u16 "Select the components to install:"
b_ckpath:   u16 "&Add Sutram to my user PATH (recommended)"
b_ckdesk:   u16 "Create a &desktop shortcut (Sutram Terminal)"
b_compnote: u16 "The compiler, standard library, language packs, examples and books are always installed. Start Menu shortcuts are always created."
b_ready:    u16 "Setup is ready to install Sutram on your computer."
b_ready2:   u16 "Click Install to begin the installation."
b_proging:  u16 "Please wait while Sutram is installed..."
b_donemsg:  u16 "Sutram has been installed successfully."
b_donemsg2: u16 "You will find Sutram IDE and Sutram Terminal in your Start Menu."
b_cklaunch: u16 "&Launch Sutram Terminal"

st_extract: u16 "Extracting package files..."
st_script:  u16 "Running setup script (this can take a minute)..."
st_final:   u16 "Finalizing installation..."

; --- summary fragments -----------------------------------------------------------------------
sum_dir:    u16 "Destination folder: "
sum_path_y: u16 "Add to user PATH: yes"
sum_path_n: u16 "Add to user PATH: no"
sum_desk_y: u16 "Desktop shortcut: yes"
sum_desk_n: u16 "Desktop shortcut: no"
crlf:       u16 ""
; (crlf built at runtime as 0x0D,0x0A)

; --- messages ----------------------------------------------------------------------------------
msg_title:      u16 "Sutram Setup"
msg_failed:    u16 "Sutram setup did not complete. Check the install log in %TEMP%\Sutram-Setup for details."
msg_nopower:   u16 "Sutram setup could not start Windows PowerShell."
msg_nodir:     u16 "Please choose an install location first."
msg_uninst_done:   u16 "Sutram was removed from this user account."
msg_uninst_failed: u16 "Sutram could not be fully removed."
arg_uninstall: u16 "--uninstall"
env_localappdata: u16 "LOCALAPPDATA"
setup_subdir:  u16 "Sutram-Setup"
fname_payload: u16 "\\payload.zip"
fname_install: u16 "\\install-core.ps1"
fname_uninst:  u16 "\\uninstall-core.ps1"
fname_log:     u16 "\\install.log"
fname_ulog:    u16 "\\uninstall.log"
sub_programs:  u16 "\\Programs\\Sutram"
ps_prefix:     u16 "powershell.exe -NoProfile -ExecutionPolicy Bypass -File "
flag_payloadzip:  u16 " -PayloadZip "
flag_installdir:  u16 " -InstallDir "
flag_setupexepath: u16 " -SetupExePath "
flag_logpath:  u16 " -LogPath "
flag_addpath:  u16 " -AddPath"
flag_desktop:  u16 " -DesktopShortcut"
flag_selfpath: u16 " -SelfPath "
ps_uninst:     u16 "powershell.exe -NoProfile -ExecutionPolicy Bypass -File "
quote:         dw '"',0
brow_title:    u16 "Select the folder to install Sutram in"
side_footer:   u16 "SUTRAM SETUP"

; --- sidebar: Sutram in ten scripts --------------------------------------------------------------
; VERIFY: transliterations below are best-effort; confirm each with a native
; speaker before release.  Gujarati form supplied by the project owner.
w_sanskrit: dw 0x0938,0x0942,0x0924,0x094D,0x0930,0x092E,0x094D,0
w_hindi:    dw 0x0938,0x0942,0x0924,0x094D,0x0930,0x092E,0x094D,0
w_bengali:  dw 0x09B8,0x09C2,0x09A4,0x09CD,0x09B0,0x09AE,0x09CD,0
w_gujarati: dw 0x0AB8,0x0AC1,0x0AA4,0x0ACD,0x0AB0,0x0AAE,0
w_kannada:  dw 0x0CB8,0x0CC2,0x0CA4,0x0CCD,0x0CB0,0x0CAE,0x0CCD,0
w_malayalam: dw 0x0D38,0x0D42,0x0D24,0x0D4D,0x0D30,0x0D2E,0x0D4D,0
w_marathi:  dw 0x0938,0x0942,0x0924,0x094D,0x0930,0x092E,0x094D,0
w_odia:     dw 0x0B38,0x0B42,0x0B24,0x0B4D,0x0B30,0x0B2E,0x0B4D,0
w_punjabi:  dw 0x0A38,0x0A42,0x0A24,0x0A30,0x0A2E,0x0A4D,0
w_tamil:    dw 0x0B9A,0x0BC2,0x0BA4,0x0BCD,0x0BA4,0x0BBF,0x0BB0,0x0BAE,0x0BCD,0
w_telugu:   dw 0x0C38,0x0C42,0x0C24,0x0CCD,0x0C30,0x0C2E,0x0C4D,0
; (ptr, glyph count) pairs, drawn small under the dominant Sanskrit form
lang_table:
    dq w_hindi,    7
    dq w_bengali,  7
    dq w_gujarati, 6
    dq w_kannada,  7
    dq w_malayalam,7
    dq w_marathi,  7
    dq w_odia,     7
    dq w_punjabi,  6
    dq w_tamil,    9
    dq w_telugu,   7
    dq 0, 0

; --- embedded artifacts ----------------------------------------------------------------------------
blob_payload:  incbin "payload.zip"
blob_payload_end:
blob_install:  incbin "install-core.ps1"
blob_install_end:
blob_uninst:   incbin "uninstall-core.ps1"
blob_uninst_end:
blob_license:  incbin "LICENSE.txt"
blob_license_end:

section .bss
p_LoadLibraryA:       resq 1
p_GetProcAddress:     resq 1
p_ExitProcess:        resq 1
p_GetTempPathW:       resq 1
p_GetEnvironmentVariableW: resq 1
p_GetModuleFileNameW: resq 1
p_CreateDirectoryW:   resq 1
p_CreateFileW:        resq 1
p_WriteFile:          resq 1
p_CloseHandle:        resq 1
p_CreateProcessW:     resq 1
p_WaitForSingleObject: resq 1
p_GetExitCodeProcess: resq 1
p_lstrcpyW:           resq 1
p_lstrcatW:           resq 1
p_GetCommandLineW:    resq 1
p_CreateThread:       resq 1
p_Sleep:              resq 1
p_GetModuleHandleW:   resq 1
p_MessageBoxW:        resq 1
p_RegisterClassExW:   resq 1
p_CreateWindowExW:    resq 1
p_ShowWindow:         resq 1
p_UpdateWindow:       resq 1
p_GetMessageW:        resq 1
p_TranslateMessage:   resq 1
p_DispatchMessageW:    resq 1
p_DefWindowProcW:      resq 1
p_PostQuitMessage:     resq 1
p_DestroyWindow:       resq 1
p_SetWindowTextW:      resq 1
p_GetWindowTextW:      resq 1
p_EnableWindow:        resq 1
p_SetFocus:            resq 1
p_SendMessageW:        resq 1
p_PostMessageW:        resq 1
p_BeginPaint:          resq 1
p_EndPaint:            resq 1
p_GetClientRect:       resq 1
p_InvalidateRect:      resq 1
p_FillRect:            resq 1
p_LoadCursorW:         resq 1
p_CreateFontW:         resq 1
p_SelectObject:        resq 1
p_DeleteObject:        resq 1
p_SetBkMode:           resq 1
p_SetTextColor:        resq 1
p_CreateSolidBrush:    resq 1
p_CreatePen:           resq 1
p_Ellipse:             resq 1
p_PolyBezier:          resq 1
p_DrawTextW:           resq 1
p_InitCommonControlsEx: resq 1
p_SHBrowseForFolderW:  resq 1
p_SHGetPathFromIDListW: resq 1
p_CoTaskMemFree:       resq 1
h_kernel:    resq 1
h_user:      resq 1
h_gdi:       resq 1
h_comctl:    resq 1
h_shell:     resq 1
h_ole:       resq 1
hwnd_main:   resq 1
hwnd_title:  resq 1
hw_p0a:      resq 1
hw_p0b:      resq 1
hw_p0c:      resq 1
hw_licedit:  resq 1
hw_accept:   resq 1
hw_decline:  resq 1
hw_lichead:  resq 1
hw_dirlbl:   resq 1
hw_diredit:  resq 1
hw_browse:   resq 1
hw_dirnote:  resq 1
hw_complbl:  resq 1
hw_ckpath:   resq 1
hw_ckdesk:   resq 1
hw_compnote: resq 1
hw_sum1:     resq 1
hw_sum2:     resq 1
hw_pbar:     resq 1
hw_pstat:    resq 1
hw_proging:  resq 1
hw_donemsg:  resq 1
hw_donemsg2: resq 1
hw_cklaunch: resq 1
hw_back:     resq 1
hw_next:     resq 1
hw_cancel:   resq 1
f_title:     resq 1
f_body:      resq 1
f_sidebig:   resq 1
f_sideword:  resq 1
f_sidetiny:  resq 1
br_teal:     resq 1
br_teal_dk:  resq 1
pen_orange:  resq 1
pen_cream:   resq 1
page_idx:    resd 1
installing:  resd 1
opt_addpath: resd 1
opt_desktop: resd 1
h_mod:       resq 1
h_thread:    resq 1
temp_path:   resw MAXP
setup_dir:   resw MAXP
local_appdata: resw MAXP
install_dir: resw MAXP
self_path:   resw MAXP
log_path:    resw MAXP
payload_path: resw MAXP
install_ps1: resw MAXP
uninst_ps1:  resw MAXP
cmdline:     resw 8192
lic_w:       resw 4096
sum_buf:     resw 2048
written:     resd 1
exit_code:   resd 1
startupinfo: resb 104
procinfo:    resb 24
wndclass:    resb 80
msg_struct:  resb 48
paintstruct: resb 64
rc_paint:    resb 16
browseinfo:  resb 64
dispname:    resw MAXP

section .text
global _start
; ============================================================================
; PEB-walk bootstrap: find kernel32 base and GetProcAddress without imports.
; (Same mechanism as sutram_setup.asm in this directory.)
; ============================================================================
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

; --- rcx = dll handle, rdx = table of (name ptr, slot ptr) pairs, 0,0 ends ---
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

; --- load one dll by name and fill its table. rdi=name(db), rsi=table ---------
load_one:
    PROLOG 64
    mov  [rbp-8], rdi
    mov  [rbp-16], rsi
    mov  rcx, [rbp-8]
    API  LoadLibraryA
    test rax, rax
    jz   .fail
    mov  rcx, rax
    mov  rdx, [rbp-16]
    call fill_table
    test eax, eax
    jz   .fail
    mov  eax, 1
    jmp  .done
.fail:
    xor  eax, eax
.done:
    EPILOG

; --- resolve every entry point we use ------------------------------------------
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

    PTR  rdi, name_kernel32
    PTR  rsi, kernel_table
    call load_one
    test eax, eax
    jz   .fail
    PTR  rdi, name_user32
    PTR  rsi, user_table
    call load_one
    test eax, eax
    jz   .fail
    PTR  rdi, name_gdi32
    PTR  rsi, gdi_table
    call load_one
    test eax, eax
    jz   .fail
    PTR  rdi, name_comctl32
    PTR  rsi, comctl_table
    call load_one
    test eax, eax
    jz   .fail
    PTR  rdi, name_shell32
    PTR  rsi, shell_table
    call load_one
    test eax, eax
    jz   .fail
    PTR  rdi, name_ole32
    PTR  rsi, ole_table
    call load_one
    test eax, eax
    jz   .fail
    mov  eax, 1
    jmp  .end
.fail:
    xor  eax, eax
.end:
    EPILOG

; --- write a file.  rcx = UTF-16 path, rdx = data, r8 = size ---------------------
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

; --- dest = base + suffix.  rcx = dest, rdx = base, r8 = suffix -------------------
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

; --- append a literal to cmdline.  rcx = literal ----------------------------------
app:
    PROLOG 48
    mov  rdx, rcx
    PTR  rcx, cmdline
    API  lstrcatW
    EPILOG

; --- rcx = haystack (UTF-16), rdx = needle (UTF-16) -> rax = ptr or 0 ---------------
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

; --- truncate rcx (UTF-16 path) after the last backslash ---------------------------------
dirname:
    PROLOG 48
    mov  [rbp-8], rcx
    mov  r10, rcx
    xor  r11, r11
.scan:
    mov  ax, [r10]
    test ax, ax
    jz   .end
    cmp  ax, 92
    jne  .fwd
    mov  r11, r10
    jmp  .cont
.fwd:
    cmp  ax, 47
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

; --- convert the ASCII license blob to UTF-16 in lic_w ------------------------------------
license_to_utf16:
    PROLOG 48
    PTR  rsi, blob_license
    PTR  rdi, lic_w
    mov  rcx, blob_license_end - blob_license
.loop:
    test rcx, rcx
    jz   .done
    movzx eax, byte [rsi]
    mov  [rdi], ax
    inc  rsi
    add  rdi, 2
    dec  rcx
    jmp  .loop
.done:
    mov  word [rdi], 0
    EPILOG

; --- post a progress percent to the UI thread.  ecx = percent --------------------------------
post_progress:
    PROLOG 48
    mov  edx, ecx
    mov  rcx, [rel hwnd_main]
    mov  r8d, WM_WIZ_PROGRESS
    xor  r9d, r9d
    API  PostMessageW
    EPILOG
; ============================================================================
; Install engine (worker thread).  Adapted from do_install in sutram_setup.asm:
; the destination directory and the -AddPath / -DesktopShortcut switches now
; come from the wizard pages, and progress is posted to the UI thread.
; Returns eax: 0 ok, 1 failed, 2 no PowerShell.
; ============================================================================
do_install_staged:
    PROLOG 96
    mov  ecx, 5
    call post_progress

    ; %TEMP%\Sutram-Setup
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

    ; paths
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
    ; NOTE: install_dir was filled from the directory page before the thread
    ; started; it is used verbatim here.

    mov  ecx, 20
    call post_progress

    ; write the three artifacts
    PTR  rcx, payload_path
    PTR  rdx, blob_payload
    mov  r8,  blob_payload_end - blob_payload
    call write_file
    test eax, eax
    jz   .dfail
    mov  ecx, 40
    call post_progress

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
    mov  ecx, 55
    call post_progress

    ; build the PowerShell command line
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
    cmp  dword [rel opt_addpath], 1
    jne  .no_path
    PTR  rcx, flag_addpath
    call app
.no_path:
    cmp  dword [rel opt_desktop], 1
    jne  .no_desk
    PTR  rcx, flag_desktop
    call app
.no_desk:

    ; zero STARTUPINFOW / PROCESS_INFORMATION
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

    ; CreateProcessW(NULL, cmdline, ...)
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

    mov  ecx, 60
    call post_progress
    mov  rcx, [rel procinfo]
    mov  edx, INFINITE
    API  WaitForSingleObject
    mov  ecx, 90
    call post_progress
    mov  rcx, [rel procinfo]
    PTR  rdx, exit_code
    API  GetExitCodeProcess
    cmp  dword [rel exit_code], 0
    jne  .dfail
    mov  ecx, 100
    call post_progress
    xor  eax, eax
    EPILOG
.dnopw:
    mov  eax, 2
    EPILOG
.dfail:
    mov  eax, 1
    EPILOG

; --- worker thread: runs the engine, then notifies the UI ----------------------------
install_thread:
    PROLOG 64
    call do_install_staged
    mov  edx, eax              ; status -> wParam
    mov  rcx, [rel hwnd_main]
    mov  r8d, WM_WIZ_DONE
    xor  r9d, r9d
    API  PostMessageW
    xor  eax, eax
    EPILOG

; ============================================================================
; Uninstall mode (--uninstall): same behaviour as sutram_setup.asm.
; ============================================================================
do_uninstall:
    PROLOG 96
    xor  ecx, ecx
    PTR  rdx, self_path
    mov  r8d, MAXP
    API  GetModuleFileNameW
    PTR  rcx, install_dir
    PTR  rdx, self_path
    API  lstrcpyW
    PTR  rcx, install_dir
    call dirname

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

    PTR  rcx, uninst_ps1
    PTR  rdx, blob_uninst
    mov  r8,  blob_uninst_end - blob_uninst
    call write_file
    test eax, eax
    jz   .failed

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
; ============================================================================
; GUI construction
; ============================================================================

section .data
; page titles and visibility
page_titles:
    dq t_welcome, t_license, t_dir, t_comp, t_ready, t_prog, t_done
; (hwnd slot, page bitmask) — bit n set = visible on page n
vis_table:
    dq hw_p0a,     0x01
    dq hw_p0b,     0x01
    dq hw_p0c,     0x01
    dq hw_lichead, 0x02
    dq hw_licedit, 0x02
    dq hw_accept,  0x02
    dq hw_decline, 0x02
    dq hw_dirlbl,  0x04
    dq hw_diredit, 0x04
    dq hw_browse,  0x04
    dq hw_dirnote, 0x04
    dq hw_complbl, 0x08
    dq hw_ckpath,  0x08
    dq hw_ckdesk,  0x08
    dq hw_compnote, 0x08
    dq hw_sum1,    0x10
    dq hw_sum2,    0x10
    dq hw_proging, 0x20
    dq hw_pbar,    0x20
    dq hw_pstat,   0x20
    dq hw_donemsg, 0x40
    dq hw_donemsg2, 0x40
    dq hw_cklaunch, 0x40
    dq hw_back,    0x1F
    dq hw_next,    0x7F
    dq hw_cancel,  0x3F
    dq 0, 0
nl: dw 13, 10, 0
thread_pts: dd 90,95, 92,52, 138,108, 140,64
cmd_term1: u16 "cmd.exe /K "
cmd_set:    u16 "set "
cmd_patheq: u16 "PATH="
cmd_binsemi: u16 "\\bin;"
cmd_pathvar: u16 "%PATH%"
cmd_andver: u16 " && sutram --version"

section .text

; --- make a font. rcx = pixel height (negative), edx = weight, r8 = face -> rax=HFONT
make_font:
    PROLOG 128
    mov  [rbp-8], rcx
    mov  [rbp-16], rdx
    mov  [rbp-24], r8
    mov  rcx, [rbp-8]
    xor  edx, edx
    xor  r8d, r8d
    xor  r9d, r9d
    mov  rax, [rbp-16]
    mov  [rsp+32], rax          ; fnWeight
    mov  qword [rsp+40], 0      ; italic
    mov  qword [rsp+48], 0      ; underline
    mov  qword [rsp+56], 0      ; strikeout
    mov  qword [rsp+64], DEFAULT_CHARSET
    mov  qword [rsp+72], 0      ; out precision
    mov  qword [rsp+80], 0      ; clip precision
    mov  qword [rsp+88], 0      ; quality
    mov  qword [rsp+96], 0      ; pitch/family
    mov  rax, [rbp-24]
    mov  [rsp+104], rax         ; face
    API  CreateFontW
    EPILOG

create_fonts:
    PROLOG 64
    mov  ecx, -26
    mov  edx, FW_SEMIBOLD
    PTR  r8, face_segoe
    call make_font
    mov  [rel f_title], rax
    mov  ecx, -19
    mov  edx, FW_NORMAL
    PTR  r8, face_segoe
    call make_font
    mov  [rel f_body], rax
    mov  ecx, -42
    mov  edx, FW_SEMIBOLD
    PTR  r8, face_segoe
    call make_font
    mov  [rel f_sidebig], rax
    mov  ecx, -19
    mov  edx, FW_NORMAL
    PTR  r8, face_segoe
    call make_font
    mov  [rel f_sideword], rax
    mov  ecx, -15
    mov  edx, FW_BOLD
    PTR  r8, face_segoe
    call make_font
    mov  [rel f_sidetiny], rax
    mov  ecx, COL_TEAL
    API  CreateSolidBrush
    mov  [rel br_teal], rax
    mov  ecx, COL_TEAL_DK
    API  CreateSolidBrush
    mov  [rel br_teal_dk], rax
    mov  ecx, PS_SOLID
    mov  edx, 5
    mov  r8d, COL_ORANGE
    API  CreatePen
    mov  [rel pen_orange], rax
    mov  ecx, PS_SOLID
    mov  edx, 3
    mov  r8d, COL_CREAM
    API  CreatePen
    mov  [rel pen_cream], rax
    EPILOG

; --- create a child control --------------------------------------------------------
; rcx=class, rdx=text, r8d=style, r9d=x, stack: y, w, h, parent, id -> rax=hwnd
make_control:
    PROLOG 128
    mov  [rbp-8], rcx
    mov  [rbp-16], rdx
    mov  [rbp-24], r8
    mov  [rbp-32], r9
    mov  rax, [rbp+16]
    mov  [rbp-40], rax
    mov  rax, [rbp+24]
    mov  [rbp-48], rax
    mov  rax, [rbp+32]
    mov  [rbp-56], rax
    mov  rax, [rbp+40]
    mov  [rbp-64], rax
    mov  rax, [rbp+48]
    mov  [rbp-72], rax
    xor  ecx, ecx
    mov  rdx, [rbp-8]
    mov  r8, [rbp-16]
    mov  r9d, dword [rbp-24]
    mov  eax, dword [rbp-32]
    mov  [rsp+32], rax
    mov  rax, [rbp-40]
    mov  [rsp+40], rax
    mov  rax, [rbp-48]
    mov  [rsp+48], rax
    mov  rax, [rbp-56]
    mov  [rsp+56], rax
    mov  rax, [rbp-64]
    mov  [rsp+64], rax
    mov  rax, [rbp-72]
    mov  [rsp+72], rax
    mov  qword [rsp+80], 0
    mov  qword [rsp+88], 0
    API  CreateWindowExW
    EPILOG

; --- rcx=hwnd, rdx=font -----------------------------------------------------------------
set_font:
    PROLOG 48
    mov  r8, rdx
    mov  edx, WM_SETFONT
    mov  r9d, 1
    API  SendMessageW
    EPILOG

; --- rcx=hwnd, edx=check(0/1) ---------------------------------------------------------------
set_check:
    PROLOG 48
    mov  r8, rdx
    mov  edx, BM_SETCHECK
    xor  r9d, r9d
    API  SendMessageW
    EPILOG

; --- rcx=hwnd -> eax=1 checked / 0 not ----------------------------------------------------------
get_check:
    PROLOG 48
    mov  edx, BM_GETCHECK
    xor  r8d, r8d
    xor  r9d, r9d
    API  SendMessageW
    EPILOG

; --- helper: make a static with body font --------------------------------------------------------
; rcx=text, edx=x, r8d=y, r9d=w, stack: h, slot
mk_static:
    PROLOG 96
    mov  [rbp-8], rcx
    mov  [rbp-16], rdx
    mov  [rbp-24], r8
    mov  [rbp-32], r9
    mov  rax, [rbp+16]
    mov  [rbp-40], rax          ; h
    mov  rax, [rbp+24]
    mov  [rbp-48], rax          ; slot
    xor  ecx, ecx
    PTR  rdx, cls_static
    mov  r8, [rbp-8]
    mov  r9d, WS_CHILD | WS_VISIBLE | SS_LEFT
    mov  eax, dword [rbp-16]
    mov  [rsp+32], rax          ; x
    mov  rax, [rbp-24]
    mov  [rsp+40], rax          ; y
    mov  rax, [rbp-32]
    mov  [rsp+48], rax          ; w
    mov  rax, [rbp-40]
    mov  [rsp+56], rax          ; h
    mov  rax, [rel hwnd_main]
    mov  [rsp+64], rax
    mov  qword [rsp+72], 0
    mov  qword [rsp+80], 0
    mov  qword [rsp+88], 0
    API  CreateWindowExW
    mov  r10, [rbp-48]
    mov  [r10], rax
    mov  rcx, rax
    mov  rdx, [rel f_body]
    call set_font
    EPILOG

; ============================================================================
; Build the main window and every page control.  eax = 1 ok / 0 fail.
; ============================================================================
create_window:
    PROLOG 160

    ; common controls (progress bar class)
    mov  dword [rsp+32], 8
    mov  dword [rsp+36], ICC_PROGRESS_CLASS
    lea  rcx, [rsp+32]
    API  InitCommonControlsEx

    call create_fonts

    ; module handle for the window class
    xor  ecx, ecx
    API  GetModuleHandleW
    mov  [rel h_mod], rax

    ; default install dir: %LOCALAPPDATA%\Programs\Sutram
    PTR  rcx, env_localappdata
    PTR  rdx, local_appdata
    mov  r8d, MAXP
    API  GetEnvironmentVariableW
    PTR  rcx, install_dir
    PTR  rdx, local_appdata
    PTR  r8,  sub_programs
    call join

    ; license text -> UTF-16
    call license_to_utf16

    ; WNDCLASSEXW
    PTR  rdi, wndclass
    mov  ecx, 10
    xor  eax, eax
    rep  stosq
    PTR  rax, wndclass
    mov  dword [rax+0], 80
    PTR  r10, wndproc
    mov  [rax+8], r10
    mov  r10, [rel h_mod]
    mov  [rax+24], r10          ; hInstance
    xor  ecx, ecx
    mov  edx, 32512             ; IDC_ARROW
    API  LoadCursorW
    mov  [rax+40], rax          ; hCursor
    mov  qword [rax+48], 1      ; hbrBackground = COLOR_WINDOW+1
    PTR  r10, cls_wiz
    mov  [rax+64], r10
    PTR  rcx, wndclass
    API  RegisterClassExW
    test eax, eax
    jz   .fail

    ; main window: 800x600, fixed
    xor  ecx, ecx
    PTR  rdx, cls_wiz
    PTR  r8,  wiz_title
    mov  r9d, WS_OVERLAPPED | WS_CAPTION | WS_SYSMENU | WS_MINIMIZEBOX
    mov  rax, 0x80000000
    mov  [rsp+32], rax
    mov  [rsp+40], rax
    mov  qword [rsp+48], 800
    mov  qword [rsp+56], 600
    mov  qword [rsp+64], 0
    mov  qword [rsp+72], 0
    mov  rax, [rel h_mod]
    mov  [rsp+80], rax
    mov  qword [rsp+88], 0
    API  CreateWindowExW
    test rax, rax
    jz   .fail
    mov  [rel hwnd_main], rax

    ; ---- title (shared across pages) ----
    xor  ecx, ecx
    PTR  rdx, cls_static
    PTR  r8,  t_welcome
    mov  r9d, WS_CHILD | WS_VISIBLE | SS_LEFT
    mov  qword [rsp+32], 246
    mov  qword [rsp+40], 16
    mov  qword [rsp+48], 530
    mov  qword [rsp+56], 34
    mov  rax, [rel hwnd_main]
    mov  [rsp+64], rax
    mov  qword [rsp+72], 0
    mov  qword [rsp+80], 0
    mov  qword [rsp+88], 0
    API  CreateWindowExW
    mov  [rel hwnd_title], rax
    mov  rcx, rax
    mov  rdx, [rel f_title]
    call set_font

    ; ---- page 0 ----
    PTR  rcx, b_welcome
    mov  edx, 246
    mov  r8d, 66
    mov  r9d, 530
    mov  qword [rsp+32], 50
    PTR  rax, hw_p0a
    mov  [rsp+40], rax
    call mk_static
    PTR  rcx, b_welcome2
    mov  edx, 246
    mov  r8d, 124
    mov  r9d, 530
    mov  qword [rsp+32], 72
    PTR  rax, hw_p0b
    mov  [rsp+40], rax
    call mk_static
    PTR  rcx, b_welcome3
    mov  edx, 246
    mov  r8d, 210
    mov  r9d, 530
    mov  qword [rsp+32], 28
    PTR  rax, hw_p0c
    mov  [rsp+40], rax
    call mk_static

    ; ---- page 1: license ----
    PTR  rcx, b_lichead
    mov  edx, 246
    mov  r8d, 62
    mov  r9d, 530
    mov  qword [rsp+32], 26
    PTR  rax, hw_lichead
    mov  [rsp+40], rax
    call mk_static
    ; read-only license edit
    xor  ecx, ecx
    PTR  rdx, cls_edit
    PTR  r8,  lic_w
    mov  r9d, WS_CHILD | WS_VISIBLE | WS_BORDER | WS_VSCROLL | ES_MULTILINE | ES_READONLY | ES_AUTOVSCROLL | WS_TABSTOP
    mov  qword [rsp+32], 246
    mov  qword [rsp+40], 94
    mov  qword [rsp+48], 530
    mov  qword [rsp+56], 216
    mov  rax, [rel hwnd_main]
    mov  [rsp+64], rax
    mov  qword [rsp+72], IDC_LICEDIT
    mov  qword [rsp+80], 0
    mov  qword [rsp+88], 0
    API  CreateWindowExW
    mov  [rel hw_licedit], rax
    mov  rcx, rax
    mov  rdx, [rel f_body]
    call set_font
    ; radios
    xor  ecx, ecx
    PTR  rdx, cls_button
    PTR  r8,  b_accept
    mov  r9d, WS_CHILD | WS_VISIBLE | BS_AUTORADIOBUTTON | WS_GROUP | WS_TABSTOP
    mov  qword [rsp+32], 246
    mov  qword [rsp+40], 322
    mov  qword [rsp+48], 530
    mov  qword [rsp+56], 26
    mov  rax, [rel hwnd_main]
    mov  [rsp+64], rax
    mov  qword [rsp+72], IDC_ACCEPT
    mov  qword [rsp+80], 0
    mov  qword [rsp+88], 0
    API  CreateWindowExW
    mov  [rel hw_accept], rax
    mov  rcx, rax
    mov  rdx, [rel f_body]
    call set_font
    xor  ecx, ecx
    PTR  rdx, cls_button
    PTR  r8,  b_decline
    mov  r9d, WS_CHILD | WS_VISIBLE | BS_AUTORADIOBUTTON | WS_TABSTOP
    mov  qword [rsp+32], 246
    mov  qword [rsp+40], 352
    mov  qword [rsp+48], 530
    mov  qword [rsp+56], 26
    mov  rax, [rel hwnd_main]
    mov  [rsp+64], rax
    mov  qword [rsp+72], IDC_DECLINE
    mov  qword [rsp+80], 0
    mov  qword [rsp+88], 0
    API  CreateWindowExW
    mov  [rel hw_decline], rax
    mov  rcx, rax
    mov  rdx, [rel f_body]
    call set_font
    mov  rcx, [rel hw_decline]
    mov  edx, BST_CHECKED
    call set_check

    ; ---- page 2: directory ----
    PTR  rcx, b_dirlabel
    mov  edx, 246
    mov  r8d, 62
    mov  r9d, 530
    mov  qword [rsp+32], 26
    PTR  rax, hw_dirlbl
    mov  [rsp+40], rax
    call mk_static
    xor  ecx, ecx
    PTR  rdx, cls_edit
    PTR  r8,  install_dir
    mov  r9d, WS_CHILD | WS_VISIBLE | WS_BORDER | WS_TABSTOP | 0x0080
    mov  qword [rsp+32], 246
    mov  qword [rsp+40], 94
    mov  qword [rsp+48], 420
    mov  qword [rsp+56], 28
    mov  rax, [rel hwnd_main]
    mov  [rsp+64], rax
    mov  qword [rsp+72], IDC_DIREDIT
    mov  qword [rsp+80], 0
    mov  qword [rsp+88], 0
    API  CreateWindowExW
    mov  [rel hw_diredit], rax
    mov  rcx, rax
    mov  rdx, [rel f_body]
    call set_font
    xor  ecx, ecx
    PTR  rdx, cls_button
    PTR  r8,  btn_browse
    mov  r9d, WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON | WS_TABSTOP
    mov  qword [rsp+32], 676
    mov  qword [rsp+40], 92
    mov  qword [rsp+48], 100
    mov  qword [rsp+56], 32
    mov  rax, [rel hwnd_main]
    mov  [rsp+64], rax
    mov  qword [rsp+72], IDC_BROWSE
    mov  qword [rsp+80], 0
    mov  qword [rsp+88], 0
    API  CreateWindowExW
    mov  [rel hw_browse], rax
    mov  rcx, rax
    mov  rdx, [rel f_body]
    call set_font
    PTR  rcx, b_dirnote
    mov  edx, 246
    mov  r8d, 136
    mov  r9d, 530
    mov  qword [rsp+32], 52
    PTR  rax, hw_dirnote
    mov  [rsp+40], rax
    call mk_static

    ; ---- page 3: components ----
    PTR  rcx, b_complbl
    mov  edx, 246
    mov  r8d, 62
    mov  r9d, 530
    mov  qword [rsp+32], 26
    PTR  rax, hw_complbl
    mov  [rsp+40], rax
    call mk_static
    xor  ecx, ecx
    PTR  rdx, cls_button
    PTR  r8,  b_ckpath
    mov  r9d, WS_CHILD | WS_VISIBLE | BS_AUTOCHECKBOX | WS_TABSTOP
    mov  qword [rsp+32], 246
    mov  qword [rsp+40], 100
    mov  qword [rsp+48], 530
    mov  qword [rsp+56], 28
    mov  rax, [rel hwnd_main]
    mov  [rsp+64], rax
    mov  qword [rsp+72], IDC_CKPATH
    mov  qword [rsp+80], 0
    mov  qword [rsp+88], 0
    API  CreateWindowExW
    mov  [rel hw_ckpath], rax
    mov  rcx, rax
    mov  rdx, [rel f_body]
    call set_font
    mov  rcx, [rel hw_ckpath]
    mov  edx, BST_CHECKED
    call set_check
    xor  ecx, ecx
    PTR  rdx, cls_button
    PTR  r8,  b_ckdesk
    mov  r9d, WS_CHILD | WS_VISIBLE | BS_AUTOCHECKBOX | WS_TABSTOP
    mov  qword [rsp+32], 246
    mov  qword [rsp+40], 134
    mov  qword [rsp+48], 530
    mov  qword [rsp+56], 28
    mov  rax, [rel hwnd_main]
    mov  [rsp+64], rax
    mov  qword [rsp+72], IDC_CKDESK
    mov  qword [rsp+80], 0
    mov  qword [rsp+88], 0
    API  CreateWindowExW
    mov  [rel hw_ckdesk], rax
    mov  rcx, rax
    mov  rdx, [rel f_body]
    call set_font
    PTR  rcx, b_compnote
    mov  edx, 246
    mov  r8d, 178
    mov  r9d, 530
    mov  qword [rsp+32], 76
    PTR  rax, hw_compnote
    mov  [rsp+40], rax
    call mk_static

    ; ---- page 4: ready ----
    PTR  rcx, b_ready
    mov  edx, 246
    mov  r8d, 62
    mov  r9d, 530
    mov  qword [rsp+32], 26
    PTR  rax, hw_sum1
    mov  [rsp+40], rax
    call mk_static
    PTR  rcx, sum_buf
    mov  edx, 246
    mov  r8d, 100
    mov  r9d, 530
    mov  qword [rsp+32], 170
    PTR  rax, hw_sum2
    mov  [rsp+40], rax
    call mk_static

    ; ---- page 5: progress ----
    PTR  rcx, b_proging
    mov  edx, 246
    mov  r8d, 62
    mov  r9d, 530
    mov  qword [rsp+32], 26
    PTR  rax, hw_proging
    mov  [rsp+40], rax
    call mk_static
    xor  ecx, ecx
    PTR  rdx, cls_pbar
    xor  r8d, r8d
    mov  r9d, WS_CHILD | WS_VISIBLE
    mov  qword [rsp+32], 246
    mov  qword [rsp+40], 100
    mov  qword [rsp+48], 530
    mov  qword [rsp+56], 30
    mov  rax, [rel hwnd_main]
    mov  [rsp+64], rax
    mov  qword [rsp+72], IDC_PBAR
    mov  qword [rsp+80], 0
    mov  qword [rsp+88], 0
    API  CreateWindowExW
    mov  [rel hw_pbar], rax
    mov  rcx, rax
    mov  edx, PBM_SETRANGE32
    xor  r8d, r8d
    mov  r9d, 100
    API  SendMessageW
    PTR  rcx, st_extract
    mov  edx, 246
    mov  r8d, 144
    mov  r9d, 530
    mov  qword [rsp+32], 26
    PTR  rax, hw_pstat
    mov  [rsp+40], rax
    call mk_static

    ; ---- page 6: finish ----
    PTR  rcx, b_donemsg
    mov  edx, 246
    mov  r8d, 62
    mov  r9d, 530
    mov  qword [rsp+32], 30
    PTR  rax, hw_donemsg
    mov  [rsp+40], rax
    call mk_static
    PTR  rcx, b_donemsg2
    mov  edx, 246
    mov  r8d, 100
    mov  r9d, 530
    mov  qword [rsp+32], 52
    PTR  rax, hw_donemsg2
    mov  [rsp+40], rax
    call mk_static
    xor  ecx, ecx
    PTR  rdx, cls_button
    PTR  r8,  b_cklaunch
    mov  r9d, WS_CHILD | WS_VISIBLE | BS_AUTOCHECKBOX | WS_TABSTOP
    mov  qword [rsp+32], 246
    mov  qword [rsp+40], 166
    mov  qword [rsp+48], 530
    mov  qword [rsp+56], 28
    mov  rax, [rel hwnd_main]
    mov  [rsp+64], rax
    mov  qword [rsp+72], 2060
    mov  qword [rsp+80], 0
    mov  qword [rsp+88], 0
    API  CreateWindowExW
    mov  [rel hw_cklaunch], rax
    mov  rcx, rax
    mov  rdx, [rel f_body]
    call set_font
    mov  rcx, [rel hw_cklaunch]
    mov  edx, BST_CHECKED
    call set_check

    ; ---- navigation buttons ----
    xor  ecx, ecx
    PTR  rdx, cls_button
    PTR  r8,  btn_back
    mov  r9d, WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON | WS_TABSTOP
    mov  qword [rsp+32], 482
    mov  qword [rsp+40], 470
    mov  qword [rsp+48], 90
    mov  qword [rsp+56], 34
    mov  rax, [rel hwnd_main]
    mov  [rsp+64], rax
    mov  qword [rsp+72], IDC_BACK
    mov  qword [rsp+80], 0
    mov  qword [rsp+88], 0
    API  CreateWindowExW
    mov  [rel hw_back], rax
    mov  rcx, rax
    mov  rdx, [rel f_body]
    call set_font
    xor  ecx, ecx
    PTR  rdx, cls_button
    PTR  r8,  btn_next
    mov  r9d, WS_CHILD | WS_VISIBLE | BS_DEFPUSHBUTTON | WS_TABSTOP
    mov  qword [rsp+32], 584
    mov  qword [rsp+40], 470
    mov  qword [rsp+48], 90
    mov  qword [rsp+56], 34
    mov  rax, [rel hwnd_main]
    mov  [rsp+64], rax
    mov  qword [rsp+72], IDC_NEXT
    mov  qword [rsp+80], 0
    mov  qword [rsp+88], 0
    API  CreateWindowExW
    mov  [rel hw_next], rax
    mov  rcx, rax
    mov  rdx, [rel f_body]
    call set_font
    xor  ecx, ecx
    PTR  rdx, cls_button
    PTR  r8,  btn_cancel
    mov  r9d, WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON | WS_TABSTOP
    mov  qword [rsp+32], 686
    mov  qword [rsp+40], 470
    mov  qword [rsp+48], 90
    mov  qword [rsp+56], 34
    mov  rax, [rel hwnd_main]
    mov  [rsp+64], rax
    mov  qword [rsp+72], IDC_CANCEL
    mov  qword [rsp+80], 0
    mov  qword [rsp+88], 0
    API  CreateWindowExW
    mov  [rel hw_cancel], rax
    mov  rcx, rax
    mov  rdx, [rel f_body]
    call set_font

    ; show the first page, then the window
    mov  ecx, 0
    call show_page
    mov  rcx, [rel hwnd_main]
    mov  edx, SW_SHOWNORMAL
    API  ShowWindow
    mov  rcx, [rel hwnd_main]
    API  UpdateWindow
    mov  eax, 1
    EPILOG
.fail:
    xor  eax, eax
    EPILOG

; --- show wizard page n (0..6). rcx = n -----------------------------------------------------
show_page:
    PROLOG 96
    mov  [rbp-8], ecx
    mov  [rel page_idx], ecx

    ; title text
    PTR  rax, page_titles
    mov  edx, [rbp-8]
    mov  r10, [rax+rdx*8]
    mov  rcx, [rel hwnd_title]
    mov  rdx, r10
    API  SetWindowTextW

    ; visibility walk
    PTR  rsi, vis_table
.vis:
    mov  rax, [rsi]
    test rax, rax
    jz   .vis_done
    mov  r10d, [rsi+8]
    mov  ecx, [rbp-8]
    bt   r10, rcx
    mov  rcx, [rax]             ; hwnd
    mov  edx, SW_HIDE
    jnc  .hide
    mov  edx, SW_SHOW
.hide:
    API  ShowWindow
    add  rsi, 16
    jmp  .vis
.vis_done:

    ; navigation state per page
    mov  ecx, [rbp-8]
    cmp  ecx, 0
    je   .pg0
    cmp  ecx, 1
    je   .pg1
    cmp  ecx, 4
    je   .pg4
    cmp  ecx, 5
    je   .pg5
    cmp  ecx, 6
    je   .pg6
    ; pages 2,3: back on, next = "Next >", cancel on
    mov  rcx, [rel hw_back]
    mov  edx, 1
    API  EnableWindow
    mov  rcx, [rel hw_next]
    PTR  rdx, btn_next
    API  SetWindowTextW
    mov  rcx, [rel hw_next]
    mov  edx, 1
    API  EnableWindow
    mov  rcx, [rel hw_cancel]
    mov  edx, 1
    API  EnableWindow
    jmp  .done
.pg0:
    mov  rcx, [rel hw_back]
    xor  edx, edx
    API  EnableWindow
    mov  rcx, [rel hw_next]
    PTR  rdx, btn_next
    API  SetWindowTextW
    jmp  .done
.pg1:
    mov  rcx, [rel hw_back]
    mov  edx, 1
    API  EnableWindow
    ; next enabled only when the license is accepted
    mov  rcx, [rel hw_accept]
    call get_check
    mov  rcx, [rel hw_next]
    mov  edx, eax
    API  EnableWindow
    mov  rcx, [rel hw_next]
    PTR  rdx, btn_next
    API  SetWindowTextW
    jmp  .done
.pg4:
    call build_summary
    mov  rcx, [rel hw_sum2]
    PTR  rdx, sum_buf
    API  SetWindowTextW
    mov  rcx, [rel hw_back]
    mov  edx, 1
    API  EnableWindow
    mov  rcx, [rel hw_next]
    mov  edx, 1
    API  EnableWindow
    mov  rcx, [rel hw_cancel]
    mov  edx, 1
    API  EnableWindow
    mov  rcx, [rel hw_next]
    PTR  rdx, btn_install
    API  SetWindowTextW
    jmp  .done
.pg5:
    ; lock navigation while installing
    mov  rcx, [rel hw_back]
    xor  edx, edx
    API  EnableWindow
    mov  rcx, [rel hw_next]
    xor  edx, edx
    API  EnableWindow
    mov  rcx, [rel hw_cancel]
    xor  edx, edx
    API  EnableWindow
    mov  rcx, [rel hw_pbar]
    mov  edx, PBM_SETPOS
    xor  r8d, r8d
    xor  r9d, r9d
    API  SendMessageW
    mov  rcx, [rel hw_pstat]
    PTR  rdx, st_extract
    API  SetWindowTextW
    jmp  .done
.pg6:
    mov  rcx, [rel hw_next]
    PTR  rdx, btn_finish
    API  SetWindowTextW
    mov  rcx, [rel hw_next]
    mov  edx, 1
    API  EnableWindow
.done:
    EPILOG

; --- build the ready-page summary into sum_buf ---------------------------------------------------
build_summary:
    PROLOG 64
    PTR  rcx, sum_buf
    PTR  rdx, sum_dir
    API  lstrcpyW
    PTR  rcx, sum_buf
    PTR  rdx, install_dir
    API  lstrcatW
    PTR  rcx, sum_buf
    PTR  rdx, nl
    API  lstrcatW
    PTR  rcx, sum_buf
    cmp  dword [rel opt_addpath], 1
    je   .py
    PTR  rdx, sum_path_n
    jmp  .pc
.py:
    PTR  rdx, sum_path_y
.pc:
    API  lstrcatW
    PTR  rcx, sum_buf
    PTR  rdx, nl
    API  lstrcatW
    PTR  rcx, sum_buf
    cmp  dword [rel opt_desktop], 1
    je   .dy
    PTR  rdx, sum_desk_n
    jmp  .dc
.dy:
    PTR  rdx, sum_desk_y
.dc:
    API  lstrcatW
    PTR  rcx, sum_buf
    PTR  rdx, nl
    API  lstrcatW
    PTR  rcx, sum_buf
    PTR  rdx, nl
    API  lstrcatW
    PTR  rcx, sum_buf
    PTR  rdx, b_ready2
    API  lstrcatW
    EPILOG
; ============================================================================
; Sidebar painting — the "Guided Split" brand panel
; ============================================================================
paint_sidebar:
    PROLOG 160
    PTR  rcx, hwnd_main
    PTR  rdx, paintstruct
    API  BeginPaint
    mov  [rbp-8], rax                 ; hdc

    PTR  rcx, hwnd_main
    PTR  rdx, rc_paint
    API  GetClientRect
    PTR  rax, rc_paint
    mov  dword [rax+8], SIDE_W
    mov  eax, [rax+12]
    mov  [rbp-40], eax                ; client height

    ; teal background
    mov  rcx, [rbp-8]
    PTR  rdx, rc_paint
    mov  r8, [rel br_teal]
    API  FillRect

    ; icon: orange ring, dark teal disc
    mov  rcx, [rbp-8]
    mov  rdx, [rel pen_orange]
    API  SelectObject
    mov  rcx, [rbp-8]
    mov  rdx, [rel br_teal_dk]
    API  SelectObject
    mov  rcx, [rbp-8]
    mov  edx, 70
    mov  r8d, 36
    mov  r9d, 160
    mov  dword [rsp+32], 126
    API  Ellipse
    ; thread curve across the disc
    mov  rcx, [rbp-8]
    mov  rdx, [rel pen_cream]
    API  SelectObject
    mov  rcx, [rbp-8]
    PTR  rdx, thread_pts
    mov  r8d, 4
    API  PolyBezier

    ; text
    mov  rcx, [rbp-8]
    mov  edx, TRANSPARENT
    API  SetBkMode
    mov  rcx, [rbp-8]
    mov  edx, COL_WHITE
    API  SetTextColor
    mov  rcx, [rbp-8]
    mov  rdx, [rel f_sidebig]
    API  SelectObject
    ; dominant Sanskrit form
    PTR  rax, rc_paint
    mov  dword [rax], 8
    mov  dword [rax+4], 138
    mov  dword [rax+8], SIDE_W-8
    mov  dword [rax+12], 192
    mov  rcx, [rbp-8]
    PTR  rdx, w_sanskrit
    mov  r8d, 7
    PTR  r9, rc_paint
    mov  dword [rsp+32], DT_CENTER | DT_SINGLELINE | DT_VCENTER
    API  DrawTextW

    ; the other ten scripts, smaller
    mov  rcx, [rbp-8]
    mov  rdx, [rel f_sideword]
    API  SelectObject
    mov  rcx, [rbp-8]
    mov  edx, COL_CREAM
    API  SetTextColor
    PTR  rsi, lang_table
    mov  dword [rbp-16], 204
.lang:
    mov  rax, [rsi]
    test rax, rax
    jz   .lang_done
    mov  r10d, dword [rsi+8]
    mov  [rbp-24], rax
    mov  [rbp-32], r10
    PTR  rax, rc_paint
    mov  dword [rax], 8
    mov  ecx, [rbp-16]
    mov  [rax+4], ecx
    mov  dword [rax+8], SIDE_W-8
    add  ecx, 26
    mov  [rax+12], ecx
    mov  rcx, [rbp-8]
    mov  rdx, [rbp-24]
    mov  r8d, dword [rbp-32]
    PTR  r9, rc_paint
    mov  dword [rsp+32], DT_CENTER | DT_SINGLELINE | DT_VCENTER
    API  DrawTextW
    add  rsi, 16
    add  dword [rbp-16], 26
    jmp  .lang
.lang_done:

    ; footer
    mov  rcx, [rbp-8]
    mov  rdx, [rel f_sidetiny]
    API  SelectObject
    mov  rcx, [rbp-8]
    mov  edx, COL_SIDE_DIM
    API  SetTextColor
    PTR  rax, rc_paint
    mov  dword [rax], 8
    mov  ecx, [rbp-40]
    sub  ecx, 42
    mov  [rax+4], ecx
    mov  dword [rax+8], SIDE_W-8
    mov  ecx, [rbp-40]
    sub  ecx, 14
    mov  [rax+12], ecx
    mov  rcx, [rbp-8]
    PTR  rdx, side_footer
    mov  r8d, 12
    PTR  r9, rc_paint
    mov  dword [rsp+32], DT_CENTER | DT_SINGLELINE | DT_VCENTER
    API  DrawTextW

    PTR  rcx, hwnd_main
    PTR  rdx, paintstruct
    API  EndPaint
    EPILOG

; --- folder picker ----------------------------------------------------------------------
do_browse:
    PROLOG 128
    PTR  rdi, browseinfo
    mov  ecx, 8
    xor  eax, eax
    rep  stosq
    PTR  rax, browseinfo
    mov  rcx, [rel hwnd_main]
    mov  [rax], rcx
    PTR  r10, dispname
    mov  [rax+16], r10
    PTR  r10, brow_title
    mov  [rax+24], r10
    mov  dword [rax+32], BIF_RETURNONLYFSDIRS | BIF_NEWDIALOGSTYLE
    mov  rcx, rax
    API  SHBrowseForFolderW
    test rax, rax
    jz   .done
    mov  [rbp-8], rax
    mov  rcx, rax
    PTR  rdx, dispname
    API  SHGetPathFromIDListW
    mov  rcx, [rbp-8]
    API  CoTaskMemFree
    mov  rcx, [rel hw_diredit]
    PTR  rdx, dispname
    API  SetWindowTextW
.done:
    EPILOG

; --- launch Sutram Terminal after a successful install -------------------------------------
launch_terminal:
    PROLOG 96
    PTR  rcx, cmdline
    PTR  rdx, cmd_term1
    API  lstrcpyW
    PTR  rcx, cmdline
    PTR  rdx, quote
    API  lstrcatW
    PTR  rcx, cmdline
    PTR  rdx, cmd_set
    API  lstrcatW
    PTR  rcx, cmdline
    PTR  rdx, quote
    API  lstrcatW
    PTR  rcx, cmdline
    PTR  rdx, cmd_patheq
    API  lstrcatW
    PTR  rcx, cmdline
    PTR  rdx, install_dir
    API  lstrcatW
    PTR  rcx, cmdline
    PTR  rdx, cmd_binsemi
    API  lstrcatW
    PTR  rcx, cmdline
    PTR  rdx, cmd_pathvar
    API  lstrcatW
    PTR  rcx, cmdline
    PTR  rdx, quote
    API  lstrcatW
    PTR  rcx, cmdline
    PTR  rdx, cmd_andver
    API  lstrcatW
    PTR  rcx, cmdline
    PTR  rdx, quote
    API  lstrcatW
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
    jz   .done
    mov  rcx, [rel procinfo]
    API  CloseHandle
    mov  rcx, [rel procinfo+8]
    API  CloseHandle
.done:
    EPILOG

; --- Next / Install / Finish ------------------------------------------------------------------
on_next:
    PROLOG 96
    mov  eax, [rel page_idx]
    cmp  eax, 0
    je   .p0
    cmp  eax, 1
    je   .p1
    cmp  eax, 2
    je   .p2
    cmp  eax, 3
    je   .p3
    cmp  eax, 4
    je   .p4
    cmp  eax, 6
    je   .p6
    EPILOG
.p0:
    mov  ecx, 1
    call show_page
    EPILOG
.p1:
    mov  ecx, 2
    call show_page
    EPILOG
.p2:
    mov  rcx, [rel hw_diredit]
    PTR  rdx, install_dir
    mov  r8d, MAXP
    API  GetWindowTextW
    test eax, eax
    jz   .nodir
    mov  ecx, 3
    call show_page
    EPILOG
.nodir:
    xor  ecx, ecx
    PTR  rdx, msg_nodir
    PTR  r8,  msg_title
    mov  r9d, MB_OK | MB_ICONERROR
    API  MessageBoxW
    EPILOG
.p3:
    mov  rcx, [rel hw_ckpath]
    call get_check
    mov  [rel opt_addpath], eax
    mov  rcx, [rel hw_ckdesk]
    call get_check
    mov  [rel opt_desktop], eax
    mov  ecx, 4
    call show_page
    EPILOG
.p4:
    mov  ecx, 5
    call show_page
    mov  dword [rel installing], 1
    xor  ecx, ecx
    xor  edx, edx
    PTR  r8, install_thread
    xor  r9d, r9d
    mov  qword [rsp+32], 0
    mov  qword [rsp+40], 0
    API  CreateThread
    mov  [rel h_thread], rax
    EPILOG
.p6:
    mov  rcx, [rel hw_cklaunch]
    call get_check
    test eax, eax
    jz   .close
    call launch_terminal
.close:
    mov  rcx, [rel hwnd_main]
    API  DestroyWindow
    EPILOG

on_back:
    PROLOG 48
    mov  eax, [rel page_idx]
    cmp  eax, 1
    je   .b
    cmp  eax, 2
    je   .b
    cmp  eax, 3
    je   .b
    cmp  eax, 4
    je   .b
    EPILOG
.b:
    dec  eax
    mov  ecx, eax
    call show_page
    EPILOG

; ============================================================================
; Window procedure
; ============================================================================
wndproc:
    PROLOG 128
    mov  [rbp-8], rcx
    mov  [rbp-16], rdx
    mov  [rbp-24], r8
    mov  [rbp-32], r9
    cmp  edx, WM_CREATE
    je   .create
    cmp  edx, WM_PAINT
    je   .paint
    cmp  edx, WM_COMMAND
    je   .command
    cmp  edx, WM_WIZ_PROGRESS
    je   .progress
    cmp  edx, WM_WIZ_DONE
    je   .done_msg
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
    xor  eax, eax
    EPILOG
.paint:
    call paint_sidebar
    xor  eax, eax
    EPILOG
.command:
    movzx eax, word [rbp-24]       ; control id
    movzx edx, word [rbp-22]       ; notification
    cmp  eax, IDC_BACK
    je   .do_back
    cmp  eax, IDC_NEXT
    je   .do_next
    cmp  eax, IDC_CANCEL
    je   .do_cancel
    cmp  eax, IDC_BROWSE
    je   .do_browse
    cmp  eax, IDC_ACCEPT
    jne  .chk_decline
    cmp  edx, BN_CLICKED
    jne  .cmd_done
    mov  rcx, [rel hw_next]
    mov  edx, 1
    API  EnableWindow
    jmp  .cmd_done
.chk_decline:
    cmp  eax, IDC_DECLINE
    jne  .cmd_done
    cmp  edx, BN_CLICKED
    jne  .cmd_done
    mov  rcx, [rel hw_next]
    xor  edx, edx
    API  EnableWindow
.cmd_done:
    xor  eax, eax
    EPILOG
.do_back:
    call on_back
    xor  eax, eax
    EPILOG
.do_next:
    call on_next
    xor  eax, eax
    EPILOG
.do_browse:
    call do_browse
    xor  eax, eax
    EPILOG
.do_cancel:
    cmp  dword [rel installing], 1
    je   .cmd_done
    mov  rcx, [rbp-8]
    API  DestroyWindow
    xor  eax, eax
    EPILOG
.progress:
    ; wParam = percent
    mov  rcx, [rel hw_pbar]
    mov  edx, PBM_SETPOS
    mov  r8, [rbp-24]
    xor  r9d, r9d
    API  SendMessageW
    mov  rax, [rbp-24]
    cmp  rax, 55
    jl   .st_extract
    cmp  rax, 90
    jl   .st_script
    PTR  rdx, st_final
    jmp  .st_set
.st_extract:
    PTR  rdx, st_extract
    jmp  .st_set
.st_script:
    PTR  rdx, st_script
.st_set:
    mov  rcx, [rel hw_pstat]
    API  SetWindowTextW
    xor  eax, eax
    EPILOG
.done_msg:
    ; wParam = engine status: 0 ok, 1 failed, 2 no PowerShell
    mov  dword [rel installing], 0
    mov  rax, [rbp-24]
    test rax, rax
    jnz  .done_bad
    mov  ecx, 6
    call show_page
    xor  eax, eax
    EPILOG
.done_bad:
    cmp  rax, 2
    jne  .done_fail
    xor  ecx, ecx
    PTR  rdx, msg_nopower
    PTR  r8,  msg_title
    mov  r9d, MB_OK | MB_ICONERROR
    API  MessageBoxW
    jmp  .done_back
.done_fail:
    xor  ecx, ecx
    PTR  rdx, msg_failed
    PTR  r8,  msg_title
    mov  r9d, MB_OK | MB_ICONERROR
    API  MessageBoxW
.done_back:
    mov  ecx, 4
    call show_page
    xor  eax, eax
    EPILOG
.close:
    cmp  dword [rel installing], 1
    je   .close_done
    mov  rcx, [rbp-8]
    API  DestroyWindow
.close_done:
    xor  eax, eax
    EPILOG
.destroy:
    xor  ecx, ecx
    API  PostQuitMessage
    xor  eax, eax
    EPILOG

; --- message loop ---------------------------------------------------------------------------
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

; ============================================================================
; Entry point
; ============================================================================
section .data
msg_fb_ask:  u16 "Install Sutram for the current user with default options?"
msg_fb_done: u16 "Sutram installed successfully."

section .text
_start:
    and  rsp, -16
    sub  rsp, 8
    PROLOG 96
    call init_apis
    test eax, eax
    jz   .quit

    API  GetCommandLineW
    mov  rcx, rax
    PTR  rdx, arg_uninstall
    call find_w
    test rax, rax
    jz   .do_install
    call do_uninstall
    jmp  .quit

.do_install:
    call create_window
    test eax, eax
    jnz  .run_gui

    ; ---- no interactive desktop: fall back to a single confirmation dialog ----
    xor  ecx, ecx
    PTR  rdx, msg_fb_ask
    PTR  r8,  msg_title
    mov  r9d, MB_YESNO | MB_ICONQUESTION
    API  MessageBoxW
    cmp  eax, IDYES
    jne  .quit
    PTR  rcx, env_localappdata
    PTR  rdx, local_appdata
    mov  r8d, MAXP
    API  GetEnvironmentVariableW
    PTR  rcx, install_dir
    PTR  rdx, local_appdata
    PTR  r8,  sub_programs
    call join
    mov  dword [rel opt_addpath], 1
    mov  dword [rel opt_desktop], 0
    call do_install_staged
    cmp  eax, 2
    je   .fb_nopw
    test eax, eax
    jnz  .fb_fail
    xor  ecx, ecx
    PTR  rdx, msg_fb_done
    PTR  r8,  msg_title
    mov  r9d, MB_OK | MB_ICONINFORMATION
    API  MessageBoxW
    jmp  .quit
.fb_nopw:
    xor  ecx, ecx
    PTR  rdx, msg_nopower
    PTR  r8,  msg_title
    mov  r9d, MB_OK | MB_ICONERROR
    API  MessageBoxW
    jmp  .quit
.fb_fail:
    xor  ecx, ecx
    PTR  rdx, msg_failed
    PTR  r8,  msg_title
    mov  r9d, MB_OK | MB_ICONERROR
    API  MessageBoxW
    jmp  .quit

.run_gui:
    call gui_loop
.quit:
    xor  ecx, ecx
    API  ExitProcess
