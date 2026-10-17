# Library layers

Charter item 14 (one language with layered libraries): **core** (no OS
or allocator dependency) · **alloc** (needs a heap) · **std** (OS
services). This page marks every module in `lib/` with its layer and
the reason. The marker is machine-readable — each module's header
carries `# layer: core|alloc|std` — and `tools/check_layers.py`
verifies the claim: a core module must not call `nirmmita` and must
not import an alloc/std module; an alloc module must not import a
std module. A layer claim nobody can check is decoration.

```
$ python3 tools/check_layers.py
layers OK: 14 core, 9 alloc, 1 std
```

## The table

| Module | Layer | Reason |
|---|---|---|
| `array` | alloc | `mala_nava` allocates; every array is heap storage. |
| `baseconv` | alloc | Temp buffers (`nirmmita`) for digit reversal. |
| `bigint` | alloc | Temp buffers in `brihat_shesh` / `brihat_ghatmod`. |
| `chandas` | core | Pure arithmetic on caller values; no allocation, no imports. |
| `file` | std | Genuine OS services: `dvaram`/`paadh`/`likha`/`band` (open/read/write/close). The only module allowed to call OS builtins. |
| `fmt` | alloc | Temp buffers for digit reversal and `roop_varg_ank`. |
| `ganita` | core | Pure checked/saturating arithmetic; `ok` arrays are caller-provided. |
| `hash` | core | Pure FNV-1a arithmetic; no allocation. |
| `kalana` | core | Numerical methods on caller arrays; `kosh_len` only, no allocation. |
| `list` | alloc | `list_new` allocates. Imports `sort` (alloc). |
| `madhava` | core | Pure series arithmetic; no allocation, no imports. |
| `map` | alloc | Table allocation. Imports `hash` + `strb` (both core). |
| `math` | core | Pure arithmetic; no allocation, no imports. |
| `num` | core | Pure arithmetic; no allocation, no imports. |
| `samanvaya` | core | Pure arithmetic on caller arrays; `kosh_len` only. |
| `sankhyiki` | core | Statistics on caller arrays; `kosh_len` only. |
| `set` | alloc | Table allocation. Imports `map` (alloc) + `strb` (core). |
| `sort` | alloc | Merge-sort temp buffer. |
| `strb` | core | Byte-string ops on caller-provided buffers; no allocation. |
| `strconv` | alloc | Temp buffers for digit reversal. |
| `string` | core | Cell-array ops on caller-provided buffers; no allocation. |
| `result` | core | Result values on caller-provided cells; the checked producers reuse `out` as the `ok` cell, so no allocation. Imports `ganita` (core). |
| `serial` | core | Binary serialisation on caller-provided byte buffers; no allocation, no imports. |
| `util` | core | Pure arithmetic helpers; no allocation, no imports. |

## Dependency edges

Only four modules import anything (`ayojan` is textual inclusion, so
the import list is the complete dependency list):

- `list` → `sort` (alloc → alloc: allowed)
- `map` → `hash` (core), `strb` (core): alloc → core is downward, allowed
- `set` → `map` (alloc), `strb` (core): allowed
- `result` → `ganita` (core → core: allowed)

No core module imports an alloc or std module, so no core module
depends upward. The full import graph is acyclic.

## Why `std` was empty until R30, and what changed

The `0 std` result was investigated in R29, not assumed. The question was
whether some module that genuinely needs OS services is mis-marked
as `alloc`. The answer was no, for two checked reasons:

1. **No lib module called any OS-service builtin.**
   `tools/check_layers.py` enforces this: it fails if any core/alloc
   module calls `likha` / `likha_fmt` / `likh` (console output),
   `paadh` (console input), `band` (file handles), `dvaram` (open),
   or `netsock` / `netbind` / `netlisten` / `netaccept` (sockets).
   A module that starts calling one fails the checker until relabelled
   `std`. A module already marked `std` calling one is correct.
2. **The allocator is not an OS service.** `nirmmita` is implemented
   with `mmap` under the hood, but an `alloc` module needs *a* heap,
   not the OS: a freestanding heap would serve the same code. The
   charter's `std` layer means files, networking, threads — none of
   which any module touched. Likewise `kosh` growth (compiler-side,
   `mmap`-backed) is allocation, not an OS service.

R30 adds the first genuine `std` module, `file` (open/read/write/close
via `dvaram`/`paadh`/`likha`/`band`). The `0 std` kramgun became `1 std`
because a module now genuinely uses OS services — not because the
old classification was wrong.

## Notes

- `kosh_len` (used by `kalana`, `samanvaya`, `sankhyiki`) is a
  language builtin for array length, not an allocator or OS service;
  it does not change a module's layer.
- `nirmmita` is the allocator. A module that calls it — even only
  for a temporary buffer (`fmt`, `strconv`, `bigint`, `baseconv`) —
  is `alloc`, because it cannot run without a heap.
- The layer split is about *dependencies*, not importance: `ganita`
  is core and is the safety-critical module.
