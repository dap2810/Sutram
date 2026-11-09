import os, subprocess, time, sys, json
def once(b):
    t=time.perf_counter()
    p=subprocess.Popen([b], env={}, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out=p.stdout.read()
    _, st, ru = os.wait4(p.pid, 0)
    return time.perf_counter()-t, ru.ru_maxrss, os.waitstatus_to_exitcode(st), out.decode().strip().replace('\n',' ')
res={}
progs=['Z']+[f'{k}{n}' for k in 'ABCDGM' for n in (50000,200000,800000)]
for rep in range(5):
    for pr in progs:
        res.setdefault(pr,[]).append(once('./'+pr+'.bin'))
for pr in progs:
    r=res[pr]
    print(f"{pr:9s} exit {sorted(set(x[2] for x in r))} out {r[0][3]!r:28s} rss KB {[x[1] for x in r]}  wall ms {[round(x[0]*1000,1) for x in r]}  best {min(x[0] for x in r)*1000:.1f}")
json.dump({k:[list(x) for x in v] for k,v in res.items()}, open('runs.json','w'))
