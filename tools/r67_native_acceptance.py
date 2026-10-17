#!/usr/bin/env python3
"""Real compiler acceptance: exact unchanged Gujarati golden, two scripts,
optional pure-stack-pair codegen A/B, and full-suite report. No golden writes.
Run --compiler <R67 staged default> --pair-compiler <explicit pure-pair mode>.
--reference <accepted default> and --suite add identity/regression checks.
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def run(argv,env=None,timeout=20):
    return subprocess.run([str(x) for x in argv],cwd=ROOT,capture_output=True,timeout=timeout,env=env,check=False)

def compile_run(compiler,src,out,lang=None):
    cmd=[compiler]+(['--lang',lang] if lang else [])+[src,out]
    c=run(cmd)
    if c.returncode or not out.exists(): raise AssertionError(f'compile {src}: {c.returncode} {c.stdout!r} {c.stderr!r}')
    r=run([out]);return r,out.read_bytes()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--compiler',type=Path,required=True)
    p.add_argument('--pair-compiler',type=Path)
    p.add_argument('--reference',type=Path)
    p.add_argument('--suite',action='store_true')
    a=p.parse_args(); comp=a.compiler.resolve();rows=[]
    for path in (comp,a.pair_compiler,a.reference):
        if path and not path.resolve().is_file(): p.error(f'missing compiler {path}')
    example=ROOT/'examples/37_native_gujarati.sm';gold=ROOT/'tests/expect/37_native_gujarati.out'
    # Pin both untouched accepted artifacts, including the golden's missing final newline.
    for file,want in [(example,'aedd12d69b77f3e66610278bf24a5709f1b75a18'),(gold,'9599e58025ba07520b8d1a7ad4b21b2b3b9a102a')]:
        data=file.read_bytes();blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        if blob!=want: raise AssertionError(f'accepted Gujarati artifact changed: {file}')
    with tempfile.TemporaryDirectory(prefix='sutram-r67-') as d:
        work=Path(d)
        cases=[(example,'gujarati',gold.read_bytes())]
        for lang in ('bengali','punjabi'):
            stem=ROOT/f'examples/r67/{lang}_native'
            cases.append((stem.with_suffix('.sm'),lang,stem.with_suffix('.out').read_bytes()))
        for i,(src,lang,want) in enumerate(cases):
            r,b=compile_run(comp,src,work/f'case{i}',lang)
            if r.returncode!=0 or r.stdout!=want: raise AssertionError(f'{src.name}: exit={r.returncode} expected={want!r} actual={r.stdout!r}')
            rows.append({'case':src.name,'status':'PASS','stdout_hex':r.stdout.hex()})
        # All scripts use identical digit values, including fractions; compare native outputs.
        src=work/'mixed.sm';src.write_text('mukhya() { likha(১২ + ੩) likha(১૨.੫) }\n',encoding='utf-8')
        r,b=compile_run(comp,src,work/'mixed')
        if r.returncode!=0 or r.stdout!=b'15\n12.500000\n': raise AssertionError('mixed decimal digits failed')
        rows.append({'case':'mixed digits','status':'PASS'})
        # Whole-block pure-ASM contract; no arbitrary byte deletion permitted.
        if a.pair_compiler:
            for reg in range(16):
                if reg==4: continue
                raw=bytes((0x50+reg,0x58+reg)) if reg<8 else bytes((0x41,0x50+reg-8,0x41,0x58+reg-8))
                src=work/f'pair{reg}.sm'
                src.write_text('mukhya() { yantra("'+raw.hex(' ')+'") likha(42) }\n')
                rb,before=compile_run(comp,src,work/f'b{reg}')
                ra,after=compile_run(a.pair_compiler.resolve(),src,work/f'a{reg}')
                if rb.returncode!=0 or ra.returncode!=0 or rb.stdout!=b'42\n' or ra.stdout!=rb.stdout: raise AssertionError(f'pair semantics failed reg={reg}')
                if len(before)-len(after)!=len(raw): raise AssertionError(f'pair not removed before emission reg={reg}')
                rows.append({'case':f'same register {reg}','status':'PASS','bytes_removed':len(raw)})
            for hexdata in ('50 90 58','54 5c','50 59'):
                # Negative cases execute only when balanced and valid; compare bytes otherwise.
                src=work/'nonmatch.sm';src.write_text('mukhya() { yantra("'+hexdata+'") likha(42) }\n')
                # Different-register pair may clobber RCX but remains stack balanced.
                rb,before=compile_run(comp,src,work/'nonmatch_before')
                ra,after=compile_run(a.pair_compiler.resolve(),src,work/'nonmatch_after')
                if before!=after: raise AssertionError('nonmatching raw block changed')
            rows.append({'case':'nonmatches byte-identical','status':'PASS'})
        else: rows.append({'case':'same-register native A/B','status':'NOT RUN'})
        if a.reference:
            src=work/'ascii.sm';src.write_text('mukhya() { vitti x=7 likha(x*3+1) }\n')
            oldr,old=compile_run(a.reference.resolve(),src,work/'old')
            newr,new=compile_run(comp,src,work/'new')
            if old!=new: raise AssertionError('default ASCII image changed; do not rewrite goldens')
            rows.append({'case':'default ASCII image identity','status':'PASS'})
        else: rows.append({'case':'default ASCII image identity','status':'NOT RUN'})
    if a.suite:
        env=os.environ.copy();env['SUTRAM_COMPILER']=str(comp)
        r=run([os.sys.executable,ROOT/'tests/run_tests.py'],env=env,timeout=900)
        print(r.stdout.decode(errors='replace'));print(r.stderr.decode(errors='replace'))
        rows.append({'case':'full accepted suite','exit':r.returncode,'status':'PASS' if r.returncode==0 else 'NOT FULLY GREEN'})
        print(json.dumps(rows,ensure_ascii=False,indent=2))
        # Existing NO-EXPECTATION cases are not silently treated as success.
        return 0 if r.returncode==0 else 1
    print(json.dumps(rows,ensure_ascii=False,indent=2));return 0
if __name__=='__main__': raise SystemExit(main())
