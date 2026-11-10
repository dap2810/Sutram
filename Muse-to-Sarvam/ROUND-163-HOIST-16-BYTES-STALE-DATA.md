# ROUND-163 — the hoist, audited; the 16 bytes, third time; the stale-data bug

**Base:** main at `2b70aa18` (compiler v315). **Hoisting code read on branch
`r172-chakra-kosh` @ `501d35fd`** (v317 staged on v316-ready `59d60353`, NOT merged).
**Read only. Nothing compiled or run.** **Deliver into:** `Muse-to-Sarvam/`

**Verdicts up front**

1. **Task 1 — the hoist is SOUND.** No breaking program was found. Audit 1 is
   answered: the per-pass reset touches **only `[d-16]` (length)** — capacity and
   elements pointer are untouched, so a `kosh` that grows keeps its grown buffer on
   the next pass. Audit 2 is caught twice over: `kosh_kship(matrix, row)` and
   `matrix[i] = row` are both refused at compile time (the scan flags them AND the
   `r126` doors refuse them), so the program never runs under the hoist. Audit 3's
   premise is answered, not confirmed: candidacy is direct statements only, but the
   scan walks into nested blocks — a `kosh` declared under a `yadi` or in a `mandapa`
   inside the loop is simply **not hoisted** (fail-closed), and the "leak" for it is
   the pre-existing per-pass allocation, unchanged. The test file covers growth
   (`grown`, `region`, redzones to 20,000,000 elements) but does NOT cover the
   container escape, growth on a later pass, a hoisted-but-nested use, FFI,
   recursion, a nested bare block, or `kosh_kship(k, k)`.
2. **Task 2 — the brief's premise is wrong: the answer exists, twice.** R161
   answered the 16 bytes and R162 re-verified them and answered the conditional.
   This is the third verification at this tip, no corrections. The extra 16 bytes
   are 24 bytes of R82 header minus 8 of alignment padding, and the header is **used**
   bookkeeping. On the brief's new angle — three no's: the 16 bytes are not
   bookkeeping the hoist cannot reach past (a hoisted `kosh` still carries the header,
   written once); the 48/64 split is not explained by the hoist's reach (it predates
   the hoist); nothing in the `mandapa` allocates bookkeeping per `kosh` per pass.
3. **Task 3 — the claim as stated is FALSE.** An ordinary `nirmmita` taken after a
   block has ended is **not** handed memory the block wrote — and the reason is not
   that the block's bytes are cleared, but that the post-block allocation never touches
   the block's addresses at all: a `nirmmita` outside any block takes the **persistent**
   path from the bottom of the arena, while the block wrote the **scratch** side near
   the top, and the persistent cursor only ever moves forward. A `nirmmita` inside a
   later block does reuse the first block's addresses — but its requested bytes are
   **zeroed at allocation time**, exactly as §19 promises. There IS a real defect
   underneath, and it is narrower: the scratch zeroing loop covers `ceil(size/8)*8`
   bytes of an `align16(size)` block, leaving an **8-byte alignment tail un-zeroed**
   when `size mod 16` is 1..8 — reachable only through unchecked out-of-bounds access,
   never by a legal in-bounds program. The one example in §4 needs an out-of-bounds
   write in block A; no legal program exhibits the bug.

---

## Task 1 — read the hoisting code

