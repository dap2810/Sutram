#!/usr/bin/env python3
"""R72 fail-closed source audit of keyword constants, not a native compiler test."""
from pathlib import Path
import argparse
import json
import re

EXPECTED = (
    ("yoj_core", r'^\s*kw_ayojan\s+db\s+"yoj",\s*0\b'),
    ("yoj_graph", r'^\s*mg_w_ayojan:\s*db\s+"yoj",\s*0\b'),
    ("tak_core", r'^\s*kw_to_str\s+db\s+"tak",\s*0\b'),
    ("niryat_graph", r'^\s*mg_w_niryat:\s*db\s+"niryat",\s*0\b'),
    ("yoj_location_low", r'cmp word \[rbx\+r9\],\s*0x6F79'),
    ("yoj_location_high", r'cmp byte \[rbx\+r9\+2\],\s*0x6A'),
    ("niryat_location_low", r'cmp dword \[rbx\+r9\],\s*0x7972696E'),
    ("niryat_location_high", r'cmp word \[rbx\+r9\+4\],\s*0x7461'),
    ("yoj_expand_immediate", r'cmp word \[rsi\],\s*0x6F79'),
    ("yoj_expand_offset", r'^\s*add r12,\s*3\s*$'),
    ("yoj_graph_offset", r'^\s*add r8,\s*3\s*;\s*keyword is now "yoj"'),
    ("niryat_graph_offset", r'^\s*add r8,\s*6\s*;\s*skip "niryat"'),
    ("tak_low", r'cmp ecx,\s*0x6174'),
    ("tak_high", r'cmp ecx,\s*0x6B'),
)

def inspect(source: str):
    lines = source.splitlines()
    findings = []
    for name, pattern in EXPECTED:
        matches = [(n + 1, line.strip()) for n, line in enumerate(lines)
                   if re.search(pattern, line)]
        findings.append({"name": name, "matches": matches,
                         "status": "PASS" if len(matches) == 1 else "FAIL"})
    return findings

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path,
                        default=Path(__file__).resolve().parents[1] / "src" /
                        "sutram_compiler.asm")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if args.source.is_symlink() or not args.source.is_file():
        parser.error("missing/nonregular/symlinked source")
    findings = inspect(args.source.read_text(encoding="utf-8"))
    summary = {"source": str(args.source), "tested": len(findings),
               "pass": sum(x["status"] == "PASS" for x in findings),
               "fail": sum(x["status"] == "FAIL" for x in findings),
               "native_status": "NOT_RUN", "findings": findings}
    if args.report:
        with args.report.open("x", encoding="utf-8") as out:
            json.dump(summary, out, indent=2)
            out.write("\n")
    print(json.dumps(summary, indent=2))
    return 1 if summary["fail"] else 0

if __name__ == "__main__":
    raise SystemExit(main())
