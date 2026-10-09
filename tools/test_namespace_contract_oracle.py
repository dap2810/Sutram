#!/usr/bin/env python3
"""Independent R33/R34 namespace contract oracle (development-only Python).

Does not execute the modified NASM importer. Compiles manually expanded Sutram
through the previously verified compiler to test intended semantics. Validation
of rejection examples is an independent Python model, NOT compiler verification.
"""
from pathlib import Path
import re, subprocess, tempfile, sys
from test_module_namespace_oracle import ROOT, rewrite_module

E=ROOT/'examples'; X=ROOT/'tests'/'expect'
LINE=re.compile(r'^\s*ayojan\s+(\S+)\s*$',re.ASCII)
IDENT=re.compile(r'[A-Za-z_][A-Za-z_0-9]{0,30}\Z')
MODULE=re.compile(r'[A-Za-z_0-9-]{1,30}\Z')
INVALID='Sutram Error: invalid namespaced ayojan (use module@alias, max 31 alias bytes)\n'
ALIAS_REUSE='Sutram Error: namespaced alias already assigned to another module\n'
MISSING='Sutram Error: namespaced module file not found\n'

def transform(code):
    registry={}; keys=set(); out=[]
    for line in code.splitlines(keepends=True):
        m=LINE.fullmatch(line.rstrip('\n\r'))
        if not m:
            out.append(line); continue
        target=m.group(1)
        if '@' not in target:
            # preserve the original legacy meaning in the independent oracle.
            path=E/'lib'/f'{target}.smlib'
            if not path.is_file():
                path=ROOT/'lib'/f'{target}.smlib'
            if path.is_file() and target not in keys:
                out.append(path.read_text()+'\n');keys.add(target)
            continue
        parts=target.split('@')
        if len(parts)!=2: raise ValueError(INVALID)
        mod,alias=parts
        if not MODULE.fullmatch(mod) or not IDENT.fullmatch(alias):raise ValueError(INVALID)
        key=f'{mod}@{alias}'
        if alias in registry and registry[alias]!=mod:raise ValueError(ALIAS_REUSE)
        registry[alias]=mod
        if key in keys: continue
        if len(keys)>=16:raise ValueError(INVALID)
        keys.add(key)
        path=E/'lib'/f'{mod}.smlib'
        if not path.is_file():path=ROOT/'lib'/f'{mod}.smlib'
        if not path.is_file():raise ValueError(MISSING)
        out.append(rewrite_module(path.read_text(),alias)+'\n')
    return ''.join(out)

def main():
    success=0; rejected=0
    with tempfile.TemporaryDirectory(prefix='sutram-r34-oracle-') as d:
        for n in range(149,163):
            matches=sorted(E.glob(f'{n}_namespaced*.sm'))
            if not matches:raise AssertionError(f'missing fixture {n}')
            src=matches[0]; name=src.stem
            expected=(X/f'{name}.out').read_text()
            compile_fail=(X/f'{name}.compile_fail').exists()
            try: expanded=transform(src.read_text())
            except ValueError as exc:
                if not compile_fail or str(exc)!=expected:
                    raise AssertionError(f'{name}: rejection disagrees: {exc!s} expected {expected!r}')
                rejected+=1;print('PASS CONTRACT REJECT',name);continue
            if compile_fail:raise AssertionError(f'{name}: rejected fixture was accepted by oracle')
            input_path=Path(d)/'test.sm'; output_path=Path(d)/'run.bin'
            input_path.write_text(expanded)
            c=subprocess.run([str(ROOT/'sutram_compiler'),str(input_path),str(output_path)],capture_output=True,text=True,timeout=20)
            if c.returncode:raise AssertionError(f'{name}: old compiler rejects expanded valid source: {c.stdout!r} {c.stderr!r}')
            p=subprocess.run([str(output_path)],capture_output=True,text=True,timeout=20)
            if p.returncode or p.stdout!=expected:raise AssertionError(f'{name}: {p.returncode=} {p.stdout=} != {expected!r}')
            success+=1;print('PASS ORACLE EXEC',name)
    print(f'ORACLE {success} executable cases and {rejected} rejection contracts checked; NEW NASM IMPORTER UNBUILT')
    assert (success,rejected)==(7,7)
if __name__=='__main__':sys.exit(main())
