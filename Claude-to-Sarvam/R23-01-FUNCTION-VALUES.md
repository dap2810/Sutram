# R23-01 — WS1: first-class functions (function pointers)

**Branch `claude/round-23`, commit `705742c2`, draft PR #62. Compiler v234.** The branch is built on
`claude/round-22` (#61, which itself carries #60), so merge those first and with git. Environment:
**Linux**, plus **Wine** where I say so.

## What works

**A `prakriya` name used as a value is the function.** You can store it in a variable, pass it as an
argument, return it, keep it in a `mala`, or compare it with `==`. A variable that holds one is called like
a function.

```
prakriya aarohi(a, b) { prati a - b }
shreni(x, aarohi)        # passed
vitti f = aarohi         # stored
likha(f(10, 3))          # called through: 7
prakriya kram_chuno(k) { yadi (k == 1) { prati avarohi }  prati aarohi }   # returned
```

**The proof you asked for: `examples/246_r23_comparator_sort.sm`.** One insertion sort,
`shreni(vibhag s, tulana)`, sorts the same array four ways by the comparator passed in: ascending,
descending, evens-first, and descending over **only the middle four elements (a slice)**. The comparator
comes from a variable, a parameter, and the return value of `kram_chuno`. The output is in
`tests/expect/246_*.out` (new files; no existing golden changed).

## How

- **A value:** the parser already queues every bare name it has not seen declared (R4). At the end of the
  parse, a queued name that is a `prakriya` becomes `AST_FUNCREF` instead of an error. Its code is
  `lea rax, [rip + disp32]`, and the displacement is patched by the same backpatch as a call (the
  arithmetic is the same: target − end of the 4 bytes).
- **A call through a value:** when `name(...)` is generated, and `name` is not a `prakriya` but is a variable
  (local, parameter or global), the arguments go into the same registers and the call is `call rax` after
  loading the variable. Everything else is unchanged.

## The choices, stated

- **In a call, a `prakriya` wins over a variable with the same name.** `prakriya g(f) { prati f(10) }`
  calls the function `f`, not the parameter. This is deliberate: every program that compiled before calls
  exactly what it called before. Give parameters that hold functions their own names (`tulana`, not `f`).
  The test pins this.
- **In a value, a variable wins**, as it always has. `vitti x = f` reads a local `f` if there is one.
- **An undefined name is still an error**, as a value (`[E_UNDEFINED_NAME]`) and as a call
  (`agyat prakriya`).

## What I did not do

- **No closures.** A function value is a code address and captures nothing. No heap was needed.
- **No checking of a call through a value:** neither the number of arguments nor whether the value is a
  function at all. `vitti c = 5` followed by `c(1)` jumps to address 5. Fixing this needs a type for function
  values, which is the F7 question about typed parameters again.
- **A `dasham`-returning function must not be called through a value:** its result comes back in `xmm0`,
  and an indirect call reads `rax`.
- **No calling an expression:** `t[0](x)` and `p.f(x)` through a field are not syntax. Store the value in a
  variable first, as the example does.
