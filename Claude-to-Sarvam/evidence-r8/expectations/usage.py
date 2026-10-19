import sys,re,json,subprocess
sys.path.insert(0,'tools'); import lib_proof_gaps as G
from pathlib import Path
funcs=[f for p in sorted(G.LIB.glob('*.smlib')) for f in G.parse_module(p)]
files=subprocess.run(['git','ls-files','*.sm','*.smlib','*.md','*.html'],capture_output=True,text=True).stdout.split()
texts={}
for f in files:
    if f.startswith(('Sarvam-to-Claude','Claude-to-Sarvam','evidence')): continue
    try: texts[f]=open(f,encoding='utf-8').read()
    except: pass
use={}
for fn in funcs:
    rx=re.compile(r'(?<![\w])'+re.escape(fn['name'])+r'\s*\(')
    n={'lib':0,'examples':0,'tests':0,'docs':0}
    for f,t in texts.items():
        c=len(rx.findall(t))
        if f=='lib/'+fn['module']+'.smlib': c-=1
        if c<=0: continue
        k='lib' if f.startswith('lib/') else 'examples' if f.startswith('examples/') else 'tests' if f.startswith('tests/') else 'docs'
        n[k]+=c
    use[fn['module']+'.'+fn['name']]=n
json.dump(use,open(sys.argv[1],'w'),indent=0)
top=sorted(use.items(),key=lambda kv:-(kv[1]['lib']+kv[1]['examples']+kv[1]['docs']))
for k,v in top[:15]: print(k,v)
