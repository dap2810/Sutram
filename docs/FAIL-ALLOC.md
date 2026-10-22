# `--fail-alloc N`: making an allocation fail, for tests (R38)

```
sutram_compiler --fail-alloc N <in.sm> <out>
```

The ordinary compile, except that in the program it writes, the **Nth allocation returns 0**
without calling `mmap`. Every other allocation is made as usual. N counts from 1, in the order
the running program makes them, over every allocation that goes through the compiler's
allocation sequence: `nirmmita`, including every `nirmmita` inside a library, and the
compiler's own `kosh` storage.

No machine runs out of memory on demand, so before this switch an "allocation failed" branch
could only be read, never run. `tests/r38/test_fail_alloc.py` uses it to call every library
function that allocates, once for each allocation it makes, and checks the documented result.

## What it is not

* **Not a mode of the language.** Without the flag the compiler emits exactly the bytes it
  emitted before (566 programs, 0 differ: `Claude-to-Sarvam/evidence-r38/ordinary-path-linux.txt`).
* **Linux only.** A `.exe` output is refused, and the Windows compiler does not have the flag.
* **Not combined with another mode.** `--object`, `--separate`, `--ffi` or `--check` after it
  is a usage error; so are N = 0, a non-decimal N, N of 10^9 or more, and a missing argument.
  None of these writes an output file.

## How

The first allocation site the compiler emits also emits an 8-byte counter, initialised to N,
inside the code (a Sutram program's one segment is read-write-execute) behind a short jump.
Every allocation site then begins with

```
dec qword [rip -> counter]
jnz .allocate
xor eax, eax          ; the Nth allocation: 0
jmp .done
.allocate:  <the ordinary mmap sequence, unchanged>
.done:
```

so the counter reaches 0 at the Nth allocation only, and goes on below 0 after it.
Source: `src/r38_fail_alloc.inc`; the hook is the first two instructions of
`emit_nirmmita_from_rax` in `src/sutram_compiler.asm`.

## The library's failure values (R38)

| Module | Functions | When an allocation fails |
|---|---|---|
| `sangrah` | `rakh_samroop_diff`, `rakh_sangam`, `rakh_sampat`, `rakh_bhed`, `rakh_asti_upasamuh`, `rakh_sam`, `rakh_tak_mala` | `-1`; `out` unchanged |
| `nighantu` | `nighantu_mil` | `-1`; `dst` unchanged |
| `brihat` | `brihat_shesh`, `brihat_ghatmod` | `-1`; `res` unchanged |
| `aadhar` | `brihat_ank_tak` | `-1`; `out` unchanged |
| `shreni` | `mil_shreni` | `-1`; the array unchanged |
| `roop` | `roop_ank`, `roop_ank_aadhar`, `roop_varg_ank`, `roop_sthir_mool` (`roop_sthir`, `roop_sthir_chinhit`), `roop_chinhit`, `roop_sign_akshar` | `0`; `out` holds only the terminator |
| `vakyank` | `ank_tak_varna`, `ank_tak_aadhar_varna` | `0`; `out` holds only the terminator |
| `suchi`, `nighantu`, `mala` | `suchi_srij`, `suchi_khip`, `avali_srij`, `avali_pravesh`, `nighantu_srij`, `nighantu_vardh`, `mala_nava` | `0` (unchanged since R9/R35/R36) |

A count can never be negative, so `-1` cannot be mistaken for a result. A formatter's `0` with a
valid base cannot be a result either: every number has at least one digit.

**Still open:** the compiler's own `kosh` storage crashes when its allocation fails
(`Claude-to-Sarvam/evidence-r38/kosh-under-fault.txt`). Fixing it adds a check to every kosh
allocation, which changes the ordinary compile's bytes, so it waits for a decision.
