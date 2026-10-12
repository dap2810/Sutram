#!/usr/bin/env python3
"""Verify accepted 186 golden tests plus the 3 newer Muse example-local goldens.
No expected output file is created or modified.
"""
from pathlib import Path
import subprocess, tempfile, sys
ROOT=Path(__file__).resolve().parents[1]
EXPECT=ROOT/"tests"/"expect"
examples=ROOT/"examples"
names=sorted(p.stem for p in examples.glob("*.sm")
             if (EXPECT/(p.stem+".out")).exists() and (EXPECT/(p.stem+".exit")).exists())
print("R54_ORIGINAL_GOLDENS",len(names),flush=True)
assert len(names)==186,("unexpected original-golden count",len(names))
subprocess.run([sys.executable,str(ROOT/"tests/run_tests.py"),*names],cwd=ROOT,check=True)
for name in ["215_r12_wordfreq","216_r12_expr","217_r12_report"]:
    with tempfile.TemporaryDirectory(prefix="r54-muse-") as d:
        wd=Path(d);src=examples/(name+".sm");exe=wd/"out"
        p=subprocess.run([str(ROOT/"sutram_compiler"),str(src),str(exe)],
                         cwd=ROOT,text=True,capture_output=True,timeout=15)
        assert p.returncode==0 and exe.exists(),(name,p.returncode,p.stdout,p.stderr)
        x=subprocess.run([str(exe)],cwd=ROOT,text=True,capture_output=True,timeout=15)
        expected=(examples/(name+".out")).read_text()
        expected_exit=int((examples/(name+".exit")).read_text().strip())
        print("R54_MUSE_GOLDEN",name,"compile",p.returncode,
              "exit",x.returncode,"stdout",repr(x.stdout),flush=True)
        assert x.returncode==expected_exit and x.stdout==expected,(
            name,x.returncode,expected_exit,repr(x.stdout),repr(expected))
print("R54_MUSE_ACCEPTED original=186 example_local=3 original_golden_changes=0",flush=True)
