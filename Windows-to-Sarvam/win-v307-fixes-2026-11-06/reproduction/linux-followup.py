from pathlib import Path
import subprocess,json,time,os
root=Path(__file__).resolve().parents[2];out=root/'build/fixes/linux-final';out.mkdir(exist_ok=True)
comp=root/'build/fixes/linux/candidate/sutram_compiler'
subprocess.run(['nasm','-f','elf64','-I.','src/r68_compiler_entry.asm','-o',str(out/'candidate.o')],cwd=root,check=True)
subprocess.run(['ld','-o',str(comp),str(out/'candidate.o')],check=True)
commands=[('baseline-proof',['tools/proof_lib.py','--compiler',str(root/'build/fixes/linux/baseline/sutram_compiler')]),
 ('candidate-proof',['tools/proof_lib.py','--compiler',str(comp)]),
 ('candidate-r23',['tests/r23/test_capabilities.py','--compiler',str(comp)]),
 ('candidate-suite',['tests/run_tests.py']),
 ('candidate-slices',['tools/test_v307_fix_regressions.py','--compiler',str(comp),'--phase','slice','--evidence',str(out/'slices')])]
rows=[]
for label,args in commands:
    start=time.monotonic()
    with (out/(label+'.log')).open('w') as f:p=subprocess.run(['python3',*args],cwd=root,env=dict(os.environ,SUTRAM_COMPILER=str(comp)),stdout=f,stderr=subprocess.STDOUT,timeout=240)
    row=dict(label=label,command=args,exit=p.returncode,seconds=time.monotonic()-start,tail=(out/(label+'.log')).read_text(errors='replace').splitlines()[-3:]);rows.append(row)
    (out/'results.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(row),flush=True)
