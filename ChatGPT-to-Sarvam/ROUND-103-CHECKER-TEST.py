#!/usr/bin/env python3
"""R103 standalone source-gate regression fixtures, not native Sutram tests."""
from pathlib import Path
import subprocess
import sys
import tempfile

SCRIPT = Path(__file__).with_name('ROUND-103-CHECK-ALLOC-SIZES.py')

with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp)
    target = path / 'mala.smlib'
    target.write_text('prakriya mala_nava(n) {\n vitti sz = n * 8\n prati nirmmita(sz)\n}\n')
    out = subprocess.run([sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True)
    assert out.returncode == 0, (out.stdout, out.stderr)
    print('PASS reviewed spellings accepted (NOT certified safe)')

    target.write_text('prakriya mala_nava(n) {\n prati nirmmita(n * 8)\n}\n')
    out = subprocess.run([sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True)
    assert out.returncode == 1 and 'UNREVIEWED' in out.stdout
    print('PASS new unsafe allocation formula rejected')

    target.write_text('prakriya mala_nava(n) {\n prati nirmmita((n * 8) + 16)\n}\n')
    out = subprocess.run([sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True)
    assert out.returncode == 1 and 'UNREVIEWED' in out.stdout
    print('PASS parenthesized new formula rejected')

    target.write_text('prakriya mala_nava(n) {\n prati nirmmita(n * 8\n}\n')
    out = subprocess.run([sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True)
    assert out.returncode == 1 and 'UNPARSED' in out.stdout
    print('PASS incomplete allocation call rejected')

print('RESULT 4 PASS / 0 FAIL; checker fixtures only')
