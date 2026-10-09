#!/usr/bin/env python3
"""Diagnostic inventory. Uses real native --check, no second parser.
Prints observed stdout and accurately flags known incomplete location families.
This is an audit, not a successful acceptance of universal diagnostics.
"""
from pathlib import Path
import subprocess, re, tempfile
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"tests"/"r49_check"
BIN=ROOT/"r48_after"
CASES=("missing_separators.sm","nested_expressions.sm","top_level_malformed.sm","module_missing.sm","import_bad.sm")
located_pattern=re.compile(r"^.+\.smlib:\d+:\d+: Sutram Error|^.+\.sm:\d+:\d+: Sutram Error",re.M)
nonlocated=0
wrong_provenance=0
for case in CASES:
    with tempfile.TemporaryDirectory(prefix="sutram-r49-") as dest:
        p=subprocess.run([str(BIN),"--check",str(SRC/case)],cwd=dest,text=True,
                         capture_output=True,timeout=30)
        output=p.stdout+p.stderr
        all_errors=[line for line in output.splitlines() if "Sutram Error" in line]
        located=[line for line in all_errors if located_pattern.match(line)]
        raw=output.rstrip()
        print("R49_AUDIT_BEGIN",case,"rc",p.returncode)
        print(raw)
        print("R49_AUDIT_COUNTS",case,"error_lines",len(all_errors),"located",len(located))
        print("R49_AUDIT_END",case,flush=True)
        assert p.returncode!=0, f"{case} unexpectedly succeeded"
        assert not list(Path(dest).iterdir()),"check wrote output binary"
        nonlocated += len(all_errors)-len(located)
        # A matching file:line:column syntax is not proof of source provenance.
        if case == "import_bad.sm" and not any(
            "faulty_r49.smlib:" in err for err in all_errors
        ):
            wrong_provenance += 1
            print("R49_PROVENANCE_UNRESOLVED: imported parser error reports root filename")
        if case == "module_missing.sm":
            if not any("module_missing.sm:2:" in err and
                       "[E_MODULE_MISSING]" in err for err in located):
                print("R49_MODULE_LOCATION_UNRESOLVED")
print(f"R49_AUDIT_STATUS unlocated={nonlocated},wrong_provenance={wrong_provenance},universal_diagnostics_accepted=0",flush=True)
