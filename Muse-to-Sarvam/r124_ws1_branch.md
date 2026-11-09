# Muse Round 124 WS1 — Attack on the Windows round-4 branch (pr65-wr4)

## Scope, method, and what this is not

- **Task:** attack the cases the branch's own probes did not cover, by reading the
  branch's PE code path. Read-only. No merge, no push, no code change to main or
  to the branch, no worktree deletion, no other agent's rounds.
- **Branch:** local branch `pr65-wr4`, tip `029c06d4`
  ("Document concurrent v298 integration conflict and inherited string
  compatibility gap"). Worktree: `<workspace>/r121-124/tree-wr4`.
- **Base divergence (important):** the merge-base of `pr65-wr4` against
  `origin/main` is `5d7d21cb` (Rounds 119+120), **not** current v298 main
  (`33cab2dc`). The branch therefore predates the v298 work. All verdicts below
  are about the branch's code, not about v298 main.
- **Brief discrepancy, noted not followed:** the assignment brief said
  `Windows-to-Sarvam/win-round4-2026-11-03/` does not exist in the repo and to
  work from the branch. In the `tree-wr4` worktree that folder **does** exist,
  containing `arena.patch` (3,188 bytes, UTF-16LE/CRLF), `regions.patch`
  (2,606 bytes, same format), `FIXES.md`, `MEMORY.md`, `INTEGRATION.md`,
  `contracts.py`, `contracts-*.json`, `final-windows/`, `arena-windows/`,
  `regions-windows/`, and `programs/*.sm` (23 probes). The analysis below is of
  the branch code; the folder's reports were used only as coverage evidence
  (what the branch claims to have tested), never as proof.
- **Windows cannot be run from here.** The verdicts rest on code reading of the
  branch. Where a code path is shared with Linux, the equivalent was run on
  Linux v298 in `<workspace>/r121-124/tree298` (compiler
  `Sutram 1.0 (v298)`). Every such result is labelled **Linux v298, not PE
  proof**. The PE differences that matter are confined to (i) the allocator
  translation (`rt_syscall` → `VirtualAlloc`, see §0) and (ii) eager commit;
  the budget checks, the `parimana()` formula, the kosh-growth sequence, and
  the scratch/persistent cursor logic are emitted machine code that is
  identical on both targets (the only target-dependent byte in the error paths
  is the exit translation through `emit_syscall` → `rt_syscall` `.exit`).
- **Branch claims under test (not accepted as verified):** 312 PASS / 0 FAIL on
  Windows (up from 306/3), `parimana()` returning live logical bytes on
  Windows, `mandapa parimita` enforcing, and the kosh alias giving
  `a[0]=99 k[0]=99` on Windows. The branch's own reports state no claim of
  complete memory safety, low-memory resilience, or unbounded alias stability.

## §0. Reserve-and-commit: CONFIRMED — the PE adapter reserves AND commits

**Verdict: the branch's cost claim is correct, and it is visible in the code,
not just in the branch's measurements.**

The PE runtime shim is `win/winrt_blob.asm` (embedded as bytes in
`win/rtblob.inc`, `RT_BLOB_LEN` 759). Its mmap translation, `.alloc`
(`win/winrt_blob.asm:143-151`):

```nasm
.alloc:
    xor ecx,ecx            ; lpAddress = NULL, let Windows choose
    mov rdx,r14            ; dwSize = the Linux length argument (rsi)
    mov r8d,0x3000         ; flAllocationType = MEM_COMMIT | MEM_RESERVE
    mov r9d,4              ; flProtect = PAGE_READWRITE
    call qword [rbx+RT_VirtualAlloc]
    test rax,rax
    jz .error              ; failure -> rax = -1, mapped to 0 by callers
```

`0x3000 = 0x1000 (MEM_COMMIT) | 0x2000 (MEM_RESERVE)`. There is **one** call,
for the **full** requested size, with no reserve-only step and no incremental,
page-granular commit anywhere in the shim. Consequences, all from this call
site:

- The 1 GiB arena reservation (`R65_ARENA equ 0x40000000`,
  `src/r65_arena.inc:48`) is a single `VirtualAlloc(NULL, 1 GiB, 0x3000, 4)`:
  **1 GiB of commit charge on first use, even for a tiny program.** Cursor
  rewind never decommits it (there is no `VirtualFree` path at all — syscall
  11, `munmap`, is not handled by `rt_syscall` and returns `ENOSYS -38`).
- Each kosh region (`R101A_REGION equ 0x04000000`,
  `src/sutram_compiler.asm:8946`) is a single `VirtualAlloc(NULL, 64 MiB,
  0x3000, 4)`: **64 MiB of commit per kosh, even when almost empty**.
- The shim ignores the Linux protection and flags arguments and always uses
  `PAGE_READWRITE`; it ignores the address hint. Every mmap-shaped request
  becomes a fresh, fully committed allocation.

This corroborates the branch's own Windows measurements (`cost-windows.json`,
single sample per process, quoted from the branch, not re-measured here):
empty probe 475,136 bytes private commit; arena probe 1,076,314,112;
one kosh 67,715,072; arena + two kosh 1,210,793,984; working sets only
~3.7 MB. The deltas are the proof: arena − empty = 1,075,838,976 =
**1 GiB + exactly 2 MiB**; one kosh − empty = 67,239,936 = **64 MiB +
128 KiB**; two kosh − arena = 134,479,872 = **128 MiB + 256 KiB**. That is
full-size commit plus small fixed overhead — not lazy, not reserve-only.
Working set stays small because commit is not the same as touched pages; the
branch's warning is about commit charge (pagefile-backed), and the code
confirms it.

