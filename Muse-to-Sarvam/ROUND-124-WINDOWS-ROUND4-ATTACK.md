# Muse Round 124 — Attack the Windows round 4 branch before it merges

- **Base for WS2/WS3:** main at v298 (`33cab2dc`, compiler `Sutram 1.0 (v298)`).
- **Base for WS1:** the Windows round-4 branch `pr65-wr4` (fetched from GitHub PR
  #65, tip `029c06d4`, "Windows round 4: verify shared memory accounting,
  budgets and kosh regions").
- **Deliverables:** this report, `r124.json`, `r124_ws1_branch.md` (full branch
  attack log), `r124_maxcap_alias.sm`, `r124_parimita_kosh.sm`,
  `r124_hello_loop.sm`, `r124_kosh_16.sm`.
- **Attack only.** No merge, no push, no code change to main or to the branch.

## Corrections to the brief, stated first

1. The brief says the patches are in `Windows-to-Sarvam/win-round4-2026-11-03/`
   as `arena.patch`/`regions.patch`. That folder does **not** exist on main —
   but it **does** exist on the branch worktree (with `arena.patch`,
   `regions.patch`, `FIXES.md`, `MEMORY.md`, `INTEGRATION.md`, contracts, and 23
   probe programs). The attack therefore worked from the branch code itself,
   using the folder only as coverage evidence. The brief's path was right about
   the branch, wrong about main.
2. The branch's merge-base against main is `5d7d21cb` (the Round 119+120
   delivery, v297), **not** current v298 main (`33cab2dc`). Verdicts below are
   about the branch, not v298 — and the branch does **not** include v298's
   string fixes. It has its own string work (see the integration caveat at the
   end), which is incompatible with v298's in the one place that matters.

## WS1 — Attack the branch, not the report. Verdict: two holds with degradation findings, one hold with bypasses, one HOLE — and the hole is on main too

### Reserve-and-commit: CONFIRMED from code (this corroborates WS2)

The PE shim `win/winrt_blob.asm:143-151` (`.alloc`) issues one
`VirtualAlloc(NULL, size, 0x3000, 4)` — `0x3000 = MEM_COMMIT | MEM_RESERVE`,
`PAGE_READWRITE` — for the full requested size, with no reserve-only step and
no incremental commit anywhere, and no `VirtualFree` path (`munmap` returns
`ENOSYS`). So the 1 GiB arena costs 1 GiB of commit on first use and each kosh
region costs 64 MiB of commit, even when nearly empty. This corroborates the
branch's Windows measurements: arena − empty = 1,075,838,976 = 1 GiB + exactly
2 MiB; one kosh − empty = 67,239,936 = 64 MiB + 128 KiB; working sets only
~3.7 MB. The commit is real; the working set is small. Both numbers matter.

### (a) What happens to a kosh alias when the arena is exhausted? HOLDS for the alias, with degradation findings. Coverage: none.

On a normal PE build a kosh never lives in the arena: `r101a_regions_on` is
true on ELF and PE, `kosh_push` calls `r101a_emit_kosh_extend` and skips the
arena-extension path entirely when regions are on. Arena exhaustion itself is
clean: the persistent side falls back to per-call `VirtualAlloc` (`r69_n7` →
`r38_nirm_mmap`); the scratch side exits 1 with `kshetra purnam`
(`r73_gen_scratch_nirm`); reserve failure sets `cur = end = sima = 16`
(`r69_n3`), after which every nonzero `mandapa` allocation exits 1 while
persistent allocation continues — a PE-specific availability cliff, since eager
1 GiB commit fails far more readily than Linux `MAP_NORESERVE`. `parimana()`
also freezes at the arena size thereafter (fallback bytes uncounted).
**Coverage: none** — no probe fills the arena, and `alias_obstacle` passes
trivially under regions (its obstacle is a persistent allocation, the kosh is
in its own region, the arena path is skipped), so it does not test obstacle
aliasing. Linux v298 (shared paths, not PE proof): arena filled exactly
(`parimana()` = 1,073,741,824), alias still `99/99`; post-fill fallback
`nirmmita` leaves `parimana()` frozen at 1,073,741,824; post-fill scratch exits
1 with `kshetra purnam`.

### (b) What happens to `parimana()` inside nested `mandapa` blocks? HOLDS for nested reads, with two adjacent accounting holes. Coverage: none at depth ≥ 2.

