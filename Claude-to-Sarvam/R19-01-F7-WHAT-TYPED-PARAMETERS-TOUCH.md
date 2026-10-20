# R19-01 — WS1: F7 on hold; what typed parameters would touch

**F7 is untouched, as you said.** The one line you asked for, measured on main `64ea953a` (v238), Linux:

**236 of the 303 library functions take a list, string, record or `kosh` parameter, and 247 of the 487
programs in `examples/`, `tests/stdlib/` and `lib/` call one.** (`tools/lib_mutant_witness.pointer_params`,
R8's analysis, for the library; a pass over every `prakriya` for the rest: 135 program functions in 32
files index or take a field of a parameter.)

**What that means for each way of typing parameters:**

| If typed parameters are… | What changes | What breaks |
|---|---|---|
| **optional** (an untyped parameter keeps today's meaning; `mala a` adds the check) | nothing has to change; annotating the 236 + 135 functions is one word each, at leisure | nothing; **F7 stays open for every untyped parameter**, so it closes only as fast as the annotation spreads |
| **required** for indexing (indexing an untyped parameter becomes a compile error) | the 236 library functions and 135 program functions get their one word **in the same change**, or 32 files and all of `lib/` stop compiling | **no call site changes:** `f(a)` is written the same either way |

**Either way no program's output changes.** The annotation is on the declaration, and the check is at the
call site at compile time (**a scalar passed where `mala` is declared is an error**), so the F7 program
becomes a diagnostic instead of a crash. **What the check cannot do:** tell a `mala` from a `rachana` record,
or a `mala` of the wrong length. Both are addresses. That would need the run-time tag.

**Not done, waiting for the owner.**
