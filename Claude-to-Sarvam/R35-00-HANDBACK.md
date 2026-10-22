# R35-00 — Hand-back to Sarvam: the first lines

- **Code pushed to `main`: `46540309`.** The delivery documents are in the commit directly on top of it. Pushed
  with git: not file by file, and not `--force`.
- **Compiler on main: `Sutram 1.0 (v244) - sampurna sutra`, unchanged.** The fix is in the standard library.
- **`crash corpus: 227 cases + manifest, 0 failed`** (Linux).
- **Suite: PASS=218, FAIL=0, NO-EXPECTATION=4** (Linux). **One golden changed, and why is the whole of WS1:**
  `tests/stdlib/r18_srij_overflow_guard.out`. The test's inputs were wrong, so it was corrected, not rewritten to
  pass (below).
- **The fuzzer:** `fuzz_r23` 1000 programs, 35,862 values, 0 differ · `fuzz_valid --capabilities` 500 / 500 ·
  `fuzz_robust` 5000, 0 crash, 0 hang. **The fuzzers do not reach huge capacities;** the guard's net is the two
  stdlib tests below.
- **`tools/gates.sh`: 32 PASS / 0 FAIL / 1 NOT-RUN (Windows).** Library proofs **221 / 221 under a 4 GB address
  limit and unlimited**.

## WS1: the r18 defect. Both were wrong: the guard, and the test. The test was mine

**What the guard is.** `suchi_srij`, `avali_srij`, `mala_nava` and `nighantu_srij` allocate a capacity's worth of
bytes. **A capacity whose byte size wraps must give 0 rather than a handle.** If it does not, the program gets a
small buffer that claims to be huge, and writes past it.

**The guard was wrong.** It was `yadi (sz < 0) { prati 0 }`, which assumes that a wrapped size is negative.
**It is not always negative:**

| Call | The byte size after the wrap | Before | Now |
|---|---|---|---|
| `suchi_srij(2^61 + 1)` | `c * 8` = **8** | a handle; **SIGSEGV** on the second push | 0 |
| `avali_srij(2^61 + 1)`, `mala_nava(2^61 + 1)` | **8** | a handle | 0 |
| `nighantu_srij(988218432520154552)` | `16 + 56c` = **80** | **SIGSEGV** while clearing itself. Its own comment describes this crash as fixed | 0 |
| `suchi_srij(2^60)` | negative | 0 (the old guard caught this kind) | 0 |

**The fix bounds the count itself, before multiplying:** `c > (2^63 − 1) / 8` (suchi, avali, mala) and
`c > (2^63 − 17) / 56` (nighantu) give 0. The old `sz < 0` stays.

**The test was wrong too, and I wrote it, in R18.** It used `3037000499`, and R18-02 said its byte size wraps.
**It does not:** `3037000499 × 8` is 24,296,003,992, which is **24 GB, far inside int64.** (3037000499 is √(2⁶³), a
square-overflow edge from another witness; I carried it to a place where it means nothing.) So the guard never
fired. **The test was really asking whether the machine refuses a 24 GB allocation.** It passed where the
allocation failed (your sandbox, mine, a 4 GB limit). It failed where it succeeded (WSL with 48 GB): the
"address-shaped" values were simply the two successful handles.

**So, to your question, "whether the guard is wrong or the test is":** both. The test could never have caught the
guard's real hole, because its inputs did not wrap.

**ChatGPT's R101, written at the same time and without seeing this, reached the same diagnosis:** *"invalid
portable expectation plus positive-wrap guard hole"* (`ChatGPT-to-Sarvam/ROUND-101-WS1-*`). That is two
independent readings, which is better evidence than one.

**The test now, in `tests/stdlib/r18_srij_overflow_guard.sm`:**
- 2⁶¹ + 1, which wraps positive: the hole;
- 2⁶⁰, which wraps negative;
- the largest count that does not wrap, 2⁶⁰ − 1. That is 9.2e18 bytes, more than any x86-64 address space, so
  every machine refuses it;
- `MAX`;
- a small count, which must still give a handle.

**`tests/stdlib/r35_alloc_wrap_guard.sm`** (new) does the same for `mala_nava` and `nighantu_srij`, including
the first count over nighantu's bound.

**Which environment it must pass in: every one, and it now does.** No value depends on how much memory the
machine will grant. **Checked:**

| Check | Result |
|---|---|
| the new tests on the **old** library | **fail**: handles for 2⁶¹ + 1, and nighantu SIGSEGVs. The check can fail |
| the new tests on the new library | pass |
| library proofs under a 4 GB address limit and unlimited | **221 / 221** both |
| both tests under **Wine** | match their goldens |

## WS2: what fits next, in one sentence

**The next thing is the `likha` printing of a large `dasham` (R33's finding). It is a silent wrong answer, the
worst class this project has: `likha(1870271503745.0)` prints `1870271503744.999936`. But it changes what
existing programs print, so it needs the owner's word first, like the `yoj` scanner fix waiting on
`claude/round-30-yoj-scan`.**

What does not fit now:
- **The type on variables:** still the owner's.
- **Namespaced `yoj` in separate builds:** needs a versioned symbol format first (ChatGPT, R96).
- **A NASM build driver:** the Python one works and is opt-in.
- **More `nirmmita` sites without an allocation-failure check** (`aadhar`, `brihat`, `shreni`, `sangrah`): these
  are a different and smaller class. Their counts describe memory the caller already has, so the size cannot wrap
  for a real array, but a failed allocation is not checked. That is a library round for Muse, and I list it rather
  than take it.

## WS3: the guard

- **The compiler did not change:** v244 compiles every program to the bytes v244 did.
- **The library did, on purpose.** With the same compiler, main's library against this one, over 564 programs:
  - **432 byte-identical and 92 refused identically;**
  - **39 differ: exactly the 39 programs that reach `suchi`, `mala` or `nighantu`.** Each carries the new check,
    and none of the others differs. All 39 still pass their goldens and proofs;
  - 1 is new (the R35 test).

  Evidence: `evidence-r35/library-change-guard.txt`.
- **Your 476** is the Windows session's count on its program set. In my counting the compiler-path number is the
  same as R34's: 0 differ.

## All checks

| Check | Environment | Result |
|---|---|---|
| `tools/gates.sh` | Linux | 32 PASS / 0 FAIL / 1 NOT-RUN |
| library proofs, 4 GB limit · unlimited | Linux | 221 / 221 · 221 / 221 |
| the new tests on the old library (check the check) | Linux | fail, as they must |
| the library change, 564 programs | Linux | 432 identical, 92 refused identically, 39 differ = exactly the module users |
| suite · corpus | Linux | PASS=218 · 227 + manifest, 0 failed |
| fuzzers (3) | Linux | 0 differ · 500/500 · 0 crash |
| `tests/r66 r67 r68 r72 ci windows_accept r65_finish gui r83 sandesh r70` · `r69 --check-only` | Linux | all OK · SOURCE_PINS_CHECKED |
| both guard tests | **Wine** | match |
| Windows | — | **NOT-RUN** |

## What I did NOT do, and why

- **The installer was not rebuilt.** It carries `lib/`, so it is now stale twice: v243 inside, and the old
  library. It should be rebuilt on the owner's PC (as R34-02 did). The cloud toolchain gives other bytes than the
  accepted one.
- **`docs/sutram-stdlib.html`** is regenerated by the gate and still not committed by me (it is yours).
- **The other `nirmmita` sites:** listed above, not changed.
