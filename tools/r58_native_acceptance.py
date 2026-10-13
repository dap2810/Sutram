#!/usr/bin/env python3
"""Round 58 real ELF A/B; no synthesized timings or self-modifying goldens."""
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import os
import statistics
import subprocess
import time

ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/"r58_before"
NEW=ROOT/"r48_after"
CASES={
 "tests/r58_check/fold_vs_dynamic_folded.sm":"92\n3\n",
 "tests/r58_check/fold_vs_dynamic_dynamic.sm":"92\n3\n",
 "tests/r58_check/div_signed.sm":"-50\n-25\n-12\n-6\n-1\n12\n1\n",
 "tests/r58_check/effectful_identity.sm":"1\n2\n3\n3\n",
 "tests/r58_check/fold_nested.sm":"64\n56\n12\n3\n64\n59\n11\n11\n11\n",
 "tests/r57_check/arithmetic_10m.sm":"99999990000000\n",
 "tests/r57_check/control_10m.sm":"49999995000000\n",
 "tests/r58_check/foldable_10m.sm":"640000000\n",
}
BENCHMARKS=("tests/r57_check/arithmetic_10m.sm",
            "tests/r57_check/control_10m.sm",
            "tests/r58_check/foldable_10m.sm")
def run(args,timeout=90):
    return subprocess.run([str(x) for x in args],cwd=ROOT,capture_output=True,
                          text=True,timeout=timeout)
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def main():
    assert OLD.is_file() and NEW.is_file()
    try:
        cpu=min(os.sched_getaffinity(0))
        os.sched_setaffinity(0,{cpu})
        print("R58_CPU_PIN",cpu,flush=True)
    except (AttributeError,OSError):
        print("R58_CPU_PIN unavailable",flush=True)
    compiled={}
    with TemporaryDirectory(prefix="sutram-r58-") as td:
        tmp=Path(td)
        for source,expected in CASES.items():
            outs={}
            for label,compiler in (("before",OLD),("after",NEW)):
                out=tmp/(Path(source).stem+"_"+label)
                cp=run((compiler,ROOT/source,out))
                assert cp.returncode==0 and out.is_file(),(source,label,cp.stdout,cp.stderr)
                p=run([out])
                assert p.returncode==0 and p.stdout==expected,(
                    source,label,p.returncode,repr(p.stdout),repr(expected),p.stderr)
                print("R58_NATIVE",source,label,
                      "sha256",sha(out),"bytes",out.stat().st_size,
                      "stdout",repr(p.stdout),flush=True)
                outs[label]=out
            compiled[source]=outs
        folded=compiled["tests/r58_check/fold_vs_dynamic_folded.sm"]
        unfolded=compiled["tests/r58_check/fold_vs_dynamic_dynamic.sm"]
        assert folded["after"].stat().st_size<unfolded["after"].stat().st_size
        assert folded["after"].read_bytes()!=folded["before"].read_bytes()
        assert bytes.fromhex("48 d3 e0") in unfolded["after"].read_bytes(), (
            "dynamic left-shift disappeared")
        print("R58_FOLD_DEMO folded_bytes",folded["after"].stat().st_size,
              "unfolded_bytes",unfolded["after"].stat().st_size,
              "folded_changed_vs_before=1",
              "same_stdout=1",flush=True)
        for source in BENCHMARKS:
            outs=compiled[source]
            expected=CASES[source]
            times={"before":[],"after":[]}
            for _ in range(2):
                for label in ("before","after"):
                    p=run([outs[label]])
                    assert p.returncode==0 and p.stdout==expected
            for index in range(3):
                order=("before","after") if index%2==0 else ("after","before")
                for label in order:
                    t=time.perf_counter_ns()
                    p=run([outs[label]])
                    ns=time.perf_counter_ns()-t
                    assert p.returncode==0 and p.stdout==expected
                    times[label].append(ns/1e6)
            b=min(times["before"])
            a=min(times["after"])
            bm=statistics.median(times["before"])
            am=statistics.median(times["after"])
            print("R58_TIMING",source,"iterations=10000000",
                  "before_best3_ms=%.6f"%b,"after_best3_ms=%.6f"%a,
                  "best_speedup=%.4fx"%(b/a),
                  "before_median_ms=%.6f"%bm,"after_median_ms=%.6f"%am,
                  "median_speedup=%.4fx"%(bm/am),
                  "before_samples_ms="+repr(times["before"]),
                  "after_samples_ms="+repr(times["after"]),flush=True)
        print("R58_ACCEPTED native_cases",len(CASES),
              "fold_demo=1 arithmetic_control_foldable_timed=3",flush=True)
if __name__=="__main__":
    main()
