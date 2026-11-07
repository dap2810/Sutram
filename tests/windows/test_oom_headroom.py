#!/usr/bin/env python3
"""R136: settle why the out-of-memory exit overflows the stack at some commit limits and not others. Windows only.

Native v306/v307: B3 (100 million pushes) printed `Sutram truti: smritih na labdha` and then exited 0xC00000FD
(STATUS_STACK_OVERFLOW) at 480 and 512 MiB (3/3), 2 of 3 at 448, never at 64-256 or 544-640; mandapa at 64 MiB 10/10.
The source cannot say why (Muse R137): the faulting code, the stack depth and the handler path are the same at 128
and 512 MiB. Two measurements can:

  1. the headroom: the job's limit minus the process's peak commit (job_runner now records PeakProcessMemoryUsed).
     Prediction: 0xC00000FD exactly when the headroom at the peak is below what the exit's stack needs (a few pages);
  2. Muse's probe: the same binary with SizeOfStackCommit raised to 1 MiB (the stack is committed at start, so the
     exit never grows it). Prediction: no 0xC00000FD at any limit on v306/v307 binaries.
And v308's answer: its runtime keeps 64 KiB of commit and releases it before the message, so the headroom at the
exit is at least 64 KiB. Prediction: no 0xC00000FD from a v308 binary, stack commit unchanged.

    python tests/windows/test_oom_headroom.py --compiler PATH --out DIR [--runs 3]
Run it with a v307 compiler and with the v308 one. It writes DIR/headroom.json and prints one row per run; the last
line is "oom headroom: N runs, M ended 0xC00000FD". Prints NOT RUN off Windows.
"""
import argparse, json, os, struct, subprocess, sys
from pathlib import Path

B3 = 'mukhya() {\n    kosh k[1]\n    chakra i = 1 tak 100000000 {\n        kosh_kship(k, i)\n    }\n    likha(kosh_gan(k))\n}\n'
MANDAPA = ('mukhya() {\n    mandapa parimita 67108864 {\n        vitti s = 0\n        chakra i = 1 tak 2000000 {\n'
           '            vitti p = nirmmita(64)\n            p[0] = i\n            s = s + p[0]\n        }\n        likha(s)\n    }\n}\n')
CASES = [('B3', B3, [448, 480, 512, 544, 640]), ('mandapa', MANDAPA, [64])]


def stack_commit(src, dst, commit):
    d = bytearray(open(src, 'rb').read())
    o = struct.unpack_from('<I', d, 0x3C)[0] + 24
    assert struct.unpack_from('<H', d, o)[0] == 0x20B, 'not PE32+'
    reserve = max(struct.unpack_from('<Q', d, o + 72)[0], 2 * commit)
    struct.pack_into('<Q', d, o + 72, reserve)
    struct.pack_into('<Q', d, o + 80, commit)
    open(dst, 'wb').write(d)


def main():
    if os.name != 'nt':
        print('NOT RUN: native Windows required')
        print('oom headroom: 0 runs, 0 ended 0xC00000FD')
        return 0
    ap = argparse.ArgumentParser()
    ap.add_argument('--compiler', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--runs', type=int, default=3)
    a = ap.parse_args()
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from job_runner import run_limited
    out = Path(a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    rows, fd = [], 0
    for name, src, limits in CASES:
        sm = out / (name + '.sm')
        sm.write_text(src, encoding='utf-8')
        exe = out / (name + '.exe')
        c = subprocess.run([a.compiler, str(sm), str(exe)], capture_output=True, text=True)
        if not exe.exists():
            print(f'FAIL compile {name}: {c.stdout} {c.stderr}')
            return 1
        stk = out / (name + '-stackcommit1M.exe')
        stack_commit(exe, stk, 1 << 20)
        runs = a.runs if name == 'B3' else max(a.runs, 5)
        for variant, binary in (('as built', exe), ('stack commit 1 MiB', stk)):
            for limit in limits:
                for i in range(runs):
                    r = run_limited(binary, out / f'{name}-{variant[:5].strip()}-{limit}-{i}', limit)
                    r.update(case=name, variant=variant, limit_mib=limit)
                    fd += r.get('exit') == 0xC00000FD
                    rows.append(r)
                    print(f"{name:8} {variant:19} {limit:4} MiB  exit {r.get('exit'):#x}  headroom "
                          f"{r.get('headroom_bytes', 'n/a')}  stderr {r.get('stderr', '')!r}", flush=True)
    (out / 'headroom.json').write_text(json.dumps(rows, indent=2) + '\n', encoding='utf-8')
    print(f'oom headroom: {len(rows)} runs, {fd} ended 0xC00000FD')
    return 0


if __name__ == '__main__':
    sys.exit(main())
