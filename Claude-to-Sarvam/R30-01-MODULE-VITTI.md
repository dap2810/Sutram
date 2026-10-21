# R30-01 — A module-level `vitti` in an object, shared across modules

## What changed

**R28 and R29 refused a module-level `vitti` in an object.** That meant a module with state (a counter, a
configuration value) could not be compiled separately at all. **Now:**

1. **Each object holds the 8 bytes of every `vitti` declared in it,** after its code, which is exactly where the
   one-pass compile puts them.
2. **It exports each one as the symbol `vitti:<name>`.** The colon cannot appear in a Sutram name, so a `vitti`
   can never collide with a prakriya.
3. **In `--separate`, a `vitti` that a `yoj` brought in is not held in the importing object.** Every read and
   write of it is a relocation to `vitti:<name>`. **So the whole program has one copy,** in the object of the
   module that declares it.
4. **The root initializes every `vitti`,** including its modules', at the start of `mukhya` and in source order.
   That is what the one-pass compile does, and the root can do it because it sees every module's declarations.

## Why no new relocation kind was needed (R28 said one would be)

**In R28 I wrote that this would need "a second kind of hole". It does not.** A global is read with
`mov rax, [rip + disp32]` and written with `mov [rip + disp32], rax`. In both, the displacement is the **last
four bytes** of the instruction, so it is filled with `target − (offset + 4)`. That is exactly what a call's
`rel32` gets. **So `SUTRAMO1` and `sutram-link` are unchanged:** the linker does not know a `vitti` from a
prakriya, and it does not need to.

## What is still refused

**A library object compiled with plain `--object`** (no `mukhya`, and no root that `yoj`s it) **refuses a `vitti`
with an initializer:** no `mukhya` of its own would ever run the initializer, so the value would silently be zero.
A `vitti` with no initializer is accepted, since it starts at zero anyway. **With `--separate` or
`tools/sutram_build.py`, the root runs the initializer, so nothing is refused.**

## Where it is

- **`src/r28_object.inc`**: `r30_object_globals` replaces the global placement in object mode, and the writer
  emits the `vitti:` symbols.
- **`src/sutram_compiler.asm`**: two hooks. One notes where a top-level `vitti` starts (as R29 does for a
  prakriya); the other sends object mode to `r30_object_globals`. **Both are behind the object flags.**

## The proof: `tests/r30/test_vitti.py`, now a gate (Linux)

| What | Result |
|---|---|
| **Shared state.** `tests/r30/proj`: two modules both `yoj r30_ganak`, which holds `ganak` and `prarambha`. Built separately, it prints what the one-pass compile prints (`1 11 12 112 7`) | yes |
| `vitti:ganak` and `vitti:prarambha` are each defined in **exactly one** object, `r30_ganak`'s | yes |
| the root object holds only the root's own `vitti` (`mukhya`, `vitti:mula`) | yes |
| **The same bytes.** A program with a `vitti`, compiled with `--object` and linked alone, equals the direct compile | yes; in `tests/r28` too, whose identity count rises from 186 to **187** |
| **The refusal.** An initialized `vitti` in a library object is refused; without an initializer it is held | yes |
