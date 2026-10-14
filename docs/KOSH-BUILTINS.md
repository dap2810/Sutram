# Sutram — `kosh` compiler builtins: specification

**Status:** specification of the builtins as merged (R63) and verified by
execution against the compiler below. This is the user-facing spec. The
R63 implementation handoff (`docs/R63-KOSH-BUILTINS.md`) describes the
source-level implementation and its pre-execution claims; this document
states the behaviour as measured from real compiled programs.

**Verified against compiler:** `f52a9ad78785faa8997356200f61e06e290725079229c897a6dc55bc5ccd621b`
(`sha256sum src/sutram_compiler.asm`), plus `tools/r63_kosh_acceptance.py`
(9 gates: 5 exact-output programs, 2 compile errors, 2 runtime traps).

## What `kosh` is

`kosh name[capacity]` declares a growable array (Devanagari `कोश`);
capacity is optional and defaults to 4. Logical length starts at 0 and
`a[index]` reads/writes against that length. Capacity doubles on growth.

Two element types exist:

| Declaration | Element type | Values |
|---|---|---|
| `kosh v` (default) | integer (qword) | integers |
| `kosh dasham d` | binary64 (`dasham`) | floats |

`push`/`pop`/the builtins below take a **direct kosh variable** — not an
expression, not a library-function parameter. Library functions cannot
take a generic `kosh` parameter (no generic kosh parameter type, no
overloading), which is why these operations are compiler builtins rather
than library functions.

## The builtins

| Builtin | Arguments | Returns | Return type |
|---|---|---|---|
| `kosh_push(k, v)` | kosh, value | new length | integer |
| `kosh_pop(k)` | kosh | last element, removed | element type (integer or binary64) |
| `kosh_len(k)` | kosh | logical length | integer |
| `kosh_cap(k)` | kosh | current capacity | integer |
| `kosh_clear(k)` | kosh | `0` | integer |
| `kosh_empty(k)` | kosh | `1` if length is zero, else `0` | integer |
| `kosh_peek(k)` | kosh | last element, **not** removed | element type (integer or binary64) |
| `kosh_enqueue(k, v)` | kosh, value | new length | integer |
| `kosh_dequeue(k)` | kosh | first (oldest) element, removed | element type (integer or binary64) |

Measured behaviour (real programs, this compiler):

```
kosh_empty(fresh)              -> 1
kosh_push(v, 10)               -> 1   (new length; 20 -> 2, 30 -> 3)
kosh_cap after 3 pushes        -> 4   (default capacity)
kosh_peek(v) after [10,20,30]  -> 30  (length still 3 — nothing removed)
kosh_enqueue(v, 40)            -> 4   (new length; alias of push)
kosh_dequeue(v)                -> 10  (oldest first — FIFO; length 3)
kosh_dequeue x3                -> 20, 30, 40 (FIFO order)
after draining: len 0, cap 4 (dequeue does not shrink capacity), empty 1
kosh_clear(empty)              -> 0; len 0, cap 4, empty 1
push 99 after clear            -> peek 99 (reuse works)
5 pushes -> len 5, cap 8 (grew 4 -> 8); kosh_clear -> 0, len 0, cap 8 (kept)
dasham: push 1.5, 2.5 -> peek 2.500000, dequeue 1.500000, peek 2.500000
dasham: kosh_enqueue(d, 9.5) -> 2 (new length); peek -> 9.500000
```

### `kosh_clear(k)` — length only, NOT erasure

`kosh_clear` sets the logical length to zero and returns `0`. It does
**not** change capacity and does **not** erase the storage cells: the old
values remain in the backing buffer, unreachable through the API because
all indexing is bounds-checked against the (now zero) length. Do **not**
assume cryptographic erasure — zeroing the storage would be a separate
feature. This is deliberately different from the library's `map_clear`,
which zeroes the map's storage: `map_clear` closes a stale-segment hazard
in a caller-held buffer, while a `kosh`'s storage is never directly
exposed to the caller.

### `kosh_peek(k)` — LIFO read without removal

Returns the last element without removing it. The kosh's length is
unchanged. There is no "peek front" builtin — the only front access is
`kosh_dequeue`.

### `kosh_enqueue(k, v)` — alias of `kosh_push`

Appends `v` and returns the new length, with exactly `kosh_push`'s
append/grow logic and typing rules. It exists so queue-shaped code reads
as a queue (`enqueue`/`dequeue`) while stack-shaped code reads as a stack
(`push`/`pop`) — same storage, two spellings.

### `kosh_dequeue(k)` — FIFO removal, O(n)

Removes and returns the **first (oldest)** element. Implementation shifts
the remaining elements one slot toward the front, so dequeue is **O(n)**
in the kosh's length. The trailing slot left by the shift is not erased
(same length-only semantics as `kosh_clear`).

### Empty `peek` / `dequeue` — diagnostic, no ok-channel

Both abort with the diagnostic (note: the message says "pop" even for
`dequeue` — that is the compiler's shared diagnostic text, not a
documentation error):

```
Sutram Error: kosh pop from empty array
exit 1
```

There is **no** `ok[0]` channel here, unlike the library's
`stack_pop`/`queue_dequeue`, which return `ok[0] = 0` on empty. Code that
must survive an empty `peek`/`dequeue` must check `kosh_empty(k)` first
(or `kosh_len(k) == 0`).

### Compile-time errors

- Non-kosh argument: `Sutram Error: kosh builtin requires a kosh variable`, exit 1.
- Wrong arity (e.g. `kosh_peek(v, 2)`, `kosh_enqueue(v)`): a parse error
  at the call site, exit 1. The builtins have fixed arity.

## `kosh` vs the library's `list` / `queue`

| | `kosh` (compiler builtin) | `list` (library, `lib/list.smlib`) | `queue` (library, `lib/list.smlib`) |
|---|---|---|---|
| Storage | compiler-managed growable array | library qword-cell list | library ring buffer |
| Element type | integer **or** binary64 (`kosh dasham`) | integers (qword cells) only | integers (qword cells) only |
| Append | `kosh_push` / `kosh_enqueue` | `list_push` / `stack_push` | `queue_enqueue` |
| Remove last | `kosh_pop` (O(1), aborts if empty) | `stack_pop` (ok-channel) | — |
| Remove first | `kosh_dequeue` (O(n) shift, aborts if empty) | — (use `list_remove_at(l, 0)`, O(n)) | `queue_dequeue` (O(1), ok-channel) |
| Peek | `kosh_peek` (last; aborts if empty) | `stack_peek` (ok-channel) | `queue_peek` (ok-channel) |
| Clear | `kosh_clear` (length only, no erasure) | `list_clear` (zeroes data cells) | `queue_clear` (zeroes ring data) |
| Empty test | `kosh_empty` | `stack_empty` / `list_len(l) == 0` | `queue_empty` |
| Sort / min / max / sum / count | — (none) | `list_sort`, `list_min`, `list_max`, `list_sum`, `list_count` | — (none) |
| Values flow into library functions? | **No** — no generic kosh parameter type | Yes | Yes |

Which to use: `kosh` for typed arrays — especially `dasham` — and when
compiler-managed growth is wanted. `list` for integer cell lists with the
library analytics (`list_sort`, `list_min`, ...). `queue` for FIFO where
O(1) dequeue matters (`kosh_dequeue` is O(n)). For FIFO over integers
with survival on empty (ok-channel instead of abort), `queue` is the
right choice; for FIFO over floats, `kosh` is the only choice.
