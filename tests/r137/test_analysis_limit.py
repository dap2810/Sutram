#!/usr/bin/env python3
"""Force the validator budget to zero in a disposable host build; never alter the shipped host."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--nasm', default='nasm')
    p.add_argument('--linker', default='ld')
    p.add_argument('--report', type=Path, required=True)
    a = p.parse_args()
    original = (ROOT / 'src/sutram_compiler.asm').read_bytes()
    source = original.decode('utf8')
    old = 'mov qword [rel r137_budget], 200000'
    assert source.count(old) == 1
    build = ROOT / 'build'
    build.mkdir(exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix='analysis-limit-', dir=build))
    (work / 'src').mkdir()
    (work / 'src/sutram_compiler.asm').write_text(source.replace(old, 'mov qword [rel r137_budget], 0'), encoding='utf8')
    shutil.copyfile(ROOT / 'src/r68_compiler_entry.asm', work / 'entry.asm')
    commands = [
        [a.nasm, '-f', 'win64', '-dWINDOWS', '-I' + ROOT.as_posix() + '/', 'entry.asm', '-o', 'host.obj'],
        [a.linker, '-mi386pep', '--entry=_start', '-o', 'host.exe', 'host.obj'],
    ]
    rows = []
    for cmd in commands:
        r = subprocess.run(cmd, cwd=work, capture_output=True, text=True, timeout=60)
        rows.append(dict(command=cmd, exit=r.returncode, stdout=r.stdout, stderr=r.stderr))
        assert r.returncode == 0, rows[-1]
    for name, program in [('local', 'mukhya() { likha(1) }\n'), ('global', 'vitti a = 1\nmukhya() { likha(a) }\n')]:
        sm, exe = work / f'{name}.sm', work / f'{name}.exe'
        sm.write_text(program, encoding='utf8')
        cmd = [str(work / 'host.exe'), str(sm), str(exe)]
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=15)
        rows.append(dict(command=cmd, exit=r.returncode, stdout=r.stdout, stderr=r.stderr, output_exists=exe.exists()))
        assert r.returncode != 0 and not exe.exists() and '[E_VISHLESHANA_SEEMA]' in r.stdout + r.stderr, rows[-1]
    assert (ROOT / 'src/sutram_compiler.asm').read_bytes() == original
    a.report.write_text(json.dumps(dict(source_sha256=hashlib.sha256(original).hexdigest(),
                                      forced_budget=0, commands=rows, source_unchanged=True), indent=2) + '\n', encoding='utf8')
    print('PASS: local and global validation refuse an exhausted budget; production source unchanged')


if __name__ == '__main__':
    main()
