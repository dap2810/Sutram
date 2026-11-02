# R108-00 — The correction arrived mid-build: the arena was finished and works, so it is on a review branch, not main. Main gets the outlives rule (no keeping `prakriya`), the `mala` refusal, and `parimana()` moving (v290).

- **Commit on `main`:** `__SHA__` (the v289 base was `3d8e6c4`). **Review branch:** `claude/r108-arena-review`, commit `0e71e54`.
- **Compiler: `Sutram 1.0 (v290) - sampurna sutra`** (was v289). Linux x86-64 cloud, 2 cores, 7 GB.
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Suite: `NO-EXPECTATION=4 PASS=287`, FAIL=0** (285 + goldens 318, 319; 316 is now a compile-time refusal golden).
- **Gates (`sh tools/gates.sh`, Xvfb display, Linux): 59 PASS / 1 FAIL / 1 NOT-RUN** (FAIL: `installer version`, v243
  against v290). **The first run was 58 / 2 / 1:** `guard pages` failed on my new golden 318, which reads the arena
  that the guard-page build does not have - the same thing 317 needed last round, and I should have added it with
  the golden. Skipped there; re-run passes.
- **The guard, origin/main (v289) → v290, 697 programs** (`evidence-r108/guard.txt`):
  - **Linux ELF: 557 byte-identical, 137 refused identically, 1 DIFFER, 2 new.**
  - **Linux PE: 557 byte-identical, 137 refused identically, 1 DIFFER, 2 new.**
  - **The Windows compiler under Wine: 557 byte-identical, 137 refused identically, 1 DIFFER (the same 316), 2 new; its 1115 outputs are byte-identical to the Linux compiler's PE outputs.**
  - **The one DIFFER is example 316, an error example**, as you predicted: v289 ran it and stopped at run time
    (R82); v290 refuses it when compiled. Nothing else moved - `286` and `299`, which make a `kosh` in a block and use
    it inside, are byte-identical.

## What happened with the correction

Your `ROUND-108-CORRECTION` arrived when the arena was already built and passing its suite. You wrote: *"If you had
already started the arena, stop and report what you have. A half-built arena on a flawed premise is worse than
none."* So: **it is not on main.** It is complete, though, and it does not rest on the flawed premise in the
way the correction fears, so here is exactly what it is, and the branch is there to read or delete.

**What the branch does** (`claude/r108-arena-review`, suite 288 / 0, its own README in
`Claude-to-Sarvam/evidence-r108-arena-branch/`):

- A `kosh` declared in a `mandapa` is a slot of the block's arena: counted by `parimita`, released at block exit.
  kb1 (100,000 blocks, each a 100-number `kosh`): **0 KB, 0.02 s**, against v289's 400 MB, 0.46-0.59 s.
- Growth takes a new slot and copies. **ChatGPT R177 is right that this is relocation**, and I do not call it
  anything else.
- **It closes the alias hole without a descriptor, by making a second name impossible:** `vitti a = k` for a block
  `kosh` is refused (`E_KOSH_MANDAPA`, "gets no second name"), and `kosh_push` on a `prakriya`'s parameter was
  already refused. So there is never a second name at the moment the data moves - the hole is not left open and
  patched later; it cannot be written. That is a narrower language than a descriptor gives (a block `kosh` has one
  name), and that is the trade-off to judge.
- It closes the lifetime hole with the outlives rule below.

**Why I did not merge it anyway:** your instruction was explicit, and the correction's third point - *"do not
reclaim storage while the call-through escape gap is still accepted"* - is a sequencing decision, not only a
technical one. Main now has the escape fix; the reclaim waits for your call (branch as is, or the descriptor).

## WS1 - option B, the outlives rule: built (main)

**A `kosh` made in a `mandapa` may be passed only to a `prakriya` parameter that does not keep it.** A parameter
keeps what it is given if any use of it is other than a read (`k[i]`), a `kosh` builtin's own operand
(`kosh_len(k)`, `kosh_push(k, ..)`), or an argument to another parameter that does not keep. The compiler computes
this for every `prakriya` and parameter of the program, as a greatest fixpoint (recursion is fine); a function
value or a foreign function counts as keeping. Otherwise:

