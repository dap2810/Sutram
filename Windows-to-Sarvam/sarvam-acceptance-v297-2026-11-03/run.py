import ctypes, hashlib, json, os, platform, re, subprocess, time
from pathlib import Path
ctypes.windll.kernel32.SetErrorMode(0x8003)
here=Path(__file__).resolve().parent
install=Path(os.environ['LOCALAPPDATA'])/'Programs/Sutram'
compiler=install/'bin/sutram.exe'
work=here/'programs'; work.mkdir(exist_ok=True)
request=(here/'request.md').read_text(encoding='utf8')
def run(args,cwd=install):
    start=time.monotonic()
    try:
        p=subprocess.run([str(a) for a in args],cwd=cwd,capture_output=True,timeout=5)
        return dict(command=[str(a) for a in args],exit=p.returncode,stdout=p.stdout.decode('utf8','replace'),stderr=p.stderr.decode('utf8','replace'),seconds=time.monotonic()-start)
    except subprocess.TimeoutExpired as e:
        return dict(command=[str(a) for a in args],timeout=True,stdout=(e.stdout or b'').decode('utf8','replace'),stderr=(e.stderr or b'').decode('utf8','replace'),seconds=time.monotonic()-start)
rows=[]
expected={5:'namaste',7:'eq: 1\nne: 1\n',8:'lt: 1\ngt: 0\n',9:'abcd',10:'5 7\n',11:'gan=2\nhri=20\nrikt=0\n',12:'1\n',16:'10\n',18:'start=0\nin=4096\nafter=0\n',21:'नमस्ते'}
codes={13:'E_SHUNYA_BHAJAN',14:'E_CHAKRA_DASHAM',15:'E_ATIPRAVAH',17:'E_PHALA_SEEMA',19:'E_PARIMITA',20:'E_PRATYAHRITA'}
for section in re.split(r'(?=### Test \d+ —)',request):
    m=re.match(r'### Test (\d+) — ([^\n]+)',section)
    if not m: continue
    n=int(m[1]); row=dict(test=n,title=m[2],result='NOT-RUN')
    if n in (1,3,4): row['notes']='Direct compiler route; install/uninstall and fresh desktop CMD PATH acceptance not performed.'
    elif n==2:
        row['run']=run([compiler,'--version']); row['result']='PASS' if row['run']['stdout'].startswith('Sutram 1.0 (v297) - sampurna sutra\n') else 'FAIL'
    elif n==6:
        row['compile']=run([compiler,work/'does_not_exist.sm',work/'missing.exe']); row['result']='PASS' if row['compile'].get('exit')==1 and 'Sutram truti' in row['compile']['stdout']+row['compile']['stderr'] else 'FAIL'
    elif 5<=n<=21:
        source=re.search(r'```sutram\n(.*?)```',section,re.S)[1]
        name=re.search(r'\*\*Write `([^`]+)`',section)[1]
        path=work/name; path.write_text(source,encoding='utf8',newline='\n')
        row['source']=name; exe=path.with_suffix('.exe')
        row['compile']=run([compiler,path,exe])
        if row['compile'].get('exit')==0: row['run']=run([exe],work)
        if any(row.get(k,{}).get('timeout') for k in ('compile','run')): row['result']='FAIL HANG'
        elif n in expected:
            r=row.get('run',{}); row['result']='PASS' if r.get('exit')==0 and r.get('stdout','').replace('\r\n','\n')==expected[n] else 'FAIL'
            if n==12 and not ('kosh_kship' in row['compile']['stderr'] and 'kosh_kship' not in row['compile']['stdout']): row['result']='FAIL'
        else:
            r=row.get('run',row['compile']); text=r['stdout']+r['stderr']
            row['result']='PASS' if codes[n] in text and r.get('exit')==1 else 'FAIL'
        if n==21: row['notes']='UTF-8 captured text verified; no terminal-font rendering claim.'
    else: row['notes']='IDE evidence to be added by GUI driver.'
    rows.append(row)
meta=dict(windows=platform.platform(),console='Windows PowerShell 5.1 launcher; Python subprocess capture (developer harness only)',compiler=str(compiler),sha256=hashlib.sha256(compiler.read_bytes()).hexdigest(),rows=rows)
(here/'results.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf8')
for r in rows: print(r['test'],r['result'])
