# ROUND-164 — the hoist's escape check, the `mala` without a refusal, and §19 revised

**Base:** main at `446c30cc` (compiler v315; the brief landed in that commit).
**Read-only. Nothing compiled, nothing run, nothing executed.**
**Code read:** the R172 kosh hoist on branch `r172-chakra-kosh` @ `501d35fd`
(v317, staged); the R173 mala hoist on branch `r173-chakra-mala` @ `c1f516f8`
(v318, staged on v317). Also read: `Sarvam-to-Claude/ROUND-174.md` (the design
brief for Claude, same commit), Claude's R173 hand-back
(`Claude-to-Sarvam/R173-00-...-AND-A-MALA-IS-NOW-MADE-ONCE-TOO.md`, updated in
`e07c408a`), and the R162 and R163 reports.
**Method:** read the new code first (`git diff 501d35fd..c1f516f8`, +63 lines in
`src/sutram_compiler.asm`), then the routines it touches, then the test file.
Every decisive claim below was spot-checked by re-reading the cited code, not
taken from a brief or a hand-back. File:line citations are at `501d35fd` for
v317 and `c1f516f8` for v318, unless the citation says the tip (`446c30cc`).

## Verdicts first

**Task 1 — the hoist's escape check: SOUND.** No breaking program was found.
The scan sees every call form — a foreign-function call is the same
`AST_FUNCALL` node as a Sutram call, and the scan's `.args` handler scans all
its arguments — so a `kosh` or a `mala` passed to a `prakriya` or to a foreign
function is flagged and NOT hoisted, on the statement path exactly as on the
expression path. The R162 FFI program is **not** a breaking program for the
hoist: the scan flags it, the `kosh` is made anew every pass, and without
R171's reclaim the region is never released anyway. The R162 hole persists in
the pre-existing doors (the FFI door still permits a block `kosh` to a foreign
`ptr` on the statement path; `r108_check_call` still never runs there) — but
the hoist does not hoist the `kosh`, so it adds no new breakage there. One
asymmetry matters: for a **`mala`**, the hoist's scan is the ONLY net — no
pre-existing door refuses a `mala` escape at all — so the scan's completeness
is load-bearing for the `mala` in a way it is not for the `kosh`. It holds: the
scan's dispatch is complete over the AST node types (verified in §1.6).

**Task 2 — the `mala` without a refusal: §19 is right, and the "already
refuses every `mala` escape" argument is false — but the hoist is safe anyway,
for a different reason than the argument claims.** The reference, precisely
read, does NOT say "a `mala` escapes a block with no error at all". It says
two things (`docs/LANGUAGE-REFERENCE.md:1294-1298` at the tip): "Returning one
from inside the block is not refused — its memory stays, so the address stays
good — **but putting it in an outer `vitti` is (`E_VITTI_PRAKAR`, the kind
rule)**." Both halves check out. Of the four escape paths, **one is refused**
and **three compile**. Gemini's challenge holds: adding a real `mala`-escape
refusal WOULD stop programs that compile today. What is true — and what the
argument should have said — is the narrower claim: **the hoist never applies
to a `mala` that can escape.** The scan declines to hoist in every one of
those paths, so no hoisted `mala` aliases. The safety comes from the scan, not
from a refusal; "not hoisted" is not "refused". And the hoisted `mala` DOES
clear its N elements: `rep stosq` over its own length at the top of each pass
— test A prints 99 then 0.

**Task 3 — §19, revised: the paragraph is written below, as the actual words.**
It is Claude's branch paragraph with four corrections (it does not name the
foreign function as an escape; it does not name `nivartanam` as an escape;
"used only as `k[i]` / `m[i]`" does not say writes count; "Two cases no longer
grow" is loose). The R162 paragraph is **dropped, not revised** — it was
written for ROUND-171 (the region released at block exit), which was never
built and is superseded by the hoist. The books' advice — "inside a block
meant to give memory back, take it with `nirmmita`" — is still right for its
own case, a `mandapa` block, and incomplete for a loop; the qualified sentence
is given in §3.3, in all three places.

---

## 1. Task 1 — and the hoist's escape check

### 1.1 What v318 changed (the whole diff, for the mala)

`git diff 501d35fd..c1f516f8 -- src/sutram_compiler.asm` is +63 lines:

- New state, `.bss` (`:1624-1625`): `r173_mala resq 1` ("the scan is for a
  mala (the name only as an index base)"), `r173_p resq 3` ("the three jumps
  to the allocation").
- `r172_for_enter` candidacy: a `mala` is now a candidate too — kind < 2 with
  a size (`[rdi+24] != 0`) and no initializer (`[rdi+16] == 0`) sets
  `r173_mala = 1` and falls into the same `.cand:` path as a `kosh`.
- New routine `r173_mala_begin` (`:11040`): the reuse path for a `mala` —
  `test rax,rax ; jle .fresh ; mov rcx,[rbp+slot] ; test rcx,rcx ; jz .fresh ;
  cmp rax,[rcx-8] ; jne .fresh ; push rcx ; mov rdi,rcx ; mov rcx,rax ;
  xor eax,eax ; cld ; rep stosq ; pop rax ; jmp .have ; .fresh:` — it DOES
  zero the `mala`'s N elements on reuse (a `mala` has no length to reset: all
  its numbers are readable at once, so they are zeroed, as a new `mala`'s
  are). A different length this pass: a new `mala`, as before (the old one is
  kept; it fails toward leaking).
- The scan's `.own` handler (`:11244`): `cmp qword [rel r173_mala],0 ;
  jne .al0` — for a `mala`, the name as arg0 of a whitelisted `kosh` builtin
  is NOT whitelisted; it falls to `.al0`, which scans all arguments → `.esc`.
  Stricter than the `kosh`, not looser.
- Call sites: `r173_mala_begin` in the `mala` decl codegen (`:19852`, after
  the size expression is evaluated, before the allocation), and
  `r172_decl_end` after the allocation (`:19896`, "remembered for the next
  pass").
- The `mala` layout (unchanged): allocation base +0 = element count (hidden),
  user pointer = base +8 (`:19844-19896`, comment "T8b runtime-header layout").
  So `[rcx-8]` in `r173_mala_begin` is the stored element count, and the reuse
  path compares the new length against it, then zeroes exactly N qwords at the
  user pointer.

Nothing else in the scan changed. The `.args` handler (`AST_FUNCALL`) is
identical for `kosh` and `mala`.

### 1.2 Q1 — a `kosh` passed as an argument to a `prakriya`

**Yes, the hoist considers it an escape. The `kosh` is NOT hoisted, on either
path.**

The scan's `.args` handler (v317 `src/sutram_compiler.asm:11201-11214`; v318
`:11256-11269`) scans ALL arguments of an `AST_FUNCALL` node (`[rbx+24+r12*8]`
for each arg index, count at `[rbx+16]`, > 6 → `.esc`). Any argument that is an
`AST_VAR` of the hoisted name hits `.var` → `.esc` (`r172_esc = 1`), and
`r172_for_enter` hoists only if `r172_esc == 0` AND `r172_cnt == 1`. A
statement call and an expression call produce the same `AST_FUNCALL` node
(parser `:18067-18073`, "[AST_FUNCALL][name_ptr][arg_count][arg1..arg6]"), so
the scan treats them identically — the R162 statement-call seam does not apply
to the scan.

**The pre-existing doors, for the same program** (a `kosh` passed to a
`prakriya` that stores its parameter):

- `r108_check_call` (`:13162` v317; `:13219` v318 — same code): for each
  argument that is a `kosh` of an open block (`r108_bk_of`, `:13180`, name
  lookup in the `r108_bk_name` table), it runs `r108_compute_esc` (the greatest
  fixpoint, `:13211`) and looks the callee up in `func_defs` (`rfx3_fn_index`);
  an unknown callee (a function value, a foreign function) → `.bad` (refused);
  a callee whose parameter may keep → `.bad`. It has exactly ONE call site, in
  `.ge_funcall` — **:21957 on v317, :22014 on v318** (see the correction in
  §1.7). So on the **expression** path it refuses the call if the callee keeps
  the parameter; on the **statement** path it never runs.
- `r126_check_untyped_arg` (`:29744` v317; `:29801` v318): "a `kosh` to a
  parameter that is not declared `kosh` is refused". It is called from
  `gen_typed_call_arg` on the scalar path (`:27734` v317; `:27791` v318) —
  which runs on BOTH paths (statement calls use the same typed helper,
  `.gs_funcall` `:19462` / `:19519`). For a **kosh parameter**, `.gtca_kosh`
  (`:27801`) accepts a named `kosh` variable of the same element type and calls
  NO `r126`/`r108` check — the only check for a `kosh` parameter is
  `r108_check_call`, i.e. expression path only. For a **non-kosh parameter**,
  `r126_check_untyped_arg` refuses a `kosh` argument on both paths. For a
  **function value** (`r23_call_is_indirect`), its parameters have no kinds, so
  the check is skipped (`.known`) — and `r108_check_call` refuses it as an
  unknown callee, on the expression path.
- What "keeps" means (`r108_param_kept`, `:13331`): a greatest fixpoint over
  the callee body. `.var` counts every `AST_VAR` of the parameter name
  (`r108_cnt_all`++). `.bcall` counts a use as a `kosh` builtin's own operand
  as a read (`r108_cnt_ok`++). `.fcall` counts an argument to a parameter that
  does not keep as a read. `.end`: kept = (`cnt_all > cnt_ok`) OR overflow. So
  ANY use of the parameter name that is neither a `kosh` builtin's operand nor
  an argument to a non-keeping parameter counts as keeping — including all four
  stores below (each is an `AST_VAR` of the parameter in a position no handler
  excuses). Index reads `k[i]` are not counted at all (the index base is a
  name pointer, never a node) — the comment says "a read (k[i])".

**The four stores, inside the callee** (each is refused by a callee-side check
at the callee's own codegen, independent of how the callee was called — so on
BOTH paths, except as noted for the return):

- **Module variable** (`g = k`): `r126_check_assign` `.var` branch (`:29681`
  v317; `:29738` v318): the target is not local (`r126_is_local` = 0) and is a
  global (`r56_global_index` != 0), so `r134_holds_kosh` on the value →
  refused (`r126_d_glob`).
- **Rachana field** (`p.field = k`): `.cell` branch (target `AST_INDEX` or
  `AST_FIELD`): `r134_holds_kosh` on the value → refused (`r126_d_cell`).
- **Kosh element** (`m[i] = k`): same `.cell` branch → refused.
- **Return** (`nivartanam k`): `r126_check_return` (`:29835` v317; `:29892`
  v318). The phal branch (`siddhi(v)` / `dosh(c)`) refuses any `kosh` value
  outright (`r134_holds_kosh` → `.bad`). The plain branch enforces kind match
  against `r126_ret_kind`: if the `prakriya` returns a number (kind 5) and the
  value is a `kosh` (kind 2/3/6) → `.bad` (refused). **If the `prakriya`'s
  return kind IS a `kosh` (kind 2/3), the kinds match and the return is ALLOWED
  by `r126_check_return`.** But then the fixpoint has already marked the
  parameter as keeping (the `AST_VAR` in the return is `cnt_all`, not
  `cnt_ok`), so on the **expression** path `r108_check_call` refuses the CALL.
  On the **statement** path `r108` never runs — but a statement call discards
  the return value, so nothing is handed out. The return-escape needs an
  expression call to keep the value, and that is exactly where `r108`
  refuses. No break.
- **Local alias** (`vitti x = k`, then `g = x`): closed twice over.
  `r38_mark_alias` (`:28216` v318), called from `.gs_decl` (`:19659`) and
  `.gs_assign` (`:20013`): a plain-variable alias of a `kosh` marks the target
  the same kind, so `x` IS a `kosh` after `vitti x = k`, and `g = x` is refused
  by `.var` (`r134_holds_kosh(x)` = 1). And `r108_note_alias` (`:13134` v318;
  "R109 (ChatGPT R178): `vitti a = k` and `a = k`, k a kosh of an open block,
  make a a name of that kosh, so `r108_check_call` treats `rakh(a)` as
  `rakh(k)`") records the alias in the `r108_bk` tables. (The alias creation
  itself — `vitti a = k` in the loop — contains `AST_VAR(k)`, so the hoist's
  scan flags `k` anyway; an alias created outside the loop cannot name a
  loop-local `kosh`, which does not exist outside it.)

So: the hoist flags the call on both paths; `r108` refuses a keeping callee on
the expression path only; the stores themselves are refused by callee-side
checks on both paths (with the return-kind-match case above, which is harmless
on the statement path because the value is discarded).

### 1.3 Q2 — a `kosh` passed to a foreign function

**Yes, the hoist considers it an escape. The `kosh` is NOT hoisted.**

First, what node a foreign call produces. The `.sffi` sidecar is read once,
after parsing and before any code (`src/r32_ffi.inc:28-31`: "a call to the
local name with the wrong number of arguments is E_ARITY ... it is NOT a
prakriya: no FUNCDEF, no body, no stub, nothing exported"). There is **no
parser change** for foreign functions: a call `c_keep(k)` is parsed exactly like
a call to a Sutram `prakriya`, as an `AST_FUNCALL` node (parser `:18067-18073`).
The foreign-ness is decided at **codegen** time: both `.gs_funcall` and
`.ge_funcall` check `r32_ffi_count` and `r32_ffi_find` (lookup by name in the
FFI table, `r32_ffi_rec`, `src/r32_ffi.inc:45`) and dispatch to
`r33_gen_foreign_funcall` if found. So `r172_scan` cannot distinguish a foreign
call from a Sutram call — and does not need to: its `.args` handler scans all
arguments of any `AST_FUNCALL`, and the `kosh` argument (an `AST_VAR` of the
hoisted name) hits `.var` → `.esc` → NOT hoisted. (The same holds for a slice
argument, `c_keep(k[0:2])`: the argument node is `AST_SLICE` → the scan's
fall-through `jmp .esc`. And for a call returning a `kosh` passed on,
`c_keep(identity(k))`: the argument is an `AST_FUNCALL` whose own `.args`
scans `k` → `.esc`.)

**The R162 FFI program, traced through the hoist's checks:**

```sm
.sffi: c_keep|1|ptr|void|c_keep
       c_read|0||i64|c_read
