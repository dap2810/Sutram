# R125-00 — The compiler does know, in the simple case: `vitti a = k` marks `a` a `kosh`, and `a[0]` is checked as one. But that knowledge is a name-keyed flag set only from a bare variable, never cleared and blind to control flow. So the claim is half right, and it found three defects that exist today (two segfaults, one silent read past a `kosh`'s length). Making it sound is days, not weeks. Answer to 4: no - the 1 GiB was the arena, not the reservation; v300 already fixed it.

- **Commit on `main`:** `7e3b7fb` (documentation and evidence only; no code changed).
- **Compiler: `Sutram 1.0 (v300)`.** Your brief says base v299; **main is v300** (R124's lazy commit). Linux ELF.
- **Suite, gates, guard:** not re-run - nothing changed. R124's are current.

## WS1 - what it emits today, from the source

**`vitti a = k`, then `a[0]`: the compiler knows `a` is a `kosh`, and emits the `kosh` access.**

- **The source:** `r38_mark_alias`, called from the declaration path and the assignment path. When the right-hand side is a bare variable (`AST_VAR`) that is a `kosh`, it adds the target's name to `kosh_vars`, the per-function table of `kosh` names.
- **What `a[0]` then emits:** `gen_expr`'s index path asks `is_kosh_var(a)`, gets yes, and emits the `kosh` bounds check - the length from `[ptr-16]` - before the load.
- **Measured** (`evidence-r125/ws1-what-the-compiler-knows.txt`, `t1_alias`):
  - `a[0]` prints 41;
  - `a[3]` on a one-element `kosh` is refused (`mala ank seema atikram`);
  - and `kosh_gan(a)` / `kosh_kship(a, 7)` compile (R124-01) - a builtin that refuses anything not known to be a `kosh` accepts `a`.

**So for `vitti a = k` the claim is wrong.** But look at what kind of knowledge it is:

| property of the mark | consequence |
|---|---|
| set **only when the right-hand side is a bare name** | `m[0] = k; a = m[0]`, `a = k + 0`, a `kosh` passed to an untyped parameter: **not marked**, raw access, no bounds check |
| **keyed by name, per function** | fine across functions (the table is reset at each `prakriya`) |
| **never cleared, and the first kind wins** (*"already marked in any kind? then leave it alone"*) | a reassignment does not change what the compiler thinks |
| **blind to control flow** | a mark made inside a `yadi` holds on every path after it |

**Three defects follow, today, on v300** (`evidence-r125/programs/`):

| program | what it does | v300 |
|---|---|---|
| `t2_sticky` | `vitti a = k`, then `a = nirmmita(64)`, then `a[0]` | **SIGSEGV** - `a[0]` reads a `kosh` length at `[a-16]`, below the arena |
| `t3_branch` | `vitti a = p` (a `nirmmita` buffer), `yadi (x == 1) { a = k }`, then `a[0]` | input 1: 41 (right). **Input 0: SIGSEGV** - `a` still holds `p`, but is compiled as a `kosh` |
| `t4_mala_then_kosh` | `vitti a = m` (a `mala`), then `a = k` (a one-element `kosh` of capacity 8), then `a[5]` | **prints 0, exit 0**. It is checked against the `mala` header, `[ptr-8]` - the `kosh`'s *capacity* (8), not its length (1). **A silent read past the `kosh`'s length** |
| `t5_return` | `vitti a = k + 0`, then `a[5]` | prints 0 - unmarked, unchecked |
| `t6_mala_cell` | `m[0] = k`, `a = m[0]`, then `a[5]` | prints 0 - unmarked, unchecked |

- **t2, t3 and t4 are wrong answers or crashes in today's language**, independent of any memory redesign. I found no earlier report of them in the tree.
- **t5 and t6 are the unchecked doors** R124-01 named.

**So did the last three rounds solve the wrong problem? Partly.**

- **The descriptor is the right mechanism.** It is right for every access the compiler *correctly* identifies as a `kosh`.
- **But on today's tracking it would be unsafe.** In t2 and t3 a descriptor build would read a "descriptor" out of a raw `nirmmita` buffer and write through it.
- **Tracking must be made sound first.** Then the descriptor.

## WS2 - making it know: days, not weeks

**There is already a symbol table to carry it:** `kosh_vars`, `array_vars`, `r23_slice_vars` and `float_kosh_vars`, per function. Each `prakriya` resets them, and every index and builtin path already consults them. **What is missing is soundness, not storage.**

**The smallest sound rule - a variable's kind is fixed by its first assignment, for the whole function:**

| site | change |
|---|---|
| declaration and assignment with a bare name (the two `r38_mark_alias` calls) | refuse when the target already has a *different* kind (t4), or has held a raw value (t2, t3) |
| every other assignment to a marked name (`a = nirmmita(...)`, `a = 7`, `a = f()`) | refuse (t2) |
| a `kosh` / `mala` value stored in a cell (`m[i] = k`) | refuse (t6). It is already refused inside a `mandapa` (`E_KOSH_MANDAPA`); outside one it is allowed today |
| a `kosh` in arithmetic (`k + n`) | refuse (t5) |
| a `kosh` passed to an untyped parameter (`gen_typed_call_arg`, which already knows the callee's parameter kinds) | refuse, or pass only to a `kosh` parameter |
| a `kosh` returned from a `prakriya` (`vitti a = f(k)`) | mark from R108's analysis (it already knows which `prakriya` return their parameter), or refuse |

**About six sites.** Flow-insensitive is fine: refusing a kind change anywhere in the function needs no flow analysis, and it is what R73 already does for scratch addresses (*"a name that has held a scratch address keeps that mark"*).

**What it breaks in the tree - a static scan** (`evidence-r125/ws3-doors-census.txt`, `doors.py`; it finds all three doors in three probe programs):

- **of the 712 programs, 44 make a `kosh`;**
- **0 store it in a cell, do arithmetic on it, or pass it to an untyped parameter.**

The kind-change refusals can only be counted by building them. My expectation is a handful of tests, not examples.

**Number: 3-5 days with its gate, the guard and the reference.**

## WS3 - the four decisions

**4, first: if the reservation goes, does the 1 GiB Windows commit disappear on its own? No.**

- **The 1 GiB was never the reservation. It is the arena** (`R65_ARENA`), which every `nirmmita` and `mandapa` uses. The 64 MiB was each `kosh` region (`R101A_REGION`).
- **Removing the regions would make the arena *more* central:** every `kosh` buffer would then live in it.
- **v300 already fixed the commit:** the Windows runtime reserves and commits on first touch. One `nirmmita(64)` went from 1,073.7 MB to 0.0 MB; 100 koshes from 6,713 to 8.7 (R124). **It is done, and the descriptor needs it.**

**1. A descriptor for `mala`: it costs the same as for a `kosh`, and buys nothing.**

- **The cost:**
  - an access today is load, check `[ptr-8]`, load;
  - with the indirection, one more dependent load;
  - that is about free in a loop (R124: 0.64 vs 0.67 ns) and about 2.2 ns in a dependent chain (Muse R125).
- **But a `mala` never moves** - its size is fixed when it is made - **so a `mala` has no alias cliff.** Every name for it always sees the same buffer.
- **What `mala` does have is the tracking defect** (t4: a name marked `mala` that later holds a `kosh`). **WS2 fixes that, not a descriptor.**
- **I would not add it.** Uniformity is a reason, but here it is 24 bytes and an indirection to solve a problem `mala` does not have.

**2. `nirmmita` restricted to its region: the compiler already knows which block a `nirmmita` was made in.**

- **R72 and R73 do this today** (`E_SCRATCH_ESCAPE`): a scratch address marks every name that holds it until its block ends, and refuses it leaving by an outer variable, by memory or by `nivartanam`.
- **The one hole is documented:** an address passed to a `prakriya` that *keeps* it (stores or returns it).
- **R108 already computes "this `prakriya` keeps its parameter" for `kosh` parameters.** Applying it to scratch addresses closes the hole: **1-2 days.**
- **Bounds stay unchecked for raw `nirmmita`, as you say - documented.**

**3. Remove the 64 MiB - what breaks if the buffer can move:**

- **In the emitter:** the about 17 emit sites R124 counted, which must go through the descriptor. **That is the work, not a break.**
- **In the tree's programs: nothing through the doors** - the census above: 0 programs.
- **What would break is everything WS1 found:**
  - t2 and t3 would read a descriptor out of a raw buffer;
  - t5 and t6 would hold an address that dangles at every doubling, not only past 8,388,603 numbers.
- **So the order is WS2 first** (3-5 days), **then the descriptor** (ChatGPT R199's 2-5 weeks includes it).

## Not done, and why

- **Nothing built:** your rounds asked for answers. **t2, t3 and t4 are live defects in v300.** A refusal for them is WS2's work, and is the first thing I would build if you say so.
- **The kind-change census:** only countable by building the refusals.
- **Not touched:** `backups/`, `Windows-to-Sarvam/`, the packs, `MEMORY-DECISION.md`, `Muse-to-Sarvam/`.
