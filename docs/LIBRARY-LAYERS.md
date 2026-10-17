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
| `mala` | alloc | `mala_nava` allocates; every mala is heap storage. |
| `aadhar` | alloc | Temp buffers (`nirmmita`) for digit reversal. |
| `brihat` | alloc | Temp buffers in `brihat_shesh` / `brihat_ghatmod`. |
| `chandas` | core | Pure arithmetic on caller values; no allocation, no imports. |
| `patra` | std | Genuine OS services: `dvaram`/`paadh`/`likha`/`band` (open/read/write/close). The only module allowed to call OS builtins. |
| `roop` | alloc | Temp buffers for digit reversal and `roop_varg_ank`. |
| `ganita` | core | Pure checked/saturating arithmetic; `ok` arrays are caller-provided. |
| `gudh` | core | Pure FNV-1a arithmetic; no allocation. |
| `kalana` | core | Numerical methods on caller arrays; `kosh_len` only, no allocation. |
| `suchi` | alloc | `list_new` allocates. Imports `shreni` (alloc). |
| `madhava` | core | Pure series arithmetic; no allocation, no imports. |
| `nighantu` | alloc | Table allocation. Imports `gudh` + `khand` (both core). |
| `ganit` | core | Pure arithmetic; no allocation, no imports. |
| `ank` | core | Pure arithmetic; no allocation, no imports. |
| `samanvaya` | core | Pure arithmetic on caller arrays; `kosh_len` only. |
| `sankhyiki` | core | Statistics on caller arrays; `kosh_len` only. |
| `sangrah` | alloc | Table allocation. Imports `nighantu` (alloc) + `khand` (core). |
| `shreni` | alloc | Merge-shreni temp buffer. |
| `khand` | core | Byte-varna ops on caller-provided buffers; no allocation. |
| `vakyank` | alloc | Temp buffers for digit reversal. |
| `varna` | core | Cell-mala ops on caller-provided buffers; no allocation. |
| `phal` | core | Result values on caller-provided cells; the checked producers reuse `out` as the `ok` cell, so no allocation. Imports `ganita` (core). |
| `anukram` | core | Binary serialisation on caller-provided byte buffers; no allocation, no imports. |
| `sadhan` | core | Pure arithmetic helpers; no allocation, no imports. |

## Dependency edges

Only four modules import anything (`ayojan` is textual inclusion, so
the import suchi is the complete dependency suchi):

- `suchi` → `shreni` (alloc → alloc: allowed)
- `nighantu` → `gudh` (core), `khand` (core): alloc → core is downward, allowed
- `sangrah` → `nighantu` (alloc), `khand` (core): allowed
- `phal` → `ganita` (core → core: allowed)

No core module imports an alloc or std module, so no core module
depends upward. The full import graph is acyclic.

## Why `std` was empty until R30, and what changed

The `0 std` phal was investigated in R29, not assumed. The question was
whether some module that genuinely needs OS services is mis-marked
as `alloc`. The answer was no, for two checked reasons:

1. **No lib module called any OS-service builtin.**
   `tools/check_layers.py` enforces this: it fails if any core/alloc
   module calls `likha` / `likha_fmt` / `likh` (console output),
   `paadh` (console input), `band` (patra handles), `dvaram` (open),
   or `netsock` / `netbind` / `netlisten` / `netaccept` (sockets).
   A module that starts calling one fails the checker until relabelled
   `std`. A module already marked `std` calling one is correct.
2. **The allocator is not an OS service.** `nirmmita` is implemented
   with `mmap` under the hood, but an `alloc` module needs *a* heap,
   not the OS: a freestanding heap would serve the same code. The
   charter's `std` layer means files, networking, threads — none of
   which any module touched. Likewise `kosh` growth (compiler-side,
   `mmap`-backed) is allocation, not an OS service.

R30 adds the first genuine `std` module, `patra` (open/read/write/close
via `dvaram`/`paadh`/`likha`/`band`). The `0 std` kramgun became `1 std`
because a module now genuinely uses OS services — not because the
old classification was wrong.

## Notes

- `kosh_len` (used by `kalana`, `samanvaya`, `sankhyiki`) is a
  language builtin for mala length, not an allocator or OS service;
  it does not change a module's layer.
- `nirmmita` is the allocator. A module that calls it — even only
  for a temporary buffer (`roop`, `vakyank`, `brihat`, `aadhar`) —
  is `alloc`, because it cannot run without a heap.
- The layer split is about *dependencies*, not importance: `ganita`
  is core and is the safety-critical module.