`parimana()` (`.ge_call_parimana`) is depth-free: `(cur − base) + (sima − end)
+ 0parimana`. Per-depth marks (`0mNN`, max depth 32, deeper is a compile
refusal), block-exit rewinds, and return-rewind to the outermost mark of the
procedure make nested reads correct by cursor arithmetic. **Coverage: none at
depth ≥ 2** — branch probes read it only at one level. Linux v298: nested reads
`0, 16, 48, 16, 0`; return from the inner of two nested blocks gives `7, 0`; a
callee called from inside a block sees the caller's scratch (`16`), confirming
accounting is global, not lexical. Adjacent holes: (1) after any kosh
relocation, `parimana()` **overcounts by exactly the dead region** — measured
`100663328` = dead `33554448` + live `67108880`, because the relocate path
skips the `0parimana` count and the old region is never subtracted; (2) after
arena exhaustion it **undercounts** (frozen, §(a)).

### (c) What happens when a `parimita` budget is hit inside a nested block? HOLDS for lexical nesting, with two scope bypasses. Coverage: partial.

`r103_emit_budget_checks` walks the parse-time budget chain innermost-first,
checks `(mark − new_end) > N` (aligned bytes, so `parimita 15` + `nirmmita(1)`
refuses) **before** storing `[end]`, and exits 1 with `E_PARIMITA` naming the
violated budget. The walk has no depth cap. **Coverage: partial** — 2 levels
covered (`budget_inner`, `budget_outer` — the latter does cover
inner-fits-but-outer-exhausted, naming outer 16; plus rounding/exact cases);
3+ levels and both bypasses uncovered. Linux v298: 3-level inner hit names 16,
3-level outer-only hit names 16, both exit 1. Bypasses (documented scope,
unprobed, real on PE): **kosh allocations never trip a budget** (`mandapa
parimita 16` containing a kosh declaration + push prints `reached`, exit 0 —
confirmed on Linux v298 by probe `r124_parimita_kosh.sm` — and each such kosh
costs 64 MiB commit on PE); **called procedures' persistent allocations are
never charged and escape the block's rewind**.

### (d) Does the PE path handle a kosh that grows past `R101A_MAXCAP`? HOLE — silent alias break, and the real cliff is lower. Coverage: none near the boundary.

Growth always doubles (`newcap = cap*2`); `r101a_e1` does `cmp r11, MAXCAP;
ja <relocate>`; the relocate copy path updates **only the named variable** —
every alias keeps the old pointer, with no error and exit 0. Because doubling
goes 4,194,304 → 8,388,608 (5 over `MAXCAP` = 8,388,603), a grown kosh relocates
on the push from 4,194,304 to 4,194,305 elements — the effective alias-stability
limit is **4,194,304, not 8,388,603** (8,388,603 is reachable as a held length
only via a declared capacity in that window, and even then the first
overshooting doubling relocates). **Coverage: none near the boundary** —
`alias_many` stops at 10,001 elements, 400× below the cliff.

**Confirmed on Linux v298 by probe `r124_maxcap_alias.sm`** (so this hole is on
MAIN, not just the branch): create a kosh, push 41, alias it (`vitti k = a`),
push 4,194,305 more elements (past the doubling cliff), then write `a[0] = 99`
after relocation and read both names — `a[0]` prints `99` (new region,
updated), `k[0]` prints `41` (old region, stale), exit 0. (A first probe that
read `[0]` without a post-relocation write printed `41`/`41` and proved
nothing, because both regions held 41 at `[0]`; the post-relocation write is
what distinguishes the regions, and it is the probe delivered here.)

Separately, **allocation failure → crash, not refusal**: neither the declaration
path (`.gs_decl_kosh`) nor the relocate copy path checks for 0, but both
allocator paths map failure to 0 (`r101a_a2`, `r38_nirm_mmap`; the PE shim
returns −1 on `VirtualAlloc` failure) — so on PE, under commit pressure, a kosh
declaration or a relocating push writes its header to address 0
(`0xC0000005`), not a diagnostic. A latent capacity-overflow note (bytes =
`(cap+5)*8` with only negative→0 normalisation) is included as code-derived,
not run.

**WS1 verdict: the branch's 312 PASS / 0 FAIL is real for what it probes, and
the probes do not cover the four cases above.** The alias-on-exhaustion and
nested-`parimana` cases hold; the nested-`parimita` case holds lexically but has
two real bypasses; the MAXCAP case is a silent alias break on main as well as
on the branch, and it is the finding that should block a merge until the
relocate path updates aliases (or refuses aliased growth past the cliff).