**Why this matters for WS1:** on PE, commit exhaustion is far more reachable
than Linux address-space exhaustion (Linux uses `MAP_NORESERVE`, pages
committed only when touched). Every failure mode below that depends on an
allocation failing is therefore a live PE concern, not a theoretical one —
and the failure handling in the kosh paths is, as §(d) shows, a crash, not
a diagnostic.

## §(a). Kosh alias when the arena is exhausted on PE

### What the code does

On this branch a normal PE kosh **does not live in the arena at all**, so
arena exhaustion does not touch it:

- `r101a_regions_on` (`src/sutram_compiler.asm:8964` region, helper just
  above it) returns true whenever `r65_active` is true and `--fail-alloc` is
  off. `r65_active` (`src/r65_arena.inc`, "Shared ELF/PE arena") returns 1 on
  ELF **and** PE (the old `target_pe` exclusion survives only under
  `GUARD_PAGES`). So on a normal PE build every kosh is allocated by
  `r101a_emit_kosh_alloc` into its own region (see §0), and every growth goes
  through `r101a_emit_kosh_extend` first.
- In `kosh_push` (`.ge_call_koshpush`, `src/sutram_compiler.asm:21988`),
  after computing `newcap = cap ? cap*2 : 4`, the code calls
  `r101a_emit_kosh_extend` and, if it returns nonzero, jumps to
  `.r101a_extended`, **skipping `r65_emit_kosh_extend` entirely**. The
  arena-extension path (which is the one sensitive to what sits at the
  persistent cursor) is never attempted for a region kosh.
- Arena exhaustion itself has two clean, distinct behaviours, both in
  `src/r65_arena.inc`:
  - **Persistent side** (`r65_emit_nirm`, `r69_n7` room check): if
    `size > end - cur` (or size is 0), control falls to `.mmap`, the old
    per-call sequence (`r38_nirm_mmap`, `src/sutram_compiler.asm:26365`),
    which on PE becomes one `VirtualAlloc` per call. Allocation keeps
    working; it is simply untracked (see the `parimana()` note below).
  - **Scratch side** (`r73_gen_scratch_nirm`, `src/r65_arena.inc:419`):
    `end - align16(size)` underflowing, or the new scratch pointer meeting
    the persistent cursor (`cmp rdx, rax; jb .full`), prints
    `kshetra purnam` and exits 1. No silent corruption, no fallback.
  - **Reserve failure** (the PE-relevant exhaustion): the arena reserve
    (`r69_n3`, `src/r65_arena.inc:80`: `cmp rax,-4095; jb .ok; mov eax,16;
    xor edx,edx`) sets `cur = end = sima = 16` on failure — "room 0 forever".
    After that, every nonzero persistent allocation takes the per-call
    fallback, and every nonzero scratch allocation hits `.full`
    (`end - size` wraps or the new pointer is below `cur = 16`) and exits 1
    with `kshetra purnam`. A failed 1 GiB eager commit therefore makes
    `mandapa` unusable while ordinary `nirmmita` keeps working — an
    asymmetric degradation that exists only because PE commits eagerly.
