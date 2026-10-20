# F7 - indexing a scalar parameter SEGFAULTS (a new crash, distinct from F1)

**Found 2026-10-20 while writing a benchmark. Not F1 - this function has 4 locals.**

## The minimal reproduction

```sm
prakriya f(ok) {
    ok[0] = 5
    prati 1
}
mukhya() {
    vitti x = 0
    likha(f(x))
}
```

```
Siddh: ... sankalit        <- compiles, reports SUCCESS
exit 139                   <- SEGFAULT
```

**Verified on main (v218). `f` has ONE parameter and NO locals, so the F1 many-locals path is not involved.**

## What triggers it

**Indexing a parameter that is a scalar.** `ok[0] = 5` where `ok` holds an integer. The compiler accepts it
and emits an indexed store through a non-pointer value, and the program crashes.

**The same shape reaches a shipped library function.** `lib/ganita.smlib`'s
`ganita_janchit_yuj(a, b, ok)` indexes its third argument (`okp[0] = 0`). So a user who calls it with a scalar
third argument gets a segfault:

```sm
yoj ganita
mukhya() {
    vitti ok = 0                          # a scalar, not an array
    likha(ganita_janchit_yuj(1, 2, ok))
}
```
```
exit 139
```

**That is the worst version of this: a documented library function, called in the obvious wrong way, crashes
the program instead of saying so.**

## Why this matters more than it looks

**The compiler should reject `ok[0]` when `ok` is not an array.** It already rejects undeclared names
(`E_UNDEFINED_NAME`), unknown fields (`E_UNKNOWN_FIELD`) and undeclared arrays
(`E_UNDECLARED_ARRAY`) - **it has the machinery. It is not applied to indexing a scalar.**

**And the failure mode is a crash with no diagnostic**, which is the same class as F1: **the compiler reports
`Siddh: ... sankalit`, and then the program dies.** A user would not suspect the compiler.

## How it was found, which is the point

**I was writing a performance benchmark** and used the wrong argument type. **The compiler did not tell me -
it crashed.**

**This is exactly what ROUND-15's robustness fuzzer is for**, and it is now a concrete case to give it: **an
argument whose type does not match how the callee uses it.** The fuzzer should be told this shape, because a
generator of random valid programs would not produce it - **this is a VALID program whose type use is wrong,
and the language has no check for it.**

## Status

**Recorded, not fixed.** It is a compiler change and it is on the road to v1.0: **a language that segfaults on
a plausible mistake is not usable by a beginner.** Assigned to the fuzzer round's owner.

