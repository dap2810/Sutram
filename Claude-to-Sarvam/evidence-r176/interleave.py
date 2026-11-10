import subprocess,sys,time
progs=sys.argv[1:]; best={p:[] for p in progs}
for r in range(25):
    for p in progs:
        t=time.perf_counter(); subprocess.run([p],capture_output=True); best[p].append((time.perf_counter()-t)*1000)
print('25 rounds, the programs run in turn; 1,000,000 passes each')
for p in progs:
    v=sorted(best[p]); print(f'{p}: best {v[0]:.1f} ms, 5th of 25 {v[4]:.1f} ms, median {v[12]:.1f} ms')
