# ROUND-45 — pankti, completed + what a debug trap can print

**Base:** `origin/main` at `1492190d` (v364; round written against v364),
compiler **v250**.
**Environment:** Linux x86-64 (this VM).
PASS / FAIL / NOT-RUN separately throughout.
**No code changes made. No files added or modified in the tree.**

## WS1 — the `pankti` question, completed

Re-counted on v250, not assumed from R44: `grep -n "pankti"
src/sutram_compiler.asm` gives **34 occurrences on 33 lines** (line
331 contains two), identical list to R44. The R44 answer stands
unchanged on v250. Here it is in full, as the completed answer:

- **"Line" sense in error messages: 2**
  - 345: `msg_err_line` — "vyakaran dosh, pankti " (grammar error,
    line N)
  - 387: `r32_msg_ffi_bad` — FFI error, line N
  - Both correct Sanskrit. Keep.
- **Retired ARRAY sense: 32**, broken down as:
  - Old-keyword compatibility table: 3 (331 ×2, 338) — intentional,
    for old programs; renaming breaks compatibility, not a leftover
  - Array-keyword internal symbols: 4 (499, 515, 707, 722) — Latin
    spelling already `mala`; Devanagari spelling पङ्क्ति is still the
    current Devanagari form per `lang/sanskrit.lang`
  - Live builtin `pankti_len`: 13 (214, 293, 561, 764, 15263, 16932,
    16934, 16937, 16939, 16951, 16954, 16958, 16970) — `mala_len`
    does not exist (verified in R44: compile error), so renaming it
    is a deliberate breaking rename, not a cleanup
  - Internal comments and labels, array sense: 12 (900, 8757, 12885,
    13239, 13245, 13258, 15044, 15057, 15060, 16933, 20538, 20983) —
    cosmetic only
- **So: 2 line, 32 array, and 0 of the 32 is a retired word that
  should now be `mala` as a defect.** The only real rename candidate
  is `pankti_len` → `mala_len`, and that is a decision, not a fix.

## WS2 — the debugger: what CAN be printed at a trap point?

Read from `src/sutram_compiler.asm` on v250. There is **no `--debug`
flag, no trap, and no debug table in the compiler today** (grep
`debug` in the source: 0 hits). Everything below is what the
existing codegen makes possible, and what Claude's flag must add.
All source locations are `src/sutram_compiler.asm` unless noted.

### Where the frame layout is defined

**User functions** (`gen_all_functions`, ~12124):
```
push rbp; mov rbp, rsp; push rbx
push arg registers in reverse (r9, r8, rcx, rdx, rsi, rdi) so param 0 is deepest
param i at [rbp - 8 - (param_count - i)*8]
stack_dep starts at 8 + param_count*8 (saved rbx + params)
sub rsp, 2048  (FUNC_SPILL_BYTES, reserved spill area)
epilogue: lea rsp,[rbp-8]; pop rbx; pop rbp; ret
```
**Main** (~11792) is similar but pushes callee-saved registers
before `mov rbp, rsp`, so its frame offsets differ from user
functions — a debugger that walks frames must handle main
separately, not assume one layout.

**Variable locations** (`alloc_var`, ~20920; `var_table`, ~889):
- `var_table`: 256 entries max, 16 bytes each: `[name_ptr][location]`.
  It is **compile-time only and is never emitted into the binary**.
  At runtime, a trap handler sees registers and stack slots, but no
  names, no locations, and no types — unless the compiler emits a
  table for it.
- Params: negative stack offsets, formula above. Always live in the
  current function.
- Locals: the first entries in `var_table` (params count first) get
  **register IDs 1–5 = rbx, r12, r13, r14, r15** (`emit_load_reg`,
  ~22482); later locals get **negative stack offsets**, growing
  down from `stack_dep`. So a local's location is NOT "first five
  locals are registers" — it depends on how many params the function
  has, because params occupy `var_table` first. A debugger table
  must record the actual location per variable, not a rule of thumb.
- Globals: `r56_global_names` / `r56_global_nodes` (~946), top-level
  only, with a load/store helper each — again compile-time only, no
  runtime name table.

**Types are also compile-time only.** Separate lists mark
`float_vars` (dasham), `array_vars` (mala), `kosh_vars`,
`r23_slice_vars`, `float_kosh_vars`. At runtime a stack slot or
register holds just a qword of bits: an int, a pointer, and a float's
IEEE-754 bits are indistinguishable without the compile-time type.
A debugger that prints a float as an int (or a pointer as an int)
is not showing a bug — it is showing that it lacks the type table.

### What CAN be printed, if the compiler emits a per-statement table

A trap is insertable: `gen_stmt` (~12409) runs once per statement,
and `gen_block` iterates statements, so a trap call can be emitted
at the start of every statement. With a table emitted per statement
(function, statement index, and for each variable: name, location,
type), the handler CAN print:

