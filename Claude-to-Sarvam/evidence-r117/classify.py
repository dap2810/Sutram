import glob, os, subprocess, sys, re
G=sys.argv[1]; R=G+'/r116/guard'; NEW='<repo>'; OLD=R+'/old'
sys.path.insert(0, NEW+'/tests'); import run_tests as RT
PAT=['examples/*.sm','examples/*/*.sm','tests/stdlib/*.sm','tests/r*/*.sm','tests/r*/*/*.sm']
rels=sorted({os.path.relpath(p,NEW) for pat in PAT for p in glob.glob(os.path.join(NEW,pat))} - {'examples/345_r116_long_literal.sm'})  # the guard's list: 345 was added after it ran
differ=[l.split()[1] for l in open(R+'/guard-elf.txt') if l.startswith('DIFFER')]
F=['dvigun','trigun','vardh','nirapeksh_mulya','mahattam_samapavartak','viparyay_ank','ganita_nirapeksh','brahmagupta_kshetr','brihat_ank_se','brihat_ank_tak_laghu','yog_seema','adish_gunan','bindu_gunan','suchi_shreni','varna_tak_dashm','mil_shreni']
cls={}
for rel in differ:
    i=rels.index(rel); stem=os.path.splitext(os.path.basename(rel))[0]
    stdin=RT.STDIN.get(stem,'') if rel.startswith('examples/') else ''
    res=[]
    for side,cwd in (('old',OLD),('new',NEW)):
        r=subprocess.run([f'{R}/g-elf/{i}.{side}'],input=stdin.encode(),capture_output=True,timeout=30,cwd=cwd)
        res.append((r.stdout,r.stderr,r.returncode))
    txt=open(os.path.join(NEW,rel),encoding='utf-8',errors='replace').read()
    oldtxt=open(os.path.join(OLD,rel),encoding='utf-8',errors='replace').read() if os.path.exists(os.path.join(OLD,rel)) else None
    calls=sorted({f for f in F if re.search(r'\b'+f+r'\s*\(',txt)})
    (o1,e1,c1),(o2,e2,c2)=res
    if res[0]==res[1]: k='A same stdout, stderr and exit'
    elif c2==1 and e2.startswith(b'Sutram truti [') and o2==o1[:len(o2)]: k='B now stops with a contract refusal (output up to it unchanged)'
    elif oldtxt!=txt: k='C program text rewritten this round (deliberate migration)'
    else: k='D OTHER - behaviour changed, not explained'
    cls.setdefault(k,[]).append((rel,calls,c1,c2,e2.decode(errors='replace').strip()[:110]))
for k in sorted(cls):
    print(f'\n## {k}: {len(cls[k])}')
    if k[0]=='A':
        n=sum(1 for x in cls[k] if x[1]); print(f'   of these, {n} call a changed function in their own text; {len(cls[k])-n} only import a changed module')
    else:
        for rel,calls,c1,c2,e in cls[k]: print(f'   {rel}: calls {calls}; exit {c1} -> {c2}; {e}')
print('\ntotal', sum(len(v) for v in cls.values()))
