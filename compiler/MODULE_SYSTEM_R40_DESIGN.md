# Sutram Module System v1 — Round 40 implementation and remaining design

## Status / non-negotiable distinction

**Implemented in the NASM source in this round:** a bounded multi-pass `ayojan`
expansion with a **single visited key table across passes**. This closes the
one-level import limitation and makes transitive diamond source definitions
available exactly once. The existing `ayojan module@alias` rename mechanism is
unchanged. Legacy `ayojan module` is unchanged when imports have no children.

**NOT implemented or claimed:** object-file separate compilation, private/export
visibility, explicit initializer semantics, cyclic-import rejection, provenance-
accurate file+line diagnostics, or module-cache reuse across translation units.
The new diamond golden **requires a NASM rebuild**. Do not merge it into a
release until Sarvam verifies the generated binary and other regressions.

## Language compatibility and proposed opt-in

Legacy source (`ayojan math`, old `.smlib` files) retains its single global
namespace and previous visibility. The new contract uses an opt-in marker in
both the root and module for export-controlled mode:

```
# sutram-module-v1
ayojan vectors@vec
mukhya() { likha(vec__length()) }
```

`lib/vectors.smlib`:

```
# sutram-module-v1
niryat length
prakriya length() { pratiyati helper() }
prakriya helper() { pratiyati 1 }
```

`niryat` (export) is proposed Sanskrit-oriented syntax; NOT yet a compiler
keyword. Only `vec__length()` is publicly visible; `vec__helper()` is private.
Unqualified legacy import rules remain unchanged. Modern unqualified imports
must reject duplicate exports rather than silently clobber. A qualified
alias must be unique within each importing module.

Avoid unreviewed dotted-call grammar: `alias__name` already works and does not
conflict with AST_FIELD, decimal literals or standard `ayojan` syntax.

## Resolver and cycle semantics

- Parse imports on logical source lines while excluding comments, quotes, and
  byte sequences resembling `ayojan` inside identifiers. Track original file,
  original line and the effective compilation mode. Validate names against
  the project-owned `lib` root; no traversal or privileged paths.
- A graph node is its canonical module identity (root + normalized module name),
  **not** an alias. Aliases belong to import edges and symbol references.
- Depth-first three-color traversal: unseen = 0, visiting = 1, emitted = 2.
  `visiting → visiting` is `E_MODULE_CYCLE` with `a -> b -> ... -> a` and
  the location of the back edge, rather than successful deduplication.
- A `complete` node is emitted once; diamond branches reuse it. This
  satisfies deterministic order: imported modules before importers, siblings
  left-to-right as written, main root last. For `a -> {b,c}`, `b -> d`,
  `c -> d`, order is `d,b,c,a`.
- Enforce bounded stack, module count and source/object sizes with explicit
  errors. Import path must always be printed with line and error kind:
  `examples/main.sm:12: Sutram Error [E_MODULE_MISSING]: ...`.
- Parsing a module's transitive imports must resolve paths against the
  canonical importing module path, not only the root source path.

**Known gap in this round:** the multi-pass importer is not the DFS above;
cyclic sources can currently collapse through the visited table without a
cycle error. The independent Python oracle tests the desired DFS contract,
NOT the live compiler. Do not call the compiler cycle-safe.

## Real separate compilation, native objects (not implemented)

The current compiler produces one final ELF or PE image from a single AST.
True separate compilation requires a new output form and relocatable linking
inside the *same handwritten NASM compiler*. Proposed versioned `.smo` layout:

| Region | Required fields |
|---|---|
| Header | 8-byte magic, version, source digest, module identity, target architecture, ABI ID, section bounds, checksum |
| TEXT | native machine-code bytes for exported and private functions |
| Symbols | stable names, section-relative offsets, visibility, type/arity/float ABI |
| Relocations | kind (rel32 call, abs64 data, RIP relative), section offset, target symbol/addend |
| Dependencies | canonical IDs + interface digests, rooted deterministic order |
| Initializers | optional named init symbol and idempotent execution guard |

Build/cache algorithm: compile a module once into `.smo` under a
**user-owned local project cache** (or process memory in cache-disabled mode),
read interface metadata on import, resolve external symbol relocations,
layout imported modules deterministically, apply checked relocations, link
into ELF/PE. Atomic temporary+rename writes; cache key includes source digest,
transitive interface digests, target, compiler version and feature flags.
Cache absence/corruption must rebuild or produce an explicit diagnostic, never
execute untrusted cache data. No global service, admin access, system writes,
external linker or third-party runtime for end users.

**Init semantics decision needed:** Current Sutram library grammar has
function definitions rather than arbitrary executable top-level statements.
Therefore a literal "top-level side effect runs once" assertion cannot be
honestly made for current modules. For v1 use an explicit `prakriya <module>__init`
(or future `prarambh` initializer) stored as initializer metadata, invoked
in topo order at most once before main. This is a proposed extension; no
automatic initializer calls exist in the current compiler.

## ABI and privacy implications

Keep the custom raw-qword Sutram `prakriya` calling convention byte-identical
across module links. IEEE-754 float must stay raw binary64, not integer
conversion; keep typed `kosh` parameter restrictions. Compile-time module
privacy means `private` symbols must not be resolved through a qualified or
unqualified import; linker symbol IDs must distinguish equal function names
in different modules. Check entry signatures before patching calls. Flag-off
or legacy mode cannot silently alter produced binaries.

## Review / acceptance sequence

1. Rebuild full Linux + PE32+ compiler. Run canonical 177 goldens plus new
   `163_r40_transitive_diamond` (target 178) and all 12 codegen gates.
   Check `17\n7\n` output and that only one `r40_shared` definition is emitted.
2. Compare output bytes and runtime of `126_numeric_pipeline` with the verified
   prior compiler. The added import pass should not alter the generated program
   on a shallow-import program; prove this, do not assume. Report min/p10.
3. Implement the full graph resolver in the NASM compiler with unique module
   identity, cycle back-edge diagnostics and file/line. Promote pending
   `tests/module_graph/pending` cases only when new NASM build passes them.
4. Add opt-in `niryat` parser and enforce explicit exports/private calls. Assert
   that colliding unqualified exports fail, aliases work, legacy source unchanged.
5. Introduce `.smo` emission and linkage; prove two independently compiled
   modules can be linked with no source-body import/inlining; validate cache
   invalidation, both targets, modules containing float/kosh functions.
6. Only after correctness, measure compile-time improvements and output size;
   report absolute before/after instead of projecting hypothetical gains.

## GUI acceptance (independent)

The Unicode GUI native-script highlighter was assembled/shape-verified by
Sarvam in R39 but **not visually tested on Windows**. Follow
`tests/gui/R40_NATIVE_SCRIPT_MANUAL.md`, record screenshots showing native
keywords blue only in code, not in comments/strings. Do not conflate a PE
header with actual Windows GUI success.