The code: state in `.bss` (`src/sutram_compiler.asm:1616-1623` at `501d35fd`):
`r172_decl resq 256` (kosh declarations made once for their chakra),
`r172_slot resq 256` (the frame slot holding each one's descriptor), `r172_n`,
`r172_name`, `r172_cnt`, `r172_esc` (1 = a use that is not proven local),
`r172_cur` (the slot of the kosh being declared, 0 if made every pass),
`r172_patch` (its jump over the allocation). Header comment (`:10870-10883`): "A
kosh declared as a statement of a chakra's own body, and used in the loop only in
ways that cannot make a second reference to it, is made once: the first pass
allocates it, every later pass finds its descriptor in a frame slot and sets its
length to 0. Descriptor, elements and (if it grew that far) region are the same
memory every pass; nothing is zeroed, because nothing past the length can be read."
"Proven local" is a whitelist (`r172_scan`), not an escape analysis. Routines:
`r172_for_enter` `:10894-10983`, `r172_slot_of` `:10987-11004`,
`r172_decl_begin` `:11006-11025`, `r172_decl_end` `:11026-11038`,
`r172_scan` `:11040-11230`, `r172_is_name` `:11231+`. Call sites:
`r172_for_enter` in `.gs_for` at `:20666`; `r172_decl_begin` / `r172_decl_end`
in the kosh decl codegen at `:19707` / `:19767`. Diff `59d60353..501d35fd`: 24
files, 740 insertions, 58 deletions; `src/sutram_compiler.asm` +388 lines
(version string v316 → v317, the new R172 state and routines, the three call-site
insertions); new test `tests/r172/test_chakra_kosh.py` (244 lines); a new gate
"R172 chakra kosh" in `tools/gates.sh` (+2 lines).

### Q1 — What is emitted at the top of each loop pass?

**Only `[d-16] = 0` (length). `[d-8]` (capacity) and `[d]` (elements pointer) are
NOT touched.** `r172_decl_begin` (`:11006-11025`) emits, after the capacity is in
`rax` and checked:

```
mov rcx,[rbp+slot] ; test rcx,rcx ; jz .fresh ; mov qword [rcx-16],0 ; mov rax,rcx ; jmp .have ; .fresh:
```

The byte sequence (from the `R172_EMIT` calls at `:11014-11020`): `0x48,0x8B` +
modrm (`mov rcx,[rbp+slot]`), `0x48,0x85,0xC9` (`test rcx,rcx`),
`0x0F,0x84,0x10,0x00,0x00,0x00` (`jz +0x10` — exact: 8 bytes
`mov [rcx-16],0` + 3 bytes `mov rax,rcx` + 5 bytes `jmp rel32` = 16),
`0x48,0xC7,0x41,0xF0,0x00,0x00,0x00,0x00` (`mov qword [rcx-16],0`),
`0x48,0x89,0xC8` (`mov rax,rcx`), `0xE9` + rel32 (`jmp .have`, patched by
`r172_decl_end` to after `mov [rbp+slot],rax`). The reset offset `[d-16]` is the
length in BOTH layouts (32-byte descriptor and 56-byte with R82: length at d-16,
capacity at d-8, elements at d, region size at d+8; the R82 words sit at
d-40/d-32/d-24, untouched). The slot-zeroing (`mov [rbp+slot],0`) is in the loop
prologue — `r172_for_enter` is called in `.gs_for` at `:20666`, before the entry
jump — executed once per loop entry, not per pass. There is no `goto` in the
language, so no path enters the loop skipping the prologue.

### Q2 — Does a kosh that grows re-allocate every pass?

**No. Pass 2 keeps the grown buffer — capacity and elements pointer intact, no
re-allocation.** Push handler (`:22840-22938`): `r8` = descriptor, `r9` = len
(`[d-16]`), `r10` = cap (`[d-8]`); `cmp r9,r10; jb .space` — if len < cap, jump to
the append path, no growth; else `newcap = cap ? cap*2 : 4`, then
`call r127_emit_grow` (`:22938`). A kosh grown to 100 on pass 1 (cap 128) takes
the append path for all 100 pushes on pass 2; `r127_emit_grow` is never called.
Growth path (`r127_emit_grow`, `src/r65_arena.inc:579-730`): if a region exists
and the new bytes fit it, grow in place (`mov [d-8],newcap`); if no region and the
new bytes are under `R127_BIG` (65536), `r65_emit_kosh_extend` (in place at the
arena cursor, or falls through); else `.move`: allocate a new backing store
(arena for small; `mmap` of `max(2*new_bytes, 64 MiB)` via `r101a_a1` for big),
copy elements one by one for `rcx < len` — only within the length — then if the
old `[d+8] != 0` release the old region (`munmap`, syscall 11), then write the
descriptor together: `mov [d],new_elements; mov [d-8],newcap;
mov [d+8],new_region_size`. Audit 1 is answered: the reset touches only the
length, and a growing kosh is the case the fix handles, not the case it fails on.

### Q3 — What decides that a kosh does not escape?

Three layers. The hoist's own check is the deciding one; the pre-existing doors
are a second, independent net. **The hoist code calls NO pre-existing check** — it
does not call `r108`, `r126`, `r127`, `r134`, the walk, or the taint check. It
relies on them only in the sense that programs the scan misses are still refused
by them at compile time.

**Layer 1 — the hoist's own whitelist (`r172_scan`, `:11040-11230`).**
`r172_for_enter` (`:10894-10983`) iterates ONLY the direct statements of the loop
body (body at `[rbx+32]`; if `AST_BLOCK`, its children; else the single statement).
For each `AST_DECL` with kind 2 or 3 (kosh / kosh dasham): sets `r172_name`,
`r172_cnt=0`, `r172_esc=0`, calls `r172_scan` on the whole `AST_FOR` (bounds and
body); hoists only if `r172_esc==0` AND `r172_cnt==1`. Then it appends a NEW
var-table entry under the hidden name `"0k172"` (`r172_hidden`, `:10985` — a name
no program can write, starts with `0`), bounded by `VAR_TABLE_CAP` (256) and
`FUNC_SPILL_BYTES - 16` (2048-16); stores decl+slot in `r172_decl`/`r172_slot`
at index `r172_n & 255`, increments `r172_n`, and emits
`mov qword [rbp+slot],0`.

`r172_scan` is a recursive whitelist walk. In the whole loop the name may appear
only as:

- the base of an index (`k[i]`, `k[i] = v`) — `AST_INDEX` (`:11088`): the base is
  a NAME POINTER (a string), never a node (construction `:18002-18020` confirms
  `[type][name_ptr][index_node]`), so `.one_16` scans only the index node. There
  is no index-base expression to hide a use in — `f(k)[0]` cannot parse.
- the first argument of `kosh_kship`/`kosh_yuj` (BN 37), `kosh_hri` (38),
  `kosh_gan` (39), `kosh_rikt` (42), `kosh_iksh` (44), `kosh_apanay` (45) —
  `.builtin` → `.own` (`:11177-11195`): skips arg0 IF it is an `AST_VAR`, scans
  the rest. `BN_KOSHCAP` (40, `kosh_ksham`) is NOT whitelisted, so
  `kosh_ksham(k)` → `.al0` scans arg0 → `.esc`.

Any other appearance sets `r172_esc=1` and the kosh is left alone (fail toward
leaking): `AST_VAR` of the name (`.var`, `:11104` — a right side
`vitti a = k`, an argument of a prakriya, a slice base, `nivartanam`, a second
declaration — all `.esc`); `AST_CALL` with a non-whitelisted builtin
(`.builtin` → `.al0` — all args scanned; arg count > 6 → `.esc`);
`AST_FUNCALL` (`.args` — all args scanned; a statement call and an expression
call produce the same `AST_FUNCALL` node, so the R162 statement-call seam does
not apply here); `AST_SLICE`, `AST_FIELD`, `AST_FUNCREF`, `AST_HANDLE`,
`AST_WRITEMEM`, `AST_VEC`, `AST_NISHKRIYA`, anything new → `.esc` (`:11103`);
`AST_DECL` (`.decl` — counts declarations of the name, `r172_cnt`; kind > 3 →
`.esc`; scans `[rbx+24]` (size/capacity); if kind ≤ 1 also scans `[rbx+16]`
(initializer) — a kosh has no initializer); `AST_FOR` (`.for` — a loop variable
of that name → `.esc`; scans start `[rbx+16]`, end `[rbx+24]`, body `[rbx+32]`,
`[rbx+40]`); `AST_BLOCK` (`.block` — scans all children; **there is no
`AST_MANDAPA` node type** — `r72_parse_mandapa` (`:8361`) builds a mandapa as an
`AST_BLOCK` with 3 children, so the scan DOES descend into a mandapa);
`AST_BINOP`, `AST_TERNARY`/`AST_IF`, `AST_WHILE`/`AST_DO_WHILE`/`AST_ASSIGN`,
`AST_RETURN`/`AST_ASSERT`/`AST_HALT`/`AST_PRASAR`. Ignored (leaves, cannot
contain a use): `AST_NUM`, `AST_FLOAT`, `AST_STR`, `AST_SCRCUR`, `AST_REWIND`,
`AST_BREAK`, `AST_CONTINUE`.

`r172_slot_of` (`:10987-11004`): lookup by decl pointer, scans at most
`min(r172_n, 256)` entries from the top, returns the slot (negative) or 0.
`var_cnt` resets per function (`:18461`, `:18863`), so at most 256 hoists per
function; the `& 255` wrap in `r172_for_enter` can only overwrite EARLIER
functions' entries — harmless, because lookup is by decl pointer and earlier
functions' code is already emitted. Within one function no two decls can collide
(each hoist appends a fresh var-table entry with a fresh stack offset; the shared
hidden name `"0k172"` is never looked up — `r172_slot_of` returns the stored slot
directly).

**Layer 2 — the pre-existing doors (not called by the hoist; an independent
net).** `r126_check_builtin` (`:29680`): for each argument that holds a kosh
(`r134_holds_kosh`), if it is NOT argument 0 → refused; if it IS argument 0, the
builtin id must be in `[BN_PANKTILEN (36), BN_KOSHDEQUEUE (45)]` excluding
`BN_SETCHAR` (41). Comment: "a kosh is the first argument of a kosh builtin,
nothing else." `r126_check_assign` (`:29624`): `.cell` branch (target
`AST_INDEX` or `AST_FIELD`) calls `r134_holds_kosh` on the value `[rbx+16]` → if
it holds a kosh → refused (`r126_d_cell`); the `.var` branch refuses a kosh into
a module-global variable (`r126_d_glob`); `.local` calls
`r127_check_slice_value` + `r126_value_kind` + `r126_bind`. `r134_holds_kosh`
(`:28796`): kinds 2, 3, 6 (kosh, float kosh, mixed) via `r126_is_kosh_value`
(`:28771`), or a slice of a kosh / slice name / vibhag parameter via
`r134_kosh_slice`. `r129_check_call` (slice + growth): a slice of the hoisted
kosh is excluded by the scan (`AST_SLICE` → `.esc`), so this door is never
reached for a hoisted kosh.

### Q4 — Does it catch the container escapes? (Audit 2)

**Yes — twice over. All three forms are caught by the scan AND refused by the
pre-existing doors, so the audit-2 program does not compile and `matrix[0][0]`
never prints under the hoist.** The brief's program:

```sm
kosh matrix[10]
chakra i = 1 tak 5 {
    kosh row[2]
    kosh_kship(row, i)
    kosh_kship(matrix, row)     // is this an escape of `row`?
}
```

- `kosh_kship(matrix, row)`: scan — `kosh_kship` is whitelisted (BN 37), `.own`
  skips arg0 (`matrix`, an `AST_VAR`) and scans arg1 (`row`, an `AST_VAR` of the
  name) → `.esc` → NOT hoisted. Door — `r126_check_builtin`: `row` is a kosh at
  arg index 1 → refused (`E_KOSH_DVARA`). The program does not compile.
