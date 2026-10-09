#!/usr/bin/env python3
"""Verify native unresolved function pointer identity and proper separate caret locations."""
from pathlib import Path
import subprocess,re,tempfile
ROOT=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix="sutram-r49-") as d:
 p=subprocess.run([str(ROOT/"r48_after"),"--check",str(ROOT/"tests/r49_check/repeated_undefined.sm")],cwd=d,text=True,capture_output=True,timeout=25)
 print("R49_REPEATED_SEMANTIC_RAW_BEGIN\n"+p.stdout+p.stderr+"R49_REPEATED_SEMANTIC_RAW_END",flush=True)
 assert p.returncode!=0
 errors=re.findall(r"repeated_undefined\\.sm:(\\d+):(\\d+): Sutram Error \\[E_UNDEFINED_FUNCTION\\]",p.stdout)
 assert [int(x[0]) for x in errors]==[2,3,4],errors
 assert all(int(x[1])==11 for x in errors),errors
 assert not list(Path(d).iterdir()),"check wrote binary"
 print("R49_REPEATED_SEMANTIC_PASS,unique_correct_lines=3,no_output=1")
