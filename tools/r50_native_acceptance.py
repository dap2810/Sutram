#!/usr/bin/env python3
"""R50 actual compiler validation. No second parser. Requires r48_after ELF."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
COMPILER=ROOT/"r48_after"
SAMPLES={
 "runtime_hi.sm":"104\n105\n104\n105\n2\n0\n",
 "byte_truncation.sm":"44\n44\n255\n255\n2\n"
}
def run(*args, cwd=ROOT):
    return subprocess.run([str(x) for x in args],cwd=cwd,capture_output=True,text=True,timeout=30)
def main():
    if not COMPILER.exists(): raise AssertionError("build r48_after first")
    with TemporaryDirectory(prefix="sutram-r50-") as tmp:
        work=Path(tmp)
        for name,expected in SAMPLES.items():
            src=ROOT/"tests"/"r50_check"/name
            out=work/(name+".bin")
            comp=run(COMPILER,src,out)
            assert comp.returncode==0,(name,comp.stdout,comp.stderr)
            assert out.exists(),(name,"binary missing")
            exe=run(out)
            print("R50_RUN",name,"rc",exe.returncode,"stdout",repr(exe.stdout),"stderr",repr(exe.stderr),flush=True)
            assert exe.returncode==0,(name,"native program failed")
            assert exe.stdout==expected,(name,repr(exe.stdout),repr(expected))
            ok=run(COMPILER,"--check",src)
            assert ok.returncode==0 and "Sutram check: OK" in ok.stdout,(name,ok)
            assert not list(work.glob("*.exe")),"check created output"
        print("R50_ACCEPTED: runtime byte writes, byte truncation, char_at, vartani_len and vartani_cmp; 2/2 native executions; 2/2 --check")
    return 0
if __name__=="__main__":sys.exit(main())
