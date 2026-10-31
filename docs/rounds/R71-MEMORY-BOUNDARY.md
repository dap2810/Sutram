# Round 71 — explicit raw-operation boundary (experimental, opt-in)

**Sutram is not memory-safe.** This mechanism does not add ownership, borrowing,
automatic cleanup, allocation-failure handling, race prevention or pointer
validity. It is one visible and enforceable boundary for a defined operation set.
It follows the incremental, legacy-compatible direction in `MEMORY-MODEL.md`.

## Profile and syntax

The experimental canonical Sanskrit transliteration is:

```sm
mukhya() {
    vitti buf = nirmmita(64)
    asurakshit {
        likh8c(buf, 42, buf + 64)
        likha(pad8c(buf, buf + 64))
    }
}
```

Build the R71 entry with `SUTRAM_R71_UNSAFE_BOUNDARY=1`. The ordinary Round 69
release build still selects the accepted R68 diagnostic entry and preserves
legacy behavior. Existing libraries are not modified or implicitly trusted.
There are no new language-pack spellings for this experimental marker yet.

Inside this profile, raw operations must occur lexically inside a marked block.
The set is `likh`, `pad`, `likh8`, `pad8`, `likh8c`, `pad8c`, `smaran`,
`smaran_cp`, and inline `nishkriya`. The `*c` operations already take explicit
bounds in the inherited implementation; this profile also requires a boundary
for those raw-address operations. Supplied bounds do not establish lifetime or
ownership. The exact canonical token IDs are used, so a language-pack alias
for a listed operation does not evade the check.

The block may be nested inside ordinary blocks or another marked block. A
marker at top level, without its opening brace, or containing a procedure
definition is rejected. Calls to a procedure whose body has its own marked
block are not subject to a new interprocedural effect analysis. Allocation,
other builtins and arbitrary integer values do not become safe because they
are outside the listed set. This is not a general capability sandbox.

## Implementation

The existing lexer runs first, including the R68 source UTF-8 precheck. A new
compiler-host pass then validates all tokens without modifying them. It
checks a bounded brace stack (256) and the 65537-token capacity. On any pass
failure, the original token buffer is unchanged.

After validation, it expands each marker backwards into `yadi (1)` while
**retaining its original braces**. This deliberately avoids flattening a block
under an outer condition or loop. The existing parser/code generator handles
the resulting ordinary conditional. New tokens retain the marker's source
line and source pointer. This adds generated conditional overhead; no
zero-cost or performance claim is made.

The pass is in `src/r71_unsafe_tokens.vardh`; the existing-compiler hook and
source-located fatal diagnostic are in `src/r71_unsafe_integration.vardh`.
`src/r71_compiler_entry.asm` preserves the accepted R68 diagnostic hooks.
No existing compiler implementation or accepted golden is rewritten.

## Diagnostics

For an operation outside a marked block, the proposed integrated compiler emits:

```text
Sutram Error [E_UNSAFE_BOUNDARY]: <file>:<line>: unchecked operation requires asurakshit { ... }
```

Other marker/capacity/brace failures use:

```text
Sutram Error [E_UNSAFE_BOUNDARY]: <file>:<line>: malformed or unsupported asurakshit boundary
```

Both use the inherited R68 fatal-report path and exit 1. The file is the root
input and, after textual imports, the line can be an expanded-source line.
Original imported-file provenance is not implemented by this extension.
The exact wrapper-level diagnostic still requires the full native acceptance
run; the local machine-code tests validate the token-pass error codes instead.

## Evidence and remaining limits

22 local tests execute the actual token-pass instructions through a narrow
GNU-as test bridge. They cover all listed IDs, native-token aliases by ID,
nesting, brace retention, short identifier names, capacity, malformed markers,
read-only failure behavior and 200 seeded generated balanced inputs.

The full NASM compiler/profile, generated `.sm` positive/negative cases, Windows
host and R48 recovery interactions were **not executed** here. Source integration
and its exact emitted program behavior remain unaccepted until those tests run.
The delivered `tools/r71_native_acceptance.py` includes dedicated positive
controls and profile cases. Native helper results must not be relabeled as a
complete compiler pass or as memory-safety evidence.
