# R73 WS3 — exact separate-compilation integration design, not an implementation

Current `yoj` is textual expansion: compiler `expand_imports` begins at **2513**; namespace-aware rewrite in that path uses `ns_*` state near **2614–2964**. `graph_preflight_v1` begins at **2263** and owns module graph validation. These are NOT independently linkable module objects.

Changes required in the existing one-file NASM compiler:
1. **Parser and interface extraction** at `parse_program` and `mg_parse_niryat` (source **3562**): define a versioned `SUO1` export record with Sanskrit module name, public symbol name, procedure arity/types and source module digest. Private `init` is local to a module and must never be exported.
2. **Code generation** at `gen_code`, `gen_all_functions` (function emission; look up labels in the exact reviewed core), and `r56_patch_global_storage` (**21078**): emit relocatable code/data for EACH .sm unit, not a full executable entry for every unit. Distinguish local calls from exported cross-unit calls and preserve typed ABI metadata.
3. **Linking**: add a native linker path in that compiler (not a Python substitute). Reuse previously reviewed R71 rel32 resolution primitives only after re-pinning/verifying their NASM ABI on current core. Link each module once, define single `mukhya` entry, reject duplicate public symbols and unresolved/nonpublic imports, and check arity/type compatibility.
4. **Resolution order**: local names in the current unit, then explicitly named `yoj` module exports in source order. Never resolve private exports via a global fallback. Reject ambiguities deterministically. Cycles and dependency graph details require a separate contract.

Proposed object record (DESIGN ONLY): magic `SUO1`, version, target triple, compiler source digest, module identifier, text/data blobs, export/interface table, relocations (section, offset, kind, target, addend). Reject unsupported versions and architecture; no network or package manager.

**Acceptance**: two actual source .sm units with same private `init`, public exports and a third `mukhya` root; compile units separately, link once and run. Negative cases private import, missing export, duplicate export and arity mismatch must fail. Confirm no textual re-inclusion. Test Linux and Windows as separate targets.

**NOT IMPLEMENTED:** SUO1 emission, module-unit driver, native link entry, actual .sm two-module program. The earlier 156-byte ELF that exits 42 used handcrafted fixture machine code, not Sutram-generated objects. This is a concrete design, not proof of separate compilation. Schedule this as a multi-stage project, not an ungrounded hours estimate.
