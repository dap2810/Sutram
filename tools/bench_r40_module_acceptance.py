#!/usr/bin/env python3
"""ACCEPTANCE ONLY: benchmark a NASM-rebuilt R40 compiler against verified R39.

Usage: python3 tools/bench_r40_module_acceptance.py /path/to/verified /path/to/new
No Python is used by Sutram-generated programs or the production compiler.
"""
from pathlib import Path
import hashlib,os,subprocess,sys,tempfile,time
ROOT=Path(__file__).resolve().parents[1]
LEGACY=['07_module.sm','66_module_dedupe.sm','126_numeric_pipeline.sm']
NEW='163_r40_transitive_diamond.sm'

def percentile(xs,p):
    z=sorted(xs); k=(len(z)-1)*p;i=int(k);j=min(len(z)-1,i+1)
    return z[i]+(z[j]-z[i])*(k-i)

def compile(compiler,source,out):
    p=subprocess.run([str(compiler),str(ROOT/'examples'/source),str(out)],cwd=ROOT,capture_output=True,text=True,timeout=40)
    if p.returncode:raise AssertionError(f'{source}: compiler exit {p.returncode}\n{p.stdout}\n{p.stderr}')
    return out.read_bytes()

def run(out):
    p=subprocess.run([str(out)],capture_output=True,text=True,timeout=60)
    if p.returncode:raise AssertionError(f'{out} runtime exit {p.returncode}: {p.stderr}')
    return p.stdout

def main(a,b):
    old,new=Path(a).resolve(),Path(b).resolve()
    if hasattr(os,'sched_setaffinity'):
        try:os.sched_setaffinity(0,{min(os.sched_getaffinity(0))})
        except OSError:pass
    with tempfile.TemporaryDirectory(prefix='sutram-r40-') as tmp:
        tmp=Path(tmp)
        for source in LEGACY:
            x,y=tmp/'old.bin',tmp/'new.bin'
            ob=compile(old,source,x);nb=compile(new,source,y)
            if ob!=nb:raise AssertionError(f'legacy changed unexpectedly: {source}; sha old={hashlib.sha256(ob).hexdigest()} new={hashlib.sha256(nb).hexdigest()}')
            if run(x)!=run(y):raise AssertionError(f'legacy stdout differs: {source}')
            print(f'PASS byte-identical {source} ({len(ob)} bytes)')
        y=tmp/'new.bin';compile(new,NEW,y)
        stdout=run(y)
        assert stdout=='17\n7\n',f'R40 diamond output: {stdout!r}'
        print(f'PASS R40 transitive import golden {NEW}: {stdout!r}')
        old_bin,new_bin=tmp/'old.bin',tmp/'new.bin'
        compile(old,LEGACY[-1],old_bin);compile(new,LEGACY[-1],new_bin)
        for _ in range(3):run(old_bin);run(new_bin)
        a_times=[];b_times=[]
        for i in range(12):
            pairs=[(old_bin,a_times),(new_bin,b_times)]
            if i%2:pairs.reverse()
            for prog,arr in pairs:
                start=time.perf_counter_ns();run(prog)
                arr.append((time.perf_counter_ns()-start)/1e6)
        for name,vals in [('before',a_times),('after',b_times)]:
            print(f'{name} 126: min={min(vals):.3f}ms p10={percentile(vals,0.10):.3f}ms')
        print('PASS: legacy output byte identity, new diamond output, pinned interleaved benchmark')
if __name__=='__main__':
    if len(sys.argv)!=3:raise SystemExit(__doc__)
    main(sys.argv[1],sys.argv[2])
