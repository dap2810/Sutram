#!/bin/sh
# R68: the guard-page compiler used for the dynamic audit. Scratch build, never shipped.
# Every nirmmita block ends flush against a PROT_NONE page: one byte written or read past
# the block is SIGSEGV. nirmmita(0) -> 0 as today. Build from a copy of src/:
#   cp -r src W/src; cp evidence-r68/r68_efence.inc W/src/
#   in W/src/sutram_compiler.asm replace the three lines after `r38_nirm_seq:`
#     (call r65_active / test rax, rax / jnz r65_emit_nirm) with `jmp r68_emit_efence`
#     and add `%include "src/r68_efence.inc"` after the r65_arena include;
#   in W/src/r65_arena.inc make r65_active `xor eax, eax / ret` (no arena, no kosh extension).
#   cd W && ln -s <tree>/win win && ln -s <tree>/lib lib && ln -s <tree>/lang lang
#   nasm -f elf64 -I. src/r68_compiler_entry.asm -o ef.o && ld -o sutram_efence ef.o
# Then, in the tree:
#   SUTRAM_COMPILER=W/sutram_efence python3 tests/run_tests.py
#   python3 tools/proof_lib.py   --compiler W/sutram_efence
#   python3 tools/proof_props.py --compiler W/sutram_efence
