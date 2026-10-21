#!/usr/bin/env python3
"""Measure real /proc mappings at kosh checkpoints using two native Sutram compilers.

Requires existing Linux x86-64 compiler ELF files, no network, no CI, no golden rewrites.
Raw aliases are untracked; a better RSS/mapping result is NOT a memory safety proof.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import select
import signal
import stat
import struct
import subprocess
import tempfile
import time


def source(n: int) -> str:
    if not 16 <= n <= 8_000_000:
        raise ValueError('bounded push count required')
    return ("mukhya() {\n"
            "    kosh v[4]\n"
            '    likha("R75_BASE\\n")\n'
            "    grahan()\n"
            "    vitti i = 0\n"
            f"    yavat (i < {n}) {{\n"
            "        kosh_push(v, i)\n"
            "        i = i + 1\n"
            "    }\n"
            '    likha("R75_GROWN\\n")\n'
            "    grahan()\n"
            "    likha(kosh_len(v))\n"
            '    likha("\\n")\n'
            "}\n")


def elf_info(path: Path) -> dict:
    if path.is_symlink() or not path.is_file() or not stat.S_ISREG(path.stat().st_mode):
        raise ValueError('non-regular executable: '+str(path))
    raw = path.read_bytes()
    if len(raw) < 64 or raw[:7] != b'\x7fELF\x02\x01\x01' or struct.unpack_from('<H', raw, 18)[0] != 62:
        raise ValueError('not x86-64 Linux ELF: '+str(path))
    return {'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}


def snapshot(pid: int) -> dict:
    entries = Path(f'/proc/{pid}/maps').read_text().splitlines()
    status = Path(f'/proc/{pid}/status').read_text().splitlines()
    out = {'maps_count': len(entries)}
    for metric in ('VmSize', 'VmRSS', 'VmHWM'):
        val = next((line.split()[1] for line in status if line.startswith(metric+':')), None)
        out[metric+'_kb'] = int(val) if val is not None else None
    return out


def until(proc: subprocess.Popen, marker: bytes, deadline: float) -> bytes:
    seen = b''
    while marker not in seen:
        if proc.poll() is not None:
            raise RuntimeError(f'child exited before {marker!r}: {seen[-160:]!r}')
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError('marker timeout '+repr(marker))
        r, _, _ = select.select([proc.stdout.fileno()], [], [], remaining)
        if not r:
            raise TimeoutError('marker timeout '+repr(marker))
        data = os.read(proc.stdout.fileno(), 4096)
        if not data:
            raise RuntimeError('unexpected EOF before marker')
        seen += data
        if len(seen) > 65536:
            raise RuntimeError('unexpected excessive stdout')
    return seen


def run(compiler: Path, source_path: Path, output_path: Path, n: int, seconds: float) -> dict:
    p = subprocess.run([str(compiler), str(source_path), str(output_path)],
                       capture_output=True, stdin=subprocess.DEVNULL, timeout=seconds)
    if p.returncode != 0 or not output_path.is_file():
        raise RuntimeError(f'compile exit={p.returncode} stdout={p.stdout[-240:]!r} stderr={p.stderr[-240:]!r}')
    binary = elf_info(output_path)
    output_path.chmod(0o700)
    child = subprocess.Popen([str(output_path)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, start_new_session=True)
    out = b''
    try:
        deadline = time.monotonic()+seconds
        out += until(child, b'R75_BASE', deadline)
        first = snapshot(child.pid)
        child.stdin.write(b'0\n')
        child.stdin.flush()
        out += until(child, b'R75_GROWN', deadline)
        second = snapshot(child.pid)
        child.stdin.write(b'0\n')
        child.stdin.flush()
        child.stdin.close()
        while child.poll() is None and time.monotonic() < deadline:
            time.sleep(.01)
        if child.poll() is None:
            raise TimeoutError('child did not exit')
        out += child.stdout.read()
        err = child.stderr.read()
        if child.returncode or err:
            raise RuntimeError(f'child exit={child.returncode} stderr={err[-240:]!r}')
        if str(n).encode() not in out.split(b'R75_GROWN')[-1]:
            raise RuntimeError(f'kosh_len did not report {n}')
        return {'compiler': str(compiler), 'compiler_binary': elf_info(compiler),
                'generated_binary': binary, 'source_sha256': hashlib.sha256(source_path.read_bytes()).hexdigest(),
                'before': first, 'after_growth': second, 'stdout_hex': out.hex(), 'exit': child.returncode}
    finally:
        if child.poll() is None:
            os.killpg(child.pid, signal.SIGKILL)
            child.wait(timeout=3)
        for stream in (child.stdin, child.stdout, child.stderr):
            if stream and not stream.closed:
                stream.close()


def main() -> int:
    arg = argparse.ArgumentParser(description=__doc__)
    arg.add_argument('--legacy-compiler', type=Path, required=True)
    arg.add_argument('--reclaim-compiler', type=Path, required=True)
    arg.add_argument('--items', type=int, default=1_000_000)
    arg.add_argument('--timeout', type=float, default=120)
    arg.add_argument('--report', type=Path)
    a = arg.parse_args()
    try:
        if platform.system() != 'Linux' or platform.machine() != 'x86_64':
            raise ValueError('Linux x86-64 required')
        legacy = a.legacy_compiler.resolve(strict=True)
        candidate = a.reclaim_compiler.resolve(strict=True)
        if legacy == candidate or elf_info(legacy)['sha256'] == elf_info(candidate)['sha256']:
            raise ValueError('independent, distinct compiler binaries required')
        with tempfile.TemporaryDirectory(prefix='sutram-r75-maps-') as td:
            work = Path(td)
            source_path = work/'grow.sm'
            source_path.write_text(source(a.items))
            left = run(legacy, source_path, work/'left.bin', a.items, a.timeout)
            right = run(candidate, source_path, work/'right.bin', a.items, a.timeout)
        def delta(r):
            return {k: (r['after_growth'][k]-r['before'][k])
                    if r['after_growth'][k] is not None and r['before'][k] is not None else None
                    for k in ('maps_count','VmSize_kb','VmRSS_kb','VmHWM_kb')}
        data = {'status':'MEASURED_REQUIRES_REVIEW', 'items':a.items,
                'legacy':left, 'candidate':right,
                'delta':{'legacy':delta(left),'candidate':delta(right)},
                'warnings':['Linux may merge adjacent VMAs: map count alone is insufficient',
                            'Peak RSS includes transient coexistence during copy',
                            'Raw aliases may dangle after reclamation',
                            'Final live container backing is not freed at scope exit']}
        result = 0
    except (OSError,ValueError,RuntimeError,TimeoutError,subprocess.TimeoutExpired) as exc:
        data={'status':'FAIL','reason':str(exc)}
        result = 2
    text = json.dumps(data,indent=2)+'\n'
    print(text,end='')
    if a.report:
        with a.report.open('x',encoding='utf8') as f:
            f.write(text)
    return result

if __name__ == '__main__':
    raise SystemExit(main())