- A **new** kosh region can still be allocated after arena exhaustion: the
  region `VirtualAlloc` is independent of the arena cursors. Kosh creation
  survives arena exhaustion; only `parimana()` accounting does not (below).

### Is it covered by the branch's probes?

**No — not the exhaustion itself, and the one probe that looks relevant
passes for the wrong reason.**

- No branch probe fills the 1 GiB arena, simulates reserve failure, or reads
  `parimana()` after the arena is full. The experiment probe sets
  (`arena-windows/`, `regions-windows/`, `final-windows/probes.json`) contain
  only the string probes plus `memory_query` (`likha(parimana())` alone) and
  `memory_budget` (a `parimita 1` refusal). The 9 contracts in `contracts.py`
  contain no exhaustion case.
- `alias_obstacle.sm` (`kosh k[1]`, push 41, `vitti a = k`, then
  `vitti obstacle = nirmmita(64)` as a **persistent** allocation outside any
  `mandapa`, push 42, `k[0] = 99` → `a[0]=99 k[0]=99`) does **not** test
  arena-obstacle aliasing on this branch. Under regions the obstacle is
  irrelevant twice over: the kosh is not in the arena, and the arena-extension
  path is skipped. The probe passes because the region path grows in place,
  not because the obstacle logic was exercised. Anyone reading it as
  "obstacle aliasing verified" is misled.
- The old arena path, where an obstacle *would* break the alias (extension
  requires the kosh data to end at `cur` and the new cursor to stay below
  `end`; `r65_emit_kosh_extend`, `src/r65_arena.inc:301`), survives only
  under `--fail-alloc` (regions off) on this branch. That path is untested
  by the branch probes in any form.

### Linux v298 observations (shared paths, not PE proof)

Run on Linux v298 (`tree298`), where the cursor/fallback/region logic is the
same emitted code and only the allocator differs:

- `arena_fill_alias`: 64 × `nirmmita(16777216)` fills the arena exactly
  (`parimana()` = 1,073,741,824), then a region kosh alias still gives
  `a[0]=99 k[0]=99`, exit 0. **Alias holds through arena exhaustion.**
- `arena_fill_parimana`: after the fill plus one fallback `nirmmita(16)`,
  `parimana()` is still 1,073,741,824. **Fallback bytes are not counted** —
  `parimana()` freezes at the arena size once the arena is full, because the
  formula (§(b)) only sees the cursors and the region counter. This is the
  branch docs' stated exclusion ("excludes … fallback allocations outside
  the arena"), but it means `parimana()` stops being "live bytes" exactly
  when the program is under memory pressure.
- `arena_fill_scratch`: a `mandapa` scratch allocation after the fill exits
  1 with `kshetra purnam`, no `BAD` output. **Clean refusal, as the code
  says.**

### Verdict (a): HOLDS for the alias — with two degradation findings

The kosh alias itself **holds** when the arena is exhausted on PE, because
region koshs never touch the arena. The findings are about what else breaks
around it: (1) after arena reserve failure (the PE-likely form of
exhaustion, given eager 1 GiB commit), every `mandapa` scratch allocation
exits 1 while persistent allocation continues via fallback — `mandapa`
becomes unusable, not degraded; (2) `parimana()` freezes at the arena size
and ignores all fallback bytes thereafter. Neither is a silent wrong value
from the alias, but the second is a wrong accounting value, and the first
is a PE-specific availability cliff the branch does not probe.

## §(b). `parimana()` inside nested `mandapa` blocks on PE

### What the code does

`parimana()` (`.ge_call_parimana`, `src/sutram_compiler.asm:23613`) is a
pure function of three global values — it has no notion of nesting depth,
which is exactly why nesting works:

```
parimana() = (0kshetra_cur - arena_base) + (0kshetra_sima - 0kshetra_end)
             + 0parimana
```

- Persistent bytes: `cur - base`, where base is recovered as
  `sima - R65_ARENA` (`r107_p3` byte string,
  `src/sutram_compiler.asm:555-557`).
