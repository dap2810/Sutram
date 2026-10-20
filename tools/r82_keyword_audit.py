#!/usr/bin/env python3
"""Read-only tracked-source vocabulary candidate inventory for Sutram.

A clean scan is not proof of semantic correctness. No files are rewritten. Report
both coverage and candidate positions, including explicit excluded directories.
"""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
import re
import subprocess

OLD = {
    'sort': 'shreni', 'list': 'suchi', 'map': 'nighantu', 'set': 'sangrah',
    'array': 'mala', 'string': 'varna', 'file': 'patra', 'hash': 'gudh',
    'result': 'phal', 'fmt': 'roop', 'pankti': 'mala',
    'punaravartana': 'chakra', 'pratiyati': 'prati', 'ayojan': 'yoj',
    'nishkriya': 'yantra', 'nishedha': 'abhava', 'srijana': 'ganana',
    'char_at': 'akshar', 'char_code': 'aksharank', 'set_char': 'akshar_rakh'
}
TOKEN = re.compile(r'(?<!\w)(' + '|'.join(map(re.escape, OLD)) + r')(?!\w)')
RANGE = re.compile(r'\bchakra\b[^\n]*\bto\b')
QUOTED = re.compile(r'''(['"])(%s)\1''' % '|'.join(map(re.escape, OLD)))
PLACEHOLDER = re.compile(r'\{kw:([^}\s]+)\}')
SUFFIXES = {'.sm','.smlib','.asm','.inc','.py','.c','.h','.js','.ps1',
            '.sh','.html','.md','.lang','.sandesh','.txt'}
HISTORY = ('ChatGPT-to-Sarvam/','Sarvam-to-ChatGPT/','Claude-to-Sarvam/',
           'Muse-to-Sarvam/','Sarvam-to-Muse/','Sarvam-to-Claude/',
           'ChatGPT-to-Sarvam-Clean/','Sarvam-to-ChatGPT-Clean-Project/')


def mask_sutram(text: str) -> list[str]:
    """Preserve exact line offsets across quoted strings and multiline comments."""
    lines, block, quote, escaped = [], False, None, False
    for source in text.splitlines():
        chars=list(source)
        i=0
        while i<len(chars):
            c=source[i]
            pair=source[i:i+2]
            if block:
                chars[i]=' '
                if pair=='*/':
                    chars[i+1]=' '
                    block=False
                    i+=2
                    continue
            elif quote is not None:
                chars[i]=' '
                if escaped: escaped=False
                elif c=='\\': escaped=True
                elif c==quote: quote=None
            elif pair=='/*':
                chars[i]=chars[i+1]=' '
                block=True
                i+=2
                continue
            elif pair=='//' or c=='#':
                chars[i:]=[' ']*(len(chars)-i)
                break
            elif c in ('"', "'"):
                quote=c
                chars[i]=' '
            i+=1
        lines.append(''.join(chars))
    return lines


def emit(path: str, num: int, old: str, kind: str, source: str, column: int = 0) -> dict:
    return {'path':path, 'line':num, 'column':column,
            'old':old, 'proposed':OLD.get(old,'tak'),
            'kind':kind, 'context':source.strip()[:160]}


