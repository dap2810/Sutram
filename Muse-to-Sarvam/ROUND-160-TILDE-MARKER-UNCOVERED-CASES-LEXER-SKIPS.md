# ROUND-160 — the `~` region marker: what the four programs do not cover, `~` against `mandapa`, and every character the lexer silently skips

**Base:** main at `27bed64a` (compiler v315). **Read only. Nothing compiled or run.**
**Delivered:** report + `r160.json`. **Method:** read the compiler (`src/sutram_compiler.asm`,
`src/r65_arena.inc`, `src/r66_indic_lexer.inc`, `src/r32_ffi.inc`, `docs/`), traced the
relevant paths token for token, and spot-checked every decisive claim by re-reading the
cited code. All `file:line` citations are at `27bed64a`.

## Verdicts, in one paragraph

The three proposed rules do not decide the feature. Rule (2) says "keeps something"
without defining keeping; rule (1) says "reused on every pass" without defining reuse
(per-entry? per-pass? static buffer? mark discipline?) and without saying whether the
logical length resets — which decides whether Program B prints 15 or 5; and neither rule
says what counts as "something" — a descriptor, a buffer, a slice, a `mala`, a grown
element block. Of the nine named cases, one is decided for a `prakriya` but not for
`mukhya`, one is decided for refusal but not for reuse, one is decided the wrong way (the
`mala`), and six are undecided. Of the eight further cases, none is decided. `~` is not
quite a second spelling of `mandapa`: the one thing it still adds, once `mandapa`
reclaims a `kosh` and a `mala`, is reuse across passes of an object declared inside the
loop body — while `mandapa` has a budget, the address-vs-value distinction, every exit
path, a runtime second line, and fourteen mentions in each book that `~` lacks.
`mandapa` should survive. The no-marker version is not expressible with the current
analysis: the compiler has fixpoints over booleans and taints, not over quantities, and
a proof of bounded total would not give what `~` promises, which is bounded peak by
reuse. Program B's error does land on `kosh_kship`, three lines after the `~`, exactly
as the brief measured — but not because the `{` "becomes an unnamed block": there is no
unnamed-block statement in the parser. What happens is the expression parser's legacy
fallback treating an unsupported primary as `(`. And the lexer silently skips **163 of
the 256 byte values** — six printable ASCII characters (`$` `'` `@` `\` `` ` `` `~`),
30 control/DEL bytes, and 127 high-byte values. That last finding is the defect that
exists now, and it is worth more than the feature: a `$` before a name silently compiles
as if it were not there.

**Facts re-verified at this base.** A `kosh` is "a descriptor d: `[d-16]` length,
`[d-8]` capacity … `[d]` the elements. The descriptor never moves; growth moves the
elements and updates `[d]`" (`src/sutram_compiler.asm:572-573`); four 8-byte words, 32
bytes, or 56 with the R82 liveness flag (`docs/MEMORY-MODEL.md:7`). Growth allocates
fresh elements "in the arena when small, else a region"
(`src/r65_arena.inc:564-565`); growth arithmetic is `newcap = cap ? cap*2 : 4`
(`src/sutram_compiler.asm:22502`). `mandapa` gives back only `nirmmita`: "a `kosh`,
not — it is ordinary memory and keeps its bytes for the whole program, only its life
ends with the block; a `mala`, never" (`docs/MEMORY-MODEL.md:5`). `parimana()` counts
"a `kosh` by its capacity, not its length" (`docs/MEMORY-MODEL.md:9`).

**The standing precedent the rules never mention.** Everything `~` would need already
exists for `mandapa` — and it exists in three different mechanisms that do not agree
with each other: (a) the parse-time taint check (`r73_check_stmt`,
`src/sutram_compiler.asm:13123`, taint from `r73_taint`, `:12539`); (b) the codegen-time
call check (`r108_check_call`, `:12767`, over the `r108_compute_esc` fixpoint,
`:12811`); (c) the runtime generation check (`r82_param_checks`, `:10975`). The four
programs exercise none of the seams between them. Most of the cases below are those
seams.

---

## Task 1 — the nine named cases

### 1. A `kosh` declared outside `~` and grown inside it — UNDECIDED

**Today.** Nothing checks it. `r73_check_stmt` (`:13123`) handles only `AST_ASSIGN` and
`AST_RETURN`; a `kosh_kship` is a call, not an assignment. `r73_check_call` (`:8702`)
does check `kosh_kship` — but only the *value being pushed*: "the first argument is
where; the rest are what" — it taint-checks arguments from index 1 onward. Growing an
outer kosh with a plain number passes; only pushing a scratch address is refused. The
growth itself allocates from the arena or a fresh region (`src/r65_arena.inc:564-565`),
never from the scratch side, and the descriptor never moves (`:572-573`), so the outer
kosh's descriptor stays valid and its new elements are persistent memory.

**What `~` should do.** Under rule (2) read literally, this is *not* an escape:
nothing born inside `~` is kept — the kosh predates the region, and its new elements
are persistent. The `total = total + temp[0]` in Program D is the same shape
(mutation of outer state from inside) and the brief says that is not an escape. So the
honest answer under the rules is "allowed".

**Why that answer is not safe.** It holds only if growth inside `~` is defined to
allocate persistently. The rules never say where growth inside `~` allocates. If `~`
reuses memory by rewinding the arena cursor, a pass's growth is rewound while the
outer descriptor still points at it — a dangling kosh created by a legal program. If
growth allocates persistently, rule (1) fails for exactly this kosh: every pass's
growth is fresh memory, i.e. Program A's leak through a different door. And a slice of
the outer kosh taken *before* the region and used *after* it is invalidated by the
growth inside it — no check in the region sees that, because the slice predates the
region.

**Extra rule needed.** One of: (a) growth of an outer kosh inside `~` is refused; (b)
growth inside `~` allocates persistently and is explicitly exempt from reuse (state the
leak); or (c) growth inside `~` allocates from the region and the outer kosh is pinned
for the region's lifetime (state it). The three rules pick none of the three.

### 2. A slice taken inside `~` and used after it — NO (split: kosh half already refused, mala half not refused at all)

**Today.** A slice is a 16-byte descriptor in a frame slot: "this site's descriptor: 16
bytes of the frame" (`src/r23_capabilities.inc:677`). The fifteen refused shapes are
about slices escaping a *function*; a region boundary is a new boundary and the checks
do not know about it. What exists:

- Slice of a **kosh**, stored in a name: refused — but for growth reasons, not region
  reasons. `r127_check_slice_value` (`src/sutram_compiler.asm:28878`) refuses
  `vitti s = k[0:1]` whenever the base `is_kosh_var`, because "a later `kosh_kship`
  may move them (R127)". The walk (`r137_check_stmt`, `:28454`, `.assign`) allows a
  slice into a name of its own and defers to that door. So `s = temp[0:1]` inside `~`,
  used after it, is already refused — this is not a sixteenth shape, it is the old
  shape with a new boundary.
- Slice of a **mala**, stored in a name: allowed. `r127_check_slice_value` returns
  `.ok` for any non-kosh base, and the walk allows it. A mala's elements are
  persistent arena memory, so the slice stays valid today — but only because a mala is
  never reclaimed (case 5). If `~` ever reclaims a mala's buffer, this slice dangles,
  and no check exists to stop it being made.

**What `~` should do.** A slice made inside `~` must not be usable after `~`,
whichever base it has. The kosh half is already decided by accident; the mala half is
undecided by the rules, because the rules never say what a slice *is* (a descriptor
made at a site plus elements that live elsewhere) and therefore never say which half of
it is temporary.

**Extra rule needed.** A slice's lifetime is the shorter of its base elements' lifetime
and its descriptor site's region. Either the mala-slice door is closed the same way the
kosh-slice door is, or malas are explicitly exempted from reclamation and the slice is
declared valid — with the reuse consequence (case 5) stated, not silently assumed.

### 3. A `kosh` passed to a `prakriya` from inside `~` — UNDECIDED

**Today — the analysis can tell store from read, for direct uses.**
`r108_compute_esc` (`:12811`) is "a greatest fixpoint, every parameter starting as
'does not keep' and marked when some use of it is not a read (`k[i]`), a kosh
builtin's own operand, or an argument to a parameter that does not keep. Recursion is
allowed for." `r108_param_kept` (`:12878`) counts `AST_VAR` uses of the parameter
against uses that are a kosh builtin's operand (`.bcall`: "a kosh builtin's own operand
is a read", `:12971`) or an argument to a non-keeping parameter; any other use —
assignment to an outer variable, return, store into a cell or memory — marks the
parameter as keeping. An unknown callee (function value, foreign function) is refused
outright (`r108_check_call`, `:12767`: `rfx3_fn_index` negative goes to `.bad` with
`r108_msg_keep`, `:569`). Overflow is conservative: "a walk that did not finish proves
nothing — 'keeps'" (`:13016`, `.end`).

**Today — the gate is wired to one of the two call paths.** `r108_check_call` has
exactly one call site in the tree: `:21556`, in the *expression* form `.ge_funcall`.
The *statement* form `.gs_funcall` (`:19028` onward) calls only `r129_check_call` and
`r25_check_call`, then evaluates its arguments through `gen_typed_call_arg`
(`:27304`), which never calls `r108_check_call`. So `x = store(temp);` is checked and
`store(temp);` as a bare statement is not. The comment on the statement path claims
the opposite: "Use the same typed helper as expression calls so statement calls cannot
bypass dasham/kosh conversion or checks" — conversion, yes; the keep-check, no. (This
matches the R148 correction that `r108_check_call` is called only at `:21503` on its
base; the line moved to `:21556` here.)

**Today — the fixpoint is blind to borrows.** It counts only `AST_VAR` nodes. A
parameter used as `k[i]` makes no `AST_VAR` node at all — `AST_INDEX` is
"[type][name_ptr][index_node]" (`:104`), the base is a name pointer, not a node — so
an index read is invisible (benign: it is a read). But a slice of the parameter,
`k[0:1]`, is equally invisible: its base is also a name pointer. A callee that takes a
kosh parameter, slices it, and hands the slice to a `vibhag` parameter is never marked
as keeping by `r108`; the closure then rests on the slice doors (`r127`, `r134`,
`r23_check_return`), not on the fixpoint. And `kosh_kship` on the parameter counts as
a *read* (`.bcall`), so growth by the callee is "not keeping" — see further case F4.

**What `~` should do.** Rule (2) says "keeps something" without defining keeping. The
`r108` definition — store, return, forward-to-a-keeper is keeping; index,
builtin-operand, forward-to-a-non-keeper is reading — is a candidate definition the
rules never adopt, and it has the two holes above.

