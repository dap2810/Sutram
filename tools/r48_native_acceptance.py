#!/usr/bin/env python3
"""Native R48 check-mode acceptance. Never substitutes another parser.

Compile both NASM compiler versions first. Confirm multi-error native output,
absence of binaries on success or failure, and byte-identical ordinary
generated binaries across original R46 and new R48 source.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
NEW=ROOT/"r48_after"
OLD=ROOT/"r48_before"
FIXTURES=ROOT/"tests"/"r48_check"
EXAMPLES=[
    ROOT/"examples"/"41_recursion.sm",
    ROOT/"examples"/"126_numeric_pipeline.sm",
    ROOT/"examples"/"163_r40_transitive_diamond.sm",
    ROOT/"examples"/"111_t18_kosh_dasham_function_return.sm",
]
def run(args):
    return subprocess.run([str(x) for x in args],cwd=ROOT,capture_output=True,text=True,timeout=30)

def main():
    assert NEW.is_file() and OLD.is_file(), "build both native compilers first"
    with TemporaryDirectory(prefix="sutram-r48-") as d:
        tmp=Path(d)
        failed=FIXTURES/"three_parse_errors.sm"
        p=run((NEW,"--check",failed))
        print("R48_MULTI_BEGIN")
        print(p.stdout,end="")
        print(p.stderr,end="")
        print("R48_MULTI_END")
        diags=re.findall(r"three_parse_errors\.sm:(\d+):(\d+): Sutram Error \[E_PARSE\]: near '([^']+)'",p.stdout)
        assert p.returncode!=0 and len(diags)>=3, f"must report 3 real parse diagnostics: {p.returncode} {diags}"
        assert {int(x[0]) for x in diags} >= {2,3,4}, f"wrong locations: {diags}"
        assert all(int(line)>0 and int(col)>0 and tok for line,col,tok in diags)
        assert not any(tmp.iterdir()), "check failure created an output"
        valid=FIXTURES/"valid.sm"
        ok=run((NEW,"--check",valid))
        assert ok.returncode==0 and "Sutram check: OK" in ok.stdout, f"valid source failed {ok}"
        invalid=run((NEW,"--check",failed))
        assert invalid.returncode!=0
        # Semantic validation uses the real backpatch resolver without output.
        unknown=FIXTURES/"semantic_unknown.sm"
        semantic=run((NEW,"--check",unknown))
        print("R48_SEMANTIC_BEGIN")
        print(semantic.stdout,end="")
        print(semantic.stderr,end="")
        print("R48_SEMANTIC_END")
        assert semantic.returncode!=0, "unresolved call should fail --check"
        assert "semantic_unknown.sm:2:11: Sutram Error [E_UNDEFINED_FUNCTION]" in semantic.stdout, repr(semantic.stdout)
        assert "missing_fun" in semantic.stdout and "^" in semantic.stdout
        # A user-provided potential output file must not be created.
        assert not (ROOT/"out.bin").exists(), "unexpected workspace output out.bin"
        data=[]
        for i,source in enumerate(EXAMPLES):
            if not source.is_file():
                print(f"R48_SKIP_MISSING_SAMPLE: {source}")
                continue
            first=tmp/f"before{i}.bin"
            second=tmp/f"after{i}.bin"
            before=run((OLD,source,first))
            after=run((NEW,source,second))
            assert before.returncode==0 and after.returncode==0,(source,before,after)
            a,b=first.read_bytes(),second.read_bytes()
            assert a==b,f"R46/R48 native binary mismatch for {source} ({len(a)} vs {len(b)})"
            print(f"R48_BINARY_EQUAL,{source.name},{len(a)},{hashlib.sha256(a).hexdigest()}")
            data.append(source)
        assert len(data)>=3
    print(f"R48_ACCEPTED_CHECK_TESTS,parse_diags={len(diags)},native_byte_equal={len(data)},check_valid=1,no_output=1")
    return 0
if __name__=="__main__":sys.exit(main())
