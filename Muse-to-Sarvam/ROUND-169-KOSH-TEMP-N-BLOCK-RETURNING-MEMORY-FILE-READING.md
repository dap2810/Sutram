# ROUND-169 — `kosh temp[n]`, a block returning memory, and the file-reading section

**Base:** main at v315, tip commit `064b05ad` · **Deliver into:** `Muse-to-Sarvam/`

**Read only. Nothing compiled or run.** Every line number below was re-grepped
on the tree or branch cited; none was carried from the brief or another round.
Counts were re-derived from the tree. Task 1 read the hoist on the v319 tip
`4c1159be`, branch `r176-made-once-anywhere`. Paths are relative to the repo
root.

---

## Task 1 — `kosh temp[n]`: CONFIRMED

R165 said the runtime-capacity question was "sound but vacuous — the
restriction does not exist. The gate already asserts the runtime-capacity
case is hoisted." That is correct, and the reading extends it to a
computed size and to growth across passes.

### The candidacy check accepts a data-dependent size

`r175_cand` (`src/sutram_compiler.asm:10958-11029` on v319) checks only
the declaration kind (`[decl+32] <= 3`, `:10967`; kosh kinds 2/3,
`:10969`; mala kind 0/1 with a size and no initializer, `:10971-10975`).
It never looks at `[decl+24]` (the size) at all. The scan arm for a
declaration, `r172_scan` `.decl` (`:11263-11292`), scans the size
expression exactly like any other expression (`mov rdi, [rbx+24]`,
`:11286`): it escapes only if the size mentions the kosh's own name or
contains a node the scan does not know. So `vitti n = i * 10` followed
by `kosh temp[n]` passes, exactly like the gate's `kosh k[j]`; the same
holds for `kosh temp[i]` directly. The only size that disqualifies is
one that uses the kosh itself (`kosh temp[temp]`,
`kosh temp[kosh_gan(temp)]`) or an unknown node. The declaration is
hoisted only if `r172_esc == 0` and `r172_cnt != 0` (`:10984-10988`);
`kosh_ksham` is not in the seven-name whitelist (`.own`, `:11298-11311`),
so reading the capacity escapes and declines the hoist.

### The size is evaluated once per pass, used only once

The declaration statement still runs every pass. `.gs_decl_kosh`
(`:19801-19891`) evaluates the size into `rax` on every pass (`call
gen_expr`, `:19812`) and runs the R128 cap check every pass
(`:19830`), so a later pass whose `n` is over-large still refuses even
though the value is then discarded. Only at `:19831` does the hoist
branch: `r172_decl_begin` (`:11049-11090`) on the reuse path overwrites
the fresh capacity with the old descriptor and jumps past the whole
allocation. `[rcx-8]` (capacity) is never compared with or updated from
the new `rax`. First pass fixes the capacity; later passes re-evaluate
`n` and throw it away. That is sound because a declared capacity is
only an initial hint — length starts at 0, elements arrive through
`kosh_kship`, and growth supplies whatever later passes need. A mala
differs: `r173_mala_begin` (`:11091-11133`) compares the new length
against the stored one every pass and takes the fresh path when it
differs — a mala's size IS used every pass; a kosh's is not.

### Growth across passes: the grown buffer is kept, only the length resets

Growth is the ordinary `kosh_kship` path, untouched by the hoist:
`newcap = cap ? cap*2 : 4` (`src/sutram_compiler.asm:23030`),
`r127_emit_grow` (`src/r65_arena.inc:579`). The region path is taken
when the new elements reach 64 KiB (`R127_BIG equ 65536`, `:571`); the
region is `max(2 * new, R101A_REGION)` with `R101A_REGION equ
0x04000000` — 64 MiB per kosh (`src/sutram_compiler.asm:9130`). The
descriptor never moves; growth updates `[d]`, `[d-8]`, `[d+8]`
(`:718`). An old region is given back (`munmap`) only when the SAME
kosh moves to new elements. Nothing is ever freed at pass end ("Memory
from the arena is never reused", `src/r65_arena.inc:23`), so a fresh
kosh per pass keeps its region; a hoisted kosh keeps exactly one.

Reuse resets only the length: `mov qword [rcx-16],0` (`:11066`;
descriptor `[d-16]` length, `[d-8]` capacity, `[d]` elements, `[d+8]`
region size, `src/sutram_compiler.asm:572-574`). Capacity, elements
pointer and region size are untouched; nothing is zeroed ("nothing is
zeroed, because nothing past the length can be read", header comment
`:10880-10886`). A mala reuse instead zeroes all N elements via `rep
stosq` (`:11121`).

### The gate

`tests/r172/test_chakra_kosh.py:55-56` on v319:

- `region`: "grown to 4,097 every pass (a region: one, kept, not one a
  pass)", expected made once.
- `capacity`: "a declared capacity that changes every pass", expected
  made once, `kosh k[j]` with one push per pass, sum 230.

Part 1 compiles each case with 1 pass and with 20 passes and asserts
20 passes hold exactly what 1 pass holds (`parimana()` equality,
`:200-203`). The redzone phase (`:160`) grows to 20,000,000 elements in
each of three passes and expects a single region and `moved 0`. Scope
note, honestly: the gate's `capacity` case varies capacity via the loop
variable `j` itself, with one push per pass and no growth to a region.
It does NOT contain a computed-local form (`vitti n = ...; kosh
temp[n]`) or a grown-across-passes form. Those follow from the same code
path by reading (§2–§4 above), but the gate does not execute them — the
program below is the case that would.

