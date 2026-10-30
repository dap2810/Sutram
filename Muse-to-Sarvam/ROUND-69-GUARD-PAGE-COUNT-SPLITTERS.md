# ROUND-69 — the guard-page run, the honest scalar-mandapa count, and the two splitters

Base: origin/main `b2d47734` (compiler v263). No tree
changes. I rebuilt Claude's guard-page compiler from
`Claude-to-Sarvam/evidence-r68/` (the 94-byte efence
emitter + arena disabled, per `guard-pages-how.sh`)
and ran everything below against it; the normal
compiler is a fresh build from the same source.

## WS1 — the guard-page run: trustworthy, but not permanent yet

### What it is

Every `nirmmita` block is mmap'd so it ends flush
against a `PROT_NONE` page: one byte past, read or
write, is SIGSEGV. The variant also disables the
arena (`r65_active` forced to 0), so kosh growth
reverts to the relocating mmap path. It lives today
as scratch in `evidence-r68/` (one `.inc`, one
how-to), not as a tool, and it is not wired into any
gate. Claude's parallel brief builds
`tools/guard_page.py` — this section is the
evaluation that tool must satisfy, not a second
implementation.

### 1. Equivalent for in-bounds programs? Yes — with one named exception

Program-by-program comparison, normal vs guard-page
(stdout + exit code, every program):

| Corpus | Result |
|---|---|
| Suite (`tests/run_tests.py`) | **225 PASS / 4 NO-EXPECTATION under both, per-test results identical** |
| `proof_lib` | **226/226 under both** |
| `proof_props` | **86/86 under both** |
| All 229 `examples/` | **229 identical, 0 differ, 0 faults** |
| All 562 `tests/**/*.sm` | 268 compile-fail under both, 294 run-identical, **0 differ** |

The exception: programs that **alias a kosh and then
grow it** are NOT output-equivalent. The R65 P1
program prints `99/99, 4/4, 5/5, a[1]=8` under normal
v263 (in-place extension) and `99/7, 2/3, 4/2, 5`
under the guard-page variant (relocating growth —
the v261 semantics). This is a semantic difference,
not a fault: both runs are memory-safe, but the
guard-page compiler is not a drop-in equivalent
compiler. No tree program exhibits it (the only
aliasing programs, 252/255, do not grow after
aliasing — which is why the suite and examples come
out identical). Two further non-equivalences to
record for the tool: per-block mmap+mprotect costs
two syscalls per allocation (the suite runs in
seconds either way; long-running programs pay more),
and address-dependent output would differ (no tree
program prints a pointer).

### 2. Coverage of allocation paths: all of them, and it closes a real hole

| Path | Guarded? | Note |
|---|---|---|
| `nirmmita` blocks | **Yes, read + write** | In-bounds probe prints fine; read-past and write-past both SIGSEGV |
| `kosh` buffers (declared + grown) | **Yes** | Plus the compiler's checked indexing, which traps first (`mala ank seema atikram`, exit 1) |
| `mala` arrays | **Yes** | Same: checked indexing traps first |
| Module globals | N/A | Globals are scalars only; global arrays are unsupported (R56 negative test) — there is no guardable global block |

The guard page matters exactly where the checks do
not reach: **laundered access**. A handle retrieved
through a container read loses its kind (R65), so
indexing it is unchecked raw pointer arithmetic.
Probed under both compilers: a write 5 cells past a
kosh buffer, 9 cells past a grown kosh buffer, and 5
cells past a mala array all **SIGSEGV under the
guard-page compiler and silently succeed under the
normal one** (exit 0, plausible output). The
checked-indexing layer and the guard-page layer are
complementary, not redundant — the first catches
direct over-indexing, the second catches the bypass.

Controls reproduced on my build: the pre-fix 217
(SIGSEGV, exit 139 — the current 217 is fixed and
correctly does not fault) and the laundered writes
above. These two are the controls the permanent tool
should name.

### 3. How many examples does it exercise? All of them

The worry that "it only runs the tests" does not
survive inspection: **the suite IS the examples**
(`tests/run_tests.py` globs `examples/*.sm`) — 225
verified against goldens, 4 reported NO-EXPECTATION
(215, 216, 217, 219: run, but no golden to compare).
My direct run closes even that gap: all 229 examples
run cleanly under the guard-page compiler with
outputs identical to normal. Add 226 stdlib proofs
and 86 property proofs, and the gate covers every
runtime program in the tree. The remaining `.sm`
files (`tests/r*_check/`, `tests/r44_pending/`) are
compile-time checks, mostly negative (unclosed
blocks, unknown imports) — they never produce a
runnable binary, so the guard page has nothing to
cover there.

### Permanence verdict

**Not permanent today.** Reproducing it took a
source copy, two edits, and symlinks, and two pieces
of friction the tool must fix: `SUTRAM_COMPILER` as
a relative path breaks (the runner changes directory
— an absolute path is required), and the compiler
resolves `lib/` relative to its own binary, so the
tool must place or link `lib/` next to the built
binary. Recommendation: adopt Claude's
`tools/guard_page.py` when it lands, wire
suite + proofs under it as a gate, and name the two
controls (pre-fix 217, laundered-write probe) in the
tool's documentation. Do not wire it as a
replacement compiler — the kosh-semantics
difference in §1 means it is a gate, not a build.

