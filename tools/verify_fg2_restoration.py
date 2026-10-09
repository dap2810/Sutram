#!/usr/bin/env python3
"""Guard the restored, independently verified FG2 release code against silent loss.

This is a SOURCE-LEVEL NEGATIVE GATE, not a substitute for NASM builds. The
experimental XMM Stage-1 code must disappear from the effective flag-OFF source;
its removal must leave the same assembly-token sequence as the FG2 snapshot.
After *intentional* release-code changes, revise the snapshot only after new
independent acceptance and record the new verified source hash.
"""
from __future__ import annotations
import hashlib
from pathlib import Path
import difflib
import sys

ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT / 'src/sutram_compiler.asm'
BASELINE = ROOT / 'compiler/verified_snapshots/FG2_R30_verified.asm.txt'
EXPECTED = 'ada9e37417edd84e40bbf5d4375e468cfbe3fa6bbbc39640261b354c2245b39a'
FLAG = 'SUTRAM_EXPERIMENTAL_XMM_CACHE'


def effective_lines(source: str):
    # Strip ONLY the opt-in experimental block; preserve normal release code,
    # %ifdef WINDOWS and all other NASM conditionals. Never reinterpret them.
    lines = []
    stack = []
    active = True
    for lineno, raw in enumerate(source.splitlines(), 1):
        stripped = raw.strip()
        parts = stripped.split()
        if parts and parts[0] in ('%ifdef','%ifndef','%if'):
            is_flag = len(parts)>1 and parts[1]==FLAG
            stack.append((active,is_flag,parts[0]))
            if is_flag: active = active and parts[0]=='%ifndef'
            elif active: lines.append(stripped)
            continue
        if stripped.startswith('%else') or stripped.startswith('%elif'):
            if not stack: raise ValueError(f'unmatched %else/%elif line {lineno}')
            parent, flagged, kind = stack[-1]
            if flagged:
                if stripped.startswith('%elif'): raise ValueError('unsupported experimental %elif')
                active = parent and not active
            elif active: lines.append(stripped)
            continue
        if stripped.startswith('%endif'):
            if not stack: raise ValueError(f'unmatched %endif line {lineno}')
            parent, flagged, _ = stack.pop()
            if not flagged and active: lines.append(stripped)
            active = parent
            continue
        if active:
            payload = raw.split(';',1)[0].strip()
            if payload: lines.append(payload)
    if stack: raise ValueError(f'unbalanced NASM conditionals: {len(stack)}')
    return lines


def main():
    baseline = BASELINE.read_bytes()
    actual_sha = hashlib.sha256(baseline).hexdigest()
    if actual_sha != EXPECTED:
        print(f'FAIL archived verified FG2 SHA: {actual_sha}', file=sys.stderr)
        return 1
    ref = effective_lines(baseline.decode('utf-8'))
    got = effective_lines(CURRENT.read_text(encoding='utf-8'))
    if got != ref:
        print('FAIL: release assembly differs from independently verified FG2',file=sys.stderr)
        print(''.join(list(difflib.unified_diff(ref,got,fromfile='verified_FG2',tofile='current_flag_OFF',lineterm='\n'))[:75]),file=sys.stderr)
        return 1
    print(f'PASS verified FG2 snapshot SHA256 {EXPECTED}')
    print(f'PASS flag-OFF release assembly token identity: {len(ref)} logical lines')
    print(f'PASS experimental source isolated; active source SHA256 {hashlib.sha256(CURRENT.read_bytes()).hexdigest()}')
    return 0


if __name__=='__main__':
    raise SystemExit(main())
