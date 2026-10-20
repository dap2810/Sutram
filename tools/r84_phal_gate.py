#!/usr/bin/env python3
"""Experimental fail-closed checker for a SMALL subset of existing phal calls.

This is NOT compiler enforcement or a verified general control-flow analyzer.
It demonstrates a potential pre-compilation obligation rule for linear,
standalone phal_janchit_* calls and immediate failure-exit checks.
Unrecognized protected call shapes are rejected, not silently accepted.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

IDENT = r'[A-Za-z_][A-Za-z_0-9]*'
PRODUCER = re.compile(r'^phal_janchit_\w+\s*\(\s*('+IDENT+r')\s*,.*\)\s*;?$')
GUARD = re.compile(r'^yadi\s*\(\s*phal_asti_siddhi\s*\(\s*('+IDENT+r')\s*\)\s*==\s*0\s*\)\s*\{\s*$')
EXIT = re.compile(r'^(?:prati\s+[^{}]+|sthagita\s*\([^{}]*\)\s*;?)$')
MESSAGE = re.compile(r'^(?:likha|phal_dosh)\s*\([^{}]*\)\s*;?$')


def mask_comments_strings(source: str) -> str:
    """Preserve newlines, strip #,//,/*...*/ and strings; fail closed on unterminated syntax."""
    out=[]; i=0; state='code'
    while i<len(source):
        c=source[i]; two=source[i:i+2]
        if state=='code':
            if two=='/*':state='block';out.extend('  ');i+=2;continue
            if two=='//':state='line';out.extend('  ');i+=2;continue
            if c=='#':state='line';out.append(' ');i+=1;continue
            if c=='"':state='string';out.append(' ');i+=1;continue
            out.append(c);i+=1
        elif state=='line':
            if c=='\n':state='code';out.append('\n')
            else:out.append(' ')
            i+=1
        elif state=='block':
            if two=='*/':state='code';out.extend('  ');i+=2
            else:out.append('\n' if c=='\n' else ' ');i+=1
        else:
            if c=='\\' and i+1<len(source):out.extend('  ');i+=2
            elif c=='"':state='code';out.append(' ');i+=1
            else:out.append('\n' if c=='\n' else ' ');i+=1
    if state in ('block','string'):
        raise ValueError('unterminated block comment or string')
    return ''.join(out)


def check(source: str) -> list[dict[str,object]]:
    try: stripped=mask_comments_strings(source)
    except ValueError as e:return [{'line':1,'code':'UNSUPPORTED_SYNTAX','message':str(e)}]
    lines=[(i+1,line.strip()) for i,line in enumerate(stripped.splitlines()) if line.strip()]
    findings=[]; p=0
    while p<len(lines):
        line_no,body=lines[p]
        if 'phal_janchit_' not in body:
            p+=1;continue
        m=PRODUCER.fullmatch(body)
        if m is None:
            findings.append({'line':line_no,'code':'UNSUPPORTED_PRODUCER','message':'checked call must be a standalone statement'})
            p+=1;continue
        name=m.group(1)
        if p+1>=len(lines):
            findings.append({'line':line_no,'code':'E_PHAL_UNHANDLED','message':'no check after '+name})
            p+=1;continue
        guard_no,guard_body=lines[p+1];g=GUARD.fullmatch(guard_body)
        if g is None or g.group(1)!=name:
            findings.append({'line':line_no,'code':'E_PHAL_UNHANDLED','message':name+' requires immediate failure guard'})
            p+=1;continue
        # Accepted guard is a flat failure-only block ending with unconditional exit.
        # Nested braces, alternate branch, or unknown statements fail closed.
        q=p+2;guard_stmts=[]
        while q<len(lines) and lines[q][1]!='}':
            guard_stmts.append(lines[q][1]);q+=1
        if (q==len(lines) or not guard_stmts or not EXIT.fullmatch(guard_stmts[-1])
                or any(not MESSAGE.fullmatch(s) for s in guard_stmts[:-1])
                or (q+1<len(lines) and re.match(r'^anya\b',lines[q+1][1]))):
            findings.append({'line':guard_no,'code':'E_PHAL_UNHANDLED','message':'guard must end in unconditional return/halt without alternate branch'})
            p+=1;continue
        p=q+1
    return findings


def main() -> int:
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('source',type=Path)
    a.add_argument('--json',action='store_true')
    args=a.parse_args()
    try: data=args.source.read_text(encoding='utf-8')
    except (OSError,UnicodeError) as e:
        print('BLOCKED: '+str(e),file=sys.stderr);return 2
    errors=check(data)
    result={'source':str(args.source),'status':'REJECTED' if errors else 'ACCEPTED_SUBSET_ONLY',
            'issues':errors,'compiler_test':'NOT_RUN','compiler_enforced':False}
    if args.json:print(json.dumps(result,indent=2))
    else:
        for e in errors:print(f"{args.source}:{e['line']} {e['code']}: {e['message']}")
        if not errors:print('ACCEPTED_SUBSET_ONLY (experimental precheck, NOT compiler acceptance)')
    return 1 if errors else 0

if __name__=='__main__':raise SystemExit(main())
