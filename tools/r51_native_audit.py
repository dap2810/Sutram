#!/usr/bin/env python3
"""Actual NASM compiler diagnostic checks; never synthesize compiler output."""
from pathlib import Path
import subprocess,re,tempfile
R=Path(__file__).resolve().parents[1]
C=R/"r48_after"
D=R/"tests"/"r51_check"
cases=[
 ("nested_root.sm","inner_r51.smlib",2,1),
 ("namespaced_root.sm","broken_ns_r51.smlib",2,1),
 ("semantic_import.sm","semantics_r51.smlib",2,3),
 ("missing_three.sm","missing_three.sm",2,3),
 ("nested_braces.sm","nested_braces.sm",3,1),
]
fail=0
for file,expected_file,firstline,minimum in cases:
 with tempfile.TemporaryDirectory(prefix="r51-original-") as tmp:
  p=subprocess.run([str(C),"--check",str(D/file)],cwd=tmp,stdout=subprocess.PIPE,
                   stderr=subprocess.PIPE,text=True,timeout=20)
  result=p.stdout+p.stderr
  actual=re.findall(r"^([^\s:]+):(\d+):(\d+): Sutram Error \[([^\]]+)\]",result,re.M)
  relevant=[(name,int(line),int(col),code) for name,line,col,code in actual
            if name==expected_file and int(col)>0]
  print("R51_BEGIN",file,"exit",p.returncode)
  print(result.rstrip())
  print("R51_COUNTS",file,"reported",len(actual),"correct_origin",len(relevant),"expected_at_least",minimum)
  print("R51_END",file,flush=True)
  if p.returncode==0 or len(relevant)<minimum or not any(x[1]==firstline for x in relevant) or list(Path(tmp).iterdir()):
   fail+=1
print("R51_ACCEPTANCE", "PASS" if fail==0 else "FAIL", "failed_cases", fail, flush=True)
if fail:raise SystemExit(1)