## WS2 — the scalar-only mandapa count: 33, not 3 (and still small)

Definition, stated before the number: a program
qualifies iff (1) its own code contains **no kosh**
at all, (2) it has **at least one allocation**, and
(3) **every** allocation in its own code is
fixed-size with scalar contents — a constant-size
`nirmmita` holding scalars (including a rachana
block of scalar fields) or a constant-size `mala` of
scalars. Pointer arrays, variable sizes, and
growable containers disqualify.

**Headline: 33 of 229 (14.4%).** Strict reading
(scalars or arrays of scalars literally — rachana
blocks excluded): **25 of 229 (10.9%).**

Qualifying, by kind:

- Rachana blocks of scalar fields (8): 06, 08, 224,
  226, 234, 235, 244, 247.
- Fixed byte/number buffers (5): 217 (scores,
  koshtha, row — all scalars), 256 (byte buffer),
  array_demo, full_demo, mem_safe.
- Fixed `mala` arrays of scalars (20): 20, 246, 249,
  251, 253, 254, 67, 68, 71, 72, 73, 74, 76, 80, 82,
  83, 85, 89, 90, 91.

Excluded, and why (the near-misses matter):

- 237, 248: real kosh use (decl + push).
- 75: variable-size mala (`mala[n+1]`) — not fixed.
- 215: pointer array (`uptrs` holds packed-byte
  pointers) **and** a nighantu use — doubly out.
- 216: `avastha[0]` holds a string pointer — the
  block is a pointer+scalars mix, not scalars.
- The other 191 examples have **no allocations at
  all** — there is nothing for a block to hold.

Two caveats. Transitive: no qualifying program calls
a lib function that allocates kosh internally (the
lib's kosh users are the kosh builtins themselves
and container modules no qualifier touches), so the
count survives the transitive reading. And the
narrowest reading — allocations that are temporary
workspace repeated per loop iteration or per call
(R68's strong sense) — is still **1 (217, 1,408 B)**.
So: not three, but not the memory model either.
Fourteen percent of programs qualify on the broad
reading, eleven on the strict one, and the programs
whose allocations actually grow are the kosh
programs K0 excludes.

## WS3 — the two splitters: both doc bugs, pad_vam-style

The splitters are `varna_bhed` (cell strings,
`lib/varna.smlib:248`) and `khand_bhed` (byte
strings, `lib/khand.smlib:201`), same signature
`(src, sn, sep, sepn, parts, maxparts)`. (`rakh_bhed`
is set difference, not a splitter.) ChatGPT's R140
flagged two contract problems; both check out, and
both are **contract wrong, body right** — the same
diagnosis as `pad_vam`.

### Problem 1 (both): the zero-limit contradiction

Stated contract: "returns the segment count
(capped at maxparts)". Actual behavior: the two
degenerate cases ignore `maxparts` entirely — empty
input writes `parts[0] = 0` and returns 1; empty
separator writes the whole input as one segment and
returns 1. Probed all four degenerate calls at
`maxparts = 0`: **all return 1**. Why the body is
right: the R8 split model (300 random cases, a
passing proof) generates `maxparts` 0..4 together
with empty inputs and empty separators, so the
1-segment degenerate behavior is golden-pinned —
changing the body to return 0 would break the proof.
The contract must except the degenerate cases:
*maxparts caps split-produced segments; degenerate
inputs always yield exactly 1 segment.*

### Problem 2 (khand only): the terminator cell

Each segment is unpacked by `khand_mukt`, which by
its own contract "writes a 0 terminator at
`out[n]`". The next segment's length overwrites
every terminator except the last, so a final
**nonempty** segment writes one cell past
`sum(1+seglen)` — probed: `khand_bhed("ab",...)`
writes `parts = [2, 97, 98, 0]`. A final **empty**
segment consumes that position as its own length
cell, so the extra cell is path-dependent — but the
capacity formula must still include it (worst case).
`varna_bhed` has no terminator (direct cell writes;
probed: the cell after the last segment untouched),
so its bound is exactly `sum(1+seglen)`. Why the
body is right: `khand_mukt`'s terminator is its
specified contract (the strb pack/unpack proof was
fixed in R68 to allocate for it), and no reader
needs the final terminator removed — the fix is the
formula, not the code.

### The formulas the contracts must state

| Function | Exact capacity | Worst case (before splitting) |
|---|---|---|
| `varna_bhed` | `sum(1+seglen)` over the first `maxparts` segments | `slen + maxparts` cells |
| `khand_bhed` | `sum(1+seglen) + 1` | `slen + maxparts + 1` cells |

Plus the degenerate cases: empty input → 1 cell;
empty separator → varna `sn+1` cells, khand `sn+2`
cells (prefix + `sn` cells + terminator) — all
regardless of `maxparts`.

Callers are safe by margin where checked: 215's
`parts` (512 cells) verified by the guard-page run
(0 faults); the R8 model (40 cells vs worst 14);
`string_split_join` (20 vs worst 15);
`string_strb_split_join` (64 vs worst 14). No caller
change is needed — only the two contracts.

## NOT RUN

- Windows / WSL: no Windows component in this round.
- Browser automation: no browser component in this round.
- Implementation: no code was changed; the permanent
  tool and the splitter contract fixes belong to
  Claude's parallel brief.