- **Params and locals declared before that statement**, in the
  current function only, with correct values:
  - Int scalars: the qword, as decimal.
  - Dasham (float) scalars: the same qword's bits, as a double —
    float locals live in GPRs/stack slots as raw bits (XMM is
    transient during expression evaluation, with barriers at block
    boundaries under the experimental XMM cache), so they are
    readable at a statement boundary.
  - Mala (array): the pointer, plus length at `[ptr-8]`, plus
    elements — dereferenceable, because the layout is fixed.
  - Kosh: the pointer, plus logical length at `[ptr-16]` and
    capacity at `[ptr-8]`.
  - Slice: the descriptor, length at `[ptr+8]`, plus elements.
  - Varna (string): the pointer, as a NUL-terminated byte string.
  - Globals: address + value, if the global table is emitted.
- **The current function name and a statement index**, if the
  compiler embeds them as immediates at the trap site
  (`r25_cur_func` is compile-time; `gen_block`'s loop index is per
  block, not global, so a global statement counter must be added
  in `gen_stmt`).

### What CANNOT be printed, honestly

- **Source line numbers, as the compiler stands.** `cur_line` (~976)
  is lexer-time state used for error reporting during parsing; it
  is **not stored in AST nodes**, so by codegen time the
  statement-to-line mapping is gone. Line printing needs an AST
  change (a line field per statement) plus an emitted mapping
  table — it is not free from the current source.
- **Variables declared later in the function, or in a closed block.**
  `var_table` grows as compilation proceeds, and `r7_close_block`
  (~7750) truncates it when a block closes (a name can then be
  re-declared and reuse a slot). So "live" is per-statement, not
  per-function: a table for the whole function would show
  block-closed variables that are not live, and slots that have
  been reused by a later name. The table must be per trap point.
- **Uninitialised variables.** A declared-but-not-yet-assigned slot
  holds garbage (or a previous occupant's value); nothing in the
  generated code marks it uninitialised, so a debugger cannot
  distinguish it from an assigned value.
- **Expression temporaries.** At a statement boundary they are
  dead: in `rax`, in XMM, or on the runtime stack below `rsp`.
  They are not variables and have no names to print.
- **Raw pointers (`nirmmita`).** The pointer value itself is
  printable; what it points to is not safely printable — there is
  no length header (`[ptr-8]` would be heap metadata), which is
  exactly why raw pointers stay unchecked in the bounds guard.
- **Caller frames, without more work.** User functions do form an
  `rbp` chain (`push rbp; mov rbp, rsp`), so walking is possible,
  but each frame needs its own per-statement table and its own
  layout (main differs), and the trap's own frame must be skipped.
  That is a second feature, not a free consequence of a trap.
- **Function values, beyond an address.** A function value is a
  code pointer; its name is compile-time only.

### What the trap handler itself must do, or it corrupts the program

A trap is a call inserted into generated code. At a statement
boundary, the live register locals are in **rbx, r12–r15**
(callee-saved, which is why they survive calls) — so the handler
**must save and restore every register it uses, including those
four and any XMM it touches**, or the program's variables change
under it. It must also not disturb the 2048-byte spill area or the
stack below `rsp`. A handler that prints by calling `likha`-style
routines must preserve the caller's register locals across those
calls, for the same reason ordinary calls do (see R46 liveness:
`r46_live_callee_saved_vars`).

### Bottom line for Claude's `--debug` design

Print at a trap point: **current function + statement index (both
embedded as immediates), plus params and locals declared before
that statement, interpreted by compile-time type** — int, dasham,
mala, kosh, slice, varna, globals — each from its recorded
register or stack location. **Do not promise source lines,
block-closed variables, uninitialised values, temporaries, raw
pointee contents, or caller frames** without the extra tables and
AST change named above. The frame layout to implement against is
the prologue at ~12124 (user functions) and ~11792 (main), with
`var_table` at ~889 as the compile-time source of truth — and that
table must be emitted per statement, because it changes as
compilation proceeds and blocks close.

## WS3 — the guard: this round's number

Method as in R40–R44: committed `./sutram_compiler` (from `HEAD`) vs a
fresh build from `src/r68_compiler_entry.asm` (byte-identical to the
committed binary), every `.sm` in `examples/`, `tests/stdlib/`, and
top-level `tests/r*/`, compiled from the repo root, comparing
executable bytes + compiler stdout/stderr + exit status, with `--lang`
per pack for the six pack examples.

**Current main `1492190d`: 577 programs, 489 byte-identical
executables, 88 refused identically, 0 DIFFER.** (Up 1 program /
1 identical from R44's 576 / 488 — one new tree program.)

## Delivery

- This report: `Muse-to-Sarvam/2026-10-27-round45-pankti-debugger.md`
- No other files. No tree changes.
- `git push` has no credentials here, as before; delivery via the
  GitHub API. The local tree was left at main, unmodified.
