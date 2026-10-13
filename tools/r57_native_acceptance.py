#!/usr/bin/env python3
"""R57 native A/B: compare actual stdout, generated code and 10M-loop times.
Benchmarks are development-only; only src/sutram_compiler.asm is the compiler.
A measured speedup must come from the real executable, not modeled estimates.
"""
from __future__ import annotations
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import os
import statistics
import subprocess
import time
ROOT = Path(__file__).resolve().parents[1]
BEFORE = ROOT/"r57_before"
AFTER = ROOT/"r48_after"
FIX = ROOT/"tests"/"r57_check"
CASES = {
 "arithmetic_10m.sm":"99999990000000\n",
 "control_10m.sm":"49999995000000\n",
 "nested_registers.sm":"77\n4\n7\n-23\n21\n",
 "legacy_fallback.sm":"7\n4\n6\n",
 "large_literals.sm":"23622320128\n4294967307\n33\n",
 "global_registers.sm":"99\n30\n17\n10\n20\n",
}
REFERENCE = [
 "examples/41_recursion.sm",
 "examples/126_numeric_pipeline.sm",
 "examples/163_r40_transitive_diamond.sm",
 "examples/111_t18_kosh_dasham_function_return.sm",
]
def execute(argv, timeout=60):
    return subprocess.run(list(map(str,argv)),cwd=ROOT, text=True,
                          capture_output=True, timeout=timeout)
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def time_bin(path,expected):
    t=time.perf_counter_ns()
    cp=execute([path],timeout=60)
    ms=(time.perf_counter_ns()-t)/1e6
    assert cp.returncode==0 and cp.stdout==expected,(
        path,cp.returncode,repr(cp.stdout),repr(expected),repr(cp.stderr))
    return ms
def check():
    if hasattr(os,"sched_setaffinity") and hasattr(os,"sched_getaffinity"):
        try:
            cpu=min(os.sched_getaffinity(0))
            os.sched_setaffinity(0,{cpu})
            print("R57_CPU_PIN",cpu,flush=True)
        except OSError as ex:
            print("R57_CPU_PIN unavailable",repr(ex),flush=True)
    assert BEFORE.is_file() and AFTER.is_file()
    with TemporaryDirectory(prefix="sutram-r57-") as tmp:
        tmp=Path(tmp)
        timings={}
        for name,expected in CASES.items():
            bins={}
            for label,compiler in (("before",BEFORE),("after",AFTER)):
                output=tmp/(name+"_"+label+".elf")
                r=execute([compiler,FIX/name,output])
                assert r.returncode==0 and output.is_file(),(name,label,r.stdout,r.stderr)
                print("R57_COMPILE",name,label,"exit",r.returncode,
                      "sha256",sha(output),"bytes",output.stat().st_size,flush=True)
                bins[label]=output
                cp=execute([output])
                print("R57_STDOUT",name,label,cp.returncode,repr(cp.stdout),flush=True)
                assert cp.returncode==0 and cp.stdout==expected,(
                    name,label,repr(cp.stdout),repr(expected))
            if name == "arithmetic_10m.sm":
                # Compiler output bytes: the original generic tree used
                # POP RDX / XCHG RAX,RDX after PUSH RAX; the R57 pure-register
                # expression tree must not contain that operand roundtrip.
                old=bins["before"].read_bytes()
                new=bins["after"].read_bytes()
                assert bytes.fromhex("5a 48 87 d0") in old
                assert bytes.fromhex("5a 48 87 d0") not in new
                assert bytes.fromhex("4c 01 d0") in new
                print("R57_CODE_SHAPE old_pop_xchg=1 new_pop_xchg=0 new_add_rax_r10=1",flush=True)
            if name in ("arithmetic_10m.sm","control_10m.sm"):
                for label in ("before","after"):
                    time_bin(bins[label],expected)
                results={"before":[],"after":[]}
                for repeat in range(3):
                    order=("before","after") if repeat%2==0 else ("after","before")
                    for label in order:
                        results[label].append(time_bin(bins[label],expected))
                before=min(results["before"])
                after=min(results["after"])
                timings[name]=(before,after)
                print("R57_TIMING",name,"iterations=10000000",
                      "before_best3_ms=%.6f"%before,"after_best3_ms=%.6f"%after,
                      "speedup=%.4fx"%(before/after),
                      "before_samples_ms="+repr(results["before"]),
                      "after_samples_ms="+repr(results["after"]),flush=True)
        different=0
        for sample in REFERENCE:
            ref=ROOT/sample
            outputs=[]
            hashes=[]
            for label,compiler in (("R46",ROOT/"r48_before"),("R57",AFTER)):
                output=tmp/(ref.stem+"_"+label+".elf")
                c=execute([compiler,ref,output])
                assert c.returncode==0 and output.is_file(),(sample,label,c.stdout,c.stderr)
                p=execute([output])
                assert p.returncode==0,(sample,label,p.stdout,p.stderr)
                outputs.append(p.stdout)
                hashes.append(sha(output))
            assert outputs[0]==outputs[1],(sample,repr(outputs[0]),repr(outputs[1]))
            changed=hashes[0]!=hashes[1]
            different+=int(changed)
            print("R57_R46_STDOUT",sample,repr(outputs[1]),"parity",1,
                  "r46_sha256",hashes[0],"r57_sha256",hashes[1],
                  "new_baseline_candidate",1,flush=True)
        print("R57_R46_OUTPUT_ACCEPTED samples",len(REFERENCE),
              "different_binaries",different,flush=True)
        print("R57_RESULT arithmetic_speedup=%.4fx"%(timings["arithmetic_10m.sm"][0]/
                                                      timings["arithmetic_10m.sm"][1]),
              "control_ratio=%.4fx"%(timings["control_10m.sm"][0]/
                                     timings["control_10m.sm"][1]),
              "native_cases",len(CASES),"reference_stdout",len(REFERENCE),flush=True)
if __name__=="__main__":
    check()
