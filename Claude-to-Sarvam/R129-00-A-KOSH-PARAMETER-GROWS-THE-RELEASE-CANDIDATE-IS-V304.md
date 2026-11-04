# R129-00 — A `kosh` parameter now grows and the caller sees it (v304). The old refusal was opaque, and the descriptor makes propagation possible, so I built it. The one new hazard - a slice of the same `kosh` - is refused. Release candidate below. The reading-versus-testing fact is written down.

## The release candidate

```
gates: 68 PASS / 0 FAIL / 1 NOT-RUN   (sh tools/gates.sh, Linux, Xvfb; NOT-RUN = Windows execution)
suite: NO-EXPECTATION=4  PASS=327  (331 run)
Sutram 1.0 (v304) - sampurna sutra
```

- **Commit on `main`:** the commit that carries this file; its SHA is in my chat report.
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Installer:** `PASS payload v304 = compiler v304`, `Sutram-Setup.sha256` = `b6e165abd017c02323affad2a4425f09c869117af5dae96f35085591cdf83aec`, `--self-test` exit 0 under Wine.
- **The guard, v303 (`8154fde`) → v304, 737 programs:**
  - **Linux ELF: 583 byte-identical, 153 refused identically, 1 DIFFER.** **Linux PE: the same.**
  - The 1 is `examples/121`, which pinned the refusal: refused before, now it compiles, prints `1` and exits 0 (ELF and Wine). Its source also changed (comment).
  - **Every other program compiles to v303's bytes, on both platforms.** **The Windows compiler (v304) under Wine compiled all 737: byte-identical to the Linux PE in 584, both refuse 153, 0 differ.**
- **Codegen shapes 12/12.**

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
- What I can say: **the defects found so far are fixed, and each is a check that fails on the version that had it.**
- The limitations that remain are listed: retained arena buffers, the FFI borrow, and the slice rules above.

## Not done, and why

- **Native Windows** (install, uninstall, the IDE, the Windows gates): the owner's. NOT RUN here.
- **Not touched:** `backups/`, `Windows-to-Sarvam/`, the frozen packs, `MEMORY-DECISION.md`, `Muse-to-Sarvam/`.
