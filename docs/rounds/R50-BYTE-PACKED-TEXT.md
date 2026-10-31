# Byte-packed text construction (Round 50)

New builtin: `set_char(buf, byte_index, value)`. It evaluates three arguments exactly once, left-to-right; writes the low 8 bits of `value` to memory address `buf + byte_index`; returns the unsigned stored byte (0..255). Negative or out-of-range byte indexes are not bounds-checked: supply valid writable storage. The programmer must write a terminating zero byte when using NUL-terminated string functions.

Use `vitti buf = nirmmita(16)`; `set_char(buf,0,104)`; `set_char(buf,1,105)`; `set_char(buf,2,0)`; then `char_at(buf,1)` returns 105, `vartani_len(buf)` returns 2, and `vartani_cmp(buf,"hi")` returns 0. Existing byte-aware `char_at`, `vartani_len` and `vartani_cmp` remain unchanged. No new length/compare primitives are needed.

**Unchanged intentionally:** `buf[i] = value` writes qword cells at 8-byte stride; `char_at` reads bytes at 1-byte stride. The original `tests/stdlib/width_repro.sm` fixture continues to document that distinction; its golden must NOT be silently changed. The new `tests/r50_check/` fixtures document the correct runtime byte-packed alternative. The compiler is still one pure NASM source and generated programs have no extra runtime dependency.
