# ROUND-149: closure answer — one page, read only

**Base read:** `origin/main` at `241840ef` ("R146 and R147 withdrawn"), 2026-11-08.
File read: `src/sutram_compiler.asm` (33,554 lines), `src/r45_debug.inc`,
`src/r32_ffi.inc`, `src/r25_phal.inc`, `src/r65_arena.inc`.
Nothing compiled, nothing run.

## Answer: 1 — the claim holds, with one wording correction

Every path that generates code for an expression goes through `gen_expr`, and
every such path is checked. The closure is a property of the two-layer door,
not of `gen_expr` alone: `gen_expr` runs the check first only on entry from
outside a checked statement. Nested `gen_expr` calls skip their own walk by
design and rely on the enclosing statement's walk, which covers the whole
statement tree. That is the correction to the sentence as written; the
substance — no expression reaches code generation unchecked — holds.

## The paths checked

**One entry.** The compile driver calls `gen_code` once (line 3151).
`gen_code` routes to exactly three generators:

- `r56_gen_global_initializers` (line 18105): walks each initializer with
  `r137_check_stmt` (line 18348), applies the module-`vitti` door
  (`r134_holds_kosh`, line 18351), then calls `gen_expr` with
  `r142_checked` raised (lines 18361–18365).
- `gen_block` (line 18110, mukhya body; line 18667, each function body):
  `gen_block` is the wrapper in `src/r45_debug.inc:738` over
  `r45_gen_block_body`, which calls `gen_stmt` for every statement
  (line 18822).
- `gen_all_functions` (line 18158): per function, prologue then `gen_block`.

**One statement door.** `gen_stmt` (line 18854) calls `r137_check_stmt` on
the statement, raises `r142_checked`, then runs `r142_gen_stmt_body`.
Every value-bearing handler in that body reaches its expressions through
`gen_expr` (counted per handler: decl 3, assign 5, if 3, while 3, for 2,
assert 2, do-while 1, return 1, writemem 1, call 4, funcall via
`gen_typed_call_arg` 1, stage-1 assignment 1). The dispatch default for any
unlisted statement kind is `gen_expr` itself (`.r73_not_rewind`).
`gen_typed_call_arg` calls `gen_expr` on all three of its paths (scalar,
kosh, slice); the foreign-function path (`r33_gen_foreign_funcall`) and the
failure-handler path (`r26_gen_handle`) also call `gen_expr`.

**One expression door.** `gen_expr` (line 21415): if `r142_checked` is 0,
it calls `r137_check_stmt` on the root as a number (line 21421) before
`r142_gen_expr_body` (line 21425); if the flag is raised it goes straight
to the body. All 133 `call gen_expr` sites sit inside statement bodies,
`gen_expr`'s own body, `r56`, or emit helpers called from those
(`r103_emit_budget_checks`, `r82_emit_check`, `r80_emit_div_fatal`,
`r80_emit_likha_tail`) — every one of them under the flag or under the
fallback walk. There are no direct calls to `r142_gen_expr_body` or
`r142_gen_stmt_body` anywhere: only the two wrappers call them.
`r142_checked` is raised in exactly three places, each immediately after a
walk (`gen_stmt`, `r56`, `gen_expr` itself).

**The walk covers the tree.** `r137_check_stmt` (line 28402) walks with its
own stack and a budget that refuses on exhaustion (R141). It descends into
every expression position — binop operands, call/funcall arguments (all 6;
the parser refuses a 7th: "prakriya adhikatamam 6 tarkan grihnati"),
indexes, conditions, `for` bounds, assignment values, writemem address and
value, slice bounds — and its `.gen` default pushes every node field
(offsets 8–64), so unlisted node types still have their children walked.
Leaves (`NUM`, `FLOAT`, `STR`, `VAR`) hold no expressions. `BLOCK` and
`FUNCDEF` are skipped because their statements come through `gen_stmt`
separately. Slice bases are always names (parser builds `AST_SLICE` only
from a name, lines 17539 and 27342), so not pushing the base is sound.
The `gen_expr` fallback also checks the root itself as a number
(`.walked` epilogue, `r142_value_mode`).

## The two things that do not go through `gen_expr`

Neither can carry an expression value, so neither breaks the claim:

- Fixed control-flow bytes (jumps, prologue, trap sequences) emitted by
  statement handlers — constants, not values.
- `AST_NISHKRIYA` — emits literal hex bytes from source, verbatim. No
  expression is evaluated, so no slice can hide in it.

## What this does not claim

The answer is about paths, not about the check's completeness for every
shape — whether `r137_check_stmt` refuses each of the fourteen shapes is
ROUND-148's question, not this one. One related note: at a "door"
(`r10 = 1`: function argument, builtin argument, writemem, non-`var`
assignment target) a slice that holds a `kosh` is left to the door's own
check rather than refused by the walk. The value still cannot reach
code generation — either the walk or the door refuses it — but which one
refuses depends on the position.