def scan(path: str, content: str) -> list[dict]:
    ext=Path(path).suffix.lower()
    result=[]
    if ext in ('.sm','.smlib'):
        lines=content.splitlines()
        for line, (src, mask) in enumerate(zip(lines,mask_sutram(content)),1):
            for m in TOKEN.finditer(mask):
                result.append(emit(path,line,m.group(1),'active_sutram_token',src,m.start()+1))
            for m in RANGE.finditer(mask):
                result.append(emit(path,line,'to','suspect_range_to',src,m.end()-1))
    elif ext=='.lang':
        # The second column is the canonical Sutram token, the first is native spelling.
        for line,src in enumerate(content.splitlines(),1):
            stripped=src.strip()
            if not stripped or stripped.startswith('#'):continue
            fields=stripped.split()
            if len(fields)>=2 and fields[1] in OLD:
                result.append(emit(path,line,fields[1],'language_pack_canonical',src))
    elif ext=='.sandesh':
        for line,src in enumerate(content.splitlines(),1):
            stripped=src.strip()
            if not stripped or stripped.startswith('#'):continue
            # Only placeholder references to canonical keywords; prose and quoted
            # translated explanations aren't compiler grammar.
            for m in PLACEHOLDER.finditer(src):
                if m.group(1) in OLD:
                    result.append(emit(path,line,m.group(1),'old_keyword_placeholder',src,m.start()+1))
    elif ext in ('.md','.html'):
        pattern=(r'```(?:sutram|sm)\s*\n[\s\S]*?```' if ext=='.md'
                 else r'<(?:pre|code)\b[^>]*>[\s\S]*?</(?:pre|code)>')
        for b in re.finditer(pattern,content,flags=re.IGNORECASE):
            block=html.unescape(b.group(0))
            # Treat literal backslash+n/r inside code blocks as a boundary.
            candidate=re.sub(r'\\[nr]','  ',block)
            for m in TOKEN.finditer(candidate):
                position=b.start()+m.start()
                result.append(emit(path,content.count('\n',0,position)+1,
                                   m.group(1),'documentation_code_review',
                                   block[max(0,m.start()-25):m.end()+80].replace('\n',' ')))
            for m in RANGE.finditer(candidate):
                position=b.start()+m.start()
                result.append(emit(path,content.count('\n',0,position)+1,'to',
                                   'documentation_range_review',block[max(0,m.start()-25):m.end()+80]))
    else:
        for line,src in enumerate(content.splitlines(),1):
            for m in QUOTED.finditer(src):
                result.append(emit(path,line,m.group(2),'quoted_dispatch_review',src,m.start()+1))
    return result


def tracked_paths(root:Path)->list[str]:
    p=subprocess.run(['git','-C',str(root),'ls-files','-z'],capture_output=True,check=True,timeout=30)
    return [b.decode('utf-8') for b in p.stdout.split(b'\0') if b]


def audit(root:Path)->dict:
    root=root.resolve()
    files=tracked_paths(root)
    candidates=[];errors=[]
    counts={'tracked':len(files),'history_excluded':0,'extension_excluded':0,
            'scanned':0,'smlib_sm_scanned':0,'pack_scanned':0,'message_pack_scanned':0}
    for path in files:
        if path.startswith(HISTORY):counts['history_excluded']+=1;continue
        ext=Path(path).suffix.lower()
        if ext not in SUFFIXES:counts['extension_excluded']+=1;continue
        target=root/path
        if target.is_symlink() or not target.is_file():
            errors.append({'path':path,'error':'missing or symlink'});continue
        try:src=target.read_text(encoding='utf-8')
        except (OSError,UnicodeError) as exc:
            errors.append({'path':path,'error':type(exc).__name__});continue
        counts['scanned']+=1
        if ext in ('.sm','.smlib'):counts['smlib_sm_scanned']+=1
        if ext=='.lang':counts['pack_scanned']+=1
        if ext=='.sandesh':counts['message_pack_scanned']+=1
        candidates.extend(scan(path,src))
    candidates.sort(key=lambda r:(r['path'],r['line'],r['column']))
    return {'status':'INVENTORY_PASS' if not errors else 'INVENTORY_FAIL',
            'coverage':counts,'candidate_count':len(candidates),
            'candidates':candidates,'errors':errors,
            'notice':'Candidates require human/manual semantic review; exclusions are explicit. '
                     'A zero candidate count does not certify compiler behavior.'}


def main()->int:
    arg=argparse.ArgumentParser(description=__doc__)
    arg.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[1])
    arg.add_argument('--output',type=Path)
    args=arg.parse_args()
    report=audit(args.repo)
    content=json.dumps(report,indent=2,ensure_ascii=False)+'\n'
    print(content,end='')
    if args.output:
        with args.output.open('x',encoding='utf-8') as f:f.write(content)
    return 0 if report['status']=='INVENTORY_PASS' else 2


if __name__=='__main__':raise SystemExit(main())
