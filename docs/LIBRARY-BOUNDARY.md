# The library's honest boundary

One page on what the Sutram standard library (`lib/`, 24 modules, 303
functions) deliberately does **not** do, with the reason for each. A
stated boundary is worth more than a longer function list. This page is
the R27 answer; R28 extends it with the layer markers that enforce the
core/alloc split; R29 adds the `Result` type and serialisation; R30
adds the first `std` module (`file` — the file-I/O entry below now
points at it instead of claiming the library has none).

## Deliberately not in the library

- **File I/O (beyond `file`).** `lib/file.smlib` (R30, layer `std`)
  provides exactly three functions — `patra_path_sarv`,
  `patra_likh_sarv`, `patra_asti` — over the `dvaram`/`paadh`/`likha`/
  `band` builtins. Everything else (directories, permissions, seek,
  append, stat, locking) is still deliberately absent: the core
  library is pure and freestanding where there is no filesystem
  (charter item 13), and a file API belongs to the OS-specific
  `std` layer, not the core library. (File I/O via `lib/fileio.smlib` was deleted
  in R1 for exactly this reason: it was a trivial rename of the
  builtins. The R30 `file` module is not a rename — it adds the
  open/read-loop/close and open/write-loop/close compositions with
  a uniform -1 error contract.)
- **Networking.** No sockets, no HTTP, no DNS. Reason: same as file
  I/O — no OS, no network stack assumed. (A set of socket builtins
  exists in the compiler and is under audit; it is not a library
  surface and may be retired.)
- **Time and clocks.** No "now", no sleep, no timers, no dates.
  Reason: no clock assumed; time is an OS service. The one
  time-adjacent module, `kalana`, is numerical methods (integration,
  slopes, polynomials), not a clock.
- **Threading and concurrency.** No threads, locks, channels, or
  atomics. Reason: the language has no concurrency model yet
  (charter item 06, not started). A library cannot provide safe
  concurrency the language cannot express.
- **Processes and environment.** No spawning, no exit codes beyond
  `pratiyati`, no environment variables, no command-line arguments.
  Reason: no OS assumed; process semantics belong to the host.
- **FFI / calling foreign code.** No C interop, no dynamic loading.
  Reason: there is no FFI yet (charter item 19, not started). The
  library is self-contained by design.
- **GUI and windowing.** No windows, events, or drawing. Reason: the
  IDE has its own X11 event loop, but the language has no event or
  async facility (charter item 07, not started).
- **Hardware access.** No ports, interrupts, or device registers.
  Reason: that is compiler-level (`nishkriya` inline assembly) and
  board-specific, not library code.
- **Garbage collection / ownership.** No GC, no borrow checker, no
  RAII. Reason: memory is manual (charter item 11, not started).
  The library does not claim memory safety and must not until the
  model exists and is tested.
- **Randomness with entropy.** No true randomness, no OS entropy
  source. Reason: no OS assumed. `ganit_yadricch` (R26) is a deterministic
  PRNG with a caller-owned seed — honest about what it is.
- **Exceptions / panics.** No throw/catch, no stack unwinding.
  Reason: errors are values. The `ok` out-parameter convention
  and the `Result` type (see `docs/ERROR-CONVENTION.md`, R29)
  are the error model; there is no propagation operator and no
  exhaustiveness checking yet (charter item 12, partial).
- **Generics, closures, methods, traits.** No first-class functions,
  no generic collections, no methods. Reason: the language does not
  have them yet (charter items 02–04). Every collection in `lib/` is
  written against one concrete cell type. Higher-order operations
  (`list_map`, `list_filter`) are impossible without callbacks and
  are not faked with macros.

## What the library does *not* promise (R28 extension)

Beyond the missing features above, the library does not claim:

- **Memory safety.** Memory is manual; there is no ownership, no
  borrow checking, and no unsafe boundary (charter item 11, not
  started). A program that frees or dvigun-uses storage is a caller
  bug the library cannot catch. The `kosh` growth path retains
  superseded buffers (a compiler-side leak, verified in R29;
  see `MEMORY-MODEL.md` §7 and `tools/test_kosh_growth_leak.py`).
- **A result type.** Errors are the `ok` out-parameter convention
  and, since R29, the `Result` value (see
  `docs/ERROR-CONVENTION.md`). Nothing forces the caller to check
  `ok[0]` or `phal_asti_siddhi` — there is no exhaustiveness checking.
- **Formal type contracts.** Integer sizes, conversions, overflow,
  and comparison are defined in `docs/NUMERIC-CONTRACT.md` and
  pinned by tests, but there is no formal type-contract system in
  the compiler (charter item 10, partial).
- **A formal specification.** Behaviour is defined in these docs
  and pinned by the proof suites, but there is no formal written
  specification yet (charter item 20, partial).

## Layers (R28 extension, R29 resolution)

The library is split into **core** (no allocator, no OS),
**alloc** (needs a heap), and **std** (OS services — since R30, one
module: `file`, genuinely using the file builtins; the layer checker
enforces that no core/alloc module calls any OS-service builtin).
Each module's header carries a machine-readable `# layer:` marker, and
`tools/check_layers.py` verifies that no core module depends
upward. See `docs/LIBRARY-LAYERS.md` for the per-module table.

Pure computation over values the caller provides: containers (`map`,
`set`, `list`, `queue`, `stack`), text and bytes (`string`, `strb`,
`str`), numbers (`math`, `ganita`, `bigint`, `strconv`, `baseconv`,
`fmt`, `sankhyiki`, `kalana`), hashing (`hash`), sorting (`sort`),
serialisation (`serial`, R29), the `Result` type (`result`, R29),
and the safety net (`ganita_checked_*`, `ganita_sat_*`). Everything
in `lib/` runs on plain arithmetic and explicit caller-provided
storage; the layer split (core vs alloc) is marked per module in
`docs/LIBRARY-LAYERS.md` (R28).

## The rule

A feature is added to the library only when the language can express
it honestly and the layer it belongs to is clear. Everything else is
a stated boundary, not a missing feature to be padded in.
