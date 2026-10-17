#!/usr/bin/env python3
"""Produce/check a pinned, local-only build-command migration; never edits files.

Historical round reports and CHANGELOG preserve their snapshot commands. All
other tracked md/html/txt documents are scanned at the pinned baseline. Current
working-tree bytes must equal either that baseline or its exact migration.
"""
from __future__ import annotations
import argparse, difflib, os, re, subprocess
from pathlib import Path

BASE = '11f41d3fcc8377dbcc1453f36a47a6122e3b1954'
ROOT = Path(__file__).resolve().parents[1]
OLD = 'src/sutram_compiler.asm'
NEW = 'src/r68_compiler_entry.asm'

def migrate(data: bytes) -> bytes:
    text = data.decode('utf-8')
    # Only command lines; the implementation source is still named normally
    # in descriptions, hashes and include directives.
    result=[]
    for line in text.splitlines(keepends=True):
        if re.search(r'(?i)\bnasm(?:\.exe)?\b', line):
            line=line.replace(OLD,NEW).replace(OLD.replace('/','\\'),NEW.replace('/','\\'))
        result.append(line)
    return ''.join(result).encode('utf-8')

def current_document(name: str) -> bool:
    p=Path(name)
    if p.suffix.lower() not in ('.md','.html','.txt'):return False
    if any(x.startswith(('Sarvam-to-','ChatGPT-to-','Muse-to-')) for x in p.parts):return False
    if p.name=='CHANGELOG.md' or re.match(r'ROUND-\d+',p.name):return False
    if re.match(r'R\d+[-_]',p.name):return False  # immutable per-round design reports
    return True

def git(*args: str, root: Path=ROOT) -> bytes:
    proc=subprocess.run(['git','-C',str(root),*args],stdin=subprocess.DEVNULL,
                        capture_output=True,timeout=30,check=False)
    if proc.returncode:raise ValueError(proc.stderr.decode('utf-8','replace'))
    return proc.stdout

def make_patch(root: Path=ROOT) -> tuple[str,list[str]]:
    names=git('ls-tree','-r','--name-only',BASE,root=root).decode('utf-8').splitlines()
    pending=[];pieces=[]
    for name in names:
        if not current_document(name):continue
        before=git('show',BASE+':'+name,root=root)
        try:after=migrate(before)
        except UnicodeDecodeError:continue
        if after==before:continue
        path=root/name
        if path.is_symlink() or not path.is_file():raise ValueError('missing/reparse document: '+name)
        actual=path.read_bytes()
        if actual==after or migrate(actual)==actual:continue
        if actual!=before:raise ValueError('document drift; reconcile explicitly: '+name)
        pending.append(name)
        pieces.extend(difflib.unified_diff(before.decode().splitlines(True),after.decode().splitlines(True),
                     fromfile='a/'+name,tofile='b/'+name))
    return ''.join(pieces),pending

def main()->int:
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true')
    p.add_argument('--patch',type=Path);a=p.parse_args()
    try:
        patch,names=make_patch()
        if a.patch:
            with a.patch.open('x',encoding='utf-8',newline='\n') as f:f.write(patch)
        print('Remaining build-command documents:',len(names))
        for n in names:print(n)
        if not a.patch and not a.check:print(patch,end='')
        return 1 if a.check and names else 0
    except (OSError,ValueError,subprocess.TimeoutExpired) as e:p.exit(2,str(e)+'\n')
if __name__=='__main__':raise SystemExit(main())
