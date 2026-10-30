import sys
toks=open(sys.argv[1]).read().replace("CASE"," CASE ").split()
i=0; bad=0; kinds={}; cases=0; zero=0
def expect(s, sep, maxp):
    if maxp<=0: return []
    if len(s)==0: return [""]
    if len(sep)==0: return [s]
    return s.split(sep)[:maxp]
while i<len(toks):
    i+=1; n,spn,maxp=int(toks[i]),int(toks[i+1]),int(toks[i+2]); i+=3
    chars=[int(x) for x in toks[i:i+n]]; i+=n; sp=[int(toks[i]),int(toks[i+1])][:spn]; i+=2
    s="".join(map(chr,chars)); sep="".join(map(chr,sp)); exp=expect(s,sep,maxp)
    cases+=1; zero+=(maxp==0)
    for fn in range(2):
        cnt=int(toks[i]); i+=1; got=[]
        for g in range(cnt):
            L=int(toks[i]); i+=1; got.append("".join(chr(int(t)) for t in toks[i:i+L])); i+=L
        if got!=exp:
            bad+=1; k=["varna_bhed","khand_bhed"][fn]+(" empty input" if n==0 else " empty separator" if spn==0 else " ordinary")+" maxparts=%d"%maxp
            kinds[k]=kinds.get(k,0)+1
print("%d cases (%d with maxparts=0): %d results differ from str.split truncated to maxparts %s"%(cases,zero,bad,kinds))