## WS2 — Is the "reserves AND commits" cost true on Linux too? No. It is a platform difference, and Linux proves lazy is possible.

Method: a hello-world that prints `hello` and then busy-loops so a Python
sampler can poll `/proc/<pid>/status` (same sampler as Round 121 WS2,
`r124_hello_loop.sm`).

| Platform | Peak RSS | Peak VSZ |
|---|---:|---:|
| Linux v298, hello-world (no allocation) | 16 KB | 240 KB (0.2 MB) |
| Linux v297, 1 kosh (Round 121 WS2) | 32 KB | 1,088.2 MB (= 1 GiB arena + 64 MB region + 0.2 MB) |
| Windows round-4 branch, hello-world (branch report + code) | ~3.7 MB working set | 1 GiB commit on first use |

The Linux hello-world reserves **nothing**: no 1 GiB arena, no region. The arena
is reserved lazily on first allocation (the kosh probes, which call `nirmmita`,
show the full 1 GiB in VSZ; hello, which never allocates, shows 0.2 MB), and
untouched pages are never committed (`MAP_NORESERVE`). Windows, per the branch
code (`VirtualAlloc` with `MEM_COMMIT | MEM_RESERVE` for the full size) and
the branch's measurements, commits the whole 1 GiB on first use and 64 MiB per
kosh region, even when nearly empty. **So the brief's claim is true on Windows
and false on Linux, and the difference is the adapter, not the design:** Linux
proves the arena can be lazy and the regions can be reserve-only. The 1 GiB
Windows charge is the PE adapter's eager commit, and it is worth documenting
as such — a Windows student who reads the Linux numbers (0.2 MB for hello)
and expects the same on Windows will be surprised by 1 GiB of commit.

## WS3 — The 16-kosh ceiling, verified on Linux. Claude's number is correct, and the crash is a segfault, not a refusal.

Method: probe `r124_kosh_16.sm` creates 16 kosh (one per iteration, via a
`make_kosh` helper, held in a `nirmmita` buffer) and prints `made N` after each.

- Control (no limit): `made 1` … `made 16`, `all 16 made`, exit 0.
- Under `ulimit -v 1048576` (1 GiB address space): `made 1` … `made 15`, then
  **segfault, exit 139**, during the 16th kosh creation (before `made 16` is
  printed).

**Claude's number is verified: under a 1 GiB address limit, the 16th kosh
crashes.** The arithmetic is exact: 15 × 64 MB = 960 MB fits; the 16th (1,024 MB
+ overhead) exceeds `RLIMIT_AS`, the region `mmap` fails, and the failure is
unchecked (the same unchecked-failure shape as WS1(d)'s allocation-failure
crash) — so the program segfaults instead of refusing cleanly. Note: the arena
did not block the run (its reservation failed silently / fell back under the
limit, since kosh regions are separate from the arena) — the crash point (16th)
is exactly the region count, not the arena. **This is a hard ceiling nobody
documented**, and it interacts with Round 121 WS2 (64 MB per kosh virtual) and
WS1(d) (allocation failure → crash): the ceiling is real, the crash is dirty,
and both should be documented (and the failure path should refuse, not
segfault).

## Integration caveat — do not merge the whole branch over v298 without reconciliation (from the branch's own `INTEGRATION.md`, tip commit; concurred)

Round 3/4 replaced `vartani_sandhi`'s in-place body with a fresh-allocation
join, while v298 preserves in-place mutation (with the literal refusal
`E_VARTANI_STHIRA`, see Round 122 WS2). Main's Round 121 report identifies
`tests/r54_check/raw_valid.sm` as depending on mutation. Merging the branch's
string body would break mutation-dependent programs (and would re-open the
Round 120 mutation question in reverse: now the mutation is gone, but programs
expecting it break). The branch itself recommends retaining v298 semantics and
porting only the PE enablement/harness corrections. **Concurred.** Claude
remains the merger; this round's contribution is the four uncovered cases
above, not a merge recommendation.

## NOT RUN

Windows execution of any kind (all PE statements are code readings plus the one
shim call site; Linux results are labelled as not PE proof where the allocator
differs), browser, merge/push/code change (attack only), native-speaker review.
