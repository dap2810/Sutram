# ROUND-68 — `pad_vam` writes one cell past its contract; the guard cannot see the class; a scalar-only `mandapa` helps one example

Base: origin/main `ace0a4e9` (compiler v263; the v418
version is docs, not compiler). No tree changes. Note on
timing: the "fix `pad_vam`" commits on main
(`8ecf26af`, `f629b57a`, `eb9a42a0`) touch only
`Sarvam-to-Claude/ROUND-68.md` — Claude's parallel
brief (fix + audit). The library itself is unchanged:
`pad_vam` below is the current code, still buggy.

## WS1 — the over-write, its callers, its siblings

### 1. Yes: `pad_vam` writes `dst[w]` (`lib/vakyank.smlib`, "Caller must allocate >= width cells")

```sutram
prakriya pad_vam(out, count, width, fill) {
    vitti dst = out
    vitti cnt = count
    vitti w = width
    vitti f = fill
    yadi (w <= cnt) { nivartanam cnt }
    vitti shift = w - cnt
    vitti p = cnt - 1
    yavat (p >= 0) {          # move: max index cnt-1+shift = w-1  (within width)
        dst[p + shift] = dst[p]
        p = p - 1
    }
    vitti q = 0
    yavat (q < shift) {       # fill: max index shift-1 < w      (within width)
        dst[q] = f
        q = q + 1
    }
    dst[w] = 0                # terminator: index w = one PAST width
    nivartanam w
}
```

Every other write stays within `width`; the terminator
does not. The contract as stated needs `width + 1`
cells, not `width`. (ChatGPT's finding is exact.)

### 2. Callers: 4 direct sites, 1 too small

| Call site | Buffer | Width | Needs (width+1) | Verdict |
|---|---|---|---|---|
| `examples/217_r12_report.sm:50` `pad_vam(koshtha, cnt, 6, 32)` | `nirmmita(32)` = 4 cells | 6 | 7 | **TOO SMALL by 3** |
| `tests/stdlib/strconv_pad.sm:6` `pad_vam(buf, 2, 5, 48)` | `nirmmita(10*8)` = 10 cells | 5 | 6 | OK (has the extra cell) |
| `tests/stdlib/strconv_pad.sm:17` `pad_vam(buf, 5, 3, 48)` | 10 cells | 3 ≤ count 5 | — | SAFE (early return, no writes) |
| `tests/stdlib/r11_misc_edges.sm:31` `pad_vam(p, 3, 3, 32)` | `nirmmita(8*8)` = 8 cells | 3 = count 3 | — | SAFE (early return; the test asserts `p[3] = 99` untouched, consistent) |

No `.py` driver generates a `pad_vam` call; `roop_pad_vam`
does not call `pad_vam` (separate implementation, see
§3). So the too-small count is **1 of 4 sites**.

217 in detail (cnt = 2 for every score, so the
early return never saves it): per iteration it writes
cells 4 and 5 (the in-width overrun past the 4-cell
block) **and** cell 6 (the terminator) — three cells
past the allocation, not two. R67-00's analysis covered
cells 4–5; the terminator cell is additional. (Why
217's v263 output shows only last digits is Claude's
settled territory and is not re-litigated here.)

Decision input, not a fix: **no in-tree caller reads
`dst[w]`** — strconv_pad reads `buf[0..n1-1]` (n1 = w),
r11 reads `p[3]` under early return, 217 reads
`koshtha[0..5]` (not [6]). Deleting the terminator
would make the stated contract true with zero in-tree
caller changes; keeping it and restating the contract
as `>= width + 1` keeps a write no caller reads and
leaves 217 still wrong. Which to choose is the fix
round's call (Claude's brief), not this count's.

### 3. Sibling contracts: 4 explicit, 1 violated; plus the pattern class

Explicit "caller must allocate ≥ N" contracts in `lib/`:

| Function | Contract | Body | Verdict |
|---|---|---|---|
| `pad_vam` (vakyank) | ≥ width cells | writes `dst[w]` | **VIOLATED by 1** |
| `chakravala` (ganita) | ≥ 2 cells | `out[0]`, `out[1]` only | WITHIN |
| `samasa` (ganita) | ≥ 2 cells | `out[0]`, `out[1]` only | WITHIN |
| `brihat_ank_tak` (aadhar) | ≥ 4n cells (n>0), ≥ 1 (n≤0) | `dst[0..rlen-1]`, no terminator past `rlen` | WITHIN on the lemma* |

\* `brihat_ank_tak` holds iff `rlen ≤ 4n`: the comment's
own digit argument (base-16 digits carry ≤ 4 bits each,
so base-2 digits ≤ 4n; its scratch `rev = nirmmita(c*4*8)`
relies on the same lemma). The lemma is asserted in a
comment, not checked by any tool — it is the one
unverified link in the "within" column.

