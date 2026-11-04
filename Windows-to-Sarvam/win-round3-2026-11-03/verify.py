"""Developer-only staged build/probes/suite; never changes a golden."""
import ctypes,hashlib,json,os,platform,shutil,subprocess,sys,time
from pathlib import Path
h=Path(__file__).resolve().parent
root=h.parents[1]
stage=sys.argv[1]
windows=os.name=='nt'
if windows:ctypes.windll.kernel32.SetErrorMode(0x8003)
out=h/(stage+('-windows' if windows else '-linux'));out.mkdir(parents=True,exist_ok=True)
build=root/'build/round3'/out.name;build.mkdir(parents=True,exist_ok=True)
compiler=build/('compiler.exe' if windows else 'compiler')
def run(args,timeout=10,env=None):
    start=time.monotonic()
    try:
        p=subprocess.run([str(a) for a in args],cwd=root,env=env,capture_output=True,timeout=timeout)
        return dict(command=[str(a) for a in args],exit=p.returncode,stdout=p.stdout.decode('utf8','replace'),stderr=p.stderr.decode('utf8','replace'),stdout_hex=p.stdout.hex(),seconds=time.monotonic()-start)
    except subprocess.TimeoutExpired as e:
        return dict(command=[str(a) for a in args],timeout=True,stdout=(e.stdout or b'').decode('utf8','replace'),stderr=(e.stderr or b'').decode('utf8','replace'),seconds=time.monotonic()-start)
obj=build/'compiler.o'
commands=[['nasm','-f','win64' if windows else 'elf64','-I.']+(['-dWINDOWS'] if windows else [])+['src/r68_compiler_entry.asm','-o',obj],
          ['ld']+(['-mi386pep','--entry=_start'] if windows else [])+['-o',compiler,obj]]
logs=[run(cmd,60) for cmd in commands]
(out/'build.json').write_text(json.dumps(logs,indent=2),encoding='utf8')
assert all(x.get('exit')==0 for x in logs),logs
for folder in ('lib','lang'):
    shutil.copytree(root/folder,build/folder,dirs_exist_ok=True)
programs={
'concat_literal':('mukhya() { vitti s = vartani_sandhi("ab", "cd") shabda(s) likha("\\n") }\n','abcd\n'),
'concat_loop':('mukhya() { vitti n = 0 yavat (n < 3) { shabda(vartani_sandhi("ab", "cd")) likha("\\n") n = n + 1 } }\n','abcd\nabcd\nabcd\n'),
'concat_inputs':('mukhya() { vitti a = "ab" vitti b = "cd" vitti c = vartani_sandhi(a, b) shabda(a) likha("|") shabda(b) likha("|") shabda(c) }\n','ab|cd|abcd'),
'concat_empty':('mukhya() { shabda(vartani_sandhi("", "cd")) shabda(vartani_sandhi("ab", "")) }\n','cdab'),
'char66':('mukhya() { shabda(anka_akshar(66)) likha("\\n") }\n','B\n'),
'char97':('mukhya() { shabda(anka_akshar(97)) likha("\\n") }\n','a\n'),
'char_kept':('prakriya f() { nivartanam 12 }\nmukhya() { vitti a = anka_akshar(66) vitti b = anka_akshar(97) vitti c = f() shabda(a) shabda(b) likha("\\n") }\n','Ba\n'),
'char_loop':('mukhya() { vitti i = 0 yavat (i < 10000) { vitti c = anka_akshar(97) i = i + 1 } likha(i) }\n','10000\n'),
'memory_query':('mukhya() { likha(parimana()) }\n','0\n'),
'memory_budget':('mukhya() { mandapa parimita 1 { vitti p = nirmmita(64) likha("reached") } }\n',''),
}
rows=[]
for name,(source,want) in programs.items():
    path=h/'programs'/(name+'.sm');path.parent.mkdir(exist_ok=True);path.write_text(source,encoding='utf8',newline='\n')
    exe=build/(name+('.exe' if windows else '.bin'))
    c=run([compiler,path,exe]);r=dict(name=name,expected=want,compile=c)
    if c.get('exit')==0:r['run']=run([exe])
    r['output_match']=r.get('run',{}).get('stdout')==want and r.get('run',{}).get('exit')==0
    rows.append(r)
    print(name,r['compile'].get('exit'),r.get('run',{}).get('exit'),ascii(r.get('run',{}).get('stdout','')),flush=True)
data=dict(stage=stage,host=platform.platform(),compiler_sha256=hashlib.sha256(compiler.read_bytes()).hexdigest(),rows=rows)
(out/'probes.json').write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf8')
env=os.environ.copy();env['SUTRAM_COMPILER']=str(compiler);env['SUTRAM_EVIDENCE']=str(out)
if windows:
    shutil.copyfile(compiler,root/'win/sutram.exe')
    for folder in ('lib','lang'):
        shutil.copytree(root/folder,root/'win'/folder,dirs_exist_ok=True)
    suite=run([sys.executable,'-B','tools/test_windows_native.py'],240,env)
else:
    suite=run([sys.executable,'-B','tests/run_tests.py'],240,env)
(out/'suite.json').write_text(json.dumps(suite,indent=2,ensure_ascii=False),encoding='utf8')
print(suite['stdout'][-2500:],flush=True)
print('SUITE EXIT',suite.get('exit'),flush=True)
