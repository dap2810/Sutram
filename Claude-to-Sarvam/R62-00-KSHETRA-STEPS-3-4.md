# R62-00 — Steps 3 and 4 of `kshetra`, finished enough to build

- **Base:** `main` at `6fe9953`, compiler v261. **A design, not an implementation.** Line counts are estimates
  calibrated on this compiler's own code; emitted byte counts are from the encodings the compiler already uses.
- **Settled and used as given:** the block is the carrier; the region is lexical; `dvi-mukha` is one arena with the
  persistent cursor growing up from the start and the scratch cursor down from the end.

## 0. One finding before the design: `kshetra` is already a word in this compiler

**`kshetra` means a struct FIELD in three existing diagnostics:**
- `Sutram Error [E_UNKNOWN_FIELD]: agyat kshetra 'w'` (`src/sutram_compiler.asm:313`);
- `Sutram Error [E_AMBIGUOUS_FIELD]: kshetra 'x'` (`:317`);
- `Sutram Error: rachana kshetra seema atikram` (`:827`).

Three goldens and `tests/r23/test_capabilities.py` pin those texts. A programmer who reads *"agyat kshetra"* and then
writes a `kshetra` block is being told the same word means a field of a `rachana` and a memory region. **The word is
usable, but the decision should be made knowing this.** ChatGPT's R134 §8 approved the word without seeing it.
If the region keeps `kshetra`, the field messages could move to another word in a later round; if not, the region
needs a different word. **Nothing below depends on the choice.**

## Step 3 — the block

### 3.1 Where the mark lives, and what entry and exit emit

**The scratch cursor is a hidden module global**, registered the way R46 registered the debug counter
(`r45_register_counter`, `src/r45_debug.inc:455`, through `r56_register_global` `:22716`): a name a program cannot
write, `0kshetra_cursor`, addressed RIP-relative like every other global.

**Each block's mark is a hidden LOCAL of the enclosing function**, `0kshetra1`, `0kshetra2`, ... by nesting depth,
made with `alloc_var`. The compiler gives it a callee-saved register or an `rbp` slot like any local. **That is what
makes it recursion-safe and nesting-safe with no shadow stack:** a recursive call has its own frame, so its own marks.

**Entry:** `0kshetra<d> = 0kshetra_cursor`. **Exit:** `0kshetra_cursor = 0kshetra<d>`. Both are generated as
ordinary assignments through the AST, exactly R45's "it is just Sutram" construction (`r45_emit_count`,
`src/r45_debug.inc:396`), so they inherit the register-or-slot handling for free.

| | instructions | bytes | note |
|---|---|---|---|
| entry | 2 | 10–14 | `mov rax,[rip+cursor]` (7) + store to a register (3) or an `rbp` slot (4–7) |
| normal exit | 2 | 10–14 | the reverse |
| `nirmmita` inside the block | 6 + zeroing | ~40 + 12 | load cursor, subtract size, align down, compare with the persistent cursor, store, return; then `rep stosb` |

### 3.2 Exit lowering: `krama`, `agrim`, `nivartanam`, `prasar`

**The rule:** an exit restores the cursor to the mark of the **outermost block it leaves.** Inner marks are lower
addresses (scratch grows down), so restoring the outermost mark releases every inner block in one store. **That is
one restore per exit path, whatever the nesting depth.**

**Which mark is "outermost left" is known at compile time:**
- the compiler keeps `r62_depth` and, per depth, the hidden local's name and the variable-table watermark;
- **loops record `r62_depth` at their entry.** The loop generator already saves `break_patch_cnt` on the compiler's
  stack per loop (`:14015`, `:14054`); the kshetra depth goes beside it. ~10 lines.
- `krama`/`agrim`: if `r62_depth > depth_at_loop_entry`, restore the mark at `depth_at_loop_entry + 1`. A break of a
  loop that lies wholly inside a block (depth unchanged) restores nothing — the block is still live.
