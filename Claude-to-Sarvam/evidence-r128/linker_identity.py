import subprocess,os,sys,glob,random
G,linker=sys.argv[1],sys.argv[2]
W='/usr/lib/wine/wine64'; env=dict(os.environ)
progs=sorted(glob.glob('examples/[0-9]*.sm')); random.seed(128); progs=random.sample(progs,30)+['examples/288_r86_kosh_alias_moves.sm','examples/255_r42_alias_kosh_push.sm']
same=diff=skip=0
for p in progs:
    d=G+'/d.exe'; o=G+'/o.smo'; l=G+'/l.exe'
    for f in (d,o,l):
        if os.path.exists(f): os.remove(f)
    r=subprocess.run([W,'win/sutram.exe',p,d],capture_output=True,env=env,timeout=120)
    if r.returncode or not os.path.exists(d): skip+=1; continue
    subprocess.run([W,'win/sutram.exe','--object',p,o],capture_output=True,env=env,timeout=120)
    subprocess.run([W,linker,l,o],capture_output=True,env=env,timeout=120)
    ok=os.path.exists(l) and open(l,'rb').read()==open(d,'rb').read()
    same+=ok; diff+=not ok
    if not ok: print('DIFFER',p)
print(f'{os.path.basename(linker)}: {same} linked = direct compile byte for byte, {diff} differ, {skip} not compiled directly')
