# ROUND-67 — the leak bound as a number, and extension coherence on the built v263

Base: origin/main `c0fe2349`, compiler v263 (Step 1 shipped).
Checked against Claude's `R67-00` / `evidence-r67/leak-bound-rss.txt`
after my own measurements were done. No tree changes.
The `217` question is not re-done here: Claude settled it
(the example's bug — `pad_vam` past a 4-cell block, wrong
on v261 too, fixed by `nirmmita(48)`), and I agree with
that verdict from his evidence; this round covers the
brief's WS1, WS2, WS3.

## WS1 — the bound, in bytes (measured on v263)

Method, stated so the numbers can be reproduced: v263
reserves one 1 GiB `MAP_NORESERVE` arena per program
(verified by strace — a single mmap, no per-buffer
syscalls), so the bound is measured as *touched arena
bytes*, sampled live from `/proc/<pid>/status` (VmRSS)
while the program holds its final state after its pushes
(a trailing infinite loop — the programs exit in
milliseconds otherwise). `ru_maxrss` gave inconsistent
readings in this sandbox (an 11 MB "floor" for a process
whose live VmRSS is 20 KB), so it is not used; the
`/proc` figures below match the allocation model to
within ~1% at every point, which is the check that the
method is sound. All programs verified by output length
(1,000,000 / 1,000,000) before sampling.

| Case (v263) | Live VmRSS | Final buffers written | Abandoned | Per append |
|---|---|---|---|---|
| Empty program (floor) | 20 KB | — | — | — |
| One kosh, 1,000,000 appends | 7,840 KB | 8,000,000 B | **0 B** | **0 B** |
| Two kosh interleaved, 1,000,000 each | 32,040 KB | 2 × 8,000,000 B | **16,777,200 B** | **8.39 B** |

**WS1.1: one kosh growing only in place abandons zero
bytes.** The single-kosh VmRSS (7,840 KB) is exactly the
final buffer's written elements (8,000,000 B = 7,629 KB)
plus floor/stack — no abandoned term at all. Extension
always succeeds for the single-kosh loop, as the brief's
"should be zero" anticipated. Saying it plainly: **zero.**

**WS1.2: two kosh interleaved abandon 16,777,200 bytes
total, 8,388,600 per kosh, 8.39 bytes per append.**
Per kosh, the abandoned buffers are the capacities
1, 2, …, 524288 — summing to 1,048,575 elements × 8 B =
8,388,600 B. Claude's independently measured figure is
identical (8.39 B/append per kosh that cannot extend, 0
for one kosh — his `two` row reads 32,000 KB where mine
reads 32,040 KB, the same measurement within page
rounding).

**WS1.3: abandoned grows with appends, not with growths.**
Series for the interleaved pair (VmRSS, floor ~20 KB):

| Appends each | Growths each | VmRSS | Abandoned (model) | Abandoned (VmRSS less final written) |
|---|---|---|---|---|
| 1,000 | 10 | 56 KB | 16,368 B | ~20 KB (page noise at this scale) |
| 10,000 | 14 | 436 KB | 262,128 B | ~260 KB |
| 100,000 | 17 | 3,636 KB | 2,097,136 B | ~2.01 MB |
| 1,000,000 | 20 | 32,040 KB | 16,777,200 B | ~16.0 MB |

Abandoned per kosh is `(2^ceil(log2 N) − 1) × 8` bytes —
between `8N` and `16N` depending on where `N` falls
between powers of two, i.e. **linear in appends**.
The growth count grows only logarithmically (10 → 20
across the series) and sets only how many abandoned
buffers the total is split across. So "bounded" now has
its figure: **at most 16 bytes per append per kosh that
cannot extend (8.39 at 1M), 0 for one that can** — and
the bound is a capacity bound, not a growth-count bound.

## WS2 — the census (same numbers as ROUND-66, delivered alongside)

R66's census, restated here because the brief says it
had not been received:

- **`vitti a = k` forms: 0. `a = k` forms: 2**
  (`252_r38_alias_kosh_oob.sm:7`, `255_r42_alias_kosh_push.sm:7`),
  both deliberate alias tests. No production program
  aliases a kosh by assignment.
- **Kosh passed to a `prakriya`: 166 arguments on 114
  call lines** (158 user + 8 FFI; builtins excluded).
  Passing must stay legal, and the proposed change
  allows it.
- **Kosh stored in a `mala`, `rachana`, or global: 0**
  in tree code (the shapes exist only in evidence
  programs).
- **Declarations in aliasing programs: 2 of 130**
  (128 unaffected; Claude's denominator 131 gives 129 —
  one declaration of method difference, decision number
  identical).
- **Mala and rachana assignments alias too** (mala:
  golden-backed in 254; rachana: proven by test) — the
  mechanism is language-wide, the relocation hazard is
  kosh-specific. Full detail, file names, and the
  language-wide-vs-kosh-scoped analysis are in
  `ROUND-66-KOSH-ALIAS-CENSUS.md`, delivered with this
  round.

## WS3 — what the built code does to the R65 finding: they agree now

R65 predicted, for program P1 (alias, then in-place
growth, then reads through both): under in-place
extension the handles would print `99/99` with equal
lengths and `a[1] = 8`, where v261 printed `99/7`,
lengths `2/3` then `4/2`, and `a[1] = 5`. Run on the
built v263 against a genuine v261 binary (built from
`f0714d09` source, `--version` verified):

| Read | v261 (before) | v263 (built) | R65 prediction for in-place |
|---|---|---|---|
| `a[0]` / `k[0]` after `a[0] = 99` | 99 / 7 | **99 / 99** | 99 / 99 |
| `len(a)` / `len(k)` after `push a 5` | 2 / 3 | **4 / 4** | 4 / 4 |
| `len(a)` / `len(k)` after `push k 10` | 2 / 4 | **5 / 5** | 5 / 5 |
| `a[1]` at the end | 5 | **8** | 8 |

**They agree where they used to diverge — extension
happened, and this is a behavior change that must be
documented.** The language now does something it did
not do before: an alias of a kosh *is* the kosh across
growth (R42's stated semantics, previously true only
until the first growth). No tree golden depends on the
old divergence (the only alias goldens, 252 and 255,
never grow after aliasing), so nothing in the tree
changes output — but any user program that aliased and
grew will observe shared state where it previously
observed divergence. That sentence belongs in the v263
release notes, not just in this report.

The coherence extends through containers, in both
directions of the model, verified on v263 vs v261:

- **Stored handles, k topmost (in-place):** `m[0] = k`,
  `d.k = k`, grow k, write `k[0] = 99` → v263 reads
  `99/99` through both stored handles; v261 reads `7/7`.
- **Stored handles, k NOT topmost (relocating):** an
  intervening `mala` + `nirmmita` allocation after k's
  first push makes k's growth relocate even on v263 →
  stored handles read `7/7` on both compilers. The model
  from R65 (extendable iff topmost) holds on the built
  compiler in both directions, not just the favorable
  one.

## NOT RUN

- Windows / WSL: no Windows component in this round.
- Browser automation: no browser component in this round.
- Implementation: no compiler code was changed; the
  v261 binary was built from archived source in the
  workspace (not in the tree) for the before-column only.