### The demonstrator program (written out, NOT run)

```sutram
mukhya() {
    vitti s = 0
    chakra i = 1 tak 20 {
        vitti n = i * 10
        kosh temp[n]
        chakra j = 1 tak 20000 {
            kosh_kship(temp, j)
        }
        s = s + temp[0] + kosh_gan(temp)
    }
    likha(s, " ", parimana(), "\n")
}
```

Each pass `temp[0]` is 1 and `kosh_gan(temp)` is 20000, so `s` is `20 *
20001 = 400020` with or without the hoist. Trace: pass 1 doubles from
`n = 10` (20, 40, …, 10240, 20480); the doubling step whose new elements
first reach 64 KiB takes the 64 MiB region, and 20480 × 8 B = 160 KiB
fits in it. Passes 2–20 reset only the length to 0 and refill to 20000,
which fits in 20480 — no growth, no new allocation, no new region.

Peak memory (address space; regions are `mmap(..., NORESERVE)`
reservations, so only touched pages cost commit):

| | regions | arena | total |
|---|---|---|---|
| WITHOUT the hoist (20 fresh koshes) | 20 × 64 MiB = 1280 MiB | ~3.1 MiB | ≈ 1283 MiB |
| WITH the hoist (one kosh) | 1 × 64 MiB = 64 MiB | ~160 KiB | ≈ 64.2 MiB |

Saving: ≈ 1216 MiB of region reservations, plus ~3 MiB of arena.
(With the R82 header the descriptors are 56 B instead of 32 B: 1120 B
vs 56 B — negligible against the regions.) Precision notes: the gate's
witness `parimana()` counts capacity bytes for a region, not the full
reservation, so in `parimana()` terms the same program shows roughly
20 × ~230 KiB without the hoist against ~230 KiB with it — the same
20:1 ratio, in KiB rather than MiB. And the saving needs the growth to
go past the declared cap: if the inner loop ran only to `n` (declared
cap covering the final size), no pass would take a region at all and the
hoist would save nothing — a different program, not a defect in this
one.

**Task 1 verdict: CONFIRMED.** No size-form check exists anywhere in
the candidacy path, the gate already asserts the runtime-capacity case
(`kosh k[j]`, changing every pass, made once), and the reading extends
it to a computed `n` and to growth across passes, where reuse resets
only the length and doubling growth supplies whatever later passes
need.

---

## Task 2 — a block returning memory to the OS: CLOSE IT, zero of 347

### (1) What the compiler knows at a block's exit, and where

Almost nothing. A block exit is an `AST_REWIND` node, and the node
carries exactly one thing: the mark name
(`AST_REWIND equ 51`, `src/sutram_compiler.asm:119`; builder
`r73_rewind_node`, `:8406`). No size, no loop flag, no iteration count,
no "will run again" bit. The emitter is correspondingly bare:
`r73_gen_rewind` (`src/r65_arena.inc:404`) loads the mark and stores it
to `[end]` — that is the whole rewind. `r73_gen_ret_rewind` (`:535`)
does the same on a `nivartanam` from inside a block. All exits funnel
through exactly these two routines: block end and `krama`/`agrim`
leaving blocks via `gen_stmt` dispatching `AST_REWIND`
(`src/sutram_compiler.asm:18992-18995`, jumps wrapped at parse time by
`r73_wrap_jump`, `:8438`); return from inside a block via two call
sites (`:21001`, `:21023`), the rewind target fixed at parse time by
`r73_ret_mark` (`:8422`). The only per-exit fact available at runtime
is the mark and `end` themselves. The span `mark − end` is computable
at an exit (two global loads and a subtract). Whether the block will
run again is not, as the three cases show.

- **Loop body:** parse time does track loop nesting
  (`r73_loop_enter` / `r73_loop_leave`, `:8462` / `:8484`; counters
  `r73_loopn` / `r73_loopbase`, `:1685-1687`), bracketing every loop
  form. But that knowledge is never carried into the AST — the rewind
  node has no field for it, and the loop emitters emit the body through
  `gen_block` without passing loop context to the rewind. And the fact
  itself is insufficient in both directions: in a loop does not mean
  will run again (condition may fail, `krama` may break, bound may be
  1); not in a loop does not mean runs once (see below).
- **Function body:** each function resets the slate
  (`r73_func_enter`, `:12371`), so a block in a function body has
  `loopn == loopbase` — "not in a loop of this function". What the
  compiler never has is a call graph or a call count. The corpus
  supplies the counterexample: `examples/268_r73_return_value.sm`
  calls `varga_yoga` once with `n = 10` and then 1,000,000 times with
  `n = 4` in a loop. The mandapa is in the function body, not in any
  loop, yet its exit runs 1,000,001 times. Giving the pages back at
  that exit would pay the re-fault cost a million times for an 80-byte
  block. Recursion is the same story.
- **Top level:** `mukhya` runs once as a program, but a mandapa at top
  level can still sit inside a loop:
  `examples/304_r103_parimita_within.sm` puts a mandapa inside a
  `yavat` loop of 1,000,000 passes at top level. Top level is not a
  "runs once" signal either.

Net: the only recurrence fact the compiler possesses is the lexical
in-a-loop bit at parse time, and it is (a) unrecorded in the AST, so
the rewind emitters cannot see it without new AST state, and (b) wrong
in both directions as a predictor. There is no correct "will run again"
bit anywhere in the compiler; producing one would need a call graph
plus loop-trip reasoning the compiler has never had.

