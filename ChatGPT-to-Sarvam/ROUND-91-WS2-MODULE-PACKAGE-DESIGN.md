# Sutram ROUND-91 WS2 — Real modules and local packages (one-page design; NOT IMPLEMENTED)

**Decision:** Preserve the existing Sanskrit-keyword procedural grammar and the already working `yoj module@alias` qualified-call spelling. Add opt-in separately compiled modules, not another compiler and not a default behavior change. **This is a design only; no compiler edits.**

## Proposed surface syntax: name, export, use

A module is named by its canonical project-root-relative path, not by a caller-chosen alias. File `lib/hisab.smlib`:

```sutram
# sutram-module-v1
niryat joda
prakriya joda(a, b) { prati a + b }
prakriya double(x) { prati joda(x, x) }
```

A root file `main.sm`:

```sutram
# sutram-module-v1
yoj hisab@h
mukhya() { likha(h__joda(17, 25)) }
```

**Accepted today:** `yoj ...@alias` textual inclusion with `alias__name()` calls. **Proposed/new and currently NOT accepted:** the `# sutram-module-v1` marker switching to separate-object mode, and the `niryat` export declaration. `niryat` is an existing R40/R71 design proposal, **not a current compiler keyword**. Private by default: `double` may be called inside `hisab` but `h__double()` must fail outside. The importing alias `h` affects the caller spelling, **not module identity**. Preserve all legacy `yoj` behavior in files without the opt-in marker; never silently switch every library to new semantics.

## Compile each module ONCE, then link

Proposed developer commands (not existing CLI flags):

```sh
sutram --object lib/hisab.smlib -o .sutram/obj/hisab.smo
sutram --link main.sm .sutram/obj/hisab.smo -o app.bin
```

The **same handwritten NASM compiler** parses each unit and emits a versioned `.smo` relocatable object. Metadata contains magic/version, compiler/target ABI ID, source hash, canonical module ID, import interface digests, exported `name + arity + typed signature + visibility`, code/data offsets, and checked `rel32` call relocations. Include neither imported source text nor unresolved call placeholders in final output. The module's symbol key is **(canonical module ID, exact source symbol)**; do not stringify by lossy concatenation or confuse `a__b` with `a.b`. Initially allow function definitions and integer arguments/results only; **reject module globals, cross-module float/kosh records and implicit initializers** until ABI and lifetime semantics are separately approved.

The linker validates object boundaries and digests, resolves visible exported symbols, enforces signatures and duplicate/private/missing diagnostics, then emits the current fixed executable ELF or PE *after all relocations are satisfied*. Internal functions may be retained as private symbols without being exported. A module graph uses tri-color DFS and rejects cycles with a path; a diamond imports a unit only once. Build order is dependencies before users and then the root `mukhya`. Do not run an initializer merely because a module was imported; an explicit opt-in initializer ABI needs its own design.

## Local packages and safe resolution

A package is a **user-owned local project directory** with one manifest (proposed `sutram.package.json`: name/version, module roots, explicit local dependency paths and content/interface hashes). The compiler resolves `yoj name@alias` **relative to its importer**, then declared project roots; paths are canonicalized, refuse `..` traversal, duplicate identities, invalid UTF-8, symlinks escaping project roots, ambiguous matches and unexpected metadata. **No network registry, downloads, elevated privileges, global cache or background daemon.** Cache `.smo` only under a writable project-local `.sutram/obj/`; key by source bytes + imported interface digests + target + compiler/feature version. Fail closed or rebuild on stale/corrupt cache. End users receive a native executable and still need no toolchain.

## What exists and what blocks this today

- `src/r71_module_link.inc` already demonstrates a bounded **64-byte in-memory symbol record** with namespace, public flag and integer arity, plus validated `E8 rel32` patching. It explicitly says production `.sm -> .smo` is **NOT wired**.
- `src/sutram_compiler.asm:11821–11858` backpatches only internal function references, and `write_elf:23049–23125` emits **ET_EXEC, one program header, no section table**, not relocatable `ET_REL` with import/export symbols.
- Therefore adding only a `niryat` parser keyword or changing `yoj` strings **does not implement separate compilation**. A versioned object writer/reader and link-mode driver are new compiler subsystems. **STOP if their safe integration requires a broad compiler rewrite**, per R91's capability rule.

## Required acceptance before calling it a FEATURE

Two independent `.sm` units must emit two real `.smo` objects and link to a native program that prints `42`; the `hisab` source must be compiled exactly once even through a diamond. Private/missing/duplicate/arity and invalid-signature imports must fail with precise `Sutram Error` and no output image. Rebuild or invalidate the object when source, ABI, import interface, or target changes. Preserve existing `yoj` goldens; test Linux and Windows native builds separately, plus compiler fuzzing and the full 227-case robustness suite. **None of these new acceptance tests were run here; implementation status: DESIGN ONLY.**

**Prior basis:** `compiler/MODULE_SYSTEM_R40_DESIGN.md`, `docs/R71-MODULES.md` and `src/r71_module_link.inc`; this page is a bounded successor, not a duplicate working linker.
