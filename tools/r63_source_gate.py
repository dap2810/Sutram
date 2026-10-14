#!/usr/bin/env python3
"""Structural R63 kosh review gate; NOT a replacement for compiling/running.

Executes offline with Python stdlib and fails if any critical code-generation
contract or additive fixture disappears. Native acceptance remains separate.
"""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPILER = (ROOT / "src" / "sutram_compiler.asm").read_text(encoding="utf-8")
HARNESS = ROOT / "tools" / "r63_kosh_acceptance.py"
TEST_DIR = ROOT / "tests" / "r63_check"


def require(label: str, passed: bool) -> None:
    if not passed:
        raise AssertionError("R63_SOURCE_FAIL " + label)
    print("R63_SOURCE_PASS " + label)


def main() -> None:
    ids = {
        "CLEAR": ("BN_KOSHCLEAR", "42", "bn_koshclear", "kosh_clear"),
        "EMPTY": ("BN_KOSHEMPTY", "43", "bn_koshempty", "kosh_empty"),
        "PEEK": ("BN_KOSHPEEK", "44", "bn_koshpeek", "kosh_peek"),
        "DEQUEUE": ("BN_KOSHDEQUEUE", "45", "bn_koshdequeue", "kosh_dequeue"),
    }
    for op, (symbol, number, label, literal) in ids.items():
        require(op + "_ID", re.search(r"^" + symbol + r"\s+equ\s+" + number + r"\b", COMPILER, re.M) is not None)
        require(op + "_NAME", label + ' db "' + literal + '"' in COMPILER)
        require(op + "_DISPATCH", re.search(r"cmp r12, " + symbol + r"\s+je \.ge_call_kosh", COMPILER) is not None)
    require("ENQUEUE_APPEND_ALIAS",
            'bn_koshenqueue db "kosh_enqueue"' in COMPILER and
            "dq bn_koshenqueue, TOK_BUILTIN, BN_KOSHPUSH" in COMPILER)
    require("VALID_ARITY_TABLE", all(x in COMPILER for x in (
        "db 1,1               ; 42 kosh_clear",
        "db 1,1               ; 43 kosh_empty",
        "db 1,1               ; 44 kosh_peek",
        "db 1,1               ; 45 kosh_dequeue",
        "r54_builtin_arity_ok:\n    cmp rdi, 45",
    )))
    require("TYPE_GUARDS",
            COMPILER.count("call is_kosh_var") >= 3 and
            "cmp qword [rbx+16], 1" in COMPILER)
    require("CLEAR_LENGTH_ONLY",
            "mov qword [rax-16],0" in COMPILER and
            "mov dil, 0xF0" in COMPILER)
    require("PEEK_DOES_NOT_WRITE_LENGTH",
            ".ge_koshpeek_only:" in COMPILER and
            "je .ge_koshpeek_only" in COMPILER and
            "jmp .ge_koshpop_load" in COMPILER)
    require("PEEK_FLOAT_TYPE",
            "cmp qword [rbx+8], BN_KOSHPEEK\n    jne .eif_no" in COMPILER)
    require("DEQUEUE_AFTER_EMPTY_GUARD", "je .ge_koshdequeue" in COMPILER and
            "call emit_kosh_empty_check_r9" in COMPILER)
    fifo = COMPILER.split(".ge_koshdequeue:", 1)[1].split(".ge_call_koshpush:", 1)[0]
    require("DEQUEUE_FIFO_COPY",
            all(x in fifo for x in ("mov rax,[r8]", "mov [r8-16],r9", "rep movsq", "0xFC", "0xF3", "0xA5")))
    require("EMPTY_ERROR_REUSED", "call emit_kosh_empty_check_r9" in COMPILER)
    for name in ("kosh_native_core", "kosh_native_float", "kosh_fifo_core", "kosh_fifo_float", "indic_danda_regression"):
        require("POSITIVE_" + name, all((TEST_DIR / (name + "." + ext)).is_file() for ext in ("sm", "out")))
    for name in ("kosh_invalid_non_kosh", "kosh_invalid_arity", "kosh_peek_empty", "kosh_dequeue_empty"):
        require("NEGATIVE_" + name, (TEST_DIR / (name + ".sm")).is_file())
    require("NATIVE_HARNESS", HARNESS.is_file())
    require("DANDA_REGRESSION",
            all(c in (TEST_DIR / "indic_danda_regression.sm").read_text(encoding="utf-8") for c in ("।", "॥")))
    print("R63_SOURCE_GATE_PASS (structural only; no native correctness claim)")


if __name__ == "__main__":
    main()