### (2) Could the caller decide? What it would look like, and what it costs

Today the language has no way to say it. `r72_parse_mandapa`
(`src/sutram_compiler.asm:8338`) accepts an optional `parimita N`
budget and then a body — nothing else. The cheapest correct vehicle
reuses the `parimita` precedent: `parimita` is not a keyword — it is a
plain identifier matched by `strcmp` in `r103_parse_budget` (`:8933`),
which also shows the disambiguation pattern (a variable named
`parimita` followed by `=` or a delimiter is not the budget). A caller
word in the same position — e.g. `mandapa parityajya { ... }` — would
cost one `strcmp` branch setting one flag bit for the block, one branch
in each of the two rewind emitters to emit the give-back for the range
`[end, mark)` when the flag is set, plus reference text and gate
coverage. No lexer change, no new keyword number. It is also the only
honest shape: the programmer is the one party who knows the block is
done, so the decision belongs in the source, not in the compiler.

A builtin would cost more machinery and be the wrong shape: a `BN_`
constant (next to `BN_PARIMANA equ 47`, `:244-246`), a name label
(`:1384-1397`), one row in `bn_table` (`:901-975`, lookup automatic
via `lookup_builtin`, `:32959`), a dispatch arm in `gen_expr`'s `BN_`
chain (e.g. near `:22087`) plus emitter, docs, and tests — and it
would still execute at a point in the body, not at block exit, so it
would have to set a flag the rewind reads, which is just the annotation
above with extra steps. A true keyword is most expensive of all (a
`KW_` number, Latin + Devanagari rows in `kw_table`, a `parse_stmt`
dispatch arm, language-pack entries, reference text). A pragma is not
a shape at all: no pragma mechanism exists anywhere in the lexer or
parser. An annotation with no program behind it is a feature with no
users, which is what §3 measures.

### (3) The decisive measurement: zero of 347

Method: counted `.sm` files twice — **331 at the top level, 347
recursively** (the extra 16 live in subdirectories `r67`, `r68`,
`r68/pairs`, `r71`; `examples/lib` holds `.smlib`, not `.sm`). The
brief's "331" is the top-level count; all 347 were counted. Extraction
over all 347 files, comments stripped before matching: every
`nirmmita(...)` call site (**78**; a plain grep returns 91 lines
because it also matches comment mentions, `nirmmita(` returns 82 of
which 4 are comment-only), every `kosh name[N]` / `mala name[N]`
declaration (**69**), every `mandapa` block. Constant arguments were
evaluated (`512 * 8` = 4096, etc.); the four non-constant sites were
bounded individually by reading. Element size is 8 bytes (kosh growth
multiplies capacity by 8, `src/r65_arena.inc:70-77`). Cross-checks:
every numeric literal ≥ 16,777,216 in the corpus was listed and
checked for an allocation context — all are arithmetic or
literal-boundary tests, none is a size. The longest string literal is
304 chars (`examples/345_r116_long_literal.sm`); literals live in the
binary, not the arena. All 22 files containing a real `mandapa` block
were read in full (a 23rd, `examples/307_r105_string_join.sm`,
mentions the word only in a comment).

Results. Largest allocations anywhere: largest constant `nirmmita`
**4,096 bytes** (`examples/215_r12_wordfreq.sm:38`,
`nirmmita(512 * 8)`), outside any block; largest kosh/mala declaration
**10 elements = 80 bytes** (`mala a[10]`); largest kosh grown by
pushes 1,000 elements = 8,000 bytes (`317`), outside any block. The
four non-constant sites: three `nirmmita(n * 8)` and one `mala a[n +
1]`, bounded by reading to at most 80 bytes (`268`: `n = 10` then `n =
4`; `269`: `n = 4`; `75`: `n = 4`).

Largest allocations **inside** a mandapa block: largest single in-block
`nirmmita` **1,000 bytes** (`examples/317_r107_parimana.sm:10`,
`nirmmita(1000)`). Next: 128 (`264`), 100 (`318`), 96 (`282`, `304`).
Largest in-block data-dependent `nirmmita`: 80 bytes (`268`, `n * 8`).
No `mala` is declared inside any mandapa in the corpus. Key correction:
a kosh in a block does **not** use scratch — `r108_kosh_alloc`
(`src/sutram_compiler.asm:12655`) keeps it in its own region, so
in-block kosh sizes do not count toward the block's scratch span at
all (largest in-block kosh growth is 100 elements = 800 bytes of
elements in its own region, `286`). A `mala` declaration allocates
through the persistent `nirmmita` path
(`emit_nirmmita_from_rax`, `:19422`), not the scratch side, so it
would not be reclaimed by a block-exit give-back either.

The near-miss, stated honestly: `examples/303_r103_parimita_refuses.sm`
runs `nirmmita(64)` in a 1,000,000-iteration loop inside a single block
— 64 MB of scratch if it ran free. It does not run free: the block
carries a `parimita` budget of 1,048,576 bytes, and
`r103_emit_budget_checks` (`:9011`) refuses the `nirmmita` that would
pass the budget before the memory is stored (`src/r65_arena.inc:438`,
before the store at `:440`). The block never holds more than 1 MiB,
and the program exits 1 with `E_PARIMITA`. It is a refusal test, not a
64 MB allocation, and counting it as ">16 MiB in a block" would be
wrong. The same holds in the other direction for `304`: its block sits
inside a million-pass loop, but the block exits every pass, so its peak
is one pass's 64 bytes.

