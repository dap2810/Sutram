# Sutram — current memory observations and proposed ownership model

**Status: current-state inventory followed by an explicitly unimplemented
design. Sutram does not claim memory safety. No ownership feature is introduced
by this document.**

Snapshot: `dde0613ca16f3e41345b1b1055733151780ef9d7`.
Compiler Git blob: `64ea028a5ccf56117c132a7efd0673cbe2df3fc6`.
This addresses the charter's **memory/resource model** heading (item 11 in the
pinned 20-item charter, notwithstanding the older numbering in the brief).

## 1. What is established today

The [charter](sutram-design-parameters.html) says memory is manual, with no
ownership checking, borrow checking or enforced `unsafe` boundary. This is the
starting condition, not a promise that a few bounds checks fill those gaps.

Keep three things separate: compiler-host scratch storage, generated-program
storage, and library-managed representations. A compiler's bounded AST/token
buffers are not the program's heap and are not evidence of runtime safety.
Likewise, a library's `ok[0]` convention is error reporting, not a lifetime proof.

| Area | Inspected evidence / present behavior | Not established |
|---|---|---|
| Scalars and function calls | The compiler describes qword values, register/stack locations and generated frame restoration. | No complete language lifetime/alias contract follows from a register convention. |
| Indexed storage | The array fixture used by `set0` is mutated through a function argument and read by its caller. | No ownership transfer, exclusive borrow or copy-by-value collection guarantee. |
| Typed `kosh` parameters | The accepted example 120 rejects raw/integer `kosh` passed to `kosh dasham`. The push emission explicitly rejects growth on a kosh parameter. | This is not generic collection typing or complete alias safety. |
| `kosh` length/capacity | The inspected compiler uses logical length at pointer minus 16 and capacity at pointer minus 8; payload cells are qwords. | Treat those offsets as implementation observations, not a supported public ABI. |
| Growth | The inspected push path allocates a new capacity, copies existing cells and updates the named variable's pointer. | No reclamation of the old buffer appears in that path. Allocation failure and huge-capacity arithmetic are not certified here. |
| Clear/pop/dequeue | Clear only changes logical length. Pop/dequeue reduce length; dequeue copies remaining cells towards the front. | No destruction of resources stored in cells, secure erasure, automatic shrink or free is established. |
| Raw memory operations | The compiler contains raw read/write, fill/copy and allocation builtins, and `nishkriya` permits inline bytes. | No checked ownership, valid-address, object-provenance, alignment or race guarantee is established. |
| File and other handles | The language reference lists explicit handle operations such as `band`; allocation and I/O are distinct resources. | No automatic close on scope exit, return, error or abnormal termination is established. |

Evidence: [example 89](../examples/89_b9_short_circuit.sm) and its
[golden](../tests/expect/89_b9_short_circuit.out),
[example 120](../examples/120_t18_kosh_param_mismatch.sm) and its
[golden](../tests/expect/120_t18_kosh_param_mismatch.out),
[compiler](../src/sutram_compiler.asm) symbols `.ge_call_koshpush`,
`.ge_call_koshclear`, `.ge_koshdequeue`, and the existing
[kosh document](KOSH-BUILTINS.md). The source-level and test-level claims above
are deliberately not interchangeable.

## 2. Allocation and reclamation

In the inspected `kosh_push` growth path, new capacity is doubled or replaced
with the fallback capacity, a header-plus-payload size is computed, and
`emit_nirmmita_from_rax` is invoked. The generated code copies prior cells and
stores the new pointer into the variable. It does not emit a matching old-buffer
free in that inspected path. Repeated growth can therefore retain otherwise
unused allocations unless some independently verified mechanism reclaims them;
this review does not assert such a mechanism exists.

`kosh_clear` is **not free**. It returns zero and sets length to zero while
retaining capacity/storage. It is also **not erase**: old bytes can remain in the
allocation even when ordinary checked indexing no longer reaches them. Neither
pop nor FIFO shifting is a destructor for a resource whose numeric handle or
address is stored in an element.

The allocator's complete implementation and all OS shims were not audited in
this round. In particular, this document does not certify a malloc/free ABI,
allocation-failure recovery, zero-initialization of all allocation forms,
reallocation-in-place, final process cleanup semantics, or a general public free
operation. The absence of a free in one inspected growth path is narrower than
a proof that no reclamation occurs anywhere in the repository.

## 3. Lifetimes, aliases and invalidation

A pointer/value copy is not presently checked as an ownership transfer. A caller
can observe mutation through the array argument in example 89; it should not be
read as an exclusive borrowing guarantee. The growth-on-parameter rejection is
specifically motivated in the source by pointer replacement: replacing the
callee's pointer would not update the caller's pointer-by-value view.