```
Sutram Error [E_KOSH_MANDAPA]: mandape rachitah kosh tam prakriyam na gacchati ya tam rakshati (nivartayati, sthapayati, anyatra preshayati)
Sanket: prakriya kosh-tarkam k[i], kosh_len(k) iti eva pathatu; kosh mandapat bahih na jivati
```

| the block's `kosh` given to | v289 | v290 |
|---|---|---|
| `padh(kosh k, i) { nivartanam k[i] }` | allowed | **allowed** |
| a recursive `yog(kosh k, n)` that reads and recurses | allowed | **allowed** |
| `rakh(kosh k) { nivartanam k }` (example 316) | ran; stopped after the block (R82, run time) | **refused at compile time** |
| a `prakriya` that stores it in a module `vitti` | ran; stopped later | **refused** |
| a `prakriya` that passes it on to `rakh` | ran | **refused** (the fixpoint follows the chain) |

**With v289's escape error, no reference to a block's `kosh` can now outlive its block** - directly, through memory,
by return, or through a call. The R82 gate's five runtime cases are all compile-time refusals now (12 checks, 0
failed); the runtime check stays in the compiler as a second line that nothing in the tree reaches. **Cost: none
at run time** - it is decided at compile time, and no program that passes its `kosh` to a reading `prakriya`
changed by a byte.

**Option A (an arena epoch) not built,** as you and ChatGPT concluded: a stamp in the block does not help a raw
pointer that does not carry it, and the same block re-entered gives the same address a fresh, valid stamp.

**The stable descriptor: not built.** On main, a `kosh` still lives in its own region and never moves, so aliases
are already coherent and the descriptor is not needed there. It becomes needed only if `kosh`s move - that is,
with an arena. It is a change to every `kosh` access (a load through the descriptor), and I would rather you choose
between it and the branch's one-name rule before I spend the days on it.

## WS3 - `parimana()`: one number, both

**It reports the arena and the regions together**: the arena's persistent side, its scratch side (open blocks),
and every `kosh`'s header and capacity. One number for a program and a test. **Golden 318**, moving:

```
start 0
a kosh of 1 48
grown to capacity 4 72
a block's nirmmita(100) 184
and a kosh of 8 in it 288
after the block 176
```

(A `kosh` costs a 40-byte header in this program, because it makes a `kosh` in a block, plus 8 bytes a number;
`nirmmita(100)` is rounded to 112.) **After the block it is 176, not 72:** the block's `nirmmita` came back, the
`kosh` made in the block did not - its region is kept for the program's life on main. On the arena branch the same
program ends at 72.

## WS4 - the reference-type class: `kosh` closed since v288; `mala` closed now

- **`kosh == kosh`: closed.** v288's `E_KOSH_GANIT` refuses any bare `kosh` as an operand; tested again on v290
  (`a == b` on two `kosh`s holding 7: refused).
- **`mala == mala` was still open**: `vitti a[2]; vitti b[2]` with `7` in each, `likha(a == b)` printed **0**, and
  `a + 1` printed an address. **Now `E_MALA_GANIT`** (golden 319). `a[0] == b[0]` and a `mala` given another name
  (`vitti p = a`, then `p[0]`) are unchanged.
- ChatGPT R176's alternative - make `==` mean identity rather than refuse - is still open; refusal is the
  conservative choice until there is an identity rule worth teaching.

## Not done

- **The arena on main** - on the review branch, waiting for your decision (merge the one-name version, or build the
  descriptor first).
- **The stable `kosh` descriptor** - not needed while `kosh`s do not move; days of work if chosen.
- **The installer** (v243); **native-speaker review** of the new `E_KOSH_MANDAPA` and `E_MALA_GANIT` texts:
  NOT RUN; real Windows.
- **Not touched:** `backups/`, `Windows-to-Sarvam/`, the frozen packs' sources, `MEMORY-DECISION.md`, `Muse-to-Sarvam/`.
