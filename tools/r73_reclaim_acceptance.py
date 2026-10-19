#!/usr/bin/env python3
"""Run genuine Sutram acceptance for the staged R73 reclamation profile.

Requires separately built Linux default-reclaim and KOSH_PRACHIN compilers.
No download or toolchain installation. Do not relabel fixture validation or
unit-test process mocks as native acceptance. Expected .out files are candidates
until this command actually succeeds against a full NASM-built compiler.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import select
import subprocess
import tempfile
import time
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT/'examples/r73'
REJECTION = b'E_KOSH_RECLAIM_TARGET'


def require(condition: bool, message: str) -> None:
    if not condition: raise ValueError(message)


def execute(command: list[str], root: Path = ROOT) -> subprocess.CompletedProcess:
    env = {k:v for k,v in os.environ.items() if not k.upper().startswith('SUTRAM_')}
    return subprocess.run(command, cwd=root, env=env, stdin=subprocess.DEVNULL,
                          capture_output=True, timeout=45, check=False)


def compile_case(compiler: Path, source: Path, output: Path) -> None:
    require(not os.path.lexists(output), 'output must be fresh')
    p=execute([str(compiler),str(source),str(output)])
    require(p.returncode==0, f'compile failed: {p.returncode} {p.stdout!r} {p.stderr!r}')
    require(output.is_file() and not output.is_symlink() and output.stat().st_nlink==1,
            'compiler did not create an unlinked regular executable')
    data=output.read_bytes()
    require(len(data)>=64 and data[:7]==b'\x7fELF\x02\x01\x01' and data[18:20]==b'\x3e\0',
            'generated output is not Linux ELF64 x86-64')


def vm_size(pid: int) -> int:
    for line in Path(f'/proc/{pid}/status').read_text('ascii').splitlines():
        if line.startswith('VmSize:'):
            fields=line.split()
            require(fields[2]=='kB','unexpected VmSize unit')
            return int(fields[1])*1024
    raise ValueError('child VmSize unavailable')


def line_before(stream, deadline: float) -> bytes:
    result=bytearray()
    while len(result)<128:
        remaining=deadline-time.monotonic()
        require(remaining>0,'timed out waiting for memory-probe barrier')
        ready,_,_=select.select([stream],[],[],remaining)
        require(bool(ready),'timed out waiting for memory-probe output')
        char=os.read(stream.fileno(),1)
        require(bool(char),'memory probe exited before barrier')
        result.extend(char)
        if char==b'\n': return bytes(result)
    raise ValueError('unbounded memory-probe output')


def measure_memory(executable: Path) -> dict[str, int]:
    env={k:v for k,v in os.environ.items() if not k.upper().startswith('SUTRAM_')}
    p=subprocess.Popen([str(executable)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, bufsize=0, env=env)
    try:
        deadline=time.monotonic()+45
        require(line_before(p.stdout,deadline)==b'1\n','wrong initial memory barrier')
        before=vm_size(p.pid)
        p.stdin.write(b'0\n'); p.stdin.flush()
        require(line_before(p.stdout,deadline)==b'2097152\n','wrong grown capacity')
        require(line_before(p.stdout,deadline)==b'1048577\n','wrong grown length')
        require(line_before(p.stdout,deadline)==b'1048576\n','growth corrupted final element')
        after=vm_size(p.pid)
        p.stdin.write(b'0\n'); p.stdin.flush()
        out,err=p.communicate(timeout=10)
        require(p.returncode==0 and out==b'' and err==b'','memory probe failed after final barrier')
        return {'before_bytes':before,'after_bytes':after,'delta_bytes':after-before}
    finally:
        if p.poll() is None:
            p.kill(); p.wait(timeout=10)
        for stream in (p.stdin,p.stdout,p.stderr):
            if stream and not stream.closed: stream.close()


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compiler',type=Path,required=True)
    parser.add_argument('--legacy',type=Path,required=True)
    parser.add_argument('--report',type=Path,required=True)
    args=parser.parse_args()
    try:
        require(not os.path.lexists(args.report),'refuse existing/symlink report')
        compilers=[args.compiler.absolute(),args.legacy.absolute()]
        for c in compilers:
            require(c.is_file() and not c.is_symlink(),'compiler must be a regular non-symlink file')
        require(not os.path.samefile(*compilers),'compilers must be independently built files')
        identities=[hashlib.sha256(c.read_bytes()).hexdigest() for c in compilers]
        require(identities[0]!=identities[1],'reclaim/legacy compiler bytes unexpectedly identical')
        results=[]
        with tempfile.TemporaryDirectory(prefix='sutram-r71-native-') as tmp:
            work=Path(tmp)
            for stem in ('growth_int','growth_float','unaffected'):
                expected=(CASES/(stem+'.out')).read_bytes()
                binaries=[]
                for n,c in enumerate(compilers):
                    exe=work/f'{stem}-{n}.bin'
                    compile_case(c,CASES/(stem+'.sm'),exe)
                    p=execute([str(exe)])
                    require((p.returncode,p.stdout,p.stderr)==(0,expected,b''),
                            f'native stdout mismatch: {stem}: {p.returncode} {p.stdout!r} {p.stderr!r}')
                    binaries.append(exe.read_bytes())
                require((binaries[0]==binaries[1]) == (stem=='unaffected'),
                        'wrong byte-identity relationship for '+stem)
                results.append({'case':stem,'status':'PASS','stdout':expected.decode('ascii'),
                                'reclaim_bytes':len(binaries[0]),'legacy_bytes':len(binaries[1])})
            measurements=[]
            for n,c in enumerate(compilers):
                exe=work/f'memory-{n}.bin'
                compile_case(c,CASES/'memory_growth.sm',exe)
                measurements.append(measure_memory(exe))
            page=os.sysconf('SC_PAGE_SIZE')
            live_bytes=((2097152*8+16+page-1)//page)*page
            # Measured VmSize, not RSS: explicit 256-KiB allowance for process
            # bookkeeping/stack differences, far below the old ~16-MiB excess.
            tolerance=256*1024
            require(measurements[0]['delta_bytes']<=live_bytes+tolerance,
                    'reclaim process retains more mapping space than live-buffer bound')
            require(measurements[1]['delta_bytes']-measurements[0]['delta_bytes']>8*1024*1024,
                    'legacy control does not reproduce measurable retained mappings')
            pe=work/'unsupported.exe'
            p=execute([str(compilers[0]),str(CASES/'growth_int.sm'),str(pe)])
            require(p.returncode==1 and REJECTION in p.stdout+p.stderr and not os.path.lexists(pe),
                    'PE path did not fail closed with target diagnostic/no output')
        report={'native_status':'PASS','compiler_executed':True,'cases':results,
                'compiler_sha256':identities,'memory':{'reclaim':measurements[0],'legacy':measurements[1],
                'live_buffer_page_bytes':live_bytes,'allowance_bytes':tolerance},
                'windows_executed':False,'scope':'staged Linux reclamation only; not full regression'}
        with args.report.open('x',encoding='utf-8') as f:
            json.dump(report,f,indent=2);f.write('\n')
        print(json.dumps(report,indent=2)); return 0
    except (OSError,ValueError,subprocess.TimeoutExpired) as exc:
        parser.exit(1,'R73_RECLAIM_ACCEPTANCE_FAILED: '+str(exc)+'\n')


if __name__=='__main__': raise SystemExit(main())