That check does not establish that every other alias is updated when a local
kosh grows. Raw addresses into a collection must not be advertised as stable
across growth. Return values, escaping addresses into frames, aliasing across
collections and overlapping raw copies require separate characterization and
rules. The compiler source includes frame teardown; it is not evidence of
transitive heap cleanup or a resource destructor schedule.

There is no present concurrency memory model, happens-before rule, atomic
contract or shared-mutation discipline established by these tests. Socket
builtins and IDE event loops do not supply those guarantees.

## 4. What “undefined” means in this draft

This is not a C-style normative undefined-behavior specification. **Unspecified
by the current evidence** means callers cannot rely on the behavior as a
supported rule; it does not authorize optimizer assumptions that have never
been designed.

Unvalidated raw addresses, out-of-lifetime storage, wrong lengths for raw copy,
misaligned access, aliasing after reallocation, allocation failure and
concurrent access are not covered by a memory-safety promise. Existing array
bounds errors protect particular indexing paths, not arbitrary `pad`/`likh`
addresses or inline assembly. Whether an invalid operation aborts, corrupts
state, returns a value or is rejected requires an explicit test and future
contract; do not invent a guaranteed diagnostic for it.

## 5. Proposed ownership rules — DESIGN ONLY, NOT IMPLEMENTED

The following is a proposal for review, not the behavior of the pinned compiler.
It deliberately introduces no source syntax and no automatic claim of safety.

### 5.1 Owned resources

An owning value would carry responsibility for releasing one resource. Moving
that value would transfer that responsibility and invalidate the old owner for
ordinary use. Simple non-owning scalar values could be copyable; whether a
structure is copyable would depend on its fields, not on a raw bitwise-copy
shortcut. Containers owning resources would release their initialized elements
before releasing the backing allocation.

**Open decisions:** which existing pointer-like values migrate to owning types,
how foreign/raw addresses are represented, allocator identity, explicit release
versus implicit cleanup, and compatibility for legacy manual programs.

### 5.2 Shared and exclusive access

A shared borrow would allow observation without mutation through that borrow.
An exclusive borrow would permit mutation only while conflicting access is
prevented. Borrow lifetime could not outlive its owner. Reallocation or moving an
owner would be disallowed while a borrow into its storage remains live, or would
require a separately specified stable-handle design.

These are desired invariants, **not a Rust-equivalence claim**. The compiler
would need a concrete analysis for control-flow joins, loops, conditional moves,
function returns and nested data before the invariants could be advertised.

### 5.3 Cleanup and failures

A candidate rule is deterministic cleanup of fully initialized owned resources
on every normal scope exit, including return and early control flow. Partial
initialization would clean up only completed subobjects. A proposed reverse
construction order is a design choice to approve, not today's destructor order.
Recoverable errors must preserve ownership accounting and define whether a
failed operation consumes an input. Unrecoverable traps must have a separately
specified cleanup policy; do not assume unwinding exists.

Allocation failure needs an explicit result, optional value or fatal-policy
contract. The current `ok[0]` library convention can inform that design but is not
already a language result type or automatic propagation mechanism.

### 5.4 Unsafe and hardware boundaries

A future narrow unsafe boundary would make unchecked raw-address operations and
inline assembly obligations visible. It would not make an invalid operation
safe merely by spelling it `unsafe`. Preconditions must cover range, alignment,
initialization, aliasing, lifetime and machine effects. Converting back to a safe
reference would require those obligations to hold.

Volatile and atomic access would remain separate contracts: neither follows
from ownership alone. Interrupt handlers, shared device state and foreign code
would need explicit interaction rules before concurrent safety claims.

### 5.5 Incremental adoption

Before implementation, agree on a versioned migration path for manual arrays,
kosh aliases, raw builtins and library signatures. Preserve accepted legacy
semantics in a clearly named compatibility profile until changed behavior is
reviewed; do not silently reinterpret a copied raw integer as an owner. Separate
allocator-free core operations from owning containers and OS resources without
creating unrelated languages with incompatible type rules.

## 6. Evidence required before claiming the proposal works

The acceptance set must include valid borrowing/moving programs and invalid
programs rejected for use-after-move, escaping borrows, double release and
conflicting mutation. It must also cover partial initialization, cleanup order,
loop/control-flow joins, reallocations with live references, resource acquisition
failure, explicit raw boundaries and library interoperability.

Runtime tests need observable resource counters and failure injection, not only
successful output. Alias/fuzz cases and each advertised target must be tested.
A source annotation or a compiler pass named “borrow checker” is not the result.

**Verification limit:** current observations come from the cited fixtures and
inspected paths; no allocator leak measurement, full reclamation audit, ownership
implementation or Windows execution was performed in R70.
