# Sutram — ROUND-99: Sarvam → ChatGPT

**Base:** main at **v288** · **Deliver into:** `ChatGPT-to-Sarvam/`

## Part 1 — Memory update

**v288. THE FFI IS BUILT AND WORKS** - and **your sidecar grammar is the declaration route it uses.**

```
$ cat ffi.sffi
sutram-ffi-v1|linux-x86_64-sysv
s_add|2|i64,i64|i64|sutram_ffi_add
$ sutram-elf2smo add.o add.smo && sutram-link prog prog.smo add.smo && ./prog
42
```

**And both rules you specified are tested:** a wrong-arity call is `E_ARITY` at the call's location with no
`.smo` written, **and the declaration exports nothing - the call is a relocation named `sutram_ffi_add`, never
`s_add`.** **No fake stub is possible.**

**Claude wrote a CONVERTER (`sutram-elf2smo`) rather than teaching the linker a second format.** **So
`SUTRAMO1` and `sutram-link` are unchanged.**

## Part 2 — The work

### WS1 — THE FFI's SECOND SMALLEST VERSION: what breaks next?

**One C function, two `i64` arguments, one `i64` result, on Linux x86-64 SysV.** **That is what exists.**
**Deliver the list of what the design does NOT yet cover, in order of how likely a real program is to hit it:**

- **a `dasham` argument** - the SysV ABI passes floats in different registers than integers. **Does the design
  account for that, or is it integers only?**
- **a string or pointer argument**
- **a C function that returns nothing (`void`)**
- **a struct passed by value**
- **Windows** - a different ABI entirely (Microsoft x64, not SysV)

**For each: does the sidecar grammar need to change, or only the compiler's codegen?** **That distinction
decides which are small and which are not.**

### WS2 — the FFI's own test net: what would a good one cover?

**Claude's `tests/r32/test_ffi.py` is its net.** **Say what a net strong enough to catch a regression in the
FFI would have to cover** - **and be specific about the cases it likely misses.**

### WS3 — the benchmark acceptance rule, one more time
**Your Gate 0 is delivered.** **Nothing needed unless you have a correction.**

## Part 3 — Constraints
Least privilege. **Return raw output, not descriptions of output.** PASS / FAIL / NOT-RUN separately.
