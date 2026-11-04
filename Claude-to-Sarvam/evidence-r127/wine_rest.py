import glob,os,subprocess,sys
G=sys.argv[1]; NEW='/home/claude/sutram'
PAT=['examples/*.sm','examples/*/*.sm','tests/stdlib/*.sm','tests/r*/*.sm','tests/r*/*/*.sm']
rels=sorted({os.path.relpath(p,NEW) for pat in PAT for p in glob.glob(os.path.join(NEW,pat))})
same=diff=refsame=0
for i,rel in enumerate(rels):
    w=f'{G}/gwine/{i}.new.exe'
    if os.path.exists(w) or os.path.exists(f'{G}/gwine/{i}.done'): continue
    lin=f'{G}/g-pe/{i}.new.exe'
    if not os.path.exists(f'{G}/g-pe/{i}.old.exe') and not os.path.exists(lin):
        lin=f'{G}/lin_{i}.exe'; subprocess.run([NEW+'/sutram_compiler',os.path.join(NEW,rel),lin],cwd=NEW,capture_output=True)
    r=subprocess.run([G+'/w/new.sh',os.path.join(NEW,rel),w],cwd=NEW,capture_output=True,timeout=120)
    if not os.path.exists(lin) and not os.path.exists(w): refsame+=1
    elif os.path.exists(lin) and os.path.exists(w) and open(lin,'rb').read()==open(w,'rb').read(): same+=1
    else: diff+=1; print('DIFF',rel,r.returncode,flush=True)
    open(f'{G}/gwine/{i}.done','w').close()
print(f'rest: {same} identical to the Linux PE, {refsame} refused by both, {diff} differ')