**The count: zero of 347 examples allocate more than 16 MiB inside a
block** — by single allocation, by block total, and by any boundable
data-dependent size. The largest block allocation found is 1,000
bytes, about 16,000× below the 16 MiB threshold; the largest any block
is ever allowed to hold is the 1 MiB budget cap in the `303` refusal
test, 16× below it. What the method could miss: (a) a data-dependent
size whose bound is not visible in the example — only 4 non-constant
sites exist and all 4 are bounded above by reading; (b) kosh growth
through a called function in a loop — irrelevant to the scratch count,
since a block kosh does not use scratch; (c) string concatenation
inside a block — not exhaustively traced across all 347 files, but
bounded by its inputs, the longest literal is 304 chars, and all 22
block files were read in full and none concatenates in a loop; (d)
recursion depth times per-call block size — no example nests mandapa
blocks recursively, deepest nesting is 2 (`304`, inner blocks of 96
bytes). None of these can plausibly bridge four orders of magnitude.

### (4) Verdict, the three primitives, and the other shapes

**Close the item: 0 of 347.** No program in the corpus would benefit,
no program is within two orders of magnitude of the threshold even
counting the refusal-test cap, and no compiler-known signal exists for
when a block will run again. This is a feature nobody needs. Close it
with the number.

- **`madvise(MADV_DONTNEED)`** is the only one of the three that fits
  the arena: the range `[end, mark)` stays mapped inside the single 1
  GiB reservation, the pages are dropped, and the next touch re-faults
  them zeroed — which is what the scratch allocator wants, since
  `r73_gen_scratch_nirm` (`src/r65_arena.inc:423`) zeroes the block
  anyway. But it exists nowhere on this tip: zero hits for `madvise`
  in `src/` and `win/`. The only numbers are R179's, measured on a
  harness making the field's own mapping calls, not on a compiled
  Sutram program (256 MiB, 274,880 KB → 12,736 KB; a 16 MiB block in a
  loop, 0.95 ms a pass kept vs 7.2 ms a pass discarded, ~1.5 µs a
  page). Those numbers are the reason a flat threshold is the wrong
  shape, and they are not a built feature.
- **`munmap` does not fit the arena.** It would unmap a subrange of the
  single 1 GiB mapping, and the next scratch allocation has no re-map
  path: `r73_gen_scratch_nirm` only checks room against `end`/`cur`
  and fails with the arena-full message if the range is gone. `munmap`
  is the right tool for whole reservations — which is why the kosh
  growth path uses it (commented at `src/r65_arena.inc:567`; on
  Windows, `VirtualFree` / `MEM_RELEASE` for a whole kosh region,
  `win/winrt_blob.asm:183-191`) — not for a subrange of the arena.
- **Windows has neither primitive on this tip.** No `MEM_RESET` and no
  `MEM_DECOMMIT` anywhere; the only give-back is the whole-region
  `VirtualFree` above. The arena on Windows is `MEM_RESERVE`-only: the
  `.alloc` path (`win/winrt_blob.asm:168-182`) selects `MEM_RESERVE`
  (`0x2000`) when the `0x4000` `NORESERVE` flag is present, and `rt_veh`
  (`:257`) commits 64 KiB on first touch. Note the header comment at
  `src/r65_arena.inc:5` says the opposite — that PE commits the whole
  arena — but on this tip the code says reserve-only plus lazy commit,
  and the code is what runs. Consequence: `MEM_RESET`, which acts on
  committed pages, is the wrong primitive for a mostly-reserved range;
  `MEM_DECOMMIT` is the closer analog (reservation kept, committed
  pages dropped, and `rt_veh`'s `State == MEM_RESERVE` check would
  recommit on next touch) — but that is a reading-based inference, not
  a verified fact, and Windows would need its own emitter branch and
  its own measurement; the Linux numbers do not transfer.

Alternative shapes, judged against the code: flat threshold — wrong
shape (R179) and dead code (zero examples cross any threshold in that
range); only-on-loop-exit — fails both ways (`268`: 1,000,000 calls of
a function-body block; a loop block may run exactly once), and the
parse-time in-a-loop bit is not even in the AST; above-a-size AND
outside-a-loop — inherits the failure of the "outside a loop" half,
and the conjunction is empty on the measured corpus; only-once-per-
program — backwards (the first exit of a loop-body block is the exit
most likely to be followed by another pass; for a function called a
million times "once" has no meaning), and needs per-block state;
runtime heuristic (counters, decay) — the compiler has no per-block
execution counters, no profiling, and no clock in generated code, and
adding a counter on every block entry would tax the hot path to serve
a case with zero examples; give-back at program exit — pointless, the
OS reclaims the whole mapping when the process exits. Only the caller
annotation is correct in principle, and it has no users: record that
design and revisit it only if a real program ever allocates a large
block once.

---

## Task 3 — the reference's file-reading section: 10 defects

### The section as found

There is no dedicated file-reading section. What a student reaching
for "how do I read a file" actually finds, scattered across
`docs/LANGUAGE-REFERENCE.md`:

- §4 builtin table, `:180-182`: three one-line rows for `dvaram`,
  `paadh`, `band` — the whole of the reference's documentation of
  open/read/close.
- §4, `:174`: one row for `dvaram_likha` (raw fd write). §4a, `:322-333`:
  a `dvaram_likha(1, "raw\n", 4)` example (a write to stdout, not to a
  file) plus one sentence naming the fd family.