chakra i = 1 tak 5 {
    kosh k[5000]
    ... grow k past 4,097 ...
    c_keep(k);          // bare statement
}
```

- Hoist: `c_keep(k)` is an `AST_FUNCALL` in the loop body. `r172_scan` `.args`
  scans arg0 `k` → `AST_VAR` of the hoisted name → `.esc`. **`k` is NOT
  hoisted.** It is made anew every pass, exactly as on v316.
- FFI door (`src/r32_ffi.inc:688-699`, the `.ptr` branch `:736-755`): a `kosh`
  by its own name as an `AST_VAR` → `is_kosh_var` → `.r152_open` → kind 2
  (ptr) → `.ptr` emits `gen_expr` then `mov rax,[rax]` (`:751-755`, "R127: a
  kosh passes its elements, not its descriptor") and hands C the elements
  address. The door is called from BOTH `.gs_funcall` and `.ge_funcall`, so it
  permits the `kosh` to a `ptr` parameter on both paths. For `i64`/`f64` kinds
  a `kosh` name is refused (`.bad`).
- **Expression path:** `.ge_funcall` (`:21954` v317; `:22011` v318) runs
  `r129_check_call`, then `r108_check_call` (`:21957` v317; `:22014` v318),
  THEN the FFI dispatch. `r108_check_call` looks the callee up in `func_defs`
  (`rfx3_fn_index`); a foreign name is not there → index -1 → `.bad`
  (refused). So on the expression path the program does not compile. (This is
  the R162 finding.)
- **Statement path:** `.gs_funcall` (`:19426` v317; `:19481` v318) checks the
  FFI table FIRST and dispatches straight to `r33_gen_foreign_funcall`,
  skipping `r129_check_call` and `r25_check_call` — and `r108_check_call`
  never runs on this path at all. **The R162 hole persists in the pre-existing
  doors: the program compiles and hands C the elements address.**
- **But it is not a breaking program for the hoist**, for two reasons. First,
  the hoist does not hoist `k` (above), so the hoist changes nothing about this
  program. Second, on v317/v318 without R171's reclaim, no `kosh` ever dies
  (R161: the region is never released at any scope exit), so C's held address
  stays valid for the program's life — the program does not break at runtime on
  the current code. The break requires R171's reclaim to land, and that is the
  R162 hole, not a hoist hole.

### 1.4 Q3 — a `mala` passed to either (a `prakriya`, a foreign function)

**The v318 check treats a `mala` the same as a `kosh` for calls — it is
flagged, NOT hoisted. But the pre-existing doors do NOT refuse a `mala` at
all, so for the `mala` the hoist's scan is the ONLY net.**

The v318 scan is the same `r172_scan`, run with `r173_mala = 1`. The only scan
change is the `.own` handler: for a `mala`, the name as arg0 of a whitelisted
`kosh` builtin falls to `.al0` (scan all arguments) → `.esc`. Every other
handler is unchanged, including `.args`: a `mala` passed to a `prakriya`
(`teen(m)`) or to a foreign function (`c_keep(m)`) is an `AST_FUNCALL` whose
argument is an `AST_VAR` of the hoisted name → `.esc` → NOT hoisted. A `mala`
as an index base (`m[i]`, `m[i] = v`) is allowed, as for a `kosh` — the base is
a name pointer, never a node (`.one_16`, v318 `:11164`, scans only `[rbx+16]`,
the index).

**Through the pre-existing doors, a `mala` is refused nowhere:**

- `r134_holds_kosh` (`:28796` v317; `:28853` v318) covers kinds 2, 3, 6
  (`kosh`, float `kosh`, mixed) via `r126_is_kosh_value`, or a slice of a
  `kosh`. A `mala` is kind 4. **It is not covered.** Every door that goes
  through `r134_holds_kosh` — `r126_check_builtin` (a `kosh` at arg index 1),
  `r126_check_assign` (`.cell`, `.var`), `r126_check_untyped_arg` (a `kosh` to
  a non-`kosh` parameter), `r126_check_return`, `r126_check_writemem`, the FFI
  door's `.r152_door` — is blind to a `mala`.
- `r126_check_assign` `.local` (`:29681` v317): `r127_check_slice_value` (only
  `AST_SLICE`, a `mala` is not a slice) + `r126_value_kind` + `r126_bind`. A
  `mala` assigned to a local name is not refused; `r126_bind` records the kind
  (4).
- **A whole `mala` CAN be passed to a `vibhag` parameter by design**
  (`.r23_gtca_slice`, `:27833` v318: "a vibhag parameter takes a slice, or a
  whole mala / integer kosh (passed as the slice [0:length])"). The scan flags
  the call anyway (fail-closed: the `mala` is made every pass), but the door
  allows it.
- **FFI door, `mala` to a `ptr`:** `is_kosh_var(m)` = 0, so the `.ptr` branch
  falls to `.gen` and emits `gen_expr` — the `mala`'s user pointer, which IS
  the elements address (a `mala` has no descriptor). C gets the address, on
  both paths, with no refusal anywhere. This is a real pre-existing hole for
  the `mala` (Task 2's territory), but it is not a hoist hole: the scan flags
  the call, so the `mala` is not hoisted.

**Test B, traced (shared state, ROUND-174 WS2):**

```sm
mala row[2]
kosh table[10]
chakra i = 1 tak 5 {
    mala row[2]
    row[0] = i
    kosh_kship(table, row)
}
likha(table[0][0])   // must be 1. If 5, all five rows alias one buffer.
```

- Scan: `kosh_kship` is whitelisted (BN 37); `.own` skips arg0 (`table`) and
  scans arg1 (`row`) → `AST_VAR` of the hoisted name → `.esc` → `row` NOT
  hoisted. (For a `mala` candidate the `.own` handler goes to `.al0` first,
  which scans all arguments — same result.)
- Doors: `r126_check_builtin` does NOT refuse it — `r134_holds_kosh(row)` =
  0, a `mala` is not a `kosh`. So the program COMPILES on v318.
- Runtime: each pass allocates a fresh `mala` (not hoisted), so `table[0]`..
  `table[4]` hold five distinct buffers and `table[0][0]` prints **1**.
  Correct — and the v318 test file's ROWS case asserts exactly this (see
  §1.8). The same holds for `out = row` (scan: `.var` → `.esc`; door:
  `r126_bind` records kind 4, no refusal — the program compiles, `row` is made
  every pass, no aliasing) and `table[i] = row` (scan: `AST_ASSIGN` →
  `.two_8_16` scans the value → `.esc`; door: `.cell` → `r134_holds_kosh` = 0,
  no refusal — compiles, made every pass, no aliasing) and `row` passed to a
  `prakriya` that stores it (scan: `.args` → `.esc`; doors: nothing refuses a
  `mala` store — the `prakriya` receives the `mala`'s user pointer and may keep
  it, but the loop's `row` is a fresh buffer every pass, so the stored pointer
  is to a buffer no later pass reuses).

### 1.5 Q4 — does any check run on the STATEMENT path?

**For the hoist's own scan: yes, and it treats a bare statement call exactly
like an expression call. For the pre-existing doors: no — `r108_check_call`
still never runs on the statement path. The hoist adds no codegen check of its
own on the statement path, and does not need one for its own decision.**

- The scan runs at codegen time over the whole loop AST: `r172_for_enter` is
  called from `.gs_for` (v317 `:20666`; v318 `:20723`) and calls `r172_scan`
  on the whole `AST_FOR` node (bounds and body). A bare statement call in the
  loop body IS an `AST_FUNCALL` node in the body's statement list — `gen_stmt`
  dispatches on the node type, and a statement call is an `AST_FUNCALL`
  statement. The scan's `.block` handler descends into the body's children,
  `.three` (AST_IF) and `.for` descend into nested blocks and loops, and
  `.args` scans every argument of every `AST_FUNCALL` it meets, in statement
  position or expression position alike. There is no position test anywhere in
  the scan. **A bare `store(k);` is seen and flagged exactly like
  `vitti x = store(k);`.**
- The pre-existing doors: `r108_check_call` has exactly one call site, in
  `.ge_funcall` — **:21957 on v317, :22014 on v318**. `.gs_funcall`
  (`:19426` v317; `:19481` v318) calls only `r129_check_call` and
  `r25_check_call` (after the FFI dispatch, which comes first and skips them
  for a foreign callee). The hoist adds no call in `.gs_funcall` and no
  statement-path check of its own — its protection is the AST walk, which
  covers statement calls because it walks the AST, not because it hooks the
  statement codegen.
- So, `kosh` hoist and `mala` hoist separately: **both use the same scan, both
  see statement calls, both do NOT inherit the `r108` gap for their hoist
  decision.** The `r108` gap remains for whether the program compiles at all
  (the R162 hole), and the hoist does not close it — it does not need to,
  because a program the gap lets through is one the scan has already refused
  to hoist.

### 1.6 The scan's completeness (why the `mala`'s only net holds)

The scan's dispatch was verified against the `AST_*` constants (`:87-119`,
`:192`): NUM, FLOAT, STR, SCRCUR, BREAK, CONTINUE are leaves; VAR, ASSIGN,
BINOP, IF, WHILE, RETURN, CALL, DECL, BLOCK, HALT, FUNCALL, INDEX, FOR,
ASSERT, TERNARY, DO_WHILE, PRASAR are handled with all children scanned;
FUNC, WRITEMEM, VEC, FUNCDEF, FIELD, FUNCREF, SLICE, HANDLE, NISHKRIYA and
anything new fall through to `.esc`. The only node the scan returns from
without scanning a child is `AST_REWIND` (whose only child is the
compiler-generated mark `0mNN`, a name no program can write — it starts with
`0`) and `AST_INDEX` (whose base is a name pointer — an element read,
whitelisted by design). The scan calls no pre-existing check (R163 Task 1), so
the `r108` statement-path gap cannot leak into the hoist's decision. For the
`mala`, the scan is the only net — but it is the same scan, with one stricter
change (`.own` → `.al0` for a `mala`), and it flags every call argument.

### 1.7 Test C — a hoisted `kosh` inside a `mandapa`

**No. The `kosh`'s descriptor is NOT allocated on the cursor the `mandapa`
saves and restores, and a `mandapa` exit cannot overwrite a hoisted
descriptor. The 64-vs-48 evidence is the R82 header, not the block touching
the descriptor.**

- Allocation path: `r101a_emit_kosh_alloc` (v318 `:9147`) is
  `jmp emit_nirmmita_from_rax` — the descriptor and its first elements are one
  ordinary persistent allocation. `r65_emit_nirm` (`src/r65_arena.inc:245`):
  block = `cur`, `cur = align16(cur + size)`, room checked against `end`; on
  first use the arena is reserved (`cur = base`, `end = sima = base + 1 GiB`).
  The persistent cursor `cur` grows UP from the arena base and is written in
  exactly four places, all forward-only (R163 Task 3).
- Rewind path: `r73_gen_rewind` (`src/r65_arena.inc:404`): evaluate the mark
  expression, `mov [end],rax`. It restores ONLY the scratch cursor `end`
  (which grows DOWN from the top). It never touches `cur`, and it never touches
  anything below `cur`. The mark itself is the value of `end` at block entry,
  stored in the hidden variable `0mNN` by `r73_gen_scrcur`
  (`src/r65_arena.inc:365`).
- So a `kosh` declared inside a `mandapa` is allocated from `cur` (bottom of
  the arena) while the block wrote scratch memory near the top, and the block
  exit rewinds `end` back to the mark — the descriptor's addresses are never
  reused, never zeroed, never overwritten by the rewind. The hoisted
  descriptor additionally lives in a **frame slot** (a stack slot, `rbp`-relative,
  recorded in `r172_slot`), which no arena operation touches at all.
- **The 64 vs 48 is the R82 header** (R161 Task 2, re-verified R163 Task 2):
  the `kosh` decl size computation is `add rax,4`, R82 branch `add rax,7`,
  `shl rax,3` (v318 `:19762-19780` area) → (cap+4)×8 plain, (cap+7)×8 with
  R82 on; `r65_emit_nirm` aligns to 16, so `kosh temp[1]` is align16(40) =
  **48** plain and align16(64) = **64** with R82 on — 24 bytes of header minus
  8 of alignment padding = **16**. The block adds the header to the one
  allocation; it does not touch the descriptor.
- **Test C's premise cannot occur on v317/v318 in any case:** a `kosh`
  declared inside a `mandapa` inside a `chakra` is NOT a hoist candidate —
  candidacy is direct statements of the loop body only (`r172_for_enter`
  iterates the body's statement array; a `mandapa` is an `AST_BLOCK` child,
  not a direct `AST_DECL`), so the `kosh` is made anew every pass. The shared
  state's numbers confirm it: under a `yadi` or in a `mandapa` inside the loop
  the leak is unchanged at 37,516 and 50,012 KB — 800,000 × 48 = 37,500 KiB
  and 800,000 × 64 = 50,000 KiB, plus the ~16–20 KB baseline — i.e. per-pass
  allocation, not a hoist. A `kosh` declared as a direct statement of the
  `chakra` body, where the `chakra` itself sits inside a `mandapa`, IS a hoist
  candidate (test case `in-mandapa`, v317) — and the `mandapa`'s rewind still
  cannot touch it, for the same persistent-vs-scratch reason.

### 1.8 The breaking program — none found

Every attack traced either escapes the scan (fail-closed: not hoisted), is
refused by a pre-existing door (does not compile), or behaves identically with
and without the hoist. The strongest programs chased, and why each does NOT
break:

1. **The R162 FFI program (strongest the brief names).** Traced in §1.3: the
   scan flags `c_keep(k)` (`.args` → `.esc`), so `k` is not hoisted; the FFI
   door still permits it on the statement path (the R162 hole persists in the
   pre-existing doors), but the `kosh` is made anew every pass and, without
   R171's reclaim, its region is never released — so it does not break at
   runtime on v317/v318. If R171's reclaim lands, the program breaks — but
   that is the R162 hole, not a hoist hole.
2. **A `mala` passed to a foreign `ptr` parameter, as a bare statement**
   (`c_keep(row);`). The scan flags it (`.args` → `.esc`), so `row` is not
   hoisted. The FFI door permits it (no refusal for a `mala` anywhere — a real
   pre-existing hole, §2), but the `mala` is made anew every pass, so no
   aliasing. Not a hoist break.
3. **A `kosh` passed to a keeping `prakriya` as a bare statement** (`store(k);`,
   where `store` keeps its parameter). The scan flags the call site (`.args` →
   `.esc`), so `k` is not hoisted. `r108_check_call` never runs on the
   statement path (the gap remains), but the callee's own stores are refused by
   `r126_check_assign` / `r126_check_return` at the callee's codegen, and the
   one unrefused callee-side path (`nivartanam k` in a `kosh`-returning
   `prakriya`) hands its value to nobody in a statement call. No break.
4. **Test B for the `mala`** (`kosh_kship(table, row)`). Compiles on v318 (no
   door refuses a `mala` at arg index 1), but the scan flags `row` → five
   distinct buffers → `table[0][0]` prints **1**. Correct, and the v318 ROWS
   test asserts it.
5. **`k()` — calling the hoisted `kosh` as a function.** The scan does NOT see
   the callee name (it is a string in the `AST_FUNCALL` node, not a node), so
   `k` IS hoisted. `r23_call_is_indirect` (`src/r23_capabilities.inc:120`):
   the name is not a `prakriya` and is a variable → an indirect call through
   the variable's slot, which holds the descriptor pointer → a jump to the
   descriptor as code → a crash. But it crashes identically on v316 (no
   hoist), and calling a non-function value is unchecked by design (reference
   §17: "A call through a value is not checked: not its number of arguments,
   not that the value is a function"; `r7_check_arity` skips a name that is
   neither a `prakriya` nor foreign, `:14440-14460`). Not a hoist break — the
   hoist changes nothing about this program. It is the one place the scan is
   blind, and it is blind to something the language already leaves unchecked.

### 1.9 Correction to R163 (own earlier report)

The R163 report (Task 1, Q3) cites the `r108_check_call` call site as
`:21556`. That line is correct **on main** — on the main tree at the R162 base
(`79e65f90`), the R163 base (`2b70aa18`), and the R164 tip (`446c30cc`), the
single `call r108_check_call` is at `:21556`, in `.ge_funcall`. It is wrong
**on the staged branches**, which is where R163 Task 1 was reading: the r172
code shifted it to **:21957 on v317** and **:22014 on v318** (verified by grep
— exactly one `call r108_check_call` per tree). On v317, `:21556` is
`mov [rax+8], rcx` — part of an `AST_STR` construction in an error-message
failure block. The substantive claim (exactly one call site, expression form
only) is TRUE on all four trees; only the line number was wrong, because the
main-tree line was carried onto the branch. The R164 report uses the
branch-correct lines throughout (§1.2, §1.3, §1.5).

### 1.10 Test-file verification — v318 `tests/r173/test_chakra_mala.py` (166 lines)

**What it tests.** Docstring: "Proven local: the declaration is a statement
of the loop's own body, the only one of its name, without an initializer, and
in the whole loop the name appears only as the base of an index (m[i], m[i] =
v). Any other appearance — a second name, an argument of a `prakriya`,
`nivartanam`, a value put into a `kosh` or a `mala` — and the `mala` is made
every pass, as before: no program is newly refused, and no two rows can become
one." The witness is `parimana()`: each case is compiled with 1 pass and with
20. "once": the same number. "every pass": more. Every program's sum is right
only if each pass saw eight zeros before it wrote.

- CASES, made once: `plain` (mala m[8], read, written, read), `named-length`
  (the length is a variable, the same every pass), `two` (two mala in one
  body), `with-kosh` (a mala and a kosh in one body), `agrim` (agrim after the
  mala is written).
- CASES, made every pass: `changing-length` (a length that changes every pass),
  `alias` (`vitti a = m`), `to-prakriya` (given to a prakriya `teen(m)` — as an
  argument in an expression, `s = s + teen(m)`), `under-yadi` (declared under a
  yadi), `yavat` (a yavat loop).
- ROWS: a mala put into a kosh every pass — five rows stay five (prints
  '11 33 55'). **This IS Test B from the shared state**, and it asserts the
  outcome (distinct buffers), which holds because the scan flags the mala.
- RED (redzones): 64 bytes of `0xDEADBEEFCAFEBABE` before the mala's length word
  and after its last number, 1,000,000 passes, a `dirty` counter (passes where
  any m[i] != 0 before writing) — asserts `bad 0, dirty 0, held 208`, and the
  sum. **This is Test A in substance** (a mala read before writing must see
  zeros), though not in Test A's exact yadi-conditional form (write on pass 1
  only, read on pass 2).

**What it does NOT cover:**

1. **No foreign-function case.** No `.sffi` declaration, no foreign call
   anywhere in the file.
2. **No statement-path call.** `to-prakriya` passes `m` as an argument in an
   expression (`s = s + teen(m)`); no case has a bare `store(m);` statement.
3. **No mala passed to a foreign function.**
4. **No mala passed to a `vibhag` parameter** (allowed by design, flagged by
   the scan — untested either way).
5. **No `nivartanam` of a mala** — the docstring names it as a disqualifier,
   but no case tests it.
6. **No mala put into another mala** — the docstring names "a value put into a
   kosh or a mala", but only the kosh case is tested (ROWS).
7. **No recursion case** (a prakriya containing the loop, called recursively).
8. **No kosh declared in a nested bare block** (`chakra { { mala ... } }`).
9. **No `kosh_kship(m, m)` self-push.**

---

## 2. Task 2 — and the `mala` that was hoisted without a refusal

### 2.1 `out = row` — refused, but by the kind rule, not a `mala` door

**Yes — but by the kind rule, not by a `mala`-escape door, and only for the
assignment spelling.** Trace, all at `c1f516f8`:

- **The hoist's own scan declines to hoist, but does not refuse.** `out = row`
  is `AST_ASSIGN`; the scan's `.two_8_16` handler scans the value `row`
  (`AST_VAR` of the name) → `.esc` → the `mala` is made every pass, as before.
  A scan decline is not a refusal: the program still compiles.
- **`r126_check_assign` (.local) refuses it.** The call site is `.gs_assign`
  (`:19951`). Target `out` is an `AST_VAR` and a local → `.local` (`:29681`):
  `r127_check_slice_value(row)` returns ok (a bare `mala` name is not a
  slice); `r126_value_kind(row)` = **4** (`:28378` — `AST_VAR` → `r126_kind`,
  which returns 4 for a `mala`: `is_array_var` at `:28050`, marked by
  `.gs_decl_array` at `:19848`); `r126_bind(out, 4, row)` (`:29287`):
  `r126_kind(out)` = **5** (a plain local: `r126_is_local` at `:28311`), 5 ≠ 4
  → `r126_fail_kind` (`:28731`), which prints `Sutram truti
  [E_VITTI_PRAKAR]: 'out' sankhya (smriti-sthanam va) asti; mala tasyam na
  sthapyate` (kind names `:607-612`, message `:602-605`) and exits 1. **The
  program does not compile.**
- **The walk does not refuse it.** `r137_check_stmt` (`:28912`), `.assign`
  door: "a name of its own may take a slice" — the target is an `AST_VAR`, so
  it goes to `.gen` with no check on the value. The walk's `.num` handler
  refuses a slice or a `kosh` used as a number, never a `mala`
  (`r134_holds_kosh` is 0 for kind 4).
- **The taint check cannot see it.** `r73_note_decl` has exactly one call site
  (`:15436`, the scalar-declaration path); the array path never calls it. A
  `mala` is never tainted, never tracked (R160/R161, unchanged on v318).
- **The declaration spelling is NOT refused.** `vitti out = row` inside the
  loop: `r126_check_decl` (`:29651`, called from `.gs_decl` at `:19646`) →
  `r126_value_kind(row)` = 4 → `r126_bind(out, 4, row)`. At that point `out`
  is not yet in the var table (the check runs at the start of `.gs_decl`,
  before `alloc_var`), so `r126_kind(out)` = 0 → the `.new` branch → the
  initializer is an `AST_VAR`, not an `AST_FUNCALL` → no refusal. Then
  `r38_mark_alias(out, row)` (`:28216`, called from `.gs_decl` at `:19659`)
  marks `out` as the same kind as `row` — an array var. **So `vitti out = row`
  compiles, and `out` holds the `mala`.** The kind rule refuses a kind
  *change* on an existing name; it does not refuse a name *born* a `mala`.
  (The name is scoped to the loop body, so this spelling alone does not carry
  the `mala` out of the loop — but it is a stepping stone: `table[i] = out`
  after it compiles, as in §2.4.)

So the answer to Q1 as asked (`out = row`, assignment into a pre-declared
number variable): **refused, `E_VITTI_PRAKAR`, by `r126_bind`'s kind check
(`src/sutram_compiler.asm:29287` → `:28731`)** — a rule that predates the
hoist, documented in §19, and not a `mala`-escape door. It does not support the
claim that the compiler refuses every `mala` escape: it fires for any kind
change, and the declaration spelling escapes it entirely.

### 2.2 `kosh_kship(table, row)` — NOT refused; it compiles

- **The hoist's scan declines to hoist, but does not refuse.**
  `kosh_kship` is a whitelisted builtin (BN 37), so the scan's `.builtin`
  handler takes `.own` — but for a `mala` (`r173_mala` = 1) the `.own` branch
  goes straight to `.al0` (`:11245`: "R173: a mala has no built-in of its own
  — its name there is a use"), which scans **all** arguments. Arg1 `row` is an
  `AST_VAR` of the name → `.esc` → the `mala` is made every pass, as before.
- **`r126_check_builtin` does not refuse it** (`:29737`). It loops over the
  arguments and calls `r134_holds_kosh` on each. Arg0 `table` is a `kosh` →
  held, index 0, builtin id 37 in `[BN_PANKTILEN (36), BN_KOSHDEQUEUE (45)]`
  → ok. Arg1 `row` is a `mala` → `r134_holds_kosh` = 0 → `.next`, no check.
  **The check that refuses a `kosh` at arg index 1 never fires for a `mala`,
  because a `mala` does not hold a `kosh`.**
- **`r134_holds_kosh` is 0 for a `mala`** (`:28853`). `r126_is_kosh_value`
  (`:28828`) returns 1 only for kinds 2, 3, 6 (float `kosh`, `kosh`, mixed); a
  `mala` is kind 4. `r134_kosh_slice` (`:28866`) returns 1 for a slice of a
  `kosh`, a slice name, or a `vibhag` parameter — its own comment says: "A
  slice of a `mala`, made in place, is not a `kosh`'s borrow." A bare `mala`
  name is none of those.
- **The walk does not refuse it.** `r137_check_stmt` `.call` door: "a `kosh`
  at a builtin is `r126_check_builtin`'s" — the walk only checks slices used
  as numbers. A `mala` as a builtin argument is not a number use.
- **So the program compiles.** The `mala` is made fresh every pass (the scan
  declined to hoist), so `table` holds five distinct rows. See §2.4 for what
  it prints.

The same holds for the other two paths in §2.4, traced there. The general rule:
**no door in the compiler knows a `mala` as an escaping value.** Every door
asks `r134_holds_kosh`, and a `mala` is not a `kosh` and does not borrow one's
elements.

### 2.3 Does the hoisted `mala` clear its N elements at the top of each pass?

**Yes. `rep stosq` over its own length — all N slots, not only the ones
written.** The v318 diff adds `r173_mala_begin` (`:11040`; comment
`:11035-11039`), called from the `mala` decl codegen at `:19855`, with
`r172_decl_end` called after the allocation at `:19896` to remember the
pointer for the next pass. The emitted sequence, quoted from the comment and
verified against the `R172_EMIT` calls:

```
test rax,rax ; jle fresh            ; the length this pass
mov rcx,[rbp+slot] ; test rcx,rcx ; jz fresh
cmp rax,[rcx-8] ; jne fresh         ; the same length as the mala in the slot? (its hidden length word)
push rcx ; mov rdi,rcx ; mov rcx,rax ; xor eax,eax ; cld ; rep stosq ; pop rax      ; zero its numbers
jmp have
fresh: (the allocation, as before) ; mov [rbp+slot],rax
have:
```

The byte sequence: `0x48,0x85,0xC0, 0x0F,0x8E` + rel32 (`test rax,rax ;
jle fresh`); `0x48,0x8B` + modrm (`mov rcx,[rbp+slot]`); `0x48,0x85,0xC9,
0x0F,0x84` + rel32 (`test rcx,rcx ; jz fresh`); `0x48,0x3B,0x41,0xF8,
0x0F,0x85` + rel32 (`cmp rax,[rcx-8] ; jne fresh`); `0x51, 0x48,0x89,0xCF,
0x48,0x89,0xC1, 0x31,0xC0, 0xFC, 0xF3,0x48,0xAB, 0x58, 0xE9` + rel32 (`push
rcx ; mov rdi,rcx ; mov rcx,rax ; xor eax,eax ; cld ; rep stosq ; pop rax ;
jmp have`). The three `fresh` jumps are patched by `r73_patch32` (via
`r173_p`, `:1624`); the `jmp have` is patched by `r172_decl_end` (`:11080`) to
land after `mov [rbp+slot],rax`.

How it works, and why it covers all N slots:

- **The count is the current pass's length.** `rax` holds the length `N` (the
  decl codegen evaluates the size expression into `rax` before calling
  `r173_mala_begin`). `mov rcx,rax` sets the `rep stosq` count to `N`.
- **The count is verified equal to the stored length first.** `cmp rax,[rcx-8]`
  compares it against the hidden length word at the allocation base. The slot
  holds the **user pointer** (`r172_decl_end` emits `mov [rbp+slot],rax` after
  the decl codegen does `add rax,8` — user pointer = base + 8 — and the decl
  stores the length in the header first: `pop rcx ; mov [rax],rcx`, "store
  header at allocation base", `:19855-19896`). So `[rcx-8]` is the stored
  length `N`, and the comparison is against it. A different length this pass →
  `.fresh`: a new `mala`, as before (the old one is kept; it fails toward
  leaking). A zero or negative length → `.fresh`.
- **The zeroing starts at the user pointer and covers exactly the elements.**
  `mov rdi,rcx` sets the destination to the user pointer; `rep stosq` zeroes
  `N` qwords from there — all N element slots. The header word `[rcx-8]` is
  **not** zeroed (it lies before `rdi`), so the stored length survives for the
  next pass's comparison. `pop rax` restores the user pointer for the `jmp
  have`.
- **The clearing happens at the declaration, before any read in that pass.**
  The decl is the first statement touching the `mala` each pass, and the
  zeroing is emitted inline at the decl. A `mala` has no length field to reset
  — this is the replacement, and it is the whole `N`, not the slots written so
  far.

This is what ROUND-173 WS4 required ("zero its `N` qwords at the top of each
pass"), and it is what was built. The comment in the code says it plainly: "A
`mala` has no length to reset: all its numbers are readable at once, so they
are zeroed, as a new `mala`'s are."

### 2.4 The programs that would show it

**(a) Test A — the stale-read program**

```sm
chakra i = 1 tak 2 {
    mala row[2]
    yadi i == 1 { row[1] = 99 }
    likha(row[1])
}
```

Trace on v318: the scan finds `row` used only as an index base (`row[1] = 99`,
`row[1]` in `likha` — an `AST_INDEX` whose base is a name pointer, never
scanned as a node — and the `yadi` is `AST_IF`, which the scan descends into) →
`r172_esc == 0`, `r172_cnt == 1` → **hoisted**. Pass 1: the slot is 0 → fresh
allocation, `row[1] = 99`, `likha(row[1])` prints **99**. Pass 2: the decl is
reached again; `r173_mala_begin` finds length 2, the slot holding pass 1's
`mala`, and `[rcx-8] == 2` → `rep stosq` zeroes both slots → the `yadi` is
false (`i == 2`), so nothing is written → `likha(row[1])` prints **0**. **It
prints 99 then 0** — the hoist zeroes, and test A passes. (Before the hoist it
also printed 99 then 0, because each pass made a fresh `mala`; the hoist
preserves that.)

**(b) Test B — the escape program**

**As written in the brief, the program does not compile — but for the wrong
reason.** It declares `mala row[2]` both outside the loop and inside it. One
namespace per function: `r7_declare_new` (`:14523` — "A declaration of a name
that is already visible in this function (same block, or an enclosing one, or a
parameter) is an error") refuses the inner declaration with
`E_DUPLICATE_NAME` (`:339`). The program that decides the question drops the
outer declaration — Claude's ROWS test is exactly this shape:

```sm
mukhya() {
    kosh table[10]
    chakra i = 1 tak 5 {
        mala row[2]
        row[0] = i
        kosh_kship(table, row)
    }
    vitti p = table[0]
    likha(p[0])
}
```

(Note the read-back goes through a `vitti`: `table[0][0]` is a syntax error —
Sutram has no double index — which Claude's hand-back already caught for the
`kosh` version. The brief's `likha(table[0][0])` does not parse.)

Trace: the scan declines to hoist (`kosh_kship(table, row)` puts `row` as arg1
→ `.al0` → `.esc`, §2.2), and no check refuses the push
(`r126_check_builtin` never fires for a `mala`, §2.2). **It compiles.** Each
pass makes a fresh `mala` (80 bytes a pass, as before), so `table` holds five
distinct rows and `p[0]` — pass 1's row, `row[0] = 1` — prints **1**. Not 5.
The rows stay separate because the `mala` was never hoisted, not because any
check refused the escape.

**The other three escape paths:**

1. **`out = row` (WS2 form: `vitti out = 0` outside, `out = row` inside).**
   **Refused.** `E_VITTI_PRAKAR`, by `r126_bind`'s kind check (`:29287` →
   `:28731`), §2.1. The program does not compile, so nothing prints. This is
   the one path the compiler refuses — and it is the kind rule, not a `mala`
   door. (The declaration spelling `vitti out = row` inside the loop compiles
   instead, §2.1 — but the name is scoped to the loop body, so it does not by
   itself carry the `mala` out.)
2. **`table[i] = row`.** **Compiles; prints 1.** Scan: `AST_ASSIGN` → the value
   `row` is scanned → `.esc` → not hoisted. Door: `r126_check_assign` `.cell`
   (`:29681`) — target `AST_INDEX` → `r134_holds_kosh(row)` = 0 → no refusal.
   Each pass makes a fresh `mala`; `table[0]` is pass 1's row, read back through
   a `vitti` (`vitti p = table[0]; likha(p[0])`) prints **1**.
3. **`row` passed to a `prakriya` that stores it in a module-level variable.**
   **Compiles; the module variable holds the last row.**
   ```sm
   vitti g = 0
   prakriya store(a) { g = a }
   mukhya() {
       chakra i = 1 tak 5 {
           mala row[2]
           row[0] = i
           store(row)
       }
       likha(g[0])
   }
   ```
   Scan: `AST_FUNCALL` → `.args` scans all arguments → `row` → `.esc` → not
   hoisted. Call: `r126_check_untyped_arg` (`:29801`) → `r134_holds_kosh(row)` =
   0 → no refusal. Store inside: `g = a` — `g` is a module global →
   `r126_check_assign` `.var` → not local → global index found →
   `r134_holds_kosh(a)` = 0 → no refusal. **Compiles.** Each pass makes a fresh
   `mala`; `g` ends up holding pass 5's row, so `likha(g[0])` prints **5** —
   the `mala` has escaped the loop into a module variable, with no error,
   exactly as §19 describes for a `mala`'s address.

**Two more paths, for the record** (not among the four asked, but the same
verdict): **returning one** (`nivartanam row` from a `prakriya`) is not refused
— `r126_check_return` (`:29835`) refuses only kinds 2, 3, 6 (a `kosh`) or a
kind mismatch against a `kosh`-returning function; a `mala` return passes when
the function's recorded kind is 5 or matches — and §19 says so in so many
words ("Returning one from inside the block is not refused"). **A foreign
function** taking a `ptr` parameter: the FFI door (`src/r32_ffi.inc:680-699`)
checks `is_kosh_var` and then `r134_holds_kosh` — both 0 for a `mala` — so the
`mala` goes to C as its address, unrefused (the scan declines to hoist it
either way: an FFI call node is not a whitelisted use). The R162 FFI hole, for
a `mala`.

### 2.5 Claude's hand-back — verified against the code

- **WS2, the container escape (for a `kosh`): verified in substance.** The
  briefed `kosh` program does not compile — `matrix[0][0]` is a syntax error
  (no double index) and `kosh_kship(matrix, row)` / `matrix[i-1] = row` are
  refused with `E_KOSH_DVARA` by the doors traced in §2.2
  (`r126_check_builtin`, `r126_check_assign` `.cell`, via
  `r134_holds_kosh`). Those are `kosh` programs; the `mala` version is the
  gate's `ROWS` case, §2.4 — which compiles and stays distinct because the
  `mala` is not hoisted. Claude's sentence "The gate has this shape for a
  `mala`, which *can* be put into a `kosh`" is accurate and is the whole
  point: a `mala` **can** be put into a `kosh`, a `kosh` cannot.
- **WS4, the zeroing sequence: verified byte-for-byte.** The sequence quoted in
  the hand-back matches the `R172_EMIT` calls in `r173_mala_begin` (`:11040`),
  §2.3. `rep stosq` over the `mala`'s own length, not eight unrolled stores —
  the length need not be 8 or constant (`mala m[n]` is a gate case).
- **"No program is newly refused": true.** The hoist refuses nothing; it only
  declines to hoist. The one refusal among the four paths (`out = row`)
  predates the hoist (the kind rule, v301) and is not the hoist's doing.
- **"How many programs in the tree that [a new refusal] would refuse: NOT
  MEASURED": honest, and it matters.** The refusal would stop programs that
  compile today (§2.4); the count is unknown. That is the language decision
  Claude names, and it is Sarvam's/owner's, not the hoist's.
- **WS5, the stale-data measurement: confirms the R163 framing's boundary.**
  The small case reads 0 and 0 — as R163 Task 3 found. The large case (a
  600,000,000 byte block, then a 600,000,000 byte `nirmmita` after it) reads 77
  in 15,782,272 of 75,000,000 words — the two sides meet once persistent +
  scratch exceed 1 GiB, exactly the boundary R163 stated ("The two sides meet
  only if ~1 GiB had been allocated persistently"). R163's verdict stands for
  ordinary programs; the large case is the mechanism, measured, not a
  contradiction of it. (Measurement is Claude's, not verified by reading — this
  round is read-only.)
- **Severity, `k5000.sm`: noted, not verified.** Claude reports the program
  killed by signal 9 at 5,810,816 KB resident on a machine with `max_map_count`
  65,530 — not the named refusal Sarvam reported at 70,000 passes. That is his
  measurement; it bears on the R163 brief-correction 3 question (the exact
  limit in force at Sarvam's measurement), but it does not settle it — a kill
  and a refusal are different stops, and neither measurement names the limit in
  force. Not investigated further here (read-only; and it is Task 1's territory
  only insofar as the hoist changes it — v317/v318 finish the same program in
  0.6 s because the `kosh` is hoisted).

---

## 3. Task 3 — and §19, revised

### 3.1 The paragraph, for Claude to paste

> **Two cases no longer grow: a `kosh` (v317, R172) and a `mala` (v318, R173)
> declared in a `chakra`'s own body.** Not a block's doing — the loop's. When
> the declaration is a statement of the loop's body itself, and in the whole
> loop the name is used only as `k[i]` — read or written — and as the `kosh`
> a `kosh_*` built-in works on (not `kosh_ksham`), the `kosh` is made on the
> first pass and every later pass starts with the same one, emptied: same
> descriptor, same elements, same region if it grew past 4,096 numbers. Each
> pass still sees an empty `kosh`. A `mala` the same way: declared in the
> loop's own body, without an initializer, its name used in the loop only as
> `m[i]` — read or written — the same length every pass — it is made on the
> first pass, and every later pass starts with the same one, its numbers set
> to 0 as a new `mala`'s are. Measured (Linux x86-64): 800,000 passes of
> `kosh temp[1]`, one number added — **16-20 KB resident on v317, 37,516 KB on
> v316**; 800,000 passes of `mala m[8]` — **20 KB resident on v318, 62,516 KB
> on v317**. Anything else is made every pass and kept, as before: a second
> name (`vitti a = k`), a `kosh` or a `mala` given to a `prakriya` or a
> foreign function, returned with `nivartanam`, or sliced; a `mala` put into a
> `kosh` — so rows collected in a loop stay separate rows. A declaration under
> a `yadi` or in a `mandapa` inside the loop is not reached either, and a
> `yavat` loop is not a `chakra`: there the leak is unchanged, 48 bytes a
> pass, 64 in a program with a `kosh` in a block. A `kosh` in an inner `chakra`
> is made once each time the inner loop starts. **A block still returns no
> memory to the operating system.**

**Anchor:** insert after the "Not a `kosh` of pointers" paragraph (`:1292` at
the tip), before "**Nor a `mala`.**" (`:1294`) — where it already sits on the
branch (`:1325` at `c1f516f8`); this paragraph replaces the branch's version
there. **Version flag — read before pasting.** "v317" (kosh) and "v318" (mala)
are provisional. Both are staged, unlanded: v317 is branch `r172-chakra-kosh`
(`501d35fd`), v318 is branch `r173-chakra-mala` (`c1f516f8`), and v316
(`59d60353`) is staged ahead of them, also unlanded. If the branches land under
different version numbers — or if v316 lands first and the numbering shifts —
correct both versions to the versions the hoists actually land in. Do not paste
"v317"/"v318" without checking.

**No amendment to `:1291-1292`.** The last sentence of the "Not a `kosh` of
pointers" paragraph — "A `kosh` of *numbers* used in a block works; its storage
is ordinary memory, which the block does not reclaim." — remains true under the
hoist. The R162 amendment (", except for one case — below") is withdrawn: the
hoist does not reclaim anything, so there is no exception to record. The new
paragraph follows it and is consistent with it (it ends "A block still returns
no memory to the operating system"; the next paragraph, "Nor a `mala`.", says
the same thing with its measurement).

### 3.2 The four corrections to the branch paragraph (what changed, and the code)

The branch paragraph (`docs/LANGUAGE-REFERENCE.md:1325-1336` at `c1f516f8`) is
accurate in substance; the paragraph above is it with these corrections:

1. **The foreign function is an escape, for both the `kosh` and the `mala`.**
   The branch says "a `kosh` given to a `prakriya` or sliced" and "A `mala`
   given to a `prakriya`, given a second name, or put into a `kosh`". Neither
   names a foreign function. The scan sees foreign calls: a foreign call is an
   `AST_FUNCALL` node (`r33_gen_foreign_funcall`, `src/r32_ffi.inc:664-666`,
   takes "the AST_FUNCALL"; `.gs_funcall` dispatches on it,
   `src/sutram_compiler.asm:19481-19494` at `c1f516f8`), and the scan's `.args`
   handler (`:11256-11271`) scans every argument `[rbx+24+r12*8]`, so a
   `kosh`/`mala` passed as an argument to a foreign function — as a bare
   statement or in an expression — is an `AST_VAR` of the name inside an
   `AST_FUNCALL` → `.var` → `.esc` → NOT hoisted. The R162 hole
   (`r108_check_call` never running on the statement path) does not apply to
   the hoist's scan, because the scan walks the AST, not the `r108` check. The
   paragraph now says "given to a `prakriya` or a foreign function".
2. **`nivartanam` is an escape, for both.** The branch names no return escape.
   The scan's `.one_8` handler scans `AST_RETURN`'s child, so returning the
   `kosh`/`mala` is `.esc` → NOT hoisted. (The v318 test file's docstring lists
   it: "a second name, an argument of a `prakriya`, nivartanam, a value put
   into a `kosh` or a `mala".) The paragraph now says "returned with
   `nivartanam`".