- Scratch bytes: `sima - end`. Every scratch allocation lowers `end`;
  every block exit restores it.
- Kosh-region bytes: the hidden global `0parimana`, incremented at each
  region allocation (`r101a_emit_kosh_alloc`: `rcx = requested bytes`,
  counted **before** the allocation syscall) and at each in-place region
  growth (`r107_e1/e2`: `(newcap - cap) * 8`, counted before the capacity
  store). It is **never decremented** — correct only because regions are
  never freed, and wrong in exactly the cases noted below.
- The `cur < 0x1000` path (`r107_p1`: `cmp rax,0x1000; jb .zero`) returns
  `0 + 0parimana` when the arena was never reserved — so `parimana()` after
  a kosh declaration but before any arena allocation correctly reports just
  the region bytes.

Nesting mechanics, all in `src/r65_arena.inc` and the `mandapa` parser:

- Block entry emits `AST_SCRCUR` (`r73_gen_scrcur`), which first reserves
  the arena if needed (`r73_emit_reserve`) and then snapshots the current
  `[end]` into a hidden local `0mNN` — one mark per nesting depth
  (`R73_MAXDEPTH equ 32`, `src/sutram_compiler.asm:35`; depth 33+ is a
  compile refusal, `capacity_fail`, not a runtime hole).
- Block exit emits a rewind (`r73_gen_rewind`: `end = mark`). Marks are
  stack locals, so recursion is safe, and an inner exit restores `end` to
  the inner mark while the outer block's scratch below it (in address terms,
  above the mark) stays live. `parimana()` after an inner exit therefore
  drops by exactly the inner block's scratch bytes and keeps the outer
  block's — the formula needs no depth bookkeeping because the cursor
  already encodes it.
