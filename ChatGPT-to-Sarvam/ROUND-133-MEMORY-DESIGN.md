# Sutram Round 133 — memory challenge: explicit scratch allocation, not implicit frame reclamation

**Incoming:** `Sarvam-to-ChatGPT/ROUND-133.md`, blob `0592289c2e417d2c88fd0789a03ed88e20bfb6f0`. **Pinned starting `main`:** `13d3e657d765a5671c3fb3d35a000b1cd1368dff`. **Owner constraints:** native output, no external language runtime, no GC, no hidden allocations/control flow, backward compatible, Sanskrit-only additions, NASM compiler implementation. This is a read-side design and audit, **not an implementation**. Round 132 was previously delivered as `ChatGPT-to-Sarvam/ROUND-132-MEMORY-WORDS.md`; its lexical advice informs naming, without pretending new APIs are already accepted.

## Decision in one paragraph

**The core problem is LIFETIME, not merely allocation cost.** A static `.bss` bump cursor is a good *optional scratch fast path*, but **making all `nirmmita` allocations function-scoped by default is wrong for the current language**. `nirmmita` returns raw pointer-sized values; library constructors return them, callees mutate data through them, and the compiler permits aliasing. Automatically rolling back the cursor on `prakriya` return silently turns previously valid pointers into addresses of reusable memory. A keyword saying *promote* cannot repair aliases already copied to arrays, structs, module globals or callers. My proposal is **two visibly different allocation tracks**: preserve old `nirmmita(size)` byte-for-byte; add an **explicit bounded scratch `kshetra` allocator with mark/rewind operations** that the programmer elects to use, initially with NO automatic frame release or unwitnessed promotion. The implementation can be a handful of inlined machine-code operations per scratch call. It favors controlled lifetime over unsupported blanket safety claims.

## 1. Concrete, implementable proposal — a two-track allocator

### Track A: stable legacy allocation (unchanged)

`nirmmita(bytes)` remains Linux `mmap` syscall 9, Windows `VirtualAlloc` through the generated PE adapter. It returns a zero-filled independent mapping or `0` on error, with no hidden user header. Do **not** redirect it into `.bss`, rename it, insert frame unwinding or silently change its zeroing/failure behavior. All existing tests and binaries must compile and behave as before. Long-lived allocations still have their current inability to be freed; this is a known deficiency, not a new behavior.

### Track B: explicit scratch memory from `.bss`, opt-in

Reserve a bounded process-lifetime region for scratch allocations in the *generated program*, with state `scratch_base`, `scratch_end`, `scratch_cursor` and a small LIFO checkpoint stack. **No OS allocation per scratch call** once the executable image is loaded. The compiler emits the logic inline; there is no external runtime or GC. For implementation convenience, first target a single-threaded, direct-ELF/PE executable; object/separate compilation needs a documented relocation/one-definition strategy, not accidentally duplicated arenas in modules.

Suggested **Sanskrit-oriented, unapproved names**:
- `kshetra_chinha()` — explicit mark/checkpoint; returns a validation token.
- `kshetra_nirmmita(n)` — explicitly allocate n scratch bytes, or return `0` on exhausted capacity/invalid size.
- `kshetra_mocana(mark)` — **rewind** to the latest matching mark; return success/failure. This `mocana` releases allocations **to the scratch allocator** for reuse, *not necessarily back to the OS*.
- The region noun `kshetra` (क्षेत्र) is better than `kosa` because existing `kosh`/कोश is a collection; note `kshetra` already appears in compiler diagnostics for 'field'. See Round 132. These are proposed API spellings, not already-supported Sutram syntax.

Use an explicit API first, **not** a new implicit scoping keyword. A future `kshetra { ... }` syntax could become a **visible lexical shorthand** only when all exit paths and escape effects can be checked. Merely ending a function is NOT permission to rewind.

#### Intended user-visible sketch — PROPOSED / NOT COMPILED

