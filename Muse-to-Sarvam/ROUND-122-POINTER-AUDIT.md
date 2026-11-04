# Muse Round 122 — Audit every function that returns a pointer

- **Base:** main at v297 (`c803cc07`, compiler `Sutram 1.0 (v297)`).
- **Deliverables:** this report, `r122.json`, `r122_ws1_pointers.md` (full 310-function
  audit), `r122_v298_fix.sm` and `r122_v298_fix2.sm` (v298 verification probes).
- **Audit only.** No code was changed, nothing was pushed or merged by this round.

## WS1 — Which of the 310 `prakriya` return a pointer, and does that pointer outlive the call?

Method: every `prakriya` body in `lib/*.smlib` (24 files) was read. `grep -c
"^prakriya "` per file sums to exactly **310**. For each function, every
`nivartanam` expression was traced to its source: a `nirmmita(...)` call, a
parameter, a parameter-indexed cell, a call to another lib function, or a scalar
computation. All 26 functions that call `nirmmita` were checked individually for
whether the `nirmmita` value itself is returned or is only scratch. No
classification below is guessed from a name.

### The strict pointer-returning list in `lib/`: 7 functions, all heap

| Function | File | Returns | Class |
|---|---:|---|---|
| `mala_nava(n)` | `mala.smlib` | Fresh qword array, `n` cells | (c) heap |
| `nighantu_srij(cap)` | `nighantu.smlib` | Fresh map handle (header + key area) | (c) heap |
| `nighantu_vardh(m, newcap)` | `nighantu.smlib` | Fresh map handle of `newcap`, contents copied | (c) heap |
| `suchi_srij(cap)` | `suchi.smlib` | Fresh list header (`len, cap, data`) | (c) heap |
| `avali_srij(cap)` | `suchi.smlib` | Fresh queue header (`len, cap, data, head`) | (c) heap |
| `rakh_srij(cap)` | `sangrah.smlib` | Fresh set handle (a map) | (c) heap, by delegation to `nighantu_srij` |
| `rakh_vardh(s, newcap)` | `sangrah.smlib` | Fresh set handle of `newcap`, contents copied | (c) heap, by delegation to `nighantu_vardh` |

**In the library: 0 caller-provided, 0 static, 0 own-stack-frame.** There is no
top-level static declaration in any lib file (verified: no top-level
`vitti`/`dasham`/`kosh` declaration outside a `prakriya`), and the only local
arrays in the library are in `ganita.brahmagupta_kshetr`, which returns only a
packed scalar, never a local.

