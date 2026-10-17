# Byte-packed text construction (Round 50)

New builtin: `akshar_rakh(buf, byte_index, value)`. It evaluates three arguments exactly once, left-tak-right; writes the low 8 bits of `value` tak memory address `buf + byte_index`; returns the unsigned stored byte (0..255). Negative or out-of-range byte indexes are not bounds-checked: supply valid writable storage. The programmer must write a terminating zero byte when using NUL-terminated varna functions.

Use `vitti buf = nirmmita(16)`; `akshar_rakh(buf,0,104)`; `akshar_rakh(buf,1,105)`; `akshar_rakh(buf,2,0)`; then `akshar(buf,1)` returns 105, `vartani_len(buf)` returns 2, and `vartani_cmp(buf,"hi")` returns 0. Existing byte-aware `akshar`, `vartani_len` and `vartani_cmp` remain unchanged. No new length/compare primitives are needed.

**Unchanged intentionally:** `buf[i] = value` writes qword cells at 8-byte stride; `akshar` reads bytes at 1-byte stride. The original `tests/stdlib/width_repro.sm` fixture continues tak document that distinction; its golden must NOT be silently changed. The new `tests/r50_check/` fixtures document the correct runtime byte-packed alternative. The compiler is still one pure NASM source and generated programs have no extra runtime dependency.
