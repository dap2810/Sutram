# R76: kuttaka (600 random cases) and meru (every C(n, k), n <= 70) against Python's exact integers.
# usage: crosscheck.py COMPILER
import random,math,subprocess,sys
C=sys.argv[1]; T='/tmp/claude-0/-home-claude/e35834e8-b611-5238-b1df-59668dfdca3d/scratchpad/r76/cc'
M=2**63-1; rnd=random.Random(76)
def lit(v): return str(v) if v>=0 else f'0 - {-v}'
cases=[]
while len(cases)<600:
    kind=rnd.randrange(4)
    if kind==0: a,b,c=rnd.randint(-50,50),rnd.randint(-50,50),rnd.randint(-100,100)
    elif kind==1: a,b,c=rnd.randint(-M,M),rnd.randint(-M,M),rnd.randint(-M,M)
    elif kind==2: g=rnd.randint(2,1000); a,b=g*rnd.randint(-10**15,10**15),g*rnd.randint(-10**15,10**15); c=g*rnd.randint(-10**12,10**12)
    else: a,b,c=rnd.randint(-M,M),rnd.choice([M,-M,M-1,2**62+1,-(2**62+3)]),rnd.randint(-M,M)
    g=math.gcd(a,b)
    if g==0 or b==0 or c%g: continue
    cases.append((a,b,c))
bad=[0,0,0,0];tot=[0,0,0,0];kinds=[]
rnd2=random.Random(76)
for start in range(0,600,150):
    chunk=cases[start:start+150]
    open(T+'.sm','w').write('yoj ganita\nmukhya() {\n'+''.join(f'    likha(kuttaka({lit(a)}, {lit(b)}, {lit(c)}), "\\n")\n' for a,b,c in chunk)+'}\n')
    subprocess.run([C,T+'.sm',T],capture_output=True,check=True)
    out=[l for l in subprocess.run([T],capture_output=True,text=True).stdout.split('\n') if l.strip()]
    for (a,b,c),v in zip(chunk,out):
        x=int(v); m=abs(b); big=m>2**40
        tot[big]+=1
        if not ((a*x-c)%m==0 and 0<=x<m): bad[big]+=1
print(f'kuttaka: |b| <= 2^40: {tot[0]-bad[0]}/{tot[0]} correct;  |b| > 2^40: {tot[1]-bad[1]}/{tot[1]} correct')
open(T+'.sm','w').write('yoj chandas\nmukhya() {\n    vitti n = 0\n    yavat (n <= 70) {\n        vitti k = 0\n        yavat (k <= n) {\n            likha(meru(n, k), "\\n")\n            k = k + 1\n        }\n        n = n + 1\n    }\n}\n')
subprocess.run([C,T+'.sm',T],capture_output=True,check=True)
out=[l for l in subprocess.run([T],capture_output=True,text=True).stdout.split('\n') if l.strip()]
k=0;fit=[0,0];over=[0,0];ex=None
for n in range(71):
    for kk in range(n+1):
        ref=math.comb(n,kk); v=out[k].strip(); k+=1
        if ref<=M: fit[0]+=1; fit[1]+= v==str(ref)
        else:
            over[0]+=1; over[1]+= v=='-1'
            if ex is None: ex=(n,kk,v,ref)
print(f'meru: answers that fit in int64: {fit[1]}/{fit[0]} right;  answers too large: {over[1]}/{over[0]} reported as -1  (first: meru{ex[:2]} printed {ex[2]}, true {ex[3]})')
