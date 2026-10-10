#!/usr/bin/env python3
from pathlib import Path
import subprocess,tempfile
root=Path(__file__).resolve().parents[1]
names=["164_r41_cycle_reject.sm","212_r41_v1_private.sm","213_r41_v1_dupexp.sm","214_r41_v1_noalias.sm","156_namespaced_alias_collision.sm"]
for name in names:
 with tempfile.TemporaryDirectory() as tmp:
  p=subprocess.run([str(root/"r48_after"),"--check",str(root/"examples"/name)],cwd=tmp,capture_output=True,text=True,timeout=10)
  print("R51_GRAPH_BEGIN",name,"exit",p.returncode)
  print((p.stdout+p.stderr).rstrip())
  print("R51_GRAPH_END",name,flush=True)