- `matrix[i] = row`: scan — `AST_ASSIGN` → `.two_8_16` scans the value `row` →
  `.esc` → NOT hoisted. Door — `r126_check_assign` `.cell`:
  `r134_holds_kosh` on the value → refused. Does not compile.
- `kosh_kship(outer, inner)` where `inner` is a kosh: identical to the first
  form — arg1 `inner` scanned → `.esc`; `r126_check_builtin` refuses a kosh at
  arg index 1. Does not compile.

The brief's feared outcome (every pass reuses one descriptor, `matrix[0]`..
`matrix[4]` all point at it, every row silently becomes the last one) does not
occur, because the hoist never happens for these programs. Note the scan catches
them even without the doors: the scan is independent of `r108`/`r126`, so the
R162 statement-call seam (which is about `r108_check_call` having exactly one
call site, the expression form) does not apply here — a statement call and an
expression call produce the same `AST_FUNCALL` node and the scan's `.args`
handler scans all arguments either way.

### Q5 — Does the hoist walk into a `mandapa` or a `yadi` nested inside the `chakra` body?

**Candidacy is direct statements only; the SCAN walks into nested blocks. A kosh
declared under a `yadi` or in a `mandapa` inside the loop is NOT hoisted
(fail-closed); a kosh declared as a direct statement and USED inside a nested
`yadi`/`mandapa` IS hoisted (and that is correct).**

- `chakra { mandapa { kosh ... } }`: the mandapa is an `AST_BLOCK` child of the
  loop body, not a direct `AST_DECL` — `r172_for_enter` skips it, so the kosh is
  not a candidate. The scan would descend into it (`.block`), but candidacy never
  starts. Not hoisted. (Test case `mandapa-in-chakra` asserts made-every-pass.)
- `chakra { yadi ... { kosh ... } }`: the `yadi` is an `AST_IF` child of the body,
  not a direct `AST_DECL` — not a candidate. Not hoisted. (Test case `under-yadi`
  asserts made-every-pass.)
- `chakra { chakra { kosh ... } }` (nested loop): the inner loop is an `AST_FOR`
  child of the outer body — not a candidate for the OUTER loop. The INNER loop's
  own `r172_for_enter` (called when the inner loop is generated) finds the decl
  as a direct statement of the INNER body and hoists it for the inner loop: made
  once per entry to the inner loop, not once per program. (Test `NESTED` asserts
  (20,20), (20,1), (1,1) holdings.)
- A kosh declared in a prakriya called from inside the loop: the prakriya's body
  is not in the loop's AST at all — `r172_for_enter` never sees it, and the call
  itself (`AST_FUNCALL` → `.args`) scans all arguments, so passing the loop's
  kosh to the prakriya is `.esc`. Not hoisted. (Test case `to-prakriya` asserts
  made-every-pass even for a prakriya that only reads it.)
- A kosh declared as a direct statement and USED inside a nested `yadi`/`mandapa`:
  the scan descends (`.three` for `AST_IF`, `.block` for the mandapa-as-block)
  and the uses are whitelisted (index base, whitelisted builtins) — hoisted,
  correctly. The nested block cannot smuggle the kosh out: any escaping use
  inside it (a second name, a prakriya call, a slice) is `.esc`, and the
  mandapa's own rewind does not touch a persistent kosh.

Audit 3's premise is therefore answered, not confirmed: the pass DOES only check
direct statements for candidacy, but that is the safe direction — a nested
declaration is simply not hoisted, and the "leak" for it is the pre-existing
per-pass allocation, unchanged. The 48-vs-64-bytes figure is the R82 header
(R161 Task 2: 24 bytes of header minus 8 of alignment padding = 16; 48+16=64),
not a hoist effect.

### The breaking program

**None was found. The hoist is sound.** Every attack traced either escapes the
scan (fail-closed: not hoisted), is refused by a pre-existing door (does not
compile), or behaves identically with and without the hoist. The strongest
programs chased, and why each does NOT break:

1. **Audit 2 (strongest the brief names)** — the three container forms above. All
   caught twice over (scan `.esc` + `r126` refusal). Do not compile.
2. **Audit 1 (growth)** — a kosh grown to 100 every pass. Hoisted; pass 2 reuses
   the grown buffer (len < cap → `jb .space`, no growth). Correct. (Test's
   `grown` case; `region` grows to 4,097 every pass.)
3. **Growth on a LATER pass beyond the previous pass's capacity** (the strongest
   UNTESTED case — see below):
   ```sm
   chakra j = 1 tak 3 {
       kosh k[1]
       chakra i = 1 tak (j * 5000) {
           kosh_kship(k, i)
       }
       s = s + kosh_gan(k)
   }
   ```
   Hoisted. Pass 1: 5,000 pushes → cap 8,192, region R1. Pass 2: reset length 0;
   10,000 pushes → at len 8,192 grows to cap 16,384, new region R2, R1 `munmap`'d
   after the copy, descriptor updated. Pass 3: same again. Correct — the
   descriptor always points at the current region, and no one else can hold the
   old region's address (no aliasing path survives the scan + `r126`). Not a
   break, but the test file does not cover it.
4. **Nested loops hoisting different koshs** (the slot-sharing scare):
   ```sm
   chakra j = 1 tak 5 {
       kosh a[1]
       chakra i = 1 tak 5 {
           kosh b[1]
           kosh_kship(b, i)
           s = s + b[0]
       }
       kosh_kship(a, j)
       s = s + a[0]
   }
   ```
   Each hoist appends a NEW var-table entry with a fresh stack offset
   (`:10941-10955`) — the shared hidden name `"0k172"` is never looked up, so
   `a` and `b` have distinct slots, each zeroed by its own loop's prologue.
   Correct. The scare evaporates on reading.
5. **A kosh used as another kosh's capacity** (`kosh k[m[0]]`, `m` hoisted earlier
   in the body): the capacity expression is evaluated and the R128 cap check runs
   on EVERY pass, before the reset jump — identically with and without the hoist.
   On a later pass the capacity result is discarded (`.have` overwrites `rax`
   with the descriptor). A capacity that becomes huge on a later pass refuses,
   exactly as on v316 (fail-closed). Not a break.
6. **A kosh read through `parimana()`**: the hoist changes what `parimana()`
   reports on later passes (the grown capacity persists instead of a fresh
   declared capacity). That is the documented, intended effect of the fix — the
   test asserts it (`once` = `held[20]==held[1]`) — not a break. A program that
   BRANCHES on `parimana()` would behave differently from v316, but that is the
   fix working, and the docs describe it (reference §19 new paragraph;
   MEMORY-MODEL.md new bullet).

What soundness rests on, verified: (1) the per-pass reset touches only `[d-16]`
— verified, byte sequence quoted in Q1; (2) no in-language read reaches past the
length — verified for `k[i]`: the index codegen (`:22266-22341`) loads the
descriptor, calls `r128_emit_kosh_refresh` (re-reads length and elements after
the index expression is evaluated), then `emit_array_bounds_check`
(`:22341-22346`) against the freshly-read length before `shl rax,3; add rax,rcx;
mov rax,[rax]` — the stale elements past the reset length are unreachable
in-language; for the push path: `cmp r9,r10; jb .space` (len < cap appends, else
grows); (3) the growth path keeps the descriptor coherent — verified in
`r127_emit_grow`: the copy runs only to `len`, and `[d]`, `[d-8]`, `[d+8]` are
written together after the copy, with the old region released only after it; (4)
no aliasing path survives the scan + `r126` — verified (Q3, Q4); (5) each hoist
has its own slot, zeroed once per loop entry in the prologue — verified
(`:10941-10955`, `:20666`); (6) the scan descends into every node type that can
contain a use, and escapes on anything unknown — verified (all handlers read;
unknown → `.esc`).

