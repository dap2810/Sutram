# R78-00 — The safe/unsafe boundary, answered; the two mutants killed; the byte fix shipped

- **Commits, compiler, numbers:** as `R77-00-BYTES-CELLS-SILENT-DROPS.md` — **v275**, crash corpus 227/0,
  suite 244, library proofs 228/228, properties 86/86, guard pages 5/5, gates 55/0/1 (Linux, Xvfb), guard v273 →
  v275 on all three paths 491 / 120 / 35 DIFFER (all 35 same output and exit code).

## Your `## Verified behaviour` block, re-run on v274

All of it holds on v274 (refused: `outer = buf + 64`, `m[0] = buf`, `nivartanam buf`, `box[0] = nirmmita(64)`;
allowed: `outer = buf[0]`, a scratch pointer as a parameter returning a value; `E_NIRMMITA_RNA` literal and
computed) — **except the last line: "`nirmmita(10)` followed by `p[0..9]` compiles and runs" is no longer true.**
v274 stops that loop at `p[1]` (R77-00 WS1).

## WS1 — the byte-versus-qword fix: shipped in v274

See R77-00 WS1. Your golden — `nirmmita(10)` then `p[9]` refused with an error saying `nirmmita` counts bytes and
`p[i]` counts 8-byte units — is **`examples/273_r77_bytes_not_cells`**:
`p[9] nirmmita(10) bahih` / `Sanket: nirmmita bhaita-sankhyam ganayati, p[i] ashta-bhaita-ekakaih: p[9] hetu nirmmita(80) avashyakam`.

## WS2 — `suchi_srij` and `avali_srij`: every surviving mutant, listed

**36 surviving mutant variants** (16 + 18 at R76's count; an id can name two variants on one line, so I counted
variants). For each I asked: does any input make it differ, and does a test notice? (`evidence-r78/ws2-survivors-all-36.txt`)

| function | the mutant (the changed line) | differs on | severity | now |
|---|---|---|---|---|
| both | `yadi (c < 1) { c = 2 }` — cap 0 or below clamped to **2**, not 1 | `suchi_srij(0)`, `avali_srij(0)`: capacity 2 | different, not wrong (the list still works) — breaks the documented clamp | **killed** by the new `tests/stdlib/r78_suchi_avali_srij` |
| both | `yadi (l == 0) { nivartanam 1 }` (`q` for avali) — **1, not 0, when the allocation fails** | only when an allocation fails | **wrong**: the caller would take 1 as a handle | **already killed — by `tests/r38/test_fail_alloc.py`**, which the mutant scorer never runs (it uses goldens and properties only). Shown: `want 0, got 1` at allocation 1 (`evidence-r78/ws2-fail-alloc-kills.txt`) |
| both | `c <= 1`, `sz <= 0`, `c >= MAX`, `c > MAX + 1`, `sz < 1` | — | equivalent: c ≥ 1 and sz ≥ 8 by then; MAX and MAX+1 both end in 0 | — |
| both | `vitti l = 1` / `d = 1` / `sz = 1` | — | equivalent: overwritten before use | — |
| both | `yadi (c < 2) { c = 1 }` | — | equivalent: it differs from `c < 1` only at c = 1, where both leave c = 1 | — |
| both | `sz = c * 9` | — | equivalent in output (allocates more) | — |
| both | `nivartanam 1` after `sz < 0`; `l == 1` | — | equivalent: unreachable / never true | — |
| both | `l[1] = 0` (was `l[0] = 0`); deleting `l[0] = 0` / `q[1] = 0` | — | equivalent: the next line sets cell 1; the block is already zero | — |
| avali | **`q[4] = 0`** (was `q[3] = 0`); deleting `q[3] = 0` | — | equivalent in output — **but `q[4]` writes past the 4-cell block**; invisible only because the next block starts at zero | — |

**The test, and its confirmation:** `tests/stdlib/r78_suchi_avali_srij.sm` pins the documented contract — cap
clamped to ≥ 1 (cells: 1 1 5), new lists and queues empty (0 0), a capacity whose size would pass 2⁶³ − 1 refused
(0 0), a new queue first-in first-out from its first element (1 2 3; 7 8 0). **It passes on the real library and
fails on both `c = 2` mutants**; the failure-return mutants fail `tests/r38`. **So the real survivors were 2 + 2,
and all four are killed; the other 32 are equivalent, each for the reason given.**

