#!/usr/bin/env python3
"""Exact R59 native generated-ELF hash proof; never edits frozen goldens."""
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib,os,subprocess
root=Path(__file__).resolve().parents[1]
compiler=Path(os.environ.get("SUTRAM_COMPILER",str(root/"r48_after"))).resolve()
entries=[]
for line in (root/"tests/r59_check/CODEGEN-BASELINE.txt").read_text().splitlines():
    if line.strip() and not line.lstrip().startswith("#"):
        digest,path=line.split("  ",1)
        entries.append((digest,path.strip()))
assert len(entries)==3
with TemporaryDirectory(prefix="r59-baseline-") as temp:
    for idx,(digest,path) in enumerate(entries):
        target=Path(temp)/(str(idx)+".elf")
        cp=subprocess.run([str(compiler),str(root/path),str(target)],cwd=root,text=True,capture_output=True)
        assert cp.returncode==0 and target.exists(),(path,cp.stdout,cp.stderr)
        got=hashlib.sha256(target.read_bytes()).hexdigest()
        assert got==digest,(path,digest,got)
        print("R59_FROZEN",path,got)
print("R59_FROZEN_CODEGEN_ACCEPTED",len(entries),"/",len(entries))