### Test-file verification — `tests/r172/test_chakra_kosh.py` (244 lines)

**Part 1 — CASES** (each compiled twice, 1 pass and 20 passes; `parimana()` is the
witness; "once" = the 20-pass program holds exactly what the 1-pass program holds;
"every pass" = it holds more; each program also prints a sum right only if every
pass saw an empty kosh): Made once: `plain` (230), `dasham` (20), **`grown` (grown
to 100 every pass; 4000)**, **`region` (grown to 4,097 every pass — a region: one,
kept, not one a pass; 163880)**, `capacity` (a declared capacity that changes every
pass, `kosh k[j]`; 230), `agrim` (agrim after the declaration; 230), `builtins`
(kosh_hri, kosh_iksh, kosh_apanay, kosh_rikt, kosh_shodh, kosh_yuj, `k[i] = v`;
20*14+210), `two` (two kosh in one body; 290), `in-prakriya` (the chakra is in a
prakriya; 230), `nivartanam` (nivartanam out of the loop with the kosh alive; 21),
`in-mandapa` (the chakra is inside a mandapa; 230). Made every pass: `alias`
(`vitti a = k`; 230), `to-prakriya` (given to a prakriya even one that only reads
it; 230), `slice` (a slice of it given to a prakriya; 230), `ksham`
(`kosh_ksham`: the capacity would show the reuse; 230), `under-yadi` (declared
under a yadi in the body; 230), `yavat` (a yavat loop, not a chakra; 230),
`mandapa-in-chakra` (declared in a mandapa inside the chakra; 230). Nested: the
inner loop's kosh is made once for each entry to the inner loop (20), not 400
times — checks (20,20), (20,1), (1,1) `parimana()` holdings.

**Part 2 — redzones** (the design's own test): 64 bytes of `0xDEADBEEFCAFEBABE`
immediately before the descriptor's first word (d-16) and immediately after its
first allocation, then 1,000,000 passes, nested chakra, a chakra in a mandapa,
growth to 20,000,000 elements in each of three passes; after each phase every
redzone word is read back and d-16 (length), d-8 (capacity), d (elements), d+8
(region size) are compared with exact values; phases p1 (1,000,000 passes, 1
push), p2 (1,000 passes, 5 pushes, plus a second inner loop with its own kosh),
p3 (only when off=3: 100,000 passes inside a mandapa), p4 (3 passes, growth to
20,000,000). Two redzone runs: off=0 (32-byte descriptor) and off=3 (56-byte
descriptor, R82, chakra inside a mandapa). Checks: all phases `bad 0`, `moved 0`
(after pass 1 the elements never move). OOM: under RLIMIT_AS (1.2 GiB), growth to
20,000,000 is refused with `kosh vardhayitum smritih na labdha`, exit 1, after
phases 1 and 2 reported intact (Linux only).

**Audit 1 IS covered by the test file:** `grown` (100/pass), `region`
(4,097/pass), redzone p4 (20,000,000), and the redzone checks (d-8, d, d+8
compared with exact values; `moved 0`). The benchmark's narrowness (one element,
never grew) is real, but the test file does not share it.

**What the test file does NOT cover:**

1. **No container-escape case (Audit 2).** No program with
   `kosh_kship(matrix, row)`, `matrix[i] = row`, or `kosh_kship(outer, inner)`
   appears in CASES — not even as a refusal assertion. Those forms are refused by
   `r126` at compile time, so they cannot be "made every pass" cases; but the test
   never asserts the refusal either. The escape net for the brief's strongest
   audit is untested by the test file.
2. **No varying-push-count growth case.** `grown`/`region` push the SAME count every
   pass, so growth happens only on pass 1. A kosh that grows FURTHER on a later pass
   (past the previous pass's capacity — the region-move path, old region `munmap`'d,
   descriptor updated) is not exercised. This is the strongest untested case
   (program 3 above).
3. **No hoisted-but-nested-use case.** `under-yadi` and `mandapa-in-chakra` cover the
   NOT-hoisted declarations; no case covers a kosh declared as a direct statement and
   USED inside a nested `yadi` or `mandapa` (the hoisted path through nested blocks).