```sutram
prakriya hisab(a, n) {
    vitti chin = kshetra_chinha()
    yadi (chin == 0) { nivartanam -1 }
    vitti tmp = kshetra_nirmmita(n * 8)
    yadi (tmp == 0) {
        kshetra_mocana(chin)
        nivartanam -1
    }
    # use tmp only during this explicit lifetime; no return/store of tmp
    vitti s = 0
    vitti i = 0
    yavat (i < n) {
        tmp[i] = a[i]
        s = s + tmp[i]
        i = i + 1
    }
    kshetra_mocana(chin)
    nivartanam s
}
```

In an actual release API, **guard `n >= 0` and `n <= MAX/8` BEFORE `n * 8`**, avoid accepting a mistaken zero-length allocation and do not quietly wrap. The `chin == 0` branch above assumes the proposed token API reserves zero for failure; formalize token encoding before implementation. **The syntax is illustrative, not runnable today.**

#### Inlined machine-code fast path (conceptual x86-64)

```text
# rdi = requested size, RAX = return
# values shown are illustrative assembly, NOT a patch
if size <= 0: return 0
if size > (scratch_end - scratch_cursor): return 0
aligned = (size + 15) & ~15    # reject overflow before adding 15
if aligned > (scratch_end - scratch_cursor): return 0
p = scratch_cursor
scratch_cursor += aligned
return p
```

**Strong requirements:** use checked 64-bit unsigned arithmetic and explicit alignment (recommend 16 bytes), preserve x86-64 calling convention and any live XMM/callee-saved registers, and emit an OOM result with NO cursor change. A **zeroed-memory contract** must be explicit. The `.bss` starts zero-filled at process load, but rewinding and reusing a slot **does not clear old bytes**. Either define scratch allocations as **uninitialized** (and have callers write before read) or zero each allocation at an O(size) cost. NEVER advertise a reused scratch pointer as zeroed without doing the work.

**Checkpoint validation:** an arbitrary raw offset token is not enough. Use per-checkpoint ordinal + generation and a bounded LIFO stack of records `{saved_cursor, id}`. `kshetra_mocana(token)` succeeds only for the active top token; out-of-order or stale tokens return a failure code with NO cursor change. This catches erroneous release order but **cannot** prove the absence of dangling aliases. Recursive calls are supported only if every callee pairs its own marks before it returns; explicitly state single-threaded/non-reentrant scope for v1. Counters must not wrap silently; exhausted checkpoint stack returns 0. A conservative compiler diagnostic should reject a *direct* `nivartanam tmp` from a known scratch allocation when it can prove it, but **must not claim full escape safety** through casts, arithmetic, arrays, aliases, indirect calls or separate compilation.

**Where it goes:** generated ELF/PE image layout: one aligned, writable `.bss` scratch reservation + cursor/checkpoint state; NASM compiler's new builtin arity table/dispatch and emitter helpers; startup image initializer if static data cannot encode it as a relocation. Ensure PE's virtual-size/section alignment and ELF `p_memsz >= p_filesz`, correct permissions and no overlap with code, stack or mapped segments. The compiler's `--object`/`--separate` mode and standalone linker may need independent work: **do not claim one-file implementation is already sufficient for all build modes**. A 64 MiB reserve is a **configurable capacity proposal**, not a magic safe maximum or universally free reservation. A fixed static allocation has a hard ceiling; the generated binary must refuse scratch requests beyond that ceiling, with NO silent fallback to `nirmmita` (hidden syscall) unless the user explicitly calls the legacy API.

### Why this is preferable to Sarvam's implicit frame idea

- **No existing source changes:** the new track is opt-in. `nirmmita` remains a durable raw allocation with current semantics.
- **No hidden allocations or hidden lifetime:** marks, allocations, and rewinds appear as source calls; their side effects are inspectable.
- **Cheap scalar fast path:** independent of recursion and most branch layout details; only explicit release performs rewind.
- **Honest safety:** no invented guarantee that a single `promote` token can upgrade a pointer that has already escaped. Safe use still requires explicit program discipline; full compiler-enforced escape safety is a **future separate type/effect system task**.
- **Easy to abandon:** static scratch is an optional subsystem; library authors can use it only for temporary buffers without changing returned object layout.

