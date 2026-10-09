# R33: namespaced `ayojan` imports (proposed experimental language extension)

## Design and Sanskrit core

Plain `ayojan module` is **unchanged**. Namespaced form:

```sutram
ayojan r33_alpha@first
ayojan r33_beta@second
mukhya() {
    likha(first__clash())
    likha(second__clash())
}
```

The Sanskrit keyword `ayojan` (आयोजन/import) remains the primitive. The `@alias`
qualifier and `alias__function(...)` syntax reuse identifiers already accepted by
Sutram's parser: there is no new keyword, field operator, or runtime dependency.
This is explicit rather than implicit import precedence. The double underscore
is a generated-symbol separator, not an extra semantic namespace lookup.
A future dotted spelling `first.clash()` is deferred because `.` also denotes
Sutram float literals and field access; introducing it now could regress parsing.

## Isolation and compatibility

The importer reads the `.smlib` into a guarded scratch buffer, enumerates its
function declarations (ASCII `prakriya` or Devanagari `प्रक्रिया` as the first
non-whitespace token on a line), and rewrites ONLY the matching function-name
tokens followed by `(` to `alias__name`. This covers both declarations and
intra-module calls. Strings, `#` comments, and `//` comments are preserved.
Functions in one module therefore cannot collide with identically named
functions in another aliased module. Plain legacy import remains textually
expanded under the historic global names and is byte-compatible.

Aliasing the same module under multiple aliases is supported. Duplicate identical
imports are deduped by `module@alias`. The existing 16-import bounded table,
64-KiB expanded source, and 128-function compiler limits still apply.
Identifier names are bounded for the scanner (up to 63 UTF-8 bytes); aliases
must be ASCII identifiers of up to 31 bytes, module names up to 30 bytes.
Namespaced missing modules fail explicitly; legacy resolution remains unchanged.

**Important limitations:** this is a compile-time function namespace mechanism,
not a data/type namespace or a separately compiled module linker. It preserves
existing textual imports, file resolution and native program generation.
Declarations must be at the beginning of their own line (after indentation),
and the importer does not recursively expand `ayojan` directives from inside a
module; those are the same structural limitations as the earlier importer.
Do not treat qualified exports as private or secure boundaries.

## Build and acceptance on Sarvam's NASM runner

Build Linux/Win64 from the attached `src/sutram_compiler.asm`, not the packaged
stale executable. Run `python3 tests/run_tests.py`; target 168/168 if baseline
163 and five tests 149–153 are present. Then run:

```
python3 tools/module_namespace_ab.py /path/to/pre-r33-compiler ./sutram_compiler
```

The A/B script requires byte-identical generated native binaries for unchanged
legacy examples, plus the exact output for the two collisions and mixed imports.
It prints CPU-pinned min/p10 for the realistic pipeline; a namespace opt-in is
not allowed to penalize legacy code. Windows build must pass PE format checks
and eventually native Windows runtime testing; Linux IDE remains Linux-only.

## Rule for merging this package

The Sarvam Round-33 incoming ZIP could not be downloaded from Google Drive
(HTTP 403), despite read access to its handoff and metadata. This code is
therefore based on the last exact verified FG2+Stage1 release from R32.
**Merge only `src/sutram_compiler.asm`, `compiler/MODULE_NAMESPACES_R33.md`,
`examples/149–153`, `examples/lib/r33_*`, their `tests/expect` files, and
`tools/module_namespace_ab.py` into Sarvam's current Round-33 tree.** Preserve
all newer books, `ROADMAP.md`, documentation, IDE undo work, Windows installers,
and libraries from Sarvam. Do NOT replace them with older snapshots.