4. **No FFI case.** No foreign-function case at all.
5. **No recursion case.** No prakriya containing the loop called recursively (each
   activation's slot is distinct, but untested).
6. **No kosh declared in a nested bare block** (`chakra { { kosh ... } }`).
7. **No `kosh_kship(k, k)` self-push** (refused by `r126`, but not asserted as a
   refusal).

---

## Task 2 — and the 16 bytes

**The brief's premise is wrong: the answer exists, twice.** The brief says "Your
R161 was asked this and I do not have the answer." The answer DOES exist in the
outbox: R161 (`Muse-to-Sarvam/ROUND-161-REGION-16-BYTES-DEATH-KNOWLEDGE.md`,
Task 2, delivered commit `c2339a6e`) and R162
(`Muse-to-Sarvam/ROUND-162-FOUR-CONDITIONS-16-BYTES-SECTION-19.md`, Task 2,
delivered commit `19bbed6c`, which also answered the brief's conditional). This is
the **third verification**, at `2b70aa18`, and it adds the brief's new hoist angle.
Every line number and every arithmetic claim in R161 Task 2 and R162 Task 2
checks out at this tip — **no corrections**. (The code tree on main is unchanged
since the R161 base: `git diff --stat 27bed64a..2b70aa18 -- src/ win/ docs/
tools/ tests/` is empty; every cited site was still re-read at this tip.)

**The answer, in one sentence:** the extra 16 bytes are **24 bytes of R82 header
(line, liveness slot, generation) added to the one descriptor+elements
allocation, minus 8 bytes of alignment padding the plain allocation already
pays.**

**The allocation:** one ordinary persistent allocation, descriptor + first
elements together, made by `emit_nirmmita_from_rax` via `r101a_emit_kosh_alloc`
(`src/sutram_compiler.asm:9122`, `jmp emit_nirmmita_from_rax`). There is no second
allocation, no per-`kosh` runtime allocation from the block, and no arena slot.

**Re-verification at the tip (all at `2b70aa18`):**

- Size computation `:19311-19323`: `add rax,4`, R82 branch `add rax,7` (`:19318`),
  `shl rax,3` → (cap+4)×8 plain, (cap+7)×8 with R82 on. For `kosh temp[1]`
  (cap 1): 40 bytes plain, 64 bytes with R82 on.
- `r82_emit_kosh_header` (`:10850`; comment `:10847-10849`): writes [rax] line,
  [rax+8] slot address or 0, [rax+16] generation or 0, [rax+24] 0, [rax+32] cap,
  then `rax += 40`. Descriptor is **4 qwords / 32 bytes plain** (length at d-16,
  capacity at d-8, elements at d, region size at d+8) and **7 qwords / 56 bytes
  with R82** (the 3 extra qwords are line at d-40, liveness slot address at d-32,
  generation at d-24).
- Alignment `r65_emit_nirm` (`src/r65_arena.inc:245`, rule `cur = align16(cur +
  size)` at `:243`): kosh temp[1] align16(40) = **48** plain, align16(64) = **64**
  R82; mala m[8] align16(72) = **80**; at 800,000 passes: 38,400,000 / 51,200,000 /
  64,000,000 bytes — all reproduce exactly.
- Program-wide flag: `r82_note_kosh_decl` (`:10662`) sets `r82_on` (`:1713`) when
  any kosh is declared at `r72_mdepth > 0`; every kosh decl checks it (`:19318`,
  `:19335`) — one kosh in a `mandapa` makes *every* kosh 56-byte-headed. The
  depth that matters is **mandapa** depth only: a kosh in a `chakra` body with no
  `mandapa` does **not** set it.
- The reader: `r82_emit_check` (`:11009`), emitted by `r82_param_checks`
  (`:10975`, called from `gen_all_functions` `:18714`), reads all three words via
  `r82_c1`–`r82_c5` (`:455-459`): slot address [d-32] (`r82_c2`, the "is this a
  block kosh" test and the pointer the check dereferences), generation [d-24]
  (`r82_c4`, compared against the live slot), line [d-40] (`r82_c5`, printed in
  the `E_KOSH_MANDAPA` message on the stale path). **Verdict on the brief's
  conditional: not a defect of that kind — used bookkeeping.** Honest
  qualification: the flag is program-wide, so koshes that never enter a block
  also pay the 24 raw bytes; the line for that overbreadth is the flag itself,
  `r82_on resq 1` (`:1713`).
- Block entry `r82_block_enter` (`:10703`): one stack slot per mandapa depth
  (`stack_dep += 8`) plus an `rdtsc` generation — no heap, no per-kosh allocation.
  Block exit `r82_block_leave` (`:10799`): drops the `r108_bk_*` record, zeroes
  the liveness slot, decrements `r82_gdepth`. Stale comment at `:19331` ("a slot
  of the block's arena") is wrong on both halves; `r108_kosh_alloc`'s own comment
  (`:12651-12654`, "No arena slot") is right.

### The hoist angle — three no's, each with its line

**(a) No — the 16 bytes are not bookkeeping the hoist cannot reach past.** On the
branch (`501d35fd`), the hoisted declaration goes through the identical
declaration path: the decl site (`:19707`) calls `r172_decl_begin` before the
size computation, and the size computation is unchanged — `add rax,4` (`:19710`),
the R82 branch `add rax,7` (`:19717`), `shl rax,3` — then
`call r108_kosh_alloc` (same stale comment), then the R82 branch
`call r82_emit_kosh_header`, then `r127_dk`, then `call r172_decl_end`, which
stores the descriptor in the frame slot. **A hoisted `kosh` still carries the R82
header, written once.** On later passes `r172_decl_begin` (`:11008`) emits only
`mov qword [rcx-16],0` — the length word only; the header words at d-40/d-32/d-24
are never touched by the reset. The R172 header comment (`:10870-10880`) states
it: "Descriptor, elements and (if it grew that far) region are the same memory
every pass… The descriptor's layout is unchanged."

**(b) No — the 48/64 split is not explained by the hoist not reaching past a
mandapa.** The split **predates the hoist**: it is present on main v315, where
there is no hoist at all. If the hoist reached past the mandapa and hoisted the
kosh, the per-pass cost would be 0 for both — the 16-byte difference would vanish,
not be explained. (Side note, verified from the code: `r172_for_enter` (`:10896`)
collects candidates from the body's direct statements only, so a kosh inside a
nested `mandapa`/`yadi` is not a hoist candidate — but that determines whether the
per-pass cost is 0 or 48/64, not the 16-byte difference. The walk-scope question
itself is Task 1's audit 3.)

**(c) No — nothing in the `mandapa` allocates bookkeeping per `kosh` per pass.**
The only per-`kosh` allocation is the single descriptor+elements allocation at
declaration. Block entry adds one stack slot per mandapa depth (not per kosh, not
heap) and a runtime `rdtsc` store into it; the mark (`0mNN`) is one hidden
stack-slot local per depth. The per-pass 48-vs-64 difference is a *size*
difference of the one allocation, not a second allocation and not a per-pass
charge.

Branch line numbers (R82 code identical, lines shifted by the R172 insertions):
`r82_c1`–`c5` `:455-459` (unchanged), `r82_on` `:1728`, `r82_note_kosh_decl`
`:10685`, `r82_block_enter` `:10726`, `r82_block_leave` `:10822`,
`r82_emit_kosh_header` `:11248`, `r82_emit_check` `:11407`, `r82_param_checks`
`:11373` (caller `:19112`), decl size computation `:19710-19722`; R172 sites:
header comment `:10870-10880`, `r172_for_enter` `:10896`, `r172_decl_begin` /
`r172_decl_end` `:11008` / `:11034`, `r172_scan` `:11048`.

---

## Task 3 — and the stale-data bug

**The claim as stated is false.** An ordinary `nirmmita` taken after a block has
ended is *not* handed memory the block wrote — and the reason is not that the
block's bytes are cleared, but that the post-block allocation never touches the
block's addresses at all. There IS a real defect underneath the claim, and it is
narrower: an 8-byte alignment tail. (All citations in this section at `2b70aa18`.)

### The arena geometry

One 1 GiB arena, `R65_ARENA equ 0x40000000` (`src/r65_arena.inc:49`). Three hidden
globals (`:50-52`): `0kshetra_cur` (persistent cursor, grows **up** from the arena
base), `0kshetra_end` (scratch cursor, grows **down** from base + 1 GiB),
`0kshetra_sima` (the range's true end). Header comment (`:9-46`): "Memory from the
arena is never reused, so it arrives zeroed like mmap memory" (persistent side),
and "a kosh growing on the persistent side can never extend into scratch memory".

**Correction to the task's framing:** a block does *not* write "from the entry mark
upward". The mark is the value of `end` at block entry (near the top of the arena),
and each scratch allocation moves `end` **down** by `align16(size)`, so the block
occupies `[mark − total, mark)` — *below* the mark, not above it.

### The persistent cursor never goes backward

`cur` is written in exactly four places, all forward-only: `r65_emit_nirm` reserve
(`src/r65_arena.inc:258`, `cur = base` on first use); `r65_emit_nirm` fast path
(`:274`, `cur = align16(cur + size)`); `r65_emit_kosh_extend` (`:319`, in-place
kosh growth); `r73_emit_reserve` (`:393`, reserve from the scratch side's entry
path). Every other `r65_idx_cur` use is a load (including `parimana()` at
`src/sutram_compiler.asm:23906`). **The persistent side never reuses memory.** A
post-block ordinary `nirmmita` therefore gets addresses no allocation has ever
held: fresh mmap pages, zeroed by the OS.

### Which path a post-block `nirmmita` takes

The parser rewrites `nirmmita` → `BN_NIRM_SCRATCH` only when written lexically
inside a `mandapa` (`r72_mdepth > 0`), at `src/sutram_compiler.asm:17781-17786`
(it also records the depth at `[rax+40]` and the budgets in force at `[rax+48]`).
The redirect is **lexical, not dynamic**: a `nirmmita` inside a `prakriya` called
from a block stays ordinary. Codegen dispatch (`:22088`): `BN_NIRMRITA` →
`.ge_call_nirm` (`:23681`) → `emit_nirmmita_from_rax` (`:26702`) →
`r65_emit_nirm` (`src/r65_arena.inc:245`): block = `cur`,
`cur = align16(cur + size)`, room checked against `end`; on first use the arena
is reserved (`cur = base`, `end = sima = base + 1 GiB`, `:258-263`); if the arena
is full it falls back to a fresh mmap per call (zeroed). **No zeroing is emitted —
none is needed, the memory was never used.** `BN_NIRM_SCRATCH` →
`.r73_ge_scratch` (`:23683`) → `r73_gen_scratch_nirm` (`src/r65_arena.inc:423`):
block = `end − align16(size)` (`:430`), `end = block` (`:440`), then the zeroing
loop (below). Except under `--fail-alloc` or non-ELF, where it falls back to the
ordinary path (`.r73_ge_plain`, `:23694`).

So a `nirmmita` written **outside any block, after a block has ended**, takes the
persistent path from `cur` (bottom of the arena). The block wrote scratch memory
near the top. The two sides meet only if ~1 GiB had been allocated persistently.
**The claim's mechanism — "a later ordinary `nirmmita` takes memory from the same
cursor position" — does not happen.** The brief's sentence "Deterministically. In
v315, today." is wrong about the mechanism it names.

### The scratch path does reuse the addresses — and zeroes them

`r73_gen_scratch_nirm` (`src/r65_arena.inc:423-470`) zeroes every successful
scratch allocation. The emitted template is `r73_s6` (`:346`):

```
lea rcx,[rsi+7] ; shr rcx,3 ; xor edx,edx
.z: mov qword [rax+rdx*8],0 ; inc rdx ; cmp rdx,rcx ; jb .z
```

where `rsi` is the requested size and `rax` is the block. It zeroes
`ceil(size/8)*8` bytes. (Side note: the header comment above
`r73_gen_scratch_nirm` still says `rep stosb` — stale; the template is the qword
loop. Either way the count below holds.) The zeroing dates from the original R73
commit (`7e6e4d30`, v269); "the block zeroed — a qword loop" was part of the
design from the start.

**The gap: the block spans `align16(size)` bytes, but the loop zeroes only
`ceil(size/8)*8`.** When `size mod 16` is 1..8, the last 8 bytes of the block are
never zeroed:

| size | block | zeroed | un-zeroed tail |
|------|-------|--------|----------------|
| 8    | 16    | 8      | `[8,16)`       |
| 17   | 32    | 24     | `[24,32)`      |
| 24   | 32    | 24     | `[24,32)`      |
| 64   | 64    | 64     | none           |

The tail is always **beyond the requested size** (`ceil(size/8)*8 >= size`), so any
read of it is definitionally out-of-bounds. The zeroing loop's size register `rsi`
survives the budget check: `r103_emit_budget_checks`
(`src/sutram_compiler.asm:9007`) states "rax and rsi survive on the .ok paths" and
pushes/pops them — no register bug there.

### What the reference promises, and what the code delivers

- `docs/LANGUAGE-REFERENCE.md:183`: "`nirmmita(n)` gives `n` **bytes**, zeroed".
- §19 (`:1302-1304`): "Each `nirmmita` inside takes memory from the scratch side
  of the program's 1 GiB field, **zeroed, like any `nirmmita` buffer**." And: "A
  later block reuses the same memory, and **sees zeros, never the earlier block's
  data**."
- `docs/MEMORY-MODEL.md:4-5`: "`nirmmita(n)` takes `n` zeroed bytes from an
  **arena**"; "The scratch side's pages are reused by the next block, not returned
  to the operating system."

For the **requested bytes**, the code delivers exactly what §19 promises: a later
block's scratch `nirmmita` reuses the addresses and reads zeros. The promise is
false only in the narrow sense that the 8-byte alignment tail is not zeroed — and
the tail is outside the requested bytes, so the promise holds for every in-bounds
read.

### What can and cannot read the tail

`r78_raw_len` (`src/sutram_compiler.asm:12249+`): for a name declared
`vitti p = nirmmita(CONST)` with a compile-time size and never reassigned, the
checked cells are `CONST >> 3` (whole cells, floor). A constant index past the end
is a compile error (`E_NIRMMITA_SEEMA`); a computed index gets a runtime bounds
check against the cells. The checked-readable region is `[0, floor(size/8)*8)`;
the zeroed region is `[0, ceil(size/8)*8)` — **the zeroing always covers the
checked-readable region**.

The tail is reachable only through the unchecked paths, which §6c
(`docs/LANGUAGE-REFERENCE.md:658-690`) names explicitly: a runtime size
(`nirmmita(n)`), a reassigned name (`p = p + 8`), an address computed from `p`, a
parameter, a `likh8`/`akshar_rakh` store. "Those are bare addresses: write past the
bytes you asked for and the program may go on, crash, or change another buffer —
exactly as in C." `akshar(p, i)` (`src/sutram_compiler.asm:24405`) is a raw byte
read with no bounds check.

**Consequence:** a legal program — every access within the requested size — can
never observe stale data from a `nirmmita`. The claim is false for every program
the reference calls correct, and true only for the 8-byte tail read through
unchecked access.

### Is it deterministic?

**Yes, for the tail read.** The addresses are fixed by the allocation order, the
sizes, and the 16-byte alignment — all deterministic for a given program. The
values at those offsets are whatever the program itself wrote there earlier (or
mmap zeros on first use). ASLR moves the arena **base**, not the **contents** at a
given offset: the value read from the tail does not depend on the base. Same
program, run twice, reads the same values — given the same allocation sequence.

What would have to vary for the outcome to vary: allocation order or sizes (a
different size shifts every later scratch address); an intervening allocation of
a different size (it reuses the same top addresses but with a different span);
a growth (a `kosh` growing in place moves `cur` forward; it cannot move `end`, so
it cannot shift the scratch addresses, but a kosh region allocation is a separate
mmap and does not touch the arena at all); a different code path (e.g.
`--fail-alloc`, or a non-ELF build, sends a scratch `nirmmita` down the ordinary
persistent path, where there is no reuse at all). Nothing in the mechanism reads
uninitialised memory whose contents vary run-to-run: the arena is fresh mmap
(zeroed), and the only un-zeroed bytes are the tails, whose contents are
determined by prior writes in the same program. For the natural (in-bounds)
program, the read is deterministically 0.

### Where a post-block `nirmmita` gets its memory, and does anything clear it?

**Ordinary post-block `nirmmita` (outside any block).** Routine: `r65_emit_nirm`,
`src/r65_arena.inc:245`. Called via `emit_nirmmita_from_rax`
(`src/sutram_compiler.asm:26702`) from `.ge_call_nirm` (`:23681`). Block = `cur`;
`cur = align16(cur + size)` (`:274`); room checked against `end`; first use
reserves the arena (`:258-263`); if full, a fresh mmap per call. **Nothing clears
anything** — nothing needs to, because the memory was never used before. There is
no zeroing, no unmapping, no overwriting between the block exit and this
allocation, because the allocation does not touch the block's addresses.

**Scratch post-block `nirmmita` (inside a later block).** Routine:
`r73_gen_scratch_nirm`, `src/r65_arena.inc:423`. Called from `.r73_ge_scratch`
(`src/sutram_compiler.asm:23683`). Block = `end − align16(size)` (`:430`);
`end = block` (`:440`); the block is zeroed by the `r73_s6` qword loop (`:441`,
template `:346`) over `ceil(size/8)*8` bytes. The 8-byte alignment tail, when
there is one, is **not** cleared.

**Block exit: the complete path inventory.** Every exit rewinds `end` to the entry
mark and **does nothing else** — no zeroing, no unmapping, no overwriting. The
bytes the block wrote stay in the arena (unreachable except via the tail).

- **End of body:** the `mandapa` is `AST_BLOCK [ vitti 0mNN = <scratch cursor> ;
  <body> ; <rewind to 0mNN> ]` (`src/sutram_compiler.asm:8323` comment; parse at
  `r72_parse_mandapa`, `:8338`). Entry stores the cursor in the hidden mark name
  `0mNN` via `r73_gen_scrcur` (`src/r65_arena.inc:365`, loads `[end]`). The
  `AST_REWIND` node (`r73_rewind_node`, `:8407`) is handled in `gen_stmt`
  (`:18992-18995`), which calls `r82_gen_rewind` then `r73_gen_rewind`.
- **`nivartanam` inside:** `r73_ret_mark` (`:8422`) records the **outermost**
  block's mark at `[rax+48]`; `r73_gen_ret_rewind` (`src/r65_arena.inc:535`,
  `end = mark`, preserving `rax`) is called at `:21001` and `:21023`.
- **`krama` / `agrim`:** `r73_wrap_jump` (`:8438`) wraps the jump in a
  `BLOCK [rewind, jump]`; called at `:15609` and `:15622`.
- **`prasar` failure:** `src/r25_phal.inc:202` calls `r73_gen_ret_rewind`
  ("inside a mandapa, rewind to the prakriya's outermost block first, as
  nivartanam does").
- **Runtime failures** (`E_PARIMITA`, `kshetra purnam`, bounds checks) exit the
  program — no further allocations, irrelevant.

`r73_gen_rewind` (`src/r65_arena.inc:404-415`) is exactly: evaluate the mark
expression, `mov [end],rax`. `r73_gen_ret_rewind` (`:535-555`) is exactly: push
the return value, `end = mark`, pop the return value. `r82_gen_rewind`
(`src/sutram_compiler.asm:10820-10845`) zeroes the R82 **liveness slots** for the
blocks being left — stack slots, not arena bytes. It does not touch the arena.

This matches §19 `:1304` ("Every exit gives it all back: reaching the end of the
body, `nivartanam`, `krama`, `agrim`, and a failure passed on by `prasar`") — all
five exit paths rewind, and none of them clears.

### The example

**First, the control: the program the brief implies reads 0.**

```sutram
mukhya() {
    mandapa {
        vitti a = nirmmita(24)
        a[0] = 10
        a[1] = 20
        a[2] = 30
    }
    mandapa {
        vitti b = nirmmita(24)
        likha(b[0])
        likha(b[1])
        likha(b[2])
    }
}
```

Trace, with `E` the entry mark (the value of `end` when the first block is
entered). Block A: `a` is at `[E−32, E)` (`align16(24) = 32`); the allocation
zeroes `[E−32, E−8)` (24 bytes). `a[0] = 10` lands at `[E−32, E−24)`,
`a[1] = 20` at `[E−24, E−16)`, `a[2] = 30` at `[E−16, E−8)` — all inside the
requested 24 bytes. The tail `[E−8, E)` is untouched (mmap zeros). Block A exits:
`end` is rewound to `E`. Block B: `b` is at `[E−32, E)` — the **same addresses**
— and the allocation zeroes `[E−32, E−8)`, wiping 10, 20, 30. `b[0]`, `b[1]`,
`b[2]` all read **0**. The student expects 0 (a fresh buffer, never written, and
the reference promises zeroed) and gets 0. This is a legal program (literal size
24, three cells, indices 0–2 in range and checked) and it refutes the claim: the
later block reuses the addresses and sees zeros, never the earlier block's data,
exactly as §19 `:1304` says.

**The one program that does read stale bytes.**

```sutram
mukhya() {
    vitti n = 24
    vitti m = 8
    mandapa {
        vitti a = nirmmita(n)
        a[0] = 10
        a[1] = 20
        a[2] = 30
        a[3] = 40
    }
    mandapa {
        vitti b = nirmmita(m)
        likha(b[1])
    }
}
```

Trace, same `E`. Block A: `a` is at `[E−32, E)`; the allocation zeroes
`[E−32, E−8)`. `a[0] = 10`, `a[1] = 20`, `a[2] = 30` land inside the requested
bytes. `a[3] = 40` lands at `[E−8, E)` — **the 8-byte alignment tail**, bytes
`[24,32)` of a 24-byte buffer. It compiles only because `n` is a runtime size, so
the `r78` check does not apply (§6c: a runtime size is unchecked). Block A exits:
`end` is rewound to `E`; the bytes `[E−8, E)` still hold 40 — nothing zeroes them
at exit. Block B: `b` is at `[E−16, E)`; the allocation zeroes `[E−16, E−8)`
(8 bytes) and **does not touch `[E−8, E)`**. `b[1]` is the 8 bytes at `[E−8, E)`
— **40**. `likha` prints **40**.

What the student expects: 0. `b` is a fresh `nirmmita(8)`, never written, and the
reference says `nirmmita` gives zeroed bytes. What comes out: 40 — a clean,
plausible-looking number (it is one of the numbers from the earlier block, but in
a buffer that should be all zeros). If the program summed the fresh buffer the sum
would be off by 40; if it tested a flag, the flag would read as set. No crash, no
garbage.

Why a student could plausibly write it: §6c's byte-vs-cell trap. `nirmmita(24)`
gives 24 **bytes**, not 24 numbers — it holds 3 cells. A student thinking in
numbers writes `a[3]` as "the fourth number", and the compiler does not refuse it
when the size is a runtime value (with literal sizes, `a[3]` on `nirmmita(24)` and
`b[1]` on `nirmmita(8)` are both compile errors, `E_NIRMMITA_SEEMA`). And
`nirmmita(8)` holds 1 cell, so `b[1]` looks like "the second number" of a fresh
buffer, expected 0. Both halves are the same beginner confusion, and both are
unchecked only because the sizes are variables rather than literals — `vitti n =
24` is the kind of naming a student does, and the sizes could equally come from
input.

Why they would not notice: the wrong value appears in block B, in a buffer the
student never wrote, in a different block from the mistake. Debugging block B
finds nothing wrong there; the cause is in block A, combined with the allocator's
un-zeroed tail. And the value is deterministic — same program, same 40 every run
— so it reproduces reliably and looks like a logic error in the student's own
code, not memory corruption.

**The honesty caveat, stated plainly:** this program *does* contain a student
mistake in block A — `a[3]` is out of bounds for a 24-byte buffer. The wrongness
in block B comes from reading the stale tail bytes, but the tail could only hold
40 because block A wrote out of bounds. A program with no out-of-bounds access
anywhere cannot observe stale data (proven above: the zeroing always covers the
checked-readable region, and any allocation whose requested span covers the tail
also zeroes it first, because the zeroed span always contains the requested
span). So the brief's claim, as a claim about ordinary student programs, is
false; the real defect is the 8-byte tail, and it is reachable only through
unchecked access. Reading a fresh `nirmmita` buffer before writing it *is* legal
— in-range reads are allowed and return the zeroed bytes — which is why the
control program above reads 0.

Two other constructs can read the tail, for the record: `akshar(p, i)`
(`src/sutram_compiler.asm:24405`), a raw byte read with no bounds check — a
student scanning a string byte-by-byte past its NUL would read tail bytes; and
`shabda(p)` on a string written to exactly fill the buffer with no NUL, whose
scan runs past the requested size into the tail (that one prints trailing garbage,
so it is noticeable, unlike the number above).

### Assessment of the proposed fix (ROUND-173 WS5)

The proposal: a dirty high-water mark, updated only at `mandapa` exit, so only
the overlapped dirty span is zeroed — "a 200 MB block followed by one
`nirmmita(64)` zeroes 64 bytes, not 200 MB".

**Is it right about the mechanism?** It targets the right cursor (the scratch
side, `end`) and the right event (`mandapa` exit, when the dirty span is known).
But it is aimed at a bug that does not exist in the form stated: the current code
already zeroes each scratch allocation's requested bytes at allocation time, so
for a `nirmmita(64)` after a 200 MB block the current code already zeroes exactly
64 bytes. The proposal zeroes the same 64 bytes. The saving is only against
zeroing the whole 200 MB span at exit — which nothing does today. The comparison
is against a strawman, not against the status quo.

Against the actual current code, the proposal's real difference is on **fresh**
addresses: the current code zeroes every scratch allocation unconditionally,
including ones on never-used addresses where the bytes are already mmap zeros. The
proposal would skip those (empty overlap) and zero only re-used addresses. That is
a genuine but marginal saving — the loop is ~4 ns per 64-byte block by the
`r73_s6` comment — and it costs the mark maintenance. It is an optimisation, not
a fix for the claimed bug.

**What the mark must track.** The dirty span is `[lowest `end` ever reached,
sima)` — a single global low-water of `end`. It must be monotonic-decreasing (it
can only move down), initialised to `sima` at reserve time (nothing dirtied yet),
and updated at exit as `low_water = min(low_water, end_at_exit)` — at exit, `end`
is the lowest point reached during *this* block, since `end` only moves down
within a block. The zeroing happens at **allocation** time, before the block is
handed out, using the mark from the last exit: zero `[block, block +
align16(size)) ∩ [low_water, sima)`. The proposal does not say where the zeroing
happens; allocation time is the only place that makes the "200 MB block, one
`nirmmita(64)`" example come out at 64 bytes.

**Exit paths the mark would miss.** All of them, unless the update is placed in
every emitter. The mark update must live in `r73_gen_rewind`
(`src/r65_arena.inc:404`), in `r73_gen_ret_rewind` (`:535`, the
`nivartanam`/`prasar` path), and in the `r73_wrap_jump` path (`:8438`, the
`krama`/`agrim` path) — there is no single place all exits share. If the update
is placed only on the normal exit path (the `AST_REWIND` node), an early exit that
pushed `end` below the old low-water leaves the mark stale, and the next
allocation over those addresses skips zeroing — **the fix would introduce the
very bug it claims to fix**: a fresh allocation reading the early-exited block's
data. §19 `:1304` ("Every exit gives it all back") is the requirement the mark
must satisfy, and it names all five exits.

**Does it fix the tail?** Only if the overlap is computed over the full
16-byte-aligned span `[block, block + align16(size))`, not the requested size. The
proposal's example does not disambiguate (`nirmmita(64)` — 64 is both the
requested size and the aligned span). If the implementation zeroes only the
requested size, the 8-byte tail stays stale and the real defect survives the fix.

**Does it fix `kosh` / `mala`?** No — and there is nothing to fix there. Both
allocate persistent memory, which is never reused and never stale. The stale-data
bug affects **only scratch `nirmmita`**.

One case the proposal does not touch, noted for completeness: the kosh in-place
extension (`r65_emit_kosh_extend`, `src/r65_arena.inc:305-330`). Its guard is
`new cursor <= end` (`r65_k3`, `:76`), which protects *live* scratch (the current
block's `[end, mark)`) but not a *rewound* earlier block's region — after a rewind,
`end` is back at the mark, so the check passes for a new cursor anywhere below the
mark, and the extension does not zero the new elements. For a kosh whose elements
end exactly at `cur`, a growth after a block could in principle walk `cur` up into
an earlier block's old scratch bytes, and the new elements would read them through
legal `k[i]` indexing. Reaching that needs the persistent side to be adjacent to
the old scratch region — i.e. ~1 GiB of total allocation (persistent + scratch) —
so it is theoretical at student scale, not the example. The WS5 mark would not fix
it either, since the extension does not consult the mark.

---

## Brief corrections

1. **Gate counts, one round later.** On main at this tip `tools/gates.sh` still has
   **78** `run_gate` invocations; max PASS on main is still **80**, and the
   reference status line still says "81 PASS" (`docs/LANGUAGE-REFERENCE.md:3`) —
   the R159 P4 / R161 / R162 off-by-one persists unchanged. On the staged branch
   `501d35fd`, `tools/gates.sh` has **80** invocations (the branch adds the R172
   gate), so the shared state's "83 gates" is right as a TOTAL on the staged
   branch (80 + X11 + doc_counts + Windows skip = 83 entries) — but the branch's
   own status line, "83 PASS / 0 FAIL / 1 NOT-RUN" (Claude's R172-00), is off by
   one the same way: max PASS on the branch is **82** (80 + X11 + doc_counts).
2. **"No rewind, no zeroing, no high-water mark, no new state" is inaccurate as
   stated.** There IS new state (the `r172_*` tables in `.bss`, `:1616-1623` at
   `501d35fd`, plus one frame slot per hoisted kosh), and the length IS zeroed every
   pass (`[d-16] = 0`). What is true: no zeroing of the ELEMENTS, no rewind, no
   high-water mark.
3. **The severity correction's mechanism is confirmed; one number is a question.**
   A 5,000-element `kosh` in a loop failing at 70,000 passes with
   `Sutram truti: kosh rachayitum smritih na labdha` — the message exists in the
   source (`r127_msg_make`, `src/sutram_compiler.asm:698` at `2b70aa18`), and the
   grow path prints it and exits 1 when the region mmap fails
   (`r127_emit_grow_check`, `:21341-21343`, per R161). `/proc/sys/vm/max_map_count`
   on this machine is **1,048,576** (the maximum, as the brief says); the brief's
   "defaults to 65,530 VMAs on a standard Linux" is the kernel default. Question,
   not a contradiction: 70,000 passes > 65,530, so the exact limit in force at the
   measurement is not established by the numbers in the brief (a process starts
   with some VMAs already, and each pass takes one live region VMA, so a 65,530
   limit would bite at ~65,500 passes, not 70,000). The mechanism is confirmed;
   the exact limit at the measurement is not.
4. **The benchmark's narrowness is real, but the test file does not share it.**
   The benchmark pushed one element and never grew; the test file covers growth
   (`grown` to 100, `region` to 4,097, redzones to 20,000,000 with exact d-8/d/d+8
   checks and `moved 0`). The benchmark is not the whole evidence.
5. **Task 2's premise is corrected above** (the answer exists in R161 and R162);
   **Task 3's claim is corrected above** (the claim as stated is false; the real
   defect is the 8-byte tail).

## Could not determine (from source — read-only round, nothing run)

- Whether `tests/r172/test_chakra_kosh.py` actually passes on the branch, and
  whether the branch's claimed numbers (83 gates PASS, guard 587 byte-identical /
  196 refused identically / 0 DIFFER, 16–20 KB vs 37,516 KB) reproduce — the test
  file's assertions are claims, not verified results.
- The exact runtime behaviour of the whitelisted builtins on an EMPTY kosh
  (`kosh_hri`, `kosh_iksh`, `kosh_apanay` with length 0) — not re-read; whatever it
  is, it is identical for a fresh kosh and a reset one, so it cannot be a
  hoist-specific break.
- Whether Claude's WS5 measurement reads the pattern or 0 — nothing was run. By
  reading: the natural program reads 0; only the tail program reads the pattern.
- The exact runtime behaviour of the §4 tail program (values, addresses) — not run,
  by rule. The trace is from the emitted code templates (`r73_s2`–`r73_s6`,
  `src/r65_arena.inc:333-347`), not from execution.
- Whether the kosh-extension-into-old-scratch path is reachable in a real program —
  it needs ~1 GiB of total allocation; not verified by execution.
- Whether any other builtin reads the tail (e.g. `smaran` with a size past the
  buffer, string scans without a NUL) — the reference says those are the
  programmer's mistake (§6c); not enumerated.
- The exact sentinel value recorded for a runtime-size `nirmmita` in the `r78`
  entry (`[r12+24]`, `src/sutram_compiler.asm:12249+`) — the reference states a
  runtime size is unchecked (§6c), which is sufficient for the analysis.
- Whether `r108_param_kept` treats a plain index read `k[i]` as a keeping use
  (the R161 T3 open item, unchanged).
- Whether the hoist's direct-statements-only candidate walk is the intended scope
  or an oversight: `r172_for_enter` reads the body's statement array with no
  recursion into nested blocks, while `r172_scan` walks the whole loop for the
  escape check. The asymmetry is visible in the code; the intent is not stated in
  the tree.
- The `parimana()` `.zero`-path displacement question from R155/R158: still open,
  still needs execution; unrelated to this round, noted only so it is not mistaken
  for resolved.