**Extra rule needed.** Adopt an explicit definition of keeping (including whether growth
and slice-borrowing count), and wire the check to statement calls as well as expression
calls. As stated, the rules do not decide the case: a storing callee called as a
statement passes them.

### 4. `nivartanam temp` from inside `~` — YES for a `prakriya`, UNDECIDED for `mukhya`

**Today.** For a `mandapa` kosh, returning is refused twice over. Parse time:
`r73_check_stmt`'s `.return` branch calls `r73_taint` on the return value and goes to
`r73_fail_ret` (`:12362`), which prints `r107_msg_ret` (`:561`): "[E_KOSH_MANDAPA]:
mandape rachitah kosh mandapat bahih na gacchati - nivartanam na shakyate". Codegen
time: `r126_check_return` (`:29377`) refuses a kosh return unless the prakriya is
declared to return one.

**What `~` should do.** In a `prakriya`, rule (2) decides this: returning is keeping,
so `nivartanam temp` must be a compile error. But the rules do not draw the
distinction the implementation must draw: `nivartanam temp[0]` — an element, a number
copied out — must be *allowed*. That is the point of the region ("Data read out of
scratch (`b[i]`, `akshar(b, i)`) carries no taint: copying the data out is the point of
the block", `r72_parse_mandapa` header, `:8334`; `r73_taint`, `:12539`, handles only
`CALL`/`VAR`/`BINOP`/`TERNARY` and returns 0 for an index read). The three rules say
"everything made inside `~` is temporary" and "keeps something" — they never say
values may leave while addresses may not.

**The `mukhya` half.** `r126_check_return` skips `mukhya` entirely (`:29377`:
`in_function == 0` goes to `.out`), so in `mukhya` only the taint check refuses. And
in `mukhya` the return value becomes the process exit status — nothing outlives the
program, so under rule (2) read literally there is nothing kept and nothing to refuse.
Refusing it anyway is a consistency choice, not a consequence of the rules.

**Extra rule needed.** Values (numbers, elements) may leave; descriptors, addresses,
and slices may not. And: `mukhya` returns are refused for consistency, or explicitly
exempted with the reason stated.

### 5. A `mala` declared inside `~` — NO

**Today.** A mala is never tainted, never tracked, and never refused.
`r73_note_decl` — the only call that gives a name a taint — has exactly one call site
in the tree (`:14983`, a scalar declaration *with an initializer*). The
array-declaration path never calls it; the kosh path calls `r107_note_kosh` (`:12615`)
instead, and there is no mala analogue of either. A mala declared in a block is
ordinary persistent arena memory (`.gs_decl_array`, `:19389`, via
`emit_nirmmita_from_rax`), and "returning one from a block is not refused (measured,
R166)" (`docs/MEMORY-MODEL.md:5`). So `mala m[4]` inside a block, `outer = m`,
`nivartanam m`, `m` stored in a cell — all compile today, and all are safe today,
because the bytes persist.

**What `~` should do.** The rules cannot say. Rule (1) is written for a kosh — "the
descriptor and buffer are made once" — and a mala has no descriptor, so the rules
never state whether a mala's buffer is in the reused set. Rule (2) would refuse
keeping the mala's address outside, but its bytes are persistent, so keeping it is
safe — the same asymmetry as a `mandapa` kosh, which *is* refused on escape although
its bytes also persist, on liveness grounds ("only its life ends with the block",
`docs/MEMORY-MODEL.md:5`). The rules give no principle for choosing between the mala
precedent (allowed, persists) and the kosh precedent (refused, liveness ends).

**Extra rule needed.** One of: (a) taint malas exactly like koshs; (b) refuse a mala
declaration inside `~` outright; or (c) exempt malas from `~` and admit rule (1) does
not cover them — i.e. a `~` loop over a mala still leaks one mala per pass, which is
Program A with a different type. The brief's Program A is a kosh; nothing in the four
programs shows the owner has noticed the mala version exists.

### 6. `~` nested inside `~` — UNDECIDED

**Today (`mandapa`).** Nesting works by stack discipline: depth is capped
(`R73_MAXDEPTH equ 32`, `:35`; `r82` slots cap at 62, `r82_block_enter`, `:10703`),
each block takes a mark, a rewind returns to its own mark, and `r82_gen_rewind`
(`:10819`) "ends blocks d .. current", so an inner rewind never disturbs an outer
block's live data.

**What `~` should do.** The rules say nothing about nesting: no depth cap, no
statement that an inner region's reuse must not disturb outer live data, and — the
sharp end — no statement about whether escaping from the inner region into the *outer*
region counts as an escape. It should: the outer region ends too, and the inner
region's memory is reused while the outer region is still running, so
`outer_kosh = inner_kosh` is use-after-reuse even though both names are "inside `~`".
But under a loose reading of rule (2) ("outside *it*" = outside the outermost `~`?) it
is not an escape at all. A nested `~` also raises the question rule (1) never answers:
is the inner region's memory reused *with* the outer's — one shared pool with marks,
or one buffer per region site? The two give different answers when the inner region is
entered from two different outer passes.

**Extra rule needed.** Regions nest as a stack; escape from an inner region to any
enclosing region is an escape; inner reuse never disturbs outer live data; state a
depth cap.

### 7. `~` with no braced body — UNDECIDED (and today: silent)

**Today.** The lexer has no `~`: the dispatch at `:7381-7422` handles delimiters,
`+ - * / % & | ^ = < >`, and then falls through to "; Unknown char — skip"
(`:7420-7422`: `inc r13; jmp .lex_loop`). So `~` is silently deleted. In the braced
form (Program B) the `{ … }` becomes an unnamed plain block — no mark, no rewind, no
taint, no liveness slot — and the error lands three lines later on `kosh_kship`,
exactly as the brief reports. In the bare form (`~ kosh temp[1]` on its own line) the
statement parses as an ordinary declaration and there is no error at all, anywhere:
the region simply never existed. (Task 3 corrects the "unnamed block" part of this
account: there is no unnamed-block statement in the parser. See §Task 3 below.)

**What `~` should do.** The rules do not define the bare form. The brief's first line
says the marker is "written inside a scope, marking everything after it as temporary"
— read literally, a bare `~` marks the *rest of the enclosing scope*, which contradicts
the braced form's block reading. The `mandapa` precedent points the other way:
`r72_parse_mandapa` (`:8338`) calls `parse_body` (`:8379`), and `parse_body`
(`:8134`) accepts a braced block, an indented block, or a single statement — so a bare
`mandapa` is one statement (or one indented block). If `~` is implemented as a keyword
like `mandapa`, the bare form is one statement; if it is implemented as the brief's
first line says, it is the rest of the scope. Those are different programs.

**Extra rule needed.** Define the bare form — one statement per the `mandapa`
precedent, or refused outright — and correct "everything after it" to "everything in
its body". As stated, the rules do not decide what `~ kosh temp[1]` followed by three
more statements means.

### 8. `~` at the top level of `mukhya` — UNDECIDED (and mostly vacuous)

**Today.** Nothing forbids a `mandapa` at the top level of `mukhya`:
`r72_parse_mandapa` has no position restriction, the block gets its mark and its
rewind as its last statement, and a kosh inside it gets a liveness slot. `mukhya` runs
once, so the region is entered once and left once.

**What `~` should do.** Rule (1) is vacuous here: there is no second pass to reuse
anything on. Rule (2)'s boundary coincides with the function boundary, where the kosh
doors already refuse (global store, return) but the mala and slice doors do not (cases
2 and 5). Rule (3) constrains only programs *without* `~`, so it says nothing about
what a top-level `~` may cost. A top-level `~` is therefore either a no-op (it refuses
nothing new and reuses nothing) or a redundant spelling of "this function's body is
temporary" — which is trivially true, since everything dies at exit.

**Extra rule needed.** Either forbid `~` at function top level as useless, or define
what it adds (e.g. it still refuses escapes to globals and foreign functions). Note
the live version of this case is further case F2: a `~` at the top level of a
*prakriya* that is called from a loop, where reuse across calls is a real question.

### 9. `~` inside `yadi` — YES for refusal, UNDECIDED for reuse

**Today.** Refusal is static, not conditional: `r73_check_stmt`'s weak update "never
clears a taint — it may sit in a `yadi`/loop branch that does not run (R145 E11)"
(`:13185-13186`). A `kept = temp` inside a branch is refused whether or not the branch
runs. Names declared in the branch end with it (`r7_close_block`), so use-after-branch
through a name is already a different error; escape needs an outer name, which is
exactly the tainted assignment the check refuses.

**What `~` should do.** Refusal: decided, YES — rule (2) applies to a branch exactly
as to a loop body, and the existing check is branch-insensitive, so there is nothing
new to decide. Reuse: undecided. Rule (1) says "reused on every pass" and a branch has
no passes; if the `yadi` is not in a loop, the region runs at most once per function
call and reuse is vacuous (as in case 8). If the `yadi` *is* in a loop, the branch may
run on some passes and not others, and the region's memory must be reused across
passes even though the branch does not run every pass — the rule as written does not
cover that, because it ties reuse to passes of *the region's own* loop.

**Extra rule needed.** Reword rule (1) as per-entry reuse — "made once per region site,
reused on every entry" — which decides the loop, branch, and call cases uniformly. As
literally stated ("every pass"), the `yadi` case is undecided, and the interesting
sub-case (branch inside a loop, entered irregularly) is not covered at all.

## Task 1 — further cases the four programs do not cover

**F1. A `~`-kosh stored into a module-level variable through a `prakriya`.**
Directly, this is decided: `r126_check_assign`'s `.var` branch refuses a kosh into a
module `vitti` (`:29223`, `r126_d_glob`, `:614`), the taint check refuses it first (a
global has depth 0, `r73_var_depth`, `:12452`), and a module initializer has its own
door (`r56_gen_global_initializers`, `:18382`, R141). But through a setter —
`set(temp)` inside `~`, where `set` stores its parameter in a global — the refusal is
the `r108` fixpoint, and the statement-call hole in case 3 lets it through: `set(temp);`
as a bare statement is never checked. Rule (2) decides the direct form and not the
indirect form. *Verdict: UNDECIDED as implemented; extra rule: the keep-check must
cover every call form.*

