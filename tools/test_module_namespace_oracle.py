#!/usr/bin/env python3
"""Independent namespace-expansion *test oracle*, not the Sutram compiler path.
It exercises parser/linker compatibility of the *intended transformed syntax* with
an existing verified native compiler; it does NOT execute the new NASM preprocessor.
"""
from pathlib import Path
import re, subprocess, tempfile, sys
ROOT=Path(__file__).resolve().parents[1]
DEF=re.compile(r'^\s*(?:prakriya|प्रक्रिया)\s+([^\W\d]\w*)\s*\(',re.MULTILINE)
IMPORT=re.compile(r'^\s*ayojan\s+(\w+)(?:@(\w+))?\s*$',re.MULTILINE)
def rewrite_module(text,alias):
    defined=set(DEF.findall(text))
    out=[];i=0;quoted=False;comment=False;escape=False
    while i<len(text):
        c=text[i]
        if comment:
            out.append(c);comment=c!='\n';i+=1;continue
        if quoted:
            out.append(c)
            if escape:escape=False
            elif c=='\\':escape=True
            elif c=='"':quoted=False
            i+=1;continue
        if c=='#' or text[i:i+2]=='//':
            comment=True;out.append(c);i+=1;continue
        if c=='"':quoted=True;out.append(c);i+=1;continue
        if c=='_' or c.isalpha():
            j=i+1
            while j<len(text) and (text[j]=='_' or text[j].isalnum()):j+=1
            token=text[i:j]
            k=j
            while k<len(text) and text[k] in ' \t\r\n':k+=1
            out.append(f'{alias}__{token}' if token in defined and k<len(text) and text[k]=='(' else token)
            i=j;continue
        out.append(c);i+=1
    return ''.join(out)
def expand(text):
    def resolve(m):
        mod,alias=m.group(1),m.group(2)
        source=(ROOT/'examples'/'lib'/f'{mod}.smlib').read_text()
        return rewrite_module(source,alias) if alias else source
    return IMPORT.sub(resolve,text)
def main():
    compiler=ROOT/'sutram_compiler'
    total=0
    for source in sorted(p for p in (ROOT/'examples').glob('1[45][0-9]_namespaced*.sm') if 149 <= int(p.name[:3]) <= 153):
        with tempfile.TemporaryDirectory() as td:
            f=Path(td)/source.name; exe=Path(td)/'result.bin'
            f.write_text(expand(source.read_text()))
            p=subprocess.run([str(compiler),str(f),str(exe)],capture_output=True,text=True)
            if p.returncode:
                print('FAIL',source.name,'compile',p.stdout,p.stderr);return 1
            p=subprocess.run([str(exe)],capture_output=True,text=True,timeout=10)
            expected=(ROOT/'tests'/'expect'/(source.stem+'.out')).read_text()
            if p.returncode or p.stdout!=expected:
                print('FAIL',source.name,'output',repr(p.stdout),'expected',repr(expected));return 1
            print('PASS ORACLE',source.name,repr(p.stdout))
            total+=1
    print(f'ORACLE {total}/{total} passed (NOT a NASM rebuild)')
    return 0
if __name__=='__main__':sys.exit(main())
