# ROUND-148: paper review (read-only, nothing run)

**Base read:** `origin/main` at `0fb61357` ("ROUND-149: closure answer — read-only, nothing run"), 2026-11-08.
**Files read:** `src/sutram_compiler.asm` (33,554 lines) and the `%include`d files
(`src/r23_capabilities.inc`, `src/r32_ffi.inc`, `src/r25_phal.inc`,
`src/r45_debug.inc`, `src/r65_arena.inc`), `Sarvam-to-Muse/ROUND-148-PAPER-REVIEW.md`,
`Sarvam-to-Muse/CANCELLATION-146-147.md`, `Muse-to-Sarvam/ROUND-149-CLOSURE-ANSWER.md`,
the gates (`tests/r137/test_slice_number.py`, `tests/r134/test_one_predicate.py`,
`tools/gates.sh`), the R147 slice programs (`tests/r147/slices/01–14`), and the
R135/R136 probe files and reports in `Muse-to-Sarvam/`.
**Method:** four read-only research tracks (one per task) plus synthesis. Nothing
compiled, assembled, run, or executed; nothing written into the repo; nothing uploaded.
Every factual claim cites file + line at commit `0fb61357`. Where a claim is a
reading inference rather than a measured result, it says so. Where a question
would need execution, the answer is "I could not determine this from source".

## Corrections to the brief (found while reading)

Four numbers in the brief do not match the tree. None of them changes the
substance of the round, but the record should carry the corrected figures.

1. **There is no `r157`.** A grep over `src/` returns zero hits; the only mention
   in the tree is the brief itself (`Sarvam-to-Muse/ROUND-148-PAPER-REVIEW.md:29`).
   The check the brief describes — "the expression walk, with its own stack" —
   is `r137_check_stmt` (`src/sutram_compiler.asm:28402`), walking on its own
   stack `r142_wstack` (defined at `src/sutram_compiler.asm:1565`, pushed by
   `r142_push` at `28677`), with depth in `r15` and a budget that refuses on
   exhaustion (`28415–28417`, `R143_WALK_BUDGET`).
2. **There are 146 `call gen_expr` sites, not 133.** ROUND-149 counted only
   `src/sutram_compiler.asm` (133, verified by grep). Thirteen more live in the
   `%include`d files, which are part of the same assembly unit (included at
   `32623–32630`): `r23_capabilities.inc` 4, `r32_ffi.inc` 3, `r25_phal.inc` 2,
   `r65_arena.inc` 4. There is also one `jmp gen_expr` (`9035`,
   `r103_emit_lkhb_num`, a synthesized `BN_LKHB(AST_NUM)` literal) in addition
   to the `call` sites — still through the wrapper.
3. **The R137 gate has 87 checks, not 64** (89 when the mutants run). See Task 4.
4. **There is no `r23_check_call`.** A grep over `src/` finds no such label. The
   actual call-side checks are `r129_check_call` (`28771`), `r126_check_untyped_arg`
   (`29204`, via `gen_typed_call_arg`), `r108_check_call` (label `12715`, called
   at `21503`), and `r23_check_return` (`src/r23_capabilities.inc:508–513`).

## Task 1 — the fourteen shapes, traced through the checks

**How to read the table.** *Direct (walk)* = `r137_check_stmt` itself refuses with
`E_VIBHAG_ANKA` (`r137_hdr`, `src/sutram_compiler.asm:629`) via `.num` with
`r10 = 0`. *Deferred (door)* = the walk's `.num` sees a slice at a "door"
(`r10 = 1`), finds `r134_holds_kosh` = 1 and returns without refusing
(`28606–28617`), leaving the refusal to the door check, which fails via
`r126_fail_door` (`28244`) — its slice branch prints `E_KOSH_VIBHAG`
(`r134_vb_hdr`, line `638`). *By construction* = the refusing check was designed
for that position/kind; *by coincidence* = caught only incidentally. **No shape
below relies on coincidence alone**, but shapes 3 and 12 are caught at a
different point than the shape names, and shape 8 is covered by code rather
than by the comment that names its door.

The shared predicate: `r134_holds_kosh` (`28343`) is a `kosh`, or a slice of a
`kosh`, of a slice name, or of a `vibhag` parameter. Its slice half,
`r134_kosh_slice` (`28356+`), accepts an `AST_SLICE` whose base is a kosh
(`is_kosh_var`) or a slice name (`r23_is_slice_var`), and an `AST_VAR` that is
a slice name. Note the conservatism: the `.name` branch (`28368–28376`) treats
*any* slice name / `vibhag` parameter as a kosh borrow, so the doors refuse
even a `mala` slice passed to an untyped parameter. The doors are stricter
than the escape requires — by construction (R134 header, `28339–28342`: a slice
"goes through no door the kosh may not").

