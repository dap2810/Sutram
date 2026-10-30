#!/usr/bin/env python3
"""The guard-page gate (R68 measurement, R69 permanent tool).

    python3 tools/guard_page.py [--quick] [--keep DIR]

Builds the compiler from src/ with `nasm -dGUARD_PAGES` into a scratch directory. In that build every
`nirmmita` block is its own mmap, placed so that the block ENDS on the last byte before a PROT_NONE page:
one byte READ or WRITTEN past any block is SIGSEGV, exactly at the byte, not at the next page. There is no
arena and no kosh extension in this build; it is never shipped. Then it runs, with that compiler:

  1. the controls in tests/guard_page/  - each `control_*.sm` must die with SIGSEGV, each `clean_*.sm` must
     exit 0. The named control bugs, all real bugs this project had:
       control_217_overrun      examples/217_r12_report.sm before R68: 4 cells handed to pad_vam(width 6)
       control_proof_overread   the "bigint divmod reconstruct" proof before R65: a READ of cells 8..15
                                of an 8-cell block (a read, not a write - the guard catches both)
       control_pack_unpack      prop_strb_pack_unpack before R68: khand_mukt writes cell 8 of 8 cells
       control_one_byte_past    one byte past a 13-byte block (precision)
     and clean_last_byte writes the 13-byte block's last byte (the guard is not one byte too tight).
     If a control does not fault, the build is not a guard-page build and nothing below means anything.
  2. the regression suite (tests/run_tests.py)  - every example, compared with its golden
  3. the library proofs (tools/proof_lib.py)    - every tests/stdlib program
  4. the property proofs (tools/proof_props.py)

A program that touches memory it was not given fails in 2-4 as a crash. The last line is the summary, e.g.
`guard pages: controls 5/5, suite PASS=225 FAIL=0, library proofs 226/226, property proofs 86/86, 0 failed`.
--quick runs the controls only (seconds). Exit 0 only when every check holds.

What it cannot see: a path no test executes; an access that lands inside ANOTHER live block without first
crossing a block's end (a wild index far past the guard page, or a negative index - the page before a block
is not guarded); a mistake within a block's own bytes; declared `mala`/`kosh` storage, which the compiler
checks itself; Windows (PE output keeps its own allocator). The static audit (Claude-to-Sarvam/R68-00) is
the other half.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTROLS = os.path.join(ROOT, 'tests', 'guard_page')


def build(work):
    obj = os.path.join(work, 'g.o')
    exe = os.path.join(work, 'sutram_compiler')
    r = subprocess.run(['nasm', '-f', 'elf64', '-dGUARD_PAGES', '-I.', 'src/r68_compiler_entry.asm', '-o', obj],
                       cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit('guard pages: the GUARD_PAGES build failed: ' + r.stderr[-400:])
    r = subprocess.run(['ld', '-o', exe, obj], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit('guard pages: link failed: ' + r.stderr[-400:])
    # the compiler finds lib/ and lang/ beside itself
    for d in ('lib', 'lang', 'win'):
        if os.path.exists(os.path.join(ROOT, d)):
            os.symlink(os.path.join(ROOT, d), os.path.join(work, d))
    return exe


def controls(exe, work):
    ok = total = 0
    for name in sorted(os.listdir(CONTROLS)):
        if not name.endswith('.sm'):
            continue
        total += 1
        src = os.path.join(CONTROLS, name)
        out = os.path.join(work, name[:-3])
        c = subprocess.run([exe, src, out], cwd=ROOT, capture_output=True, text=True)
        if c.returncode != 0:
            print(f'FAIL  {name}: did not compile: {(c.stdout + c.stderr).strip()[-200:]}')
            continue
        r = subprocess.run([out], capture_output=True, timeout=20)
        want_fault = name.startswith('control_')
        faulted = r.returncode in (-11, 139)
        if want_fault == faulted and (want_fault or r.returncode == 0):
            ok += 1
            print(f'PASS  {name}: {"SIGSEGV, as it must" if want_fault else "runs clean"}')
        else:
            print(f'FAIL  {name}: exit {r.returncode}, wanted {"SIGSEGV" if want_fault else "0"}')
    return ok, total


def run(cmd, env=None):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, env=env)
    return r.stdout + r.stderr


def main():
    quick = '--quick' in sys.argv
    keep = sys.argv[sys.argv.index('--keep') + 1] if '--keep' in sys.argv else None
    work = keep or tempfile.mkdtemp(prefix='guard-page-')
    os.makedirs(work, exist_ok=True)
    try:
        exe = build(work)
        ok, total = controls(exe, work)
        parts = [f'controls {ok}/{total}']
        failed = total - ok
        if not quick and ok == total:
            env = dict(os.environ, SUTRAM_COMPILER=exe)
            out = run([sys.executable, 'tests/run_tests.py'], env)
            p = re.search(r'PASS=(\d+)', out)
            f = re.search(r'FAIL=(\d+)', out)
            nf = int(f.group(1)) if f else 0
            parts.append(f'suite PASS={p.group(1) if p else "?"} FAIL={nf}')
            failed += nf + (0 if p else 1)
            if nf:
                print(out[-2000:])
            out = run([sys.executable, 'tools/proof_lib.py', '--compiler', exe]).strip().splitlines()
            m = re.search(r'(\d+) passed, (\d+) failed, (\d+) total', out[-1] if out else '')
            parts.append(f'library proofs {m.group(1)}/{m.group(3)}' if m else 'library proofs: no summary')
            failed += int(m.group(2)) if m else 1
            if not m or int(m.group(2)):
                print('\n'.join(out[-40:]))
            out = run([sys.executable, 'tools/proof_props.py', '--compiler', exe]).strip().splitlines()
            m = re.search(r'(\d+)/(\d+) properties hold', out[-1] if out else '')
            parts.append(f'property proofs {m.group(1)}/{m.group(2)}' if m else 'property proofs: no summary')
            failed += (int(m.group(2)) - int(m.group(1))) if m else 1
            if not m or m.group(1) != m.group(2):
                print('\n'.join(l for l in out if l.startswith('FAIL') or l.startswith('  ')))
        elif not quick:
            parts.append('corpora NOT RUN: a control failed, so this is not a guard-page build')
        print('guard pages: ' + ', '.join(parts) + f', {failed} failed')
        return 1 if failed else 0
    finally:
        if not keep:
            shutil.rmtree(work, ignore_errors=True)


if __name__ == '__main__':
    sys.exit(main())
