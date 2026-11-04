"""Linux regression gates for this compiler change; no goldens rewritten."""
import json,os,subprocess,sys,time
from pathlib import Path
h=Path(__file__).resolve().parent;root=h.parents[1]
c=root/'build/round3/explicit-memory-linux/compiler'
env=os.environ.copy();env['SUTRAM_COMPILER']=str(c)
commands={
 'codegen':[sys.executable,'tools/codegen_gate.py'],
 'packs':[sys.executable,'tools/test_lang_packs.py',str(c)],
 'library':[sys.executable,'tools/proof_lib.py','--compiler',str(c)],
 'properties':[sys.executable,'tools/proof_props.py','--compiler',str(c)],
 'crash':[sys.executable,'tools/crash_corpus.py','--compiler',str(c)],
 'vocabulary':[sys.executable,'-B','tests/r111/test_vocabulary.py','--compiler',str(c)],
}
rows=[]
for name,args in commands.items():
    start=time.monotonic()
    try:
        p=subprocess.run(args,cwd=root,env=env,capture_output=True,timeout=300)
        row=dict(name=name,command=args,exit=p.returncode,stdout=p.stdout.decode('utf8','replace'),stderr=p.stderr.decode('utf8','replace'),seconds=time.monotonic()-start)
    except subprocess.TimeoutExpired as e:
        row=dict(name=name,command=args,timeout=True,stdout=(e.stdout or b'').decode('utf8','replace'),stderr=(e.stderr or b'').decode('utf8','replace'),seconds=time.monotonic()-start)
    rows.append(row)
    (h/'regression.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding='utf8')
    print(name,row.get('exit'),row['stdout'][-400:],flush=True)
