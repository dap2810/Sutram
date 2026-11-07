from pathlib import Path
import hashlib,json,os,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
identity=json.loads((HERE/'identity.json').read_text(encoding='utf8'))
assert identity['identity_pass'],'Stop unless the new shell reports v306'
os.environ['SUTRAM_EVIDENCE']=str(HERE)
source=ROOT/'tools/test_windows_native.py'
start=time.perf_counter();code=0
try: exec(compile(source.read_text(encoding='utf8'),str(source),'exec'),{'__file__':str(source),'__name__':'__main__'})
except SystemExit as exc: code=int(exc.code or 0)
rows=json.loads((HERE/'native-cases.json').read_text(encoding='utf8'))
result=dict(exit=code,elapsed_seconds=round(time.perf_counter()-start,3),harness_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
            overrides='none; original v306 native harness',counts={s:sum(r['status']==s for r in rows) for s in sorted({r['status'] for r in rows})},failures=[r for r in rows if r['status'] in ['FAIL','COMPILE_FAIL','TIMEOUT']])
(HERE/'suite.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8');print(json.dumps(result,indent=2));raise SystemExit(code)
