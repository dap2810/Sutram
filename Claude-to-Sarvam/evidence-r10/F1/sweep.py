#!/usr/bin/env python3
"""F1 threshold sweep: a called function with N local variables (plus one parameter), and mukhya
with N variables. Every variable is declared, assigned, updated with +=, and read; the caller keeps
three register variables live and a pushed temporary (1000 + f(1)). Prints one line per N."""
import subprocess, sys, tempfile, os
from pathlib import Path

def _body(n, base):
    """n declarations, +1 on up to 12 variables spread across all slots, sums of 10 per statement.
    Stays under the 256-statements-per-block limit for n up to about 220."""
    L = [f'    vitti v{i} = {base} + {i}' for i in range(n)]
    touched = sorted({(k * n) // 12 for k in range(12)}) if n else []
    L += [f'    v{i} += 1' for i in touched]
    L += ['    vitti s = 0']
    for k in range(0, n, 10):
        L.append('    s = s + ' + ' + '.join(f'v{i}' for i in range(k, min(n, k + 10))))
    return L, touched

def callee_prog(n):
    body, touched = _body(n, 'p')
    L = ['prakriya f(p) {'] + body + ['    prati s', '}']
    L += ['mukhya() {', '    vitti a = 10', '    vitti b = 20', '    vitti c = 30',
          '    vitti r = 1000 + f(1)', '    likha(a)', '    likha(b)', '    likha(c)', '    likha(r)', '}']
    want = [10, 20, 30, 1000 + sum(1 + i for i in range(n)) + len(touched)]
    return '\n'.join(L) + '\n', want

def main_prog(n):
    body, touched = _body(n, '1')
    L = ['mukhya() {'] + body + ['    likha(s)', '}']
    return '\n'.join(L) + '\n', [sum(1 + i for i in range(n)) + len(touched)]

def run(comp, src, d, runner=None):
    sm, exe = Path(d, 't.sm'), Path(d, 't.exe' if runner else 't.bin')
    sm.write_text(src)
    c = subprocess.run((runner or []) + [comp, str(sm), str(exe)], capture_output=True, timeout=120)
    if not exe.exists():
        return 'COMPILE-ERROR'
    try:
        r = subprocess.run((runner or []) + [str(exe)], capture_output=True, timeout=60)
    except subprocess.TimeoutExpired:
        return 'TIMEOUT'
    out = r.stdout.decode(errors='replace').replace('\r', '').split()
    exe.unlink()
    return out, r.returncode

if __name__ == '__main__':
    comp = sys.argv[1]; kind = sys.argv[2]; ns = [int(x) for x in sys.argv[3].split(',')]
    runner = sys.argv[4].split() if len(sys.argv) > 4 else None
    with tempfile.TemporaryDirectory(dir=os.path.dirname(os.path.abspath(__file__))) as d:
        for n in ns:
            src, want = (callee_prog if kind == 'callee' else main_prog)(n)
            got = run(comp, src, d, runner)
            if isinstance(got, str):
                print(f'{kind} n={n}: {got}'); continue
            out, rc = got
            ok = out == [str(w) for w in want] and rc == 0
            print(f"{kind} n={n:4}: {'OK     ' if ok else 'WRONG  '} exit={rc} got={' '.join(out[:4]) or '(nothing)'} want={' '.join(map(str, want))}")
