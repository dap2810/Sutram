# Round 71 — separate compilation: design and tested linker substrate

## Status: partial implementation, not a working Sutram module system

`src/r71_module_link.inc` implements two native compiler/linker-host primitives.
There is no second parser or Python compiler. The existing pure-NASM Sutram
compiler is preserved. **The production `.sm` to object emitter, module driver,
import/export parser integration and complete native two-module Sutram build
are NOT implemented by this supplement.** Textual `ayojan` remains textual.

The implementation that exists is useful but narrower: resolve a qualified
symbol against a bounded export table, enforce its visibility and integer
arity, then patch a validated direct-call relocation in a native image. The
local tests link two independently specified machine-code fixtures, both named
`init` in different namespaces, and execute the resulting Linux ELF. It exits
42 (17 + 25). These fixtures are **not compiled Sutram module units**.

## Implemented contract

A symbol record is 64 bytes: namespace pointer/byte length, leaf-name
pointer/byte length, code offset, integer arity, public flag, owning-unit index.
The loader must have validated every referenced allocation before invoking the
routines. This in-memory record is not yet a supported on-disk `.smo` format.

`r71_resolve_export` searches at most 1024 records using exact namespace and
leaf-name bytes. It does not concatenate names, normalize Unicode, search the
filesystem or select the first duplicate. Namespace length is 1–63 bytes; leaf
length is 1–128; this prototype's arity is 0–6; visibility is exactly 0 or 1.
A duplicate matching qualified name is an error, including a private duplicate.
Private entries cannot satisfy a cross-unit import. A public entry must match
the requested arity. Code offsets must also pass relocation/image validation.

Returns EDX 0 on success; otherwise 1 unresolved, 2 private, 3 duplicate,
4 arity mismatch or 5 malformed metadata. These are **native API error codes**,
not already shipped CLI diagnostic strings. A production driver still needs
to turn them into source-located diagnostics.

`r71_patch_rel32` accepts only a displacement immediately following an `E8`
call opcode. It validates the displacement field and target within the image,
checks signed 32-bit reachability, and performs no write on rejection. It is
not an instruction decoder, global object validator or arbitrary relocation
engine. All object metadata must be validated before publishing an executable.

## Proposed minimum production implementation — not implemented

1. Reuse the existing parser/code generator once for each unit. Add an object
   output mode rather than re-parsing `.sm` in Python/C or inlining dependencies.
   Initially reject module globals/initializers and non-integer public interfaces
   until their initialization order and ABI are specified and tested.
2. Extract explicit `niryat` exports through the existing module-contract
   machinery. Default visibility is private. The native resolver's public bit
   must be derived from this check, not trusted from a user-controlled assertion.
3. Keep names as `(module identity, source name)` pairs. Emit namespace-qualified
   link symbols with an injective encoding. Two `init` procedures from different
   units must remain distinct. Internal calls remain local to the defining unit.
4. Record external calls as relocations and retain integer signatures. Do not
   silently accept arbitrary unresolved calls, waive prototype validation, or
   generate a no-op placeholder. A declared import must name an explicit export.
5. Resolve an import relative to the importing project and then explicitly
   supplied module roots, using a documented unique-match policy. Do not search
   the network or ambient package caches. The current helper itself receives
   an explicit table and implements **no filesystem resolution policy**.
6. Link each compiled unit once, check all unresolved/duplicate/private/signature
   failures, and preserve local relative references when laying out units.
   Publish only after validating the complete image and its entry point.

A standard relocatable object representation is preferable to an unversioned
ad-hoc cache. The actual file format and export metadata require a separately
reviewed writer/reader contract; this document does not freeze one prematurely.

## Why this is not reported as completed

The core changes would span prototype validation, `func_table`, `patch_list`,
`backpatch_calls`, global initializers and `write_elf`. The inspected compiler
already enforces prototype/body constraints and resolves calls before writing
an executable. Changing only symbol names would not implement separate
compilation and could silently change accepted programs. Those production
changes were not made in this delivery; the full compiler could not be built
in the available environment. No module compiler, cache or package manager is
claimed from the native helper tests.

Versioning, lockfiles, a dependency graph, transitive imports, dead-code removal,
separate global initialization, a public float/aggregate ABI, debug metadata
and Windows object linking are also unimplemented here.

## Reproduction

`python3 -m unittest discover -s tests/r71 -p 'test_linker.py' -v`

The test uses GNU as/GCC only as developer test infrastructure for the delivered
NASM instruction sequences. It is not a new shipping compiler backend. Native
Sutram object-emission/linking acceptance remains the next mandatory gate.
