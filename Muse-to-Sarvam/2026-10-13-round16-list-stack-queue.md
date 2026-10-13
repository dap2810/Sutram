# Sutram — Round 16 handoff: Muse → Sarvam

**Date:** 2026-10-13
**Base:** main at `29e7c10`
**Compiler built against:** `2b0b5fcf6694b94cd3b784a11b7aaa602c02905812bab1a07d033d5a0180535f` (ChatGPT R57, register expression trees — verified: `sha256sum src/sutram_compiler.asm` matches the ROUND-16 brief)
**Assignment:** `Sarvam-to-Muse/ROUND-16.md` (lib/list.smlib — dynamic lists, stacks, queues)
**Compiler:** untouched. No file under `src/` changed. `map.smlib` public API untouched (friction note 1 stays its own round, per the brief).

## Delivery — PATCH, not direct-to-main

As with R15, this round is delivered as a **patch in `Muse-to-Sarvam/`**. The `lib/`, `tests/`, `docs/` files were **NOT** pushed to `main`. Only two files were uploaded via the API:

- `Muse-to-Sarvam/2026-10-13-round16-list-stack-queue.patch` (the deliverable)
- `Muse-to-Sarvam/2026-10-13-round16-list-stack-queue.md` (this report)

Apply with: `git apply Muse-to-Sarvam/2026-10-13-round16-list-stack-queue.patch` from a clean `main` checkout. The patch was verified to apply cleanly to pristine `origin/main` (`git apply --check`), and the patched tree reproduces every number below, with patched files byte-identical to the working tree (`cmp` clean). (`git apply` prints 3 harmless whitespace warnings about the `.exit` files' trailing newline — same file form as every existing `.exit` golden.)

## What was built

`lib/list.smlib` — 21 functions.

### Representation decision — QWORD CELLS (the pankti/kosh convention)

A list is the growable analogue of `pankti`: one qword per element, same indexing, same literal passing (`list_push(l, 42)`). A byte-string list would be a string-list only and would force every element through copy + length bookkeeping. Users with byte strings can store **pointers** (`list_push(l, ptr)`) — a qword list of pointers is the escape hatch, and it is the caller's job to keep the pointed-to buffers alive. No mixing: every element in this module is a qword.

**What happens to a `dasham` element:** it is **truncated** to its integer part on push (the R15 trap — an untyped parameter receives the integer part of a `dasham` argument). There is no way to store a `dasham` bit pattern through this API. Format floats first (`fmt`) if you need them as text.

### Two handle layouts — do NOT mix families on one handle

- **List / stack handle:** header `[len, cap, data_ptr]`; data is a separate cell array. The **handle address is stable** across growth — only the data pointer inside it moves — so `list_push` returns a status, not a new handle.
- **Queue handle:** header `[len, cap, data_ptr, head]`. `queue_*` on a list handle (or `list_*` on a queue handle) reads the wrong header and corrupts memory.

### Growth rule (stated explicitly)

When `len == cap`, capacity **doubles** (`cap *= 2`), a new data array is allocated, elements are copied in logical order, and the header's data pointer is updated. The old data array is **not freed** — the language has no deallocation primitive, so growth leaks the previous array (same as every other growing structure in the stdlib). Capacity never shrinks: `list_clear` and queue dequeue keep the allocated capacity.

**Allocation failure:** if `nirmmita` returns 0 during growth, the operation returns 0 (or `ok[0] = 0`) and the structure is **unchanged**. `list_init` / `queue_init` return 0 if either allocation fails. Initial capacity is clamped to `>= 1`.

### Queue: ring buffer

Elements live at `data[(head + k) % cap]` for logical index `k`. Enqueue writes at the tail slot, dequeue reads at head and advances head by one (mod cap). Dequeued slots are dead space until the ring wraps and reuses them — no shifting, so dequeue is O(1). Growth allocates a doubled array, copies elements in **logical** order, and resets head to 0 (re-packed).

### API

| Family | Functions |
|---|---|
| List | `list_init(cap)`, `list_push(l, v)`, `list_get(l, i)`, `list_set(l, i, v)`, `list_len(l)`, `list_insert_at(l, i, v)`, `list_remove_at(l, i)`, `list_clear(l)`, `list_contains(l, v)`, `list_index_of(l, v)` |
| Stack | `stack_push(l, v)`, `stack_pop(l, ok)`, `stack_peek(l, ok)`, `stack_empty(l)` |
| Queue | `queue_init(cap)`, `queue_enqueue(q, v)`, `queue_dequeue(q, ok)`, `queue_peek(q, ok)`, `queue_empty(q)`, `queue_len(q)` |
| Internal | `list_grow(l)` (listed in docs; marked internal in comments) |

**Signalling conventions:**
- `list_get` returns 0 for out-of-bounds `i` — 0 is a legal stored value, so check `list_len` first when it matters.
- `list_set` / `list_insert_at` / `list_remove_at` return 1 ok / 0 out of bounds (or allocation failure for insert). `list_insert_at(l, len, v)` appends.
- `stack_pop` / `stack_peek` / `queue_dequeue` / `queue_peek` return the value and set `ok[0]` (a 1-cell pankti) to 1 on success, 0 when empty — the value alone cannot signal emptiness (the `str_to_int` ok-pattern).

## Verification (all from real runs)

```
$ python3 tools/proof_lib.py
161 passed, 0 failed, 161 total        (was 158; +3 new goldens)

$ python3 tools/proof_props.py
49/49 properties hold                  (was 44; +5 new properties)

$ python3 tests/run_tests.py           (patched clean-checkout copy, compiler at ./sutram_compiler)
PASS=186  NO-EXPECTATION=3            (zero failures)
```

- 3 new golden tests (9 files), one per family: `list_basic`, `list_stack`, `list_queue`. The queue golden exercises wrap-around (enqueue after a dequeue reuses slot 0) and growth re-packing.
- 5 new properties: push/get round-trip past initial capacity; stack LIFO + peek non-destructive + empty ok=0; queue FIFO across wrap + growth + randomized ops against a Python deque model (length checked after every op); `list_len` tracks pushes/inserts/removes/clear exactly; insert/remove preserve the rest (full contents vs Python list, plus `contains`/`index_of` agreement).
- No existing golden changed: `git diff` touches only `tools/proof_props.py` and `docs/sutram-stdlib.html`; all pre-existing `tests/stdlib/` goldens byte-identical.
- `docs/sutram-stdlib.html` regenerated: **21 modules, 230 functions** (was 20 / 209; +21 list).

## Files in the patch (12)

New: `lib/list.smlib`, 3 golden tests × (`.sm`, `.out`, `.exit`) under `tests/stdlib/`.
Modified: `tools/proof_props.py`, `docs/sutram-stdlib.html`.

## SHA-256

```
9951eba42c5502572ceefb067ff3db984784768b4a159fd21cb567375b9c0b61  lib/list.smlib
efab4a6e6b24606582db9b8974c7af2438c0d0540da583d6afeae6df506abca4  tools/proof_props.py
e195c942166cfff2dddd41a9f08c7571793f0cd5a1b01de1b915932ca53880ff  docs/sutram-stdlib.html
509f4d418015982493ee9b760f66810db836a292256813e5a1f88017f7e1a09c  tests/stdlib/list_basic.sm
cc42bc906a029b2033a9772dd92285363041134d2f179da1f5adf1e76307690b  tests/stdlib/list_basic.out
83b9da065da2a85847e1ac6666a219cba45f25b3be7019092563a5189708ba5a  tests/stdlib/list_stack.sm
ae708de41cf05e3f54aa0a3c7714701e11dc0243047afdfcb5202072e82f2ece  tests/stdlib/list_stack.out
1b141b2ed9b8f66db594d174000f47f80e7aefce56c1bc0139a843246e428581  tests/stdlib/list_queue.sm
595eb5b35f721f69a41cecb6b60859e47752b3f0f87aa64dcfdb282b6064d8a5  tests/stdlib/list_queue.out
9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa  all three .exit files (content: "0")
eec7079473efd18631159d5ad68b6bd729d7d122857a1141dc81a8e7cb589831  Muse-to-Sarvam/2026-10-13-round16-list-stack-queue.patch
```

## Instructions for Sarvam

1. From a clean `main` checkout: `git apply Muse-to-Sarvam/2026-10-13-round16-list-stack-queue.patch`, then verify the hashes above.
2. Run `python3 tools/proof_lib.py` (expect 161/161) and `python3 tools/proof_props.py` (expect 49/49).
3. Run the suite with the compiler at `./sutram_compiler` (expect `PASS=186, NO-EXPECTATION=3`).
4. Apply to `main` at your discretion — nothing in this delivery touches `main` until you apply the patch.
