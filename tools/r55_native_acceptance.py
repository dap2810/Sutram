#!/usr/bin/env python3
"""Actual native acceptance for Sutram R55 forward declarations, and explicit
negative evidence that module globals remain unimplemented (not misreported).
"""
from pathlib import Path
import os, subprocess, sys, tempfile
ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT/"tests/r55_check"
OLD = ROOT/"r55_before"
NEW = ROOT/"r48_after"
PASS_CASES = {
    "mutual_even_odd.sm":"1\n1\n0\n0\n",
    "mutual_triple_reverse.sm":"15\n8\n"
}
BAD_CASES = ["prototype_mismatch.sm","prototype_type_mismatch.sm","prototype_duplicate.sm","prototype_missing.sm"]
def run(args,cwd,timeout=20):
    try:
        r = subprocess.run([str(a) for a in args], cwd=cwd, capture_output=True,
                           text=True,timeout=timeout)
        return r.returncode,r.stdout,r.stderr
    except subprocess.TimeoutExpired:
        return "TIMEOUT","",""
def one(compiler,variant,name,execute=False):
    with tempfile.TemporaryDirectory(prefix="r55-"+variant+"-") as temp:
        wd=Path(temp)
        binary=wd/"native.elf"
        rc,out,err=run([compiler,FIX/name,binary],wd)
        print("R55_NATIVE",variant,name,"compile",repr(rc),repr(out),repr(err),flush=True)
        exists=binary.exists()
        if execute and rc==0 and exists:
            e,o,er=run([binary],wd)
            print("R55_NATIVE",variant,name,"execute",repr(e),repr(o),repr(er),flush=True)
            return e,o
        return rc,None
def check():
    for name,expected in PASS_CASES.items():
        oldrc,_=one(OLD,"before",name)
        assert oldrc!=0,(name,"old compiler accepted a prototype")
        rc,out=one(NEW,"after",name,True)
        assert rc==0 and out==expected,(name,rc,repr(out),repr(expected))
    for name in BAD_CASES:
        rc,_=one(NEW,"invalid",name)
        assert isinstance(rc,int) and rc!=0,(name,rc)
    # Unimplemented globals must not be claimed as a success.
    rc,_=one(NEW,"global-gap", "without_global_gap.sm")
    assert rc!=0,("unexpected global acceptance",rc)
    print("R55_FORWARD_ACCEPTED two_cycle=1 three_cycle=1 "
          "prototype_mismatch=1 type_mismatch=1 duplicate=1 missing=1 "
          "global_vitti_unimplemented=1",flush=True)
if __name__=="__main__":
    assert OLD.is_file() and NEW.is_file()
    check()
