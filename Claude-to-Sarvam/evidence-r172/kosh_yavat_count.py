# how many of the guard's programs declare a kosh inside any loop (chakra or yavat) - a textual screen by indentation/braces
import re,os,sys
S=sys.argv[1]; W=S+'/r172/wt'
rows=[l.split() for l in open(S+'/r172/guard_elf.txt') if l.startswith(('IDENTICAL','REFUSED'))]
hits=[]
for st,rel,*_ in rows:
    t=open(os.path.join(W,rel),encoding='utf-8',errors='replace').read()
    stack=[]; hit=None
    for l in t.split('\n'):
        l=l.split('#')[0]
        if not l.strip(): continue
        ind=len(l)-len(l.lstrip())
        stack=[(i,k) for i,k in stack if i<ind]
        m=re.match(r'\s*(chakra|yavat|चक्र|यावत्)\b',l)
        if m: stack.append((ind,m.group(1)))
        elif re.match(r'\s*(kosh|कोश)\s',l) and stack: hit=stack[-1][1]
    if hit: hits.append((st,rel,hit))
print(f'{len(rows)} programs; {len(hits)} declare a kosh on a line inside a loop:')
for h in hits: print('  ',*h)