**F2. A `~` region inside a `prakriya` that is called from a loop.** Rule (1) "made
once and reused" suggests one static buffer per region site. That breaks under
recursion and re-entry: two live activations of the same `prakriya` would share one
buffer, and the inner call would overwrite the outer call's live data. The `mandapa`
discipline avoids this because the mark is a hidden *local* ("one per nesting depth
NN, so recursion-safe", `r72_parse_mandapa` header) on a global bump arena — nested
entries get distinct ranges, and reuse happens by rewinding, not by sharing one
buffer. The rules never choose between a static buffer and mark discipline, and the
choice decides both recursion and the cross-call case (a caller holding a descriptor
across calls). *Verdict: UNDECIDED; extra rule: reuse is per-entry within one
activation, stack-disciplined; recursive entries get fresh memory.*

**F3. A slice of an *outer* kosh taken inside `~`.** Already refused — but for the
wrong reason. `vitti s = outer[0:1]` is refused by `r127_check_slice_value` (`:28878`)
because a later `kosh_kship` may move the elements, whether or not any region exists.
The region question is different: the slice's *descriptor* is made inside `~` while
its elements are outside it. For an outer *mala* the binding is allowed (case 2) and
the slice stays valid, since the elements persist. The rules never say whether a slice
is temporary because of its descriptor site or because of its elements. *Verdict:
UNDECIDED; extra rule: a slice's lifetime is the shorter of the two (see case 2).*

**F4. A `kosh` declared inside `~` and grown by a callee.** `grow(temp)` where `grow`
runs `kosh_kship` on its parameter is allowed today: kosh parameters may grow (R129,
v304 — "the caller sees it", `:22441`), `r108_param_kept` counts `kosh_kship` as a
*read* (`.bcall`), and `r129_may_grow` (`:29042`) tracks growth transitively only for
slice safety. But growth allocates persistent arena/region memory, so a `~`-kosh grown
by a callee on every pass leaks one buffer per pass — Program A's leak with the growth
outsourced. The rules do not say whether callee growth counts as keeping, as
reuse-breaking, or as neither. A region tag on the descriptor (R82's slot/generation
is exactly such a tag) would let `kosh_kship` know it is growing a region kosh — but
`r82` checks only at parameter entry (`r82_param_checks`, `:10975`), never at
`kosh_kship`. *Verdict: UNDECIDED; extra rule: either refuse passing a `~`-kosh to a
may-grow callee, or define growth inside `~` as region-allocated.*

**F5. Interaction with `parimita` budgets and `parimana()`.** `parimita` "covers what
is written inside it: a kosh, or what a called prakriya allocates, is not counted"
(`:8905-8914`). So a `~`-kosh's descriptor and buffer escape any enclosing `parimita`
budget entirely, and reuse across passes raises a question the budget never answers:
is a reused buffer counted once, or once per pass? `parimana()` counts a kosh by
capacity, not length (`docs/MEMORY-MODEL.md:9`) — a reused buffer should count once
and a reclaimed one should stop counting, but the counting code for kosh regions is
unreachable: `r101a_emit_kosh_alloc` (`:9122`) begins `jmp emit_nirmmita_from_rax`, so
the `0parimana` counting below it never runs, and the count comes only from the arena
cursor, which never retreats. The rules say nothing about either meter. *Verdict:
UNDECIDED; extra rule: state whether `~` allocations count against an enclosing
budget, and what `parimana()` reports for a reused and for a reclaimed buffer.*

**F6. Interaction with the R82 liveness flag.** `r82_on` is program-global: "a kosh
made inside a `mandapa` lives as long as the block. Only in a program that declares a
kosh inside a `mandapa` (`r82_on`; every other program compiles to the same bytes)"
(`:10642-10653`) — one `mandapa` kosh makes *every* kosh in the program 56 bytes with
generation checks and gives every kosh parameter an entry check. If `~` reuses that
mechanism, one `~` anywhere changes all koshs program-wide; if `~` is purely
compile-time, escapes through the paths the compile-time checks miss (statement
calls, FFI) have no backstop. And reuse defeats the generation check unless the
generation is refreshed on every entry: a stale pass-1 descriptor still matches a
pass-2 generation if the slot is not re-written. (Side note, re-verified:
`r82_param_checks` is called from `gen_all_functions` at `:18714`, before `gen_block`,
so its synthesized `likha` call relies on the `gen_expr` fallback walk, not the
checked flag — the R148 correction, same shape at this base.) *Verdict: UNDECIDED;
extra rule: state whether `~` gets runtime generations (with the program-wide 56-byte
cost) or is compile-time only, and require a generation refresh per entry.*

**F7. Control exits: `krama` / `agrim` / `nivartanam` out of `~`.** `mandapa` wraps
every exit: jumps get `r73_wrap_jump` (`:8438`, rewind to the outermost block the jump
leaves), returns get `r73_ret_mark` (`:8422`) plus `r73_gen_ret_rewind`
(`src/r65_arena.inc:533`). A `~` that only reclaims at its last line leaks or reuses
wrongly on `break`, `continue`, and early return — and a `continue` that skips the
reclaim reuses a half-used buffer on the next pass. The three rules mention no control
flow at all; rule (1)'s "reused on every pass" silently assumes the region is always
left through its end. *Verdict: UNDECIDED; extra rule: every exit path
reclaims/rewinds.*

**F8. A `~`-kosh or slice passed to a foreign (FFI) function — CORRECTED.** The first
draft of this case said the walk defers a kosh slice to a door that does not exist on
the FFI path. That was true at v313 (R148's fifteenth shape) and is **stale at this
base: the door was built at v314** (R152). `r33_gen_foreign_funcall`
(`src/r32_ffi.inc:666`) now checks every argument: "The foreign call is a door like
every other: a value that holds a kosh — a slice of one, a call or ?: giving one, a name
holding a slice — does not go to C" (`:686-690`), via `r134_holds_kosh` (`:699`) and
the refusal `r152_d_ffi` ("the foreign call's door"). So a slice to a foreign function
**is** refused at this base, and F8's slice half is closed. What remains is narrower,
and it is real: a kosh passed **by its own name** to a foreign `ptr` argument is
deliberately allowed ("A kosh by its own name still does (as its elements, for ptr;
refused below for i64 and f64)", `:690-691`) — the foreign function receives the
elements address — and the statement-form call path reaches
`r33_gen_foreign_funcall` directly, bypassing `r108_check_call` (case 3), which is the
check that refuses an unknown callee in expression calls. A foreign function may store
whatever it is given, so handing it a `~`-kosh's elements pointer as a statement is a
keep the rules never mention and the checks never see. *Verdict: UNDECIDED, narrowed;
extra rule: a foreign callee is an unknown keeper for a kosh by name too — refuse a
region kosh (and its elements pointer) to any foreign function, in both call forms.*

### Summary table (Task 1)

| # | Case | Decided by the three rules? |
|---|---|---|
| 1 | Outer kosh grown inside `~` | UNDECIDED — allocation site of growth unspecified |
| 2 | Slice inside `~`, used after | NO — kosh half refused (wrong reason), mala half not refused |
| 3 | Kosh passed to a `prakriya` | UNDECIDED — fixpoint can tell, gate misses statement calls, blind to slice borrows |
| 4 | `nivartanam temp` | YES (prakriya) / UNDECIDED (`mukhya`; value-vs-address unstated) |
| 5 | `mala` inside `~` | NO — no descriptor, no taint, no rule covers it |
| 6 | `~` nested in `~` | UNDECIDED — no nesting semantics |
| 7 | `~` with no braced body | UNDECIDED — "everything after it" vs one statement |
| 8 | `~` at top of `mukhya` | UNDECIDED — reuse vacuous, boundary redundant |
| 9 | `~` inside `yadi` | YES (refusal) / UNDECIDED (reuse — "every pass" has no meaning for a branch) |
| F1 | Stored to a global via a setter | UNDECIDED as implemented (statement-call hole) |
| F2 | `~` in a `prakriya` called from a loop | UNDECIDED — static buffer vs mark discipline |
| F3 | Slice of an outer kosh/mala in `~` | UNDECIDED — descriptor site vs elements |
| F4 | `~`-kosh grown by a callee | UNDECIDED — growth is counted as a read |
| F5 | `parimita` / `parimana()` | UNDECIDED — budgets exclude koshs, meters undefined for reuse |
| F6 | R82 liveness flag | UNDECIDED — program-wide cost vs no backstop |
| F7 | `krama` / `agrim` / early return | UNDECIDED — no exit-path rule |
| F8 | Foreign function | UNDECIDED, narrowed — slice door closed at v314; kosh-by-name statement pass still open |

The pattern is not that the rules are wrong in one place. It is that rule (2) says
"keeps something" without defining keeping, rule (1) says "reused on every pass"
without defining reuse (per-entry? per-pass? static buffer? mark discipline?), and
neither rule says what counts as "something" — a descriptor, a buffer, a slice, a
mala, a grown element block. The `mandapa` machinery answers all of those questions in
code, in three mechanisms that disagree with each other at the seams (cases 3, F1,
F8); `~` as proposed answers none of them in words.

---

## Task 2 — is `~` a second spelling of `mandapa`?

### What `mandapa` is today (grounding)

- A statement and a scope. `r72_parse_mandapa` (`src/sutram_compiler.asm:8338`)
  builds `AST_BLOCK [ vitti 0mNN = <scratch cursor> ; <body> ; <rewind to 0mNN> ]`,
  one hidden mark per nesting depth, recursion-safe, nesting capped at 32
  (`R73_MAXDEPTH equ 32`, `:35`). It takes an indented body, braces, or one statement
  on the line (`docs/LANGUAGE-REFERENCE.md:1255-1266`); it is a statement, so it sits
  in loops, `prakriya` bodies, and recursion. Variables declared in it are scoped to
  it.
- `nirmmita` written inside it takes the scratch side of the 1 GiB arena
  (`BN_NIRM_SCRATCH`, `:246`); every exit gives it back — end of body, `nivartanam`,
  `krama`/`agrim`, a failure passed on by `prasar` (`src/r65_arena.inc:404`,
  `r73_gen_rewind`; `:21001,21023`, `r73_gen_ret_rewind`). The pages are reused by the
  next block, not returned to the OS. **So for `nirmmita`, reuse across passes already
  exists: same pages, cursor reset, zeroed.**
- A `kosh` made in it keeps its bytes for the whole program; only its liveness ends.
  "A `kosh` declared in an open mandapa is only remembered, so that `r108_check_call`
  can refuse to give it to a `prakriya` that keeps it… No arena slot: reclaiming waits
  for the descriptor." (`:12651-12655`, `r108_kosh_alloc`). The descriptor never
  moves: four 8-byte words, 32 bytes — length `[d-16]`, capacity `[d-8]`, elements
  `[d]`, region size `[d+8]` — 56 bytes in a program that makes any `kosh` inside a
  `mandapa` (three R82 words before them: line, liveness slot, generation)
  (`:572-573,10645-10652`; `docs/MEMORY-MODEL.md:8`). Growth moves the elements and
  updates the descriptor; `newcap = cap ? cap*2 : 4` (`:22502`). Default capacity is 4
  (`:15049-15058`).
- A `mala` made in it is never given back and escapes with no refusal at all. Its
  declaration allocates by plain `emit_nirmmita_from_rax` on the persistent side
  (`.gs_decl_array`, `:19389`), with no `r107_note_kosh`-style taint call anywhere on
  the mala path (the array declaration at `:14930-14950` calls neither
  `r82_note_kosh_decl` nor `r107_note_kosh`). Reference: "a `mala`, never — a
  declaration is not a `nirmmita` call, it keeps its bytes for the whole program, and
  returning one from a block is not refused (measured, R166: 200,000 calls each making
  a `mala` of 31 numbers in a block end with `parimana()` at 51,200,000)"
  (`docs/LANGUAGE-REFERENCE.md:1293-1297`).
- Escape checks, compile time: scratch addresses via `r73_taint` / `r73_check_stmt`
  (`:12539,13123`), with the loop back-edge fixpoint `r73_fix` (`:8554`); a block
  `kosh` via `r107_note_kosh` (`:12611`), `r108_check_call` (`:12726`) and the greatest
  fixpoint `r108_compute_esc` (`:12811`, "every parameter starting as 'does not keep'");
  fifteen slice shapes via `r137_check_stmt` (`:28454`); plus the R82 runtime
  generation check as a second line (`:10645-10652`).
- Budget: `mandapa parimita N` only — `r103_parse_budget` (`:8933`) is called from
  exactly one place, `r72_parse_mandapa` (`:8356`). "The block's own `nirmmita`… may
  use at most N bytes in all… Like the block itself, it covers what is written inside
  it: a `kosh`, or what a called `prakriya` allocates, is not counted. Linux ELF only,
  as the block (PE: inert, unchecked)." (`:8906-8912`) — the PE half of that comment
  is stale at this base: `r65_active` now returns 1 on PE as well as ELF
  (`src/r65_arena.inc:120`), so do not rely on it.
- `parimana()` counts logical bytes held, kosh by capacity not length
  (`.ge_call_parimana`, `:23892`); a program without `parimana` compiles to the same
  bytes, a program with no `kosh` in a block compiles to the same bytes, a program
  without `parimita` compiles to the same bytes (reference §19).

### Q1. What can `~` do that `mandapa` cannot, once `mandapa` reclaims a `kosh` and a `mala`?

Exactly one thing, and it is a cost, not a safety property: **allocate once and reuse
across passes for an object declared inside the loop body.**

- `mandapa`'s mechanism is entry-mark plus exit-rewind. A `mandapa` inside a loop body
  exits every pass, so a reclaim built on that mechanism frees at the end of each pass
  and allocates fresh on the next: fresh descriptor, fresh elements, regrowth from
  capacity 4 every pass (`newcap = cap ? cap*2 : 4`). `~`'s promise 1 is the opposite
  shape: descriptor and buffer made once, kept across passes, grown capacity kept. The
  two differ in allocation work per pass and in peak transient use, not in values —
  *provided* `~` resets the logical length each pass.
- That proviso is load-bearing and unstated in the brief. Program B must print
  `total=15` like Program A. If `~` reuses the descriptor without resetting its
  length, `kosh_kship` appends: pass 1 pushes 1, pass 2 pushes 2, `temp[0]` stays 1 on
  every pass, and the total is **5, not 15**. If it resets length to 0 (keeping
  capacity), the total is 15. The brief's promise 1 ("descriptor and buffer are made
  once and reused") does not say which. `mandapa`+reclaim has no such ambiguity: a
  fresh `kosh` each pass gives 15 trivially. `~` needs a stated reset rule — length
  reset, and whether elements are zeroed — before Program B even has a defined answer.
  The nearest existing rule is `kosh_clear`: "clear only the kosh logical length
  in-place, leaving capacity and allocation intact" (`:22158`), i.e. exactly the reset
  `~` would need.
- The same reuse for `nirmmita` is **not** new: the scratch rewind already reuses the
  same pages across passes. The gap `~` would close is only for `kosh`/`mala`
  descriptors and their buffers.
- The reuse is also expressible without `~` today, by moving the declaration: the
  reference already teaches it — "Make a `kosh` that is reused once, outside the loop,
  and empty it with `kosh_clear` each pass: 0 MB"
  (`docs/LANGUAGE-REFERENCE.md:1417`). What `~` adds over that idiom is keeping the
  declaration *inside* the loop body, at the point of use. That is real ergonomics,
  but it is a placement convenience plus a cost saving, not a new guarantee: nothing
  `~` refuses is unrefused by `mandapa`, and nothing `~` reuses is unreusable by
  `mandapa` with the declaration moved.
- One more candidate, and it fails: `~` as a *suffix* marker ("marking everything
  after it as temporary") inside a scope, without opening a new block. In the brief's
  own examples `~` is always braced (`~ { … }`), which *is* a block, so in the form
  shown there is no structural difference from `mandapa`. In a bare suffix form, `~`
  would mark temporaries without a scope boundary — but then a name declared after
  `~` would stay visible after its storage was reclaimed, which is the escape problem
  in a new shape, not a capability. If the bare form also closes the scope, it is
  `mandapa` spelled differently.
- What `~` does **not** add, even under the hypothesis: no new refusal (Program C's
  escape is already `E_KOSH_MANDAPA` under `mandapa`: store-to-outer-variable,
  `r73_check_stmt` / `r107_note_kosh`); no new coverage of `mala` (both need a new
  check — `mandapa` has none today either, so `~` would have to build it from scratch
  just as `mandapa` would); no help for allocations inside a called `prakriya` (the
  block is lexical: "a block in a CALLER does not reclaim what a LIBRARY function
  allocates inside its own body", `docs/decisions/MEMORY-DECISION.md:92` — a `~` in
  the caller would have the same limit unless specified otherwise).

A note on the hypothetical: reclaim is not a free assumption. The reference records
the decision the other way — "Decided (R103, v285): the block does not take a `kosh`'s
memory back; the `kosh` keeps it for the program's life"
(`docs/LANGUAGE-REFERENCE.md:1406`), because the R82 runtime check reads the dead
`kosh`'s header after the block, so the header must still be there: "Giving the region
back would make a dead `kosh` reaching a `prakriya` a crash (or, if the address were
reused, a silent read of another `kosh`) instead of `E_KOSH_MANDAPA` with its line".
Any reclaim design has to keep the headers, or move the check entirely to compile
time. The scope-rewind design in general is rejected: "needs an owner-aware design
with generational handles, prototyped separately" (ROUND-159 brief; ROUND-158 brief).
Q1 takes the hypothetical as given anyway, as instructed.

### Q2. What can `mandapa` do that `~` cannot?

As proposed, `~` is a marker with three sentences; `mandapa` is an implemented
feature. The differences:

1. **A budget.** `mandapa parimita N` refuses past N bytes with `E_PARIMITA` before
   the memory is given (`:8906-8912,9007`). `~` has no budget parameter, no number, no
   refusal — there is nothing in the proposal to attach a cap to, and a bare `~`
   cannot express "at most N bytes per pass" or "at most N bytes in total". This is
   the one `mandapa` capability with no `~` counterpart at all, even in principle,
   without extending the proposal.
2. **The address-vs-value distinction.** `mandapa` refuses addresses leaving the block
   and allows numbers read out of scratch: "Data read out of scratch (`b[i]`,
   `akshar(b, i)`) carries no taint: copying the data out is the point of the block"
   (`:8334-8335`); `r73_taint` returns 0 for comparisons and for values read through
   an index (`:12539`). `~`'s rule 2 as written — "a program that keeps something from
   inside `~` outside it is a compile error" — does not draw that line. Read literally,
   Program B itself is refused: `total` is declared outside, and
   `total = total + temp[0]` keeps something made inside (a number read from `temp`)
   outside. The proposal needs `mandapa`'s distinction to let its own motivating
   program compile, which means `~` as specified is either wrong or incomplete, and
   the completion is a copy of `mandapa`'s rule.
3. **Every exit.** `mandapa` rewinds on end-of-body, `nivartanam`, `krama`, `agrim`,
   and failure propagation (`prasar`); the rewind before a return goes to the outermost
   block's mark, and a jump leaving blocks rewinds the ones it leaves (`:8420-8460`).
   `~` says nothing about any exit: what a `krama` out of a `~` loop does, what a
   `nivartanam` from inside `~` reclaims, whether a failure inside `~` reuses or
   leaks. Each answer would be a copy of the `mandapa` rule.
4. **Nesting, re-entry, and a runtime second line.** `mandapa` nests to 32, is
   recursion-safe via one hidden mark per depth, and a block re-entered on the next
   loop pass makes a new generation while the old `kosh` stays dead — enforced at
   runtime too (R82: fresh generation on entry, cleared on exit, checked on entry to
   any `prakriya` taking a `kosh` parameter). `~` specifies none of nesting,
   re-entry, or a runtime check; a reused descriptor that a stale alias still names is
   exactly the hazard the R82 generation exists for, and `~`'s reuse makes stale
   aliases *more* likely, not less.
5. **Measurement.** `parimana()` falls when a `mandapa` ends and counts a `kosh` by
   capacity. `~` has no stated interaction with `parimana()`: a reused `kosh` should
   presumably count once, by its kept capacity — but that is a specification `~` does
   not have.
6. **It exists.** `mandapa` is a keyword (`KW_MANDAPA`, `:191`, keyword table
   `:880,897`) with a Devanagari spelling `मण्डप` (`:1374`), a reference section (§19,
   `docs/LANGUAGE-REFERENCE.md:1247-1500`), a status-box entry in
   `docs/MEMORY-MODEL.md:5-10`, fourteen mentions in each book, worked examples (286,
   287, 299, 303, 304, 316–318, 320, 321), and measured results. `~` has no token, no
   keyword, no Devanagari form, no name a reader can search for or ask about, and no
   example. (Whether `~` is silently skipped by the lexer, and what else is, is Task
   3's question, not this note's.)
7. **Byte-identity guarantees already proved in the negative.** A program with no
   `kosh` in a block, without `parimana`, without `parimita`, compiles to the same
   bytes as before (reference §19). `~`'s rule 3 promises the same, but it is a
   promise about unbuilt code; `mandapa`'s is a property of shipped code with the
   gating (`r82_on`, `r107_used`) visible in the source.

### Q3. If the answer is "nothing, either way" — which spelling survives, and why?

The premise does not quite hold: Q1 finds one real delta (reuse across passes for a
loop-local object) and Q2 finds several the other way. But even granting the premise —
suppose the reuse were folded into `mandapa`, so the two spellings were behaviourally
identical — `mandapa` survives, for four reasons, in order:

1. **It is already in the language and taught.** A keyword with a Sanskrit and a
   Devanagari spelling, a reference section, book chapters, examples, and error
   messages a student can read. `~` would start from zero and would have to re-teach
   every rule in Q2 above under a new name. Two spellings for one concept doubles the
   teaching surface: every book paragraph, every error `Sanket`, every gate would have
   to say "or `~`".
2. **It already has the escape checks and the budget mechanism.** The taint table,
   the loop back-edge fixpoint, the keep-analysis fixpoint, the R82 generations, the
   budget chain — all exist, all are gated so programs that do not use them pay
   nothing. A second spelling either duplicates that machinery (two implementations to
   keep in agreement) or shares it (in which case it is one feature with two names,
   and the second name is pure cost).
3. **The compiler already implements it.** `mandapa` is ~700 lines of parser,
   checker, and codegen across `src/sutram_compiler.asm` and `src/r65_arena.inc`,
   plus the R82/R103/R107–R109/R137 machinery. `~` would be a new lexer token, a new
   parse path, and a new specification for exits, nesting, budgets, and `parimana()` —
   all to arrive back at the same behaviour.
4. **What each costs a reader.** `mandapa` is a word: it says "pavilion, hall" — a
   place you enter and leave, which is what the block does. `~` is punctuation with no
   name, no pronunciation, and no meaning a reader can infer; it can only be
   memorised. The language's own norm is words, not sigils (the design note records
   the owner rejecting braces on `mandapa` because they would look like a `rachana`
   literal, and choosing the indentation block as the language's norm,
   `docs/decisions/MEMORY-DECISION.md:122-143`).

The honest form of the owner's question is therefore not "one spelling or two" but
"where does the reuse go". The answer: on `mandapa`. Either as the existing idiom
(declare the `kosh` outside the loop, `kosh_clear` each pass — 0 MB, reference §19)
or, if declaring inside the loop matters, as a `mandapa` behaviour: hoist the
allocation out of the loop and reset the length at pass start. Hoisting is new codegen
either way — allocations are emitted inline at the declaration statement today,
nothing hoists them — so spelling it `~` saves no work and buys a second concept.

### Q4. Is there a version where the marker is not needed at all — the compiler proves a loop's allocations are bounded and refuses the one that is not?

Short answer: **no, not with the current analysis, and not in the form that would make
the marker unnecessary.** What exists is the wrong shape for the proof in one specific
sense (quantities, not booleans), and even a successful proof would answer a different
question from `~` (bounded total, not bounded peak). Detail:

**What the compiler knows about a loop today.** `chakra i = start tak end`: an
`AST_FOR` node holding `[var][start_expr][end_expr][body]` (`:106,15519-15532`). The
bound is an arbitrary expression, re-evaluated on every pass at the test (`.gs_for`,
`:20256`; the slow path calls `gen_expr` on the end expression each iteration). The
test is **inclusive**: ascending loops branch back while `var <= end`, descending while
`var >= end` (`:20450-20470`). Direction is known only when *both* bounds are
`AST_NUM` literals and start > end (`.gf2_dir_done`, `:20275-20290`). There is no
trip-count computation anywhere in the tree (no match for "trip" outside unrelated
words). `yavat (cond)` is `AST_WHILE [cond][body]` (`:15777-15806`); `kuru … yavat`
is `AST_DO_WHILE`. The condition is an arbitrary expression. There is no bound at all.
The only compile-time evaluation of values is `fold_const` (`:16802`): it folds a
`BINOP` whose *both* operands are `AST_NUM` literals (plus string concatenation). No
name is ever replaced by its value — a `sutra` constant is "treated as vitti"
(`:15441`), a variable bound is a variable. So the only bounds the compiler can know
exactly are literal bounds (or literal arithmetic on them, e.g. `tak 2+3`). A bound
that is a variable, a call, or input is opaque. The only other numeric check on loops
is `r96_check_for_float` (`:8863`): it refuses a `dasham` bound because the counter
adds 1 and compares with `cmp`. That is a type check, not a bound proof.

**What the compiler records about allocations in a loop.** Nothing per loop, and
nothing quantitative. Allocations are emitted inline at code generation, in statement
order; there is no table of allocation sites per loop, no per-loop byte total, no
capacity variable. The one loop-scoped record that exists is `r73_flows` (`:8525`):
`(kind, name, depth, value-node)` for assignments, stores, and returns — recorded
**only while inside a `mandapa`** (`r73_record` returns at once when `r72_mdepth == 0`),
capped at 4096 entries, and holding value *nodes*, not byte sizes. Outside a `mandapa`
there is no loop record at all. A `kosh`'s capacity is a runtime value in `[d-8]`; the
compiler never tracks it symbolically. Growth is doubling with a floor of 4, so the
cost of a pass depends on the whole history of pushes, not on the pass alone. A `mala`'s
size expression is evaluated at runtime each time its declaration executes
(`.gs_decl_array`, `:19389`); a `nirmmita(n)` size is a runtime value. A `kosh_kship`
inside a `yadi`, a nested loop, or a called `prakriya` makes pushes-per-pass
data-dependent. The closest thing to an interprocedural allocation summary is
`r129_may_grow` (`:29044`): **one bit per function** — "this function, or one it calls,
runs `kosh_kship`". It is a greatest-fixpoint over booleans, like `r108_compute_esc`
(one bit per parameter: keeps / does not keep) and `r73_fix` (a taint, i.e. a small
integer depth, maximised to a fixpoint). `rfx2_analyse` is a fixpoint over 2-bit value
kinds per name. All three are monotone over *finite, tiny* lattices with trivial
termination (a bit flips once; a taint rises at most to depth 32).

**What the proof would need.** For a loop `L` with body allocations, to conclude
"total bytes bounded" the compiler would need, at minimum: (1) **A trip-count bound
T(L)** as a compile-time integer or interval: for `chakra`, `end − start + 1` with both
bounds literal, *plus* a proof that neither bound's variable is assigned in the body or
by any callee (the end expression is re-evaluated per pass, so a body assignment to the
bound variable changes T); for `yavat`/`kuru`, no such bound exists in general — the
condition is arbitrary and the loop may not terminate. (2) **A per-site, per-pass byte
bound**: for each allocation site in the body (including sites inside called
`prakriya`s, transitively, and inside nested loops), the maximum bytes that site
allocates on one pass — which for a `kosh` is not a constant but a function of the
pushes so far (doubling growth), and for a `mala`/`nirmmita` is a bound on a runtime
size expression. (3) **An interprocedural summary with quantities**: the `r129_may`
bit would have to become a per-function, per-parameter allocation function (bytes as a
function of call count and argument sizes), over the call graph including recursion —
recursion depth itself then needs a bound, which is the same problem one level up.
Foreign functions and function values are opaque: no summary exists, so any call to one
must count as unbounded (or be refused outright). (4) **Alias accounting**: two names
can hold one `kosh` descriptor, so counting per name double-counts one growth; a
`kosh` grown through a parameter (allowed since v304, R129) must be attributed to the
caller's object, not the callee's local. (5) **A cap to compare against**: "bounded"
by itself is not a refusal criterion — a loop with T = 10⁹ and one byte per pass is
bounded and still exhausts the 1 GiB arena. The refusal needs a *budget* (bytes),
which is exactly what `mandapa parimita N` already is: a programmer-stated number, not
a compiler-proved one.

That is an interval/affine abstract interpretation over the whole program with
widening — a new analysis and a new lattice. The existing fixpoint *shape* (whole-AST
walks to convergence, as in `r108_compute_esc` and `r129_fixpoint`) could host it, so
the analysis is not "fundamentally the wrong shape" as a walk; it is the wrong shape as
a *domain*: every existing fixpoint tracks a boolean, a kind, or a depth — none tracks
a number that grows, and none has a widening operator, which a trip-count/byte-count
domain needs to terminate on loops. Extending `r108_compute_esc` to a boundedness
proof is not an extension; it is a different analysis that happens to also be a
fixpoint.

**What it cannot prove (so the refusal would misfire).** Any `yavat` / `kuru` loop with
an allocation inside: no bound exists. Refusing these refuses ordinary programs
(read-until-done loops that allocate a buffer per item are the normal shape, not an edge
case). Any `chakra` whose bound is a variable, a `sutra`, a call, or input (`grahan`):
the compiler cannot know the value, and the value can change per pass. Any loop that
calls a `prakriya` that allocates (including the standard library's formatting and
bigint helpers, which allocate scratch per call —
`docs/decisions/MEMORY-DECISION.md:93`), any loop over a foreign function, any
recursive call inside a loop. Any loop where the per-pass allocation depends on data:
`kosh_kship` under a `yadi`, a `mala` whose size is computed, a `nirmmita` of a computed
size. A `kosh` declared *outside* the loop and grown inside it: its per-pass allocation
is usually zero after warm-up, but proving that requires tracking capacity as a function
of total pushes so far — state carried across passes, which no current analysis holds.

The only fragment that *is* provable with a modest new analysis is narrow:
literal-bound `chakra` (`tak` with `AST_NUM` bounds, or `fold_const`-foldable
arithmetic), a body with no calls and no `yadi`-guarded pushes, allocations of literal
size only, no `kosh` growth. That fragment covers Program A and almost nothing else a
real program does.

**The deeper objection.** Even if the proof existed, it would not replace the marker.
A boundedness proof concludes "this loop allocates at most T × per-pass bytes in
total". `~` promises "this loop holds at most one pass's worth at any time" — a bound
on *peak*, achieved by reuse. Total-boundedness does not imply a small peak, and it
does not reuse anything: a loop proved to allocate at most 900 MB still allocates 900
MB. The marker is a *mechanism* (reuse); the proof is a *verdict* (finite). The
no-marker version would also invert the failure mode: instead of a programmer marking
the loops they want reused, every unprovable loop with an allocation inside would have
to be refused — which, per the list above, is most loops — or the compiler would have
to silently accept unprovable loops, in which case the proof guarantees nothing and the
marker is still doing the work wherever it matters.

---

## Task 3 — and the honest reading of Program B's error

### The skip site

There is **one** lexer (`lex:`, `src/sutram_compiler.asm:6976`), called from three
places (the Linux entry, the Windows entry, and the main compile path —
`src/r68_compiler_entry.asm:9`, `src/r71_compiler_entry.asm:9`,
`src/sutram_compiler.asm:3163`), and **one** silent-skip site.
`src/sutram_compiler.asm:7418-7422`, at the end of `.try_operator` in `lex:`:

```nasm
    cmp r8, '^'
    je .emit_op
    cmp r8, '='
    je .check_eqeq_short
    cmp r8, '<'
    je .check_le
    cmp r8, '>'
    je .check_ge
    ; Unknown char — skip
    inc r13
    jmp .lex_loop
```

What it does: advances the source pointer **one byte** (`inc r13`) and loops. It emits
**no token**, records **no position** (the token-start pointer `r12` is set at the top
of `.lex_loop` but is simply overwritten on the next iteration), counts **no line**
(even if the skipped byte is a newline — but no newline can reach here, see below),
and leaves **no trace** in any diagnostic. The next iteration re-tests the following
byte from scratch.

This is the **only** silent-skip site in the lexer. A search for other "skip" paths in
`src/*.inc` and `src/*.asm` finds only the deliberate ones: whitespace (`.skip_ws`),
line comments and block comments (`.skip_comment`, `.bc_loop`), and the string
collector. The other files that touch tokens work on the token array *after* lexing
(`src/r71_unsafe_tokens.inc` validates the `asurakshit` boundary over tokens; it does
not lex) or on diagnostics (`src/r68_diagnostics.inc`,
`src/r68_unicode_helpers.inc` — the UTF-8 width helper, not used by the lexer). The
REPL (`-i` / khol) writes its input to a `.sm` file and compiles it through the same
`lex:` (`src/sutram_compiler.asm:802-811`).

### How the lexer decides, in order

For each byte at the top of `.lex_loop` (`src/sutram_compiler.asm:6991`), in order:

1. **End of input** → `TOK_EOF` (`.lex_eof`, `:7701`).
2. **`is_space`** (`:32883`) → `.skip_ws` (`:7693`): space `0x20`, tab `0x09`, LF
   `0x0A`, CR `0x0D`. `.skip_ws` increments the line counter **only** on LF. **Not**
   whitespace: vertical tab `0x0B` and form feed `0x0C` — both fall through to the
   skip.
3. **Comments** (`:7000-7043`): `//` line comment and `/* ... */` block comment, and
   `#` line comment (all skip to the next LF; the block comment also counts LFs). A `#`
   at token start is *always* a comment — there is no other meaning for `#` in the
   language.
4. **Danda** (`r66_is_danda_at`, `src/r66_indic_lexer.inc:62`): the complete 3-byte
   sequences `E0 A5 A4` (U+0964) and `E0 A5 A5` (U+0965) → `TOK_DELIMITER` with the
   semicolon value (`.emit_danda`, `:7668`). Needs 3 bytes remaining; a truncated danda
   is not a danda.
5. **Decimal digit** (`r66_decimal_digit_at`, `src/r66_indic_lexer.inc:15`): ASCII
   `0`–`9` (width 1), or an Indic digit — lead byte `0xE0`, second byte `A5`
   (Devanagari U+0966–096F), `AB` (Gujarati U+0AE6–0AEF), `A7` (Bengali U+09E6–09EF),
   `A9` (Gurmukhi U+0A66–0A6F), `AD` (Odia U+0B66–0B6F), `AF` (Tamil U+0BE6–0BEF),
   `B1` (Telugu U+0C66–0C6F), `B3` (Kannada U+0CE6–0CEF), third byte `A6`–`AF` —
   width 3. Otherwise → number parsing (`.try_number`, `:7201`); if not a digit at all,
   `.try_operator`.
6. **Identifier start** (`is_alpha`, `:32810`): `A`–`Z`, `a`–`z`, `_`, and the single
   byte `0xE0`. The identifier collector (`.collect_id`, `:7075`) then accepts further
   `is_alpha` / `is_digit` bytes, and any `0xE0` byte goes through `.store_multibyte`,
   which validates the whole 3-byte scalar with `r66_indic_scalar_width`
   (`src/r66_indic_lexer.inc:87`: `E0 A0..BF 80..BF`, which excludes overlong UTF-8)
   and copies all three bytes — or, if the scalar is invalid, jumps to
   `capacity_fail` with `r66_msg_bad_utf8` (`"Sutram truti [E_UTF8]: ashuddh ya
   khandit bharatiya naam"`). So a stray or truncated `0xE0` byte **errors**; it never
   reaches the skip.
7. **`.try_operator`** (`:7360`): `"` → string literal; two-char operators `==`,
   `!=`, `<=`, `>=`; delimiters `(` `)` `{` `}` `;` `,` `[` `]` `.` `:` `?`;
   single-char operators `+` (with `+=`, `++`), `-` (with `-=`, `--`), `*` (`*=`),
   `/` (`/=`; `//` and `/*` were already taken as comments), `%` (`%=`), `&`
   (`&&`), `|` (`||`), `^`; then three dead duplicate tests (`=`, `<`, `>` —
   unreachable, since those bytes were already tested above). **Everything else falls
   through to the skip.**

### The complete enumeration: 163 of 256 byte values

The other 93 are: 4 whitespace bytes, `#` and `/` (comment starts; `/` alone is an
operator), 10 ASCII digits, 53 identifier-start bytes (52 letters + `_`), 23 tested
operator/delimiter bytes, and `0xE0`. Count: 4 + 2 + 10 + 53 + 23 + 1 = 93; 256 − 93
= **163**.

**A. Printable ASCII (6):**

| Byte | Character | What a reader would expect | What happens |
|---|---|---|---|
| 0x24 | `$` | shell/PHP-style variable, or currency | skipped |
| 0x27 | `'` | character literal (C-style) | skipped — there are no char literals |
| 0x40 | `@` | annotation, decorator, or namespaced import | skipped — except in a `yoj` line, which the pre-lex import expander consumes textually (see below) |
| 0x5C | `\` | escape or line continuation (outside a string) | skipped — escapes exist only *inside* string literals |
| 0x60 | `` ` `` | template literal or inline code | skipped |
| 0x7E | `~` | bitwise NOT, "approximately", or the proposed region marker | skipped |

**B. DEL and control characters (30):**

- `0x7F` DEL.
- `0x00`–`0x08` (NUL, SOH, STX, ETX, EOT, ENQ, ACK, BEL, BS) — 9 bytes. Note `0x00`
  NUL: the lexer scans by length (`source_buf` + `source_len`), not by NUL
  termination, so a NUL byte inside a file is skipped like any other unknown byte.
- `0x0B` vertical tab, `0x0C` form feed — the two whitespace characters `is_space`
  does *not* recognise. A form feed is not a newline to this lexer: it neither counts
  as whitespace nor increments the line counter; it is simply dropped.
- `0x0E`–`0x1F` (SO, SI, DLE, DC1–DC4, NAK, SYN, ETB, CAN, EM, SUB, ESC, FS, GS, RS,
  US) — 18 bytes. Note `0x1B` ESC: an ANSI escape sequence pasted from a terminal
  (e.g. colour codes) loses its ESC byte and leaves the rest (`[32m` …) to be lexed
  as delimiters, numbers and identifiers (see §5 below).

**C. High bytes (127 of 128): every byte value 0x80–0xDF and 0xE1–0xFF.**

The skip advances **one byte**, so a multi-byte UTF-8 character is skipped byte by
byte (2 skips for a 2-byte character, 3 for a 3-byte one, 4 for a 4-byte one). The
character classes this covers, by lead byte:

| Lead bytes | Characters (UTF-8) | Examples |
|---|---|---|
| 0xC2–0xC3 | U+0080–U+00FF, Latin-1 Supplement | NBSP U+00A0 (`C2 A0`), © U+00A9, ®, °, é U+00E9 (`C3 A9`), ñ, ü |
| 0xC4–0xDF | U+0100–U+07FF, Latin Extended, Greek, Cyrillic, Armenian, Hebrew, Arabic | ā U+0101, α U+03B1, Ж U+0416, ש U+05E9, ع U+0639 |
| 0xE1 | U+1000–U+1FFF, Myanmar, Georgian, Hangul Jamo, Ethiopic, Cherokee, Latin Extended Additional | ṛ U+1E5B (`E1 B9 9B`), ṝ, ṃ, ḥ — the IAST diacritics used for transliterated Sanskrit |
| 0xE2 | U+2000–U+2FFF, General Punctuation, Currency, Arrows, Math Operators | — U+2014 em dash, “ ” U+201C/U+201D smart quotes, ‘ ’, • U+2022 bullet, … U+2026, € U+20AC, ← →, − U+2212 minus, ≠, ≤, ≥ |
| 0xE3–0xEF | U+3000–U+D7FF and U+E000–U+FFFF, CJK, Hangul syllables, private use | あ U+3042, 中 U+4E2D, 한 U+D55C — and the UTF-8 byte-order mark `EF BB BF` (see below) |
| 0xF0–0xF4 | U+10000–U+10FFFF, emoji and historic scripts | 😀 U+1F600 (`F0 9F 98 80`), 𝕏 U+1D54F are 4-byte |
| 0x80–0xBF | UTF-8 continuation bytes standing alone | a lone `0xA0` (the second byte of a NBSP after its `0xC2` was skipped), a truncated sequence |
| 0xFE, 0xFF | never valid in UTF-8 | a corrupted file's bytes |

**The one high byte that never reaches the skip is 0xE0.** At token start it is
always caught earlier: danda (`E0 A5 A4/A5`), Indic digit, or identifier start
(`is_alpha(0xE0)` is true), and the identifier path validates the scalar or errors
with `E_UTF8`. So the E0-led range U+0800–U+0FFF — Devanagari, Bengali, Gujarati,
Gurmukhi, Oriya, Tamil, Telugu, Kannada, Malayalam — is the only non-ASCII range the
lexer understands. Everything else in Unicode is skipped a byte at a time.

### Where the skipped characters cannot appear

- **Inside a string literal** (`"..."`): `.str_collect` (`:7459`) copies every byte
  verbatim except `"` (ends the string) and `\` (escape). A `~`, `$`, `@`, backtick,
  smart quote, or emoji inside a string is string content, never skipped.
- **Inside a comment** (`#`, `//`, `/* ... */`): the comment skip runs to the next LF
  (or, for a block comment, to `*/` or EOF) without lexing. Every `~` in the tree
  today is inside a `#` comment (examples/200, 208), as is every backtick.
- **In a `yoj` import line**: the pre-lex import expander (`:3624`, `.ei_loop`)
  copies comment lines verbatim and expands import lines textually before `lex:`
  ever runs, so the `@` in `yoj r33_alpha@first` never reaches the lexer. Every
  `@` in the tree today is in a `yoj` line. An `@` anywhere else in program text
  *does* reach the lexer and is skipped.

### `~` specifically, and the brief's Program B

**The path `~` takes.** `~` is `0x7E`. At token start it fails `is_space`, is not a
comment start, is not a danda (`r66_is_danda_at` needs `E0 A5 A4/A5`), is not a
decimal digit, fails `is_alpha`, and in `.try_operator` it matches none of the tested
bytes (`"` `=` `!` `<` `>` delimiters `+` `-` `*` `/` `%` `&` `|` `^`). It reaches
the skip at `:7420`: one byte advanced, no token, no position recorded, no error. The
lexer then lexes the next byte — the `{` — as a delimiter token.

**Tracing Program B through the parser.** Tokens after the `~` is skipped (line
numbers from the brief's Program B):

```
{  kosh  temp  [  1  ]  kosh_kship  (  temp  ,  i  )  total  =  ...
```

1. `chakra i = 1 tak 5 {` — the for-loop parser (`.ps_for`, `:15416`) parses the body
   with `parse_body` (`:8134`), which sees `{` and calls `parse_block` (`:14788`).
2. `parse_block` loops: the current token is `{` (not `}`), so it calls `parse_stmt`.
3. `parse_stmt` (`r45_parse_stmt_body`, `:14836`) dispatches on keywords; `{` is a
   delimiter, not a keyword, so it falls to `.ps_check_expr` (`:16026`), which calls
   `parse_expr`.
4. `parse_expr` → `parse_ternary` → `parse_lor` → `parse_land` → `parse_bitor` → …
   → `parse_primary` → `parse_primary_inner` (`:17075`) with the current token `{`.
   The primary parser handles only `(`/`[` delimiters (parenthesised expression,
   vector literal), strings, numbers, identifiers, builtins, and the keywords
   `prasar`/`purna`/`shunya`. **`{` matches none of them.**
5. The fall-through at `.pp_builtin` (`:17707`):

```nasm
.pp_builtin:
    cmp rcx, TOK_BUILTIN
    je .pp_builtin_valid
    ; Check mode must reject stray ';', ']', ',' and other tokens here.
    ; The legacy fallback treated every unsupported primary as '(' and
    ; accidentally consumed tokens in later malformed declarations.
    ; Preserve historical non-check compilation behavior unchanged.
    cmp qword [rel r48_mode], 0
    jne parse_error
    jmp .pp_paren
```

   In normal (non-check) mode the parser treats the unsupported primary **as if it
   were `(`**: `.pp_paren` (`:17235`) consumes the `{` with `advance_tok` and calls
   `parse_expr` for the "inner" expression.
6. The inner `parse_expr` starts at `kosh` (TOK_KEYWORD, KW_KOSH). It is not
   `prasar`/`purna`/`shunya`, so it falls through the same chain and reaches
   `.pp_builtin` again — and again the legacy fallback treats it as `(`: it
   consumes `kosh` and calls `parse_expr` for `temp[1]`.
7. `temp[1]` parses cleanly as an index expression (`.pp_ident_index`). Back in the
   inner `.pp_paren`, the parser checks for the closing `)`: the current token is
   `kosh_kship` — not `)` — so it jumps to `parse_error`.
8. `parse_error` (`:13407`) prints the **current** token: `"Sutram truti: vyakaran
   dosh, pankti "` + line:col (via `r51_origin_line_col`) + `", shabd '"` + the
   token's text + `'`. The current token is `kosh_kship`, on line 6, column 13
   (twelve spaces of indentation, then the name). That is exactly the error the
   brief measured:

```
Sutram truti: vyakaran dosh, pankti 6:13, shabd 'kosh_kship'
```

**What the brief gets right, and what it gets wrong.** **Right:** the error lands on
`kosh_kship`, three lines after the `~`, and a student would blame `kosh_kship`. The
trace above reproduces the measured error exactly, token for token. **Wrong:** "the `{`
becomes an unnamed block". **There is no unnamed-block statement in the parser.** No
code path treats a bare `{` as a block statement — `parse_block` only ever runs after
a `{` that a *construct* consumed (a function body, a loop/if body via `parse_body`,
`mandapa`, `guna`), and `parse_stmt` has no `{` case. What the `{` becomes is a **fake
open parenthesis**, consumed by the legacy fallback — and `kosh` is consumed the same
way a moment later. The parse does change underneath, but by token-eating, not by
block formation.

**A second correction the brief does not mention: the error's location depends on the
mode.** In `--check` mode (`r48_mode` set at `:3054` and `:3099`), the same
`.pp_builtin` fall-through goes to `parse_error` immediately instead of `.pp_paren`
— so the same Program B fails at the `{` itself (line 4), not at `kosh_kship`. The
student running `--check` and the student running the plain compiler get different
error locations for the same program, from the same code. (Derived by reading; the
normal-mode location is the brief's own measurement, reproduced above token for token.
The check-mode location needs a run to confirm — see "could not determine".)

### What the compiler must do when it sees a `~` it does not support

**Answer: refuse at the marker with a clear message. No version check.**

**A version check is not the mechanism, and it cannot be one as the compiler
stands.** There is no version-gating machinery in the compiler at all:

- No feature is gated on the compiler version anywhere in `src/` or `win/`. The
  version string (`msg_version`, `:260`: `"Sutram 1.0 (v315) - sampurna sutra"`) is
  only *printed* by `--version`; nothing compares against it.
- There is no source-level version declaration and no "requires version" directive
  in the language. A version check would need inventing the directive, the
  comparison, and the message — a whole mechanism for one character.
- The nearest thing to a conditional is `r82_on` (`:1713`), and it is a **per-program
  flag**, not a version check: the program's own content (a kosh declared inside a
  mandapa) changes code generation for that program. It does not compare versions.
- The failure mode is not "this source needs a newer compiler" — it is "this
  character means nothing in the language". A version check would imply `~` will
  mean something in a later version. If it later does (the proposed region marker),
  the refusal *becomes* the feature: the same site gains a token instead of an error.

**Refusal at the marker is what the compiler already does for unsupported input:**

- **Withdrawn names** (`r115`, `:7645`): a name the compiler no longer supports is
  refused at the token's position with a named error code and a hint telling the
  reader what to use instead — header `": Sutram truti [E_PRATYAHRITA]: "`,
  text `"sankhya_bindu (sankhya_dot) pratyahrita - asyah phalam ashuddham,
  sanshodhanam pratiksate"`, hint `"Sanket: dvayoh kosh dasham bindu-gunanaya:
  yoj sankhyiki, bindu_gunan(a, b) - laghutara dirghata eva pathyate"` — via
  `r80_compile_error` with `rdi` = the token's source pointer (`r12`).
- **Bad UTF-8** (`r66_msg_bad_utf8`, `src/r66_indic_lexer.inc:11`): the one existing
  lexer error, `"Sutram truti [E_UTF8]: ashuddh ya khandit bharatiya naam"`. It is
  the precedent for the lexer refusing input — but it is printed via `capacity_fail`
  (`:7731`), which prints only the string and exits: **it carries no line or column**.
  A `~` refusal should not copy that weakness; it should use `r80_compile_error`,
  which does carry a position.
- **The `!` precedent** (`.check_neq`, `:7600`): `"R17 D1: unary not, was silently
  skipped"`. The project has already fixed a silently-skipped character once — by
  giving it a token. Here the fix runs the other way (give it an error), but the
  principle is the same: no silent skip.

**What the fix looks like, in the lexer's own terms (described, not written).**

- **Site:** the fall-through at `src/sutram_compiler.asm:7420` — the `"; Unknown char
  — skip"` lines. Replace `inc r13; jmp .lex_loop` with a refusal. Nothing else in
  the lexer needs to change: by construction, anything reaching that site has already
  failed every legitimate test (whitespace, comment, danda, digit, identifier,
  string, operator, delimiter), so the refusal cannot fire on valid input.
- **Position:** `r12` holds the token-start source pointer (set at the top of
  `.lex_loop`, `:6993`: `mov r12, r13`), and `r8` holds the byte (`movzx r8, byte
  [r13]` at `:7354`). Pass `r12` as `rdi` to `r80_compile_error` (`:11700`), which
  prints the origin (file, line, column via `r51_print_origin`, `:13535`) plus a
  source-context snippet (`r51_print_original_context`, `:13709`), then the header,
  text and hint, and exits 1. The machinery already exists; the skip site already
  has everything it needs in registers.
- **Message form:** follow the existing conventions. Header in the `r115_hdr` form
  (`": Sutram truti [E_<CODE>]: "`), Sanskrit text naming the character, and a
  `"Sanket: ..."` hint. A **new error code is needed**: no existing unknown-character
  code exists (`E_UTF8` is the only lexer error, and it is about malformed bytes, not
  unrecognised characters). The text should name the character that was refused — the
  student needs to see `~` in the message, not "unknown character" in the abstract.
- **One design decision the fix must make: report the first byte, or the whole
  character?** As written the skip is per-byte, so a multi-byte character (say, an em
  dash) would be reported at its first byte. To name the whole character, the fix
  should advance past the full UTF-8 scalar before reporting — `r68_utf8_width`
  (`src/r68_unicode_helpers.inc:5`) already computes a scalar's width (1–4, or 0
  invalid) for exactly this purpose and is available to compiler-host code. For an
  invalid byte (0xFE, 0xFF, a lone continuation byte), width 0 means "report this
  byte alone".
- **One carve-out the fix must include: the byte-order mark.** A UTF-8 BOM (`EF BB
  BF`) at the start of a file currently reaches the skip site three times (0xEF, then
  0xBB, then 0xBF) and is silently dropped — which is the correct behaviour for a
  BOM, arrived at by accident. Refusing every unknown byte would newly reject every
  BOM-marked file. The loader should strip one leading BOM (or the lexer should skip
  exactly one leading BOM) instead of refusing it. There is no BOM handling anywhere
  in the tree today (no `0xEF`/`0xBB`/`0xBF` check in the source-loading or lexer
  code); the fix has to add it, or every editor that writes a BOM breaks.
- **What must be re-verified before the fix lands (execution, not reading):** the
  suite and the library must be run with the refusal in place, because any file that
  currently *relies* on the skip would newly fail. What reading can say: every `~`
  in the tree today is inside a `#` comment, every backtick is inside a `#` comment,
  and every `@` is in a `yoj` line consumed by the pre-lex expander — so none of the
  known occurrences reaches the skip site. What reading cannot say: whether any file
  in the tree contains a skipped byte in *code* position that a grep cannot see (a
  control byte, a stray high byte inside an identifier, a NBSP between two tokens).
  A run of the suite with the refusal in place is the check.

### One confusing failure per skipped character (or class)

Each of these is a plausible student program. "Surfaces at" is where the first error
would appear, traced through the parser; the skipped character itself is never named.

- **`~` — the brief's Program B.** `~ {` inside a loop: the `~` vanishes, the `{` and
  `kosh` are eaten as fake parentheses, the error lands on `kosh_kship` three lines
  later. Also: `vitti x = a ~ b` (a C reader expecting bitwise NOT, or "approximately"):
  the `~` vanishes, leaving `a b` — two adjacent identifiers — and the error lands on
  `b`.
- **`$` — silently accepted, the worst case.** `$total = 0`: the `$` vanishes and the
  statement compiles as `total = 0` — the program runs, with no error at all, and the
  student never learns the `$` did nothing. A `$` before a name is not even an error.
  (`$5` as a literal: the `$` vanishes and `5` is the value.)
- **`'` — a char literal from C.** `vitti x = 'a'`: both quotes vanish, leaving
  `vitti x = a` — a read of the undeclared name `a`. The error names `a`, not the
  quotes. A student who has written C will stare at `a` for a long time.
- **`@` — an annotation from another language.** `@pure` above a `prakriya` definition:
  the `@` vanishes, `pure` becomes a bare expression statement, and the error lands
  on whatever follows it (the `prakriya` keyword, or the first token the expression
  parser cannot continue with). The only legitimate `@` in the language is in a
  `yoj` line, which never reaches the lexer.
- **`\` — a line continuation, or an escape outside a string.** `vitti x = 1 + \<newline> 2`:
  the `\` vanishes and the expression continues on the next line — this one happens
  to work. The confusing one is `\n` written outside a string expecting a newline:
  the `\` vanishes and `n` becomes an identifier, so the error lands on `n`.
- **`` ` `` — a template literal or Markdown inline code.** ``vitti x = `5` ``: the
  backticks vanish, leaving `vitti x = 5` — silently accepted, the backticks did
  nothing. (Inside a comment, backticks are harmless; in code, they are invisible.)
- **NBSP (U+00A0, `C2 A0`) — pasted from a web page.** `vitti␣total = 0` (NBSP between
  the type and the name): both bytes are skipped, so the NBSP acts as an invisible
  separator and the program *works* — until the student pastes `to␣tal = 5`, where
  the NBSP splits one name into two identifiers and the error lands on `tal`. The
  same invisible character sometimes helps and sometimes breaks, with no visible
  difference in the editor.
- **Smart quotes (U+201C/U+201D, `E2 80 9C/9D`) — pasted from a word processor.**
  `likha(“pass”)`: the curly quotes vanish (three skips each), leaving
  `likha(pass)` — a read of the undeclared name `pass`. The error names `pass`;
  the student sees matching quotes in their editor and cannot see the problem.
  The same applies to the em dash (`—`), which a student might use as a minus:
  `vitti x = 10 — 3` becomes `vitti x = 10 3` — the error lands on `3`.
- **IAST diacritics (U+1E00+, lead `0xE1`) — transliterated Sanskrit.** `vitti ṛṣi = 5`:
  the IAST letters are skipped byte by byte (three skips each), so the name vanishes
  entirely and the error lands on `=` — the parser expected a name after `vitti` and
  found `=`. The Devanagari spelling of the same name would lex fine (0xE0); the
  transliteration silently deletes it.
- **Emoji / symbols (lead `0xF0`, or `0xE2`) — a checkmark or bullet pasted from notes.**
  `• item` at the start of a line: the bullet vanishes (three skips) and `item`
  becomes a bare expression statement; the error lands on whatever follows `item`.
  An emoji after code, e.g. `likha("done") ✅`, vanishes the same way.
- **Control bytes — an ANSI escape pasted from a terminal.** Output containing colour
  codes, e.g. `ESC [32m vitti x = 5`: the ESC byte (`0x1B`) is skipped, `[` opens a
  vector literal, `32` is a number, `m` is an identifier — the error lands far from
  the escape, inside what the student thought was plain text. A NUL byte (`0x00`)
  from a binary paste is skipped with no trace at all.
- **VT / FF (`0x0B`/`0x0C`) — a form feed from a paginated printout.** A `0x0C`
  between two statements is dropped silently; the program behaves as if the page
  break were not there. Harmless in effect, invisible in mechanism — and the only
  two whitespace characters the lexer's own `is_space` does not recognise.

### Other silent treatments: whitespace, comments, strings, BOM

These are not the skip site, but a student would not expect them either:

- **`#` is a line comment, always.** There is no other meaning for `#` in the
  language (the compiler's own hidden names `#g<n>` are generated, never written).
  A student writing `#include <stdio.h>` (C habit) gets the whole line dropped
  silently — no error, no include, no hint.
- **An unterminated block comment swallows the rest of the file.** `.bc_loop`
  (`:7014`) runs to `.lex_eof` if no `*/` appears — there is no
  unterminated-comment error. A forgotten `*/` deletes every statement after it,
  silently, and the program compiles as if those statements did not exist.
- **An unterminated string swallows the rest of the file.** `.str_collect`
  (`:7459`) runs to `.str_done` at EOF with no error — there is no
  unterminated-string error. The rest of the file becomes string content.
- **Newlines inside a string do not count as lines.** `.str_collect` copies LF
  bytes into the string pool without touching `cur_line`, so every error reported
  *after* a multi-line string literal is on the wrong line — off by the number of
  newlines inside string literals so far. (A CR inside a string is likewise copied
  verbatim into the string pool; it is content, not a line ending.)
- **The byte-order mark is skipped silently.** `EF BB BF` at the start of a file
  reaches the skip site three times (0xEF, 0xBB, 0xBF) and is dropped with no token
  and no error. The behaviour is correct; the mechanism is accidental — see the
  BOM carve-out above.
- **CR is whitespace; LF is the only line counter.** `.skip_ws` increments `cur_line`
  only on LF (`:7693`). A file with lone CR line endings (classic Mac) would lex
  (CR is whitespace) but report every error on line 1.
- **The danda is a semicolon, silently.** `r66_is_danda_at` emits `TOK_DELIMITER`
  with the semicolon value — the brief notes this is why `।` was not chosen for the
  region marker. A student writing a danda where a statement separator is not
  wanted gets a separator anyway, with no diagnostic.

---

## Brief corrections

1. **Program B's mechanism.** The error does land on `kosh_kship`, line 6:13, exactly
   as measured — but not because the `{` "becomes an unnamed block". There is no
   unnamed-block statement in the parser. The `{` and then `kosh` are consumed as fake
   open parentheses by the legacy `.pp_builtin` fallback (`:17707`), which treats
   every unsupported primary as `(` in normal mode.
2. **The error's location depends on the mode.** In `--check` mode the same program
   fails at the `{` itself (line 4), because the fallback is disabled there
   (`r48_mode` check). The brief states one location; there are two, by mode. The
   check-mode location is derived by reading and needs a run to confirm.

## Could not determine from source

- Whether Program B in `--check` mode actually fails at the `{` on line 4: the code
  path is clear (the `.pp_builtin` fall-through checks `r48_mode` and goes to
  `parse_error` instead of `.pp_paren`), but the exact reported line and column need
  a run to confirm. The normal-mode error is the brief's own measurement, reproduced
  here token for token through the code.
- Whether any file in the tree contains a skipped byte in *code* position that a grep
  cannot see (a control byte, a stray high byte inside an identifier, a NBSP between
  two tokens): the known `~`, backtick and `@` occurrences were checked and are all
  in comments or `yoj` lines, but a byte-level scan of every file's code positions was
  not done. A run of the suite with the refusal in place is the check.
- Whether the `~` refusal would change any golden test's expected output: the goldens
  were not re-run (read-only task); none of the checked-in programs uses a skipped
  character in code position, so none should change, but that is a reading, not a run.
- Whether the parser's legacy `.pp_paren` fallback is load-bearing for any valid
  program: the comment says it is preserved for historical non-check behaviour, but
  no valid program should reach it (it only fires on an unsupported primary). Which
  valid programs, if any, depend on it could not be determined by reading.
- The exact column the `~` refusal would report: it would be the `~`'s column via
  `r51_origin_line_col`, but the column computation for a byte inside a multi-byte
  sequence (or after a string containing newlines) was not traced to a number.
- Whether the Windows entry point (`r71_compiler_entry.asm`) pre-processes the source
  before `lex:` in any way that changes which bytes reach the skip (e.g. a BOM strip
  or a CR normalisation on that path): the entry calls the same `lex:`, but its
  pre-lex code was not read line by line.
- Whether the statement-call bypass of `r108_check_call` (Task 1, case 3) is a live
  escape at runtime — it is established by reading that the check is not called on
  that path; whether a keeping callee actually receives and stores the kosh needs
  execution, which this round forbids.
- Whether a top-level `~` in `mukhya` would change emitted bytes — needs a build and
  a byte diff, forbidden here.
- The runtime effect of the FFI slice route (F8) — same limitation as R148's
  fifteenth shape. (The slice refusal itself is established by reading the R152 door.)
- What `parimana()` reports for a grown kosh after its block ends — the
  region-counting code in `r101a_emit_kosh_alloc` is unreachable behind its opening
  jump, and the arena-cursor accounting was not traced end to end; needs a run.
- Whether `r82_param_checks`' fallback-walk path at `:18714` covers every synthesized
  call it emits — the call site was re-verified, the coverage was not traced
  exhaustively.
- Which reuse implementation the owner intends (one static buffer per site vs.
  mark/rewind on a bump pool) — it is not in the brief, and cases 1, 6, F2, and F4
  turn on it.
- Whether the owner intends `~`'s reuse to reset the `kosh` length (and whether
  elements are zeroed): the brief states reuse but no reset rule, and the answer to
  Program B (15 vs 5) turns on it. Not determinable from the brief; no `~` exists in
  the tree to read.
- Whether `mandapa`'s scratch rewind and `parimita` budget are checked on Windows PE
  at v315: the R103 header comment says PE is inert and unchecked, but `r65_active`
  (`src/r65_arena.inc:120`) returns 1 on PE, and the reference says Windows has the
  block from v299. One of the two is stale; reading alone does not say which.
  (Peripheral to this task, but it affects any claim that `~` would need a PE story
  `mandapa` lacks.)
- How much the reuse in Q1 is actually worth on a real program: no measurement was
  run (read-only round), and the reference's own figures (100,000 passes making a
  `kosh` of 100 numbers: 106,240 KB on v315, reference §19) are for `mandapa`
  *without* reclaim, not for reuse. The claim is about allocation work and transient
  peak, not about values, and its size is unmeasured here.
- Whether a boundedness proof over the narrow literal fragment (Q4) would be accepted
  as useful by the owner: that is a judgement about false positives, not a fact in
  the tree.
- Whether any `~` in the tree's own test programs or gates already exists — no `~`
  handling exists in the lexer or parser at this base, so there is nothing to check
  against; the four programs are the only specification.
