#!/usr/bin/env python3
"""Pure validation/benchmark tooling; never part of Sutram compiler/runtime.
Usage: python3 tools/module_namespace_ab.py <pre-ns-compiler> <post-ns-compiler>
For old programs, check byte identity and interleaved pinned min/p10.
For new programs, check namespace collision output with post-ns.
"""
from pathlib import Path
import os, subprocess, sys, tempfile, time, statistics, hashlib
ROOT=Path(__file__).resolve().parents[1]
TESTS=['126_numeric_pipeline.sm','07_module.sm','66_module_dedupe.sm']
NEW=[('149_namespaced_colliding_imports.sm','13\n203\n12\n200\n'),('150_namespaced_same_module_two_aliases.sm','13\n13\n'),('151_namespaced_and_legacy_import.sm','13\n203\n')]
def compile_with(compiler, source, output):
    p=subprocess.run([str(compiler),str(ROOT/'examples'/source),str(output)],capture_output=True,text=True,timeout=30)
    if p.returncode: raise RuntimeError(f'{source}: compiler failed: {p.stdout} {p.stderr}')
    return output.read_bytes()
def run_program(path):
    p=subprocess.run([str(path)],capture_output=True,text=True,timeout=60)
    if p.returncode: raise RuntimeError(f'{path.name} exit {p.returncode}: {p.stderr}')
    return p.stdout

def percentile(xs,p):
    xs=sorted(xs); z=(len(xs)-1)*p; lo=int(z);hi=min(lo+1,len(xs)-1)
    return xs[lo]+(xs[hi]-xs[lo])*(z-lo)
def main():
    if len(sys.argv)!=3: raise SystemExit(__doc__)
    old,new=map(lambda s:Path(s).resolve(),sys.argv[1:])
    if hasattr(os,'sched_setaffinity'):
        try: os.sched_setaffinity(0,{min(os.sched_getaffinity(0))})
        except (OSError,ValueError): pass
    with tempfile.TemporaryDirectory(prefix='sutram-ns-') as td:
        td=Path(td)
        for f in TESTS:
            x,y=td/'old.bin',td/'new.bin'
            a=compile_with(old,f,x);b=compile_with(new,f,y)
            if a!=b: raise AssertionError(f'legacy binary changed: {f}: {hashlib.sha256(a).hexdigest()} != {hashlib.sha256(b).hexdigest()}')
            if run_program(x)!=run_program(y): raise AssertionError(f'legacy output changed: {f}')
            print(f'PASS BYTE-IDENTICAL {f}: {len(a)} bytes')
        for f,expected in NEW:
            y=td/'namespaced.bin';compile_with(new,f,y)
            actual=run_program(y)
            if actual!=expected: raise AssertionError(f'{f}: got {actual!r} expected {expected!r}')
            print(f'PASS NAMESPACE {f}: {actual!r}')
        old_path,new_path=td/'old.bin',td/'new.bin'
        compile_with(old,TESTS[0],old_path);compile_with(new,TESTS[0],new_path)
        for _ in range(3):run_program(old_path);run_program(new_path)
        t0=[];t1=[]
        for _ in range(12):
            for path,arr in ((old_path,t0),(new_path,t1)):
                start=time.perf_counter_ns();run_program(path);arr.append((time.perf_counter_ns()-start)/1e6)
        for label,vals in [('before',t0),('after',t1)]:print(f'{label}: min={min(vals):.3f}ms p10={percentile(vals,.10):.3f}ms')
        print('PASS: legacy code shape is unchanged; timing is directional only')
if __name__=='__main__':main()
