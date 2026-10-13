#!/usr/bin/env python3
"""Proposed post-R57 generated-code baseline: compile, hash, compare.

Development-only regression tool. This is not a second compiler.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import os
import subprocess
ROOT=Path(__file__).resolve().parents[1]
COMPILER=Path(os.environ.get("SUTRAM_COMPILER",str(ROOT/"r48_after"))).resolve()
MANIFEST=ROOT/"tests/r57_check/CODEGEN-BASELINE.txt"
def main():
    assert COMPILER.is_file(),"build R57 compiler first"
    rows=[]
    for line in MANIFEST.read_text().splitlines():
        if not line.strip() or line.startswith("#"): continue
        digest,source=line.strip().split("  ",1)
        assert len(digest)==64 and (ROOT/source).is_file()
        rows.append((digest,source))
    assert len(rows)==6
    with TemporaryDirectory(prefix="r57-binaries-") as d:
        for i,(expected,source) in enumerate(rows):
            out=Path(d)/f"case{i}.elf"
            p=subprocess.run([str(COMPILER),str(ROOT/source),str(out)],cwd=ROOT,
                text=True,capture_output=True,timeout=50)
            assert p.returncode==0 and out.is_file(),(source,p.stdout,p.stderr)
            actual=hashlib.sha256(out.read_bytes()).hexdigest()
            assert actual==expected,(source,expected,actual)
            print("R57_FROZEN",source,actual,flush=True)
    print("R57_FROZEN_CODEGEN_ACCEPTED",len(rows),"/",len(rows),flush=True)
if __name__=="__main__":main()