Full accounting: **7 pointer-returning + 7 no-return in-place mutators + 296
scalar-returning = 310, nothing unaccounted for.** The other 21 `nirmmita` users
use it purely as scratch that is never returned and return a scalar instead —
so their scratch can leak (no free exists) but can never dangle in the caller's
hands (e.g. `roop.roop_ank`'s `rev` digit scratch, `sangrah.rakh_sangam`'s
`tmpa`/`tmpb` key-listing scratch, `suchi.suchi_vardh`'s `nd` growth buffer).

Borderline cases, handled explicitly so they do not inflate or hide the count:

- 11 element-content accessors (`mala_grah`, `suchi_grah`, `chay_apanay`/
  `avalok`, `avali_nishkas`/`avalok`, `nighantu_grah`/`grah_mool`,
  `phal_mulya`/`mulya_va`) return a cell's *contents* — a pointer only if the
  caller stored one. Counted separately, not as pointer-returning.
- `anukram`'s `p+8`/`p2+cnt` returns are integer cursors per the file header,
  not addresses — excluded with reason.
- `suchi_vardh`/`avali_pravesh` replace the data pointer inside the caller's
  header and return status 1; the old buffer leaks, never freed, so it is
  stale-but-readable, not a dangling return. Noted, not counted.
- The bulk of `roop`/`khand`/`varna`/`patra` helpers write into a caller `out`
  and return a length/count/status — not pointer returns.

**Dangerous list in `lib/`: NONE.** The most valuable audit left, applied to 310
functions, finds the library clean: every pointer a lib function returns is heap
(`nirmmita`), which lives for the program (there is no `munmap`/free anywhere,
so heap handles never become dangling by reclamation; they leak by design).

## WS2 — Do `anka_akshar` and `vartani_sandhi` return a pointer into their own frame? No — they do NOT share a cause

The two builtins are not in `lib/` at all: they are compiler builtins (BN 25
`char_from` / BN 18 `vartani_cat`, primary names from v292) implemented by code
generation in `src/sutram_compiler.asm`. They were judged against the emitted
bytes, not a source-level local — hence the distinction below, stated explicitly
rather than forced into a class.

### `vartani_sandhi` = (a) caller-provided, mutated in place. Not a lifetime defect.

`.ge_call_vartcat` scans `dst` to its NUL, copies `src` including the terminator
into it, and ends `mov rax, r8` (return `dst`). No allocation, no new string.
The defect is **mutation + aliasing**: the caller's buffer is changed, and the
returned pointer aliases it. It crashes if and only if `dst` is a read-only
literal (the PE `0xC0000005`), and silently corrupts on Linux. This corrects the
brief's premise, which said it "returns a pointer into its own stack frame":
it returns the **caller's** buffer. That is why the golden passes on Linux
(the mutation is the documented in-place behaviour for a mutable buffer) while
Windows crashes (the literal is read-only there).

### `anka_akshar` = (d\*) stack scratch below `rsp`. Dangerous, and not (b) static.

`.ge_call_charfr` emits: `sub rsp,16; mov [rsp],al; mov byte [rsp+1],0;
mov rax,rsp; add rsp,8` — so the returned pointer is `rsp−8` on return, in
just-freed space. Its "static 1-byte buffer in BSS" comment is stale: no
`char_buf` symbol is defined anywhere else in the compiler. The next `push`/
`call` writes exactly at `rsp−8` — which is why `vartani_sandhi`'s opening
`push` clobbers an `anka_akshar` result (the Round 120 symptom, now derived
from the bytes), while successive `anka_akshar` calls (each netting `rsp−8`)
do not overwrite each other. A reader trusting the comment instead of the
emitted bytes would misclassify it as static.

**They do not share a cause, and fixing one does not fix the other.** The two
separate fix directions are: give `anka_akshar` a real buffer (heap or static,
not stack scratch); and stop `vartani_sandhi` from writing into literals
(refuse literals, or allocate — the v298 choice was the former, see below).
The Windows symptom "gives `P` instead of `B`" is the dangling stack-scratch
byte being overwritten by whatever the next call pushed on PE (observed `P`
(80), versus Linux where the slot still held 66 (`B`)): the mechanism
(dangling scratch, overwritten) is proven; the exact overwriting value is
platform- and call-sequence-dependent, not a designed `P`.

### Verified on v298: both fixed, in different ways (matching the two causes)

Probes `r122_v298_fix.sm` / `r122_v298_fix2.sm`, run on v297 and on v298
(`33cab2dc`):

- v297, same probe: `anka_akshar(66)` prints `B`, then after
  `vartani_sandhi("x","y")` the same result prints garbage, then
  `vartani_sandhi(v,"cd")` prints `abcd` for both `v` and the result (mutation).
- v298: `vartani_sandhi` on a **literal** now refuses at compile time with
  `E_VARTANI_STHIRA` ("vartani_sandhi prathamam vartanim tasyah sthane eva
  vardhayati — sthira vartani ... tasyam likhitum na shakyate"), with the hint
  "`s + t` makes a new string; or `b = nirmmita(n), vartani_pratilip(b, s)`,
  then `vartani_sandhi(b, t)". On a **mutable** buffer it still mutates in
  place (`b = "abcd"`, `s = "abcd"`, same buffer, by design).
- v298: `anka_akshar(66)` prints `B`, and after a `vartani_sandhi` on a mutable
  buffer it still prints `B` (not clobbered); `anka_akshar(97)` prints `a`
  (matching Sarvam's v298 verification).

So "both fixed on v298" is shorthand for two different fixes, exactly as the
two causes predict: a stable buffer for `anka_akshar`, a literal refusal for
`vartani_sandhi` (in-place preserved for mutable buffers).

## WS3 — The cheapest test that would have caught this on Linux, without Windows

**A two-call clobber probe: call the function, then call another function, then
read the first result.** If the result changed, it is a dangling stack pointer.
No new platform, no new tooling — just a second call in a `.sm` program:

```sutram
vitti c1 = anka_akshar(66)
vitti t = vartani_sandhi("x", "y")   /* any call that pushes/calls */
shabda(c1)                            /* "B" if live, garbage if dangling */
```

That is what Round 120's `ws2_anka2.sm` did, and it caught `anka_akshar`'s
instability on Linux. The reason it is the cheapest test is that the project's
other tooling would **not** catch this class:

- The GUARD_PAGES build catches overruns past mapped pages. A freed stack frame
  is still mapped, so reading it does not fault — it just reads stale data.
  A guard page would not fire.
- A second allocator that poisons freed memory is a heap tool. A stack-frame
  return is not heap, so heap poisoning never touches it.
- A stack canary catches stack *smashing* (overwrites past the canary), not
  dangling *reads* of a freed frame.

The class is "a function that returns a pointer to storage it does not own,"
and the only tool that catches it without Windows is a test that dirties the
storage between the call and the read. That test belongs in the guard (as a
named probe, not as a new platform): every pointer-returning builtin and lib
function should be read, then clobbered by an unrelated call, then read again.

## NOT RUN

Windows execution (cannot run Windows — the Windows claims are from Round 118's
native-cases and Round 124's branch report, and the v298 fix was verified on
Linux v298, which shares the codegen for these two builtins), browser,
implementation (audit only — no fixes made here), native-speaker review, full
suite (no tree changes; the v297 suite numbers stand).

## Follow-ups (not fixed here)

- The clobber probe above should be added to the guard for every
  pointer-returning builtin and lib function (the 7 lib heap returns are safe
  by construction, but the guard should prove it, not assume it).
- The stale `char_buf` BSS comment in the compiler should be removed, so the
  next reader does not misclassify `anka_akshar` as static.
- The `suchi_vardh`/`avali_pravesh` old-buffer leak (stale-but-readable) is
  noted, not fixed — it is a leak, not a dangle, and fixing it needs an owner
  decision about who frees.
