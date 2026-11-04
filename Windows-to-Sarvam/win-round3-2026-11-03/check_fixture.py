import json,subprocess,sys
from pathlib import Path
h=Path(__file__).resolve().parent;root=h.parents[1]
base=root/'build/round3/baseline-linux/compiler'
out=root/'build/round3/file-read-baseline.bin'
rows=[]
for cmd in [[str(base),str(root/'tests/stdlib/file_read.sm'),str(out)],[str(out)]]:
    p=subprocess.run(cmd,cwd=root,capture_output=True,timeout=10)
    rows.append(dict(command=cmd,exit=p.returncode,stdout=p.stdout.decode('utf8','replace'),stderr=p.stderr.decode('utf8','replace')))
(h/'fixture-baseline.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
print(rows[-1]['stdout'][:45])
