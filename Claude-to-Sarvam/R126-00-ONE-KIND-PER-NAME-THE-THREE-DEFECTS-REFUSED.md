# R126-00 — v301: a name keeps one kind for its whole `prakriya`. The three defects share one cause and one fix; all three are refused at compile time, with a golden each. The tracking is sound for every way a `kosh` can move in the language except two, named below. No emitted byte changed and compiling is not measurably slower. WS3: yes - `vitti a = k` now knows enough to emit a descriptor access; that makes the descriptor one decision at about 17 emit sites, not a redesign.

- **Commit on `main`:** `8d064f5` (one commit; rebased onto Muse R127 `df55c9d`, which landed while I built - see R126-01).
- **Compiler: `Sutram 1.0 (v301) - sampurna sutra`** (was v300). Linux x86-64 cloud; PE run under Wine 64.
- **`crash corpus: 227 cases + manifest, 0 failed`.** **Suite: `suite: NO-EXPECTATION=4  PASS=318  (322 run)`**, FAIL=0 (315 + the three new goldens).
- **Gates (`sh tools/gates.sh`, Xvfb display, Linux): 66 PASS / 1 FAIL / 1 NOT-RUN** (FAIL: `installer version`, payload v243, as before; NOT-RUN: Windows execution) - 68 gates now, with **`R126 kinds` (55 checks with PE: 42 compile-time and ELF, 13 PE runs under Wine; 0 failed)**.
- **The guard, main v300 (`0fd2530`) → v301, 728 programs** (`evidence-r126/guard.txt`):
  - **Linux ELF: 579 byte-identical, 143 refused identically, 3 DIFFER, 3 new.** **Linux PE: the same numbers.**
  - **The 3 DIFFER are the three examples whose source I changed** (below). Compiled from today's source, v300 and v301 give the same bytes for all three, ELF and PE. **The 3 new are the three goldens**, which v300 compiles and v301 refuses.
  - **So every program v300 compiles, v301 compiles to the same bytes.** The 143 refusals give the same message on both, word for word (`refusal_messages.py`: 0 differ).
  - **The Windows compiler under Wine: the same 579 / 143 / 3 / 3, and its 1,164 outputs are byte-identical to the Linux compiler's PE outputs.**

## WS1 - the three defects: one cause, one fix

| golden | the defect (R125) | v300 | v301 |
|---|---|---|---|
| `examples/348_r126_kosh_then_raw` | `vitti a = k`, then `a = nirmmita(64)`, then `a[0]` | **SIGSEGV** (exit 139): reads a `kosh` length at `[a-16]` | `E_VITTI_PRAKAR: 'a' kosh asti; sankhya ... tasyam na sthapyate` |
| `examples/349_r126_kosh_in_one_branch` | `vitti a = p` (raw), `yadi (x == 1) { a = k }`, `a[0]` | input 0: **SIGSEGV**; input 1: 41 | `E_VITTI_PRAKAR: 'a' sankhya ... asti; kosh tasyam na sthapyate` |
| `examples/350_r126_mala_then_kosh` | `vitti a = m` (a `mala`), `a = k` (length 1, capacity 8), `a[5]` | **prints 0, exit 0** - checked against the capacity at `[a-8]`: **a silent read past the length** | `E_VITTI_PRAKAR: 'a' mala asti; kosh tasyam na sthapyate` |

- **They share one cause:** v300's mark was *first kind wins, never cleared, set from a bare name only*. Each defect is a name that is compiled as one kind and holds another.
- **So one fix closes all three:** **a name keeps the kind its first binding gave it.** Every later declaration or assignment of it must give the same kind. All three are now refused before any code is written, and **no output file is left behind** (the gate checks).
- **The fix refuses; it does not make the unsafe programs run.** That is R201's recommendation too (*"fixes the three reported failures by refusing invalid mixes, not by making their unsafe operations run"*).

## WS2 - the tracking made sound: all three flaws, and what each cost

**The rule.** Inside a `prakriya` every name has one of five kinds:

- `vibhag`, `kosh dasham`, `kosh`, `mala`;
- or a **number / raw address** - a number, a `nirmmita` buffer, an untyped parameter, a `chakra` counter.

The first binding fixes it. Anything else is `E_VITTI_PRAKAR`.

**Flaw 1 - "set only from a bare variable": fixed.**