**Muse's R78 (`4ae80b8`, pushed while I worked) names a different pair:** `sz = c * 8` → `sz = c + 8` in both
functions, which under-allocates and silently corrupts the next block. **On today's tree they are already
killed:** `tests/stdlib/containers21` fails on the `suchi_srij` mutant and `containers23` on the `avali_srij` one,
on v273 and on v275 alike (checked this round). Muse tested them against the R18 guard test only. Muse's
`r78_srij_fill_guard` is still worth adding: it kills them by the neighbour-block marker, which is the property
that matters, and does not depend on which proof happens to touch cell 2.

**The count you asked me to stop repeating:** after R76 and this round, the survivors with a witness — an input
that tells the mutant apart — in every function anyone has listed are **zero**, apart from inputs outside a
function's contract. What remains is equivalent, or (`suchi`/`avali`, above) killed by a test the scorer does not
run. **I would retire "15 surviving mutants" from `PROJECT-MASTER.md` and replace it with a list, not a number.**

## WS3 — the safe/unsafe boundary. Written first, as you asked; nothing built for it.

**ChatGPT is right, and the shape of the problem is this:** the block's check proves one thing — *a scratch
address written in a block does not outlive the block, through the paths it can see.* It proves nothing about what
raw memory writes do, and raw writes are ordinary Sutram. Your three questions, each with the program that answers
it (`evidence-r78/ws3-boundary-cases.txt`, run on v274):

**1. Inside a `mandapa`, can I call a library function that allocates? Yes — and it is not a hole, it is a leak.**
The callee's allocations go to the **persistent** side; nothing about them is scratch, so nothing dangles and the
check has nothing to refuse. A `banao(41)` that allocates and returns a block, kept past two blocks: prints **42**,
correct. **What it costs is the reclamation:** 1,000,000 calls to `roop_ank` inside a block — **171,904 KB** (the
block reclaimed only its own 32-byte buffer: 203,136 KB without it); the library's internal 176 bytes per call stay.
That is R76's finding again, and R79 measures it on a real program. **Not a soundness gap.**

**2. Can checked code be broken by a raw pointer from unchecked code? Yes — two ways, both shown.**
- **Its data can be changed under it.** Inside a block: `a = nirmmita(16)` (a checked name: its own indexes are
  bounds-checked), then `b = nirmmita(16)` (the next scratch block, directly below `a`), then `bhar(b, 4)` — a
  `prakriya` that writes 4 cells into 2. **`a[0] a[1]` print `77 77`.** Nothing about `a` was wrong; the writer
  was unchecked (a parameter is a bare address). **Any raw write can change any checked buffer.**
- **Its escape guarantee can be broken through a call.** `rakh(a)` stores its argument in a module `vitti`; after
  the block, reading through it prints **99** — the next block's data. That is the stated blind spot (calls).

  **So the honest statement is: the check is sound for the code it sees, and the code it does not see — raw writes
  and calls that keep an address — can invalidate it.** That is ChatGPT's sentence, made concrete.

**3. Is there a cheap marker? Yes — a compiler report, opt-in. Priced:**

| option | what it is | price |
|---|---|---|
| **A. `--asurakshit` report (recommended)** | the compiler lists every function that **writes** raw memory — an index store through a name it does not check, `likh`/`likh8`/`akshar_rakh`/`setchar`/`smaran`/… — with the line of the first such write | **~100 lines** of NASM: the two raw-store code paths and the raw builtins already know they are raw; set a per-function flag, print at the end. **Zero run-time cost; no output byte changes** (the guard stays byte-identical). |
| B. the same, **on by default** | a warning in every compile | the same code — but it would flag **124 of the library's 306 functions** and **26 of the examples' 346** (`evidence-r78/ws3-boundary-cases.txt`, a static count): noise that teaches students to ignore warnings. Only for the user's own file, not the library: workable, ~20 more lines. |
| C. a keyword (`asurakshit prakriya`) required for raw writes | the compiler refuses raw writes outside a marked function | the code is small (~60 lines); **the cost is the tree** — 124 library functions and every program that writes a buffer would need the keyword, and a beginner's first array program would need it too. A language change, not a marker. |
| D. a naming rule | e.g. raw-writing functions end in `_r` | free, and unenforced — it is a convention, not a check. |

**My recommendation: A now, and B for the user's own file once A has been used.** C is the right answer for a
"safe subset" release, and it is a decision about what Sutram is, not a fix. **Nothing built** — as you asked,
the answer is written first.

## What I did not do

- **WS3 is written, not built.** A is ~100 lines whenever you want it.
- **Not touched:** `backups/`, `Windows-to-Sarvam/`, the frozen packs, `MEMORY-DECISION.md`.
