# R33-01 — The FFI's kinds, the stage-2 reader, and the nets

## The kinds

```
sutram-ffi-v1|linux-x86_64-sysv
k_mix|6|i64,f64,i64,f64,i64,f64|f64|sutram_k_mix
k_sum|2|ptr,i64|i64|sutram_k_sum
k_set|3|ptr,i64,i64|void|sutram_k_set
```

| Kind | As an argument | As the result |
|---|---|---|
| `i64` | an integer. A `dasham`, a string or a kosh is `E_FFI_KIND` (**never truncated**) | an integer |
| `f64` | a `dasham`, or an integer converted to `dasham`. A string or a kosh is `E_FFI_KIND` | a `dasham`, from `xmm0` |
| `ptr` | a string, a kosh (the address of its elements) or an integer. A `dasham` is `E_FFI_KIND` | an integer |
| `void` | — | none: a statement; its value used anywhere is `E_FFI_KIND` |

**The registers, by the System V rule:** integers and pointers go to `rdi, rsi, rdx, rcx, r8, r9` in order, and
`f64` to `xmm0..xmm5` in order. **The two sequences are counted separately:** `k_mix(1, 2.0, 3, 4.0, 5, 6.0)`
puts `1, 3, 5` in `rdi, rsi, rdx` and `2.0, 4.0, 6.0` in `xmm0, xmm1, xmm2`. **Tested:** the C function returns
`a + 10b + 100c + 1000d + 10000e + 100000f`, and the result is `654321`, so every value was in its place. The
stack is aligned to 16 around every call, as in R32.

**How:** a declared call now has its own code generator, `r33_gen_foreign_funcall` in `src/r32_ffi.inc`. It
checks and evaluates each argument against its kind, then pops each one straight into its register (`movq xmm,
rax` for an `f64`), and makes the aligned call. An `f64` result is moved from `xmm0`, and the compiler's type
inference (`func_return_is_float`) knows it is a `dasham`, so `dasham h = k_half(3.0) + 1.0` is `2.5`.

**`E_FFI_KIND` is located like `E_ARITY`:** `e.sm:3:11: Sutram Error [E_FFI_KIND]: videshi prakriya k_scale:
ghoshitat prakarat bhinnah tarkah 2`, with the source line and the caret. Exit 1, no object written. The message
is in all eleven packs (three new messages).

## The defect it found: a foreign call as a statement

**`k_set(xs, 1, 200)` on its own line** is parsed as a statement call, and statement calls have their own code
path in the compiler. **R32 hooked only the expression path,** so a statement call to a declared function was
compiled as a call to a Sutram prakriya named `k_set`. It failed at the link (`agyat prakriya: k_set`). It was
loud, not silent, but it was broken. R32's test never made a statement call, so it never saw it. **Fixed and
tested:** `k_set` and `k_nothing()` as statements.

## The stage-2 reader: what real C needs

**Stage 1 refused every C function with a `double` constant,** because gcc puts the constant in read-only data
and reaches it with a relocation. `return x / 2.0` was enough to be refused. **Stage 2, in `sutram-elf2smo`:**

- **Read-only data sections** (PROGBITS, ALLOC, not WRITE, not EXEC; MERGE and STRINGS allowed) are placed after
  the code, each at its alignment. **Alignment above 8 is refused:** `sutram-link` lays objects end to end, so a
  16-byte constant (`fabs` uses one) could not stay aligned, and an SSE instruction would fault on it.
- **Relocations in the code** of the two PC-relative kinds, `R_X86_64_PC32` and `R_X86_64_PLT32`, are resolved
  in the converter as `S + A − P`. The target must be the code or a placed data section, and the result must
  fit in 32 bits. **Nothing is left for the linker,** so `SUTRAMO1` and `sutram-link` are still unchanged.
- **Still refused:** an undefined symbol (a C function that calls out), writable data, bss, unwind tables, a
  relocation outside the code, any other relocation kind, `SHT_REL`.

`tests/r33/kinds.o` (nine functions, six relocations into its constants) converts to 416 bytes with no holes left.

## The nets

**`tools/fuzz_ffi.py`** generates random programs. They nest seven foreign functions (`s_add`, `s_neg`, `s_mix`,
`k_half`, `k_scale`, `k_mix`, `k_trunc`) inside Sutram integer and `dasham` arithmetic. They also call a Sutram
prakriya that keeps three locals live across two foreign calls. Every printed value is compared with a Python
model. **4 × 500 programs, 21,880 foreign calls, 10,888 values: 0 differ.** It is a gate (60 programs).

Two notes on the model:
- **Printed `dasham` values are kept below 1e8.** Above about 1e11, `likha` prints inexactly. That is a
  separate finding, in R33-00.
- **A `-0.0` result is expected as `0.000000`,** which is what Sutram prints.

**`tools/fuzz_elf2smo.py`** mutates the two good objects. It hits the fields the reader trusts least: the header,
and every section header's offset, size, link, info and alignment. It also hits every symbol's name, section,
value and size, and every relocation's offset, type, symbol and addend. The values it writes are 0, ±1, the
2^31, 2^32 and 2^63 edges, and random ones. On top of that come random bytes and truncations. **The contract:** no
signal, no hang, exit 0 or 1; on a refusal **no output file**; on an acceptance a well-formed `SUTRAMO1` whose
symbols lie in its code. **5 × 20,000: 63% refused, 37% accepted, 0 broke the contract.** It is a gate (3,000).

## What it is not

- **No type proof across the languages.** ELF has no argument types, so a sidecar that says `i64` for a C
  `double` cannot be detected. The declaration is the programmer's promise.
- **No structs by value, no variadic functions, no callbacks, no Windows.**
