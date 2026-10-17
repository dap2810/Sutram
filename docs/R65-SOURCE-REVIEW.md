# Sutram Round 65 — source implementation and native review instructions

**Date:** 2026-10-15. **Base:** accepted `main` commit `45ba8518a9f82bd6b481ca286b7ba8f36e6bb4d0`. **Status:** source-level implementation only; **Sarvam must assemble and run**.

## Workstream 1: safe pre-emission peepholes

**1A — generated argument push/pop coalescing.** Under optional compiler-build define `-DSUTRAM_R65_PEEPHOLES=1`, the exactly-one-argument function-call path avoids generating the former `push rax` then `pop rdi` pair. It instead transfers the final argument from RAX into RDI directly (`mov rdi,rax`). Nested expression evaluation takes place before this transfer; the helper saves its compiler-time flag on the stack. Other argument counts remain on the original ABI path. This removes two stack-memory instructions, replacing them with one move; it can **increase encoded bytes by one**, so compare instruction count and native performance rather than assuming smaller binaries.

**1B — adjacent store/reload of the same scalar.** Under the same optional mode, a generic scalar assignment records that its written value remains in generated runtime RAX. The *immediately next* generic scalar assignment with a matching variable RHS can reuse RAX instead of reloading the just-written scalar. The token is consumed at the next statement entry, invalidated on all other paths, and reset at block entry/exit. Existing register fast paths, globals, branches, calls, arrays, and separate blocks are not directly rewritten. No emitted byte is deleted; all decisions occur before emission.

A literal `push REG; pop REG` with the **same** register was not identified as a safe reachable standalone pair. Removing arbitrary inline-assembly pushes/pops would be unsound. The new single-argument transfer is instead a conservatively scoped elimination of a known generated argument-stack round trip. Sarvam should reject this optimization if the native A/B shows ABI or stack-alignment differences.

**Do not claim machine-code instruction reductions until Sarvam disassembles and executes** `tests/r65_check/peephole_scalar.sm` before/after with `objdump`, including nested and typed-function argument cases.

## Workstream 2: opt-in integer runtime traps

The compiler-build flag `-DSUTRAM_R65_TRAP_INT=1` enables the new trap mode. **Without this flag the accepted compiler codegen is preserved**, including intentional signed wrapping, the existing R18 checked/saturating library, and R57/R58 optimizations. This is a compiler *build* mode, not a source-language/CLI option; document that distinction in any future installer/UI integration.

The opt-in mode avoids the R58 codegen folding, parser `fold_const`, R57 register-tree emitter, integer fast assignments/declarations and division-by-ghat-of-two shortcut. Checked generic integer instructions emit:

- `add/sub/imul`: `JNO` around a generated operation-specific fatal handler, executed only when OF is set.
- `idiv` and remainder: `test rcx,rcx; JNZ` around a zero-divisor fatal handler, before the instruction.
- The diagnostic prints `source:line` captured into the otherwise-unused AST_BINOP `+32` slot during parsing, followed by the operation; exits nonzero. The source root path is shortened to 95 trailing bytes when long to avoid unsafe short-jump literal encoding.

**Open correctness boundaries requiring Sarvam testing:** all parser operator paths, negative/unary expressions, compiler-generated literal string printing in the fatal path, PE64 runtime syscall translation, `INT64_MIN/-1` signed division overflow (not explicitly guarded), arithmetic in imported files (diagnostic uses root source path), and whether the parser-recorded `cur_line` is the exact operator line. The mode currently does not supply an ordinary `sutram --trap-int` CLI toggle. Do **not** merge until the native gates pass and these limits are accepted or fixed.

## Workstream 3: expanded Sanskrit pack

The original `lang/sanskrit.lang` already had 31 core keyword mappings including almost every name in Sarvam's list. Round 65 adds 18 existing-builtin aliases in Devanagari and fixes the original `सङ्ख्या` RHS typo to `sankhya` (it had been `sankshya`, which was not a recognised keyword). The prior codepoint-aware lexing and danda handling are untouched. `niryat` is not in the checked builtin/keyword table; no fictitious export keyword was added. See `docs/R65-DEVANAGARI-SURFACE.md` and `examples/219_sanskrit_kosh_aliases.sm`.

## Workstream 4: Windows installer security audit

`docs/R65-LEGACY-NSIS-VS-NATIVE-INSTALLER.md` documents exactly how old `windows/sutram-installer.nsi` requests UAC and writes HKLM/HKCR/system PATH, versus supported `windows/native-installer/install-core.ps1` per-user HKCU and LOCALAPPDATA. Neither installer was executed or modified.

## How Sarvam should test

On a proper Linux NASM host, **three separate compiler builds**:

```bash
nasm -f elf64 -I. src/sutram_compiler.asm -o /tmp/r65-default.o
ld -o /tmp/r65-default /tmp/r65-default.o
nasm -DSUTRAM_R65_PEEPHOLES=1 -f elf64 -I. src/sutram_compiler.asm -o /tmp/r65-opt.o
ld -o /tmp/r65-opt /tmp/r65-opt.o
nasm -DSUTRAM_R65_TRAP_INT=1 -f elf64 -I. src/sutram_compiler.asm -o /tmp/r65-trap.o
ld -o /tmp/r65-trap /tmp/r65-trap.o
python3 tools/r65_source_gate.py
python3 tools/r65_native_acceptance.py --default /tmp/r65-default --peephole /tmp/r65-opt --trap /tmp/r65-trap
```

For **default generated-code identity** also build the compiler from parent main `45ba8518a9f82bd6b481ca286b7ba8f36e6bb4d0` as a separate baseline and pass `--reference /path/to/parent/compiler`. Inspect actual disassembly, exact stdout and errors; include full accepted regression suite, language packs, module graph, proofs, historical frozen codegen, and actual Windows PE builds where feasible.

Do not alter accepted goldens or `lib/*.smlib`. Do not modify existing CI triggers; existing policy allows deliberate `workflow_dispatch` only. No credentials, new runtime network calls, HKLM writes or GUI palette changes are in this branch.

**This document reports source work, not proof of executable correctness.**