3. **Writes count.** The branch says "used only as `k[i]`" / "only as `m[i]`".
   The whitelist is index BASES, read or written: `AST_INDEX` (`:11088` at
   `501d35fd`, unchanged at `c1f516f8`) — the base is a name pointer, never a
   node — so `.one_16` scans only the index node, and `k[i] = v` is as
   whitelisted as `k[i]`. The paragraph now says "read or written".
4. **"Two cases no longer grow" is loose.** A hoisted `kosh` still grows its
   buffer (its capacity grows; the grown buffer is kept — that is the point of
   Audit 1). What no longer grows is the program's held memory: one allocation
   instead of one per pass. The heading is kept (it is the branch's heading,
   and the body pins it down: "the `kosh` is made on the first pass and every
   later pass starts with the same one"), but a reader who takes "grow"
   literally will misread it. If the owner wants the heading tightened, "Two
   cases no longer leak" says what it means.

### 3.3 What the code does, behind each sentence (the verification)

- **Kosh reuse (v317):** per-pass reset touches only `[d-16]` (length);
  capacity and elements pointer untouched; a growing `kosh` keeps its grown
  buffer (R163 Task 1, Q1-Q2; `r172_decl_begin`, `src/sutram_compiler.asm:11006-11025`
  at `501d35fd`). Deciding check is the `r172_scan` whitelist
  (`r172_esc==0` AND `r172_cnt==1`); whitelisted: index base and arg0 of 7
  builtins (BN 37, 38, 39, 42, 44, 45); `kosh_ksham` (BN 40) NOT whitelisted.
  Candidacy is direct statements of the loop body only; the scan walks into
  nested blocks (mandapa is an `AST_BLOCK`; yadi is `AST_IF`).
- **Mala reuse (v318):** the diff `501d35fd..c1f516f8` is 63 changed lines in
  `src/sutram_compiler.asm`. New state: `r173_mala resq 1` (the scan is for a
  mala — the name only as an index base), `r173_p resq 3` (the three jumps to
  the allocation). `r172_for_enter` now also accepts a mala declaration: kind
  < 2 with `[rdi+24] != 0` (a size) and `[rdi+16] == 0` (no initializer) →
  `r173_mala = 1`, candidate. `r173_mala_begin` (new routine, comment at the
  branch): "the length is in rax. `test rax,rax ; jle .fresh ; mov
  rcx,[rbp+slot] ; test rcx,rcx ; jz .fresh ; cmp rax,[rcx-8] ; jne .fresh ;
  push rcx ; mov rdi,rcx ; mov rcx,rax ; xor eax,eax ; cld ; rep stosq ; pop
  rax ; jmp .have ; .fresh:` A mala has no length to reset: all its numbers
  are readable at once, so they are zeroed, as a new mala's are. A different
  length this pass: a new mala, as before (the old one is kept; it fails
  toward leaking)." The byte sequence was verified against the comment: `0x51`
  (push rcx), `0x48,0x89,0xCF` (mov rdi,rcx), `0x48,0x89,0xC1` (mov rcx,rax),
  `0x31,0xC0` (xor eax,eax), `0xFC` (cld), `0xF3,0x48,0xAB` (rep stosq),
  `0x58` (pop rax), `0xE9` (jmp .have). The zeroing covers exactly the mala's
  `length` qwords at its base: the length in `rax` is the runtime element count
  (from `gen_expr` of the size expression, called at `:19852`), and the stored
  length it is compared against, `[rcx-8]`, is the element count — the mala
  decl stores it at the allocation base (`mov [rax],rcx`, "pop length -> rcx;
  store header at allocation base", `:19873-19878`) and the user pointer is
  base + 8. So **yes: the elements are zeroed on reuse, all N of them, every
  pass.** A different length this pass makes a new mala (the old one kept —
  fails toward leaking). The scan change for the mala: in `r172_scan`'s `.own`
  handler, `cmp qword [rel r173_mala], 0 ; jne .al0` — "a mala has no built-in
  of its own - its name there is a use" — so for a mala, ANY builtin argument
  position is a use → `.esc`; the whitelist for a mala is index bases only.
- **The v318 test file covers it:** `tests/r173/test_chakra_mala.py` (166
  lines). `plain` reads all eight elements before writing (`Z` = reads
  `m[0..7]` into the sum), then writes, then reads `m[3]`; the sum (270) is
  right only if each pass read eight zeros — the brief's Test A shape, with
  the zeroing asserted. `named-length` (a variable length, the same every
  pass — hoisted), `changing-length` (a length that changes every pass — a new
  mala each time), `alias`, `to-prakriya`, `under-yadi`, `yavat` (all not
  hoisted). `ROWS` asserts `'11 33 55'` — five rows stay five (the brief's
  Test B shape). `RED` (redzones) asserts `dirty 0` over 1,000,000 passes —
  every pass read eight zeros — and `held 208`. What it does NOT cover: no
  `mandapa`-in-`chakra` case for the mala (no `mandapa` mention in the file at
  all) — the code path is shared with the `kosh` (`r172_for_enter`'s candidate
  loop), so a mala in a `mandapa` inside the loop is equally not a candidate,
  but the test file does not assert it (see §3.6.4).
- **Under a `yadi` / in a `mandapa` inside the loop:** not hoisted, for both
  the `kosh` and the `mala` — candidacy is direct statements of the loop body
  only (R163 Task 1, Q5; `r172_for_enter`'s candidate loop, unchanged by the
  v318 diff). The leak there is unchanged: 48 bytes a pass outside a block, 64
  in a program with a `kosh` in a block (R161 Task 2: 24 bytes of R82 header
  minus 8 of alignment padding = 16; 48+16=64). The R164 brief's shared state
  gives the same figures as totals: 37,516 KB and 50,012 KB at 800,000 passes
  (800,000 × 48 = 37,500 KiB; 800,000 × 64 = 50,000 KiB; plus the ~12-24 KB
  baseline).
- **`yavat` is not a `chakra`:** `r172_for_enter` has exactly ONE call site at
  `c1f516f8` (`src/sutram_compiler.asm:20723`, in `.gs_for`, after
  `r96_check_for_float` and the `r126_bind` of the chakra variable). There is
  no call in the `yavat` codegen. The v317 test case `yavat` and the v318 test
  case `yavat` both assert made-every-pass. Verified from the code, not just
  the test file.
- **A `kosh` in an inner `chakra`:** made once each time the inner loop starts
  (R163 Task 1, Q5; the inner loop's own `r172_for_enter` finds the decl as a
  direct statement of the inner body). The same holds for a `mala` by the same
  code path (the candidate loop is shared), though the v318 test file has no
  nested-loop case for the mala — the v317 test file's `NESTED` case covers
  the `kosh`.

### 3.4 Other sentences needing matching changes

**Reference `docs/LANGUAGE-REFERENCE.md` (tip line numbers):**

- **(a) `:1291-1292` — NO amendment (R162's amendment withdrawn).** "A `kosh`
  of *numbers* used in a block works; its storage is ordinary memory, which
  the block does not reclaim." Still true under the hoist. See §3.1.
- **(b) `:1406-1407` — NO change (R162's narrowing withdrawn).** "**Decided
  (R103, v285): the block does not take a `kosh`'s memory back; the `kosh`
  keeps it for the program's life.**" Still true: the hoist does not take
  memory back, it avoids allocating it. The R162 narrowing ("except for the
  separately mapped buffer of a `kosh` that satisfies the four conditions")
  was for ROUND-171, which was never built. The reasoning sentence that
  follows ("Giving the region back would make a dead `kosh` reaching a
  `prakriya` a crash…") also stands unchanged — nothing is given back.
- **(c) `:1417` — NEEDS A QUALIFIER.** "Make a `kosh` that is reused once,
  outside the loop, and empty it with `kosh_clear` each pass: 0 MB." The idiom
  still works, but it is no longer the only way: from v317 a proven-local
  `kosh` declared in the loop's own body is reused by the loop itself.
  Qualified sentence, paste-ready:

  > The block bounds `nirmmita` (10,000,000 `nirmmita(64)`, one block per
  > pass: under 1 MB; without blocks: 625 MB), not `kosh` storage. Make a
  > `kosh` that is reused once, outside the loop, and empty it with
  > `kosh_clear` each pass: 0 MB. From v317 you need not move it out: a `kosh`
  > declared in the loop's own body, used only as `k[i]` and through `kosh_*`
  > built-ins, is made once by the loop itself (above).

- **(d) `:1439-1440` (`parimana()`, "What it counts") — NO change (R162's
  decision point withdrawn).** "A `kosh` keeps its bytes for the program's
  life, so they never fall." Still true as a `parimana()` statement: a hoisted
  `kosh`'s bytes are held once (by capacity, as before) and never fall; a
  hoisted `mala` is allocated once and counts once. ROUND-171's open question
  (whether `parimana()` falls when the region is released) does not arise —
  nothing is released.
- **(e) `:1448-1450` (`parimana()`, "One number, moving") — NO change.** "A
  block's `nirmmita` comes back at its end; a `kosh`'s bytes do not, even one
  made in the block - its storage is kept for the program's life (§16). … what
  is still not done is giving a `kosh`'s storage back when its block ends - the
  check above reads its header after the block, so the header must stay."
  Still true: the hoist gives nothing back, and the header still stays.

**`docs/MEMORY-MODEL.md`:**

- **(f) Status-box line 5 (the `mandapa` line) — NO change.** "A `mandapa`
  block gives back, when it ends, what `nirmmita` written in its own lines
  took - and nothing else … Three kinds of memory are made in a block's text
  and **only the first comes back**: `nirmmita`, given back; a **`kosh`**,
  not …; a **`mala`**, never …" Still true. The hoist is a loop matter, not a
  block matter.
- **(g) The hoist bullet — ALREADY UPDATED on the branch, needs the same two
  additions as the reference paragraph.** On the branch (`:8` at `c1f516f8`) it
  reads: "**A `kosh` declared as a statement of a `chakra`'s own body is made
  once for the loop** (v317, R172) … A second name, a `prakriya` given it, a
  slice, a declaration under a `yadi`, a `yavat` loop, a `kosh` in a `mandapa`
  inside the loop: made every pass and kept, as before (48 bytes a pass; 64 in
  a program with a `kosh` in a block). **A `mala` declared the same way is made
  once too** (v318, R173), when its name is used in the loop only as `m[i]`
  and its length is the same every pass: each later pass zeroes its numbers.
  800,000 passes of `mala m[8]`: 20 KB resident (v317: 62,516 KB). A `mala`
  given to a `prakriya`, given a second name, or put into a `kosh`: made every
  pass and kept, as before (80 bytes a pass for eight numbers)." Add "or a
  foreign function" after "given to a `prakriya`" in both halves, and
  "returned with `nivartanam`" to each escape list, to match §3.1. The version
  flag (§3.1) applies here too.
- **(h) Status-box `parimana()` line — NO change.** "`nirmmita` outside a
  block and every `mala` count for the whole program; … a `kosh` by its
  **capacity, not its length**" — a hoisted `mala`/`kosh` counts once, as
  before.

**The books — `docs/sutram-book-english.html`, `docs/sutram-book-sanskrit.html`:**

- **(i) The three-kinds list — NO change.** English book `:822-829` ("What a
  block gives back, and what it does not": `nirmmita` given back; a `kosh` not
  given back; a `mala` never given back) and the Sanskrit book's equivalent
  (`:748-753`, "खण्डः किं प्रत्यर्पयति, किं न।") are about a `mandapa` block,
  and are still true. A `mala` declared in a `mandapa`'s own lines is never
  given back — the hoist does not reach it (see §3.6.3 for the wording trap
  this creates).
- **(j) The advice sentence — NEEDS THE QUALIFIER (§3.5).** English book
  `:830`: "So inside a block that is meant to give its memory back, take that
  memory with `nirmmita`." Sanskrit book (`:~754`): "अतः यः खण्डः स्मृतिं
  प्रत्यर्पयितुम् उद्दिष्टः, तस्मिन् `nirmmita` इत्यनेन स्मृतिं गृह्णातु।" Both
  need the qualifier in §3.5.
- **(k) A hoist paragraph is missing from both books.** The books carry no
  hoist paragraph at all: the only v318 change to either book is the footer
  version ("compiler v317" → "compiler v318"). The reference paragraph (§3.1)
  belongs in the books' memory chapter too — in the English book after the
  three-kinds list (`:829`) and before the advice sentence (`:830`), and in
  the Sanskrit book after its three-kinds list (`:753`) and before its advice
  sentence (`:~754`). Until it is added, the books' §19-equivalent chapter
  says a `mala` in a loop leaks 80 bytes a pass, which is no longer true for a
  proven-local `mala` in a `chakra` body. (The books carry no per-pass figures
  for the `kosh`/`mala` leak — no "48 bytes" / "37,516" / "62,516" hits in
  either book — so no figure in the books is stale; the gap is the missing
  paragraph, not a wrong number.)
- **(l) The "block around a loop" discussion — NO change.** English book
  `:815-819` ("a block around a loop gives back nothing until the loop ends …
  Put the block where it ends on every pass — inside the loop, or inside the
  `prakriya` the loop calls … and the peak is 264 KB") is about `nirmmita`,
  and is still true. The Sanskrit book's equivalent (`:741-747`) likewise.

**The R162 paragraph is dropped, not revised.** It was written for ROUND-171
(the region released at block exit). ROUND-171 was never built and is
superseded by the hoist (R172/R173), which does the opposite in one respect:
instead of giving the region back at block exit, it avoids allocating per
pass. The R162 paragraph must not be pasted, and its anchor is withdrawn: the
sentence it amended (`:1291-1292`, "its storage is ordinary memory, which the
block does not reclaim") remains TRUE under the hoist — the hoist reuses, it
does not reclaim — so it needs no amendment. The R162 paragraph's
other-sentence changes (§3.4 (b), (d), (e)) are likewise withdrawn, except one
sentence that survives in spirit ("a `mala` is never given back" — still true,
and already in the branch paragraph as "A block still returns no memory to the
operating system").

### 3.5 The books' advice — still right, or changed by the hoist?

The advice: reference `:1298` — "Inside a block meant to give memory back,
take it with `nirmmita`." English book `:830` — "So inside a block that is
meant to give its memory back, take that memory with `nirmmita`." Sanskrit
book `:~754` — "अतः यः खण्डः स्मृतिं प्रत्यर्पयितुम् उद्दिष्टः, तस्मिन्
`nirmmita` इत्यनेन स्मृतिं गृह्णातु।" (So, in a block intended to give memory
back, take memory with `nirmmita`.)

**It is still right — for its own case — and incomplete.** The sentence is
about a **block** (`mandapa`). Inside such a block, take the memory with
`nirmmita`, because `nirmmita` written in the block's own lines takes scratch
memory: rewound at block exit, zeroed on reuse (reference §19 `:1302-1304`;
R163 Task 3 verified the zeroing covers the requested bytes). A `kosh` or a
`mala` made in the block's own lines takes ordinary persistent memory, which
the block never reclaims. **The hoist changes nothing about what a block does.**
The sentence is not wrong.

What it does not say is what a **loop** does. A student reading the three-kinds
list ("a `mala` made inside a block — never given back", with the 51,200,000-byte
figure) and applying it to a loop body would now be wrong for the proven-local
case. The three cases a student cares about:

1. **A `kosh` in a loop.** Declare it in the loop body. If the loop uses it
   only as `k[i]` (read or written) and through `kosh_*` built-ins (not
   `kosh_ksham`), it is made once and reused: the length is reset each pass,
   the grown buffer is kept. The old advice — declare it outside the loop and
   empty it with `kosh_clear` each pass (reference `:1417`) — still works, but
   it is no longer necessary. If the `kosh` escapes (a second name, given to a
   `prakriya` or a foreign function, returned, sliced), it is made every pass
   as before — then the old idiom is still the way to reuse it.
2. **A `mala` in a loop.** Declare it in the loop body. If the loop uses it
   only as `m[i]` and the length is the same every pass, it is made once and
   reused, its numbers set to 0 each pass — pass 2 reads what a new `mala`
   would read. If it escapes, or the length changes from pass to pass, it is
   made every pass as before (a changing length makes a new `mala` each time
   the length changes; the old one is kept).
3. **A `nirmmita` in a block.** Unchanged. Scratch memory, rewound at block
   exit, zeroed on reuse. The old sentence remains exactly right, with no
   qualifier needed for this case.

**The qualified sentence, paste-ready.** For the reference (append to the
advice sentence at `:1298`, which is the last sentence of the "Nor a `mala`."
paragraph — the hoist paragraph is directly above it, so "above" refers to
§3.1):

> Inside a block meant to give memory back, take it with `nirmmita` — that is
> still the rule for a block. A loop is not a block: a `kosh` or a `mala`
> declared in a loop's own body is reused by the loop itself (above), so the
> block's rule does not decide it.

For the English book (`:830`), with the hoist paragraph added first (§3.4(k)):

> So inside a block that is meant to give its memory back, take that memory
> with `nirmmita`. A loop is not a block: a `kosh` or a `mala` declared in a
> loop's own body is reused by the loop itself — see the paragraph above.

For the Sanskrit book (`:~754`), the same qualifier in Sanskrit (a translation
to be checked by a native speaker before pasting — the books' Sanskrit is the
owner's, and this sentence was not in the tree to copy):

> अतः यः खण्डः स्मृतिं प्रत्यर्पयितुम् उद्दिष्टः, तस्मिन् `nirmmita` इत्यनेन
> स्मृतिं गृह्णातु। चक्रं तु खण्डः नास्ति: चक्रस्य स्वशरीरे लिखितः `kosh`ः वा
> `mala` वा चक्रेण एव पुनः उपयुज्यते — उपरि पश्य।

### 3.6 Ambiguities the paragraph cannot settle (strongest first)

1. **The version numbers.** "v317" and "v318" are staged, not landed (§3.1).
   If the branches land under different numbers, the paragraph's first
   sentence is wrong in its first clause. This is the same class as R162's
   version flag, and it is the only ambiguity that can make the paragraph
   false without any code changing.
2. **The measurements.** "16-20 KB resident on v317, 37,516 KB on v316" and
   "20 KB resident on v318, 62,516 KB on v317" are measurement claims, not
   verified by reading (nothing was run in this round; R163 could not verify
   them either). The test files assert `parimana()` holdings, not resident
   figures. If the RSS numbers do not reproduce on the owner's machine, the
   paragraph's numbers are wrong while its mechanism stays right.
3. **"In a `mandapa`" vs "the loop in a `mandapa`."** The paragraph says "A
   declaration under a `yadi` or in a `mandapa` inside the loop is not
   reached". It does NOT say the reverse, which is also true and easy to
   confuse with it: a `kosh`/`mala` declared in a `chakra` body where the
   `chakra` itself sits inside a `mandapa` IS hoisted (v317 test case
   `in-mandapa`). The books' "inside a block" language does not distinguish
   the two — "a `mala` made inside a block" could be read either way — and the
   paragraph's wording is the only place the distinction is drawn. A student
   who reads "in a `mandapa`" as "lexically inside a `mandapa` anywhere" will
   wrongly conclude the `in-mandapa` case is not hoisted.
4. **The `mala`-in-a-`mandapa` case is untested.** The v318 test file has no
   `mandapa`-in-`chakra` case for the mala (no `mandapa` mention in the file).
   The code path is shared with the `kosh` (`r172_for_enter`'s candidate loop
   iterates direct statements for both), so a mala in a `mandapa` inside the
   loop is not a candidate — but no test asserts it. The paragraph states it
   from the code; the test coverage gap is real.
5. **The FFI statement-call path — determined from the code, not ambiguous,
   but stated here because the brief asked.** "Escapes" DOES cover a `kosh`
   or a `mala` passed to a foreign function as a bare statement: the foreign
   call is an `AST_FUNCALL` node, and the scan's `.args` handler scans every
   argument (§3.2.1). The R162 hole does not apply to the hoist's scan.
   Residual caveat: the scan sees only uses IN the loop's AST. A handover
   through a channel the AST does not show — C writing an address into a
   `nirmmita` buffer it was handed, for example — is outside the scan's view.
   But every Sutram-side handover is an AST node, so the first link of any
   chain is always seen; no such channel is visible in the code. What would
   settle the caveat is the Task 1 attack on the hoist's escape check, not
   this paragraph.
6. **Whether the hoist applies to a `yavat` loop — determined from the code,
   not ambiguous.** It does not: `r172_for_enter` has exactly one call site
   (`:20723` at `c1f516f8`, in `.gs_for`); there is no call in the `yavat`
   codegen. The paragraph's "a `yavat` loop is not a `chakra`" is correct.

---

## 4. Brief corrections

1. **The shared state's "a `mala` escapes a block with no error at all" is a
   simplification of §19.** §19 says returning one is not refused **and**
   putting it in an outer `vitti` is refused (`E_VITTI_PRAKAR`, the kind rule).
   The precise statement is: a `mala`'s address can leave a block (return,
   `kosh` cell, module variable, `prakriya`, foreign function) with no error,
   but it cannot be assigned into a pre-declared number variable. (§2.1.)
2. **Test B as written does not compile — for two reasons unrelated to the
   escape.** The outer `mala row[2]` plus the inner `mala row[2]` is
   `E_DUPLICATE_NAME` (one namespace per function, `r7_declare_new` `:14523`),
   and `likha(table[0][0])` is a syntax error (no double index). The program
   that decides the question drops the outer declaration and reads back
   through a `vitti` — Claude's `ROWS` case is exactly that shape. (§2.4.)
3. **Gate counts, one round later.** v318 `tools/gates.sh` has **81**
   `run_gate` invocations (v317: 80; main: 78). So "84 gates" in the shared
   state is right as a **total** on the staged branch (81 + X11 + doc_counts +
   Windows skip = 84 entries), but the branch's own status line — "84 PASS /
   0 FAIL / 1 NOT-RUN" (`docs/LANGUAGE-REFERENCE.md:3` on v318) — is off by
   one the same way as before: max PASS is **83** (81 + X11 + doc_counts).
   The R159 P4 / R161 / R162 / R163 off-by-one persists, one gate higher.
   (Claude's R173-00 hand-back says the same "84 PASS" — the same off-by-one.)
   On main the reference status line still says "81 PASS" where max PASS is
   80.
4. **The 62,516 KB number — a question, not a contradiction.** 800,000 × 80
   bytes = 62,500 KiB + ~16 KB baseline = 62,516 KB. 80 bytes a pass is the
   `mala m[8]` figure (R161/R163: (8+1)×8 = 72 → align16 = 80), NOT a `row[2]`
   figure ((2+1)×8 = 24 → align16 = 32 bytes a pass → 25,000 KiB at 800,000).
   Which program the 62,516 KB number comes from is not stated in the brief —
   if it is `row[2]` the number does not match; if it is `m[8]` it does. The
   825,016 KB figure for the grown `kosh` on v316 DOES check out
   arithmetically: 800,000 × 1,056 bytes = 825,000 KiB + ~16 KB baseline
   (1,056 = align16((128+4)×8), the final cap-128 allocation after in-place
   extension at the arena cursor). The 37,516 / 50,012 KB nested-case figures
   check out too (800,000 × 48 = 37,500 KiB; × 64 = 50,000 KiB).
5. **The R163 `r108_check_call` line citation — corrected.** See §1.9: `:21556`
   is correct on main; on the staged branches the single call site is `:21957`
   (v317) / `:22014` (v318). The R162 citation was correct for its base
   (main); the R163 citation carried the main-tree line onto the branch it was
   reading. The substantive claim (exactly one call site, expression form
   only) is true on all four trees.
6. **The shared state's "the hoist is safe at all" framing for WS4 — the
   zeroing is built, not assumed.** `r173_mala_begin` (`:11040`) zeroes all N
   elements on reuse (§2.3). Test A prints 99 then 0. The stale-data bug is
   NOT moved into `mala`.

## 5. Could not determine (from source — read-only round, nothing run)

- Whether `tests/r172/test_chakra_kosh.py` and `tests/r173/test_chakra_mala.py`
  actually pass on their branches, and whether the claimed numbers (RSS
  figures, guard 587 byte-identical / 196 refused identically / 0 DIFFER,
  gates 83/84 PASS) reproduce — the test files' assertions are claims, not
  verified results.
- The exact RSS figures in the §19 paragraph (16-20 KB, 37,516 KB, 62,516 KB,
  20 KB) — measurement claims, not re-derived.
- Whether the v318 test file's ROWS (`'11 33 55'`) and RED (`dirty 0`,
  `held 208`) assertions pass — claims, not verified results.
- The exact runtime behaviour of the four escape programs (values, addresses)
  — not run, by rule. The traces are from the emitted code and the check
  routines, not from execution.
- The exact runtime behaviour of `k()` (calling a hoisted `kosh` as a
  function) — not run, by rule. By reading it is an indirect call through the
  descriptor pointer, a crash, identical with and without the hoist.
- Whether any live program passes a `mala` to a foreign `ptr` parameter — the
  FFI door permits it and no test covers it; the scan flags it, so the `mala`
  is not hoisted, but the program itself compiles and hands C the address.
- How many programs in the tree a new `mala`-escape refusal would stop
  (Claude: NOT MEASURED) — counting them needs a tree-wide census, not a code
  read.
- Whether Claude's `k5000.sm` signal-9 kill and Sarvam's 70,000-pass named
  refusal are the same limit reached differently, or different limits — both
  are measurements, neither names the limit in force.
- The exact `r126_ret_kind` value for a `prakriya` whose every `nivartanam`
  returns a `mala` (4 or 5): either way `r126_check_return` does not refuse
  it, and §19 states it is not refused — but the exact recorded kind was not
  traced.
- The `parimana()` `.zero`-path displacement question from R155/R158: still
  open, still needs execution; unrelated to this round, noted only so it is
  not mistaken for resolved.

---

*Delivered as a read-only round: report + `r164.json`. No files changed in the
repository. Sarvam's false-claim count stands at 59 (per the R164 brief).*
