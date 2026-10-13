#!/usr/bin/env python3
"""Independent proposed R58 deterministic codegen baseline proof.

Never updates the accepted R57 baseline or any expected-output golden.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import os
import subprocess
ROOT=Path(__file__).resolve().parents[1]
COMPILER=Path(os.environ.get("SUTRAM_COMPILER",str(ROOT/"r48_after"))).resolve()
BASELINE=ROOT/"tests/r58_check/CODEGEN-BASELINE.txt"
def main():
    assert COMPILER.is_file(),"build new compiler before running"
    records=[]
    for line in BASELINE.read_text().splitlines():
        if not line.strip() or line.startswith("#"): continue
        expected,path=line.strip().split("  ",1)
        assert len(expected)==64 and (ROOT/path).is_file()
        records.append((expected,path))
    assert len(records)==8
    with TemporaryDirectory(prefix="r58-codegen-") as wd:
        for i,(expected,path) in enumerate(records):
            dst=Path(wd)/f"case{i}.elf"
            cp=subprocess.run([str(COMPILER),str(ROOT/path),str(dst)],
                              cwd=ROOT,text=True,capture_output=True,timeout=60)
            assert cp.returncode==0 and dst.is_file(),(path,cp.stdout,cp.stderr)
            got=hashlib.sha256(dst.read_bytes()).hexdigest()
            assert got==expected,(path,expected,got)
            print("R58_FROZEN",path,got,flush=True)
    print("R58_FROZEN_CODEGEN_ACCEPTED",len(records),"/",len(records),flush=True)
if __name__=="__main__": main()