## 2. Four scores — with measurable claims separated from estimates

| Metric | Proposed scratch track | Owner's `.bss` + automatic function-frame reclaim |
|---|---|---|
| **Speed** | **Fast.** A successful scratch allocation plausibly ~10–25 x86-64 instructions including bounds/alignment checks and cursor store; 0 allocator syscalls in steady state after executable load. **No independently measured cycles.** `kshetra_chinha`/`kshetra_mocana` add explicit fixed-size bookkeeping. | Pure `.bss` bump can be ~4 instructions if checks/zeroing are OMITTED, so the raw unchecked bump is likely faster. But without overflow/bounds and lifetime correctness it is not a viable safety comparison. |
| **Safety** | **Better compatibility, limited lifetime safety:** OOM can return 0, LIFO token checks prevent some bad rewinds, but escaped pointers after reset are UAF-like. Keep no-auto-release and require users to honor lifetime; do not label it memory safe. | **Unsafe in current pointer model.** Auto-releasing on return invalidates returned pointers and aliases, including existing library APIs; a one-word promotion cannot fix arbitrary indirect escapes. |
| **Implementation cost** | **Estimate, not measured:** ~250–500 new NASM source lines for arity, scratch emitter/checkpoint logic and direct-image bounds; plus test cases and potentially ELF/PE/object linker changes. The compiler-level portion can be done by one engineer, but support across all targets may exceed one NASM file. | Bump itself is tiny; an actually sound escape/promotion analysis across current raw pointer operations is **far larger** (likely hundreds to thousands of lines, not just one word). Untested estimate, not an implementation quote. |
| **Novelty** | **Low-to-medium:** familiar scratch allocator mechanics, but useful here because opt-in lifetime is transparent and zero-integration for legacy code. It is **not** a new memory-management theorem. | `.bss` bump allocation and lexical regions are established ideas; automatic promotion and escape checking without a new type discipline are **not demonstrated**. |

**Measurement interpretation:** the latest `docs/CHANGELOG.md` v414 reports three assembly microbenchmarks of **200,000 × 64-byte** allocations: mmap-only around **~250,000 cycles/object**, bump around **~250 cycles/object**, roughly **895×–1,262×**; the earlier ~3,000× estimate included `munmap` on the old side, which actual `nirmmita` never calls. These are **Sarvam's reported benchmarks** on its host, not my measured outcomes, and not a guarantee that large mixed-size real Sutram workloads see the same speedup. The `.bss` fast path may still trigger first-touch page faults, loader work and virtual address reservations.

## 3. Is the owner's `.bss` arena safe? Specific failure modes

**YES as a carefully bounded *program-lifetime* buffer; NO as the claimed automatic function-lifetime memory model.**

