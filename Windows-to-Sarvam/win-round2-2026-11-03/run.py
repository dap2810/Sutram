import ctypes,hashlib,json,re,subprocess,time
from pathlib import Path
ctypes.windll.kernel32.SetErrorMode(0x8003)
h=Path(__file__).resolve().parent
repo=h.parents[1];root=repo/'build/windows-v297/source'
compiler=root/'win/sutram.exe'
work=h/'programs';work.mkdir(exist_ok=True)
request=(h/'request.md').read_text(encoding='utf8')
programs={f'B{i+1}':s for i,s in enumerate(re.findall(r'```sutram\n(.*?)```',request,re.S))}
programs.update(C1='mukhya() {\n    shabda(anka_akshar(66))\n    likha("\\n")\n}\n',C2='mukhya() {\n    vitti s = vartani_sandhi("ab", "cd")\n    shabda(s)\n    likha("\\n")\n}\n')
def run(args):
    start=time.monotonic()
    try:
        p=subprocess.run([str(a) for a in args],cwd=root,capture_output=True,timeout=5)
        return dict(command=[str(a) for a in args],exit=p.returncode,stdout=p.stdout.decode('utf8','replace'),stderr=p.stderr.decode('utf8','replace'),stdout_hex=p.stdout.hex(),seconds=time.monotonic()-start)
    except subprocess.TimeoutExpired as e:
        return dict(command=[str(a) for a in args],timeout=True,stdout=(e.stdout or b'').decode('utf8','replace'),stderr=(e.stderr or b'').decode('utf8','replace'),seconds=time.monotonic()-start)
rows=[]
def case(name,path,flags=()):
    exe=work/(name+'.exe');r=dict(name=name,source=path.read_text(encoding='utf8'),compile=run([compiler,*flags,path,exe]))
    if r['compile'].get('exit')==0:r['run']=run([exe])
    rows.append(r)
case('A220',root/'examples/220_hindi_parse_error.sm',['--lang','hindi'])
for name,source in programs.items():
    path=work/(name+'.sm');path.write_text(source,encoding='utf8',newline='\n');case(name,path)
case('B318',root/'examples/318_r108_parimana_moves.sm')
out=dict(source_commit='1263356b6cb434871680c83c6f70a8c67eb016a3',compiler=str(compiler),compiler_sha256=hashlib.sha256(compiler.read_bytes()).hexdigest(),cwd=str(root),version=run([compiler,'--version']),rows=rows)
out['hindi_exact_golden_match']=rows[0]['compile']['stdout']==(root/'tests/expect/220_hindi_parse_error.out').read_text(encoding='utf8') and rows[0]['compile']['stderr']=='' and rows[0]['compile']['exit']==1
(h/'windows-results.json').write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding='utf8',newline='\n')
for r in rows:print(r['name'],json.dumps(r.get('run',r['compile']),ensure_ascii=True))
