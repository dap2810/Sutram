/* R92 control: raw Linux _start, SysV ABI call into freestanding C. */
.intel_syntax noprefix
.section .rodata
msg:
  .ascii "NO_LIBC_C_CALL=42\n"
.set msg_len, . - msg
.section .text
.globl _start
.extern sutram_ffi_add
_start:
  and rsp, -16
  mov edi, 17
  mov esi, 25
  call sutram_ffi_add
  cmp eax, 42
  jne failed
  mov eax, 1
  mov edi, 1
  lea rsi, [rip + msg]
  mov edx, msg_len
  syscall
  mov edi, 42
  mov eax, 60
  syscall
failed:
  mov edi, 99
  mov eax, 60
  syscall
.section .note.GNU-stack,"",@progbits
