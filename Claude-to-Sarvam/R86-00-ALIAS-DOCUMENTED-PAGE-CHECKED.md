# R86-00 — The alias is documented with a pinned example; Muse's assumptions page has three wrong claims, and checking it turned up two real defects

- **Commit on `main`:** this round's one commit — documentation, one golden, evidence.
- **Compiler: `Sutram 1.0 (v278)` — unchanged** (byte-identical to origin/main's). Linux x86-64 cloud, 2 cores, 7 GB.
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Suite: `NO-EXPECTATION=4 PASS=256`, FAIL=0** (one new golden, 288). Library proofs **229/229**. Property
  proofs **86/86**.
- **Gates (`sh tools/gates.sh`, Xvfb display, Linux): 57 PASS / 0 FAIL / 1 NOT-RUN (Windows execution); guard pages 5/5, suite 256/0.**
- **The guard, origin/main → this tree: Linux ELF and Linux PE — 666 programs, 538 byte-identical, 127 refused
  identically, 0 DIFFER, 1 new (288).** **NOT RUN: the Windows compiler under Wine** — its `.exe` is byte-identical to origin/main's.

## WS1 — the reference now says it, with a program and its output

`docs/LANGUAGE-REFERENCE.md`, §16, **"Two names for one `kosh`: `vitti a = k` is not a copy"** — replacing
R83's note. It says, in this order:

- `vitti a = k` makes **a second name for the same `kosh`, not a copy**;
- if `k` grows and **cannot extend in place** — something was allocated in between, or always on Windows — `k`
  moves and `a` still points at the old buffer, with the old length;
- **reading through `a` then gives the old data; writing through `a` does not affect `k`**;
- a program that does not alias is unaffected, and nothing in the standard examples relies on a second name
  after a move (the three that alias — 252, 255, 287 — never grow it afterwards);
- the rule: one name per `kosh`; copy values out.

**The worked example is the program you asked for, with one more line that writes through `a`**, and its actual
output:

```
a[0]=41 k[0]=99
a[0]=7 k[0]=99
```

The output is identical on Linux, on PE under Wine, and in the guard-page build. The section also gives the
no-obstacle case as run: on Linux the names stay one (`99 99`, then `7 7`), and on Windows it prints the above
either way.

## WS3 — the golden that keeps it honest

**`examples/288_r86_kosh_alias_moves.sm`** — exactly that program; golden `a[0]=41 k[0]=99` / `a[0]=7 k[0]=99`.
**If the alias is ever fixed, it fails — and its comment says the reference must change with it.** It passes the
format mutator (9 checks) and runs the same in the guard-page build and on PE.

## WS2 — Muse's assumptions page, every line run on v278

I checked `Muse-to-Sarvam/R83-THE-ASSUMPTIONS-PAGE.md` (the current version; Muse's R84 rewrite was not on
`main` when I looked). Every claim was run on Linux and on PE, 25 programs (`evidence-r86/ws2-assumptions-page-checked.txt`).
**Twelve of the fifteen items are right as written. Three are wrong, one STATED/NOT STATED label is wrong, and
one "already stated" claim is true only in part:**

| item | the page says | v278 does |
|---|---|---|
| **4 (the "sharpening")** | `a[1]` faults *even when nothing relocates* if `k` had length 1 at alias time | **Wrong on Linux.** With in-place growth the two names share the header: `kosh_len(a)` is 2 and `a[1]` reads 42. It faults only when `k` moves — on PE, always. |
| **7** | `1.0 / 0.0` is +inf (right); **`0.0 / 0.0` is 0, not NaN** | **Wrong — it is NaN.** It only *looks* like 0 because **every `dasham` comparison with NaN is wrong** (below). |
| **11** | an uninitialized `vitti` reads 0, "even on a second call, after another call wrote 99" | **Wrong.** `prakriya f(n) { vitti x; yadi (n == 1) { x = 99 }; nivartanam x }`: `f(0), f(1), f(0)` prints **`0 99 99`**. In a loop, `vitti x` with no value reads the *previous iteration's* value (`0 50 51`). And it depends on the system: with another call in between, Linux gave 99 and PE 0. Do not rely on it — the page's advice "do not fear garbage" is the opposite of the truth. |
| 12 | NOT STATED | **Stated**: §6 already says "A `mukhya()` written without braces runs to the end of the file". |
| "already stated": string `+` concatenates | `"a" + "b"` is `"ab"` | **Only for two written strings** (joined when compiled). **On variables, `s + t` adds the two addresses** (prints 8388922), and `shabda` of the result **crashes (SIGSEGV)**. |

Everything else checks: `tak` inclusive (and stated in §6a); `nirmmita` bytes vs `p[i]` cells (`p[8]` on
`nirmmita(64)` refused); `-7 / 2` is −3 and `-7 % 2` is −1 (not stated anywhere — the page is right); string `==`
compares addresses (even two identical literals, 0); `s[0]` is a qword, `akshar(s, 0)` 104; `x = (y = 5)` refused;
`prakriya f(vitti n)` refused; `kosh_push` on a `kosh` parameter refused; trailing statements after a braced
`mukhya` refused, after an indented one run; `k[-1]` stops with `mala ank seema atikram` (exit 1); `likha(k)`
prints an address; two equal `kosh` compare unequal; redeclaring refused (`E_DUPLICATE_NAME`, Sanket "'x'
purvam eva ghoshitam").

## Muse's finished page (`0ceb300`, pushed while I worked) repeats two of the three — before it goes into the reference

`Muse-to-Sarvam/R84-REFERENCE-SECTION-ASSUMPTIONS.md` is the version meant for the reference. **It still says
"`0.0 / 0.0` is 0, not NaN" and "Locals are genuinely zeroed — even on a second call … `likha(x)` prints 0,
every call".** Its verification passed both, and the reasons are instructive:

- **"`0.0/0.0 == 0` true"** — that is the NaN defect below: NaN compares *equal to every number*, so `== 0` is
  true. `0.0/0.0 == 5.0` is true as well.
- **"uninitialized `vitti` 0/99/0 across two calls"** — true for that program's shape. In mine the same
  function called `f(0), f(1), f(0)` prints **`0 99 99`**, and a `vitti x` in a loop reads the previous turn's
  value (`evidence-r86/ws2-assumptions-page-checked.txt`, `d1`–`d3`). A claim of "every call" needs every shape.

**Those two entries should not go into the reference as written.** The item-4 sharpening is not in the new page.

## Two defects found while checking — reported, not fixed

**1. `dasham` comparisons are wrong for NaN.** With `n = 0.0 / 0.0`, Linux and PE alike:

| | `n == 5.0` | `n == 1000.0` | `n <= -7.0` | `n < 3.0` | `n >= 3.0` | `n > 3.0` | `n != 5.0` |
|---|---|---|---|---|---|---|---|
| v278 | **1** | **1** | **1** | **1** | 0 | 0 | **0** |
| IEEE (Python) | 0 | 0 | 0 | 0 | 0 | 0 | 1 |

NaN compares *equal* to every number and *below* every number, and `yadi (n == 42.0)` takes the branch. The
comparison ignores the "unordered" result: `ucomisd` sets the parity flag for NaN, and `==`, `<`, `<=` and `!=`
don't test it. It is a fix in the compiler's float comparisons, and it would change the bytes of every program
that compares `dasham` values, so it is your call.

**2. String `+` on variables adds addresses** — above. The reference's string section should say that `+`
joins only written strings; a library function joins variables.

**And for the page:** item 11 is the one that matters most. A student who believes it writes `vitti x` and
reads a leftover value. **I'd make it "an uninitialized `vitti` holds whatever was there — always give it a value",
and I'd consider refusing `vitti x` with no value in a later round.**

## What I did not do

- **No compiler change** — neither defect is fixed (both change bytes; your decision).
- **I did not edit Muse's page** — I reported against it, as asked. Its STATED/NOT STATED labels are right for
  items 1–11 and 13–15; 12's is not.
- **Not touched:** `backups/`, `Windows-to-Sarvam/`, the frozen packs, `MEMORY-DECISION.md`. **Not run:** real
  Windows; the Windows-compiler guard path (identical binary).
