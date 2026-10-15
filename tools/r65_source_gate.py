#!/usr/bin/env python3
"""Round 65 structural source gate. Not native compiler or execution evidence."""
from pathlib import Path
import re
ROOT = Path(__file__).resolve().parents[1]
s = (ROOT / "src" / "sutram_compiler.asm").read_text("utf-8")
pack = (ROOT / "lang" / "sanskrit.lang").read_text("utf-8")

def check(label, ok):
    if not ok:
        raise AssertionError("R65_SOURCE_FAIL " + label)
    print("R65_SOURCE_PASS " + label)

def main():
    check("TRAP_OFF_BY_DEFAULT",
          "SUTRAM_R65_TRAP_INT" in s and
          "SUTRAM_R65_TRAP_INT" not in (ROOT / "AGENTS.md").read_text("utf-8"))
    check("ALL_FIVE_INTEGER_TRAP_PATHS",
          all(f"lea rdi,[rel r65_msg_{v}]" in s
              for v in ("add", "sub", "mul", "div", "mod")))
    check("JNO_AFTER_ARITH",
          "r65_emit_overflow_guard:" in s and "mov dil,0x81" in s)
    check("JNZ_AFTER_DIVISOR_TEST",
          "r65_emit_zero_guard:" in s and
          "mov dil,0xC9" in s and "mov dil,0x85" in s)
    check("SOURCE_LINE_PARSER_METADATA",
          s.count("mov [rax+32],rcx          ; R65: parser-time BINOP source line") == 12)
    check("DEFAULT_FOLD_PRESERVED",
          "r58_fold_tree" in s and
          "%ifdef SUTRAM_R65_TRAP_INT\n    ; Parser literal folding" in s)
    check("ADJACENT_STORE_RELOAD",
          "r65_last_store_name" in s and
          ".r65_rhs_done:" in s)
    check("TRAP_MODE_GENERIC_ASSIGNMENT_REACHABLE",
          "%ifdef SUTRAM_R65_TRAP_INT\n    ; The optional safety mode bypasses all integer assignment fast paths." in s
          and "jmp .gs_assign_generic\n%endif\n.gs_assign_fast_done:" in s)
    check("TRAP_MODE_INTEGER_DECLARATION_GUARDED",
          "%ifndef SUTRAM_R65_TRAP_INT\n    mov rdi, rbx\n    call try_emit_int_decl_reg" in s)
    check("ONE_ARG_STACK_TRANSFER",
          ".r65_skip_arg_push:" in s and
          "cmp r14,1" in s and
          ".ge_fc_pop1:" in s)
    lines = [(x.split()[0], x.split()[1]) for x in pack.splitlines()
             if x.strip() and not x.lstrip().startswith("#")]
    builtin_ids = re.findall(r'bn_\w+\s+db "([^"]+)"', s)
    existing_ids = re.findall(r'kw_\w+\s+db "([^"]+)"', s)
    unmatched = [latin for dev, latin in lines
                 if latin not in builtin_ids and latin not in existing_ids
                 and latin != "to"]
    check("PACK_TARGETS_RECOGNIZED", not unmatched)
    check("PACK_18_NEW_BUILTINS",
          len([x for x in pack.splitlines() if x.strip() and
               not x.lstrip().startswith("#")]) == 49)
    check("PACK_WORD_BYTE_BOUND",
          all(len(dev.encode("utf-8")) < 64 for dev, latin in lines))
    check("NATIVE_FIXTURES",
          all((ROOT / "tests" / "r65_check" / (n + ".sm")).exists()
              for n in ("trap_add", "trap_sub", "trap_mul", "trap_div",
                        "trap_mod", "peephole_scalar", "overflow_safe")))
    check("LEGACY_DOC",
          (ROOT / "docs" / "R65-LEGACY-NSIS-VS-NATIVE-INSTALLER.md").exists())
    print("R65_SOURCE_GATE_PASS (NOT a NASM/native validation)")
if __name__ == "__main__":
    main()