| form | v300 | v301 |
|---|---|---|
| `vitti a = (k)` | already marked: the parser drops the brackets (measured) | the same |
| `vitti k2 = k`, `vitti a = k2` | already marked: each link marks the next | the same |
| **`vitti a = f(k)`, `f` returns a `kosh`** | **unmarked: `a[5]` read past the length** | **marked, and `a[5]` is bounds-checked** |
| `k + 0`, `k - 0`, `k * 1` | **unmarked**: folded to `k` *after* the kind was decided | `E_KOSH_GANIT`, as `k + 8` already was |
| `m[0] = k` (a cell), `b.x = k` (a field), a module `vitti` | **unmarked**, raw access | `E_KOSH_DVARA` |
| a `kosh` to an untyped parameter, or through a function value | **raw** inside the callee | `E_KOSH_DVARA` |
| `likha(k)`, `pad8(k)`, `likh8(p, k)`, `kosh_kship(j, k)` (a `kosh` inside a `kosh`) | **raw** | `E_KOSH_DVARA` |
| `vitti a = x ? k : j` | **unmarked** | `E_KOSH_DVARA` |
| `nivartanam siddhi(k)` (a phal result) - then `q[5]` in `yadi dosh (q = f(k))` | **printed 0**: unchecked (I found this one while building) | `E_KOSH_DVARA` |

- **Which `prakriya` return a `kosh`:** worked out once per `prakriya`, from its AST. **Every `nivartanam` must return a `kosh` parameter, or a `kosh` the `prakriya` declares, by its own name - or a call to a `prakriya` that does.**
  - Then its callers' names are marked `kosh` and checked.
  - If some `nivartanam` return a `kosh` and some do not, it is refused (`E_KOSH_DVARA`).
  - A recursive `prakriya` works (`f(k, n)` returning `k` or `f(k, n - 1)`). So does R109's 33-link chain, which still gives its `E_KOSH_MANDAPA` refusal.
- **The kosh-builtin rule:** a `kosh` is the first argument of a `kosh_*` builtin (and of `pankti_len`) and nothing else.

**Flaw 2 - "never cleared": made irrelevant, deliberately not "fixed" by clearing.**

- **Clearing the mark on reassignment would trade one bug for another.** The compiler generates in source order. So a mark cleared inside a `yadi` would be wrong after the `yadi` on the path that did not run it - t3 again, mirrored. R201 rejects it for the same reason.
- **Instead, a kind can never change.** A mark that cannot become wrong never needs clearing.

**Flaw 3 - "blind to control flow": made irrelevant.**

- **The kind is the same at every program point of a `prakriya`.** No assignment anywhere in it may change the kind, so a per-function table *is* a per-program-point table. Nothing in it can disagree with a path.
- **What it costs: programs that would be safe on every path they actually take.** Example: a name that is a raw buffer in one block and a `kosh` in a sibling block. **Write two names.**
- **What a flow-sensitive version would need, and why I did not build it:** a dataflow join at every `yadi`, loop and block end, and a per-point table read by every index site. That is weeks, not days. **In this tree it would admit nothing more:** apart from the three examples below, no program here changes a name's kind.

**What it broke in the tree: three examples, zero tests.**

