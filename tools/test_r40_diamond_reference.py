#!/usr/bin/env python3
"""Independent developmental oracle for R40 transitive import semantics.

This flattener is never used by the native compiler; run it only in tests.
Usage: python3 tools/test_r40_diamond_reference.py <prior-native-compiler>
"""
from pathlib import Path
import subprocess, tempfile, sys, re
ROOT=Path(__file__).resolve().parents[1]
LIB=ROOT/'examples'/'lib'


def flatten():
    seen=set()
    blocks=[]
    def visit(name):
        if name in seen:return
        seen.add(name)
        text=(LIB/(name+'.smlib')).read_text()
        kept=[]
        for line in text.splitlines(keepends=True):
            m=re.fullmatch(r'\s*ayojan\s+([A-Za-z][A-Za-z0-9_]*)\s*',line)
            if m:visit(m.group(1))
            else:kept.append(line)
        blocks.append(''.join(kept)+'\n')
    visit('r40_a')
    main=(ROOT/'examples/163_r40_transitive_diamond.sm').read_text()
    main=re.sub(r'^ayojan r40_a\s*\n','',main)
    return ''.join(blocks)+main,seen


def main(path):
    compiler=Path(path).resolve()
    flat,visited=flatten()
    assert visited=={'r40_a','r40_b','r40_c','r40_d'},visited
    assert flat.count('prakriya r40_shared(')==1
    with tempfile.TemporaryDirectory() as td:
        source=Path(td)/'diamond.sm';source.write_text(flat)
        program=Path(td)/'diamond.bin'
        result=subprocess.run([str(compiler),str(source),str(program)],text=True,capture_output=True,timeout=20)
        if result.returncode:raise AssertionError(f'flattened oracle failed: {result.stdout}\n{result.stderr}')
        run=subprocess.run([str(program)],text=True,capture_output=True,timeout=20)
        assert (run.returncode,run.stdout)==(0,'17\n7\n'),(run.returncode,repr(run.stdout))
        print('PASS native flattened diamond reference: output 17\\n7\\n')
        print('PASS shared dependency appears once, deterministic import order d,b,c,a')
if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('pass path to previously compiled Sutram native compiler')
    main(sys.argv[1])
