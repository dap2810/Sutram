#!/usr/bin/env python3
"""Restructure sutram_setup.asm: extract the install work into do_install(),
add a real installer window with a MessageBox fallback."""

P = "/scratch/work/windows/native-installer/sutram_setup.asm"
src = open(P, encoding="utf-8").read()
lines = src.split("\n")

def find(needle, start=0):
    for i in range(start, len(lines)):
        if needle in lines[i]:
            return i
    raise SystemExit(f"marker not found: {needle}")

# ---- 1. Extract the install work (section 2 .. just before section 8) -------
a = find("; 2. %TEMP%")
b = find("; 8. Wait and report.")
work = lines[a:b]

# Re-indent is unnecessary; rename local labels so they live in do_install.
work = [l.replace(".failed", ".dfail").replace(".nopowershell", ".dnopw") for l in work]
# The work block ends with `jz .dnopw`; after that it falls through to the
# CreateProcess success path, so append wait + status return.
work_tail = [
    "",
    "    ; wait for PowerShell, then return a status code",
    "    mov  rcx, [rel procinfo]",
    "    mov  edx, INFINITE",
    "    API  WaitForSingleObject",
    "    mov  rcx, [rel procinfo]",
    "    PTR  rdx, exit_code",
    "    API  GetExitCodeProcess",
    "    cmp  dword [rel exit_code], 0",
    "    jne  .dfail",
    "    xor  eax, eax            ; 0 = installed",
    "    EPILOG",
    ".dnopw:",
    "    mov  eax, 2              ; 2 = PowerShell could not start",
    "    EPILOG",
    ".dfail:",
    "    mov  eax, 1              ; 1 = install failed",
    "    EPILOG",
]

do_install = (
    ["; ---------------------------------------------------------------------------",
     "; Perform the installation.  Returns eax: 0 ok, 1 failed, 2 no PowerShell.",
     "do_install:",
     "    PROLOG 96"]
    + work
    + work_tail
)

# ---- 2. Remove the old work from _start ------------------------------------
del lines[a:b]
# also drop the now-orphaned reporting tail of the old _start
r = find("; 8. Wait and report.")
r2 = find(".quit:", r)
# find the end of the old report block: the .quit that ends _start's install path
del lines[r:r2]

# ---- 3. Replace the confirm-and-go with a GUI dispatch ---------------------
c = find("; 1. Confirm.")
# the confirm block runs to the line after `jne  .quit`
end = c
while "jne  .quit" not in lines[end]:
    end += 1
end += 1
dispatch = [
    "    ; Prefer the graphical installer window; fall back to a dialog if",
    "    ; the window cannot be created (no interactive desktop, policy).",
    "    call create_window",
    "    test eax, eax",
    "    jnz  .run_gui",
    "",
    "    ; ---- fallback: single confirmation dialog ----",
    "    xor  ecx, ecx",
    "    PTR  rdx, msg_welcome",
    "    PTR  r8,  msg_title",
    "    mov  r9d, MB_YESNO | MB_ICONQUESTION",
    "    API  MessageBoxW",
    "    cmp  eax, IDYES",
    "    jne  .quit",
    "    call do_install",
    "    cmp  eax, 2",
    "    je   .mb_nopw",
    "    test eax, eax",
    "    jnz  .mb_fail",
    "    xor  ecx, ecx",
    "    PTR  rdx, msg_done",
    "    PTR  r8,  msg_title",
    "    mov  r9d, MB_OK | MB_ICONINFORMATION",
    "    API  MessageBoxW",
    "    jmp  .quit",
    ".mb_nopw:",
    "    xor  ecx, ecx",
    "    PTR  rdx, msg_nopower",
    "    PTR  r8,  msg_title",
    "    mov  r9d, MB_OK | MB_ICONERROR",
    "    API  MessageBoxW",
    "    jmp  .quit",
    ".mb_fail:",
    "    xor  ecx, ecx",
    "    PTR  rdx, msg_failed",
    "    PTR  r8,  msg_title",
    "    mov  r9d, MB_OK | MB_ICONERROR",
    "    API  MessageBoxW",
    "    jmp  .quit",
    "",
    ".run_gui:",
    "    call gui_loop",
    "    jmp  .quit",
]
lines[c:end] = dispatch

out = "\n".join(lines)
# append the extracted install function at the end of the text section
out = out.rstrip("\n") + "\n\n" + "\n".join(do_install) + "\n"
open(P, "w", encoding="utf-8").write(out)
print("restructured: do_install extracted, GUI dispatch added")
