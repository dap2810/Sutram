# R25-02 — WS2: the error type, built — `siddhi`, `dosh`, `prasar`

**Compiler v236.** Environment: **Linux**, plus **Wine** where stated. **No restructuring was needed.**
The error type is one new include, `src/r25_phal.inc`, plus hooks marked `R25` in `src/sutram_compiler.asm`.

## What it is

```
prakriya bhaj(a, b) {
    yadi (b == 0) {
        prati dosh(1)            # failure, carrying the code 1
    }
    prati siddhi(a / b)          # success, carrying the value
}
prakriya ek_adhik(a, b) {
    vitti q = prasar bhaj(a, b)  # failure: returned from here at once; success: q = the value
    prati siddhi(q + 1)
}
mukhya() {
    likha(prasar ek_adhik(10, 2))    # 6
    likha(prasar ek_adhik(10, 0))    # the failure reaches mukhya: exit status 1
}
```

**How it works:**

- **No heap and no new output format.** The value, or the error code, is in `rax`, as every call already
  returns. The status is in `rdx`: 0 for `siddhi`, 1 for `dosh`.
- **`prasar f(...)`** is the call, followed by `test rdx, rdx` and a jump. On failure it runs the function's
  own return sequence, so `rax` and `rdx` go up unchanged.
- **In `mukhya`, a failure ends the program** with the code as the exit status, the low 8 bits as usual.

**The rules, each a compile error when broken.** Together they mean a status is never read from a
register nobody set:

| Rule | Message (default; all eleven packs) |
|---|---|
| a prakriya with `prati siddhi`/`prati dosh` is a **phal-prakriya**; **every** `prati` in it is one of the two | `phal-prakriya: prati siddhi va dosh bhavet` |
| a phal-prakriya is called **only under `prasar`**, including inside another call's arguments | `phal-prakriya prasar vina ahuta` |
| `prasar` is used **only on a call of a phal-prakriya** | `prasar: phal-prakriya-ahvanam apekshitam` |
| `prasar` appears **only in a phal-prakriya or `mukhya`** | `prasar kevalam phal-prakriya-madhye mukhya-madhye va` |

**Also:**

- Falling off the end of a phal-prakriya is `siddhi(0)`.
- `prati dosh(c)` in `mukhya` exits with `c`.
- Methods can be phal-prakriyas: `prasar p.ghata(4)`.
- Recursion works.
- **The three are keywords in all eleven packs:** Devanagari `सिद्धि दोष प्रसार`, Tamil `வெற்றி பிழை
  பரப்பு`, and so on. I tested a Hindi program written entirely in its own keywords.

## Against the suite and the fuzzer

| Check | Environment | Result |
|---|---|---|
| **suite** | Linux | **PASS=217**: 216 + `249_r25_phal`. No existing golden changed |
| `tests/r25/test_phal.py` (new; a gate) | Linux | **14 / 14**: every rule above, three-level propagation, recursion, a method, the exit statuses |
| **`fuzz_r23.py --seed 25 --count 1000`** | Linux | see R25-00 (first lines) |
| `fuzz_r23 --robust 5000` · `fuzz_valid` 500 · `fuzz_valid --capabilities` 500 · `fuzz_robust` 5000 | Linux | see R25-00 |
| the four capability examples | **Wine** (not Windows) | output and exit status match the goldens (249 exits 3) |

**The fuzzer covers the error type.** `tools/fuzz_r23.py` now writes 2–4 phal-prakriyas per program:

- each fails with its own `dosh(code)` on a condition of its argument;
- or calls an earlier one under `prasar`, passing an expression of `x`;
- or returns `siddhi` of an expression;
- `mukhya` then calls them under `prasar` until one fails. Its model computes the whole chain, including
  which code reaches `mukhya`, and checks the exit status.

On seed 25, **246 of 300 programs end in a failure** that propagated, and 54 run to the end. Both paths
are exercised. The robust mode adds `prasar`, `siddhi(` and `dosh(` to the tokens it inserts.

**`fuzz_valid.py` (the main generator) does not write phal-prakriyas.** Its model could carry them, but
its programs print every local at the end, and an early exit would cut that short. The new feature's
coverage is `fuzz_r23`, which is a gate.

## What I did not do, and why

- **A handler that catches a failure and goes on.** Today a failure goes up, or ends the program. The
  syntax for "catch it here" is the one decision left (R24-03). Once it is chosen it is a small addition.
- **Keeping a result in a variable.** A result is consumed by `prasar` where it arrives, because a variable
  is one qword and a result is two.
- **`phal<T>`, a typed result:** it waits on the type decision (R25-03).
- **A phal-prakriya called through a function value is not checked.** The status is ignored there, and
  `prasar` on an indirect call is refused.
- **No `dasham` value in a result.**
