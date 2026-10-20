#!/usr/bin/env python3
"""R15-01 D4: for every ordered pair of 16 binary operators, one program line whose value
differs between (x A y) B z and x A (y B z); prints the pairs that disagree with the documented
table. usage (repository root): python3 -B Claude-to-Sarvam/evidence-r15/valid/precedence_pairs.py OUTDIR"""
import itertools, random, subprocess, sys
sys.path.insert(0,'tools'); random.seed(15); import fuzz_valid as fv
ops=['||','&&','|','^','&','==','!=','<','<=','<<','>>','+','-','*','/','%']
def ev(a,op,b):
    if op in('/','%') and b==0: return None
    return fv.binop(op,a,b)
T = fv.PREC_MEASURED if "--measured" in sys.argv else fv.PREC_DOCUMENTED
lines=[];meta=[]
for A,B in itertools.permutations(ops,2):
    # find x,y,z distinguishing (x A y) B z  from x A (y B z)
    for t in range(2000):
        x,y,z=[random.randint(-6,9) for _ in range(3)]
        l1=ev(x,A,y); l=None if l1 is None else ev(l1,B,z)
        r1=ev(y,B,z); r=None if r1 is None else ev(x,A,r1)
        if l is not None and r is not None and l!=r:
            lines.append('    likha(%d %s %d %s %d)'%(x,A,y,B,z)); meta.append((A,B,l,r)); break
    # same-op associativity handled by permutations? add A,A
for A in ops:
    for t in range(2000):
        x,y,z=[random.randint(-6,9) for _ in range(3)]
        l1=ev(x,A,y); l=None if l1 is None else ev(l1,A,z)
        r1=ev(y,A,z); r=None if r1 is None else ev(x,A,r1)
        if l is not None and r is not None and l!=r:
            lines.append('    likha(%d %s %d %s %d)'%(x,A,y,A,z)); meta.append((A,A,l,r)); break
open(sys.argv[1]+'/prec.sm','w').write('mukhya() {\n'+'\n'.join(lines)+'\n}\n')
subprocess.run(['./sutram_compiler',sys.argv[1]+'/prec.sm',sys.argv[1]+'/prec.bin'],check=True,capture_output=True)
out=subprocess.run([sys.argv[1]+'/prec.bin'],capture_output=True,text=True).stdout.split()
tight={}
bad=[]
for (A,B,l,r),o,src in zip(meta,out,lines):
    o=int(o)
    doc_left = T[A] >= T[B]   # doc: left-assoc, A binds first if prec >= 
    got = 'left' if o==l else 'right' if o==r else 'neither(%d)'%o
    want='left' if doc_left else 'right'
    if got!=want: bad.append((A,B,want,got,src.strip()))
print(len(meta),'pairs tested;',len(bad),'disagree with the',('measured' if T is fv.PREC_MEASURED else 'documented'),'table')
for b in bad: print(*b)
