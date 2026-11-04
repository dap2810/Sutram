# R129-00 — A `kosh` parameter now grows and the caller sees it (v304). The old refusal was opaque, and the descriptor makes propagation possible, so I built it; the one new hazard - a slice of the same `kosh` - is refused. ChatGPT R204, which landed after v304, found two slice defects in v303 by reading: S1 was already closed by v304's rule (it crashed v303 - reproduced); S2 is fixed in v305. The release notes carry R204's corrections. The release candidate is v305. The reading-versus-testing fact is written down.

## The release candidate

```
gates: 68 PASS / 0 FAIL / 1 NOT-RUN   (sh tools/gates.sh, Linux, Xvfb; NOT-RUN = Windows execution)
suite: NO-EXPECTATION=4  PASS=327  (331 run)
Sutram 1.0 (v305) - sampurna sutra
```

- **Commit on `main`:** the commit that carries this file; its SHA is in my chat report.
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Installer:** `PASS payload v305 = compiler v305`, `Sutram-Setup.sha256` = `99d26a89f355a2b20bdf7fe1fbd94aa8e304c3eae3a9b54c8364ecf8f1e6e6f5`, `--self-test` exit 0 under Wine.
- **The guard, v304 (`773bb77`) → v305, 737 programs:**
  - **Linux ELF and PE alike: 500 byte-identical, 153 refused identically, 84 DIFFER.** The 84 are the programs that run `kosh_kship`: each growth now checks its capacity limit.
  - **Run old and new: all 84 the same output and exit, on ELF and under Wine.** **The Windows compiler (v305) under Wine: = the Linux PE output for all 737 (584 compiled, 153 refused by both), 0 differ.**
- **The guard for v304's step, v303 (`8154fde`) → v304, 737 programs:**
  - **Linux ELF: 583 byte-identical, 153 refused identically, 1 DIFFER.** **Linux PE: the same.**
  - The 1 is `examples/121`, which pinned the refusal: refused before, now it compiles, prints `1` and exits 0 (ELF and Wine). Its source also changed (comment).
  - **Every other program compiles to v303's bytes, on both platforms.** **The Windows compiler (v304) under Wine compiled all 737: byte-identical to the Linux PE in 584, both refuse 153, 0 differ.**
- **Codegen shapes 12/12.**
- **How the gate line was reached, said:**
  - **the first full run on v305 gave 66 / 2 / 1:**
    - `R126 kinds` failed one PE run under Wine. The program printed the right `4`, `2`, then Wine reported an unhandled page fault at exit.
    - `doc counts` failed because of it.
  - That PE is byte-identical to v304's (it has no `kosh`). 40 runs of it on each version under Wine: all clean. `R126 kinds` alone: 55 / 55.
  - **A Wine load flake, as in earlier rounds; the second full run, above, is clean.** Both runs are in the evidence.

## WS1 - the gap

**1. What the refusal said: `Sutram truti: kosh-tarke kosh_push asamarthitam`** (*"kosh_push is not supported on a kosh parameter"*).

- **It was honest about what, opaque about why,** and it named the builtin by its old name: the student writes `kosh_kship`. Muse R129 noted the name too.
- The reason was in a source comment only. It dated from T18: *"Parameters are pointer-by-value views. A grow operation could replace the callee's pointer without updating the caller."*

**2. Is propagation possible now? Yes, and it is built.**

- From v302 a parameter holds the descriptor, as an alias does.
- **Nothing in the growth path needed to change.** I removed the refusal and checked the paths it touches:

| | v303 | v304 |
|---|---|---|
| `jod(kk, i)` pushing 10 times through a parameter | refused | `kosh_gan(kk)` **10**, and an alias of `kk` sees element 9 |
| a parameter pushed 9,000,000 times - past a region move, the old region given back | refused | **all 9,000,000 seen** by the caller, ELF and PE |
| a `kosh dasham` parameter | refused | grows |
| a block's `kosh` grown by a `prakriya`, in 100 blocks | refused | **5000**: right, no escape. A growth's memory is on the persistent side, as all `kosh` storage is |
| `examples/121` (*"reject it until Sutram deliberately gains a reference/descriptor ABI"*) | the refusal | prints `1` - **its own comment said this day would come** |

**What it newly makes possible, and how I closed it.**

- A **slice** holds the elements' address as they were when it was made. Until v303 nothing could grow a `kosh` while a slice of it was alive: a callee could not grow a parameter, and v302 refused keeping a slice in a name. Now a callee can.
- So these are **refused, `E_KOSH_VIBHAG`**, naming the `prakriya`:
  - **a slice of a `kosh` given to a `prakriya` that may grow a `kosh`.** "May grow" means it, or a `prakriya` it calls, runs `kosh_kship`, worked out for the whole program to a fixpoint, so recursion is sound. Example: `f(kk, kk[0:1])` where `f` grows `k`;
  - **a slice of a `kosh` given beside an argument that has a call in it.** The call could run first and grow the `kosh`, as in `f(kk[0:1], kosh_kship(kk, 6))`. This hazard existed already in v303 and is now closed too.
- **A slice to a `prakriya` that only reads is unchanged.** `examples/248` gives the same golden.
- **No program in the tree is refused by either rule:** the guard's 153 refusals are v303's, and the same text.

**Gate `R127 descriptor` +5 checks: 21 on ELF, 31 with PE.** v303 fails all five: three because it refuses the growth, one because it gives the wrong error, and one - the slice beside a call - because it compiles it.

## Then: ChatGPT R204 (landed after v304 was pushed) - reproduced, and the round's last change

