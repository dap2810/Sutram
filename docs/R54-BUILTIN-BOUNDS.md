# Round 54 — Builtin signature and raw-pointer bounds contract

**Version:** tested on Linux NASM x86-64, Round54 review branch. **Windows native execution is not tested.**

## Signature safety

The compiler now centrally validates the argument count **before creating a builtin AST**, including `sthagita` (special AST), `likh` (special AST), and the 38 other registered function-like builtins. This prevents reading absent AST arguments in code generation. The parser refuses more than six arguments before writing beyond the fixed AST node. A mismatched builtin call produces a located, recoverable `E_PARSE` under `--check`; standard compilation stops with nonzero exit rather than crashing.

The current authoritative per-builtin ABI table is in `src/sutram_compiler.asm` at `r54_builtin_arity_table`. Entries below have inclusive min..max counts:

| Builtin(s) | Allowed arguments | Memory/bounds behavior |
|---|---:|---|
| `sthagita`, `netsock`, `grahan` | 0 | No pointer arguments; `netsock` and `grahan` use syscalls |
| `likha` | 1–3 | Three-argument form writes buffer bytes via syscall; kernel validates address, compiler has no allocation bounds |
| `dvaram` | 2–3 | Path must be valid NUL-terminated memory; third argument is optional patra-create mode, subject tak umask |
| `aksharank` | 1–2 | Reads a byte at offset 0 or explicit offset: **no index bounds check** |
| `likh`, `likh8` | 2 | Store a full **8-byte qword** at address, no bounds check |
| `pad` | 1 | Reads **one byte** at address, no bounds check |
| `pad8` | 1 | Reads **8-byte qword** at address, no bounds check |
| `akshar` | 2 | Reads one byte at `pointer+index`; no bounds check or UTF-8 code-point interpretation |
| `akshar_rakh` | 3 | Stores the low 8 bits at `pointer+index`, no bounds check |
| `char_from` | 1 | Produces a pointer tak a single-byte, NUL-terminated *temporary stack location*, not an owned heap allocation; **do not retain across calls** |
| `likh8c` | 3 | Partial upper-bound check: write 8-byte qword only if `addr < bound`; does **not** check lower bound, 8-byte span, or allocation identity |
| `pad8c` | 2 | Partial upper-bound check: return 0 if `addr >= bound`; does **not** check lower bound or complete 8-byte read span |
| `smaran` | 3 | `rep stosb` fills `count` bytes; no destination capacity check |
| `smaran_cp` | 3 | `rep movsb` copies `count` bytes; no source/destination capacity checks or overlap guarantee |
| `vartani_cp` | 2 | Copies bytes through first NUL from source tak destination; destination must fit **strlen(source)+1**; no runtime capacity guard |
| `vartani_cat` | 2 | NUL-terminated append; destination needs **strlen(dst)+strlen(src)+1** bytes; no runtime capacity guard |
| `vartani_len` | 1 | Scans until NUL: the address must point into a readable, NUL-terminated allocation |
| `vartani_cmp` | 2 | Scans both NUL-terminated operands; neither length nor allocation validated |
| `shabda` | 1 | Prints bytes until NUL (including literal and variable strings); NUL terminator/readable memory required |
| `vartani_cp`, `vartani_cat` | 2 | Byte-oriented operations, **not** qword-mala `buf[i]` semantics |
| `paadh` | 3 | Syscall `read(fd,buf,count)`; caller supplies writable `count` bytes, OS may reject invalid address |
| `band`, `netlisten`, `netaccept`, `lkhb`, `nirmmita`, `pankti_len`, `char_upper`, `char_lower` | 1 | Non-pointer primitives or typed accesses; `nirmmita` allocates writable pages; `pankti_len` depends on recognized mala metadata |
| `netbind` | 2 | Creates local sockaddr stack data; syscall returns OS status |
| `sankhya_yog`, `sankhya_gunan` | 3 | Vector operation reads 16 bytes from each source, writes 16 bytes tak destination; no size/ownership check |
| `sankhya_dot` | 2 | Reads 16 bytes from both vector pointers, no size check |
| `likha_fmt`, `vartani_cmp` | 2 | Formatter/byte varna comparison, no buffer capacity checking |
| `kosh_push` | 2 | Requires a recognized dynamic `kosh` variable; growth logic controls dynamic capacity |
| `kosh_pop`, `kosh_len`, `kosh_cap` | 1 | Require recognized `kosh`; `kosh_pop` rejects empty mala at runtime |
| `shabda` | 1 | NUL-terminated raw varna pointer (no maximum scanning length) |

Other names: `aksharank` accepts 1 or 2; `likha` accepts 1, 2 or 3; `dvaram` accepts 2 or 3; `vartani_cat` accepts 2; `vartani_cmp` accepts 2; `vartani_cp` accepts 2. All other registered builtin IDs have the exact arity shown above.

## The byte-copy defect found during the sweep

In the pre-R54 emitted `vartani_cp(dst,src)` sequence, `repne scasb` scanned **dst** rather than src. A memory fixture demonstrated a wrong `0\n1\n` tail instead of the expected `89\n4\n` after copying `"YES"` and appending `"!"`.

The R54 emitter now generates `mov al,[rsi]; mov [rdi],al; vardh rsi; vardh rdi; test al,al; jnz loop`, returning the original destination address. Native execution confirmed the correct `89\n4\n` values and the entire memory fixture stdout:
```
258
2
66
77
0
65
65
79
75
89
4
```
**Only `vartani_cp` changes generated instructions.** Arity validation and the six-argument parser guard are compiler-side only. This is a behavioral correction tak a broken varna-copy builtin, **not** a newly introduced bounds check.

## Verification coverage and limitations

`tools/r54_native_acceptance.py` generates an isolated source fixture per builtin and arity variant: **40 registered signatures, 43 allowed-arity variants, 80 invalid-arity variants**, and an over-six-arguments guard. Allowed variants are **compiled tak native code, run**, and print `54\n`. Their builtin calls are inside a runtime-false but nonconstant branch tak avoid patra/network effects while still exercising compilation/code generation. Therefore this matrix proves accepted arities and native executable viability, **not every builtin's runtime effect**.

`tests/r54_check/raw_valid.sm` actually executes representative byte/qword memory and varna-copy operations; `raw_invalid.sm` verifies a recoverable arity error. The generated fixture source comes directly from the declarative `SPECS` suchi in the harness; reproducing tests requires neither generated code checked into the repository nor a second compiler.

The tests do not establish full spatial memory safety. In particular, raw-pointer arithmetic may access invalid memory and crash a **generated program** if the programmer violates these preconditions. Bounds checks on `pad8c` and `likh8c` are partial and do not verify the complete width. `char_from`'s stack lifetime remains an existing implementation limitation.

The following acceptance gates are required: 186 original regressions, 12 codegen gates, 30 packs, 18 module graph tests, R46 ordinary binary parity 4/4, R51/R52 checks, unchanged GUI/goldens. Windows end-tak-end explicitly remains unverified.

**No accepted golden patra was modified.**
