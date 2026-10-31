# R79: an independent Python implementation of the marks report, for checking report_plain.sm / report_blocks.sm.
# usage: python3 reference.py INPUT_FILE
import sys
d=[int(x) for x in open(sys.argv[1]).read().split()]
n=d[0]; st=[(d[1+4*i],d[2+4*i],d[3+4*i],d[4+4*i]) for i in range(n)]
out=[]
col=lambda v,w: str(v).rjust(w)
out.append('subject    mean  median  lowest highest\n')
for k,name in ((1,'ganita  '),(2,'vijnana '),(3,'bhasha  ')):
    v=[s[k] for s in st]; sv=sorted(v,reverse=True)
    med=sv[n-1-(n-1)//2]
    out.append(name+col(sum(v)//n,8)+col(med,8)+col(min(v),8)+col(max(v),8)+'\n')
tot=[s[1]+s[2]+s[3] for s in st]
bins=[0]*10
for t in tot: bins[min(9,t//30)]+=1
out.append('totals:\n')
for i in range(10): out.append(col(i*30,4)+'-'+col(i*30+29,3)+col(bins[i],8)+'\n')
def gr(t): return 'A' if t>=270 else 'B' if t>=240 else 'C' if t>=210 else 'D' if t>=180 else 'F'
g={c:0 for c in 'ABCDF'}
for t in tot: g[gr(t)]+=1
out.append(f"grades: A {g['A']}  B {g['B']}  C {g['C']}  D {g['D']}  F {g['F']}\n")
order=sorted(range(n),key=lambda i:(-tot[i],i))
out.append('rank   roll  ganita vijnana bhasha  total grade\n')
for r,i in enumerate(order):
    s=st[i]; out.append(col(r+1,4)+col(s[0],7)+col(s[1],8)+col(s[2],8)+col(s[3],7)+col(tot[i],7)+'     '+gr(tot[i])+'\n')
sys.stdout.write(''.join(out))
