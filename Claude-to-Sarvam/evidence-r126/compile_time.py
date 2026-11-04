import subprocess,glob,os,time,sys
G=sys.argv[1]
PAT=['examples/*.sm','tests/stdlib/*.sm','tests/r*/*.sm','tests/r*/*/*.sm']
progs=sorted({os.path.abspath(p) for pat in PAT for p in glob.glob(pat)})
comps={'v300':G+'/old/sutram_compiler','new':G+'/old/sc_new'}
res={k:[] for k in comps}
for rnd in range(3):
    for k,c in comps.items():
        t=time.perf_counter()
        for p in progs:
            subprocess.run([c,p,G+'/ct.bin'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,cwd=os.path.dirname(p))
        res[k].append(time.perf_counter()-t)
print(len(progs),'programs, each compiled once per run, 3 runs alternating')
for k,v in res.items(): print(k,' '.join(f'{x:.2f}s' for x in v),'min %.2fs'%min(v))
# the largest program alone, 20 times
big=max(progs,key=os.path.getsize)
for k,c in comps.items():
    t=time.perf_counter()
    for i in range(20): subprocess.run([c,big,G+'/ct.bin'],stdout=subprocess.DEVNULL,cwd=os.path.dirname(big))
    print(k,'largest program',os.path.relpath(big),'20 compiles %.3fs'%(time.perf_counter()-t))