- §4b standard-library table, `:367-380`: six modules, "60 functions
  across six modules" — `patra` is not among them. A `brihat`
  subsection follows at `:402-408`; `patra` gets no subsection, no `yoj
  patra`, no function listed.
- Status header `:10` and §3a contract table `:138`: the only two
  mentions of `patra_asti` in the whole document.
- §20, `:1525`: file builtins appear only as "files …" in the refused
  column of the `parikshita` table.

No example in the reference opens, reads, or closes a file, and no
example uses `yoj patra`.

### Defects

- **D1 — CRITICAL, wrong: `paadh` is called "open a file"; `dvaram`
  is not called open at all.** Reference `:181` — "`paadh` | open a
  file"; `:180` — "`dvaram` | patra descriptor helper". Source:
  `src/sutram_compiler.asm:198` (`BN_DVARAM equ 5`), `:199`
  (`BN_PAADH equ 6`); `:22701-22702` — "`dvaram(path, flags[,
  mode]) -> Linux sys_open result`" (sys_open = 2); `:22750-22751` —
  "`paadh(fd, buf, count) -> bytes_read (sys_read=0)`". What is true:
  `dvaram` opens, `paadh` reads. The R166 T4 finding is re-verified on
  this tip. Consequence, not just a label error: `paadh(path, buf, n)`
  with three arguments passes the parse-time arity check
  (`:17762`, via `r54_builtin_arity_ok`), so a program written by
  following the reference compiles — and then fails at run time (a
  read issued on a string pointer used as a file descriptor returns
  -1). The real opener is never identified as such anywhere in the
  reference.
- **D2 — Omission: `dvaram`'s signature, flags, mode, and return are
  never given.** Reference: no line gives `dvaram`'s arguments; `:180`
  is the only row. Source: `:285` (arity table: 2 or 3 arguments);
  `:22701-22745` (evaluate path, flags, optional mode; default mode
  0644 = 420 when the third argument is absent; effective bits honor
  umask); `docs/rounds/R52-BUILTIN-FIXES.md:13-24` (same, with
  examples); `lib/patra.smlib:20-23` (flags are Linux values:
  `O_RDONLY = 0`, `O_WRONLY|O_CREAT|O_TRUNC = 577`; created files get
  mode 0644 subject to umask; no Windows-host equivalence claimed for
  the flag values). What is true: `dvaram(path, flags[, mode])`
  returns a file descriptor, or a negative error (Linux: negative
  errno; Windows: -1 — `win/winrt_blob.asm:201-202`). A student cannot
  open a file for writing from the reference alone: no flag value
  appears anywhere in the reference, and nothing says the third
  argument is a creation mode.
- **D3 — Omission: `paadh` and `band` have no signature, no EOF rule,
  no error rule.** Reference `:181-182` give no arguments and no
  returns. Source: `:286` (`paadh` takes exactly 3); `:22750-22751`
  (`paadh(fd, buf, count)` → bytes read); `:288` (`band` takes
  exactly 1); `:22674-22700` (`band(fd)` → sys_close = 3, result in
  rax). What is true: `paadh` returns the byte count read, 0 at
  end-of-file, and a negative value on error; `band` returns the close
  result (0 on success). None of this — including the EOF rule, the
  single most basic fact about reading a file — is stated anywhere in
  the reference. The library states the EOF convention only in its own
  comment (`lib/patra.smlib:38-41`: `n == 0` ends the read loop).
- **D4 — Wrong: `grahan` is listed as part of the file-descriptor
  family.** Reference `:333` — "`dvaram` (an opening) is the fd
  family's word, with `dvaram`/`band`/`grahan`." Source:
  `src/sutram_compiler.asm:226` (`BN_GRAHAN equ 33`, "grahan = read
  number from stdin"); `:313` (arity table: 0 arguments);
  `:22610-22650` (reads stdin one byte at a time, returns the parsed
  number, -1 at end-of-file). What is true: `grahan` takes no argument
  and no file descriptor and cannot operate on one. The "dvaram (an
  opening)" half of the sentence is right; the family list is wrong.
- **D5 — Omission: the whole `patra` module is missing from the §4b
  library table.** Reference `:367-380` ("`lib/` ships:" — six
  modules; "60 functions across six modules"). No `patra` row, no `yoj
  patra`, no `patra_path_sarv`, `patra_likh_sarv`, or `patra_asti`.
  Source: `lib/patra.smlib:29` (`patra_path_sarv`), `:57`
  (`patra_likh_sarv`), `:81` (`patra_asti`) — exactly three functions;
  `src/r52_lib_index.inc:678-683` indexes all three under module
  `patra`, so `yoj patra` resolves them;
  `docs/sutram-stdlib-reference.html:736-748` lists all three with a
  `yoj patra` example. The table is also stale, not selective, for
  the modules it does list: `ganit` is "15" but defines 18
  (`lib/ganit.smlib:7-237`); `ganita` is "6" but defines 27; `shreni`
  is "11" but defines 14; `varna` is "13" but defines 27. Counted on
  this tip, `lib/` holds 24 modules and 310 `prakriya`, not six
  modules and 60 functions. (`docs/LIBRARY-BOUNDARY.md:3` agrees: 24
  modules. Its function count, 303, differs from this count by 7 — a
  counting-method difference, not checked further; either way the
  reference's "six / 60" is not the library.)
- **D6 — Misleading: `patra_asti` is described only as blocked, never
  as what it does today.** Reference `:10` — "`patra_asti` is blocked
  on an OS query the compiler does not make"; `:138` — "not changed
  in v296 — the contract needs a new operating-system query (R116
  report)". The `:10` sentence sits inside "Fifteen library contracts
  refuse instead of wrapping (v296, R116)", inviting the reading that
  `patra_asti` is one of the fifteen that refuse. Source:
  `lib/patra.smlib:81-86` — `patra_asti` opens the path read-only
  (`dvaram(path, 0)`); 1 if the open succeeds, 0 on any open failure.
  It does not refuse anything. No stat builtin exists: there is no
  `stat` identifier in `src/`, no `E_PATRA_PARIKSHA` string anywhere in
  `src/`, `tests/`, `lib/` or the reference, and no stat-query syscall
  emission. The intended contract is
  `ChatGPT-to-Sarvam/ROUND-189-IMPLEMENTATION-MATRIX.json` id 11 and
  `.../ROUND-189-SIXTEEN-CONTRACT-IMPLEMENTATION-SPEC.md:52`:
  followed-target existence via an OS metadata query — 1 on query
  success including directories, 0 only for absent target /
  non-directory component, fatal `E_PATRA_PARIKSHA` on permission
  denial, symlink loop, or I/O fault — with the explicit note "dvaram
  alone cannot implement the distinction". What is true, and what the
  reference never says: `patra_asti` is usable today, but it means
  "opens read-only", not "exists". Permission-denied returns 0 instead
  of refusing; a symlink loop returns 0 instead of refusing
  (probe-confirmed as `patra_asti(loop) = 0` in
  `Muse-to-Sarvam/ROUND-112-CONTRACT-AUDIT.md`); a dangling symlink
  returns 0 (matching the intended contract only by accident);
  opening a FIFO read-only blocks, because the flags pass straight
  through to `open(2)` and nothing warns about it. It also has no
  boundary test: `tests/r116/test_contracts.py` contains zero mentions
  of `patra`. The correct "opens read-only, not exists" meaning is
  written down — in `docs/RELEASE-NOTES.md:339-340` — but not in the
  reference, and the name itself (`asti` = is/exists) invites exactly
  the wrong reading the reference never corrects.
- **D7 — Omission: no path rule, no error model, no EOF/binary-vs-text
  statement.** Reference: nothing on any of these. Source: paths are
  NUL-terminated byte strings (`lib/patra.smlib:9-10`); `dvaram` passes
  the pointer straight to `open(2)` with no terminator handling
  (`src/sutram_compiler.asm:22711-22745`), so a buffer built without a
  0 terminator is a latent over-read. Data buffers are raw byte
  pointers with an explicit byte count, NOT qword-cell arrays
  (`lib/patra.smlib:11-12`). Error model: every `patra_*` function
  returns -1 on any OS error; `patra_asti` returns 0/1 and never -1
  (`lib/patra.smlib:14-15`). The descriptor is always closed before
  returning (`lib/patra.smlib:16-18`). Deliberately absent, so a
  student should not go looking: directories, permissions, seek,
  append, stat, locking (`docs/LIBRARY-BOUNDARY.md:14-16`). Binary vs
  text: there is no distinction and no translation on either platform
  — raw Linux syscalls on one side, direct `ReadFile`/`WriteFile` on
  the other (`win/winrt_blob.asm:103-144`). The reference states none
  of this.
- **D8 — Omission: the platform split for the file builtins is never
  stated.** Reference: nothing says the file builtins are Linux
  syscalls, or that the Windows mapping is partial. Source: Linux
  targets emit raw syscalls (`open` = 2, `read` = 0, `write` = 1,
  `close` = 3 — `src/sutram_compiler.asm:22701-22860`); Windows targets
  go through `rt_syscall` (`win/winrt_blob.asm:49-200`), which handles
  only syscall numbers 0, 1, 2, 3 (plus allocation/exit). Its `.open`
  (`:145-160`) looks at exactly one flag bit: bit 0 set means write
  access with create-always, otherwise read access with open-existing.
  The mode argument is ignored on Windows. `O_RDWR`, `O_APPEND`, and
  `O_CREAT` without write are not mapped; opening a directory fails on
  Windows (no backup-semantics flag), so `patra_asti` of an existing
  directory is 1 on Linux and 0 on Windows.
  `docs/RELEASE-NOTES.md:341-343` states this plainly ("File flags
  differ by platform… Flags beyond those the library uses are not
  mapped"); the reference does not. Mitigation: the two flag values the
  library actually uses (0 and 577) do work on both platforms, so the
  common path is fine — but anything beyond them silently differs, and
  the student is never told where the boundary is.
- **D9 — Library comment contradicts its own code and the reference
  (stale "3-arg `likha`").** Library: `lib/patra.smlib:4-5` — "via the
  file builtins `dvaram` (open), `paadh` (read), `likha` (3-arg write),
  `band` (close)." Source: the 3-argument raw write is `dvaram_likha`
  since v286 (`src/sutram_compiler.asm:22860-22861`); the library's own
  code calls `dvaram_likha` (`lib/patra.smlib:68`); the reference is
  right about this (`docs/LANGUAGE-REFERENCE.md:322`, `:335-338`). The
  same staleness appears in `docs/LIBRARY-BOUNDARY.md:14-16` ("over the
  `dvaram`/`paadh`/`likha`/`band` builtins"). Both should say
  `dvaram_likha`. The rest of the `patra.smlib` header checks out
  against the code: flags (`:20-23`), error contract (`:14-15`),
  loop/EOF/close (`:16-18`), per-function comments (`:25-28`, `:54-56`,
  `:78-80`). One further gap in the library comment:
  `patra_path_sarv` on a directory opens successfully and then its
  first read fails, so the function returns -1 — the comment (`:25-28`)
  does not mention directories at all.
- **D10 — No file-reading example exists in the reference.** The only
  file-related example is `dvaram_likha(1, "raw\n", 4)` (`:322-333`), a
  write to stdout. Nothing opens, reads, or closes a file; nothing
  uses `yoj patra`. Runnable file programs exist in the tree and are
  not cited — `tests/stdlib/file_read.sm` (read-back, small cap, cap 0,
  negative cap, missing file, `patra_asti` 1/0) and
  `tests/stdlib/file_write.sm` (write, read-back round-trip, 0-byte
  overwrite, negative count, unwritable path). No program under
  `examples/` calls `dvaram`, `paadh`, or `band` directly or uses `yoj
  patra` (the only `dvaram_likha` uses in `examples/` are stdout writes
  in `examples/215`, `217`, `347`).

### Verified correct

- `dvaram_likha(fd, buf, len)` returns the count written (`:174`,
  `:322-333`) — `src/sutram_compiler.asm:326` (arity exactly 3),
  `:22860-22861` (sys_write = 1, count left in rax). The
  `dvaram_likha(1, "raw\n", 4)` example's argument order matches the
  source, and fd 1 is stdout on both platforms (Windows special-cases
  1/2, `win/winrt_blob.asm:103-124`).
- The v285/v286/v287 history (`:335-338`): up to v285 a 3-argument
  `likha` wrote raw bytes; v286 refused that form (`E_LIKHA_TRAYA`);
  from v287 `likha` with three values prints three values. The code
  string still exists (`src/sutram_compiler.asm:503`), but the refusal
  itself is dead in v315 — `rfx_check_likha` returns immediately
  (`:8748-8749`, "R105: `likha(a, " ", b)` prints three values; no
  refusal"). The reference's history is accurate; it just describes a
  refusal that no longer exists in the compiler.
- `band` | "close a handle" (`:182`) — terse but true
  (`src/sutram_compiler.asm:22674-22700`, sys_close = 3).
- `grahan` | "read a number from input" (`:178`) — true
  (`src/sutram_compiler.asm:226`, `:22610-22650`); the row omits that
  it takes 0 arguments and returns -1 at end-of-file.
- The §4 header claim (`:156-158`) that the table holds "the actual
  builtin names the compiler accepts, taken from its table": the file
  names present are all real — `dvaram`, `paadh`, `band`,
  `dvaram_likha`, `grahan` are all in the name table
  (`src/sutram_compiler.asm:905-908`, `:933`, `:947`) — and no other
  file builtin exists in the compiler (full `bn_*` list, `:1380-1440`):
  there is no `stat`, `seek`, `eof`, or English `open`/`read`/`close`
  builtin. The table's names are right; its purposes (D1) and its
  coverage (D5) are where it fails.
- `dvaram_likha(dvara, smriti, sankhya)` in the §4c hint note
  (`:273-274`) matches the source's own parameter naming
  (`src/sutram_compiler.asm:245`, `:22861`).
- `patra_asti` "not changed in v296" (`:138`) is accurate — the R189
  contract was specified and not implemented; what it omits is D6.
- §20 `:1525` ("files …" refused in a `parikshita` function, with
  `E_APARIKSHITA_KARYA`) is accurate: the checked-function allowlist is
  exactly `likha`, `lkhb`, `likha_rup`, `grahan`, `nirmmita`
  (`src/sutram_compiler.asm:11457-11475`); `dvaram`, `paadh`, `band`,
  and `dvaram_likha` all hit the refusal path. (Adjacent, not a file
  defect: the same allowlist admits `lkhb`, which the §20 allowed row
  omits.)
- `lib/patra.smlib` per-function contracts check out against its code:
  `patra_path_sarv` (`:25-28` vs `:29-52`: negative cap → -1 without
  opening; 0 for empty file and for cap 0 on an existing file; -1 on
  any error; descriptor closed on every path);
  `patra_likh_sarv` (`:54-56` vs `:57-76`: create/truncate via
  `dvaram(p, 577)`; returns n; -1 on negative count without opening and
  on any error); `patra_asti` (`:78-80` vs `:81-86`: 1 iff the path
  opens read-only, 0 otherwise, never -1).
- The `brihat` subsection (`:402-408`) is the one library subsection
  that does what the `patra` subsection should do — it names the
  module, its representation, and its calling convention — which makes
  `patra`'s total absence from §4b a deliberate-looking gap rather than
  a house style.

**Task 3 verdict:** the file-reading section is not merely incomplete;
its one specific instruction is backwards. A student who follows it
will call the read builtin to open a file, will never be told the open
builtin's arguments, flags, or mode, will find no `patra` module and no
working read-a-file program, and will read `patra_asti`'s name as
"exists" while the reference says only that it is "blocked" — never
that it is usable today as an open attempt that conflates missing,
forbidden, and looping paths. The correct information exists in the tree
(the R52 fix note, the library's own comments, the release notes, the
HTML stdlib reference, the `tests/stdlib` programs), but none of it
reached the page a student actually reads. The section needs, at
minimum: the `dvaram`/`paadh` rows corrected and given their signatures
(D1–D3), a `patra` row in the §4b table with `yoj patra` and its three
functions plus one read-a-file example (D5, D10), the "opens read-only,
not exists" meaning of `patra_asti` with its conflations and the missing
stat contract stated plainly (D6), and the path, error, EOF, and
platform-boundary rules the library already documents (D7–D8).

---

## Brief corrections

1. **"Read the 331 examples" is the top-level count only.** The corpus
   is 331 `.sm` files at the top level of `examples/` and **347**
   recursively (16 more in `r67`, `r68`, `r68/pairs`, `r71`). The
   measurement was done over all 347. The answer the brief wants — a
   measured "zero of 331" — is **zero of 347**, which includes the
   331.
2. **"A loop body knows. A function body does not." is half-right.**
   The loop-body bit exists at parse time (`r73_loop_enter` /
   `r73_loop_leave`, `src/sutram_compiler.asm:8462` / `:8484`) but is
   never carried into the AST, and it is wrong in both directions as a
   predictor of "will run again". The function-body half understates
   the case: a function body can run a million times per program
   (`268_r73_return_value.sm` calls `varga_yoga` 1,000,000 times), so
   "not in a loop" is no signal at all.
3. **Shared state: "`vartani_grahan` reads a line … `nivesha_anta`
   ends the loop" is not in the provided v321 tree.** A whole-tree grep
   of the v321 branch finds zero hits for `vartani_grahan` or
   `nivesha_anta` in `src/` or `lib/` (or anywhere else in that tree).
   Either the work is not in that tree or it is still in flight — the
   brief's own plan says Claude has "the file example + two `grahan`
   bugs" in flight (R186) — so this is flagged, not refuted. The lexer
   half of the shared state IS present in v321: code-point reporting
   code at `src/sutram_compiler.asm:12259-12362`.
4. **The §4b table's staleness is wider than the file section.** The
   "six modules / 60 functions" inventory is wrong on both numbers
   (24 modules, 310 `prakriya` on this tip) and on four of the six
   module counts it does give (`ganit` 15 vs 18, `ganita` 6 vs 27,
   `shreni` 11 vs 14, `varna` 13 vs 27). This is the same class of
   defect R159 found in the un-totalled lists, in the table the
   reference audit is now reading.
5. **A header comment contradicts the code it heads.** `src/r65_arena.inc:5`
   says PE commits the whole arena; on this tip the Windows arena is
   `MEM_RESERVE`-only with lazy commit via `rt_veh`
   (`win/winrt_blob.asm:168-182`, `:257`). The code is what runs.
   (Found during Task 2; not a brief claim, but the same
   documentation-vs-code class as the Task 3 defects.)

## Could not determine

- Whether the `vartani_grahan` / text-reading work exists on a branch
  other than the provided v321 tree, or is still unbuilt (see brief
  correction 3).
- Whether Sarvam's false-claim count moved from 63 (R166 brief) to 64
  (this brief) because of a finding in R167/R168: neither brief states
  the count in a greppable form, so the step is unreconciled from the
  briefs available here.
- Whether the shared-state speed claims (identical to C unoptimised,
  4.4× slower than `gcc -O2`, 13× than `clang -O2` / Rust `-O3`, 17×
  than `gcc -O3 -march=native`, 30× faster compile than gcc, 372-byte
  executable) and "825 MB → 20 KB, three times faster" hold: they
  concern staged branches and measurements outside this round's trees
  and were not part of the tasks; nothing in this report confirms or
  denies them.
- Whether the `303` refusal-test cap (1 MiB) is the largest any block
  is ever allowed to hold in the corpus, as opposed to the largest
  found: the method read all 22 block files and bounded the four
  non-constant sites, but a `parimita` budget larger than 1 MiB in an
  unexamined corner (e.g. a budget set through a variable) was not
  exhaustively excluded. The gap to the 16 MiB threshold is 16× even
  on the cap, so this does not affect the verdict.
- Whether `MEM_DECOMMIT` would actually recommit on next touch through
  `rt_veh` on Windows: a reading-based inference from the `State ==
  MEM_RESERVE` check, not a verified fact; Windows would need its own
  emitter branch and its own measurement.
- The exact runtime behaviour of the Task 1 demonstrator program
  (written out, NOT run, by rule): the trace follows from reading the
  hoist, growth, and reset code, but no execution confirms the 400020
  sum or the 64.2 MiB / 1283 MiB peaks.
- Whether any gate outside `tests/expect/` asserts the 317/318
  `parimana()` values that implementation B of the floor would change
  (a Task 2-adjacent open item from R166, not re-checked here).

---

## Summary

Task 1 is CONFIRMED: `kosh temp[n]` with a data-dependent size is already hoisted — the candidacy check never looks at the size, the gate already asserts the changing-capacity case, and a grown-across-passes demonstrator would peak at about 64.2 MiB with the hoist against about 1283 MiB without it. Task 2 is CLOSED with a measured number: zero of 347 examples allocate more than 16 MiB inside a block (largest real block allocation 1,000 bytes), the compiler has no "will run again" signal anywhere, `madvise` is the only fitting primitive and exists nowhere in the compiler, and the only correct shape — a caller word after `mandapa` on the `parimita` pattern — has no users, so the design is recorded and the feature should not be built. Task 3 found 10 defects in the reference's file-reading section, headlined by the `dvaram`/`paadh` rows being swapped — the section's one specific instruction is backwards — with the `patra` module missing from the library table, `patra_asti` described only as "blocked" when it is usable today as an open-attempt, and no file-reading example anywhere in the reference, while every correct fact already exists elsewhere in the tree and never reached the page a student reads.

---

*Read-only round. Nothing compiled or run. The Task 1 demonstrator program
is written out, not run.*
