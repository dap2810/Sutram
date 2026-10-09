# Sutram — Windows (native) port plan

Status: **started**. Build toolchain verified; first primitive written.

## Why a port, not a repackage
- The compiler talks to the Linux kernel with `syscall` (~31 sites:
  open/read/write/close/exit/mmap) and emits **ELF64** executables whose
  machine code also uses Linux syscalls.
- On Windows the compiler must call kernel32, and the programs it emits
  must be **PE64** calling kernel32. So both halves change.

## Toolchain (verified working here)
    nasm -f win64 prog.asm -o prog.obj
    ld   -mi386pep --entry=_start -o prog.exe prog.obj
    -> file(1): "PE32+ executable (console) x86-64, for MS Windows"

## Steps
1. [x] Verify Windows build toolchain (nasm win64 + ld i386pep).
2. [x] win/winapi.asm — locate kernel32 via the PEB and parse its export
       table (win_resolve). No import libraries needed. Assembles, links,
       structure verified. Runtime needs a Windows machine to confirm.
3. [x] OS layer in the compiler source (os_open/os_read/os_write/os_close/
       os_exit/os_readlink). Linux impl = raw syscalls (behaviour
       unchanged, 51/51 examples still pass); Windows impl in
       win/winrt.inc via kernel32. Compiler now ASSEMBLES and LINKS as a
       valid PE32+  ->  win/sutram.exe  (./win/build-windows.sh).
       Still Linux-shaped inside: argv comes from the stack (Windows needs
       GetCommandLineA) and the output writer still emits ELF.
4. [ ] PE64 writer in the compiler (replaces the ELF writer): DOS header,
       PE header, one code+data section, entry point.
       [ ] Windows argv: GetCommandLineA + parse (replaces stack argc/argv).
5. [ ] Codegen: emit Win64 API calls for the generated programs' write /
       read / exit / allocate instead of syscalls.
6. [ ] Package: folder + install.bat (adds PATH) and the existing NSIS
       script windows/sutram-installer.nsi for a double-click setup.

## Interim route (available now)
`windows/sutram-windows-wsl.zip` — install.bat sets up the existing Linux
compiler under WSL; sutram.cmd converts Windows paths and runs it.
