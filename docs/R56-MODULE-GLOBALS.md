# Sutram R56: module-level `vitti` globals (review candidate)

**Scope:** integer/raw-qword scalar module variables. Produced by the single NASM compiler (`src/sutram_compiler.asm`). No separate runtime, object format, interpreter, or second production compiler.

## Syntax and ordering

```sutram
vitti counter = 3
vitti doubled = counter * 2
vitti unset
prakriya add_two() {
    counter += 2
    prati counter
}
mukhya() {
    likha(add_two())
    likha(doubled)
    likha(unset)
}
```

This outputs `5\n6\n0\n` in the native Linux test environment.

- The declarations must appear **before `mukhya`**, outside functions. A `vitti` after the `mukhya` body is an error, never a silently omitted initializer. Declarations inside a function and inside `mukhya` remain locals.
- At most 128 module-global scalar declarations per compiled program. Duplicate global names reject compilation. Top-level `vitti name[N]` arrays are deliberately unsupported in this round. Dynamic pointers produced by `nirmmita` can be stored in scalar globals and indexed.
- All global slots begin at zero. An initializer is optional. Explicit initializer expressions execute **once**, in declaration order, at entry before the body of `mukhya`. They can read earlier globals, perform ordinary expression operations, and invoke user-defined functions. Referencing a later-declared global before its initializer sees its default zero; this is a consequence of the zeroed slots and ordered initialization, not a dependency sorter.
- Every function reads and writes the **same** global storage. Recursive calls do not reset it. A parameter or an already-declared local with the same spelling shadows a global inside that scope; the global remains intact. This is resolved at compile time against the existing local variable table before searching the separate global names.
- Module inclusion `ayojan` remains textual in this compiler. Globals belong to the resulting compiled translation unit; module export/alias visibility of globals is **not** separately established by these fixtures.

## Implementation details and data placement

- Compiler memory: `r56_global_names` and `r56_global_nodes` are separate from per-function `var_table`; `r56_patches` stores bounded code-relative relocation requests for accesses.
- Compiler emits `mov rax,[rip+disp32]` and `mov [rip+disp32],rax` for qword reads/writes. Relocations are resolved against the final code length after function-call backpatching. No runtime name resolution is required.
- ELF: globals are zeroed qwords appended to the existing mapped, writable load segment. Existing ELF segment permissions are not changed by this round; the original image format already uses a single RWX load segment, which should be separately hardened in a future project-wide image-layout round.
- PE: globals occupy a separate zero-filled, **RW, non-executable** `.data` section. Existing text section keeps its original read/execute flags. RIP displacements target the `.data` RVA, verified by static image analysis. PE generated image structure is checked on Linux; this is **not Windows execution acceptance**.
- Global references are resolved before the generic code generator's local auto-allocation and register fast paths. Integer compound updates, for induction, pointer indexing/fields, named-variable helpers, and expression/statement access use shared global storage.
- Programs with **no** top-level global retain the established generation path. R46 four standard binaries remain byte-identical; legacy expected outputs were not edited.

## Native evidence

The controlled GitHub workflow `.github/workflows/r56-native.yml` builds the NASM compiler, compiles and executes the ten positive Linux fixtures, rejects four invalid fixtures without producing an executable, statically inspects PE headers/RIP displacements, runs accepted R55/R54/R48-R52 checks and the original 186/12/30/18 compatibility matrix. Real stdout is retained in `ChatGPT-to-Sarvam/ROUND-56-OBSERVED.txt` and exact source hashes in `ROUND-56-SHA256.txt`.

## Limits / independent review

- **No Windows native runtime execution** in R56. Raw-pointer bounds remain caller-managed.
- Top-level arrays are rejected; other types of module-global variable, separate compilation, runtime inter-module linkage, and module-specific export visibility remain out of scope.
- Local shadowing is **scope-table-based**: it applies to parameters and local variables registered before the access, matching the existing Sutram declaration behavior. Separate lexical-block shadow trees are not introduced.
- ELF's current RWX segment is preserved to avoid a byte-format change for ordinary code; this is not a claim that RWX is an ideal executable layout.
- These fixtures and checks are concrete evidence of supported shapes, not a formal proof of arbitrary expression and error recovery combinations.
- Do not merge before Sarvam independently checks the full PR diff, source SHA manifest and regressions.