| # | Shape | Which check catches it | Error | Certain or incidental? |
|---|---|---|---|---|
| 1 | array cell — `box[0] = k[0:1]` | Door: `r126_check_assign`, `.cell` branch (`29084–29100`). Walk `.assign` (`28556`): target is `AST_INDEX`, not `AST_VAR`, so `r10=1` and `.num(value)` defers. `.gs_assign` calls `r126_check_assign` (`19442`); target `AST_INDEX`/`AST_FIELD` falls into `.cell`, which calls `r134_holds_kosh` on the value and fails via `r126_fail_door`. | `E_KOSH_VIBHAG` | **By construction.** R134 header names "a cell" as a door; `r126_check_assign` comment (`29083`): "a kosh goes into no cell, field or global." |
| 2 | untyped parameter | Door: `r126_check_untyped_arg` (`29204–29234`), called on the scalar path of `gen_typed_call_arg` (`27281`) *before* `gen_expr`/conversion. Walk `.funcall` (`28480`): `func_param_type` ≠ `PARAM_VIBHAG`, so `.num(arg)` with `r10=1` defers. `PARAM_RAW` = 0 (line `69`) < `PARAM_KOSH` = 2, so the scalar path runs and door-checks unconditionally. | `E_KOSH_VIBHAG` | **By construction.** R134 header lists "an untyped (or unknown, or function-value) parameter" as a door. |
| 3 | untyped return | **Two return doors, not the walk.** Walk: `AST_RETURN` falls to `.gen`, which only pushes fields; a slice child reaches `.slicebounds`, which checks only its bounds — the walk never refuses a return value. Door 1: `r23_check_return` (`src/r23_capabilities.inc:508–513`, called at `20910`): `r23_expr_is_slice` is true for a slice literal *and* for a slice name (marked by `r23_mark_slice_decl`, `19143`, or vibhag-param marking, `18541`). Door 2: `r126_check_return` (`29238`, called at `20905`): for `siddhi/dosh` returns (`[rbx+16]≠0`, parser `15819`) any `r134_holds_kosh` value is refused; for a plain return, a ternary returning a slice has `r126_value_kind` 6 → `.bad`. Note: `r126_check_return`'s plain path *alone* would pass a direct slice from a number-returning function (slice kind 1 vs return kind 5 → `.out`, `29260–29266`) — it is `r23_check_return` that closes the direct case. | `r23_msg_slice_return` (Door 1); `E_KOSH_DVARA` header text (Door 2) | **By construction** for Door 1 (comment: "a slice lives in the frame of the function that made it, so returning one is an error"). Door 2's plain-path coverage of slices is incidental — it refuses via kind-6, not by recognising a slice. |
| 4 | function value | Door: `r126_check_untyped_arg` (same as #2). Walk `.funcall`: `r23_call_is_indirect` true → `.fnum` → `.num(arg)`, `r10=1`, defers (`28488–28499`). Generation: indirect calls bypass the foreign path (`r23_call_is_indirect`, `21508`) and reach `gen_typed_call_arg`, whose scalar path calls the door; the door itself handles indirect explicitly (`29210`: "through a function value: its parameters have no kinds" → `.known` path, which still calls `r134_holds_kosh`). | `E_KOSH_VIBHAG` | **By construction.** Both the walk and the door have an explicit indirect branch. |
| 5 | module variable — `vitti g = k[0:1]` | Door in `r56_gen_global_initializers` (`18330–18365`): `r137_check_stmt` on the global `AST_DECL` node (`18348`) — the walk alone does not refuse it (a `DECL` falls to `.gen`; the slice child only gets its bounds checked) — then `r134_holds_kosh([rbx+16])` (`18351`), the init expression (`AST_DECL` layout `[name][init][size][type]`, `19139`), fails via `r126_fail_door`. | `E_KOSH_VIBHAG` | **By construction.** R141 comment at `18341–18346` describes this exact door ("the module-vitti door for the bound value"). |
| 6 | record field | Door: `r126_check_assign`, `.cell` branch (`29084–29100`) — the *same* branch as #1: `AST_FIELD` (target layout `[AST_ASSIGN][target=AST_FIELD][value]`, `19836`) falls into `.cell` with `AST_INDEX`. Walk `.assign` defers identically (`r10=1`). | `E_KOSH_VIBHAG` | **By construction.** R134 header names "a field" as a door. |
| 7 | raw memory | Door: `r126_check_writemem` (`29178–29196`), called at `26610` in `.ge_writemem` before either operand is generated. It calls `r134_holds_kosh` on both the address (`[rbx+16]`) and the value (`[rbx+24]`). Walk `.wmem` (`28551`): `r10=1`, `.num` on both, defers. | `E_KOSH_VIBHAG` | **By construction.** Comment (`29177`): "a kosh is neither the address nor the value." |
| 8 | decimal parameter | Door: `r126_check_untyped_arg` (same as #2). `PARAM_DASHAM` = 1 (line `70`) < `PARAM_KOSH` = 2, so `gen_typed_call_arg` takes the scalar path and calls the door (`27281`) *before* `gen_expr` and before `emit_scalar_type_conversion` — so the R136 failure mode (int-to-float conversion destroying the pointer bits) cannot happen first. Walk `.funcall` defers (`PARAM_DASHAM` ≠ `PARAM_VIBHAG`). | `E_KOSH_VIBHAG` | **By construction in effect, by naming accident.** The door's name/comment say "untyped", but the scalar-path call site is unconditional for every non-kosh parameter type, so `dasham` is covered by the code, not by the comment. |
| 9 | arithmetic — `k[0:1] + 0` | **Direct: `r137_check_stmt`, `.binop`** (`28502–28514`). `r10=0`; `.num` on both operands; a slice with `r10=0` goes to `.bad` (`28634–28645`). This is the headline R137 rule (header `28388–28396`: "a slice is used as a number… an operand of any binary or unary operator… is refused (E_VIBHAG_ANKA)"). | `E_VIBHAG_ANKA` | **By construction.** The check exists for exactly this operation. |
| 10 | module initializer — `vitti g = make_kosh()` | Door in `r56_gen_global_initializers` (same as #5, `18351–18358`): `r134_holds_kosh` on the `AST_FUNCALL` init → `r126_is_kosh_value` → `r126_value_kind` `.call` → `r126_ret_kind` (`27923`) returns kind 2/3/6 for a kosh-returning prakriya → fails via `r126_fail_door`. (The R141 comment at `18343` names this exact program.) | `E_KOSH_DVARA` (not `E_KOSH_VIBHAG` — `r134_kosh_slice` returns 0 for a `FUNCALL`, so the non-slice branch of `r126_fail_door` runs) | **By construction** (R141 comment). One qualification: the *mechanism* (`ret_kind` 2/3/6 ⇒ refused) was verified, but `make_kosh`'s own definition was not read to confirm its `ret_kind` is a kosh kind; the R141 comment asserts the case by name. |
| 11 | comparison as index (e.g. `a[k[0:1]] == 1`) | **Direct: `r137_check_stmt`, `.index`** (`28502–28506`). The comparison's `.binop` calls `.num` on the `AST_INDEX` operand, which passes (an index node is not itself a slice and `r134_holds_kosh` of it is 0), but the walk then descends via `.gen` into the index node, whose `.index` handler calls `.num(index)` with `r10=0` → `.bad`. A slice compared *directly* (`k[0:1] == 0`) is refused one step earlier by `.binop` itself. | `E_VIBHAG_ANKA` | **By construction** (`.index` comment: "an index is a number"), reached through the generic walk's descent — the walk's `.gen` default (pushing fields 8–64) is what delivers the index node to its handler. |
| 12 | through two functions in sequence (`f(g(k[0:1]))`, or via a name `t = …; h(t)`) | **Caught, but at the first violating leg — never at the outer call itself.** (a) Inner untyped: inner arg refused by #2's door. (b) Inner `vibhag`: allowed as an argument, but the slice cannot come back out — `g` cannot return its vibhag parameter (`r23_check_return`, param marked a slice var at `18541`), a fresh slice literal, or a slice name bound inside it (marked at `19143`); a ternary return of it has kind 6 and is refused by `r126_check_return` (`29260–29266`). (c) Outer `vibhag` receiving a `FUNCALL` result: `gen_typed_call_arg` `.r23_gtca_slice` (`27336`) — not a slice and not a `VAR` → `r23_slice_base_fail` (compile error). (d) Via a name: `t = k[0:1]` is refused at the binding by `r127_check_slice_value` (`28739`, called from `r126_check_decl` `29054` and `r126_check_assign` `.local` `29126`) with `E_KOSH_VIBHAG`. The outer-call check itself is *blind* to a `FUNCALL` result: `r134_holds_kosh`/`r126_value_kind` only see `ret_kind` 5/2/3/6, never kind 1 (slice), and `r129_check_call`'s `r129_is_kosh_slice` accepts only `AST_SLICE`/`AST_VAR` (`28883`). The closure is therefore inductive, resting on the return checks in (b). | `E_KOSH_VIBHAG` / slice-return error / `r23_slice_base_fail`, by leg | **By construction per leg, with an inductive caveat** (see "Could not determine"). If any callee could return a slice, the outer untyped door would pass it — no such callee path was found in the return checks as read, but that is a property of two checks, not of the outer call. |
| 13 | stored in a kosh element (`kosh_push(k, k[0:1])`) | Door: `r126_check_builtin` (`29140–29200`), called at `22003` in `.ge_call` (statement builtins reach it via `.gs_call` → `gen_expr`, `21068`). Walk `.call` (`28515`): `r10=1`; the slice in a non-first argument defers via `.num`. The door loops all args: arg 0 (the kosh) is allowed only for builtins `BN_PANKTILEN`–`BN_KOSHDEQUEUE` (36–45) except `BN_SETCHAR` (41) — `BN_KOSHPUSH` = 37 is in range; any later argument with `r134_holds_kosh` = 1 → `.bad` → `r126_fail_door`. (A `k[i] = k[0:1]` spelling is #1's cell case instead.) | `E_KOSH_VIBHAG` | **By construction.** R134 header lists "a builtin's other argument" as a door; `r126_check_builtin` comment: "a kosh is the first argument of a kosh builtin, nothing else." |
| 14 | inline assembly (`AST_NISHKRIYA`) | **No check — none is needed, by construction.** An `AST_NISHKRIYA` node is `[type][hex_str_ptr][0][0]` (parser `15077–15081`; generation `20141`): `.gs_nishkriya` parses hex digit pairs from the literal string and emits bytes verbatim. No expression is evaluated, so no slice value can hide in it. In the walk it falls to `.gen`, which pushes fields 8–64; field 8 is a string pointer outside `ast_heap`, so the walk skips it (`28422–28429`). This matches the ROUND-149 answer. | — (nothing to refuse) | **By construction** (no expression position exists in the node). |

**Task 1 verdict.** Every one of the fourteen shapes has a check, and none relies
on coincidence alone. The two places the record should be careful: shape 3 is
caught by the return doors, not by the walk the brief names; and shape 12's
closure is inductive — it rests on the return checks refusing every slice
return, because the outer call cannot see through a `FUNCALL` result.

## Task 2 — is there a fifteenth?

### The closure argument (verified, with corrections to ROUND-149)

**No path was found by which a value reaches code generation without passing
`r137_check_stmt`.** The closure argument holds — but it rests on the two-layer
door, not on `gen_expr` alone, and ROUND-149's wording needs two corrections.

*Verified anchors.* `gen_expr` `21415`, `r142_gen_expr_body` `21432`,
`gen_stmt` `18854`, `r142_gen_stmt_body` `18872`, `gen_code` label `17984`
(driver calls it once, line `3151`), `r56_gen_global_initializers` `18330`,
`r137_check_stmt` `28402`, `r134_holds_kosh` `28343`, `r142_push` `28677`.
`call r142_gen_expr_body` / `call r142_gen_stmt_body` occur only at `21425`
and `18863` (the two wrappers); the only other reference is
`jne r142_gen_expr_body` at `21417`, inside `gen_expr` itself. `gen_stmt` is
called only from `r45_gen_block_body` (`18822`) and twice in
`src/r45_debug.inc` (`431`, `668`, on compiler-synthesized debug statements)
— all through the wrapper. `r142_checked` is raised in exactly three places,
each immediately after a walk: `gen_stmt` `18859`, `r56` `18361`, `gen_expr`
itself `21423` (test-build `%ifndef R142_MUTANT_NO_*` guards aside).

*Correction 1 — the count.* 146 `call gen_expr` sites, not 133 (see the
corrections section). All 13 extra sites sit in helpers whose callers are only
inside `r142_gen_stmt_body` / `r142_gen_expr_body` (e.g. `r23_gen_slice` ←
`21493`, `r26_gen_handle` ← `18954`, `r33_gen_foreign_funcall` ← `18989` /
`21517`, `r73_gen_scratch_nirm` ← `23639`, `r75_gen_neg_check` ←
`src/r65_arena.inc:425`, `r127_emit_grow_check` ← `src/r65_arena.inc:596,682`,
`emit_array_bounds_check` ← `19793` / `21890` + `src/r23_capabilities.inc:664,671`)
— i.e. under `r142_checked` — **except one**: `r82_param_checks`, called from
`gen_all_functions` at `18662`, *before* `gen_block` (`18667`), with the flag
at 0. Its synthesized `AST_CALL` (`r82_emit_check:11034`) therefore relies on
the `gen_expr` fallback walk, not the flag. Still checked, but ROUND-149's
"under the flag" phrasing needs that exception.

*Walk coverage, verified.* `.gen` pushes fields at offsets 8–64, and
`AST_NODE_SIZE` is 72 (line `34`), so that covers every field of a plain node.
Slice bases are always names: the only two `AST_SLICE` constructions are the
parser (`17539`, base = the saved name pointer, `17495–17539`) and the
synthetic whole-array slice in `gen_typed_call_arg` (`27342`, from an
`AST_VAR` name). The 6-argument cap is enforced in the walk (`.call` /
`.funcall` stop at 6, `28474–28505`) and the parser refuses a 7th
(`msg_err_arg_limit`, line `381`; kind set at `15280`, `17600`).

### The fifteenth — a slice passed to a foreign (FFI) function

**Found by reading: a slice passed to a declared foreign function.** This route
*does* pass through the walk; it escapes because the walk defers a kosh slice
to a door that does not exist for FFI. It is a predicate/door gap, not a path
that skips the check — the same defect class as the known `keep(x)`
laundering, but a distinct route not among the fourteen shapes.

The chain, as read (`src/r32_ffi.inc`, `r33_gen_foreign_funcall` at `666`,
reached from statement `18989` and expression `21517`, both under the flag):

- `r33_gen_foreign_funcall` generates every argument through `gen_expr`
  (`709`, `727`, `737`) but performs **no slice/kosh check of its own**: the
  file contains no `r134_holds_kosh`, no `r126_check_*`, no
  `r23_expr_is_slice`, no `r129_is_kosh_slice` — only `is_kosh_var` checks at
  `694` and `723`, which catch an `AST_VAR` kosh name only. A direct slice
  node `k[0:1]` (or a slice variable) as an argument to a foreign function
  declared `i64` or `ptr` (kinds per `src/r32_ffi.inc:16`) therefore reaches
  the foreign call as the descriptor address.
- Walk: `.funcall` (`28474–28505`) calls `.num` on the argument
  (`func_param_type` returns 0 / `PARAM_RAW` for a foreign name not in
  `func_defs`, `26945–26980`, so the vibhag exemption never applies); `.num`
  (`28590–28620`) sees the slice but, with `r10=1`, defers a kosh slice to
  the door (`r134_holds_kosh` = 1 → return, no refusal). A mala slice *is*
  refused here. (This corroborates the Task 1 reading: the foreign path never
  calls `r126_check_untyped_arg` or `r134_holds_kosh` — its scalar-argument
  path checks only `AST_STR` and `AST_VAR`-that-is-a-kosh, `src/r32_ffi.inc:666–730`.)
- `r129_check_call` runs first (`18994`, `21502`), but for a foreign name
  `rfx3_fn_index` is −1, so it takes the `.unknown` path, which refuses a
  kosh slice **only beside another argument containing a call**
  (`28771–28880`; `r129_is_kosh_slice` `28883`). A lone slice argument — or a
  slice plus plain numbers — passes.
- `r108_check_call` (`21503`) only guards block-koshas and returns at once
  when `r108_bk_n` is 0 (`12714–12720`).
- The foreign callee receives the descriptor address as an integer/pointer; a
  `ptr`/`i64` return comes back in `rax` (`.result`, `src/r32_ffi.inc:870`)
  and can be stored in a `vitti` — the `.assign` walk skips `.num` on the
  value when the target is a plain `AST_VAR`, and `r126_value_kind` of a
  foreign call is raw 5 (`27868–27890`, `AST_FUNCALL` → `r126_ret_kind` →
  unknown name → 5). The statement form `f(k[0:1]);` needs no return at all:
  the address has left the program's control. FFI requires `--ffi`
  declarations (`r32_ffi_path`, `13940–13941`), so this route needs a foreign
  declaration file — it is still a real language feature.

**Status of this finding.** Source-level facts only: the compiler accepts the
call, emits the descriptor address as the argument, and no check in the chain
refuses it. **I could not determine its runtime effect from source** — whether
a foreign function in practice retains/returns the descriptor usefully, and
what the stale-read consequence is at runtime. That needs execution, which this
round forbids. The finding is therefore a *fifteenth shape by reading*, not a
measured escape.

### The non-storage, non-arithmetic shapes

- **Type conversion — no bypass.** There is no conversion AST node and no
  conversion builtin. All conversion is `emit_scalar_type_conversion`
  (`27360–27370`, `cvtsi2sd` / `cvttsd2si` emitted as bytes), applied to the
  value already in `rax` *after* `gen_expr` on the original node:
  `gen_typed_call_arg` scalar path (`27281–27290`, after
  `r126_check_untyped_arg` + `gen_expr`), declaration (`19187–19200`),
  index-assign (`19685–19705`), return (`20930–20940`). The converted value
  is the same walked node; conversion cannot smuggle an unwalked value in.
  (The known R136 dasham-param crash is conversion *destroying* pointer bits
  of a value the walk already passed — a different defect.)
- **A builtin that returns its argument — none exists.** The `AST_CALL`
  dispatch (`22003–22104`) lists every `BN_*` handler; none returns its
  argument unchanged. `kosh_peek` / `kosh_pop` / `kosh_dequeue` share
  `.ge_call_koshpop`, which loads an *element* from kosh storage (requires an
  `AST_VAR` kosh, else `.ge_call_kosh_bad`); `pankti_len` (`23697–23710`)
  returns a length (`gen_expr` on the slice, then `mov rax,[rax+8]`). The only
  "return its argument" entities are user prakriyas (`keep(x)` — known) and
  foreign functions (above).
- **A parameter passed by reference — does not exist.** `PARAM_*` has only five
  kinds (`69–73`: raw, dasham, kosh, kosh-dasham, vibhag); all Sutram
  parameters are by value (scalars in registers, kosh/slice as one qword).
  The only address-passing is foreign `ptr` parameters (`r33` `.ptr`: a kosh
  `AST_VAR` is dereferenced to its elements pointer after `gen_expr`) and raw
  `writemem` / `nirmmita` memory.
- **`AST_NISHKRIYA` — no slice can hide in it.** The node is
  `[AST_NISHKRIYA][hex_str_ptr][0][0]`, built at parse time (`15077–15081`)
  from a *string literal token*, not an expression. The statement handler
  (`20141+`) parses hex digit pairs from that literal and `emit_byte`s each;
  it never calls `gen_expr` and evaluates nothing. The walk's `.gen` push of
  field 8 is a string-pool pointer, which fails the `ast_heap` bounds test
  (`28414–28422`) and is skipped. (The bytes are arbitrary user-written
  machine code by design — an intentional escape hatch from language safety,
  not a value reaching codegen through an expression. The R67 pure-stack-pair
  opt-in at `20141+` only suppresses emission.)
- **Writemem — closed at the path level.** Statement form delegates to
  `gen_expr` (`21061–21065`); expression form (`26607–26640`) generates
  address and value both via `gen_expr`, after `r126_check_writemem`
  (`29178`, refuses a kosh as address or value) and the walk's `.wmem`
  (`28549`, `r10=1` door on both).
- **Nirmmita — closed at the path level.** `.ge_call_nirm` (`23625–23629`)
  generates the size via `gen_expr`; the result is a fresh mmap pointer, not
  a slice. Storing a slice *into* nirmmita memory is the known R136 shape 7
  (via `writemem` / index store) — those stores pass through the walk; whether
  the door refuses them is Task 1's completeness question, not a path bypass.

Also checked: all compiler-synthesized `gen_expr` / `gen_stmt` arguments
(`r103:8974` `AST_VAR` from a budget-entry name; `r82:11034`, `r80:11834` /
`11927`, `r65:32286` `AST_NUM` literals; `r121:33072` `AST_STR` constant
message; `src/r65_arena.inc:464` `BN_LIKHA(AST_STR)` constant; `r23:537`
`AST_VAR` from a given name; `src/r45_debug.inc:431/668` debug counter/summary
nodes) are compiler-built literals/internal names, never user expressions.

### Task 2 verdict and residuals

**Closure:** every expression reaches code generation through `gen_expr`
(single driver call `gen_code` `3151` → `r56` / `gen_block` /
`gen_all_functions` → `gen_stmt` per statement), and every `gen_expr` call
either runs under `r142_checked` raised by a preceding `r137_check_stmt`
walk, or runs the fallback walk itself (`gen_expr` `21415–21430`,
`r142_value_mode` epilogue in `.walked`). The two bodies are reachable only
through the two wrappers. That is what the closure rests on — **not** on
`gen_expr` alone, and **not** on the check being complete for every shape:
the known escapes (`keep(x)`, global/field/raw-memory stores, dasham
conversion) all *passed* the walk; the walk's predicates
(`r23_expr_is_slice`, `src/r23_capabilities.inc:473–485`, which recognises
only a literal `AST_SLICE` or a slice-named `AST_VAR`; `r126_value_kind`,
`27868–27890`, which knows `VAR` / `SLICE` / `FUNCALL` / `TERNARY` and
returns raw 5 for anything else, including `AST_CALL`) do not recognise a
slice laundered through a call, a builtin, or a foreign function. The FFI
route above is a new member of that class.

**Could not determine from source (Task 2 residuals):**

1. The walk skips `AST_BLOCK` and `AST_FUNCDEF` (walk at `28402`), relying on
   every block reaching `gen_block` → `gen_stmt`. The `gen_block` call-site
   list was verified (`18110`, `18667`, `20098`, `20117`, `20297`, `20628`,
   `20836`, `21031`, `src/r25_phal.inc:370,387`) but not every `AST_BLOCK`
   construction site (e.g. synthesized mandapa blocks at `8271` / `8333` /
   `8400`) was traced to a `gen_block` call.
2. `r58_fold_tree` runs inside `r142_gen_expr_body` before dispatch
   (`21436–21440`); only its head was read (`31541+`) — it folds `BINOP`s of
   two `NUM` literals and identity cases, returning already-walked sub-nodes,
   but not every fold branch was verified.
3. `r65_root_globals` (`18102`), `backpatch_calls`, and
   `r56_patch_global_storage` were not line-audited for value emission (they
   deal in globals/call patches, not expressions, as far as read).
4. The R143 walk-budget arithmetic (349,521 vs. the tree bound, lines `42–50`
   of the R143 material) was not independently verified.
5. Test-build `%ifndef R142_MUTANT_NO_STMT_CHECK / NO_GLOBAL_CHECK`
   (`18855`, `18348`) removes the checks when defined; the closure assumes a
   normal build.
6. For the FFI shape: its runtime effect — **I could not determine this from
   source** (see above).

## Task 3 — the probes, on paper

### First, a correction the files force

The brief (`Sarvam-to-Muse/ROUND-148-PAPER-REVIEW.md:78`) cites
`139537424244064` as its example. That number **does not occur in any R135/R136
probe or report**. It is Sarvam's own v308 measurement of ChatGPT's arithmetic
probe, recorded in prose only:

- `Sarvam-to-Muse/ROUND-142.md:10` — `arithmetic laundering (ChatGPT's probe)
  -> 139537424244064 exit 0`, and `:14` — "Those are not element values.
  `139537424244064` is about `0x7EEC_...` - a heap address"; `:16` —
  "`k[0:1] + 0` takes the slice's DESCRIPTOR ADDRESS as an integer and adds
  zero."
- Same pair repeated in `Sarvam-to-Muse/ROUND-144.md:27` and
  `Sarvam-to-Muse/ROUND-145.md:36–37` (direct variant `139536700079456`); also
  `Sarvam-to-ChatGPT/ROUND-208.md:16–17` and `Sarvam-to-Claude/ROUND-138.md:10–16`.
- **No `.sm` source file for the arithmetic probe exists anywhere searched**
  (`Muse-to-Sarvam/`, `Sarvam-to-Muse/`, `~/workspace/r138/`). Its expression
  is known only as prose (`k[0:1] + 0`, through a function vs direct). So there
  are no "two versions" of it to compare side by side, and no "later corrected
  version" of it in the files.

The pair the brief's lineage actually asks about is named explicitly in its
predecessors — `ROUND-142.md` WS3, `ROUND-144.md` Task 6, `ROUND-145.md`
Task 6: *"ChatGPT noted your R135 probe printed the descriptor's element
address rather than an element, and your R136 probe was sharper."* That pair
is below, and R136 itself states the contrast
(`Muse-to-Sarvam/ROUND-136-FOUR-ESCAPE-PROBES.md:51–53`).

### The two versions, side by side

**Version 1 (faulty) — R135, `Muse-to-Sarvam/r135_ws1_return_launder.sm`:**

```sm
prakriya launder(x) {
    nivartanam x
}
mukhya() {
    kosh k[4]
    kosh_kship(k, 10)
    kosh_kship(k, 20)
    vitti obstacle = nirmmita(16)
    vitti t = launder(k[0:1])
    kosh_kship(k, 30)
    kosh_kship(k, 40)
    kosh_kship(k, 50)
    k[0] = 99
    likha(t[0])          <- ONE dereference
    likha(k[0])
}
```

Output, per `Muse-to-Sarvam/ROUND-135-INDIRECT-SLICE-AND-INTERRUPTED-INSTALL.md:127–128`
and `r135.json`: *"Compiled, exit 0, printed `131351504224288` then `99`. The
first number is not an element — it is a pointer read as data."*

**The diagnostic that explains it — R135,
`Muse-to-Sarvam/r135_ws1_return_launder_diag.sm`:**

```sm
    vitti t = launder(k[0:1])
    likha(t)
    likha(t[0])
    likha(t[1])
    likha(k[0])
```

Output, per ROUND-135 report `:133–136`:

```
t     = 140728493615824  (0x7ffde7df2ad0)
t[0]  = 139932844687392  (0x7f44a7800020)
t[1]  = 1
k[0]  = 10
```

And `:139–146`: *"`t` is a **stack address** (`0x7ffd…`) — the slice descriptor
itself, living in the caller's frame. `t[0]` is the **element address**
(`0x7f44…`, the arena). `t[1]` is the length, 1. So a slice value is a pointer
to a two-word descriptor in the maker's frame… The earlier run's garbage number
(`131351504224288` = `0x7776a7c00020`) is the same thing under ASLR: the element
address printed as an integer."* Corroborated in `~/memory/2026-11-06.md:102`.

**Version 2 (correct) — R136, `Muse-to-Sarvam/r136_ws1_untyped_return.sm`:**

```sm
prakriya keep(x) {
    nivartanam x
}
mukhya() {
    kosh k[1]
    kosh_kship(k, 7)
    vitti obstacle = nirmmita(16)
    vitti t = keep(k[0:1])
    kosh_kship(k, 8)
    k[0] = 99
    vitti addr = t[0]
    likha(addr[0])       <- TWO dereferences
    likha(k[0])
}
```

Output, per ROUND-136 report `:38` and `:51–53`: *"Compiled, exit 0, printed
`7` then `99`… R135's version printed the descriptor's first word (a garbage
address). This version double-dereferences through the returned value
(`vitti addr = t[0]`, `likha(addr[0])`) and reads the **element** — the old
value, after the source grew and changed."*

### Question 1 — what was different, and why the first printed an address

- **Setup identical in kind:** an untyped identity function (`launder` /
  `keep`, `nivartanam x`), `vitti t = <fn>(k[0:1])`, then growth, then
  `k[0] = 99`. Only cosmetic differences: element values 10/20/30/40/50 vs
  7/8, `k[4]` vs `k[1]`, function renamed `launder` → `keep`.
- **The one substantive change is the read-back: one dereference → two.**
  R135 line 14 does `likha(t[0])`; R136 lines 11–12 do `vitti addr = t[0]`
  then `likha(addr[0])`.
- **Why R135 printed an address:** a slice value held in an untyped `vitti`
  is a pointer to a two-word descriptor `[element-address, length]` in the
  maker's frame (ROUND-135 `:139–146`). `t` is that descriptor pointer (a
  stack address); `t[0]` loads descriptor word 0, which *is* the raw element
  address. `likha` prints whatever qword it is given with no type information,
  so the address prints as a plain decimal integer (`131351504224288` =
  `0x7776a7c00020`). R136's extra dereference loads the qword *at* that
  address — the element itself — giving the genuine old value `7`.
- **Note:** R135 already understood this — the diagnostic probe decomposes
  `t` / `t[0]` / `t[1]` / `k[0]` correctly. The R136 change was applying the
  diagnostic's second dereference to the verdict probe.

### Question 2 — which other probes might have printed an address as a value

Audit of every `likha` in the 18 R135 + 13 R136 probes, by what the printed
expression is. **Important nuance: in the delivered reports, no address print
was actually misreported as an element value — R135 and R136 both label them
as addresses. The flaw is in probe design / raw output, where a bare number
carries no label.**

**Actually printed an address (observed; correctly labelled in the report, but
the probe's verdict rests on an address, not an element):**

| Probe | Print | Output | Status |
|---|---|---|---|
| `r135_ws1_return_launder.sm:14` | `likha(t[0])` | `131351504224288` | Address; proves escape/laundering, **not** a stale read |
| `r135_ws1_return_launder_diag.sm:10–11` | `likha(t)`, `likha(t[0])` | `140728493615824`, `139932844687392` | Intentional decomposition, labelled word-by-word — safe |
| `r136_ws1_cell_minimal.sm:8` | `likha(box[0])` | `140733170577648` — "a stack address (`0x7ffd…`)" (ROUND-136 `:34`) | Address; proves the descriptor persisted, **not** an element read. Its sibling `r136_ws1_cell_write.sm` (double-deref write form, prints genuine `7`, ROUND-136 `:35`) is the one that proves the stale write |
| `r136_ws2_dasham_diag.sm:2` | `likha(d)` inside callee | `140724879295072.000000` (ROUND-136 `:79–85`) | Address as a float — value preserved, bit pattern destroyed (`0x4270…`, not the pointer `0x7ffd…`) |

**Same flaw in the blocked round's staging (corroboration, not a new probe):**
`~/workspace/r138/probes/r138_ws1_cell_minimal.sm` is a verbatim copy of the
R136 cell probe, and its staged log
`~/workspace/r138/stage/probe-results/r138_ws1_cell_minimal.log:19` records
output `140737185282080` — the same `likha(box[0])` address print under a
different ASLR instance.

**Designed to print an address but never ran (latent same flaw — no misreading
occurred):**

- `r135_ws1_return_direct.sm:7` `likha(get_slice(k))` and
  `r135_ws1_return_passthru.sm:8` `likha(identity(k[0:1]))` — print the slice
  value itself (descriptor pointer); both compile-refused, never printed.
- `r135_ws1_slice_in_kosh_readback.sm:8` `likha(s)` — prints the slice value;
  runtime refusal at the store, never printed (ROUND-135: store itself refuses
  in all three variants).
- `r135_ws1_slice_in_kosh.sm:13` `likha(s[0])` and
  `r135_ws1_slice_store_direct.sm:7` `likha(s[0])`,
  `r136_ws2_cond_assign.sm:8` `likha(s[0])` — single dereference of an untyped
  slice holder (descriptor word 0 = address, on the R136 ternary model below);
  all refused (runtime exit 1 / compile-refused `E_KOSH_VIBHAG`), never printed.
- `r136_ws2_ternary.sm:9–10` is the *correct* pattern for contrast:
  `vitti addr = s[0]; likha(addr[0])` (double deref) — but it compile-refused
  `E_KOSH_DVARA`, so it never printed either.

**Printed genuine element values (safe — verified by pattern):** all double-deref
read-backs (`r136_ws1_untyped_return`, `r136_ws2_global/field/rawmem`,
`r136_ws1_untyped_param` — `77` then `7`); all reads through a typed `vibhag`
parameter (`s[0]` inside the callee in `r135_ws1_small_indirect`,
`r135_ws1_large_indirect`, `r135_ws1_growfn_indirect2`,
`r136_ws1_funcval_*`); and direct controls (`likha(k[0])`, `likha(k[2])` —
e.g. cell_write's `7`, growfn_indirect2's `77` then `30`). The distinguishing
rule is in the next section: a `[0]` on a *typed `vibhag` slice* yields an
element; a `[0]` on an *untyped `vitti` holding a descriptor pointer* yields
an address word — only the second `[0]` reaches the element.

**Searched and excluded:** `r89_probes.json`, `r90_probes.json`,
`r91_audit.json`, `r92_loop_table.json`, `r93_verification.json` contain no
slice-address print. The only large-number print there is `r90_probes.json`
`conv_mala`: `4615514078110652826` — explicitly identified in that file as
"float64 bits of 3.7 read as integer", a raw-bits print, not an address and not
a slice case. Dated logs `~/memory/2026-11-06.md:102,147` corroborate the
launder/dasham decompositions; no additional address-print incident was found
in `~/memory/2026-10-*.md` / `2026-11-*.md`.

### Question 3 — the general rule (method note)

**A slice value is a pointer to a two-word descriptor `[element-address,
length]`. `likha` prints any qword as a decimal integer. Therefore a printed
number's *kind* is determined by the expression that produced it, never by the
number itself.** Concrete, usable form:

1. **Pre-declare the expected set before running.** Write down every value the
   probe itself writes (`kosh_kship` values, literals: 0, 1, 7, 10, 20, 30, 77,
   99…). Any output outside that set is suspect, not a result. In these rounds
   every genuine element was in the set; every address was outside it.
2. **Magnitude tripwire.** Every address observed on Linux x86-64 here is a
   15-digit integer, ~1.3–1.4×10¹⁴: stack/descriptor pointers
   `140728493615824`, `140733170577648`, `140737185282080` (`0x7ffd…`);
   arena/heap element addresses `139932844687392` (`0x7f44…`),
   `131351504224288` (`0x7776…`), `139537424244064` / `139536700079456`
   (`0x7EEC…`); the dasham form `140724879295072.000000`. Genuine elements in
   these probes are ≤ 8,388,608 (7 digits, the large-funcval loop bound).
   **Rule of thumb: any bare integer > 2⁴⁰ (≈1.1×10¹²) — in practice anything
   with 12+ digits — is an address until proven otherwise.** Magnitude alone
   is not proof (see 5).
3. **Hex-prefix check.** Convert the number: a top byte of `0x7f…` / `0x77…` /
   `0x7E…` is a user-space pointer on Linux x86-64. A `dasham` print with a
   15-digit integer part ending `.000000` is the same address passed through
   int→float conversion (value preserved, bit pattern destroyed — ROUND-136
   `:79–85`).
4. **Deref-count check (source-level, the decisive one).** Count `[0]`s between
   the stored slice and `likha`: `likha(slice)` = descriptor pointer;
   `likha(t[0])` = element *address*; `likha(addr[0])` where `addr = t[0]` =
   element. **A probe may only report a value printed after two dereferences
   from an untyped slice holder (or one `[0]` through a typed `vibhag`
   parameter), plus a direct `likha(k[i])` control printed alongside.** One
   dereference too few is the entire R135→R136 difference.
5. **Two cross-checks, because magnitude can be fooled:** (a) **Control
   comparison** — always print `likha(k[0])` after growth + change next to
   the probed read: address vs `99`, stale `7` vs `99`, correct `99` vs `99`
   are three different verdicts; (b) **ASLR repeat** — run the identical probe
   twice: an address moves between runs (`131351504224288` vs
   `139932844687392` for the same slot; `140733170577648` vs
   `140737185282080` for cell_minimal), a value does not. And the worst case
   Sarvam flagged (ROUND-142/145: a slice *multiplied*, so the address is
   scaled) can land in a plausible range by accident — that is exactly when
   the deref-count and control checks, not magnitude, must carry the verdict.
6. **Never report a bare `likha(slice)`, `likha(t)`, `likha(box[0])`, or
   `likha(d)` as an element value.** Those print the descriptor pointer
   itself. A probe whose verdict depends on such a print proves at most
   escape, never a stale (or correct) element read.

### Task 3 — what could not be determined from source

- No `.sm` source exists for the arithmetic probe behind `139537424244064`, so
  its two versions (through-function vs direct) cannot be compared as probe
  sources — both are prose-only measurements, and both printed addresses.
  Whether that number is the descriptor pointer or the element address is also
  not fully settled in the files: `ROUND-142.md:16` says "DESCRIPTOR ADDRESS",
  `ROUND-143.md:48` says "a heap address" — both agree it is an address, not
  an element.
- For `r135_ws1_slice_store_direct.sm:7` (`likha(s[0])`, never ran), the files
  do not settle by themselves whether `s[0]` on a directly-assigned slice
  variable would be an element or an address word; it is classified as latent
  single-deref only by analogy with the R136 ternary model, and it never
  printed, so the classification has no consequence for any verdict.

## Task 4 — the gates, read not run

### First correction: the "64 checks" figure is stale

Counting the R137 gate's own source (`tests/r137/test_slice_number.py`):
`cases()` returns 57 programs (18 operators × 2, lines `54–57`, plus 21
further cases, lines `58–79`) + 1 ChatGPT S4 probe (line `177`) + 5 GLOBALS
(lines `88–96`) + 4 STACK (lines `98–114`) + 14 R147 slices (lines `117–122`,
`181–183`) = **81 program checks**, plus 5 source checks (lines `148`, `156`,
`164`, `171`, `174`) and 1 directory-equality check (line `181`) = **87
checks** on the release compiler, **+2 mutant checks** (lines `211`, `234`) =
**89 when the mutants run**. Claude's R137 report says 59 checks at v309
(`Claude-to-Sarvam/R137-00-A-SLICE-IS-NOT-A-NUMBER-V309-REFUSES-THE-USE-NOT-ANOTHER-DOOR.md`,
WS3) — the R141/R142/R147 additions since then explain the growth. Neither 59
nor the brief's 64 matches the file at HEAD.

### Question 1 — do the gates cover all fourteen shapes?

**Short answer: the R137 gate covers all fourteen *as filed*, but only because
the R147 section was bolted on later; its original R137 cases cover only a
subset. The R134 gate covers 8 of 14 fully, 2 only in adjacent form, and 4 not
at all.**

**Gate A — "R137 slice is not a number" (`tests/r137/test_slice_number.py`,
run by `tools/gates.sh:248`).** Per-shape coverage, by reading the case lists
(not by running):

| # | Shape | Covered in R137 gate? | How (file:line) |
|---|---|---|---|
| 1 | array cell store | **Yes — twice** | Original case `'cell store'`, `m[1] = m[0:2] + zero` (line `67`) — but note this is a *mala* slice in arithmetic in a cell, not a plain kosh-slice store; and R147 `01_cell` (`tests/r147/slices/01_cell.sm`, `box[0] = k[0:1]`), via `SLICES` (lines `117–118`) |
| 2 | untyped parameter | **Yes — twice** | `'untyped parameter'`, `keep(m[0:2])` (line `69`); R147 `02_untyped_param` (line `117`) |
| 3 | untyped return | **Yes — only via R147** | No plain untyped-return case in `cases()`; only R147 `03_untyped_return` (line `117`). The S4 probe (lines `81–86`, `177`) is a return *via arithmetic*, a different shape |
| 4 | function value | **Yes — twice** | `'function value'`, `f(m[0:2])` (line `70`); R147 `04_function_value` (line `118`) |
| 5 | module variable | **Yes — only via R147** | `cases()` has no module-variable store; `GLOBALS` (lines `88–96`) covers a *kosh* bound to a module vitti (`E_KOSH_DVARA`), not a slice. R147 `05_module_vitti` (line `118`) is the slice case |
| 6 | record field | **Yes — only via R147** | No field case in `cases()`; R147 `06_record_field` (line `118`) |
| 7 | raw memory | **Yes — twice** | `'raw store'`, `p[0] = m[0:2]` (line `68`); R147 `07_raw_memory` (line `119`) |
| 8 | decimal parameter | **Yes — only via R147** | No dasham case in `cases()`; R147 `08_dasham_param` (line `119`) |
| 9 | arithmetic | **Yes — extensively** | All 18 `OP_*` × 2 (lines `44–47`, `54–57`), unary `-`/`!` (line `58`), S4 probe (lines `81–86`), STACK variants (lines `98–114`), R147 `09_arithmetic` (line `119`) |
| 10 | module-level initializer | **Yes, with a caveat (see below)** | `GLOBALS` (lines `88–96`) and R147 `10_module_initializer` (line `120`), both expecting `E_KOSH_DVARA`/`E_KOSH_GANIT` |
| 11 | comparison as index | **Yes — only via R147** | `cases()` has `'index'`, `likha(m[m[0:1]])` (line `66`) — a slice as an index, but *not* a comparison as an index. Only R147 `11_comparison_as_index` (line `120`) is the shape as specified |
| 12 | through two functions | **Yes — only via R147** | No two-function case in `cases()`; R147 `12_two_functions` (line `121`) |
| 13 | stored in a kosh element | **Yes — only via R147** | No kosh-element case in `cases()`; R147 `13_kosh_element` (line `121`) |
| 14 | inline assembly | **Yes, but not by any slice check (see below)** | Only R147 `14_inline_assembly` (line `122`), expected `'SYNTAX'` |

Two caveats on the "all fourteen" verdict:

- **Shape 10 as filed contains no slice.** `tests/r147/slices/10_module_initializer.sm`
  is `vitti g = make_kosh()` — a *kosh* bound to a module vitti, not a slice
  in an initializer. The gate proves a kosh cannot be bound there
  (`E_KOSH_DVARA`); it does not test a slice reaching a module initializer. A
  slice-valued initializer (e.g. `vitti g = k[0:1]` at module level, where `k`
  is itself a module kosh) has no case in any gate read.
- **Shape 14 is covered by the parser, not by the escape machinery.** The gate
  expects `'SYNTAX'`: nonzero exit, no output file, and the string
  `vyakaran dosh` (lines `192–194`, `122` with the comment "yantra takes a
  string of machine bytes, not a value"). That proves `yantra(s)` does not
  compile; it proves nothing about any slice/door/walk check, since no such
  check is reached. If `yantra` ever accepted a value argument, no gate would
  catch a slice passing through it.

The R147 coverage is also fragile in form: the gate asserts the directory holds
exactly the fourteen files named in `SLICES` (line `181`:
`check(found == sorted(SLICES), …)`), and then runs each. A fifteenth shape
with no file is invisible to it.

**Gate B — "R134 one predicate" (`tests/r134/test_one_predicate.py`, run by
`tools/gates.sh:247`).** `WANT` (lines `27–42`) lists 21 programs: 5 `e*`, 3
controls, 13 `m_r136_*`. Mapping to the fourteen shapes:

| # | Shape | Covered? |
|---|---|---|
| 1 cell | **Yes** — `e1_cell`, `m_r136_ws1_cell_minimal`, `m_r136_ws1_cell_write` (lines `27`, `31–32`) |
| 2 untyped param | **Yes** — `e2_keep`, `m_r136_ws1_untyped_param` (lines `27`, `32`) |
| 3 untyped return | **Yes** — `m_r136_ws1_untyped_return` (line `32`) |
| 4 function value | **Yes** — `m_r136_ws1_funcval_small`, `m_r136_ws1_funcval_large` (line `33`) |
| 5 module vitti | **Yes** — `e3_global`, `m_r136_ws2_global` (lines `27`, `34`). Note: assignment inside a function, not an initializer |
| 6 record field | **Yes** — `m_r136_ws2_field` (line `34`) |
| 7 raw memory | **Yes** — `m_r136_ws2_rawmem` (line `34`) |
| 8 dasham param | **Yes** — `m_r136_ws2_dasham_param`, `m_r136_ws2_dasham_diag` (line `35`) |
| 9 arithmetic | **No** — no arithmetic program in `WANT`. This is by design of the gate's model: its docstring (lines `2–9`) says the doors never saw a slice because the operator had made it a number first; arithmetic is R137's territory, not R134's |
| 10 module initializer | **No** — `e3_global` (`tests/r134/escape/e3_global.sm`) assigns to a module vitti inside `mukhya()`; no initializer program exists in this gate |
| 11 comparison as index | **No** |
| 12 two functions | **Adjacent only** — `e4_fwd` (`tests/r134/escape/e4_fwd.sm`) forwards a slice through a `vibhag` parameter and then stores it in the caller's mala. That is forwarding-plus-store, not the R147-12 shape (outer → inner in sequence, both `vibhag`). It exercises the same forwarding idea but is not the same program |
| 13 kosh element | **Adjacent only** — `e5_pushslice` (`tests/r134/escape/e5_pushslice.sm`) pushes a slice into a kosh via `kosh_kship(h, k[0:1])`, not element assignment `k2[0] = k[0:1]` as in R147-13. Same door family, different syntax |
| 14 inline assembly | **No** |

So R134 covers **8 fully, 2 in adjacent form, 4 not at all** — exactly "the ones
that existed when it was written" (the R134/R136 shapes), plus the two
near-misses. Its source checks (lines `60–68`) are likewise frozen at five
doors: `DOORS` (line `37`) is `r126_check_assign`, `r126_check_builtin`,
`r126_check_writemem`, `r126_check_untyped_arg`, `r126_check_return`. The
module-initializer door (`r56_gen_global_initializers`, which does call
`r134_holds_kosh` at `src/sutram_compiler.asm:18351`) is **not** in that list,
so the gate never asserts it routes through the predicate.

What Claude's R137 report claims vs. the file: Claude's report (WS3)
describes the gate as it was at v309: 59 checks, every operator, unary forms,
conditions, bounds, index, cell/raw stores, untyped parameter, function value,
declaration-from-arithmetic, three kosh-arithmetic cases, the S4 probe, and
four controls — and it is explicit that "what it is not: proof that no other
form exists." That matches `cases()` + S4 + the OP check at HEAD. The GLOBALS
(R141), STACK (R142), and SLICES/R147 sections were added after that report, so
the report's claim does not cover shapes 3, 5, 6, 8, 10–14 as they stand now.

### Question 2 — if a new storage location were added, would any gate fail?

**No gate would fail for a new storage location added through the existing
entries — with two narrow exceptions that are not about storage locations at
all.**

Mechanism, gate by gate:

- **R134:** Its program list is a fixed dictionary (`WANT`, lines `27–42`). A
  new storage location has no program in it, so nothing exercises it and
  nothing fails. Its only structural tripwire is the source check (lines
  `64–66`): `call r126_is_kosh_value` must appear exactly once, inside
  `r134_holds_kosh` (verified by grep: exactly 1 occurrence, at
  `src/sutram_compiler.asm:28345`, inside `r134_holds_kosh` at line `28343`).
  That check fails only if a new door asks the **old** question — i.e. calls
  `r126_is_kosh_value` directly. A new door that calls **neither**
  `r126_is_kosh_value` **nor** `r134_holds_kosh` — a door that simply forgets
  to check — passes this gate silently. The gate enumerates five known doors
  (line `37`); it does not enumerate all stores or all door functions in the
  compiler, so it cannot detect a sixth door that checks nothing. Further
  weakening: the source checks run only when the gate uses the tree's own
  compiler (`if own:`, lines `58–60`); invoked with `--compiler`, they are
  skipped entirely and only the 21 fixed programs run.
- **R137:** Its only enumerating source check is the operator table (line
  `148`): `defined == set(OPS)` — it fails if `src/sutram_compiler.asm`
  defines an `OP_*` the gate does not spell (the docstring, lines `34–35`,
  states this explicitly). A new storage location is not an operator, so it
  cannot trip this. The 81 program cases are fixed strings/files; the R147
  directory check (line `181`) fails only if files are added to or removed
  from `tests/r147/slices/`, which a compiler change does not do. The gen_expr
  routing checks (lines `156`, `164`, `171`, `174`) are about
  *expression-entry* routing, not storage: a new store reached through
  `gen_expr` / `gen_stmt` is walked, but the walk only refuses slice-as-number
  uses and the door checks only fire at doors that exist — whether a new store
  is door-checked is asserted nowhere.
- **The one genuine tripwire, and its limit:** the R137 bodies-only check (line
  `164`) would fail if a new entry called `r142_gen_expr_body` directly,
  bypassing `gen_expr` — but that is a new *entry bypassing the walk*, not a
  new storage location. A new storage location implemented inside the existing
  generator, checked by nothing, fails no gate.

So the answer to the brief's question is **none would** — for the case as
asked. The gates test known shapes and known operators; neither enumerates
storage locations.

### Question 3 — is the deliberately-broken-compiler gate testing what it claims?

**It tests a narrower thing than its docstring claims, though what it does test
is real and valuable. There is no standalone "deliberately-broken-compiler
gate" file — this is the mutant section inside the R137 gate**
(`tests/r137/test_slice_number.py:205–236`), with the mutants defined by
`%ifndef` in the compiler source.

What it does (read from source):

- It builds two mutant compilers with `nasm -D… src/r68_compiler_entry.asm`
  (lines `211–213`): `-DR142_MUTANT_NO_STMT_CHECK` and
  `-DR142_MUTANT_NO_GLOBAL_CHECK`. In the source these remove the walk **and**
  the raising of `r142_checked` together at the two entries:
  `src/sutram_compiler.asm:18855` / `18865` (`gen_stmt`, line `18854`) and
  `:18346` / `18360` / `18364` (`r56_gen_global_initializers`, line `18330`).
- It re-runs all 81 programs with each mutant and asserts (lines `219–233`):
  every negative is still refused, and a control may be over-refused but must
  never compile to a wrong value.
- The mechanism it relies on is the `gen_expr` fallback
  (`src/sutram_compiler.asm:21415–21430`): when `r142_checked` is 0,
  `gen_expr` walks the expression itself (`call r137_check_stmt`, line
  `21421`) before generating.

What it proves: **for the 81 programs in the gate, forgetting the walk at either
of the two existing entries degrades to over-refusal, never to a leak** —
because the fallback walk in `gen_expr` catches what the entry walk would have
caught.

What it does **not** prove (each a reading finding, not a run):

1. **It does not test a new entry.** The docstring (lines `25–26`) says the
   mutant models "the entry forgets the walk, as a new entry might." That is an
   analogy, not a test: only the two entries that exist are mutated. A
   genuinely new third entry is never built, and its behaviour is asserted
   only by the static source checks (lines `156–174`), not by any mutant run.
2. **It does not test a new shape.** The mutants re-run exactly the existing 81
   programs. A fourteenth-plus shape, or a new storage location, is untested
   by the mutants exactly as it is untested by the release run.
3. **It models only one failure mode.** The `%ifndef` removes the walk *and*
   the flag-raise as a pair. A real "forgotten check" could raise
   `r142_checked` without walking (flag without walk) — that mutant is never
   built. The static check at line `171` ("`r142_checked` is raised only after
   the walk, in the same function") partially covers this, but statically, and
   only for `inc` sites that exist in the source.
4. **Its acceptance criterion is weaker than the release run's.** For mutants,
   any `[E_…]` code counts as a refusal (lines `226–229`:
   `'[E_' not in said`), whereas the release run demands the *specific*
   expected code (lines `196–197`). Over-refusal of controls is explicitly
   allowed (lines `230–233`). So the mutant check proves "no leak on these
   programs", not "same behaviour".
5. **It silently does not run in two configurations.** With `--compiler` it
   prints `NOT RUN` (lines `206–207`); without `nasm`/`ld` it prints `NOT RUN`
   (lines `208–209`). And `tools/gates.sh:126` judges the R137 gate only by the
   last line matching `", 0 failed"` — a run in which the mutant section was
   `NOT RUN` still passes the gate. (In the normal `gates.sh` run, line `248`
   passes no `--compiler`, so the mutants do run when `nasm`/`ld` are present
   — but nothing in the gate output distinguishes "mutants passed" from
   "mutants skipped" except the two `check()` lines being absent.)

### Task 4 — uncertainties (read-only limits, stated as such)

- **I could not determine from source alone which check refuses R147 shape
  12** (`12_two_functions`). Both legs pass the slice through `vibhag`
  parameters, which are legal carriers; the gate asserts only the code
  `E_KOSH_VIBHAG` (`test_slice_number.py:121`). Whether the refusal comes from
  a door check on the outer call, the inner call, or the walk is not
  determinable from the gate file, and the full call-generation path for this
  shape was not traced.
- **Attribution of R147 shapes 1, 5, 6, 13 to the R134 door vs. the R137 walk**
  is inference from the expected code (`E_KOSH_VIBHAG` suggests the door), not
  something the gate establishes — the gate asserts codes, not mechanisms.
- **I could not determine from source alone whether a new storage location
  added *inside* `r142_gen_expr_body`'s generation path would be walked.** The
  walk operates on statements/expressions before generation; whether a store
  emitted during generation (rather than from a statement node) passes any
  check is a question about code paths not fully traced. This is the one place
  where the "new storage location" answer above has a residual unknown: the
  claim "none would fail" holds for stores reached through `gen_stmt` /
  `gen_expr`; for a store emitted by a path that never goes through either, I
  cannot say from this reading whether the gate's bodies-only check (line
  `164`) would even see it.

## Task 5 — what to read next

The part of the memory model that is under-read is not the walk or the doors —
those have now been read three times (R137, R149, this round). It is the layer
underneath them: **the name-marking tables and the predicates that trust
them.** Every laundering route in this whole arc is the same shape: a value
whose kind the predicates cannot see. `r23_expr_is_slice`
(`src/r23_capabilities.inc:473–485`) recognises only a literal `AST_SLICE` or
a slice-named `AST_VAR`; `r126_value_kind` (`27868–27890`) knows `VAR` /
`SLICE` / `FUNCALL` / `TERNARY` and returns raw 5 for anything else, including
`AST_CALL` — so any value laundered through a call, a builtin, or a foreign
function looks like a plain number to every door. The FFI route in Task 2 is
the newest member of that class, not a new class.

Concretely, in reading order:

1. **The marking tables.** `r23_mark_slice_var` / `is_kosh_var` / the
   `kosh_vars` table (`KOSH_VAR_CAP`), `r38_mark_alias` (`27702+`, which
   propagates slice/kosh/array kinds through aliases — and explicitly does
   *not* mark raw `nirmmita` pointers), the vibhag-param marking (`18541`)
   and slice-decl marking (`19143`). The R135 shape-2 cause was an untyped
   parameter that is never marked; the open question is which other bindings
   are never marked, and what happens at `KOSH_VAR_CAP` overflow. Read every
   site that creates or copies a name binding (decl, assign, param binding)
   and ask of each: does the kind table learn about it?
2. **The FFI boundary as a whole** (`src/r32_ffi.inc`). It is now the live
   open route: the kind table, the `ptr` dereference of a kosh `AST_VAR`
   after `gen_expr`, the return handling (`.result`, `870`), and the `--ffi`
   declaration loading (`13940–13941`). If the fifteenth shape is real, its
   fix belongs here, not in the walk.
3. **The slice descriptor's lifetime.** A slice descriptor is two words
   (`src/sutram_compiler.asm:28386`) living in the maker's frame — the R135
   diagnostic showed `t` itself as a stack address (`0x7ffd…`,
   ROUND-135 `:139–146`) — while the kosh descriptor is `[d-16]` length,
   `[d-8]` capacity, `[d]` elements (`572–573`). What happens to a slice
   descriptor after the maker returns, and which code (if any) assumes it is
   still alive, has never been read as a lifetime question; the escape work
   has only ever asked about growth.
4. **`r58_fold_tree` (`31541+`).** Folding runs inside `r142_gen_expr_body`
   before dispatch (`21436–21440`) — *after* the walk. Only its head was read
   (`BINOP`s of two `NUM` literals and identity cases, returning
   already-walked sub-nodes). Every fold branch deserves a read: a fold that
   rebuilds or moves a node after the walk is the one place the walk's
   coverage could be undone downstream.
5. **The region allocator** (`src/r65_arena.inc`, `r127_emit_grow`). Growth
   relocation, the 64 KiB region threshold (comment at `9039`), and the R143
   walk-budget arithmetic (349,521 vs. the tree bound) — the budget number was
   never independently verified in this round.
6. **The gate enumeration problem.** The gates list known shapes; the record
   needs a positive enumeration — every store and every door, listed in one
   place, with a rule that a new storage location must satisfy — rather than
   case lists that a new location silently passes. Task 4's answer ("none
   would fail") is the evidence that this list does not exist yet.

## What could not be determined from source (consolidated)

- The runtime effect of the FFI shape (Task 2): the compiler accepts the call
  and emits the descriptor address; what a foreign function does with it at
  runtime needs execution.
- Which check refuses R147 shape 12, and the door-vs-walk attribution of R147
  shapes 1, 5, 6, 13 (Task 4): the gates assert codes, not mechanisms.
- Whether a store emitted inside `r142_gen_expr_body`'s generation path (never
  going through `gen_stmt` / `gen_expr` as a statement) would be walked or
  gated (Task 4 residual).
- Whether every `AST_BLOCK` construction site (e.g. synthesized mandapa blocks
  at `8271` / `8333` / `8400`) reaches `gen_block` → `gen_stmt` (Task 2
  residual 1); every `r58_fold_tree` branch (residual 2); the R143
  walk-budget arithmetic (residual 4).
- `make_kosh`'s own `ret_kind` for shape 10 (Task 1 qualification); the
  arithmetic probe's two versions as probe sources — no `.sm` exists (Task 3).
- `r135_ws1_slice_store_direct.sm:7` (`likha(s[0])`, never ran): whether
  `s[0]` on a directly-assigned slice variable would be an element or an
  address word is classification by analogy only, with no consequence for any
  verdict (Task 3).

---

*Read-only: nothing compiled, run, or executed. Delivered as `Muse-to-Sarvam/ROUND-148-PAPER-REVIEW.md`.*
