#!/usr/bin/env python3
"""R59 native A/B: exact stdout, instruction counts, actual best-three timing."""
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import os
import re
import statistics
import subprocess
import time

ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/"r59_before"
NEW=ROOT/"r48_after"
FIXTURES={
 "tests/r59_check/self_assign_cases.sm":"9\n17\n33\n44\n",
 "tests/r59_check/stack_self_10m.sm":"123\n",
 "tests/r59_check/global_self_10m.sm":"213\n",
 "tests/r57_check/arithmetic_10m.sm":"99999990000000\n",
 "tests/r57_check/control_10m.sm":"49999995000000\n",
 "tests/r58_check/foldable_10m.sm":"640000000\n",
}
TIMED=("tests/r59_check/stack_self_10m.sm",
       "tests/r59_check/global_self_10m.sm",
       "tests/r57_check/arithmetic_10m.sm",
       "tests/r57_check/control_10m.sm")
def run(argv,timeout=100):
    return subprocess.run([str(v) for v in argv],cwd=ROOT,capture_output=True,
                          text=True,timeout=timeout)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def count_instructions(p):
    # NASM's real x86-64 decoder counts decoded instruction boundaries,
    # never raw opcode bytes; embedded-data caveat applies tak both images.
    data=p.read_bytes()
    assert data[:4]==b"\x7fELF"
    entry=int.from_bytes(data[24:32],"little")
    phoff=int.from_bytes(data[32:40],"little")
    n=int.from_bytes(data[56:58],"little")
    phentsz=int.from_bytes(data[54:56],"little")
    offs=None
    for i in range(n):
        off=phoff+i*phentsz
        p_type=int.from_bytes(data[off:off+4],"little")
        p_flags=int.from_bytes(data[off+4:off+8],"little")
        po=int.from_bytes(data[off+8:off+16],"little")
        va=int.from_bytes(data[off+16:off+24],"little")
        fs=int.from_bytes(data[off+32:off+40],"little")
        if p_type==1 and (p_flags&1) and va<=entry<va+fs:
            offs=po+entry-va
            break
    assert offs is not None,(p,entry)
    cp=run(("ndisasm","-b64","-e",str(offs),p))
    assert cp.returncode==0,(cp.stdout[:100],cp.stderr)
    instructions=[s for s in cp.stdout.splitlines()
                  if re.match(r"^\s*[0-9A-Fa-f]+\s+[0-9A-Fa-f]+\s",s)]
    assert instructions
    return len(instructions),cp.stdout
def main():
    try:
        cpu=min(os.sched_getaffinity(0))
        os.sched_setaffinity(0,{cpu})
        print("R59_CPU_AFFINITY",cpu,flush=True)
    except (OSError,AttributeError):print("R59_CPU_AFFINITY unavailable",flush=True)
    assert OLD.exists() and NEW.exists()
    with TemporaryDirectory(prefix="r59-native-") as d:
        programs={}
        for source,expected in FIXTURES.items():
            results={}
            for label,compiler in (("old",OLD),("new",NEW)):
                binary=Path(d)/(Path(source).stem+"-"+label)
                cp=run([compiler,ROOT/source,binary])
                assert cp.returncode==0 and binary.is_file(),(source,label,cp.stdout,cp.stderr)
                result=run([binary])
                assert result.returncode==0 and result.stdout==expected,(source,label,repr(result.stdout),repr(expected))
                count,asm=count_instructions(binary)
                results[label]=(binary,count,asm)
                print("R59_NATIVE",source,label,"stdout",repr(result.stdout),
                      "elf_sha256",sha(binary),"file_bytes",binary.stat().st_size,
                      "decoded_instruction_count",count,flush=True)
            programs[source]=results
        for source in ("tests/r59_check/stack_self_10m.sm",
                       "tests/r59_check/global_self_10m.sm",
                       "tests/r59_check/self_assign_cases.sm"):
            old=programs[source]["old"]
            new=programs[source]["new"]
            assert new[1]<old[1],(source,old[1],new[1])
            assert new[0].stat().st_size<old[0].stat().st_size
            print("R59_INSTRUCTION_DELTA",source,"old",old[1],"new",new[1],
                  "removed",old[1]-new[1],flush=True)
        for source in ("tests/r57_check/arithmetic_10m.sm",
                       "tests/r57_check/control_10m.sm",
                       "tests/r58_check/foldable_10m.sm"):
            old=programs[source]["old"][0]
            new=programs[source]["new"][0]
            assert old.read_bytes()==new.read_bytes(),source
            print("R59_UNCHANGED_BASELINE",source,sha(new),flush=True)
        for source in TIMED:
            expected=FIXTURES[source]
            samples={"old":[],"new":[]}
            for warm in range(2):
                for label in ("old","new"):
                    p=run([programs[source][label][0]])
                    assert p.stdout==expected and p.returncode==0
            for i in range(3):
                for label in (("old","new") if i%2==0 else ("new","old")):
                    start=time.perf_counter_ns()
                    p=run([programs[source][label][0]])
                    ns=time.perf_counter_ns()-start
                    assert p.stdout==expected and p.returncode==0
                    samples[label].append(ns/1e6)
            ob=min(samples["old"])
            nb=min(samples["new"])
            om=statistics.median(samples["old"])
            nm=statistics.median(samples["new"])
            print("R59_TIMING",source,"old_best3_ms=%.6f"%ob,
                  "new_best3_ms=%.6f"%nb,"best_ratio=%.3fx"%(ob/nb),
                  "old_median_ms=%.6f"%om,"new_median_ms=%.6f"%nm,
                  "median_ratio=%.3fx"%(om/nm),
                  "old_samples_ms",samples["old"],
                  "new_samples_ms",samples["new"],flush=True)
    print("R59_NATIVE_ACCEPTED",len(FIXTURES),
          "stdout_pairs instruction_count_reductions=3",flush=True)
if __name__=="__main__":main()
