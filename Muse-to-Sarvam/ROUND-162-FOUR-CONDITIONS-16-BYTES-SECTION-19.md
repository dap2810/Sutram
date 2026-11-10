# ROUND-162 — the four conditions, attacked; the 16 bytes; the §19 paragraph

**Base:** main at `79e65f90` (compiler v315). **Read only. Nothing compiled or run.**
**Deliver into:** `Muse-to-Sarvam/`

**Verdicts up front**

1. **Task 1 — HOLE. The four conditions are not closed.** A block `kosh` grown past
   4,097 elements, passed by its own name to a foreign function taking a `ptr`
   parameter, **as a bare statement**, satisfies all four WS3 conditions, sets no
   flag, and hands C the elements address of a region the block exit then releases.
   The root cause is that the WS3 flag rules cover assignments, returns, and stores —
   and never mention calls at all — and the one check that covers calls,
   `r108_check_call`, never runs on the statement path. A chain of statement calls
   ending at the FFI door is the same hole with one more link. A third hole is
   conditional on the implementation: WS3 never says where the check looks, so a
   block-local implementation misses an outward assignment inside a nested `yadi`
   and reclaims a live `kosh`. And condition 4 as written is vacuous: read
   literally it disqualifies every grown `kosh`, since growth *is* `kosh_kship`.
2. **Task 2 — the 16 bytes, re-verified: every R161 line number and every arithmetic
   claim checks out at this tip, no corrections.** They are 24 bytes of R82 header
   (line, liveness slot, generation) minus 8 bytes of alignment padding. The brief's
   conditional is answered: the header is **used** bookkeeping — all three words are
   read by the runtime liveness check in every `prakriya` prologue — so there is no
   "allocated and never used" defect. The honest qualification: the flag is
   program-wide, so `kosh`es that never enter a block also pay the 24 raw bytes; the
   line for that overbreadth is the flag itself, `r82_on resq 1` (`:1713`).
3. **Task 3 — the §19 paragraph, written as the actual words** (§5 below), with its
   anchor, the other sentences that will also need a matching change, and twelve
   ambiguities in ROUND-171's wording with the choice made for each. One correction
   to the brief's framing: the §19 sentence becomes false for the `kosh`es that
   **qualify**, not the ones that **escape** — escaping `kosh`es behave exactly as
   today.

---

## Task 1 — the four conditions, attacked

The design under attack is `Sarvam-to-Claude/ROUND-171.md`. A `kosh` satisfying all
four conditions, inside a `mandapa`, has its separately mapped buffer (the region
above 4,097 elements) released when the block exits; the descriptor stays, small
allocations stay. The four conditions: (1) declared inside the block; (2) never
assigned to a variable declared outside the block; (3) never returned by
`nivartanam` from the enclosing `prakriya`; (4) never passed to `kosh_kship` or
stored in any other collection. The check (WS3) is a `decl_depth` comparison plus a
flag per `kosh` symbol: assigned outward is `lhs.decl_depth < rhs.decl_depth` at any
assignment; returned is a `nivartanam` whose expression is the symbol; stored is
the symbol appearing as an argument to `kosh_kship` or as the right side of a `kosh`
element write. "If a `kosh` is used in a way you cannot classify, do not reclaim it.
A missed reclaim is a leak; a wrong reclaim is a crash. Fail toward leaking."

### The strongest program — FFI, as a statement (§1)

Foreign declaration (the standard `.sffi` mechanism, `tests/r32/ffi.sffi` form;
`c_keep` stores its argument in a C static; `c_read` returns the first element at
the stored pointer):

```
c_keep|1|ptr|void|c_keep
c_read|0||i64|c_read
```

```sm
mukhya() {
    mandapa {
        kosh k[5000]
        chakra i = 0 tak 5000 {
            kosh_kship(k, i)
        }
        c_keep(k)
    }
    vitti x = c_read()
    likha(x)
}
```

`c_keep(k)` is a bare statement. `k` is grown past 4,097 elements inside the block,
so it has a separately mapped region. `c_read()` after the block reads through the
pointer C kept.

**What the four-condition check sees: no flag.** Condition 1: `k` is declared
inside the block — satisfied. Condition 2: no assignment of `k` to any variable; a
parameter binding is not an `AST_ASSIGN` node, and no WS3 rule mentions a call.
Condition 3: no `nivartanam` mentions `k`. Condition 4: `k` appears as the first
argument of `kosh_kship` only as the target being grown (see the spec defect below),
never as a value, never on the right side of a `kosh` element write.

What the existing checks see is the same nothing, on this path. Two load-bearing
facts, both verified at this base:

- **`r108_check_call` has exactly one call site** (`src/sutram_compiler.asm:21556`),
  inside `.ge_funcall` — the *expression* form of a call. The statement form,
  `.gs_funcall` (`:19028`, dispatched from `gen_stmt` at `:18978-18979`), calls only
  `r129_check_call` and `r25_check_call`. It never calls `r108_check_call`. The
  comment in `.gs_funcall` claims "Use the same typed helper as expression calls so
  statement calls cannot bypass dasham/kosh conversion or checks" — true for the
  typed-argument helper (`gen_typed_call_arg`, which both paths share), false for the
  keeping check. The keeping fixpoint (`r108_compute_esc`, `:12811`, to convergence
  — the R109 fix for the v290 32-round cap) is computed and never consulted on the
  statement path.
