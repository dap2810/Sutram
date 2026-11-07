"""Native memory-pressure regression; baseline mode must reproduce the v305 crash.

python tests/windows/test_commit_oom.py --compiler PATH --out DIR [--expect-baseline]
No installer, global memory limit, goldens, or CI trigger is changed.
"""
import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

OOM = 'Sutram truti: smritih na labdha\n'
PROGRAMS = {
    'kosh': 'mukhya() {\n    kosh k[1]\n    chakra i = 1 tak 100000000 {\n        kosh_kship(k, i)\n    }\n    likha(kosh_gan(k))\n}\n',
    'small': 'mukhya() {\n    vitti s = 0\n    chakra i = 1 tak 20000 {\n        kosh k[1]\n        kosh_kship(k, 1)\n        s = s + k[0]\n    }\n    likha(s)\n}\n',
    'raw': 'mukhya() {\n    vitti p = nirmmita(200000000)\n    vitti i = 0\n    yavat (i < 25000000) {\n        p[i] = 42\n        i = i + 512\n    }\n    likha("done")\n}\n',
    'null': 'mukhya() {\n    vitti p = 0\n    likha(p[0])\n}\n',
}

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--compiler', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--expect-baseline', action='store_true')
    args = ap.parse_args()
    if os.name != 'nt':
        print('NOT RUN: native Windows required')
        return 77
    from job_runner import run_limited
    ctypes.windll.kernel32.SetErrorMode(0x8003)
    compiler, output = Path(args.compiler).resolve(), Path(args.out).resolve()
    output.mkdir(parents=True, exist_ok=True)
    evidence = {'compiler': str(compiler), 'compiler_sha256': hashlib.sha256(compiler.read_bytes()).hexdigest(),
                'expect_baseline_crash': args.expect_baseline, 'compilations': [], 'checks': []}
    path = output/'results.json'
    def save():
        path.write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf8')
    for name, source in PROGRAMS.items():
        src, exe = output/(name+'.sm'), output/(name+'.exe')
        src.write_text(source, encoding='utf8', newline='\n')
        cmd = [str(compiler), str(src), str(exe)]
        c = subprocess.run(cmd, capture_output=True, timeout=30)
        evidence['compilations'].append({'command': cmd, 'exit': c.returncode,
            'stdout': c.stdout.decode('utf8', 'replace'), 'stderr': c.stderr.decode('utf8', 'replace')})
        save()
        if c.returncode:
            print(f'FAIL compile {name}: {c.stdout!r} {c.stderr!r}')
            return 1
    cases = [('kosh', cap, False, True) for cap in (64, 128, 256)]
    cases += [('raw', 64, False, True), ('kosh', 64, True, True),
              ('small', 128, False, False), ('kosh', 2048, False, False), ('null', 128, False, False)]
    for name, cap, invalid_stderr, oom in cases:
        label = f'{name}-{cap}MiB' + ('-invalid-stderr' if invalid_stderr else '')
        row = run_limited(output/(name+'.exe'), output/label, cap, invalid_stderr=invalid_stderr)
        if oom:
            want_exit = 0xC0000005 if args.expect_baseline else 1
            want_stdout = ''
            want_stderr = '' if args.expect_baseline or invalid_stderr else OOM
        else:
            want_exit = 0xC0000005 if name == 'null' else 0
            want_stdout = {'null': '', 'small': '20000\n', 'kosh': '100000000\n'}[name]
            want_stderr = ''
        row.update(name=label, expected_exit=want_exit, expected_stdout=want_stdout, expected_stderr=want_stderr)
        row['pass'] = not row['timed_out'] and (row['exit'], row['stdout'], row['stderr']) == (want_exit, want_stdout, want_stderr)
        evidence['checks'].append(row)
        save()
        print(('PASS ' if row['pass'] else 'FAIL ') + label + f" exit={row['exit']} stdout={row['stdout']!r} stderr={row['stderr']!r}", flush=True)
    evidence['passed'] = sum(r['pass'] for r in evidence['checks'])
    evidence['failed'] = len(evidence['checks']) - evidence['passed']
    save()
    return int(evidence['failed'] != 0)

if __name__ == '__main__':
    sys.exit(main())
