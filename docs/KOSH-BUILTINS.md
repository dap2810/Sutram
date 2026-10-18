# Sutram — `kosh` compiler builtins: specification

**Status:** specification of the builtins as merged (R63) and verified by
execution against the compiler below. This is the user-facing spec. The
R63 implementation handoff (`docs/R63-KOSH-BUILTINS.md`) describes the
source-level implementation and its pre-execution claims; this document
states the behaviour as measured from real compiled programs.

**Verified against compiler:** `82b0a9f8fb2a6183b6f78ffdd8dec37ce4f5967c6bb3303e86cdecb41a421891`
(`sha256sum src/sutram_compiler.asm`), plus `tools/r63_kosh_acceptance.py`
(9 gates: 5 exact-output programs, 2 compile errors, 2 runtime traps).
R64 renamed the empty `peek`/`dequeue` diagnostics to their own
messages; this spec names all three accurately (R23 WS1 reconciliation).
The R21 spec text that said peek/dequeue share pop's diagnostic is
superseded — it was true of the R63 compiler, not of R64+.

## What `kosh` is

`kosh name[capacity]` declares a growable mala (Devanagari `कोश`);
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
feature. This is deliberately different from the library's `nighantu_rikta`,
which zeroes the nighantu's storage: `nighantu_rikta` closes a stale-segment hazard
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

### Empty `peek` / `dequeue` / `pop` — three distinct diagnostics, no ok-channel

Each of the three removal/peek builtins aborts on an empty `kosh` with
its **own** diagnostic (R64 renamed the `peek`/`dequeue` messages; in R63
all three printed pop's message):

```
empty kosh_pop(k):     Sutram Error: kosh pop from empty mala
empty kosh_peek(k):    Sutram Error: kosh peek from empty mala
empty kosh_dequeue(k): Sutram Error: kosh dequeue from empty mala
```

All three exit 1. There is **no** `ok[0]` channel here, unlike the
library's `chay_apanay`/`avali_nishkas`, which return `ok[0] = 0` on empty.
Code that must survive an empty `peek`/`dequeue` must check
`kosh_empty(k)` first (or `kosh_len(k) == 0`).

### Compile-time errors

- Non-kosh argument: `Sutram Error: kosh builtin requires a kosh variable`, exit 1.
- Wrong arity (e.g. `kosh_peek(v, 2)`, `kosh_enqueue(v)`): a parse error
  at the call site, exit 1. The builtins have fixed arity.

## `kosh` vs the library's `suchi` / `queue`

| | `kosh` (compiler builtin) | `suchi` (library, `lib/suchi.smlib`) | `queue` (library, `lib/suchi.smlib`) |
|---|---|---|---|
| Storage | compiler-managed growable mala | library qword-cell suchi | library ring buffer |
| Element type | integer **or** binary64 (`kosh dasham`) | integers (qword cells) only | integers (qword cells) only |
| Append | `kosh_push` / `kosh_enqueue` | `suchi_khip` / `chay_khip` | `avali_pravesh` |
| Remove last | `kosh_pop` (O(1), aborts if empty) | `chay_apanay` (ok-channel) | — |
| Remove first | `kosh_dequeue` (O(n) shift, aborts if empty) | — (use `suchi_apanay(l, 0)`, O(n)) | `avali_nishkas` (O(1), ok-channel) |
| Peek | `kosh_peek` (last; aborts if empty) | `chay_avalok` (ok-channel) | `avali_avalok` (ok-channel) |
| Clear | `kosh_clear` (length only, no erasure) | `suchi_rikta` (zeroes data cells) | `avali_rikta` (zeroes ring data) |
| Empty test | `kosh_empty` | `chay_rikta` / `suchi_maap(l) == 0` | `avali_shunya` |
| Sort / min / max / sum / count | — (none) | `suchi_shreni`, `suchi_laghu`, `suchi_adhik`, `suchi_yog`, `suchi_gan` | — (none) |
| Values flow into library functions? | **No** — no generic kosh parameter type | Yes | Yes |

Which to use: `kosh` for typed arrays — especially `dasham` — and when
compiler-managed growth is wanted. `suchi` for integer cell lists with the
library analytics (`suchi_shreni`, `suchi_laghu`, ...). `queue` for FIFO where
O(1) dequeue matters (`kosh_dequeue` is O(n)). For FIFO over integers
with survival on empty (ok-channel instead of abort), `queue` is the
right choice; for FIFO over floats, `kosh` is the only choice.