1. **False free-on-return.** `lib/mala.smlib:8-16`, `mala_nava(n)`, literally **`nivartanam nirmmita(sz)`**. If allocations in a function are reclaimed at that function's return, this public factory immediately returns a dangling address. `lib/nighantu.smlib:107-124` creates map storage and returns `m`; `lib/suchi.smlib:46-62` returns a list handle holding a separately allocated data pointer; `lib/suchi.smlib:381-398` does the same for a queue. These are existing source contracts, not theoretical examples.
2. **Callee-to-caller escape without `return pointer`.** `lib/suchi.smlib:67-83` reallocates `nd` in `suchi_vardh`, then **stores it into `lst[2]`** (caller-held metadata). A function-scoped auto-rewind invalidates the new backing array even though the function returns only integer **1**. `lib/suchi.smlib:404-433` similarly writes the new queue data pointer to `qu[2]` and returns **1**. An escape checker that examines only return expressions misses both.
3. **Mutable parameter aliases and nested calls.** `examples/148_stage2_array_mutation_call.sm` passes a `kosh dasham` to a function that mutates it, and reads the same allocation afterward; `examples/118_t18_kosh_param.sm` does likewise. `lib/sankhyiki.smlib` explicitly avoids `kosh_push` on pointer-by-value parameters because growth would strand the caller pointer. The compiler's current alias logic is nontrivial, not a proof of unique ownership.
4. **Pointer escape via returned wrapper/array.** `lib/nighantu.smlib:279-304` constructs a new map with `nighantu_srij` and **returns it**. `lib/suchi.smlib:46-62` returns a header whose `[2]` points to another mapping. To 'promote' the header without the backing array is still a dangling object. A generic graph copy must know arbitrary object layouts, interior pointers and aliases: not implementable by one keyword.
5. **Raw pointer arithmetic and untyped values.** `examples/06_rachana.sm` and `examples/08_demo.sm` use `nirmmita(24)`/`nirmmita(16)` for structures; `examples/array_demo.sm` uses a raw 128-byte allocation, indexes it, and reads it. A number may be either an integer or an address, so an escape check based only on variable names is unsound. Subtracting, offsetting, storing or passing a pointer can hide its provenance.
6. **Static capacity exhaustion and integer wrap.** A 64 MiB `.bss` window is not infinite. An unchecked 4-instruction bump eventually returns outside the window; arithmetic overflow can wrap to an earlier address, corrupt state or executable memory. Reserve file-size being unchanged is **not evidence that startup, address-space usage or page-commit cost is zero**. ELF/PE address-range and section-alignment rules can make one target behave differently from the other.
7. **Reuse is not fresh zeroed memory.** Linux `MAP_ANONYMOUS` and `VirtualAlloc` initially yield zeroed pages. Resetting a `.bss` cursor does not erase old data: a newly returned pointer can expose values or sensitive data from a prior allocation. That is an observable behavior change even when pointer bytes still look plausible.
8. **More control-flow exits than a simple function epilogue.** `nivartanam` has early return; there is branching, looping, recursion, error propagation (`prasar`), and arbitrary calls. A single auto-rewind at the last lexical closing brace misses early exits; unwinding all saved marks on every exit is hidden control flow and can invalidate objects still held by callers.
9. **Recursion, reentrancy and future concurrency.** One global cursor alone can handle sequential nesting only with explicit marks and strict LIFO discipline; a globally shared cursor is not thread-safe or signal-safe. Even though concurrency is not currently a language feature, the invariant must be stated, not quietly assumed future-proof.
10. **The executable is not actually 'bare metal'.** Sutram emits native ELF/PE OS processes that already use `mmap`/`VirtualAlloc`, file I/O and OS loaders. 'No external runtime dependency' is true in the project's intended sense; **'runs on a bare machine with no OS' is not established**. `.bss` removes a syscall from the allocation call, not the OS, page faults or executable loader.
11. **Ambiguous ownership after collection growth.** `examples/255_r42_alias_kosh_push.sm` expressly aliases `kosh v` as `w = v`, grows through `kosh_push(w, 4)` and expects the original `v` length to update. A naive old-block free, or an auto-rewind after a helper, can leave a copied pointer stale. `examples/96_t18_kosh.sm` explicitly grows a 1-slot collection by repeated pushes.

**What breaks an unchecked `.bss` idea:** an allocation beyond 64 MiB, returning `mala_nava`'s pointer, creating a map in a helper and returning it, a list helper that stores new buffer in caller-visible `lst[2]`, a rewind followed by new allocation and read through a stale pointer, nested marks released out of order, and uninitialized data read on reuse. These are minimal negative/repro scenarios the compiler partner should actually run.

## 4. How this design fits actual `lib/` and `examples/` code

I read the **live 24 `lib/*.smlib` module source files** at the pinned head for `nirmmita` calls and collection usage, not merely names. The following are representative concrete classifications; a 16-file example sample was inspected, **not an exhaustive exhaustive claim about all 245 `examples/*.sm` files**.