- **The FFI door affirmatively permits it** (`src/r32_ffi.inc:688-699`): "A kosh by
  its own name still does (as its elements, for ptr; refused below for i64 and f64)."
  A slice of a `kosh`, a call or `?:` giving one, or a name holding a slice is
  refused via `r134_holds_kosh` (`:699`) — but a `kosh` by its own name goes to
  `.r152_open`, and for a `ptr` parameter the `.ptr` branch (`:736-755`) emits
  `mov rax,[rax]` (`:751-755`, "R127: a kosh passes its elements, not its
  descriptor") and hands C the **elements address**. The door checks the parameter
  kind, not whether the `kosh` is a block `kosh`. A second asymmetry: `rfx3_fn_index`
  (`:9923`) searches `func_defs` only, and foreign functions live in a separate
  table (`r32_ffi_count`, `src/r32_ffi.inc:45`; they are never added to
  `func_defs`), so on the expression path a block `kosh` passed to a foreign function
  is refused by `r108_check_call` (unknown callee → `.bad`). The reference claims
  (`docs/LANGUAGE-REFERENCE.md:1373-1375`): "a function value or a foreign function
  counts as keeping" — true on the expression path, false on the statement path.

**Runtime after the block exits:** at block exit ROUND-171 releases the region
(`munmap` of `[d]`, size `[d+8]`). C still holds the elements address in its static.
`c_read()` then reads through it. If the address is still unmapped: a segfault in C.
If it has since been reused by a later `mmap` — another `kosh`'s region, another
allocation: C reads stale or wrong data silently. Either way it is a use-after-free
of the released region, through a pointer the program obtained entirely inside the
rules. Note the asymmetry: `vitti x = c_keep(k)` would be refused by
`r108_check_call` (unknown callee). The same call as a statement compiles. The only
difference is whether the call's value is used.

**Verdict: HOLE.** This is the strongest program: it needs no exotic construct, no
chain, no aliasing trick — one permitted call, one permitted door.

### The chain — a `prakriya` called from inside the block that keeps the address (§2)

```sm
prakriya store(kosh k) {
    c_keep(k)
}
mukhya() {
    mandapa {
        kosh k[5000]
        chakra i = 0 tak 5000 {
            kosh_kship(k, i)
        }
        store(k)
    }
}
```

No flag: a call is not an assignment, return, or store, as in §1. The callee cannot
keep the address by any Sutram-only means — the `r126` doors refuse every store and
the return is discarded by the statement call (`g = k` refused by
`r126_check_assign`'s `.var` branch via `r134_holds_kosh`; `p.field = k` and
`m[i] = k` refused by the `.cell` branch; `kosh_kship(other, k)` refused by
`r126_check_builtin`; `nivartanam k` refused by `r126_check_return`) — but the
chain is unbroken because **no link in it is ever checked**: each statement call
passes a `kosh` to a `kosh` parameter, which the typed-argument helper accepts
without any keeping check, and the only keeping route open to the callee is the FFI
door (§1), reached one hop later. **Verdict: HOLE**, in its FFI-terminated form.
The defect is the missing `r108_check_call` on the statement path; the FFI door is
the terminal link. Fixing either one closes this hole; fixing neither leaves it open.

### The branch — safe in one direction, underspecified in the other (§7)

```sm
vitti outer = 0
mukhya() {
    mandapa {
        kosh k[5000]
        chakra i = 0 tak 5000 {
            kosh_kship(k, i)
        }
        yadi (0) {
            outer = k
        }
    }
}
```

The flag **is** set: the WS3 check is static — it walks the source, not the runtime
— so `outer = k` inside a branch that never runs still sets the assigned-outward
flag, and `k` is not reclaimed. The existing taint check has exactly this property
(`r73_fix` / `r73_check_stmt`: "never clears a taint — it may sit in a `yadi`/loop
branch that does not run"). A missed reclaim is a leak, not a crash, and the
design's "fail toward leaking" covers it explicitly. **CLOSED in the leak
direction.**

The other direction is the one that matters. WS3 says the flag is set "at **any**
assignment", but never says **where the check looks**. If the check walks the whole
enclosing function (as "any" implies), a use inside a nested `yadi`/`chakra` inside
the block is seen and the flag is set — closed. If the check scans only the block's
direct statements — the natural misreading, since the flag is per block-`kosh` and
the release is at block close — then `outer = k` inside a `yadi (1)` is invisible
to the scan, the flag stays clear, the region is released at block exit, and `outer`
still holds the descriptor of the freed region. Use-after-free. **Verdict:
HOLE-IF.** The four conditions as **worded** close the branch case; as **specified**
they do not, because the walk scope is unstated. WS3 must say the check walks the
whole enclosing `prakriya` — statements, nested blocks, branches, and loops — or the
first implementation will get this wrong.

### Spec defect — condition 4 as written is vacuous (§A)

WS3 condition 4 / "stored": "the symbol appearing as an argument to `kosh_kship`".
Read literally, that includes the **first** argument (the target `kosh`). But a
`kosh` only acquires a separately mapped buffer by being grown past 4,097 elements,
and the only way to grow it is `kosh_kship(k, v)` — with `k` as the first argument.
Under the literal reading every reclaimable `kosh` is disqualified by the very
growth that makes it reclaimable, and the design reclaims nothing, ever. The only
coherent reading is the **value** argument: the symbol pushed as an element into
another collection. Every program above is judged under that reading, and the finding
is recorded as a spec defect: WS3 must say "as the value argument of `kosh_kship`",
or the implementation will either reclaim nothing or reclaim a `kosh` it was told
not to, depending on which reading the implementer picks.

### The closed cases — and who closes them

The attack covered fourteen candidate holes. Everything else is closed, but the
closures are unevenly owned, and the attribution matters: **the four conditions
contribute almost nothing to most of these closures.** A future refactor that leans
on the WS3 flag instead of the doors would silently open them.

- **A slice** (`vitti s = k[0:5]` inside the block, then `s` used after it) —
  **CLOSED, by three cooperating pre-existing checks, not by the four conditions.**
  No flag fires in any variant (a slice creation is none of the four conditions —
  the slice is a name the four conditions do not cover). But: an outer name with a
  bare slice is refused by `r127_check_slice_value` (`:28878`, via
  `r126_check_decl` `:29197` and `r126_check_assign`'s `.local` branch `:29265` —
  note: two call sites, not both inside `r126_check_decl` as an earlier summary
  said); an inner name is out of scope after the block; a ternary-wrapped slice is
  refused by `r126_bind` (kind 6) and the walk's `.num` door (`:28639`, ternary-aware);
  a slice may go only to a `vibhag` parameter, cannot be stored (`r134_holds_kosh`),
  cannot be returned (`r23_check_return`, `src/r23_capabilities.inc:510`), cannot go
  to C (FFI door `:699`). One reading-level blind spot, which does **not** reach past
  the block: `r127_check_slice_value` checks only a bare `AST_SLICE` with a `kosh`
  base, so `vitti t = p[0:3]` through a `vibhag` parameter is not refused — but `t`
  cannot escape the callee, so it doesn't reach past block exit.
- **A `kosh` passed to a `prakriya` that stores it in a module-level variable** —
  **CLOSED by `r126_check_assign`, not by the four conditions.** The WS3 flag would
  not fire — the assignment is to the parameter symbol in another function. What
  saves it is `r126_check_assign` (`.gs_assign`, `:19494`) running on the assignment
  inside `store`; its `.var` branch calls `r134_holds_kosh` and refuses a `kosh`
  into a module variable.
- **A `kosh` stored into a `rachana` field** (`p.v = k`) — **CLOSED by `r126`, not by
  the four conditions.** A field store is not one of the four conditions (WS3's
  "stored" covers `kosh_kship` and "the right side of a `kosh` element write"; a
  `rachana` field is neither). `r126_check_assign`'s `.cell` branch covers
  `AST_INDEX` **and** `AST_FIELD` (`:29223-29240`) and refuses via `r134_holds_kosh`.
- **A `kosh` returned through a `phal`/`siddhi` result** (`nivartanam siddhi(k)`) —
  **CLOSED.** The flag is set (WS3's returned rule, `siddhi(k)` wraps the symbol),
  and the existing doors agree: `r126_check_return` (`:29377`) takes the phal branch
  and calls `r134_holds_kosh` on the value. This is the one return shape where the
  four conditions and the existing checks say the same thing.
- **A function value** (`f(k)` where `f` holds `store`) — **CLOSED, on both paths.**
  `r126_check_untyped_arg` (`:29343`) is called from `gen_typed_call_arg` (`:27333`,
  the scalar-argument path, shared by statement and expression calls) and refuses a
  `kosh` through a function value via `r134_holds_kosh`. The function value is safe
  precisely because it has no declared parameter kind to route around the check — the
  contrast with §2, where a **named** `prakriya` with a `kosh` parameter takes the
  `.gtca_kosh` path, which calls no `r126` check and no `r108` check on the statement
  path.
- **Recursion** (the same `kosh` symbol at two depths) — **CLOSED, with an
  implementation requirement.** Each activation has its own frame, its own descriptor
  slot, its own region; the release reads the **current frame's** descriptor
  (`[d]`/`[d+8]`), so the inner activation's exit releases the inner region and the
  outer's releases the outer's. If the implementation instead cached the region
  pointer in a per-symbol global (or in the `r108_bk_*` record, which is compile-time
  state), the inner activation would overwrite the outer's pointer. The four
  conditions say nothing about this; the requirement belongs in WS3 alongside the
  flag rules. The cross-activation hole is §1, not recursion itself.
- **A `kosh` grown by a callee** — **CLOSED.** Growing is not an assignment, return,
  or store — and correctly so. The growth path maintains exactly one live backing
  store (`src/r65_arena.inc:579`, `r127_emit_grow`): if the new size fits the existing
  region it grows in place; otherwise it allocates a new backing store, copies the
  elements, **releases the old region itself** (`munmap` of the old `[d]` with the old
  `[d+8]`, `:711-713`), and only then updates the descriptor. A `kosh` parameter
  passes the descriptor **pointer**, so the callee's growth writes through to the
  caller's descriptor, and the block-exit release reads the current `[d]`/`[d+8]`.
- **A `kosh` element written through a slice** — **CLOSED.** Writing a **number**
  through a slice (`s[0] = 99`) writes a value, not an address. Writing the `kosh`
  through a slice (`s[0] = k`) is refused by `r126_check_assign`'s `.cell` branch via
  `r134_holds_kosh`. (The program as first written does not compile anyway:
  `vitti s = k[0:5]` is itself refused by `r127_check_slice_value`.)
- **The descriptor's `[d]` word read as a plain value** — **CLOSED in Sutram, HOLE
  via FFI.** No Sutram operation yields the descriptor address or the elements
  address as a number (a `kosh` used as a number is refused by the walk `.num`,
  `:28639`; there is no address-of operator; `vitti a = k` binds `a` as a `kosh`
  name, not a number; `likha(k)` prints the address — the R100 trap #5, still live —
  but does not hand the number to the program). The FFI door hands C the elements
  address without ever touching the descriptor — §1 again.
- **A `nirmmita` pointer that aliases the `kosh`'s buffer** — **CLOSED in Sutram,
  HOLE via FFI.** No Sutram-only path lets a plain pointer hold the region's address.
  The FFI route is the exception: C receives the elements address as a `ptr`
  argument and can keep it itself, or write it into a `nirmmita` buffer Sutram passed
  to C, from which Sutram reads it back as a plain number. Any fix that closes §1
  closes this one.
- **A `kosh` kept by a `vibhag` parameter** — **CLOSED.** A `vibhag` parameter holds a
  **slice** in the callee's frame, not the `kosh`; it cannot be kept, returned, or
  passed to C, and can only be passed down a live call chain that returns before the
  block exits. The callee cannot grow the `kosh` through the slice, so the slice
  cannot go stale by growth either (`r129_check_call`, `:28910`, refuses the call
  itself if the callee may grow a `kosh` it is given alongside a `kosh`-made slice).
  The `r127` blind spot from the slice case (`vitti t = p[0:3]`) applies here too,
  contained inside the callee.

**The fix direction, for Claude, is two lines of work, not a redesign:** call
`r108_check_call` on the statement path too (`.gs_funcall`, `:19028`), and treat a
foreign `ptr` parameter as keeping for a block `kosh` — which the reference already
claims (`docs/LANGUAGE-REFERENCE.md:1373-1375`) and the code contradicts on the
statement path. Until then, the four conditions reclaim a region that C can still
hold.

The reference itself already admits the neighbouring fact for scratch addresses
(`docs/LANGUAGE-REFERENCE.md:1340-1345`): "An address passed to a `prakriya` that
keeps it … Those programs compile and are wrong … So a program that compiles is not
proved safe." The same sentence is true of the `kosh`'s region under ROUND-171.

---

## Task 2 — the 16 bytes

**The allocation:** one ordinary persistent allocation, descriptor + first elements
together, made by `emit_nirmmita_from_rax` via `r101a_emit_kosh_alloc`
(`src/sutram_compiler.asm:9122`, `jmp emit_nirmmita_from_rax`). There is no second
allocation, no per-`kosh` runtime allocation from the block, and no arena slot.

**The 16 bytes:** 24 bytes of R82 header (3 extra qwords — line, liveness slot,
generation) added to that one allocation, minus 8 bytes of alignment padding the plain
allocation already pays. Net observable difference: **16 bytes per `kosh`**.

**What they are for:** the three words are the runtime liveness check for a `kosh`
made inside a `mandapa` — the second line of defence behind the compile-time
`E_KOSH_MANDAPA` refusal. All three are **read**, by the check `r82_emit_check`
emitted in every `prakriya`'s prologue for each `kosh` parameter (see below). So the
answer to the brief's conditional — "if it is bookkeeping the block allocates per
`kosh` and never uses, that is a defect with a line number" — is **no: it is used
bookkeeping, not a defect of that kind.**

### Re-verification against R161

Every R161 Task 2 line number and arithmetic claim was re-read at this tip
(`79e65f90`; the code tree is identical to the R161 base `27bed64a` — only briefs
changed since). **No corrections.**

- Size computation `src/sutram_compiler.asm:19311-19323`: `add rax,4` (`:19311`, "2
  header qwords + R127's elements pointer and region size"), R82 branch
  `add rax,7` (`:19318`, "R82: 5 - line, liveness slot, generation, length,
  capacity"), `shl rax,3` (`:19323`) → (cap+4)×8 plain, (cap+7)×8 with R82 on.
- `r82_emit_kosh_header` (`:10850`; comment `:10847-10849`): writes `[rax]` line,
  `[rax+8]` slot address or 0, `[rax+16]` generation or 0, `[rax+24]` 0, `[rax+32]`
  cap, then `rax += 40`. Read in full, the writer does exactly what the comment says.
  The descriptor is **4 qwords / 32 bytes plain** (length at d-16, capacity at d-8,
  elements at d, region size at d+8) and **7 qwords / 56 bytes with R82** (the 3 extra
  qwords are line at d-40, liveness slot address at d-32, generation at d-24).
- Alignment `r65_emit_nirm` (`src/r65_arena.inc:245`; rule `cur = align16(cur +
  size)` at `:243`): `kosh temp[1]` align16(40) = **48** plain, align16(64) = **64**
  R82; `mala m[8]` align16(72) = **80**; 800,000 × 48/64/80 = 38,400,000 /
  51,200,000 / 64,000,000 bytes — all reproduce exactly. No growth happens for the
  measured programs (the push handler `:22440+` emits `cmp r9,r10` then `jb.space` —
  len 0 < cap 1 jumps to the append path, skipping growth).
- Program-wide flag: `r82_note_kosh_decl` (`:10662`) sets `r82_on` (`:1713`) when any
  `kosh` is declared at `r72_mdepth > 0`; every `kosh` decl checks it (`:19318`,
  `:19335`) — one `kosh` in a `mandapa` makes *every* `kosh` in the program
  56-byte-headed.
- Block entry `r82_block_enter` (`:10703`): one stack slot per `mandapa` depth
  (`stack_dep += 8`) plus an `rdtsc` generation — no heap, no per-`kosh` allocation.
  Block exit `r82_block_leave` (`:10799`): drops the `r108_bk_*` record, zeroes the
  liveness slot, decrements `r82_gdepth`; `r73_gen_rewind`
  (`src/r65_arena.inc:404`) restores only the scratch cursor end.
- Mala path `.gs_decl_array` (`:19389-19421`): `add rax,1`, `shl rax,3`,
  `call emit_nirmmita_from_rax`, never checks `r82_on` — 80 bytes, block or not.

| program | computed from code | brief |
|---|---|---|
| `kosh temp[1]`, no block | align16((1+4)×8) = 48 | 48 |
| same, in a `mandapa` | align16((1+7)×8) = 64 | 64 |
| `mala m[8]`, either | align16((8+1)×8) = 80 | 80 |

### The brief's conditional — is the R82 header used? Yes, all three words are read

The reader is `r82_emit_check` (`src/sutram_compiler.asm:11009`), the runtime check
emitted in a `prakriya`'s prologue for each `kosh` parameter by `r82_param_checks`
(`:10975`, called once per `prakriya` from `gen_all_functions`, `:18714`). The check
reads the header through the byte sequences `r82_c1`–`r82_c5` (`:455-459`), whose
decoded comments match their bytes exactly (verified against the `db` lines):

| sequence | emitted code | reads |
|---|---|---|
| `r82_c1` (`:455`) | `test rax,rax ; jz ok` | the descriptor itself (null check) |
| `r82_c2` (`:456`) | `mov rcx,[rax-32] ; test rcx,rcx ; jz ok` | the **slot address** word ([d-32]): non-zero means "this `kosh` was made in a block"; zero skips the check |
| `r82_c3` (`:457`) | `cmp rcx,rsp ; jb stale` | the slot address against the current stack pointer: a slot below `rsp` belongs to a frame that is gone |
| `r82_c4` (`:458`) | `mov rdx,[rcx] ; cmp rdx,[rax-24] ; je ok` | the **generation** in the live slot (`[rcx]`) against the header's **generation** word ([d-24]): equal means alive, different means stale |
| `r82_c5` (`:459`) | `mov rax,[rax-40]` | the **line** word ([d-40]) — on the stale path only, for the error message |

The stale path then prints, via `r82_m1`–`r82_m5` (`:438-442`), the `E_KOSH_MANDAPA`
message (including the line) and exits 1. So:

- **Line ([d-40])** — read on the stale path (`r82_c5`), printed as the block's line
  in the message. Without it the error could not say where the dead `kosh` was made.
- **Slot address ([d-32])** — read by `r82_c2` (the "is this a block `kosh`" test)
  and used as the pointer `r82_c3`/`r82_c4` dereference. Without it there is no slot
  to check.
- **Generation ([d-24])** — read by `r82_c4` and compared against the live slot. This
  is the comparison that makes the check work: the slot is written at block entry
  (fresh `rdtsc` generation) and zeroed at block exit, so a `kosh` whose block has
  ended, or whose block has been re-entered (new generation), fails the comparison.

The three header words are also preserved across growth: `r82_emit_grow_header`
(`:10955-10967`) copies line, slot, and generation into the new header
(`r82_grow_bytes`, `:451`).

**Verdict on the conditional: not a defect of the kind the brief names.** The header
is bookkeeping the block allocates per `kosh` and *uses* — every word has a read site
in the runtime liveness check, which is the second line of defence behind the
compile-time refusal (a dead `kosh` reaching a `prakriya` through a hole in the
static checks is caught here, with its line, instead of reading freed memory). There
is no line number to attach to an "allocated and never used" defect, because there
is none.

**The honest qualification.** The header is turned on by a program-wide flag, not
per `kosh`: one `kosh` in a `mandapa` makes *every* `kosh` in the program carry the 3
extra words, including `kosh`es that never enter a block and never reach a `prakriya`
parameter — for those, the words are written and never read. That is a precision
question (a per-`kosh` flag would cost a check at each declaration; the program-wide
flag costs 24 raw bytes per `kosh`), not unused bookkeeping. If the owner wants a
defect to chase, it is that overbreadth — and its line is the flag itself,
`r82_on resq 1` (`:1713`), set by `r82_note_kosh_decl` (`:10662`) — not any of the
three words.

**The stale comment.** At `:19331` the call site says `call r108_kosh_alloc ; R108:
in a mandapa, a slot of the block's arena; else R101A's region`. Both halves are
wrong at this base, and `r108_kosh_alloc`'s own comment (`:12651-12654`) is right:
"A kosh declared in an open mandapa is only remembered, so that r108_check_call can
refuse to give it to a prakriya that keeps it (the outlives rule). **No arena slot:
reclaiming waits for the descriptor.**" There is no arena slot for a `kosh` in a
`mandapa` — the storage is ordinary persistent `nirmmita` (`r101a_emit_kosh_alloc`,
`:9122`, jumps to `emit_nirmmita_from_rax`), and the only "slot" is the R82 liveness
slot, which is a **stack** slot (`stack_dep += 8` in `r82_block_enter`), not an arena
slot. And "else R101A's region" is the superseded R101A story: creation never takes a
region (R127, v302).

---

## Task 3 — reference §19, after the change

### The paragraph — the actual words, for Claude to paste

> From v316, one `kosh` in a block is different: a `kosh` made inside the block,
> never assigned to a variable declared outside the block, never returned with
> `nivartanam`, and never put into another `kosh` — pushed into it with `kosh_kship`,
> or written into it at an index — has its region given back when the block ends.
> The region is the separate buffer a `kosh` gets when it grows past 4,096 numbers,
> and it is returned to the operating system; the `kosh`'s own descriptor stays, and
> a `kosh` that never grows that big — even one made with room for more — has no
> region, so the block gives back nothing for it. Nothing else the block holds goes
> back to the operating system. A `kosh` that fails any of the four keeps its memory
> exactly as today, silently, with no error; and a `mala` is never given back. You can
> tell by reading the block: the `kosh` is made inside it, it is never assigned to a
> variable declared outside it, it is never returned, it is never put into another
> `kosh` — and it grew past 4,096 numbers.

One paragraph, ~180 words. It states all four conditions, what is released (only the
region above 4,096 elements), what stays (descriptor, small allocations, `mala`,
everything else the block holds), the escape behaviour (silent, exactly as today),
and the student's test (read the block; the four checks plus the growth test).

**Version flag — read before pasting.** "From v316" is provisional. v316 is staged on
branch `v316-ready` (`59d60353`) with the output-collision refusal and has not landed;
ROUND-171 has not been implemented yet, so its landing version is not assigned. If
v316 lands before ROUND-171, correct the version to the version ROUND-171 actually
lands in. Do not paste "v316" without checking.

### Anchor — where it goes, and the sentence it amends

File: `docs/LANGUAGE-REFERENCE.md`, §19, subsection "What it holds in v1.0".

**The sentence the brief quotes** is `docs/LANGUAGE-REFERENCE.md:1291–1292`, the last
two lines of the "Not a `kosh` of pointers" paragraph (`:1289–1292`):

> "A `kosh` of *numbers* used in a block works; its storage is ordinary memory, which
> the block does not reclaim."

**Amend that sentence minimally**, so the new paragraph does not contradict it:

> "A `kosh` of *numbers* used in a block works; its storage is ordinary memory, which
> the block does not reclaim, except for one case — below."

**Insert the new paragraph immediately after that paragraph** — i.e. after `:1292`,
before the blank line and the "**Nor a `mala`.**" paragraph at `:1294–1299`. The
`mala` paragraph then follows the new paragraph and is consistent with it (the new
paragraph ends "a `mala` is never given back"; the next paragraph says the same thing
with its measurement).

### Other sentences that will also need a matching change after ROUND-171

**(a) `docs/LANGUAGE-REFERENCE.md:1406–1407`** — "Decided (R103, v285)" paragraph:
"**Decided (R103, v285): the block does not take a `kosh`'s memory back; the `kosh`
keeps it for the program's life.** That is what keeps the check above exact: the check
reads the `kosh`'s header, so the header must still be there after the block." What is
now wrong: the decision has one exception — the separately mapped buffer of a `kosh`
that satisfies the four conditions. The *reason* still holds (the header stays; only
the buffer goes), so the fix is to narrow the decision, not remove it: "the block
does not take a `kosh`'s memory back, except for the separately mapped buffer of a
`kosh` that satisfies the four conditions above". The reasoning sentence that follows
it ("Giving the region back would make a dead `kosh` reaching a `prakriya` a crash…")
also needs its qualifier: it holds for a `kosh` that can still be reached; a
proven-local `kosh` cannot reach a `prakriya`, which is why giving its region back is
safe. The measurements in the same paragraph (the three programs `286`, `287`, `299`;
the 100,000-pass figures) are all small `kosh`es and stay true.

**(b) `docs/LANGUAGE-REFERENCE.md:1439–1440`** — `parimana()` "What it counts" bullet:
"A `kosh` keeps its bytes for the program's life, so they never fall." What is now
wrong — or, more precisely, undecided: this sentence is about what `parimana()`
reports. ROUND-171 does not say whether `parimana()` falls when the region is
released. If `parimana()` falls, the sentence needs the exception ("except for the
region of a qualifying big `kosh`, which is given back when its block ends"). If
`parimana()` does not fall, the sentence stays true *as a `parimana()` statement* —
but then `parimana()` and the operating system disagree about the same memory, which
would itself need a sentence. This one needs a decision from the implementation, not
just a wording change.

**(c) `docs/LANGUAGE-REFERENCE.md:1448–1450`** — `parimana()` "One number, moving"
paragraph: "A block's `nirmmita` comes back at its end; a `kosh`'s bytes do not, even
one made in the block - its storage is kept for the program's life (§16). The
descriptor is stable from v302, so a second name can no longer be left behind; what is
still not done is giving a `kosh`'s storage back when its block ends - the check above
reads its header after the block, so the header must stay." What is now wrong: "a
`kosh`'s bytes do not" is false for the region of a qualifying big `kosh`; "what is
still not done is giving a `kosh`'s storage back when its block ends" is now partly
done — the buffer, not the header. Fix: "a `kosh`'s bytes do not — except for the
region of a qualifying big `kosh`, whose buffer is given back while its header stays".
The reason ("the check above reads its header after the block, so the header must
stay") still holds and is exactly why the paragraph keeps the descriptor.

**(d) `docs/MEMORY-MODEL.md:5`** — status box, the three kinds: "Three kinds of memory
are made in a block's text and **only the first comes back**: `nirmmita`, given back;
a **`kosh`**, not - it is ordinary memory and keeps its bytes for the whole program,
only its life ends with the block; a **`mala`**, never…" What is now wrong: "only the
first comes back" is false for a qualifying big `kosh` — its region comes back too.
Fix: "a `kosh`, not — except for the region of a qualifying big `kosh` (see reference
§19)". The same line's last sentence, "The scratch side's pages are reused by the
next block, not returned to the operating system", stays true for the scratch side,
but the line as a whole now needs the qualifier that the block *does* return one
thing to the OS (the big region).

**(e) `docs/MEMORY-MODEL.md:9`** — status box, `parimana()`: "`parimana()` counts what
all the live blocks hold… a `kosh` by its **capacity, not its length**." Same open
question as (b): whether `parimana()` falls when the region is released. If it falls,
"counts what all the live blocks hold" and "a `kosh` by its capacity" need the same
exception; if it does not, the line stays true but disagrees with the OS. Decision
needed from the implementation.

**(f) `docs/sutram-book-english.html:823`** — chapter 19, "What a block gives back, and
what it does not" (list opens `:820`): "a `kosh` made inside a block - **not given
back**: it keeps its bytes for the whole program (section 3). Only its life ends with
the block, and it may not leave it (`E_KOSH_MANDAPA`)." Needs the same exception as
(d). The `mala` bullet below it (`:825–829`) stays true.

**(g) `docs/sutram-book-sanskrit.html:748–749`** — chapter 19, same list: "खण्डे
निर्मितः `kosh` - **न प्रत्यर्प्यते**: सम्पूर्णं क्रमादेशं स्वबाइट्-भागान् धारयति (§3)।"
Needs the same exception, worded in Sanskrit (Claude/owner to word it — this task
does not draft Sanskrit). The `mala` bullet below it (`:750–753`) stays true.

Checked, no change needed: `docs/LANGUAGE-REFERENCE.md:1294–1299` ("Nor a `mala`…");
`:1416–1417` ("The block bounds `nirmmita`…, not `kosh` storage." — a *budget*
statement, not a reclamation claim); §19 "Run time" bullet, "Pages are reused, not
returned." (scratch pages); `:967` (§16, "into a region of their own past 64 KiB");
`docs/MEMORY-MODEL.md:7` (descriptor layout); `:8` ("A `kosh` made in a block cannot
outlive it" — liveness); §2 and §7 (historical snapshot with superseding notes
already in place). English book `:948` and `:959` stay true.

### Vocabulary check — the paragraph uses only words the language already defines

`kosh`, `mala`, `mandapa`, block (§19 throughout); `nivartanam` (§19); "assigned to
a variable declared outside the block" (§19: "stored in a variable declared outside
it"); `kosh_kship` (§19); "written into it at an index" (§16/§19 indexing); region,
the separate buffer (§16: "into a region of their own past 64 KiB"; MEMORY-MODEL
status box line 7); descriptor (§16: "a descriptor that never moves"); "returned to
the operating system" / "goes back to the operating system" (§19 "Run time": "Pages
are reused, not returned"); "given back" (§19's own word); "grows past 4,096
numbers" (§16 growth); "silently, with no error" (WS4's own words, in plain
language); "You can tell by reading the block" (plain language; the four checks are
the four conditions restated, not a new rule). **No new jargon.** No `decl_depth`, no
"escape analysis" (per the design note, calling it that would be misleading — it is a
small conservative escape check), no `munmap`/`VirtualFree`, no "aliasing", no
"liveness", no "fixpoint", no "borrow checker", no "proven-local". The only number a
student has to remember is 4,096, and the paragraph tells them how to test it (did
the `kosh` grow past 4,096 numbers).

### Ambiguities in ROUND-171's wording, and the choice made in the paragraph

**(A) Which argument of `kosh_kship`? — the most important one.** WS3 says "the
symbol appearing as an argument to `kosh_kship`" without saying *which* argument.
Read literally it includes the destination: in `kosh_kship(k, x)`, `k` is argument 0.
But a `kosh` only grows by being pushed into — so read literally, every `kosh` that
ever grew would be flagged, and the feature would never reclaim anything. The
paragraph follows the only workable reading: the symbol as the *value* being pushed
into another `kosh`, not the `kosh` being pushed into ("pushed into it with
`kosh_kship`" — "it" is another `kosh`). The implementation must check the value
arguments, not the destination. (Same finding as Task 1 §A.)

**(B) "Stored in any other collection" (WS1) is broader than what WS3 checks.** WS3
lists only two forms: the symbol as an argument to `kosh_kship`, or as the right side
of a `kosh` element write. The paragraph states those two forms and does not promise
more. The other stores — a `mala` element write (`m[i] = k`), a `rachana` field, a raw
cell — are already refused outright by `E_KOSH_MANDAPA` for a block `kosh` (§19:
"stored in a variable declared outside it, written into memory (`kosh_kship(outer,
k)`, `m[i] = k`), or returned"; R161 T3), so they never reach the reclamation
decision — they disqualify by refusing, not by flagging. Choice: follow WS3, and rely
on the existing refusals for the rest.

**(C) "Assigned outward" — outer block vs module-level.** WS1 says "a variable
declared outside the block", which covers both a module-level variable and a variable
declared in a block around it. The paragraph uses WS1's words. Choice: both count.
WS3's `decl_depth` comparison agrees under either reading of `decl_depth` (lexical
depth or `mandapa` depth), because an outer variable has a smaller depth either way.

**(D) A slice.** A slice is not "stored" under WS3's check: a slice expression
(`k[0:5]`) is neither an argument to `kosh_kship` nor the right side of a `kosh`
element write. The paragraph does not claim the four conditions cover slices; the
existing slice doors refuse a `kosh` slice being kept in a name. Whether a slice
that escapes through a path the doors miss breaks the reclamation is Task 1's
question, not this paragraph's. Choice: the paragraph is silent on slices; it states
the four conditions about the `kosh` itself.

**(E) "Released" vs "given back to the OS".** WS6 says "a block still never returns
memory to the OS". Read strictly, that is false after ROUND-171: the big region is
`munmap`'d on Linux and `VirtualFree`'d on Windows — returned to the OS (verified
R161 T1). The paragraph says the region "is returned to the operating system" and
confines the never-returned claim to everything else ("Nothing else the block holds
goes back to the operating system"). Choice: the paragraph follows the mechanism.
WS6's bullet should be read as "a block still never returns its *arena* memory to the
OS" — a wording correction to WS6, not just a paragraph choice.

**(F) Every exit, or only the last line?** WS1 says the buffer is "released when the
block exits" without stating whether the release runs on every exit path (end of
body, early `nivartanam`, `krama`, `agrim`, `prasar`) or only at the last line. The
paragraph says "when the block ends", following the `mandapa`'s own every-exit rule
(§19: "Every exit gives it all back", `:1304` — end of body, `nivartanam`, `krama`,
`agrim`, failure). Choice: every exit. If the implementation only hooks the last
line, "when the block ends" would be false on `krama`/`agrim`/early-return exits.

**(G) The version number.** See the flag in the paragraph section: "From v316" is
provisional; correct it to the landing version.

**(H) The `kosh` as the left side (`k = outer`).** The four conditions say nothing
about the `kosh` being assigned a value from outside. If `k` is assigned an outer
`kosh`, the names alias and releasing `k`'s region would free the outer `kosh`'s
region. That is Task 1's question (the attack), not this paragraph's. Choice: out of
scope; the paragraph does not claim to cover it.

**(I) Returned inside `siddhi`/`dosh`.** WS3 says "a `nivartanam` whose expression is
the symbol". Read strictly, `nivartanam siddhi(k)` has expression `siddhi(k)`, not
the symbol. The paragraph says "never returned with `nivartanam`" in the student's
sense — any form. The gap is closed by the existing return refusal
(`E_KOSH_MANDAPA` refuses tainted values returned plain, `siddhi(...)`, or
`dosh(...)` — reference `:1108`: "as a `siddhi` / `dosh` value"), so no compiling
program reaches the gap. Choice: the paragraph uses the student's broader sense.

**(J) What does `parimana()` report after the release?** ROUND-171 does not say. The
paragraph promises nothing about `parimana()`. See items (b) and (e) above: if
`parimana()` falls, two §19 sentences and one MEMORY-MODEL line need the exception
as `parimana()` statements; if it does not fall, those sentences stay true but
`parimana()` and the OS then disagree about the same memory, which would need its own
sentence.

**(K) A `kosh` declared in a block nested inside the `mandapa`.** Is it "made inside
the block"? The paragraph says "made inside the block" on the plain reading — the
nested block's text is inside the `mandapa`'s text, so yes, and the release would
happen at the `mandapa`'s exit, not the inner block's. Choice: plain reading; the
implementation's `decl_depth` comparison decides.

**(L) The declared-big edge case — resolved in the paragraph, not left open.** A
`kosh` declared with room for 5,000 numbers but never grown past its first size has
no region (a region is taken only on growth past `R127_BIG`, 64 KiB — first
region-taking growth is the 4,097th push; R161 T1). The paragraph says it outright:
"even one made with room for more — has no region, so the block gives back nothing
for it."

### One correction to the brief's framing

The brief says the §19 sentence "becomes true for most `kosh`es and false for the
ones that escape". That is backwards. The sentence becomes false for the `kosh`es
that **qualify** (proven-local, big — their region *is* reclaimed); it stays true for
the ones that **escape** (they behave exactly as today, silently, per WS4). The
paragraph is written on the corrected framing.

---

## Brief corrections

1. **The installer hash in the shared state is stale — confirmed.** The shared state
   (carried from the R159/R161 briefs) says the installer is `6f9cdbda…`. That was
   correct at base `035a2567` (verified in R159 T2) but is stale at this tip: the
   installer was rebuilt in commit `e5088fe2` (Claude R167). At `79e65f90`,
   `Sutram-Setup.exe` hashes to
   `d8ae75c94bf94cedab31ce7cd7fb261c70ea93edc8cb6b1b0fbcb4da0f7cadc9` (verified by
   `git show HEAD:Sutram-Setup.exe | sha256sum` in the worktree). The R162 brief's
   own count ("fifty-five false claims… a stale installer hash") is right on this
   one.
2. **The §19 framing (see Task 3):** the sentence becomes false for the `kosh`es that
   **qualify**, not the ones that escape.
3. **WS6's "a block still never returns memory to the OS" is false after ROUND-171**
   (see Task 3 (E)): the big region is `munmap`'d / `VirtualFree`'d — returned to the
   OS. The bullet should read "a block still never returns its *arena* memory to the
   OS".
4. **The 312 KB baseline — the R162 brief's correction is accepted, and it does not
   touch the per-pass numbers.** The R161 brief said the baseline was 312 KB with an
   empty environment; the R162 shared state corrects it to 12–24 KB ("the 312 was
   `/usr/bin/time`'s own size"), and its measured-leaks table puts the `nirmmita`
   flat line at ~20 KB. The R161 T2 per-pass figures (48 / 64 / 80 bytes) are cursor
   advances computed from the code, not baselines — re-derived in Task 2 above and
   unchanged.
5. **The gate-count off-by-one, one round later.** The shared state says "81 gates".
   That is right as a **total** (78 `run_gate` invocations + X11 + doc_counts +
   Windows skip = 81 entries — verified at this base; the code tree is unchanged
   since `27bed64a`). But the reference status line still says "gates **81 PASS / 0
   FAIL / 1 NOT-RUN**" (`docs/LANGUAGE-REFERENCE.md:3`) — max PASS is **80**, the same
   off-by-one as R159 P4, one gate higher. The status line should read "80 PASS / 0
   FAIL / 1 NOT-RUN".

## Could not determine from source

- The exact runtime outcome of reading the freed region in Task 1 §1/§2 (segfault vs.
  silent wrong data): it depends on whether the address has been remapped by a later
  `mmap` by the time C reads it. Needs execution; this round is read-only.
- Whether the WS3 check walks the whole enclosing `prakriya` or only the block's
  direct statements (Task 1 §7): the spec does not say, and the code does not exist
  yet (ROUND-171 is a design, not built). This is a spec gap, not a reading gap.
- Whether the block-exit release will read `[d]`/`[d+8]` from the current frame's
  descriptor (Task 1 §8): the release code does not exist yet. Frame-relative is the
  only recursion-safe choice; a per-symbol global would break it.
- Whether a slice-of-a-slice through a `vibhag` parameter (`vitti t = p[0:3]`,
  Task 1 §5) is refused anywhere other than `r127_check_slice_value`: `r127` does
  not see it (base is a parameter, not a `kosh` name) and `r126_bind` binds it as a
  slice name. It cannot escape the callee by any door found, but whether it can be
  used to write through to the `kosh`'s elements after a growth is `r129`'s
  territory, not this attack's.
- Whether any `.sffi` declaration in the tree already declares a `ptr` parameter
  that a block `kosh` could reach: the mechanism supports it (`tests/r32/ffi.sffi`
  form), and the C side is the user's to write. No existing test was found that
  passes a block `kosh` to C; the hole is in the door, not in a test.
- Whether `r108_param_kept` treats a plain index read `k[i]` as a keeping use (the
  R161 T3 open item, unchanged): its comment (`:12807-12811`) says a parameter is
  marked as keeping when some use of it is "not a read (k[i]), a kosh builtin's own
  operand, or an argument to a parameter that does not keep", but the walk counts
  `AST_VAR` occurrences and the dispatch was not fully read. If a read counts as
  keeping, that fails closed — a conservatism question, not a soundness hole.
- Where the R82 generation is verified at a `kosh`'s use site other than a `prakriya`
  prologue: the read side traced here is `r82_emit_check` in the prologue only. A
  dead `kosh` used directly (indexed, pushed) in the same function after its block
  ends is refused by the compile-time checks (`r73_check_stmt`, `r108_check_call`),
  not by a runtime read of the generation — whether any direct-use path also reads
  the header was not traced.
- Whether the program-wide `r82_on` flag's overbreadth (every `kosh` pays 24 raw
  bytes once any `kosh` is in a block) was a deliberate trade or an oversight: the
  flag's comment (`:1713`) states what it is, not why it is program-wide. A
  per-`kosh` flag would need a check at each declaration; no design note in the tree
  discusses the choice.
- Whether any live program path produces a kind-6 return that `r126_check_return`
  refuses in practice (a `?:` with a `kosh` arm gives kind 6 via `r126_value_kind`,
  `:27920`); no live example was traced.
- The exact line of `r73_gen_scrcur` (cited by its call site `:21498` and the
  `AST_SCRCUR` node creation `:8370`).
- The `parimana()` `.zero`-path displacement question from R155/R158: still open,
  still needs execution; unrelated to this round, noted only so it is not mistaken
  for resolved.
