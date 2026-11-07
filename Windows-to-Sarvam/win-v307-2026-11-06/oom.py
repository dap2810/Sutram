"""Requested v307 boundary map; inspect redirected stderr as bytes after exit."""
from pathlib import Path
import ctypes,hashlib,json,os,subprocess
from job_runner import run_limited
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
WORK=ROOT/'build/windows-v307-2026-11-06'
WORK.mkdir(parents=True,exist_ok=True)
streams=HERE/'streams';streams.mkdir(exist_ok=True)
compiler=Path(os.environ['LOCALAPPDATA'])/'Programs/Sutram/bin/sutram.exe'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected_hash='0444b43552f6140147ee4701aeac857d585086681bbe4e5bd71d8f90bedd3f7b'
assert sha(compiler)==expected_hash,'Stop: installed compiler is not pinned v307'
expected=b'Sutram truti: smritih na labdha\n'
ctypes.windll.kernel32.SetErrorMode(0x8003)
r=dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),compiler=str(compiler),compiler_sha256=sha(compiler),expected_stderr_hex=expected.hex(),compilations=[],runs=[])
def save(): (HERE/'oom.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf8')
for name in ['B3','A3-mandapa','A3-nirmmita-touch-pages']:
    cmd=[str(compiler),str(HERE/(name+'.sm')),str(WORK/(name+'.exe'))]
    p=subprocess.run(cmd,cwd=WORK,capture_output=True,timeout=30)
    r['compilations'].append(dict(command=cmd,cwd=str(WORK),exit=p.returncode,stdout=p.stdout.decode(),stderr=p.stderr.decode()))
    save();assert p.returncode==0
cases=[('B3',cap,n) for cap in [448,480,512,544,576,608,640] for n in range(1,4)]
cases += [('A3-mandapa',64,n) for n in range(1,11)]
cases += [('A3-nirmmita-touch-pages',64,1)]
for name,cap,iteration in cases:
    label=f'{name}-{cap}-{iteration}'
    exe=WORK/(name+'.exe');directory=WORK/label
    row=run_limited(exe,directory,cap)
    raw=(directory/'stderr').read_bytes();stdout=(directory/'stdout').read_bytes()
    (streams/(label+'.stderr')).write_bytes(raw)
    row.update(probe=name,limit_mib=cap,iteration=iteration,exit_hex=f"0x{row['exit']:08X}",executable_sha256=sha(exe),
               stderr_bytes=len(raw),stderr_hex=raw.hex(),stderr_ends_lf=raw.endswith(b'\n'),stderr_exact=raw==expected,
               message_present=expected.rstrip(b'\n') in raw,stderr_file=f'streams/{label}.stderr',stdout_bytes=len(stdout))
    row['clean_refusal']=not row['timed_out'] and row['exit']==1 and raw==expected and not stdout
    r['runs'].append(row);save()
    print(label,row['exit_hex'],'exact_stderr=',row['stderr_exact'],'ends_LF=',row['stderr_ends_lf'],flush=True)
r['summary']=dict(total=len(r['runs']),clean_refusals=sum(x['clean_refusal'] for x in r['runs']),abnormal_exits=sum(x['exit'] not in (0,1) for x in r['runs']),complete_messages=sum(x['stderr_exact'] for x in r['runs']))
save();print(json.dumps(r['summary'],indent=2))
raise SystemExit(any(not x['clean_refusal'] for x in r['runs']))
