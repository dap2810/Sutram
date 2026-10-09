#!/usr/bin/env python3
"""Round 45: reproducible raw measurements for native Sutram A/B compilation.

The compiler is native NASM; Python is development-only benchmarking.
Compilers for detailed phases are built with -dR45_PROFILE, which emits
R45_STAGE,<stage>,<tsc cycles> after the output file is already written.
Pin to an allowed CPU, warm up, interleave variants in the A/B mode.
Save per-run data, not only aggregate estimates.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import os
from pathlib import Path
import statistics
import subprocess
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parents[1]
NAMES=("126_numeric_pipeline","163_r40_transitive_diamond",
       "110_t18_kosh_dasham_devanagari","114_perf_loop_fastpaths",
       "41_recursion")
STAGES=("graph","expand","lex","parse","gen","write")
COLUMNS=("label","program","kind","iteration","elapsed_ns","stdout_sha256",
         "binary_sha256","native_stdout_sha256","native_exit","cpu",
         *(f"{name}_cycles" for name in STAGES))

def checksum(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def command(cmd,timeout=30):
    start=time.perf_counter_ns()
    p=subprocess.run(cmd,cwd=ROOT,stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE,timeout=timeout)
    return time.perf_counter_ns()-start,p

def profile_lines(output:bytes):
    d={}
    for line in output.decode("utf-8",errors="replace").splitlines():
        if line.startswith("R45_STAGE,"):
            _,name,value=line.split(",")
            d[name]=int(value)
    if set(d)!=set(STAGES):raise RuntimeError(f"Missing TSC stage data: {d}")
    return d

def pinned_cpu():
    if not hasattr(os,"sched_getaffinity"):return "none"
    try:
        cpu=min(os.sched_getaffinity(0))
        os.sched_setaffinity(0,{cpu})
        return str(cpu)
    except (OSError,PermissionError):return "none"

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--compiler",type=Path,required=True)
    parser.add_argument("--other",type=Path)
    parser.add_argument("--label",default="baseline")
    parser.add_argument("--runs",type=int,default=15)
    parser.add_argument("--warmup",type=int,default=4)
    parser.add_argument("--output",type=Path,required=True)
    a=parser.parse_args()
    if a.runs<7 or a.warmup<2:parser.error("requires >=7 runs and >=2 warmups")
    cpu=pinned_cpu()
    programs={p:ROOT/"examples"/(p+".sm") for p in NAMES}
    for p,source in programs.items():
        if not source.is_file():raise RuntimeError(f"Missing source {p}: {source}")
    compilers=[(a.label,a.compiler.resolve())]
    if a.other is not None:
        compilers.append(("optimized",a.other.resolve()))
    for label,exe in compilers:
        if not exe.is_file():raise RuntimeError(f"Missing compiler: {exe}")
    rows=[];outputs={}
    with tempfile.TemporaryDirectory(prefix="sutram-r45-bench-") as d:
        root=Path(d)
        for program,source in programs.items():
            for rep in range(-a.warmup,a.runs):
                # Alternate interleaved A/B order; same physical host, CPU affinity.
                order=compilers if rep%2==0 else list(reversed(compilers))
                for label,exe in order:
                    output=root/(label+"_"+program+".bin")
                    ct,process=command([str(exe),str(source),str(output)],timeout=30)
                    if process.returncode:
                        raise RuntimeError(f"{label}/{program}: compiler {process.returncode}: {process.stdout+process.stderr!r}")
                    stages=profile_lines(process.stdout)
                    emitted=output.read_bytes()
                    digest=checksum(emitted)
                    native_t,native=command([str(output)],timeout=30)
                    if native.returncode:
                        raise RuntimeError(f"{label}/{program}: program rc={native.returncode}: {native.stdout+native.stderr!r}")
                    signature=(digest,checksum(native.stdout),native.returncode)
                    previous=outputs.setdefault(program,signature)
                    if previous!=signature:
                        raise RuntimeError(f"Generated code or stdout changed for {program}, {label}: {signature} != {previous}")
                    if rep>=0:
                        compile_row={"label":label,"program":program,"kind":"compile",
                                     "iteration":rep,"elapsed_ns":ct,
                                     "stdout_sha256":checksum(process.stdout),
                                     "binary_sha256":digest,
                                     "native_stdout_sha256":checksum(native.stdout),
                                     "native_exit":native.returncode,"cpu":cpu}
                        compile_row.update({f"{stage}_cycles":stages[stage] for stage in STAGES})
                        run_row={**compile_row,"kind":"execute","elapsed_ns":native_t}
                        rows.extend((compile_row,run_row))
        a.output.parent.mkdir(parents=True,exist_ok=True)
        with a.output.open("w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=COLUMNS)
            w.writeheader()
            w.writerows(rows)
    print("R45_MACHINE_CPU="+cpu)
    print(f"R45_CSV_FILE={a.output}")
    print("R45_SUMMARY,label,program,kind,median_ns,min_ns,max_ns")
    for label,exe in compilers:
        for program in NAMES:
            for kind in ("compile","execute"):
                x=[r["elapsed_ns"] for r in rows if r["label"]==label and r["program"]==program and r["kind"]==kind]
                print(f"R45_SUMMARY,{label},{program},{kind},{statistics.median(x):.0f},{min(x)},{max(x)}")
            stages={stage:statistics.median(r[f"{stage}_cycles"] for r in rows if r["label"]==label and r["program"]==program and r["kind"]=="compile") for stage in STAGES}
            print("R45_STAGES,"+label+","+program+","+",".join(f"{k}={v:.0f}" for k,v in stages.items()))
    print(f"R45_COUNTS,rows={len(rows)},cases={len(NAMES)},runs={a.runs},warmup={a.warmup}")
    return 0

if __name__=="__main__":
    sys.exit(main())
