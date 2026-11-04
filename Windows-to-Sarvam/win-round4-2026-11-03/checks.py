import json,os,subprocess,sys
from pathlib import Path
h=Path(__file__).resolve().parent;root=h.parents[1];win=os.name=='nt'
c=root/'build/round3'/('final-windows/compiler.exe' if win else 'final-linux/compiler')
env=os.environ.copy();env['SUTRAM_COMPILER']=str(c)
tmp=root/'build/round4-temp';tmp.mkdir(exist_ok=True);env['TMP']=env['TEMP']=env['TMPDIR']=str(tmp)
commands={'contracts':[sys.executable,'-B','-m','unittest','discover','-s','tests/windows_round3','-v']}
if not win:
 # Preserve the committed fixture bytes; CRLF checkout otherwise changes its byte-count contract.
 # Prepared from git show by Windows Python; WSL git cannot resolve Windows worktree metadata.
 commands.update(codegen=[sys.executable,'tools/codegen_gate.py'],packs=[sys.executable,'tools/test_lang_packs.py',str(c)],library=[sys.executable,'tools/proof_lib.py','--compiler',str(c)],properties=[sys.executable,'tools/proof_props.py','--compiler',str(c)],crash=[sys.executable,'tools/crash_corpus.py','--compiler',str(c)])
rows=[]
for name,cmd in commands.items():
 p=subprocess.run(cmd,cwd=root,env=env,capture_output=True,timeout=300)
 rows.append(dict(name=name,command=cmd,exit=p.returncode,stdout=p.stdout.decode('utf8','replace'),stderr=p.stderr.decode('utf8','replace')))
 (h/('checks-windows.json' if win else 'checks-linux.json')).write_text(json.dumps(rows,indent=2),encoding='utf8')
 print(name,p.returncode,rows[-1]['stdout'][-300:],rows[-1]['stderr'][-300:],flush=True)
sys.exit(any(r['exit'] for r in rows))
