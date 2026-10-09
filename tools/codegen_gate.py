#!/usr/bin/env python3
"""Generated-code regression gate for Sutram hot integer forms.

This is intentionally outside the compiler/runtime path.  It compiles tiny marked
programs, slices the raw emitted bytes between nishkriya sentinels, asks objdump
to decode that raw slice, and enforces instruction-count ceilings.

Usage: python3 tools/codegen_gate.py
       SUTRAM_COMPILER=/path/to/compiler python3 tools/codegen_gate.py
"""
from __future__ import annotations
import os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPILER = Path(os.environ.get("SUTRAM_COMPILER", ROOT / "sutram_compiler"))
OBJDUMP = shutil.which("objdump")
START = bytes.fromhex("0f0b66900f0b")
END = bytes.fromhex("0f0b67900f0b")

CASES = {
    "while_hot": (5, True, r'''mukhya()
    vitti n = 100
    vitti i = 0
    vitti s = 0
    nishkriya("0F 0B 66 90 0F 0B")
    yavat (i < n) {
        s = s + i
        i = i + 1
    }
    nishkriya("0F 0B 67 90 0F 0B")
'''),
    "for_hot": (7, True, r'''mukhya()
    vitti n = 100
    vitti total = 0
    nishkriya("0F 0B 66 90 0F 0B")
    punaravartana j = 0 to n {
        total = total + 1
    }
    nishkriya("0F 0B 67 90 0F 0B")
'''),
    "wide_immediate_update": (4, False, r'''mukhya()
    vitti a = 0
    vitti b = 0
    vitti c = 0
    vitti d = 0
    vitti e = 0
    vitti f = 0
    nishkriya("0F 0B 66 90 0F 0B")
    a = a + 128
    b = b - 2147483647
    f = f + 1000
    f = f - 2000000000
    nishkriya("0F 0B 67 90 0F 0B")
'''),
    "register_destination": (7, False, r'''mukhya()
    vitti a = 7
    vitti b = 3
    vitti c = 0
    vitti d = 0
    vitti e = 0
    nishkriya("0F 0B 66 90 0F 0B")
    c = a + b
    d = a - b
    e = a * b
    c = 7
    nishkriya("0F 0B 67 90 0F 0B")
'''),
    "float_reg_self": (4, False, r'''mukhya() {
    dasham s = 1.5
    dasham x = 2.0
    nishkriya("0F 0B 66 90 0F 0B")
    s = s + x
    nishkriya("0F 0B 67 90 0F 0B")
    likha(s)
}
'''),
    "register_immediate_destination": (8, False, r'''mukhya()
    vitti a = 37
    vitti b = 0
    vitti c = 0
    vitti d = 0
    vitti e = 0
    nishkriya("0F 0B 66 90 0F 0B")
    b = a + 1000
    c = a - 2000
    d = a + 2147483647
    e = a - 2147483647
    nishkriya("0F 0B 67 90 0F 0B")
'''),
    "float_reg_compare": (36, False, r'''mukhya() {
    dasham a = 2.5
    dasham b = 4.5
    vitti yes = 0
    nishkriya("0F 0B 66 90 0F 0B")
    yes = a == b
    yes = a != b
    yes = a < b
    yes = a > b
    yes = a <= b
    yes = a >= b
    nishkriya("0F 0B 67 90 0F 0B")
    likha(yes)
}'''),
    "float_scalar_call_rhs": (18, False, r'''prakriya twice(dasham v) {
    pratiyati v + v
}
mukhya() {
    dasham s = 2.0
    dasham x = 3.0
    nishkriya("0F 0B 66 90 0F 0B")
    s = s + twice(x)
    nishkriya("0F 0B 67 90 0F 0B")
    likha(s)
}
'''),
    "float_reg_destination": (16, False, r'''mukhya() {
    dasham a = 7.5
    dasham b = 2.5
    dasham c = 0.0
    nishkriya("0F 0B 66 90 0F 0B")
    c = a + b
    c = a - b
    c = a * b
    c = a / b
    nishkriya("0F 0B 67 90 0F 0B")
    likha(c)
}'''),
    "float_index_left_reg_right": (43, False, r'''mukhya() {
    kosh dasham a[1]
    kosh_push(a, 2.0)
    dasham w = 3.0
    dasham c = 0.0
    nishkriya("0F 0B 66 90 0F 0B")
    c = a[0] + w
    nishkriya("0F 0B 67 90 0F 0B")
    likha(c)
}'''),
    "float_call_left_reg_right": (17, False, r'''prakriya twice(dasham x) { pratiyati x + x }
mukhya() {
    dasham a = 2.0
    dasham b = 3.0
    dasham c = 0.0
    nishkriya("0F 0B 66 90 0F 0B")
    c = twice(a) + b
    nishkriya("0F 0B 67 90 0F 0B")
    likha(c)
}'''),
    "float_index_left_literal_right": (44, False, r'''mukhya() {
    kosh dasham a[1]
    kosh_push(a, 2.0)
    dasham c = 0.0
    nishkriya("0F 0B 66 90 0F 0B")
    c = a[0] + 2.5
    nishkriya("0F 0B 67 90 0F 0B")
    likha(c)
}'''),
}

