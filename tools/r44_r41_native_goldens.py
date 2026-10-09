#!/usr/bin/env python3
"""Native R41 verification against the FIVE actual GitHub golden fixtures.

Unlike the generic suite, this adapter normalizes only the checkout prefix
of locations in already-recorded golden files. It does not rewrite goldens or
invent expected output. Relevant to R44 pre-pass consolidation.
"""
from pathlib import Path
import subprocess
import tempfile
import sys

ROOT=Path(__file__).resolve().parents[1]
CASES=("210_r41_cycle","211_r41_v1_public","212_r41_v1_private","213_r41_v1_dupexp","214_r41_v1_noalias")
COMPILER=ROOT/"sutram_compiler"

def normalize(output):
    # Historical native goldens use a different checkout location.
    return output.replace("/scratch/work/", "").replace(str(ROOT)+"/","")

def main():
    if not COMPILER.is_file():
        print("NO COMPILER")
        return 2
    total=0
    with tempfile.TemporaryDirectory() as td:
        for case in CASES:
            expected=(ROOT/"tests"/"expect"/(case+".out")).read_text()
            expected_exit=int((ROOT/"tests"/"expect"/(case+".exit")).read_text().strip())
            wants_failure=(ROOT/"tests"/"expect"/(case+".compile_fail")).exists()
            native=Path(td)/(case+".bin")
            c=subprocess.run([str(COMPILER),str(ROOT/"examples"/(case+".sm")),str(native)],
                              cwd=ROOT,capture_output=True,text=True,timeout=30)
            if wants_failure:
                actual=c.stdout+c.stderr
                exit_code=c.returncode
            elif c.returncode != 0:
                actual=c.stdout+c.stderr
                exit_code=c.returncode
            else:
                p=subprocess.run([str(native)],capture_output=True,text=True,timeout=10)
                actual=p.stdout
                exit_code=p.returncode
            good=(normalize(actual)==normalize(expected) and exit_code==expected_exit)
            print(f"{'PASS' if good else 'FAIL'} {case}: native_rc={exit_code}; normalized={normalize(actual)!r}")
            if not good:
                print(f"  expected rc={expected_exit} {normalize(expected)!r}")
            total+=good
    print(f"R41 native goldens: {total}/{len(CASES)}")
    return int(total!=len(CASES))

if __name__=="__main__":
    sys.exit(main())
