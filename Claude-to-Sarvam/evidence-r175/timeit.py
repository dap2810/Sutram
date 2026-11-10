import subprocess,sys,time
for prog in sys.argv[1:]:
    ts=[]
    for _ in range(7):
        t=time.perf_counter(); r=subprocess.run([prog],capture_output=True,text=True); ts.append((time.perf_counter()-t)*1000)
    ts.sort()
    print(f'{prog}: best {ts[0]:.1f} ms, median {ts[3]:.1f} ms (7 runs), prints {r.stdout.strip()}')
