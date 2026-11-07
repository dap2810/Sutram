"""Follow-up for observed abnormal exits; no suite or IDE runs concurrently."""
from pathlib import Path
import ctypes,hashlib,json
from job_runner import run_limited
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
WORK=ROOT/'build/windows-v306-2026-11-06'
assert json.loads((HERE/'identity.json').read_text())['identity_pass']
ctypes.windll.kernel32.SetErrorMode(0x8003)
rows=[]
for iteration in range(1,6):
    for name,cap in [('B3',512),('A3-mandapa',64),('B3',640),('A3-nirmmita-touch-pages',64)]:
        exe=WORK/(name+'.exe')
        row=run_limited(exe,WORK/f'repeat-{iteration}-{name}-{cap}',cap)
        row.update(probe=name,limit_mib=cap,iteration=iteration,executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest())
        row['exit_hex']=f"0x{row['exit']:08X}"
        row['pass']=not row['timed_out'] and (row['exit'],row['stdout'],row['stderr'])==(1,'','Sutram truti: smritih na labdha\n')
        rows.append(row)
        (HERE/'oom-repeats.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf8')
        print(iteration,name,cap,row['exit_hex'],repr(row['stderr']),row['pass'],flush=True)
raise SystemExit(any(not r['pass'] for r in rows))
