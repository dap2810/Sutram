# R84-00 — The withdrawal is wrong: two names for one `kosh` DO diverge on v278. Your own program diverges on Windows. Do not reopen the recycling bins on that test.

- **Commit on `main`:** the one after `a41b5ba` (R83) — documentation and evidence only. **Compiler: `Sutram 1.0 (v278)`, unchanged**
  (binaries byte-identical to origin/main, so the guard is unchanged: R83-00's 0 DIFFER on Linux ELF and PE stands).
- Suite, proofs, gates: as R83-00 (255/0, 229/229, 86/86, gates 57 / 0 / 1). Linux x86-64 cloud.

## Your question, answered with output: yes — in five cases out of six

Everything below is in `evidence-r84/divergence.txt`: each program, then Linux ELF, PE under Wine, and the
guard-page build. `a[0] = 999` is written through the alias after the growth.

| program | Linux ELF | PE (Wine) | guard-page |
|---|---|---|---|
| **your program exactly** (`kosh k[1]`, push 111, `vitti a = k`, push 222 333 444, `a[0] = 999`) | `a[0]=999 k[0]=999` — together | **`a[0]=999 k[0]=111` — apart** | **apart** |
| the same, with **one `vitti p = nirmmita(8)`** before the pushes | **apart** | **apart** | **apart** |
| the same, with **one other `kosh j[1]`** declared before the pushes | **apart** | **apart** | **apart** |
| growth **inside a `mandapa`** (with a scratch `nirmmita` in it) | together | **apart** | **apart** |
| a `kosh` **passed as a parameter, grown by the callee** | refused when compiled (`kosh-tarke kosh_push asamarthitam`), as before | | |
| a `kosh` **stored in a `rachana` field, then grown** | **apart** | **apart** | **apart** |

**Why your test agreed: it hit the one case where they stay together.** A `kosh` grows **in place** only when its
buffer is the newest block in the arena (R65's extension, Linux only). Your program allocates nothing between
`vitti a = k` and the pushes, so on Linux `k` was the newest block and its cells never moved. Allocate anything
first — a `nirmmita`, another `kosh`, a library call that allocates — and growth copies the cells to a new buffer;
only the name pushed through follows. **PE output has no in-place extension at all, so there your exact program
diverges.**

**So the mechanism in the correction is not what happens.** A `kosh` variable holds the address of its cells, not a
handle: growth that moves the cells writes the new address into the variable pushed through and nowhere else.
"Growth updates the shared header" is true only for in-place growth, where the length and capacity at `[k-16]`
and `[k-8]` are shared because the cells did not move. (The same as R83-00 WS1, and R64's finding.)

## What this means

- **`vitti a = k` is a hazard, not a feature.** Its behaviour depends on what else the program allocated, and on
  the operating system: your own program prints different results on Linux and Windows.
- **Do not reopen the recycling bins on the strength of that test.** The old buffer is *not* dead: the second name
  still points at it and still reads and writes it (999 above). Today that is a stale read, because nothing is ever
  freed. With bins that recycle the old buffer, the same programs become use-after-free. The bins' premise —
  "after growth, nobody points at the old buffer" — is exactly what these programs refute.
- **What would have to be true for recycling:** no second `kosh` name can exist. R83's option 1 (refuse `vitti a =
  k`, `a = k`, `k2 = k`, `m[i] = k`) plus the existing type rule gets there for `kosh` names. The variant is
  measured in `evidence-r83/` and breaks exactly three fixtures (252, 255, 287). Raw addresses (`k + 0`, a `kosh`
  returned through a plain value) would still need the handle design before any recycling.

## What I did not do

- No compiler change. Option 1 stays unshipped, as R83 reported (your rule: it breaks 3 fixtures).
- The reference §16 note from R83 stays as written: it says exactly this, with a program checked on Linux and PE.
- **Not run:** real Windows. Wine runs the same PE bytes; the divergence there comes from the generated code
  (PE has no in-place extension), not from Wine.
