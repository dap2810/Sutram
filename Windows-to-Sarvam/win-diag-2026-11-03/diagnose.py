import ctypes,hashlib,json,os,subprocess,time
from pathlib import Path
ctypes.windll.kernel32.SetErrorMode(0x8003)
h=Path(__file__).resolve().parent
root=h.parents[1]/'build/windows-v297/source'
compiler=root/'win/sutram.exe'
work=h/'programs';work.mkdir(exist_ok=True)
names=['303_r103_parimita_refuses','317_r107_parimana','318_r108_parimana_moves','322_r111_new_names','323_r111_old_names','288_r86_kosh_alias_moves','29_nishkriya','220_hindi_parse_error']
def run(args):
    t=time.monotonic()
    try:
        p=subprocess.run([str(x) for x in args],cwd=root,capture_output=True,timeout=5)
        return dict(command=[str(x) for x in args],exit=p.returncode,stdout=p.stdout.decode('utf8','replace'),stderr=p.stderr.decode('utf8','replace'),stdout_hex=p.stdout.hex(),seconds=time.monotonic()-t)
    except subprocess.TimeoutExpired as e:
        return dict(command=[str(x) for x in args],timeout=True,stdout=(e.stdout or b'').decode('utf8','replace'),stderr=(e.stderr or b'').decode('utf8','replace'),seconds=time.monotonic()-t)
rows=[]
def case(name,source,flags=(),golden=None):
    exe=work/(name+'.exe');r=dict(name=name,source=source.read_text(encoding='utf8'),compile=run([compiler,*flags,source,exe]))
    if golden:
        r['expected_stdout']=golden.with_suffix('.out').read_text(encoding='utf8');r['expected_exit']=golden.with_suffix('.exit').read_text().strip()
    if r['compile'].get('exit')==0:
        r['run']=run([exe]);r['sha256']=hashlib.sha256(exe.read_bytes()).hexdigest()
    rows.append(r)
for name in names:
    case(name,root/'examples'/(name+'.sm'),golden=root/'tests/expect'/name)
case('220_with_hindi',root/'examples/220_hindi_parse_error.sm',['--lang','hindi'],root/'tests/expect/220_hindi_parse_error')
probes={
'new_char':'mukhya() { shabda(anka_akshar(66)) likha("\\n") }\n',
'old_char':'mukhya() { shabda(char_from(66)) likha("\\n") }\n',
'new_concat_literal':'mukhya() { vitti s = vartani_sandhi("ab", "cd") shabda(s) }\n',
'old_concat_literal':'mukhya() { vitti s = vartani_cat("ab", "cd") shabda(s) }\n',
'new_concat_writable':'mukhya() { vitti p = nirmmita(64) akshar_rakh(p, 0, 97) akshar_rakh(p, 1, 98) akshar_rakh(p, 2, 0) vitti s = vartani_sandhi(p, "cd") shabda(s) }\n',
}
for name,source in probes.items():
    path=work/(name+'.sm');path.write_text(source,encoding='utf8');case(name,path)
pairs={}
for a,b in [('322_r111_new_names','323_r111_old_names'),('new_char','old_char'),('new_concat_literal','old_concat_literal')]:
    pairs[a+' / '+b]=(work/(a+'.exe')).read_bytes()==(work/(b+'.exe')).read_bytes()
out=dict(compiler=str(compiler),compiler_sha256=hashlib.sha256(compiler.read_bytes()).hexdigest(),cwd=str(root),rows=rows,byte_identical_pairs=pairs)
(h/'results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8',newline='\n')
for r in rows: print(r['name'],r['compile'].get('exit'),r.get('run',{}).get('exit'),ascii(r.get('run',{}).get('stdout','')))
print(pairs)