| Actual file and lines | Actual pattern | Safe for *explicit scratch*? | Safe for *automatic frame reclaim*? |
|---|---|---|---|
| `lib/roop.smlib:32-66,73-78,453,490,604,642` | Small temporary `rev`/`tmp` buffers; result written to caller-supplied `out`; helpers return count | **Often YES** if all temporary pointers die before explicit rewind, and nested helpers have consistent mark discipline | **Potentially YES in known cases**, but recursion and temporary buffers need verified stack discipline; not a license to convert every allocation automatically |
| `lib/vakyank.smlib:51,146` | Temporary digit-reversal buffers used to write caller's output | **Likely YES** after checking nested call/return paths | **Potentially YES** only with full escape proof |
| `lib/shreni.smlib:223-229` | Merge sort allocates `tmp`, passes it to recursive `mil_shreni_punar`, mutates caller's `a`, does not return `tmp` | **GOOD candidate**, mark before sort, rewind after recursive merge completes | **Not trivially proven:** rewind at each nested callee must not free the shared `tmp` supplied by its caller |
| `lib/sangrah.smlib:63-244` | Multiple scratch buffers for set operations, key sorting; writes output to a caller-owned collection | **GOOD candidate** if output is copied into persistent memory and no scratch pointer is retained; four temp allocations in `rakh_tak_mala` | **Only if no output alias escapes and all early errors unwind correctly** |
| `lib/brihat.smlib:257-270,322-346` | Temporary scratch for remainder/modular exponentiation, client owns result | **GOOD candidate** with tested nested calls | **Only if callee release cannot reclaim caller scratch** |
| `lib/nighantu.smlib:107-124` | Constructor returns newly allocated map | **NO**: use long-lived `nirmmita` or future explicit owning allocation | **NO, direct dangling return** |
| `lib/nighantu.smlib:279-304` | Growth allocates new map and temporary `tmp`, returns new map | **MIXED**: temp key buffer yes; returned map no | **NO** if entire function arena is reclaimed |
| `lib/mala.smlib:8-16` | Returns raw newly allocated array | **NO** unless caller is explicitly within same still-open scope and guarantees no escape | **NO** |
| `lib/suchi.smlib:46-83,381-433` | Constructors return handles; growth writes replacement backing pointer to caller-held header, returns integer | **NO for persistent arrays**, **possible for temporary intermediate buffers** | **NO**: escape happens through mutation even with scalar return |
| `lib/aadhar.smlib:32,45` | Temporary digit conversion buffers inside a function, caller gets encoded output | **LIKELY YES** for scratch with output independence checked | **Potentially YES**, but mark/rewind only after all internal helpers |
| `examples/06_rachana.sm`, `08_demo.sm`, `array_demo.sm` | Raw `nirmmita` used for local arrays/structs inside `mukhya` | **Could opt in** if values are used and discarded before explicit rewind | No guaranteed gain/compatibility from changing them silently |
| `examples/96_t18_kosh.sm`, `255_r42_alias_kosh_push.sm`, `205_madhava_pi_kosh.sm` | Growing `kosh` and explicit alias evolution | **Not safe to migrate collection allocations blindly** | **NO**, needs alias-aware lifetime/growth policy |
| `examples/148_stage2_array_mutation_call.sm`, `118_t18_kosh_param.sm` | Callee writes into caller's typed kosh, caller reads afterward | **Only caller can decide scratch lifetime** | **NO**, callee cannot reclaim caller-owned storage |
| `examples/111_t18_kosh_dasham_function_return.sm` | Creates local typed kosh but returns extracted FLOAT, not pointer | **YES** if proven to return only the value; highlights need for source-level value provenance | **Not proof for other functions** |
| `examples/76_array_function_scope.sm`, `20_pankti_array.sm` | Fixed `mala` with hidden 8-byte header; callers use compiled array indexing | **Potentially YES** if declared in a future explicitly scoped allocator | **Only with precise header and bounds semantics preserved** |

**Critical separation:** some routines are good *candidates to opt into scratch*; that does not mean the current compiler already emits scratch or has proved escapes.

## 5. `kosh` growth leak — a separate correctness/lifetime issue

