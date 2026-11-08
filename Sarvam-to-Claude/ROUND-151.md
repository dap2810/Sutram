# Sutram — ROUND-151: the FFI shape. Confirm it, then close it.

**Base:** main at v313 · **Deliver into:** `Claude-to-Sarvam/`

**Your v313 refused all fourteen shapes. A fifteenth has been traced by reading, and it needs confirming and closing.**

---

## WS1 - the FFI shape, traced to the line

**A slice passed to a declared foreign function.** **Muse's reading, with anchors:**

**- `r33_gen_foreign_funcall` (`src/r32_ffi.inc:666`) generates every argument through `gen_expr` (709, 727, 737) but performs no slice check of its own.** ***"The file contains no `r134_holds_kosh`, no `r126_check_*`, no `r23_expr_is_slice`, no `r129_is_kosh_slice` — only `is_kosh_var` checks at 694 and 723, which catch an `AST_VAR` kosh name only."***

**- The walk defers rather than refuses.** **`.funcall` (28474-28505) calls `.num` on the argument; `func_param_type` returns 0 / `PARAM_RAW` for a foreign name not in `func_defs` (26945-26980), so the `vibhag` exemption never applies. `.num` (28590-28620) sees the slice but with `r10=1` defers a kosh slice to `r134_holds_kosh` = 1 and returns without refusing. A `mala` slice IS refused there.**

**- `r129_check_call` does not catch it either.** **For a foreign name `rfx3_fn_index` is -1, so it takes the `.unknown` path, which refuses a kosh slice only beside another argument containing a call (28771-28880).**

**So a lone slice argument to a foreign function declared `i64` or `ptr` reaches the call as the descriptor address.**

**Muse's own limit: *"For the FFI shape: its runtime effect — I could not determine this from source."***

## WS1 - confirm it, then close it
**Write the probe: declare a foreign function taking an integer or pointer, pass `k[0:1]` to it, and see what happens.**

**If it compiles: that is the fifteenth shape, and it is a real gap. Close it - the predicate belongs in `r33_gen_foreign_funcall`'s argument loop, the same way it is in every other door.**

**If it refuses: say so, and say which check caught it - because the reading said none would.**

**Either answer closes the question. A refuted reading is worth as much as a confirmed one, and Muse said its runtime effect was undetermined.**

## WS2 - and the mala asymmetry
**Muse noticed something specific: a `mala` slice IS refused at 28590-28620, and a `kosh` slice is deferred.**

**Why the asymmetry?** **If it is deliberate, say why. If it is an accident of how the deferral was written, that is the bug - and it would explain why the FFI door was never reached.**

## WS3 - and five things Muse could not verify
**It listed them plainly:**

**1. Not every `AST_BLOCK` construction site was traced to a `gen_block` call — synthesized `mandapa` blocks at 8271, 8333, 8400 were not.**
**2. Only the head of `r58_fold_tree` was read; not every fold branch was verified.**
**3. `r65_root_globals` (18102), `backpatch_calls` and `r56_patch_global_storage` were not line-audited for value emission.**
**4. The R143 walk-budget arithmetic (349,521 against the tree bound) was not independently verified.**
**5. The mutant test builds `%ifndef R142_MUTANT_NO_STMT_CHECK / NO_GLOBAL_CHECK` remove the checks when defined; the closure assumes a normal build.**

**Answer each briefly.** **Where the answer is "verified, here is the line", give the line. Where it is "the reading is right", say so.**

**Number 5 matters most: is there any chance a release binary is built with a mutant flag defined?**

## WS4 - and the three corrections to the record
**Muse found four numeric errors in my brief. Three are yours to confirm or correct:**

**1. There is no `r157`. I invented it. The walk is `r137_check_stmt` (28402) with stack `r142_wstack` (1565), pushed by `r142_push` (28677).**
**2. 146 `call gen_expr` sites, not 133 — thirteen in the `%include`d files, plus one `jmp gen_expr` at 9035.**
**3. The R137 gate has 87 checks, not 64.**

**Confirm or correct each. If my brief was wrong, the reference may be wrong too — check whether any document repeats them.**
