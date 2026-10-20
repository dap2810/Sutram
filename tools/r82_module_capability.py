#!/usr/bin/env python3
"""Inspect Sutram's actual NASM source for the minimum independent object mode.

This is a *static* capability check; it does not pretend to have compiled or
linked two .sm modules. Run on a source-locked checkout and then execute the
real native probe from Round 76 to decide capability independently.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re


def inspect(text:str)->dict:
    lines=text.splitlines()
    anchors={name:[i+1 for i,l in enumerate(lines) if re.match(r'^\s*'+re.escape(name)+r':\s*$',l)]
             for name in ['write_elf','want_pe','write_pe']}
    if any(len(v)!=1 for v in anchors.values()):
        return {'status':'STATIC_INCONCLUSIVE','reason':'expected writer labels not unique','anchors':anchors}
    pos=anchors['write_elf'][0]
    end=anchors['want_pe'][0]
    if end<=pos:return {'status':'STATIC_INCONCLUSIVE','reason':'unexpected layout','anchors':anchors}
    writer='\n'.join(lines[pos:end-1])
    # Intentionally use the machine's raw e_type=2 assignment, not a stale
    # comment, as source evidence that this writer emits ET_EXEC (not ET_REL).
    active=[(i+pos,line.strip()) for i,line in enumerate(writer.splitlines())
            if re.match(r'^\s*mov word\s+\[rsp\+16\],\s*2\s*(?:;.*)?$',line)]
    elf_output_re=re.compile(r'^\s*call write_elf\s*(?:;.*)?$',re.MULTILINE)
    pass_count=len(elf_output_re.findall(text))
    evidence={'anchors':anchors,'elf_e_type_2_assignments':active,
              'call_write_elf_count':pass_count,
              'source_lines':len(lines)}
    if len(active)==1 and pass_count==1:
        return {'status':'STATIC_ET_EXEC_ONLY_OBSERVED',**evidence,
                'native_compile_link_test':'NOT_RUN',
                'interpretation':'Current visible main output dispatch emits full executable type 2; '
                                 'no independent .sm relocatable-object mode demonstrated'}
    return {'status':'STATIC_INCONCLUSIVE',**evidence,
            'reason':'writer or dispatch changed; inspect manually'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--report',type=Path)
    a=p.parse_args();result=inspect((a.repo/'src/sutram_compiler.asm').read_text(encoding='utf-8'))
    out=json.dumps(result,indent=2)+'\n';print(out,end='')
    if a.report:
        with a.report.open('x') as f:f.write(out)
    return 0 if result['status']=='STATIC_ET_EXEC_ONLY_OBSERVED' else 2
if __name__=='__main__':raise SystemExit(main())