R204 reviews v303 by reading, NOT RUN. Its verdict is **"NO to general v1.0"** on v303, for two slice findings. I ran its programs on v303 and on v304:

| R204 | its program | v303 | v304 | v305 |
|---|---|---|---|---|
| **S1** a slice beside an argument that grows the same `kosh` | `pratham(k[0:1], kosh_kship(k, 9))`, `k` at 8,388,608 | **SIGSEGV** (exit 139): the slice kept the given-back region | refused, `E_KOSH_VIBHAG` | refused |
| S1, a whole `kosh` to a `vibhag`, growth through an alias, as a statement call | `pratham(k, kosh_kship(a, 9))` | ran (statement calls evaluate right to left) | refused | refused |
| **S2** `k[lo:]` where `lo` grows the `kosh` | `pratham(k[kosh_kship(k, 8) - 1:])` | refused (`mala ank seema atikram`: the old end, 1) | the same | **`8`**: the end is the length after `lo` |
| S2 where `lo` shrinks or clears | `k[kosh_hri(k) - 3:]`, `k[kosh_shodh(k):]` | refused | refused | `2`, `0` |

- **S1 was already closed by v304's rule**, which I had built for parameter growth. It refuses a slice beside any argument with a call, in either call form. R204 asks for exactly that narrow fix: *"refusing unsupported kosh-slice/call combinations is acceptable if the refusal is enforced and documented."* It is both.
- **S2, fixed in v305:** an omitted `hi` is read from the descriptor after `lo`. An explicit `hi` is evaluated once, as written. That is R204's own *"consistent extension"*, and it is in the reference.
- **R204's F2 qualification:** the declared-capacity limit is now also checked on every growth, with the same message. It is unreachable (2^40 pushes first need 8 TiB), so it is a stated invariant, checked.
- **Its release-note corrections, all applied:**
  - what a `mandapa` gives back (scratch `nirmmita`; not a block's `kosh`, not helper allocations), and `mandapa parimita`'s scope;
  - what `parimana()` counts and excludes;
  - finite limits (the 64 MiB per *small* `kosh` is gone; a large one still reserves a region; capacities above 2^40 are refused);
  - what the out-of-memory message covers;
  - the slice rules in place of "pass it on directly";
  - what the allocator keeps - including a large declared `kosh`'s first elements;
  - the v298 history (Windows exposed it; R121 proved both on Linux);
  - mixed-version objects as unsupported.
- **Gate `R127 descriptor` +5 (S1 ×2, S2 ×3): 37 checks with PE, 0 failed.** v304 fails the three S2 checks.
- **R204's verdict, my reading:** its blockers on v303 were S1 and S2. Both are closed on v305, each a gate check. **It does not pre-approve v305, and I do not claim it would.** The installer's execution-policy limitation and native Windows remain the owner's, as before.
- **Muse R130** (also landed) attacked v303 and found no crash; its parameter-growth note is WS1 above.

## One open observation, not resolved - for the native Windows run

**A rare Wine fault at process exit.**

- About 1 run in 200, Wine reports *"Unhandled page fault on read access to 0000000000000008 at address 00006FFFFB642600"*. It comes **after all the program's output, with exit code 0**, at the same address in Wine's code each time.
- **It caused the first full gate run's one failure.** The re-run of `R127 descriptor` for the evidence hit it once too (`pop, peek, dequeue, clear`, PE); that gate passed in both full gate runs.
- **Measured with nothing else running** (`evidence-r129/wine-exit-fault.txt`), a program with no `kosh`, 200 runs each:

| version | runs with the fault |
|---|---|
| v305 | 0 |
| v301 | 1 |
| v300 | 0 |
| v299 (before the R124 exception handler) | 0 |

- **A `kosh` pop / peek program, 60 runs each: v305 1, v300 0.**
- **Too rare to say when it began, or whether it is Wine's or ours.** It is on programs with no `kosh`, so it is not the descriptor.
- **The release notes list it as an open observation for the native Windows run.** I did not start an investigation this round, as you asked.

## WS2 - and then stop

**Done, and nothing new started.**

- The reference has a section, *A `kosh` parameter can grow (v304)*.
- Also updated: the release notes, the changelog, the memory model's status box and `PROJECT-MASTER`.
- The installer was rebuilt with v304 before the final gate run, so the gate line above is one run.

## WS3 - for the record

**`docs/reports/HOW-DEFECTS-WERE-FOUND.md`:**

- **the table of who found what between v297 and v303, and what each method missed:**
  - a second platform (the two Windows builtins Linux hid);
  - testing while reading (R125's three);
  - an independent attack (Muse's eight, the global door);
  - reading alone (R203's three, which the 15-check gate, Muse R129 and the owner's four checks had all passed);
- **what each method is good at;**
- **what the project does because of it:**
  - every reading finding is reproduced before it is fixed;
  - every fix becomes a gate check that fails on the old compiler;
  - no round declares "no known defect".
- It is linked from the release notes and the status box, where a future reader starts.

**One correction to the brief's first lines:**

- *"Memory has no known defect"* - I would not write that, and the release notes do not.
- What I can say: **the defects found so far are fixed, and each is a check that fails on the version that had it.** R204 then proved the point during this round: it found two more by reading v303's fix.
- The limitations that remain are listed: retained arena buffers, the FFI borrow, and the slice rules above.

## Not done, and why

- **Native Windows** (install, uninstall, the IDE, the Windows gates): the owner's. NOT RUN here.
- **Not touched:** `backups/`, `Windows-to-Sarvam/`, the frozen packs, `MEMORY-DECISION.md`, `Muse-to-Sarvam/`.