- `examples/252`, `253`, `255` (R38 / R42's alias tests) wrote `vitti w = 0` and then `w = v`: a number that then holds a `kosh` or a slice - **the shape of t3.**
- **I rewrote each to declare `w` from a collection of `v`'s kind** (`kosh dasham u[1]` / `vitti w = u` / `w = v`; for the slice, `vitti t = a[0:1]`), with a comment. **They still test the assignment path, and their goldens are unchanged.**
- Nothing else in the 728 programs changed: 579 identical, 143 refusals identical.

**Not covered, said plainly:**

1. **A foreign function** (`--ffi`, a `ptr` parameter) receives a `kosh` as its raw address. **That is R33's contract, kept.** It is the borrow / FFI policy R199 and R201 put inside the descriptor work. `tests/r33` / `tests/r35` pass a `kosh` this way.
2. **A `prakriya` compiled in another object** (`--object` / `--separate`) is assumed to return a number. A caller there that gets a `kosh` back holds it raw: **unchecked, not misread.** In the `prakriya`'s own compile its `nivartanam` are checked as above.
3. **`mala` doors are unchanged:** a `mala` to an untyped parameter is still raw memory. A `mala` never moves, and the tree uses that form (`examples/` pass a `mala` to `prakriya f(a)`). **Only kind changes are refused for `mala`.**

**Already true, found while testing:** `vitti a` with no value is refused (`E_MULYA_VINA`). So R201's definite-initialisation concern does not arise here: every name has a value from its declaration.

**What it cost:**

- **Emit sites changed: 0.** No generated byte changed (the guard). Everything is a compile-time check.
- **Check sites added: 9.**
  - the declaration;
  - the assignment;
  - the `chakra` variable;
  - `nivartanam`;
  - builtin calls;
  - raw memory writes;
  - the untyped-parameter path of `gen_typed_call_arg`;
  - R58's identity fold;
  - each function's entry.
- **Source: about 880 lines of NASM**, one routine set (`r126_*` in `src/sutram_compiler.asm`).
- **Compile speed: no measurable change** (`evidence-r126/compile-time.txt`):
  - **715 programs:** 1.26 s on v300 vs 1.24 s on v301 (best of three, quiet machine); 1.19 vs 1.30 s with the gates running alongside. Process start-up dominates.
  - **A 58 KB program with 11 `prakriya` of 240 statements and 100 names each:** 20 compiles take 473-478 ms on v300 and 446-493 ms on v301.
  - **The checks are linear scans of the per-function name tables**, the same scans `is_kosh_var` already does at every index.

**Number: the round's work, about a day.** That is inside R125's 3-5 days because the refusal form needed no flow analysis, and no example needed more than a declaration changed.

## WS3 - does `vitti a = k` now know enough to emit a descriptor access? **Yes.**

- **After v301 the compiler's `kosh` mark is exact in both directions:**
  - **a name marked `kosh` holds a `kosh` on every path** (no binding of another kind exists in its `prakriya`);
  - **a `kosh` at run time is reachable only through such a name, a `kosh` parameter, or a `kosh` builtin's argument.** The exceptions are an FFI `ptr` and another object's return (above).
- **That is the precondition the descriptor needed.** In R125 I wrote that on v300 a descriptor build would read a "descriptor" out of a raw buffer in t2 / t3. **That can no longer happen:** `is_kosh_var(a)` is true only where `a` holds a `kosh`.
- **So the descriptor is one decision, made at the sites that already make it.** Every `kosh` access already dispatches on `is_kosh_var` and its siblings. **R124's count stands: about 17 emit sites in about 13 routines.**
- **It is not literally one emit path.** Each of those sites changes from `[p-16]` / `[p]` to `[d+8]` / `[[d]]`. Making and growing a `kosh` changes too.

**What is still missing, and none of it is tracking:**

1. **The FFI / raw boundary:** a `ptr` argument must pass the buffer, not the descriptor, under a rule that the callee does not keep it across a growth (R199 / R201's borrow rule).
2. **Growth that can fail:** allocate and copy first, publish the new buffer in the descriptor last (R201).
3. **Old buffers:** given back at the block's end or the program's end (R124: at most about twice the final size).
4. **Separate objects:** a `kosh` passed between objects is then a descriptor address - the object format's ABI changes, and old objects must not link (`SUTRAMO3`, or a refusal).

## WS4 - the order, with a number for each

**Agreed with R201: tracking, then the descriptor, then the reservation goes.** Removing the reservation first would make every raw alias stale at every doubling instead of only at the cliff.

| step | what | number |
|---|---|---|
| **1. Tracking** | **done: v301**, this round | about 1 day |
| **2. The descriptor** | the about 17 emit sites; making and growing; the FFI buffer rule; failure-safe growth; its gate and the two-platform guard, run while the 64 MiB regions still exist | **about 1-1.5 weeks** (R201: 3-7 days of emitter work plus 2-5 of review) |
| **3. The reservation goes** | growth by copying in the arena (doubling), `R101A_REGION` and its `mmap` removed; tests that really move a buffer; peak memory and the lazy commit re-measured on Windows; the reference rewritten | **about 3-4 days** |
| **total** | | **about 2-2.5 weeks** |

**The cliff today, measured on v301** (`evidence-r126/alias-cliff.txt`; a one-element `kosh`, a second name, N pushes):

- **up to 4,194,304 pushes the two names agree;**
- **at 4,194,305 they part.** The doubling from 4,194,304 asks for 8,388,608, more than the region's 8,388,603.
- **ChatGPT R201 explains exactly this.** The "about 15 `kosh`" figure is the 1 GiB address-limit case R122 measured, not a limit on an ordinary machine.
- **Your brief calls the 64 MiB "the only memory defect left".** After v301 it is the only one I know of in the tracked language. The FFI / raw-pointer rule is the other obligation, and it belongs to step 2.

## Not done, and why

- **The descriptor and the removal of the reservation:** ordered and priced, not built. Your round asked for the tracking first.
- **Flow-sensitive kinds:** not built, on purpose (WS2).
- **Native Windows:** NOT RUN. Wine is the proxy; the owner's machine runs the Windows gates.
- **Not touched:** `backups/`, `Windows-to-Sarvam/`, the frozen packs (the new messages are default-pack strings, untranslated as R121's were), `MEMORY-DECISION.md`, `Muse-to-Sarvam/`.
