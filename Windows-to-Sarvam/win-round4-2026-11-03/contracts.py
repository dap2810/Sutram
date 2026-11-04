"""Cross-platform memory boundary probes, with literal expected results; no goldens."""
import json,os,subprocess,sys,time
from pathlib import Path
h=Path(__file__).resolve().parent;root=h.parents[1];win=os.name=='nt'
c=root/'build/round3'/('final-windows/compiler.exe' if win else 'final-linux/compiler')
cases={
'rounding_rewind':('mukhya() { likha(parimana()) vitti p=nirmmita(1) likha(parimana()) mandapa { vitti q=nirmmita(17) likha(parimana()) } likha(parimana()) }','0\n16\n48\n16\n',0),
'budget_exact':('mukhya() { mandapa parimita 16 { vitti p=nirmmita(1) likha(parimana()) } likha(parimana()) }','16\n0\n',0),
'budget_rounding':('mukhya() { mandapa parimita 15 { vitti p=nirmmita(1) likha("BAD") } }','E_PARIMITA',1),
'budget_outer':('mukhya() { mandapa parimita 16 { vitti p=nirmmita(16) mandapa parimita 64 { vitti q=nirmmita(1) likha("BAD") } } }','E_PARIMITA',1),
'budget_inner':('mukhya() { mandapa parimita 64 { mandapa parimita 16 { vitti q=nirmmita(17) likha("BAD") } } }','E_PARIMITA',1),
'zero_reuse':('mukhya() { mandapa { vitti p=nirmmita(16) p[0]=99 } mandapa { vitti p=nirmmita(16) likha(p[0]) } likha(parimana()) }','0\n0\n',0),
'alias_obstacle':('mukhya() { kosh k[1] kosh_push(k,41) vitti a=k vitti obstacle=nirmmita(64) kosh_push(k,42) k[0]=99 likha("a[0]=",a[0]," k[0]=",k[0]) }','a[0]=99 k[0]=99',0),
'alias_many':('mukhya() { kosh k[1] kosh_push(k,41) vitti a=k vitti i=0 yavat(i<10000) { kosh_push(k,i) i=i+1 } k[0]=99 likha(a[0]) }','99\n',0),
'return_rewind':('prakriya f() { mandapa { vitti p=nirmmita(64) nivartanam 7 } } mukhya() { likha(f()) likha(parimana()) }','7\n0\n',0),
}
rows=[]
for name,(src,want,code) in cases.items():
 p=h/'programs'/(name+'.sm');p.write_text(src+'\n',encoding='utf8')
 target=c.parent/(name+('.exe' if win else '.bin'))
 command=[str(c),str(p),str(target)];comp=subprocess.run(command,capture_output=True)
 row=dict(name=name,command=command,compile_exit=comp.returncode,compile_stdout=comp.stdout.decode('utf8','replace'),compile_stderr=comp.stderr.decode('utf8','replace'),expected=want,expected_exit=code)
 if comp.returncode==0:
  r=subprocess.run([str(target)],capture_output=True,timeout=20);out=r.stdout.decode('utf8','replace').replace('\r\n','\n')
  row.update(run_command=[str(target)],exit=r.returncode,stdout=out,stderr=r.stderr.decode('utf8','replace'),passed=(r.returncode==code and (want in out if code else out.rstrip()==want.rstrip()) and 'BAD' not in out))
 rows.append(row);print(name,row.get('passed',False),flush=True)
(h/('contracts-windows.json' if win else 'contracts-linux.json')).write_text(json.dumps(rows,indent=2),encoding='utf8')
sys.exit(not all(r.get('passed') for r in rows))
