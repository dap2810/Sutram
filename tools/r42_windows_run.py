#!/usr/bin/env python3
"""R42: the Windows checks Wine cannot settle, run on a real Windows machine (a GitHub
windows-2025 runner, started by hand from .github/workflows/r42-windows.yml).

    python -B tools/r42_windows_run.py --old-ref <commit with the previous win/sutram.exe> --out DIR

Each step's full transcript goes to DIR/<step>.txt; DIR/SUMMARY.txt gives one line per step,
PASS / FAIL / NOT-RUN, kept separate. Nothing outside DIR and a temporary directory is written.

  1. versions      the committed win/sutram.exe, and the previous one from --old-ref
  2. alias         examples 251-255 compiled by win/sutram.exe and RUN natively, against tests/expect
  3. guard         every examples/, examples/*/, tests/stdlib/, tests/r*/ program compiled the ordinary
                   way by both compilers; the PE bytes compared
  4. ffi_windows   tests/r35/test_ffi_windows.py (all its parts)
  5. link_windows  tests/r34/test_link_windows.py
  6. win_fixes     tests/r34/test_windows_fixes.py
  7. abi_gcc       tests/r35/winffi.c compiled HERE by the runner's gcc (the flags in tests/r35/OBJECTS.md),
                   read by sutram-coff2smo, linked, run, against winffi.expect - the Microsoft x64 call,
                   mixed i64/f64 by position, against a C compiler on Windows rather than a committed object
  8. abi_msvc      the same with MSVC's cl.exe, if the runner has it (NOT-RUN if not)
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
COMPILER = ROOT / 'win' / 'sutram.exe'
LINKER = ROOT / 'sutram-link.exe'
COFF2SMO = ROOT / 'sutram-coff2smo.exe'
RESULTS: list[tuple[str, str, str]] = []


def run(cmd, cwd=ROOT, timeout=120, stdin=None):
    try:
        r = subprocess.run([str(c) for c in cmd], cwd=str(cwd), capture_output=True,
                           timeout=timeout, input=stdin)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return 'TIMEOUT', b'', b''
    except OSError as e:
        return 'OSERROR', b'', str(e).encode()


def nl(b: bytes) -> bytes:
    return b.replace(b'\r\n', b'\n')


def record(step, status, detail, log, out: Path):
    RESULTS.append((step, status, detail))
    (out / f'{step}.txt').write_text('\n'.join(log) + '\n', encoding='utf-8')
    print(f'{status:8} {step}: {detail}', flush=True)


def step_versions(out, old):
    log = []
    for name, exe in (('committed win/sutram.exe', COMPILER), ('previous (--old-ref)', old)):
        rc, so, se = run([exe, '--version'])
        log.append(f'{name}: rc={rc} sha256={hashlib.sha256(Path(exe).read_bytes()).hexdigest()}')
        log.append(nl(so + se).decode('utf-8', 'replace').rstrip())
    record('versions', 'PASS', log[1].splitlines()[0] + ' / previous: ' + log[3].splitlines()[0], log, out)


def step_alias(out, tmp):
    log, bad = [], 0
    names = sorted(Path(p).stem for p in glob.glob(str(ROOT / 'examples' / '25[1-5]_*.sm')))
    for n in names:
        exe = tmp / f'{n}.exe'
        rc, so, se = run([COMPILER, ROOT / 'examples' / f'{n}.sm', exe])
        if rc != 0:
            bad += 1
            log.append(f'FAIL {n}: compile rc={rc} {nl(so + se)[-200:]!r}')
            continue
        prc, pso, pse = run([exe], timeout=30)
        want_out = nl((ROOT / 'tests' / 'expect' / f'{n}.out').read_bytes())
        want_rc = (ROOT / 'tests' / 'expect' / f'{n}.exit').read_text().strip()
        ok = nl(pso) == want_out and str(prc) == want_rc
        bad += not ok
        log.append(f'{"PASS" if ok else "FAIL"} {n}: exit {prc} (want {want_rc}), stdout {nl(pso)!r} (want {want_out!r})')
    record('alias', 'PASS' if bad == 0 and names else 'FAIL',
           f'{len(names) - bad}/{len(names)} run natively and match tests/expect', log, out)


def step_guard(out, tmp, old):
    pats = ['examples/*.sm', 'examples/*/*.sm', 'tests/stdlib/*.sm', 'tests/r*/*.sm', 'tests/r*/*/*.sm']
    progs = sorted({Path(p) for pat in pats for p in glob.glob(str(ROOT / pat))})
    ident = refused = 0
    differ: list[str] = []
    log = []
    for i, p in enumerate(progs):
        res = []
        for tag, c in (('old', old), ('new', COMPILER)):
            o = tmp / f'g{i}.{tag}.exe'
            rc, _, _ = run([c, p, o], timeout=60)
            res.append((rc, o.read_bytes() if o.exists() else None))
        (orc, od), (nrc, nd) = res
        rel = p.relative_to(ROOT).as_posix()
        if od is None and nd is None and orc == nrc:
            refused += 1
            log.append(f'REFUSED-SAME {rel} rc={orc}')
        elif od is not None and od == nd and orc == nrc:
            ident += 1
            log.append(f'IDENTICAL    {rel} {hashlib.sha256(od).hexdigest()[:16]}')
        else:
            differ.append(rel)
            log.append(f'DIFFER       {rel} old rc={orc} {len(od) if od else None}B, new rc={nrc} {len(nd) if nd else None}B')
    line = f'{len(progs)} programs: {ident} byte-identical, {refused} refused identically, {len(differ)} DIFFER'
    log.append(line)
    # the intended differences are the alias tests this change adds; anything else is a regression
    unexpected = [d for d in differ if not Path(d).name.startswith(('251_', '252_', '253_', '254_', '255_'))]
    log.append(f'DIFFER outside the five new alias tests: {len(unexpected)} {unexpected}')
    record('guard', 'PASS' if not unexpected else 'FAIL',
           line + f' (outside the 5 new alias tests: {len(unexpected)})', log, out)


def step_script(out, step, script, args):
    rc, so, se = run([sys.executable, '-B', ROOT / script] + args, timeout=1800)
    text = nl(so + se).decode('utf-8', 'replace')
    last = [l for l in text.splitlines() if l.strip()][-1:] or ['(no output)']
    record(step, 'PASS' if rc == 0 else 'FAIL', f'rc={rc}; {last[0][:160]}', [text], out)


def ffi_end_to_end(obj: Path, tmp: Path, tag: str, log: list) -> bool:
    smo, msmo, exe = tmp / f'{tag}.smo', tmp / f'{tag}-m.smo', tmp / f'{tag}.exe'
    r1 = run([COFF2SMO, obj, smo])
    r2 = run([COMPILER, '--ffi', ROOT / 'tests/r35/winffi.sffi', '--object', ROOT / 'tests/r35/winffi.sm', msmo])
    r3 = run([LINKER, exe, msmo, smo])
    for what, r in (('coff2smo', r1), ('compile --ffi --object', r2), ('link', r3)):
        log.append(f'{what}: rc={r[0]} {nl(r[1] + r[2]).decode("utf-8", "replace").strip()}')
    if not all(r[0] == 0 for r in (r1, r2, r3)):
        return False
    prc, pso, pse = run([exe], timeout=30)
    want = nl((ROOT / 'tests/r35/winffi.expect').read_bytes())
    got = nl(pso)
    nw, ng = want.count(b'\n'), got.count(b'\n')
    log.append(f'run: exit {prc}; {ng} lines; expect {nw} lines')
    for i, (a, b) in enumerate(zip(want.split(b'\n'), got.split(b'\n'))):
        if a != b:
            log.append(f'  first difference, line {i + 1}: want {a!r} got {b!r}')
            break
    return prc == 0 and got == want


def step_abi_gcc(out, tmp):
    gcc = shutil.which('gcc')
    if not gcc:
        record('abi_gcc', 'NOT-RUN', 'no gcc on PATH', ['no gcc on PATH'], out)
        return
    log = []
    rc, so, se = run([gcc, '--version'])
    log.append(nl(so).decode('utf-8', 'replace').splitlines()[0] if so else f'gcc --version rc={rc}')
    obj = tmp / 'winffi-gcc.obj'
    rc, so, se = run([gcc, '-c', '-O2', '-ffreestanding', '-fno-asynchronous-unwind-tables',
                      '-fno-stack-protector', ROOT / 'tests/r35/winffi.c', '-o', obj])
    log.append(f'gcc -c rc={rc} {nl(so + se).decode("utf-8", "replace").strip()}')
    if rc != 0:
        record('abi_gcc', 'FAIL', 'gcc could not compile winffi.c', log, out)
        return
    same = obj.read_bytes() == (ROOT / 'tests/r35/winffi.obj').read_bytes()
    log.append(f'object identical to the committed winffi.obj (GCC 16.2.0 MSYS2): {same}')
    ok = ffi_end_to_end(obj, tmp, 'gcc', log)
    record('abi_gcc', 'PASS' if ok else 'FAIL',
           f'{log[0]}: winffi.sm prints winffi.expect exactly: {ok} (object same as committed: {same})', log, out)


def step_abi_msvc(out, tmp):
    # tests/r35/winffi.c has three __attribute__((naked)) functions in GCC inline assembly (w_align, w_shadow,
    # w_clobber); MSVC has no x64 inline assembly, so cl cannot compile it. Run 40515082104 confirmed it
    # (C2143 at lines 43, 48, 53). That is a property of the test file, not an ABI result: NOT-RUN.
    if b'__attribute__((naked))' in (ROOT / 'tests/r35/winffi.c').read_bytes():
        record('abi_msvc', 'NOT-RUN', 'winffi.c has GCC naked inline asm; MSVC x64 has no inline asm', [
            'NOT-RUN: tests/r35/winffi.c uses __attribute__((naked)) + __asm__ (w_align, w_shadow, w_clobber);',
            'MSVC x64 supports no inline assembly. A MSVC check needs those three moved to a separate .asm file.'], out)
        return
    cl = shutil.which('cl')
    if not cl:
        record('abi_msvc', 'NOT-RUN', 'no cl.exe on PATH (the workflow sets up the MSVC environment first)',
               ['no cl.exe on PATH'], out)
        return
    log = []
    obj = tmp / 'winffi-msvc.obj'
    # /GS- no stack cookie (a call out), /Zl no default-library directive, /Gs999999 no stack probe;
    # MSVC still writes .pdata/.xdata for non-leaf functions and debug sections, which the reader may refuse
    rc, so, se = run([cl, '/nologo', '/c', '/O2', '/GS-', '/Zl', '/Gs999999', '/Fo' + str(obj),
                      ROOT / 'tests/r35/winffi.c'], cwd=tmp)
    log.append(f'cl /c rc={rc} {nl(so + se).decode("utf-8", "replace").strip()}')
    if rc != 0:
        record('abi_msvc', 'FAIL', 'cl could not compile winffi.c', log, out)
        return
    ok = ffi_end_to_end(obj, tmp, 'msvc', log)
    refused = 'coff2smo: rc=0' not in log[1]
    status = 'PASS' if ok else 'FAIL'
    detail = f'winffi.sm prints winffi.expect exactly: {ok}'
    if refused:
        detail = 'sutram-coff2smo refused the MSVC object (see the log for the reason); not an ABI result'
    record('abi_msvc', status, detail, log, out)


def main(argv) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--old-ref', required=True)
    ap.add_argument('--out', required=True, type=Path)
    a = ap.parse_args(argv)
    if os.name != 'nt':
        print('NOT-RUN: Windows only')
        return 0
    out = a.out
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='r42-') as td:
        tmp = Path(td)
        old = tmp / 'sutram-old.exe'
        old.write_bytes(subprocess.run(['git', 'show', f'{a.old_ref}:win/sutram.exe'], cwd=ROOT,
                                       capture_output=True, check=True).stdout)
        steps = [
            lambda: step_versions(out, old),
            lambda: step_alias(out, tmp),
            lambda: step_guard(out, tmp, old),
            lambda: step_script(out, 'ffi_windows', 'tests/r35/test_ffi_windows.py', []),
            lambda: step_script(out, 'link_windows', 'tests/r34/test_link_windows.py', []),
            lambda: step_script(out, 'win_fixes', 'tests/r34/test_windows_fixes.py',
                                ['--compiler', str(COMPILER), '--linker', str(LINKER)]),
            lambda: step_abi_gcc(out, tmp),
            lambda: step_abi_msvc(out, tmp),
        ]
        for s in steps:
            try:
                s()
            except Exception as e:  # a crashed step is a FAIL with its reason, and the rest still run
                RESULTS.append((getattr(s, '__name__', 'step'), 'FAIL', f'driver error: {e!r}'))
                print(f'FAIL     driver error: {e!r}', flush=True)
    counts = {k: sum(1 for _, s, _ in RESULTS if s == k) for k in ('PASS', 'FAIL', 'NOT-RUN')}
    lines = [f'{s:8} {n}: {d}' for n, s, d in RESULTS]
    lines += ['', f'PASS {counts["PASS"]}  FAIL {counts["FAIL"]}  NOT-RUN {counts["NOT-RUN"]}']
    (out / 'SUMMARY.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print('\n'.join(lines[-1:]))
    return 1 if counts['FAIL'] else 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
