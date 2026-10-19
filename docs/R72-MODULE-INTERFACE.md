# Round 72 — separate-compilation object/interface contract (design, not integrated)

**Gate 3 is NOT accepted.** Current canonical yoj is textual expansion. This branch does not add a second parser, non-NASM compiler, Python backend, or a fake compiled .sm object. Do not call raw assembly fixtures a Sutram object build.

## Proposed minimum versioned interface

An independently compiled source unit would have an explicit relative module identity (Sanskrit name), source SHA-256, target triple, object format version, code/data sizes, public/private symbol records and relocations. External names are pairs (module identity, Sanskrit identifier), NEVER concatenated unescaped strings. Every symbol records its byte length, the existing integer/dasham/kosh ABI signature or initially an intentionally restricted integer-only 0–6 arity, defined owner, and a validated code offset. Imported symbols must resolve uniquely to a niryat export; private/unresolved/duplicate/ABI-mismatched symbols all reject with source-located diagnostics. Imported units are compiled once, not textually pasted into the importer.

The version must be explicit and incompatible unknown versions fail closed. A hypothetical object magic and exact binary layout must not be silently frozen before the reviewer agrees to ABI, relocations, Unicode namespace spelling/normalization and initialization order. The old R71 in-memory 64-byte symbol helper is a tested substrate, NOT already a public on-disk ABI.

## Proposed resolution order

1. Resolve an unqualified name in the current compilation unit first.
2. Resolve a qualified name only through an explicit yoj module identity and niryat public symbol.
3. Select only an explicitly pinned relative module path under the project root; reject traversal, ambiguities, symlinks and ambient auto-discovery.
4. Validate arity, parameter kinds and return types *before* applying a call relocation.
5. Resolve every relocation; refuse executable publication if anything remains unresolved.

Private same-named procedures such as aarambh in module agni and aarambh in module soma must coexist. Duplicate public definitions within one module fail. No versioning, dependency cache, package manager, cross-target linking or full module graph implementation is claimed.

## Test required before Gate 3 can pass

Create two actual .sm units with private aarambh and distinct public niryat procedures, invoke the existing Sutram parser/code generator once per unit, produce two objects, validate namespaced imports and link them once into a runnable native executable. Prove outputs and negative tests for private/missing/duplicate/incompatible imports, record the emitted native bytes and toolchain. This has **NOT been implemented or run** in this round.

The earlier R71 experimental native rel32 relocation and export resolution helpers (draft PR #30) remain available as separately reviewed groundwork. They link hand-authored instruction fixtures, not compiled .sm units. Those files were not directly copied over the renamed v172 baseline because doing so alone would not implement separate compilation.
