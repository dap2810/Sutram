#!/usr/bin/env python3
"""R169: current resident memory at named points of a running Sutram program.
The program prints a number and waits on grahan() (a read from standard input) at each point; while it waits this
reads /proc/<pid>/status (VmRSS, VmHWM, VmSize) and /proc/<pid>/smaps_rollup (Anonymous), then sends "0" so it
goes on. The time between sending "0" and the next point is the work between the two points, with no pause in it.
Usage: probe.py PROGRAM [RUNS]   (empty environment)"""
import os, subprocess, sys, time, json

def status(pid):
    d = {}
    for line in open(f'/proc/{pid}/status'):
        k, _, v = line.partition(':')
        if k in ('VmRSS', 'VmHWM', 'VmSize'):
            d[k] = int(v.split()[0])
    for line in open(f'/proc/{pid}/smaps_rollup'):
        if line.startswith('Anonymous:'):
            d['Anon'] = int(line.split()[1])
    return d

def run(prog):
    p = subprocess.Popen([prog], env={}, stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=0)
    pts, t0 = [], time.perf_counter()
    while True:
        line = p.stdout.readline()
        if not line:
            break
        t1 = time.perf_counter()
        st = status(p.pid)
        pts.append({'point': line.decode().strip(), 'ms_since_previous': round((t1 - t0) * 1000, 2), **st})
        p.stdin.write(b'0\n')
        t0 = time.perf_counter()
    p.wait()
    return pts, p.returncode

if __name__ == '__main__':
    prog, runs = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 3
    allruns = []
    for r in range(runs):
        pts, rc = run(prog)
        allruns.append({'run': r + 1, 'exit': rc, 'points': pts})
        print(f'run {r + 1} exit {rc}: ' + ' | '.join(
            f"{x['point']}: RSS {x['VmRSS']:,} KB (anon {x['Anon']:,}, HWM {x['VmHWM']:,}, size {x['VmSize']:,}) +{x['ms_since_previous']} ms" for x in pts))
    json.dump(allruns, open(os.path.basename(prog) + '.json', 'w'), indent=1)
