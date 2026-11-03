import math, random, subprocess, sys, json
MIN,MAX=-2**63,2**63-1
C,D=sys.argv[1],sys.argv[2]
def lit(v): return '((0 - 9223372036854775807) - 1)' if v==MIN else (str(v) if v>=0 else f'(0 - {-v})')
def ref(a,b,c,d):
    if not (a>0 and b>0 and c>0 and d>=0): return 'inv'
    T=a+b+c+d; F=[T-2*x for x in (a,b,c,d)]
    if min(F)<0: return 'inv'
    P=F[0]*F[1]*F[2]*F[3]; A=math.isqrt(P)//4
    return 'big' if A>MAX else A
def run(src):
    open(D+'/bk.sm','w').write(src)
    r=subprocess.run([C,D+'/bk.sm',D+'/bk.bin'],capture_output=True,text=True)
    assert r.returncode==0,r.stdout
    return subprocess.run([D+'/bk.bin'],capture_output=True,text=True)
random.seed(8)
cases=[(1,1,2,3),(2,3,4,0),(3,3,3,3),(1,1,1,3),(3,4,5,0),(MAX,MAX,MAX,MAX),(MAX,MAX,1,1),(MAX,MAX,MAX,0),(2**31,2**31,2**31,2**31),(2**32,2**32,2**32,2**32),(3037000499,3037000499,3037000499,3037000499),(3037000500*2,3037000500*2,3037000500*2,3037000500*2),(1,MAX,MAX,1),(5,5,1,0)]
for _ in range(400):
    k=random.choice([3,10,20,31,32,33,40,63])
    s=[random.randint(1,min(MAX,2**k)) for _ in range(4)]
    if random.random()<0.2: s[3]=0
    cases.append(tuple(s))
# boundary: squares s,s,s,s area s^2; MAX boundary near s = 3037000499
for s in range(3037000495,3037000505): cases.append((s,s,s,s))
ok=[c for c in cases if ref(*c) not in ('inv','big')]
bad=0
for i in range(0,len(ok),80):
    ch=ok[i:i+80]
    out=run('yoj ganita\n\nmukhya() {\n'+''.join(f'    likha(brahmagupta_kshetr({", ".join(lit(x) for x in c)}))\n' for c in ch)+'}\n').stdout.split()
    for c,o in zip(ch,out):
        if int(o)!=ref(*c): bad+=1; print('BAD',c,o,ref(*c))
    if len(out)!=len(ch): bad+=1; print('short',len(out),len(ch))
print('ok cases',len(ok),'bad',bad)
d=json.load(open('ChatGPT-to-Sarvam/ROUND-189-IMPLEMENTATION-MATRIX.json'))
M=[r for r in d['rows'] if r['function']=='brahmagupta_kshetr'][0]['message']; INV=d['invalid_input_message'].format(function='brahmagupta_kshetr')
rf=[c for c in cases if ref(*c) in ('inv','big')][:12]+[(0-5,3,3,3),(3,0,3,3),(3,3,3,0-1),(1,2,10,3),(1,2,3,0),(1,1,10,0),(0,0,0,0)]
for c in rf:
    r=run('yoj ganita\n\nmukhya() {\n    likha(brahmagupta_kshetr('+', '.join(lit(x) for x in c)+'))\n}\n')
    want=M if ref(*c)=='big' else INV
    g= r.returncode==1 and r.stdout=='' and r.stderr==want+'\n'
    print('PASS' if g else 'FAIL', c, ref(*c), r.returncode, r.stdout.strip(), r.stderr.strip()[:40])