- `nivartanam`/`prasar`: if `r62_depth > 0`, restore the mark at depth 1 (the function's outermost block).

| Exit | Where | Added when crossing ≥ 1 block | Added when crossing none |
|---|---|---|---|
| `krama` | `.gs_break` `:14063` | 2 instr, 10–14 bytes, before the existing `jmp` | **0 bytes** |
| `agrim` | `.gs_continue` `:14085` | same | **0 bytes** |
| `nivartanam` | `.gs_return` `:14440`, after the value is in `rax` (and `rdx` for a phal-prakriya) | **2 instr, 14 bytes** via a scratch register that the value does not use: `mov r11,[mark]; mov [rip+cursor],r11`. Done through the generic AST assignment instead, it is 6 instructions with `push`/`pop` around it. I would write the 14-byte emitter; it is ~15 lines. | **0 bytes** |
| `prasar` | `r25_gen_prasar` `src/r25_phal.inc:178`, before its inline `lea rsp,[rbp-8]; pop; pop; ret` | same 14 bytes | **0 bytes** |
| `sthagita` | — | nothing: the process ends | |

**One trap, found by ChatGPT and confirmed in the source:** `prasar` patches a *short* `jz` and refuses a
displacement over 127 (`src/r25_phal.inc:203`). Fourteen more bytes inside that branch can cross the bound. The
fix is to emit the restore *before* the `jz` only when inside a block — or to widen that branch to `rel32` on the
block path only. **Either way the no-block encoding stays byte-identical.**

**Cost of the exits in lines:** ~12 per site at 4 sites, plus the 14-byte emitter: **~65 lines.**

### 3.3 Nested blocks

```
kshetra                    # depth 1: 0kshetra1 = cursor        (mark A)
    vitti a = nirmmita(64)   #   cursor = A - 64
    kshetra                # depth 2: 0kshetra2 = cursor        (mark B = A - 64)
        vitti b = nirmmita(64)   # cursor = B - 64
        yadi (x) { krama }  # inside a loop that encloses BOTH blocks: restore 0kshetra1, then jmp
    # normal end of depth 2: cursor = 0kshetra2 (= B): b is gone, a is intact
# normal end of depth 1: cursor = 0kshetra1 (= A)
```

- **Leaving only the inner block restores B, not A:** `a` survives. That is the normal exit of depth 2.
- **Leaving both at once** (the `krama` above) restores A. One store.
- **Using `a` inside the inner block is fine**; assigning `b` to `a` is refused by Step 4 (the target is declared
  outside depth 2).
- **Allocating into the outer block from inside the inner one is not offered.** With one LIFO cursor it cannot be,
  and the lexical rule makes the question moot: where the `nirmmita` is written is its block.
- The compile-time depth is bounded by `BLOCK_NESTING_CAP` like every other block.

### 3.4 Can a `kshetra` contain a `nivartanam`? Yes — allow it.

- **The cost is 14 bytes and 2 instructions,** emitted only when a return sits inside a block.
- **Forbidding it would make the block useless for this library's own style:** early returns are everywhere
  (677 `nivartanam` in `lib/`, a large share of them guards at the top of a function).
- **What makes it safe is Step 4, not the lowering:** the returned value is checked before the restore is emitted.
  `nivartanam p` with a block-kind `p` is refused at compile time; `nivartanam n` with a plain integer restores and
  returns.

### 3.5 Exhaustion: when the two cursors meet

There are two meetings, and they deserve different answers because the programs that hit them are different.

| Who runs out | Behaviour | Why |
|---|---|---|
| **the persistent cursor** (every `nirmmita` outside a block — all existing programs) | **fall back to today's `mmap` for that allocation, silently** | Existing programs allocate beyond any arena: the 1,000,000 × 64 B program takes 4 GB today and works. Constraint 3 forbids breaking it. The fallback changes speed, never behaviour. |
| **the scratch cursor** (a `nirmmita` inside a block) | **plain `nirmmita` returns 0** — its failure contract today | A fallback `mmap` here would not be rewound, so the block's one promise would silently stop holding. 0 is the contract every caller already knows how to test. |
| **a `kosh` or `mala` declaration inside a block** | **a runtime error and exit 1** | Today these write their header through the returned pointer without testing it (ChatGPT's R131 hazard), so 0 would be a crash. The runtime-error path exists: the `mala` bounds failure builds `likha("...")` + exit as AST (`:14620-14640`). Same construction. |

**The message to a Sanskrit-speaking programmer, proposed, NOT yet checked by ChatGPT (the owner's rule):**

> `Sutram Error: kshetra purnam - smritih nasti` / **क्षेत्रं पूर्णम् — स्मृतिः नास्ति** ("the region is full — there is no
> memory"), followed by the requested size.

**Where the string lives is a decision:** a message in the per-pack table needs an entry in all eleven packs or
`tools/sandesh.py --check` fails (every pack must be complete). **That is new development in the ten frozen
packs.** R52 avoided it by keeping its `yoj` hint as a Sanskrit-only string outside the table
(`src/r52_yoj_hint.inc`); I would do the same here and report it, as R52 did.

**Also decided by exhaustion policy:** the arena size. With rewind, the scratch side holds the peak live set, so a
few hundred MiB is plenty; the persistent side is bounded by the fallback, not by the arena. A `.bss` arena must stay
well under the smallest machine's RAM (measured in R60: 8 GiB of `.bss` fails to load on 7 GB).

## Step 4 — the check

### 4.1 Is it a new pass? No. The AST for a function exists before any byte of it is emitted.

`parse_block` builds the whole block's AST (`:8711`), and `gen_block` walks it. `r23_check_return` already does its
slice check inside that walk. **The block-kind check runs in the same walk, at the same hooks.** Sutram stays
single-pass over the source.

**One honest exception:** loop-carried flow. In

```
kshetra
    vitti x = 0
    yavat (c)
        outer = x            # x is not yet a block pointer when this line is walked...
        x = nirmmita(8)      # ...it becomes one here, and the next iteration escapes
```

a single forward walk accepts `outer = x`. **The fix is a pre-scan of the block's own subtree at block entry**:
collect every variable that is ever assigned a block-kind value anywhere in the block, and treat it as block-kind
from the first line. The subtree exists (it was just parsed), the scan is the same recursive walk `gen_block` does
with emission turned off, and it costs about 60 lines. **It is a second walk over the block's subtree, not a second
pass over the program.** Monotone kinds make it sound without a fixed point: a variable, once block-kind, stays so
for the rest of the block.

### 4.2 The kind, and how it moves

A per-function list exactly like `r23_slice_vars` (`src/r23_capabilities.inc:415-470`): **(name, depth)** pairs,
"this variable may hold a pointer allocated in the block at depth d".

**`kind(expr)`** — a small recursive function over the expression AST, ~60 lines:

| Expression | kind |
|---|---|
| `nirmmita(...)` written inside a block | **block, depth = current** |
| a `kosh`/`mala` declared inside a block | block (its storage is a `nirmmita` emitted inside the block) |
| a variable | its recorded kind, or none |
| `e1 + e2`, `e1 - e2`, any `BINOP` with a block-kind operand | **block**, the deepest operand's depth (this is the rule today's slice check lacks: `s + 0` launders a slice, measured in R61) |
| a call, `pad8(...)`, `m[i]`, a field read, `yantra` | **none** — honestly unknown |
| a literal, a string | none |

### 4.3 The rules, each with what it catches and what it lets through

| # | Hook | Rule | Catches | Lets through |
|---|---|---|---|---|
| **A** | `.gs_assign` `:13074`, and `vitti x = e` | if `kind(e)` is block at depth d and `x` was declared before block d's watermark (or `x` is a module global): **refuse** | `outer = p`, `outer = p + 64`, `g = p`, assignment to an outer block's variable from an inner block | `outer = helper(p)`; `outer = pad8(cell)` after `likh8(cell, p)` |
| **B** | `.gs_assign_index` `:13267`, `.gs_assign_field` `:13432`, `likh8` (`BN_LIKH8` in `gen_expr`), `kosh_push` (`.ge_call_koshpush` `:15651`), `smaran_cp` | if `kind(value)` is block at depth d: **refuse unless the container is itself block-kind at depth ≥ d** | storing into an outer `mala`, an outer `rachana`, a parameter, a global `kosh`, or through any pointer the compiler cannot place | a store through a pointer that was itself laundered |
| **C** | `.gs_return` `:14440`, `r25_gen_prasar` | if `kind(e)` is block: **refuse** | `nivartanam p`, `nivartanam p + 8` | `nivartanam helper(p)` — a call result has kind none, so a helper that returns its argument passes; and the laundered return |
| **D** | call arguments | **allow**, and say so | — | **passing `p` to a function that keeps it** (`suchi_yuj(outer_list, p)` stores the integer). Refusing would also refuse `varna_maap(buf)`, the whole point of a scratch buffer. A per-function "retains argument i" summary needs the callee's body analysed first, which is a second pass over the program. **Not in v1.** |
| **E** | loop-carried | the pre-scan of 4.1 | the example in 4.1 | — |

**Two documented holes remain, D and the integer laundering through memory.** In R61 I gave the mitigation I would
insist on: **in a `--debug` build, the scratch cursor never rewinds and each block's pages are `mprotect`ed on exit
(~40 lines in `src/r45_debug.inc`), so a pointer that slips through either hole faults at its first use.** A lint
plus a fail-stop debug build is the honest shape; a lint alone is not.

**The error must carry a line.** The slice refusal today goes through `capacity_fail` and prints no line number
(`Sutram Error: vibhag prakriyayah na pratyarpaniyah`, measured). The new refusal must use the `pankti N` path
(`msg_err_line`, `:345`); the statement's position is already recorded for the debugger in `r45_map`
(`src/r45_debug.inc:73`). ~20 lines. The message itself, like 3.5, stays outside the per-pack table.

### 4.4 Price

**Run-time cost: zero.** Every rule is decided in the compiler; no byte is emitted for a check that passes.

**Compile-time cost per operation**, in the compiler:

| Operation | Work |
|---|---|
| per assignment / store | one `kind(expr)` walk of the right-hand side (a few nodes), one scan of the kind list (`strcmp` per entry; the list is per function and short), one compare of the target's variable index against the block's watermark |
| per call | nothing (rule D) |
| per arithmetic operation | one recursion step inside `kind(expr)` |
| per block entry | the pre-scan: one extra walk of the block's statements |

**Compiler lines, Step 4:**

| Part | Lines |
|---|---|
| kind list: mark, test, clear at function end | ~50 |
| `kind(expr)` | ~60 |
| pre-scan at block entry | ~60 |
| hooks A, B, C (about 8 sites) | ~80 |
| error with line number | ~20 |
| **total** | **~270**, in a new `src/r62_kshetra.inc` plus one-line hooks |

**Compiler lines, Step 3:** keyword + constant ~8; parse (beside `.ps_if` `:9053`, reusing the braces-optional body
path) ~30; generate entry/exit + depth bookkeeping ~70; exits ~65; loop-depth record ~10; the scratch-cursor
`nirmmita` path with zeroing, beside `r38_nirm_seq` `:19892` ~120; outer-`kosh` growth picking the persistent cursor
at `:15799` ~10. **~310.** Steps 3 + 4 together: **~580**, of which the debug fail-stop is 40 more.

## What the guard proves

**Every hook is gated on `r62_depth > 0`, and the keyword appears in no existing program. So for the 577 guard
programs, Steps 3 and 4 emit no byte: the guard stays at 0 DIFFER on all three paths, and that is the first thing to
run after the hooks are in and before the block itself works.** If it does not, the gate is leaking and the veto
applies.

Three things are guard-visible, all by the owner's decision in Steps 0–2, not by Steps 3–4:
- Step 1 changes how the 248 allocating guard programs allocate (`evidence-r60/guard-programs-that-allocate.txt`):
  their bytes change, their output must not;
- Step 0's `kosh` growth changes every program with a `kosh`;
- Windows changes every `.exe`, which is the owner's work.

One subtle point to test rather than assume: the hidden mark local takes a register or slot, which can move a user
variable from a register to the stack **in functions that contain a block only.** Programs without a block are
unaffected, which the guard will confirm.

## The two tests, and a third

1. **1,000,000 × 64 B in a block inside a loop:** peak live is 64 bytes per iteration; memory must not grow. Also
   measure the cycles, since the zeroing and the two cursor stores are in the path now.
2. **`outer = p` inside a block:** a compile error **with a line number** (4.3, the line plumbing).
3. **The loop-carried case of 4.1:** it distinguishes a check with the pre-scan from one without, and it is the one
   a single forward walk gets wrong.