- `nivartanam` inside nested blocks rewinds to the **outermost** block's
  mark of its `prakriya` (`r73_gen_ret_rewind`, `src/r65_arena.inc:531`,
  via `r73_ret_mark` selecting depth-1's mark). A return from an inner
  block therefore rewinds all of that procedure's scratch, not just the
  inner block's. `krama`/`agrim` rewind to the outermost block inside their
  loop (`r73_wrap_jump`), preserving enclosing blocks' scratch.
- One non-lexical property, by design: `parimana()` is **global**, not
  lexical. A `prakriya` called from inside a `mandapa` sees the caller's
  scratch in its `parimana()` reading, because the callee's own block
  entries snapshot the same global `end`. This is "the program's bytes",
  not "this block's bytes".

### Is it covered by the branch's probes?

**No probe reads `parimana()` at nesting depth ≥ 2, or after an inner exit
while an outer block is still open.**

- `rounding_rewind` reads `parimana()` at one level (0 → 16 → 48 → 16).
  `budget_exact` reads it inside one budgeted block and after it (16 → 0).
  `return_rewind` covers a return from one level (7 → 0).
  `test_contract.py:test_accounting_and_budget_work` is the same single
  level (0 → 64 → 0). Nothing reads it inside an inner block, after an
  inner exit with the outer block open, inside a `prakriya` called from a
  block, or after a return from nested blocks.

### Linux v298 observations (shared paths, not PE proof)

- `nested_parimana` (outer 16, inner 32): `0, 16, 48, 16, 0` — exactly the
  formula's prediction. Nested reads, inner-exit drop, and outer-exit
  zeroing all behave.
- `nested_return` (return from the inner of two nested blocks in a
  `prakriya`): `7, 0` — the outermost-mark rewind works.
- `callee_parimana` (`prakriya f()` reading `parimana()` while called from
  inside a 16-byte `mandapa`): `16, 5, 0` — the callee sees the caller's
  scratch (16), its own return value is unaffected, and the caller's
  `parimana()` is 0 after the block. Global accounting confirmed, not
  lexical isolation.

### Verdict (b): HOLDS for nested reads — with two accounting holes adjacent to nesting

The nested question itself **holds**: the cursor formula is depth-free, the
per-depth marks and the outermost-mark return rewind are correct, and the
Linux probes match the code's predictions exactly. But `parimana()` is not
"live logical bytes" in two cases the branch does not probe, both confirmed
on Linux v298 (shared formula) and both present in the branch code:

1. **After any kosh relocation, `parimana()` overcounts by exactly the dead
   region.** The relocate path skips the `0parimana` count (`r101a_e1`'s
   `ja` jumps over the count), the new block is counted via the arena
   cursor, and the old region's bytes are never subtracted. Measured:
   `reloc_parimana` prints `100663328` = dead old region `33554448` + live
   new block `67108880`. The overcount is precisely the abandoned region.
2. **After arena exhaustion, `parimana()` undercounts** (frozen at the
   arena size; §(a)). A third, smaller overcount: a region allocation that
   *fails* is still counted, because the count is emitted before the
   allocation syscall in `r101a_emit_kosh_alloc` — on PE, where a 64 MiB
   commit can fail, this is reachable, and it compounds with the crash in
   §(d) (the program dies on the header write before anyone reads the
   inflated counter, so this one is latent rather than observable).

## §(c). A `parimita` budget hit inside a nested block on PE

### What the code does

Budget enforcement lives entirely in the scratch-allocation path and is a
walk of a parse-time chain — again depth-free in the right way:

- At parse time, `r103_parse_budget` (`src/sutram_compiler.asm:8777`)
  builds, per depth, a record `[mark name, N, source position, enclosing
  record]`; a block without its own `parimita` inherits the enclosing
  record. A `nirmmita` written inside a block becomes `BN_NIRM_SCRATCH`
  and captures the innermost budgeted record into its AST node
  (`[rax+48]`, `src/sutram_compiler.asm:17624-17632`).
- At code generation, `r103_emit_budget_checks`
  (`src/sutram_compiler.asm:8855`) runs inside `r73_gen_scratch_nirm`
  **after** the new scratch pointer is computed and **before** it is stored
  to `[end]`. For each record in the chain, innermost first, it emits:
  `if (mark - new_end) > N: print E_PARIMITA with that block's line and
  budget, exit 1`. The walk has no depth cap (it follows `[record+32]`
  until 0), so three or more levels work by the same mechanism as two.
- The measured quantity is `mark - new_end`, i.e. **aligned** bytes: the
  new pointer already subtracts `align16(size)`. Hence `parimita 15` with
  `nirmmita(1)` refuses (16 > 15) and `parimita 16` with `nirmmita(1)`
  passes — the branch's rounding probes test exactly this.
- A refusal happens **before** the allocation is committed (`[end]` is not
  yet stored, the block is not yet zeroed), and the program exits 1, so
  there is no partial-allocation state to reason about. "Continue after the
  hit" is not a meaningful case.
- The check's scope is stated in the code comments and is the whole story
  for the bypasses below: it covers **lexical scratch allocations only**.
  Kosh storage is not counted, and allocation inside a called `prakriya`
  is not counted (a callee's `nirmmita` is persistent, not scratch,
  because it was parsed with `mdepth = 0`).

### Is it covered by the branch's probes?

**Partially: two levels are covered; three-plus levels and both bypasses
are not.**

- Covered: `budget_inner` (outer 64, inner 16, `nirmmita(17)` → refuses
  naming 16), `budget_outer` (outer 16 already used, inner 64,
  `nirmmita(1)` → refuses naming the **outer** 16 — i.e. the
  inner-fits-but-outer-exhausted variant *is* covered, contrary to a first
  glance), `budget_rounding` (15 vs aligned 16), `budget_exact` (16
  exactly), and the single-level `parimita 1` refusal in
  `test_contract.py`.
- Not covered: a hit at three or more levels; a hit where the violated
  budget is the middle of three; behaviour after an inner rewind followed
  by outer reuse (budget accounting is per block entry, since the mark
  resets on re-entry — a loop iteration re-arms the budget, so a budget
  bounds live scratch, not cumulative allocation); a budget around a call
  to an allocating `prakriya`; a budget around kosh creation or growth.

### Linux v298 observations (shared paths, not PE proof)

- `budget_3level_inner` (64/32/16, `nirmmita(17)`): `E_PARIMITA …
  (parimitih 16 baait)`, exit 1 — innermost violation named.
- `budget_3level_outer` (outer 16 used, then 64, then 64, `nirmmita(1)`):
  `E_PARIMITA … (parimitih 16 baait)`, exit 1 — the outer violation is
  found after both inner budgets pass, exactly as the chain walk predicts.
- `budget_kosh_bypass` (`mandapa parimita 16` containing a kosh declaration
  and a push): prints `reached`, exit 0 — **the budget never fires**.
  Kosh region allocation bypasses `parimita` entirely, by code design.

### Verdict (c): HOLDS for lexical nesting — with two scope holes that are bypasses, not misfires

When a budget **is** hit inside a nested block, the branch code does the
right thing at every depth the chain walk can express: it names the
violated budget (innermost-first walk, so the first message is the
innermost violation, and an outer-only violation is still found), it
refuses before committing the allocation, and it exits 1. The 3-level
Linux probes confirm the mechanism generalises past the branch's 2-level
probes. The holes are in what can never *become* a hit:

1. **Kosh allocations bypass the budget completely.** A `parimita 16`
   block can declare and grow koshs without tripping, and on PE each such
   kosh costs 64 MiB of commit (§0). A budget therefore does not bound the
   block's memory cost on PE — it bounds only its scratch bytes. This is
   documented scope ("budgets cover lexical scratch allocations, not kosh
   storage"), but it is a real bypass of the feature's apparent promise,
   and it is unprobed.
2. **Called procedures bypass the budget completely.** A block that calls
   an allocating `prakriya` is not charged for the callee's persistent
   allocations, which also escape the block's rewind. Same documented
   scope, same unprobed status.

Neither bypass produces a wrong value or a silent misfire inside the
checked path; both mean the checked path is narrower than a reader of
"budget" would assume.

## §(d). A kosh that grows past `R101A_MAXCAP` (8,388,603 elements) on PE

### What the code does

This is the one case that is a genuine, silent, observable hole — and the
effective boundary is not the one the branch docs headline.

**The arithmetic.** `R101A_MAXCAP equ (R101A_REGION - 40) / 8`
(`src/sutram_compiler.asm:8947`) = (67,108,864 − 40) / 8 = **8,388,603**.
The 40 is the 5-qword header used when `r82_on` is set (a kosh declared
inside a `mandapa` anywhere in the program); with the plain 2-qword header
the same bound is merely conservative (16 + 8,388,603×8 < 64 MiB), so the
bound is safe for both header shapes.

**The growth sequence** (`.ge_call_koshpush`, `src/sutram_compiler.asm:21988`):

1. `newcap = cap ? cap*2 : 4` — **doubling, always**. There is no
   grow-to-fit and no cap at `MAXCAP`.
2. `r101a_emit_kosh_extend` (`src/sutram_compiler.asm:8995`) emits, from
   the `r101a_e1` byte string (`src/sutram_compiler.asm:461`):
   `cmp r11, R101A_MAXCAP; ja <relocate>; mov [r8-8], r11; mov r10, r11;
   jmp .space`. If `newcap ≤ MAXCAP`, growth is in place, the capacity
   field changes, no copy, aliases stay valid.
3. If `newcap > MAXCAP`, the `ja` skips the in-place update and control
   falls into the caller's copy path (`.r101a_extended`): preserve old
   pointer/length/newcap, allocate a new block with
   `emit_nirmmita_from_rax` (arena persistent, or the per-call fallback),
   copy `len` qwords, write the header, and — critically — update **only
   the named variable** (`emit_store_named_var` for the push target).
   Every alias (`vitti a = k`, `a = k`) keeps the old pointer. There is
   no error, no message, no exit code: the program continues with two
   live names for two different buffers.

**The effective boundary is 4,194,304 elements, not 8,388,603.** Because
growth doubles, a kosh grown from the default capacity follows
4 → 8 → … → 4,194,304 → **8,388,608**, and 8,388,608 > 8,388,603 by 5, so
the push that takes length from 4,194,304 to 4,194,305 relocates. A grown
kosh can therefore never hold more than 4,194,304 elements without
breaking its aliases; 8,388,603 is reachable as a *held* length only via a
declared capacity in (4,194,304, 8,388,603] — and even then, the first
growth past the declared capacity relocates whenever doubling overshoots
`MAXCAP` (e.g. declared 5,000,000 holds 5,000,000, then relocates on the
first further growth because `newcap` = 10,000,000). Declared capacities
above `MAXCAP` get a region of exactly their size (the `max(requested,
REGION)` in `r101a_a1`) and relocate on their first growth, as the branch
docs state.

**Two further failure modes on the same path, both code-derived:**

- **Allocation failure → crash, not refusal.** Neither the declaration
  path (`.gs_decl_kosh`, `src/sutram_compiler.asm:19067`: capacity → bytes
  → `r108_kosh_alloc` → header writes via `r82_emit_kosh_header` /
  plain `mov [rax],0; mov [rax+8],rcx`) nor the relocate copy path
  (header writes `mov [rax],r9; mov [rax+8],r11; lea r10,[rax+16]` and the
  copy loop) checks the allocation result for 0. But allocation failure
  *is* mapped to 0: the region path (`r101a_a2`: `cmp rax,-4095; jb +2;
  xor eax,eax`) and the fallback path (`r38_nirm_mmap`, same mapping;
  the PE shim returns −1 on `VirtualAlloc` failure) both yield 0. So on
  PE, where a 64 MiB commit or a relocate allocation can genuinely fail
  under commit pressure, a kosh declaration or a relocating push writes
  its header to address 0 (and then copies into `0+16`/`0+40`) — a Windows
  access violation (`0xC0000005`), not a `E_…` diagnostic, not exit 1.
  The `nirmmita`-returns-0 contract is sound for `nirmmita()` itself; the
  kosh paths treat "allocation always succeeds" as an invariant, and on
  PE it is not one.
- **Capacity arithmetic has no overflow check** (code-derived, not run):
  `.gs_decl_kosh` computes `bytes = (cap + 2 or 5) * 8` with only a
  negative→0 normalisation. A declared capacity near 2^61 wraps the byte
  count to a small value, the region allocation succeeds small, the
  capacity field keeps the huge value, and pushes then write past the
  region without ever triggering growth. Reaching this needs an absurd
  literal, so it is listed as a latent defect, not a headline hole.

### Is it covered by the branch's probes?

**No, not at any point near the boundary.**

- `alias_many` reaches 10,001 elements — 0.24% of the 4,194,304 doubling
  boundary and 0.12% of `MAXCAP`. `alias_obstacle` reaches 2 elements.
- No probe declares a kosh with a capacity near, at, or above `MAXCAP`;
  no probe pushes past 4,194,304 elements; no probe reads `parimana()`
  after a relocation; no probe simulates a kosh allocation failure.
  The branch docs state the boundary ("alias stability is bounded by
  requested capacity"; "standard doubling from capacity 4,194,304 already
  asks for 8,388,608 and relocates") but no probe exercises it.

### Linux v298 observations (shared paths, not PE proof)

- `reloc_alias` (kosh `k[1]`, push 41, alias `a = k`, 4,194,304 loop
  pushes, one more push, `k[0] = 99`, print `a[0]`, print `k[0]`):
  output `41, 99`, exit 0. **The alias is silently stale**: `a[0]` reads
  the abandoned region (41, the pre-relocation value), `k[0]` reads the
  new block (99), and nothing reports an error. This is the exact
  behaviour the branch code predicts for PE, because the growth/relocate
  sequence is target-independent; only the allocator behind the new block
  differs (Linux `mmap` vs PE `VirtualAlloc`).
- `reloc_parimana` (same growth, then `parimana()`): `100663328` =
  dead old region `33554448` + live new block `67108880`. The
  `parimana()` overcount from §(b) is the same event viewed from the
  accounting side.

### Verdict (d): HOLE — silent alias break at 4,194,304 grown elements, plus a crash on allocation failure

Growing past the boundary does not refuse, does not warn, and does not
exit nonzero: it relocates, updates only the named variable, and leaves
every alias pointing at stale data that the program can still read and
write (writes through the alias are silently lost to the kosh). The
branch's headline number understates the exposure: for the normal
doubling growth path the cliff is at **4,194,304 elements**, less than
half the advertised 8,388,603, and the branch's largest alias probe
(10,001 elements) is more than 400× below it. Separately, any kosh
allocation failure on PE — made plausible by eager 64 MiB commits — is a
null-dereference crash, because no kosh path checks for the 0 that the
allocator paths deliberately return.

## Coverage table

| Attack case | Branch probe coverage | Verdict |
|---|---|---|
| (a) kosh alias, arena exhausted | None. No arena-filling probe; `alias_obstacle` passes trivially under regions and does not exercise the arena path | **HOLDS** (alias), with mandapa-unusable-after-reserve-failure and frozen-`parimana()` findings |
| (b) `parimana()` in nested `mandapa` | None at depth ≥ 2. Single-level reads only (`rounding_rewind`, `budget_exact`, contract test) | **HOLDS** for nested reads; adjacent holes: overcount after relocation, undercount after exhaustion |
| (c) `parimita` hit in a nested block | 2 levels covered (`budget_inner`, `budget_outer`, `budget_rounding`, `budget_exact`); 3+ levels, callee bypass, kosh bypass not covered | **HOLDS** for lexical nesting (3-level confirmed on Linux); bypasses are documented scope holes |
| (d) kosh past `R101A_MAXCAP` | None near the boundary. `alias_many` stops at 10,001 elements | **HOLE** — silent stale alias at 4,194,304 grown elements; crash on allocation failure |
| Reserve vs commit (WS2 corroboration) | Branch cost measurements only | **CONFIRMED** from `win/winrt_blob.asm:143-151`: one `VirtualAlloc` with `MEM_COMMIT \| MEM_RESERVE` for the full size |

## Integration caveat (from the branch itself — do not merge it whole)

`Windows-to-Sarvam/win-round4-2026-11-03/INTEGRATION.md` (the tip commit
`029c06d4`, which adds only that file) states: upstream advanced during
the run (including v298 compiler changes), the verified Round 4 candidate
is `1b984b5c` based on Round 3 `a01bd5bf`, and the whole branch must not
be merged over v298 without reconciliation. The conflict is semantic, not
just textual: Round 3/4 replaced the in-place `vartani_sandhi` body with a
fresh-allocation join, while v298 (Claude's R121 handoff) preserves the
in-place mutation, refuses literal destinations, and guards literal
addresses at runtime — and main's R121 report identifies
`tests/r54_check/raw_valid.sm` as an existing caller depending on
mutation. The branch's own recommendation is to retain v298 builtin
semantics, port only the `r65_active` PE enablement and harness
corrections independently, reconcile reference and tests, and rerun the
native Windows and Linux suites plus the R121 and R54 contracts; Claude
remains the merger. Nothing in this attack depends on resolving that
conflict, but no WS1 verdict here should be read as clearing the branch
for merge.

## Files read (branch worktree, unless noted)

- `win/winrt_blob.asm` (§0, `.alloc` at :143-151), `win/rtblob.inc`,
  `win/pe_layout.inc` (`RT_VirtualAlloc` offset).
- `src/r65_arena.inc`: arena constants (:48), reserve failure (`r69_n3`,
  :80), arena kosh extension (:301), rewind (:400), scratch allocation
  (:419), return rewind (:531).
- `src/sutram_compiler.asm`: `r101a_a1`/`r101a_e1` (:453, :461),
  `r103_emit_budget_checks` (:8855), `R101A_REGION`/`R101A_MAXCAP`
  (:8946-8947), `r101a_emit_kosh_alloc` (:8964),
  `r101a_emit_kosh_extend` (:8995), `BN_NIRM_SCRATCH` budget capture
  (:17624-17632), `.gs_decl_kosh` (:19067), `.ge_call_koshpush`
  (:21988), `.ge_call_parimana` (:23613), `r38_nirm_mmap` (:26365),
  `r107_p1/p3` (:553-557).
- Branch evidence: `Windows-to-Sarvam/win-round4-2026-11-03/{FIXES, MEMORY,
  INTEGRATION}.md`, `contracts.py`, `contracts-windows.json`,
  `contracts-linux.json`, `programs/*.sm`,
  `{arena,regions,final}-windows/probes.json`,
  `final-windows/native-cases.json`, `cost-windows.json`,
  `tests/windows_round3/test_contract.py`.
- Linux probes (v298, `tree298`, sources in `/tmp/r124/*.sm`): listed
  inline above with their outputs. These files are scratch and are not
  part of the deliverable.

## NOT RUN / not claimed

- No Windows execution of any kind (no Windows host available here). All
  PE statements are code readings of the branch plus the one shim call
  site; Linux results are explicitly labelled and are not PE proof where
  the allocator differs.
- No native-speaker review, no browser work, no merge, no push, no code
  change. The branch worktree was left untouched (only read); the only
  new file is this report.
