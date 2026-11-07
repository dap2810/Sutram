"""Native v307 slice probes; distinguish descriptor display from value correctness."""
from pathlib import Path
import ctypes, hashlib, json, os, subprocess, time
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
WORK=ROOT/'build/windows-v307-2026-11-06/slices'
WORK.mkdir(parents=True,exist_ok=True)
compiler=Path(os.environ['LOCALAPPDATA'])/'Programs/Sutram/bin/sutram.exe'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(compiler)=='0444b43552f6140147ee4701aeac857d585086681bbe4e5bd71d8f90bedd3f7b'
ctypes.windll.kernel32.SetErrorMode(0x8003)
r=dict(compiler=str(compiler),compiler_sha256=sha(compiler),runs=[])
cases=[('cell_minimal',None),('cell_write','99\n'),('untyped_param','77\n77\n'),('untyped_return','99\n99\n'),('funcval_small','0\n99\n'),('funcval_large','1\n')]
def run(cmd):
    start=time.perf_counter()
    try:
        p=subprocess.run(cmd,cwd=WORK,capture_output=True,timeout=30)
        return dict(command=cmd,cwd=str(WORK),exit=p.returncode,exit_hex=f'0x{p.returncode & 0xffffffff:08X}',stdout=p.stdout.decode('utf8','replace'),stderr=p.stderr.decode('utf8','replace'),seconds=time.perf_counter()-start)
    except subprocess.TimeoutExpired:
        return dict(command=cmd,cwd=str(WORK),timeout=True,seconds=time.perf_counter()-start)
for name,expected in cases:
    src=HERE/('r136_ws1_'+name+'.sm');exe=WORK/(name+'.exe')
    row=dict(probe=name,source=src.name,source_sha256=sha(src),expected=expected)
    row['compile']=run([str(compiler),str(src),str(exe)])
    c=row['compile']
    if c.get('exit')==0:
        row['run']=run([str(exe)]);p=row['run']
        if expected is None: row['verdict']='INFORMATIONAL_DESCRIPTOR_DISPLAY' if p.get('exit')==0 else 'FAIL'
        else: row['verdict']='PASS_VALUE' if p.get('exit')==0 and p['stdout']==expected and not p['stderr'] else 'FAIL'
    else:
        row['verdict']='PASS_REFUSAL' if c.get('exit')==1 and 'E_KOSH_VIBHAG' in (c.get('stderr','')+c.get('stdout','')) else 'FAIL_UNEXPECTED_COMPILE_ERROR'
    r['runs'].append(row)
    (HERE/'slice.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf8')
    print(name,row['verdict'],json.dumps(row.get('run',c)),flush=True)
raise SystemExit(any(x['verdict'].startswith('FAIL') for x in r['runs']))
