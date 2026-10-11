# Round 52 — builtin correctness and compatibility

Round 52 fixes compiler defects discovered during the standard-library work. The implementation remains in the single native NASM compiler `src/sutram_compiler.asm`.

## `char_code(s, i)` — already correct in the accepted compiler

The old `lib/string.smlib` comment claimed `char_code` ignored its index. This was stale. The current compiler already emits indexed-byte loads when given two arguments. `char_code("AZ", 1)` returns `90`, while `char_code("AZ")` remains a compatible single-argument form returning `65`. The new `tests/r52_check/char_code_index.sm` executes both, plus `char_at` and a dynamically built `set_char` byte string. The compiler now rejects any other argument count instead of dereferencing absent AST nodes.

## `likh(addr, value)` — fixed compiler crash

`likh` writes a full 64-bit qword into caller-owned writable memory at `addr`. The parser formerly constructed its AST from a stale `call_args` scratch buffer; arguments are actually stashed on the parser stack. This caused a compiler segfault even for a valid two-argument program. The parser now pops the *two actual parsed AST nodes* and checks the count. Invalid arities produce a recoverable `E_PARSE` under `--check`. `likh` is a qword store; `set_char` is a byte store, so `pad` sees the low byte of a qword.

## `dvaram(path, flags[, mode])` — fixed creation permissions

The Linux-native builtin wraps `open(2)`, returning its file descriptor. On a two-argument call it now supplies deterministic mode **0644** (`420` decimal) in `rdx`, rather than leaving the register uninitialized. With a third argument the emitted program evaluates the mode once and passes it to `rdx`. The effective mode still honors the running process's **umask**. Examples:

```sutram
vitti fd = dvaram("example.txt", 577)       # O_WRONLY | O_CREAT | O_TRUNC, mode 0644
band(fd)
vitti private_fd = dvaram("private.txt", 577, 384)  # explicit mode 0600
band(private_fd)
```

The Linux `open` flags `577` are `O_WRONLY | O_CREAT | O_TRUNC` on the tested Linux ABI. This is a Linux syscall-level guarantee, **not an unverified promise of Windows-host equivalence**. `dvaram` accepts exactly 2 or 3 arguments.

## Other related builtins

The new checks also reject invalid arities for `char_at` (exactly 2 arguments) and `char_code` (1 or 2 arguments). `set_char` already validates exactly 3 arguments and was not changed. `pad`, `pad8`, `likh8`, `char_from`, and several other older low-level builtins were **not fully audited for missing-argument AST safety in this round**. Avoid invalid arities; a future dedicated sweep should check their guards and bounds behavior. No claim of automatic bounds-checking is made for raw pointer operations.

Existing expected-output goldens and cell-array byte-width semantics were not modified. The four accepted R46 ordinary-codegen samples still produce byte-identical binaries. Only calls to the defect-affected functions intentionally change generated code.