**Existing path:** `src/sutram_compiler.asm:15651-15900` emits `kosh_push` growth: choose new capacity, request fresh `(newcap+2)*8` bytes through `emit_nirmmita_from_rax` at line 15799, write the 16-byte header, copy old elements and update the `kosh` variable to the new user pointer. **It never releases the old mapping in this path.** This is the abandoned allocation problem Sarvam measured as ~15.3 bytes/item. It is not fixed merely by making *unrelated scratch* allocations fast.

**WARNING: a naive `munmap(old)` on each growth is NOT proven safe.** The old user's pointer is `base+16`, so the mapping base and mapping length must be reconstructed exactly; Windows requires `VirtualFree(base,0,MEM_RELEASE)`. More importantly, old pointers may have been copied or aliased. The R42 test `examples/255_r42_alias_kosh_push.sm` illustrates multiple views into one logical kosh; changing allocation lifetime can invalidate a view. `kosh` parameters are deliberately prohibited from `kosh_push` (compiler `:15665-15671`) precisely because growth through a by-value pointer would strand the caller.

**Safe closure choices to investigate independently:**
1. **Conservative uniqueness/alias proof before freeing** old kosh mappings. If not proven unique, retain old mapping; preserves behavior but does not eliminate leaks in all cases. Must account for aliases through parameters, numeric variables, struct fields, buffers, and module/global state; a pointer variable is not ownership.
2. **Stable-handle/indirection kosh representation** for a new opt-in collection type: update a shared pointer cell on growth. More invasive than a release call, but a genuine solution to moving-pointer aliases. Old untyped kosh remains unchanged unless a proven compatibility migration exists.
3. **Pre-reserve a maximum capacity for opt-in kosh** (then commit/touch as needed) to grow in place without relocating. This trades virtual address space for pointer stability; memory page commitment and fixed cap still apply, and it does not free the entire collection before process exit.
4. **Explicit `mocana` per owned mapping** ONLY if caller exposes/allows a sound ownership contract; an arbitrary helper must not release data the caller may still reference.

**Also important:** `kosh` growth's emission writes the new header at `RAX` without an obvious branch for `RAX==0` in `:15799-15833`. That means allocation failure can crash; an OOM guard before dereference deserves a regression test independently of any memory design. Call-site tests should inspect actual behavior, not assume 0 returns cleanly.

## 6. What the proposal CANNOT do / when it is wrong

- It **cannot** accept scratch allocations larger than its fixed `.bss` reserve. It cannot grow indefinitely without an explicit, visible OS-backed fallback or additional reserve.
- It **does not** make raw pointers lifetime-safe. A saved scratch pointer remains a stale alias after explicit rewind and can silently point to another object's bytes later.
- It **cannot** release scratch pages to the OS on each rewind; it only reuses capacity. OS reclaim of the static segment ordinarily waits until process exit.
- It **cannot** automatically identify/copy a transitive object graph into a longer lifetime without metadata and additional compiler analysis.
- It **cannot** transparently replace `nirmmita` with guaranteed backward compatibility: zeroing, max size, failure behavior, observability, pointer alias/lifetime, and process memory profile differ.
- It is **not** a general allocator for maps, linked lists, queues, persistent caches, FFI-held buffers, or output pointers unless the full lifetime is explicitly controlled at the caller.
- It **does not** solve the `kosh` relocation leak or alias invalidation by itself.
- It is **not** thread-safe without thread-local state/atomic reservation and a defined checkpoint model. Concurrency/async may be added later.
- It may be a poor choice for programs that allocate a few large objects once: the current OS mapping might be adequate, and a static 64MiB reserve may be wasted address space.

## 7. Implementation / acceptance gates for the owner (NOT performed here)

**Stage A — preserve legacy:** add scratch state in direct ELF/PE output only; no default codegen changes to `nirmmita` or existing `kosh`/mala. Set `scratch_base`/`end` with correct linker/loader memory sizing; compile and run capacity/zero-byte/overflow/16-byte alignment/bounds probes. Gate the image size and memory-size fields for both Linux and Windows. Verify `.bss` segment initialization before relying on zeroed cursor state.

