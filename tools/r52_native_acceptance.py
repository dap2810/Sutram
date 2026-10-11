#!/usr/bin/env python3
"""R52 native compiler regressions. Tests real compiled programs and file modes."""
from pathlib import Path
import os, stat, subprocess, tempfile, re, sys
ROOT=Path(__file__).resolve().parents[1]
FIX=ROOT/"tests"/"r52_check"
OLD=ROOT/"r52_before"
NEW=ROOT/"r48_after"
CASES={
 "char_code_index.sm": "90\n65\n90\n105\n105\n",
 "likh_valid.sm": "44\n66\n",
 "dvaram_default.sm": "1\n",
 "dvaram_explicit.sm": "1\n",
}
BAD=["likh_missing_value.sm","likh_no_args.sm","dvaram_bad_arity.sm",
     "char_at_bad_arity.sm","char_code_bad_arity.sm"]
def run(args,cwd,timeout=16):
    try:
        p=subprocess.run([str(x) for x in args],cwd=cwd,capture_output=True,
            text=True,timeout=timeout)
        return p.returncode,p.stdout,p.stderr
    except subprocess.TimeoutExpired:
        return "TIMEOUT","",""
def report(tag,version,name,phase,rc,out,err):
    print("R52_"+tag,version,name,phase,"exit",rc,
          "stdout",repr(out),"stderr",repr(err),flush=True)
def exercise(compiler, version, name):
    with tempfile.TemporaryDirectory(prefix="r52-"+version+"-") as dir:
        wd=Path(dir)
        exe=wd/"result.bin"
        src=FIX/name
        rc,out,err=run([compiler,src,exe],wd)
        report("OBSERVED",version,name,"compile",rc,out,err)
        if rc!=0 or not exe.exists():
            return rc,None,None
        rc,out,err=run([exe],wd)
        report("OBSERVED",version,name,"execute",rc,out,err)
        target={"dvaram_default.sm":"created_default.txt",
                "dvaram_explicit.sm":"created_private.txt"}.get(name)
        mode=stat.S_IMODE((wd/target).stat().st_mode) if target and (wd/target).exists() else None
        if target:
            print("R52_FILE_MODE",version,name,"mode",oct(mode) if mode is not None else "NO_FILE")
        return rc,out,mode
def main():
    assert OLD.is_file() and NEW.is_file(),"both original and modified NASM compilers must be built"
    # One controlled umask gives deterministic expected mode on Linux runners.
    prior=os.umask(0o022)
    try:
        for name in CASES:
            exercise(OLD,"before",name)
        for name,expect in CASES.items():
            rc,stdout,mode=exercise(NEW,"after",name)
            assert rc==0 and stdout==expect,(name,rc,repr(stdout),repr(expect))
            if name=="dvaram_default.sm":
                assert mode==0o644,(name,mode)
            if name=="dvaram_explicit.sm":
                assert mode==0o600,(name,mode)
        for name in BAD:
            with tempfile.TemporaryDirectory(prefix="r52-bad-") as d:
                dest=Path(d)
                rc,out,err=run([NEW,"--check",FIX/name],dest)
                report("INVALID","after",name,"check",rc,out,err)
                assert isinstance(rc,int) and rc!=0,(name,rc)
                assert "Sutram Error" in out+err,(name,out,err)
                assert not list(dest.iterdir()),(name,"--check created output")
        print("R52_ACCEPTED PASS indexed_char_code=1 likh_store=1 "
              "dvaram_default_mode=0644 dvaram_explicit_mode=0600 bad_arity=5")
        return 0
    finally:
        os.umask(prior)
if __name__=="__main__":
    sys.exit(main())
