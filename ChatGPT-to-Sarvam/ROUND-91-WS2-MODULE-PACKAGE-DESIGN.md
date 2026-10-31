# Sutram ROUND-91 WS2 — Real modules and local packages (one-page design)

**Status: DESIGN ONLY; not implemented.** Preserve Sanskrit keywords, the accepted `yoj module@alias` and `alias__function()` spelling, the handwritten NASM compiler and dependency-free output. Opt-in files use the existing R40 proposal `# sutram-module-v1`; `niryat` is **proposed** export syntax, **not** a current compiler keyword.

**Named module** — `lib/hisab.smlib` is module identity `hisab` within a canonical project root:

```sutram
# sutram-module-v1
niryat joda
prakriya joda(a, b) { prati a + b }
prakriya helper(x) { prati x + 1 }
```

**Consumer** — `main.sm`:

```sutram
# sutram-module-v1
yoj hisab@h
mukhya() { likha(h__joda(17, 25)) }
```

Default visibility is **private**: `h__helper` cannot be called externally. The alias `h` belongs to the import edge, not the module identity. Existing files **without the opt-in marker** retain current textual `yoj` semantics and goldens unchanged.

**Compile once.** Proposed CLI (not accepted today): `sutram --object lib/hisab.smlib -o .sutram/obj/hisab.smo`; then `sutram --link main.sm .sutram/obj/hisab.smo -o app.bin`. The same NASM compiler writes one versioned, bounded `.smo` containing source/interface digests, module identity, target ABI, private/public symbols, checked integer signatures, section offsets and `E8 rel32` call relocations. Link each unit once in deterministic dependency order, resolving symbols by **(canonical module ID, exact source name)**; only after all references are satisfied emit the usual standalone ELF or PE. Initially **reject module globals/initializers and cross-unit float/kosh ABI** instead of guessing. Do not add an end-user linker/runtime requirement.

**Local packages.** Proposed `sutram.package.json` in a user-owned project declares package name/version, module roots and explicit local dependency paths/content hashes. Resolve imports first relative to the importing file, then declared roots, with a unique-match rule. Canonicalize paths and fail closed on traversal, symlink escapes, duplicate/ambiguous names, unsupported metadata, cycles, private/missing symbols and arity mismatches. Three-color DFS detects cycles and deduplicates diamonds. A project-local `.sutram/obj` cache is keyed by source, transitive interface digests, compiler profile, feature flags and target; rebuild or fail on corruption. **No network registry, admin rights or ambient global caches.**

**Existing substrate, not acceptance:** `src/r71_module_link.inc` has a native bounded 64-byte export-record resolver and validated `rel32` patching but explicitly says production `.sm → .smo` emission is **not wired**. The current `src/sutram_compiler.asm` resolves calls in its local function table and writes `ET_EXEC`, not relocatable `ET_REL`. Real object emission and linking therefore need reviewed compiler changes; do **not** claim that changing only `yoj` makes separate compilation work. **STOP if it requires a broad compiler restructure** (Round-91 rule).

**Acceptance before FEATURE:** independently compile two `.sm` units and link one executable printing `42`; a diamond must compile its shared module only once. Validate private/missing/duplicate/arity/cycle/corrupt-object failures (exit nonzero, located diagnostic, no executable), cache invalidation, Linux and Windows output, old `yoj` goldens, fuzzing and the 227-case crash suite. **All new module execution tests: NOT_RUN.** Source basis: `compiler/MODULE_SYSTEM_R40_DESIGN.md`, `docs/rounds/R71-MODULES.md` and the R71 linker include.