def disasm(blob: bytes, tmp: Path):
    raw = tmp / "slice.bin"
    raw.write_bytes(blob)
    cp = subprocess.run(
        [OBJDUMP, "-D", "-b", "binary", "-m", "i386:x86-64", str(raw)],
        text=True, capture_output=True, check=True,
    )
    ins = []
    row = re.compile(r"^\s*([0-9a-f]+):\s+(?:[0-9a-f]{2}\s+)+\s*([a-z][a-z0-9]*)\s*(.*)$", re.I)
    for line in cp.stdout.splitlines():
        m = row.match(line)
        if m:
            ins.append((int(m.group(1), 16), m.group(2).lower(), m.group(3).strip(), line))
    return ins

def bottom_test_shape(ins) -> bool:
    # Steady-state loop must have a backward conditional branch and no backward
    # unconditional jmp.  PERF1 had the inverse: forward conditional + backward jmp.
    backward_cond = 0
    backward_uncond = 0
    for addr, op, operands, _ in ins:
        if not op.startswith("j"):
            continue
        m = re.search(r"(?:0x)?([0-9a-f]+)\s*$", operands, re.I)
        if not m:
            continue
        target = int(m.group(1), 16)
        if target < addr:
            if op == "jmp":
                backward_uncond += 1
            else:
                backward_cond += 1
    return backward_cond >= 1 and backward_uncond == 0

