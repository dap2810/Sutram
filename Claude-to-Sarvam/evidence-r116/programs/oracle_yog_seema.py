import random, subprocess, sys
MIN,MAX=-2**63,2**63-1
def lit(v): return '((0 - 9223372036854775807) - 1)' if v==MIN else (str(v) if v>=0 else f'(0 - {-v})')
def ref(a,b):
    if b<a: return 0
    s=(a+b)*(b-a+1)//2
    return max(MIN,min(MAX,s))
random.seed(116)
cases=[(2**62,2**62),(MIN,MAX),(MIN+2,MAX),(MIN,MIN),(MAX,MAX),(0,4294967296),(-5,5),(-5,4),(-4,5),(1,10),(MIN,0),(0,MAX),(MIN+1,MAX),(-1,0),(MAX-1,MAX),(MIN,MIN+1),(3,2),(-2**62,-2**62),(-2**62-1,-2**62-1), (2**62, 2**62+1)]
specials=[MIN,MIN+1,MIN+2,-2**62-1,-2**62,-2**32,-3,-2,-1,0,1,2,3,2**32,2**62-1,2**62,2**62+1,MAX-2,MAX-1,MAX]
for x in specials:
    for y in specials: cases.append((x,y))
for _ in range(300):
    k=random.choice([2,10,32,40,62,63])
    a=random.randint(-2**k,2**k-1); b=random.randint(-2**k,2**k-1)
    a=max(MIN,min(MAX,a)); b=max(MIN,min(MAX,b))
    cases.append((min(a,b),max(a,b)) if random.random()<0.9 else (a,b))
bad=[];tot=0
for c0 in range(0,len(cases),100):
    ch=cases[c0:c0+100]
    src='yoj sadhan\n\nmukhya() {\n'+''.join(f'    likha(yog_seema({lit(a)}, {lit(b)}))\n' for a,b in ch)+'}\n'
    open(sys.argv[2]+'/ys.sm','w').write(src)
    r=subprocess.run([sys.argv[1],sys.argv[2]+'/ys.sm',sys.argv[2]+'/ys.bin'],capture_output=True,text=True,cwd='.')
    assert r.returncode==0, r.stdout
    out=subprocess.run([sys.argv[2]+'/ys.bin'],capture_output=True,text=True).stdout.split()
    tot+=len(out)
    bad+=[(a,b,o,ref(a,b)) for (a,b),o in zip(ch,out) if int(o)!=ref(a,b)]
print(len(cases),tot,'bad',len(bad)); print(bad[:10])
