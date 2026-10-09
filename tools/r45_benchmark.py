#!/usr/bin/env python3
"""Round 45 controlled compile/runtime A/B benchmark (development tooling only).

Example:
 python3 tools/r45_benchmark.py --baseline /tmp/base --candidate /tmp/new \
   --runs 41 --warmup 5 --csv /tmp/r45_samples.csv --summary /tmp/r45_summary.json

Measures *separate* compiler execution and native-program runtime with
alternating A/B order, CPU pinning if permitted, identical sources/output names,
recorded golden output checks and byte-for-byte emitted binary checks.
Does not assert a speedup where host noise exceeds the observed difference.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, os, platform, statistics, subprocess, tempfile, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PROGRAMS=("07_module","163_r40_transitive_diamond","126_numeric_pipeline",
          "114_perf_loop_fastpaths","109_t18_kosh_dasham")
def percentile(v,q):
    s=sorted(v);p=(len(s)-1)*q;i=int(p);j=min(i+1,len(s)-1)
    return s[i]+(s[j]-s[i])*(p-i)
def measure(cmd,*,cwd=None):
    t=time.perf_counter_ns()
    q=subprocess.run(cmd,cwd=cwd or ROOT,stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE,timeout=90)
    return (time.perf_counter_ns()-t)/1e6,q
def ensure(result,name):
    ms,q=result
    if q.returncode!=0:raise RuntimeError(f"{name}: exit {q.returncode}: {q.stderr[:500]!r}")
    return ms,q
def brief(v):
    return {"n":len(v),"min_ms":min(v),"p10_ms":percentile(v,.1),
      "median_ms":statistics.median(v),"p90_ms":percentile(v,.9),
      "max_ms":max(v),"spread_ms":max(v)-min(v)}
def verify_golden(name,p):
    expected=(ROOT/"tests"/"expect"/(name+".out")).read_bytes()
    exitcode=int((ROOT/"tests"/"expect"/(name+".exit")).read_text().strip())
    ms,q=measure([str(p)])
    if q.stdout!=expected or q.returncode!=exitcode:
        raise AssertionError(f"{name}: expected {expected!r} rc={exitcode}; got {q.stdout!r} rc={q.returncode}")
    return ms
def one(args):
    cpu=None
    if hasattr(os,"sched_getaffinity"):
        allowed=sorted(os.sched_getaffinity(0))
        if allowed:
            try:
                os.sched_setaffinity(0,{allowed[0]})
                cpu=allowed[0]
            except OSError: pass
    base=args.baseline.resolve();new=args.candidate.resolve()
    if not base.is_file() or not new.is_file():raise ValueError("both compiler executables must exist")
    allrows=[];details={}
    with tempfile.TemporaryDirectory(prefix="sutram-r45-") as folder:
        td=Path(folder)
        for name in PROGRAMS:
            src=ROOT/"examples"/(name+".sm")
            outs={"A":td/(name+"_A.bin"),"B":td/(name+"_B.bin")}
            comp={"A":base,"B":new}
            for tag in ("A","B"):
                for _ in range(args.warmup):ensure(measure([str(comp[tag]),str(src),str(outs[tag])]),name+" warm")
                verify_golden(name,outs[tag])
            if outs["A"].read_bytes()!=outs["B"].read_bytes():
                raise AssertionError(f"{name}: compiled ELF differs BEFORE timing")
            baseline_hash=hashlib.sha256(outs["A"].read_bytes()).hexdigest()
            for phase in ("compile","run"):
                for warm in range(args.warmup):
                    for tag in (("A","B") if warm%2==0 else ("B","A")):
                        cmd=[str(comp[tag]),str(src),str(outs[tag])] if phase=="compile" else [str(outs[tag])]
                        ensure(measure(cmd),name+" "+phase+" warm")
                for pair in range(args.runs):
                    order=("A","B") if pair%2==0 else ("B","A")
                    for tag in order:
                        cmd=[str(comp[tag]),str(src),str(outs[tag])] if phase=="compile" else [str(outs[tag])]
                        dt,_=ensure(measure(cmd),name+" "+phase)
                        allrows.append({"program":name,"phase":phase,"pair":pair,"variant":tag,
                            "time_ms":f"{dt:.9f}","cpu":cpu if cpu is not None else "unpinned"})
            if outs["A"].read_bytes()!=outs["B"].read_bytes():
                raise AssertionError(f"{name}: compiled ELF differs AFTER timing")
            details[name]={"elf_sha256_both":baseline_hash}
    for name in PROGRAMS:
        for phase in ("compile","run"):
            x={tag:[float(r["time_ms"]) for r in allrows if r["program"]==name and r["phase"]==phase and r["variant"]==tag] for tag in ("A","B")}
            a,b=brief(x["A"]),brief(x["B"])
            ratio=a["median_ms"]/b["median_ms"]
            details[name][phase]={"baseline":a,"candidate":b,
                "median_speedup_x":ratio,"median_delta_ms":a["median_ms"]-b["median_ms"],
                "note":"Measurements from hosted runner; jitter may exceed effect"}
            print(f"R45 {name} {phase}: A median {a['median_ms']:.5f} ms, "
                  f"B median {b['median_ms']:.5f} ms, A/B {ratio:.3f}x, "
                  f"p10/p90 A={a['p10_ms']:.4f}/{a['p90_ms']:.4f} "
                  f"B={b['p10_ms']:.4f}/{b['p90_ms']:.4f}")
    payload={"baseline":str(base),"candidate":str(new),"host":platform.uname()._asdict(),
             "cpus_pinned":cpu,"runs_per_variant":args.runs,"warmup_per_variant":args.warmup,
             "programs":details,"method":"alternating paired subprocess calls, entire process wall time; compare identical ELF hashes"}
    args.csv.parent.mkdir(parents=True,exist_ok=True)
    with args.csv.open("w",newline="") as file:
        w=csv.DictWriter(file,fieldnames=["program","phase","pair","variant","time_ms","cpu"]);w.writeheader();w.writerows(allrows)
    args.summary.write_text(json.dumps(payload,indent=2))
    print(f"R45 RAW_ROWS={len(allrows)} CSV_SHA256={hashlib.sha256(args.csv.read_bytes()).hexdigest()}")
    print("R45 VERIFY: all 5 emitted ELF binaries byte-identical and existing goldens matched.")
    return 0
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--baseline",type=Path,required=True);p.add_argument("--candidate",type=Path,required=True)
    p.add_argument("--runs",type=int,default=41);p.add_argument("--warmup",type=int,default=5)
    p.add_argument("--csv",type=Path,default=Path("/tmp/r45_samples.csv"))
    p.add_argument("--summary",type=Path,default=Path("/tmp/r45_summary.json"))
    a=p.parse_args()
    if a.runs<10 or a.warmup<2:p.error("requires >=10 runs and >=2 warmups")
    return one(a)
if __name__=="__main__":raise SystemExit(main())
