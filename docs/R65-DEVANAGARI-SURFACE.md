# R65 Sanskrit/Devanagari alias extension

The accepted `lang/sanskrit.lang` already maps 31 core keywords including `kosh`, `pankti`, `rachana`, `srijana`, `kuru`, `nishkriya`, `parigrah`, and `grahan` (grahan is a builtin in the compiler). R65 preserves those mappings rather than introducing duplicate keyword entries.

R65 adds **18 aliases for existing recognised builtins** in `lang/sanskrit.lang`: printing, halt, file/byte, memory allocation, string/array length, and `kosh` operations. Each RHS has to resolve to an existing builtin ID through `lookup_builtin`; no new builtin semantics have been invented. These aliases are supported when the Sanskrit language pack is active (`--lang sanskrit` or `SUTRAM_LANG=sanskrit`). Danda and double-danda lexing remain unchanged.

The string `niryat` from the incoming examples is **not** an existing recognised keyword or builtin in the checked compiler table. It was deliberately not mapped as if a native export statement already existed.

Proof fixture: `examples/219_sanskrit_kosh_aliases.sm` should output the bytes in `tests/r65_check/sanskrit_kosh_aliases.out` using `sutram --lang sanskrit <fixture.sm> <executable>`, then execute the generated Linux binary. Native compilation/execution are left to Sarvam.

Safety constraints: no edits to `is_alpha`, Indic UTF-8 multi-byte lexer handling, danda recognition, or accepted goldens. The new aliases must still be validated by Sarvam's language pack gate and native invocation.
