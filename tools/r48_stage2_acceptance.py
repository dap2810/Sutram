#!/usr/bin/env python3
"""Native Stage 2 checks: real compiled compiler, not a second parser."""
from pathlib import Path
import re, subprocess, sys, tempfile

ROOT=Path(__file__).resolve().parents[1]
BIN=ROOT/"r48_after"
DIR=ROOT/"tests"/"r48_check"

def run(name):
    with tempfile.TemporaryDirectory(prefix="sutram-r48s2-") as cwd:
        p=subprocess.run([str(BIN),"--check",str(DIR/name)],cwd=cwd,
                         capture_output=True,text=True,timeout=20)
        print("==",name,"exit",p.returncode,"==")
        print(p.stdout,p.stderr)
        assert p.returncode!=0,(name,"unexpected success")
        assert "Sutram check: errors found; no output binary" in p.stdout,name
        assert not list(Path(cwd).iterdir()), (name,"check created output file")
        return p.stdout

def parses(name, count, lines):
    out=run(name)
    m=re.findall(r"([^\s:]+\.sm):(\d+):(\d+): Sutram Error \[E_PARSE\]: near '([^']+)'",out)
    assert count<=len(m)<=8,(name,m)
    assert set(lines).issubset({int(x[1]) for x in m}),(name,m)
    assert all(int(x[2])>=1 for x in m),(name,m)
    assert "^" in out,(name,"missing source caret")
    return len(m)

def main():
    assert BIN.exists(),"Build r48_after first"
    a=parses("structural_three_errors.sm",3,{2,3,4})
    b=parses("nested_recovery.sm",2,{3,6})
    c=parses("unclosed_block.sm",1,{4})
    text=run("three_undefined_functions.sm")
    m=re.findall(r"three_undefined_functions\.sm:(\d+):(\d+): Sutram Error \[E_UNDEFINED_FUNCTION\]: unknown function '([^']+)'",text)
    assert len(m)>=3,m
    assert {int(x[0]) for x in m}>={2,3,4},m
    assert {x[2] for x in m}>={"missing_alpha","missing_beta","missing_gamma"},m
    print(f"STAGE2_PASS structural={a} nested={b} unclosed={c} undefined={len(m)}")
if __name__=="__main__":sys.exit(main())