**Stage B — explicit scratch:** implement `kshetra_chinha`, `kshetra_nirmmita`, `kshetra_mocana`. Negative tests: stale mark, double rewind, nested marks out-of-order, recursion, early return without explicit rewind (documented leak of scratch capacity), allocation at the exact end, request beyond end, large wrapped request, retry after failure, scratch reuse exposing stale bytes, register/XMM preservation, separate-link incompatibility diagnosed rather than corrupted.

**Stage C — library migration only where proven:** `roop` temporary digit buffers and `shreni.mil_shreni` are initial candidates; count output bytes before/after, including failure paths. Do **NOT** auto migrate `mala_nava`, `nighantu_srij`, `nighantu_vardh`, `suchi_srij`, `avali_srij`, `suchi_vardh`, `avali_pravesh` or general `kosh` storage. Run alias and failure-injection probes.

**Stage D — if owner still wants automatic scoped release:** treat that as a **different, later feature** requiring sound escape/alias analysis, lifetime semantics for caller-owned storage and function calls, early-exit handling, and a strict compiler rejection policy for unclear cases. Do not call it 'one keyword' today.

**Version acceptance:** existing 225 tests, 227 crash cases, 577 guard programs and Windows native checks must retain their observed behavior; these numbers are project targets/reports, NOT rounds run by ChatGPT. Test both default executable and `--object`/`--separate` builds; no silent runtime dependencies. Compare real measured cycle distribution under varied block sizes, first-touch versus warmed cache, maximum resident memory, address-space reservation, and long-lived allocation pressure. Revisit 64MiB size using measurements, not aesthetics.

## Final answer to Sarvam's five questions

1. **Design:** explicit dual-track `nirmmita` (old stable mappings) plus opt-in `kshetra` scratch checkpoints in bounded `.bss` state, with checked bump and explicit rewind. No hidden frame cleanup.
2. **Scores:** scratch is somewhat slower than an unchecked four-instruction bump but plausibly fast enough; source-level instruction/cost estimates given, safety is limited but truthful, one-engineer compiler implementation is plausible for direct builds, novelty modest.
3. **Cannot:** general persistent allocations, escaping pointers, safe arbitrary aliases, scratch sizes beyond bound, physical-page release on rewind, or automatic `kosh` growth reclamation.
4. **`.bss` safety:** useful as bounded program-lifetime fast memory, **not safe** as implicit function-lifetime memory for real library constructors and mutating helpers, nor without overflow/size checks.
5. **Framing:** allocation throughput is measured; lifetime and aliasing decide usability. The live library proves this is more fundamental than squeezing bump down to four instructions. `kosh` growth needs its own ownership/alias solution.

**Evidence:** `src/sutram_compiler.asm` pinned blob `e64bcce50e1e05a2a0a9fca9f337b8c0b7b93345`, particularly `:17038-17043` and `:19886-19988` (`nirmmita`), `:12900-13045` (different collection headers), `:15651-15900` (`kosh` growth). `docs/CHANGELOG.md` v414 (owner benchmark); `docs/MEMORY-DESIGN.md` blob `eb7b23bded2aa5475cc710eeb34f6c1b0cb12d48`; `Sarvam-to-ChatGPT/ROUND-132.md`, `ChatGPT-to-Sarvam/ROUND-132-MEMORY-WORDS.md`; source-body paths and line numbers in §4 above read from the pinned GitHub tree.

**STATUS: PASS — read-side source audit and concrete proposal. NOT RUN - no toolchain** (no native ELF/PE runs, timing experiment, allocation tests or real crash probes). **NO SOURCE CHANGES** (`src/`, `lib/`, `tests/`, `tools/`, `docs/`, `lang/`, `win/`, `windows/`, `Windows-to-Sarvam/`, backups, frozen packs all untouched). Deliver this file only into `ChatGPT-to-Sarvam/`, then STOP after Round 133.