def one(name: str, ceiling: int, require_bottom: bool, source: str, tmp: Path) -> bool:
    src = tmp / f"{name}.sm"
    out = tmp / f"{name}.bin"
    src.write_text(source, encoding="utf-8")
    cp = subprocess.run([str(COMPILER), str(src), str(out)], text=True,
                        capture_output=True)
    if cp.returncode != 0:
        print(f"FAIL {name}: compiler exit {cp.returncode}\n{cp.stdout}{cp.stderr}")
        return False
    data = out.read_bytes()
    a = data.find(START)
    b = data.find(END, a + len(START))
    if a < 0 or b < 0:
        print(f"FAIL {name}: sentinel not found")
        return False
    body = data[a + len(START):b]
    ins = disasm(body, tmp)
    count = len(ins)
    shape_ok = (not require_bottom) or bottom_test_shape(ins)
    if name == "float_reg_self":
        # PERF-F1: exactly four instructions. The scalar ABI still uses GPR
        # raw qwords, but inner-loop float ops must not spill onto the stack.
        # Full persistent XMM allocation is a *separate* future step.
        mnemonics = [opcode for _, opcode, _, _ in ins]
        shape_ok = ("addsd" in mnemonics and
                    not any(op in ("push", "pop") for op in mnemonics) and
                    len([op for op in mnemonics if op == "movq"]) == 3)
    if name == "float_reg_compare":
        # Six comparisons: two MOVQ, UCOMISD, SETcc, MOVZX, store in 'yes'.
        # Store is one extra instruction each. Reject legacy runtime stack
        # traffic and enforce every comparison condition and result normalization.
        ops = [op for _, op, _, _ in ins]
        scc = {"sete", "setne", "setb", "seta", "setbe", "setae"}
        shape_ok = (len(ops) == 36 and ops.count("movq") == 12 and
                    ops.count("ucomisd") == 6 and ops.count("movzbq") == 6 and
                    sum(op in scc for op in ops) == 6 and
                    not any(op in ("push", "pop", "xchg") for op in ops))
    if name == "float_reg_destination":
        # Four independent float binops, four runtime instructions each.
        # Require both operand movq loads, scalar SSE2 op and result movq;
        # prohibit runtime push/pop and legacy GPR/stack operand scheduling.
        mnemonics = [op for _, op, _, _ in ins]
        shape_ok = (len(mnemonics) == 16 and
                    mnemonics.count("movq") == 12 and
                    all(mnemonics.count(op) == 1 for op in
                        ("addsd", "subsd", "mulsd", "divsd")) and
                    not any(op in ("push", "pop", "xchg") for op in mnemonics))
    if name == "float_scalar_call_rhs":
        # R47: a single typed argument must move directly RAX -> RDI, rather
        # than spilling it as PUSH RAX / POP RDI; preserve the R46 callee-save
        # traffic if caller variables occupy r12-r15. The original scalar
        # LHS remains in a GPR without an unrelated PUSH/POP to RDX.
        instructions = [(op, operands) for _, op, operands, _ in ins]
        shape_ok = (count <= ceiling and
                    sum(op == "movq" for op, _ in instructions) == 3 and
                    sum(op == "addsd" for op, _ in instructions) == 1 and
                    any(op == "mov" and "%rax,%rdi" in operands
                        for op, operands in instructions) and
                    not any(op == "push" and "%rax" in operands
                            for op, operands in instructions) and
                    not any(op == "pop" and ("%rdi" in operands or "%rdx" in operands)
                            for op, operands in instructions))
    if name in ("float_index_left_reg_right", "float_call_left_reg_right",
                "float_index_left_literal_right"):
        # FG2: no runtime spill of the outer float expression's LHS.
        # Indexed load itself legitimately pushes base/length for bounds checks;
        # inspect the final instruction suffix instead of prohibiting all PUSH.
        ops = [op for _, op, _, _ in ins]
        if name == "float_index_left_literal_right":
            shape_ok = ops[-6:] == ["movq", "movabs", "movq", "addsd", "movq", "mov"]
        else:
            shape_ok = ops[-5:] == ["movq", "movq", "addsd", "movq", "mov"]
    ok = count <= ceiling and shape_ok
    shape = " bottom-test" if require_bottom else ""
    print(f"{'PASS' if ok else 'FAIL'} {name}: {count} instructions (ceiling {ceiling}){shape}")
    if require_bottom and not shape_ok:
        print("  loop shape failure: expected backward conditional and no backward unconditional jmp")
    if not ok or "--verbose" in sys.argv:
        print("\n".join(row for *_, row in ins))
    return ok

def main() -> int:
    if not COMPILER.exists():
        print(f"compiler not found: {COMPILER}", file=sys.stderr)
        return 2
    if not OBJDUMP:
        print("objdump is required for the codegen gate", file=sys.stderr)
        return 2
    with tempfile.TemporaryDirectory(prefix="sutram-codegen-") as d:
        tmp = Path(d)
        oks = [one(n, lim, bottom, src, tmp) for n, (lim, bottom, src) in CASES.items()]
    return 0 if all(oks) else 1

if __name__ == "__main__":
    raise SystemExit(main())