Pattern siblings (same `dst[w] = 0` shape, **no stated
contract**): `roop_pad_vam`, `roop_pad_dakshin`,
`roop_pad_madhya` in `lib/roop.smlib` all write
`akshar_rakh(dst, w, 0)` on the pad path and
`akshar_rakh(dst, cnt, 0)` on the early-return path —
so they need `width + 1` (or `count + 1`) cells without
saying so. Their only callers are in
`tests/stdlib/fmt_pad.sm` (`out = nirmmita(128)` = 16
cells, widths ≤ 6, need ≤ 7) — safe by margin. Vague
cousin: the khand module convention ("out-buffers get a
0 terminator; the caller allocates generously") states
no number, so compliance cannot be checked — but every
terminator-writing khand function inherits the same +1
requirement implicitly.

**Verdict for "fix one function or audit the library":
fix one function (`pad_vam`), and annotate the pattern
class.** The explicit-contract audit finds exactly one
violator; the pattern audit finds three more functions
with the same shape but no contract and currently-safe
callers. The library does not have a systemic
over-write problem — it has one bug and one unstated
convention.

## WS2 — can the existing guard catch this class? No, by construction

`tools/check_alloc_bounds.py` (run today: 26 computed
allocations, 13 bounded + 13 exempt, 0 failed) checks
**allocation sizes**: every computed `nirmmita(...)`
size in `lib/` must be preceded by a bound on its count
(so a wrapped size never exists). It does not read
write indices at all. Three independent reasons it
cannot catch `dst[w]`:

1. **Wrong domain.** It reads size expressions, never
   index expressions. `dst[w]` vs `width` is an index
   question; the tool has no index input.
2. **Nothing to check.** `pad_vam` contains no
   `nirmmita` — it writes into the caller's buffer. A
   function with zero allocations is invisible to this
   guard however wrong its writes are.
3. **Wrong property even where it applies.** Where it
   does see an allocation, it checks the size
   computation (overflow), not whether later writes stay
   within the allocated size.

**The smallest change that would catch it** has two
parts, and both are needed — either alone is insufficient:

1. A machine-readable contract annotation per prakriya,
   in a strict format reusing the existing phrasing
   (e.g. `# requires: <buffer> >= <expr> cells` —
   `pad_vam`'s would read `# requires: out >= width cells`).
   Without this, the checker has no size to compare an
   index against, and cannot distinguish `dst[w-1]`
   (fine) from `dst[w]` (bug).
2. Extend the same line-reader to collect indexed writes
   with non-constant indices and flag any write whose
   index is not proven `<` the annotated size by a
   preceding bound or loop condition. For `pad_vam`:
   annotated size `width`, write index `w` — `w < width`
   is false → flagged. (A cheaper heuristic — "flag
   writes at exactly a parameter" — would false-positive
   on legitimate terminators and is not recommended as
   the guard.)

**How many of the 26 would need the new rule?
Strictly 0; functionally 1 function.** The 26 are
allocation sites; the new rule checks write sites — a
disjoint population, so the guard still passes all 26
after adding it. At function granularity, only
`brihat_ank_tak` (2 of the 26 sites) directly writes a
caller buffer under an explicit contract — the one place
the new rule adds information the allocation guard cannot
give. The other 24 sites sit in container constructors
and growth functions (writes into their own fresh
allocations, passing a write rule by construction) or in
helpers that delegate writes to callees (`brihat_shesh`,
`brihat_ghatmod` write only through `brihat_gun` /
`brihat_shesh_sahaya` calls) — which a line-based rule
cannot follow. And the class the bug is in
(caller-buffer writers like `pad_vam`) has **zero**
representation among the 26: the guard's coverage and
the bug's class do not overlap at all.

## WS3 — a scalar-only `mandapa`: the count is 1 (strong) / 16 (weak)

Definition, stated before the number: "helped" in the
strong sense means the block eliminates a leak that
grows with execution — a scratch allocation repeated
per loop iteration or per call in a loop. A once-used
buffer in a short program gains nothing measurable from
rewinding (the program ends). Both counts are given;
the strong one is the decision number.

- **Direct loop scratch: 0 examples.** No example
  allocates `nirmmita` textually inside a loop body
  (brace-tracked scan, verified against do-while tails
  and the `215:72` / `216:88` near-misses, both outside
  loops).
- **Indirect (helper allocates per call in a loop): 1
  example.** `217_r12_report.sm` calls `ank_tak_varna`
  8 times in its loop, and `ank_tak_varna` allocates a
  176-byte `rev` scratch buffer on every call — 1,408
  bytes retained that a `mandapa` inside the helper
  would rewind. No other example loop calls a
  scratch-allocating lib function.
- **Weak (function-local scalar scratch that could sit
  in a `mandapa`): 16 files** — `06_rachana`, `08_demo`,
  `215_r12_wordfreq`, `216_r12_expr`, `217_r12_report`,
  `224_unknown_field`, `226_long_field_names`,
  `234_ambiguous_field`, `235_duplicate_field`,
  `237_many_variables`, `244_r18_rachana_in_function`,
  `247_r23_methods`, `256_r44_vartani_sanskrit_names`,
  `array_demo`, `full_demo`, `mem_safe` — all
  single-use buffers and rachana blocks, none returned
  or stored globally (checked). Rewinding them at
  function exit saves nothing these programs can
  observe.
- **Contrast (excluded by K0): the loop-allocation
  population that leaks meaningfully is `kosh`.** 36
  examples use `kosh_push`; the loop-kosh programs are
  `203` (single), `205` (single), `208` (interleaved
  pair), `209` (single-kosh loops) — plus the R67
  single-kosh long-loop pattern. K0's kosh exclusion
  removes exactly this population from the block.

**Answer: if the number must be one, it is 1 (217, by
1.4 KB).** On the weak reading it is 16 with no
measurable gain. Either way the block is a small feature,
not the memory model — the programs whose allocations
actually grow are the ones K0 excludes. (What this count
does not measure: the block's escape-safety value as a
programming model, which is a separate argument from
leak elimination.)

## NOT RUN

- Windows / WSL: no Windows component in this round.
- Browser automation: no browser component in this round.
- Implementation: no code was changed; the fix belongs
  to Claude's parallel brief.
