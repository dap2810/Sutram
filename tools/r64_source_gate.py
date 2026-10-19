#!/usr/bin/env python3
"""R64 structural gate: source inspection only, not native execution."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
src = (ROOT / "src" / "sutram_compiler.asm").read_text(encoding="utf-8")
previous = (ROOT / "tools" / "r63_kosh_acceptance.py").read_text(encoding="utf-8")
tests = ROOT / "tests" / "r64_check"

def check(label, cond):
    if not cond:
        raise AssertionError("R64_SOURCE_FAIL " + label)
    print("R64_SOURCE_PASS " + label)

def main():
    check("POP_UNCHANGED", 'msg_kosh_empty db "Sutram Error: rikta kosh se kosh_pop", 10, 0' in src)
    check("PEEK_TEXT", 'msg_kosh_peek_empty db "Sutram Error: rikta kosh se kosh_peek", 10, 0' in src)
    check("DEQUEUE_TEXT", 'msg_kosh_dequeue_empty db "Sutram Error: rikta kosh se kosh_dequeue", 10, 0' in src)
    helper = src.split("emit_kosh_empty_check_r9:", 1)[1].split(
        "\n; R46 compiler-time call liveness:", 1)[0]
    check("COMPILE_TIME_SELECTION",
          helper.index("cmp r12, BN_KOSHPEEK") <
          helper.index("cmp r12, BN_KOSHDEQUEUE") <
          helper.index("mov [rax+8], rcx"))
    check("POP_FALLBACK",
          "lea rcx, [rel msg_kosh_empty]" in helper and
          "jne .r64_not_peek" in helper and
          "jne .r64_message_selected" in helper)
    check("ONE_SHARED_RUNTIME_GUARD",
          src.count("call emit_kosh_empty_check_r9") == 1 and
          "cmp r12, BN_KOSHDEQUEUE\n    je .ge_koshdequeue" in src and
          "cmp r12, BN_KOSHPEEK\n    je .ge_koshpeek_only" in src)
    check("R63_RUNTIME_EXPECTATIONS_UPDATED",
          'b"rikta kosh se kosh_peek"' in previous and
          'b"rikta kosh se kosh_dequeue"' in previous)
    for name in ("kosh_pop_empty", "kosh_peek_empty", "kosh_dequeue_empty",
                 "kosh_nonempty", "default_compat"):
        check("FIXTURE_" + name, (tests / (name + ".sm")).is_file())
    check("EXPECTED_STDOUT",
          (tests / "kosh_nonempty.out").read_text() == "1\n2\n20\n2\n10\n20\n1\n" and
          (tests / "default_compat.out").read_text() == "42\n")
    check("NATIVE_RUNNER", (ROOT / "tools" / "r64_kosh_diagnostic_acceptance.py").is_file())
    print("R64_SOURCE_GATE_PASS (NOT native evidence)")

if __name__ == "__main__":
    main()
