"""R71 Linux reclamation: real payload instructions + mocked source preparation.

Not a full NASM compiler test. No generated Sutram binary is used here.
"""
from __future__ import annotations
import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
PAYLOAD = ROOT / 'src/r73_kosh_vriddhi.inc'
CAPACITY_ERROR = b'Sutram Error [E_KOSH_CAPACITY]: kosh vriddhi parimana dosh\n'
ALLOC_ERROR = b'Sutram Error [E_KOSH_ALLOC]: kosh vriddhi viniyog asafal\n'
RECLAIM_ERROR = b'Sutram Error [E_KOSH_RECLAIM]: purana kosh smriti mukti asafal\n'


def payload_gas(name: str) -> str:
    """Narrow test-only syntax bridge; product source stays hand-written NASM."""
    text = PAYLOAD.read_text('utf-8')
    marker = '; BEGIN PAYLOAD ' + name + '\n'
    end = '; END PAYLOAD ' + name
    if text.count(marker) != 1 or text.count(end) != 1:
        raise ValueError('bad payload markers')
    body = text.split(marker)[1].split(end)[0]
    out = []
    for original in body.splitlines():
        line = original.split(';', 1)[0].strip()
        if not line: continue
        line = re.sub(r'(?<![\w])\.([A-Za-z_]\w*)', lambda m: '.L_' + name + '_' + m[1], line)
        line = line.replace('[rel ', '[rip + ')
        if line.startswith('db '):
            parsed = re.fullmatch(r'db ("[^"\\]*"),10', line)
            if not parsed: raise ValueError('unsupported db syntax: ' + line)
            out.append('.ascii ' + json.dumps(ast.literal_eval(parsed.group(1)) + '\n'))
        else:
            out.append(line)
    # Test-only RET, not part of the emitted inline payload.
    out.append('ret')
    return '\n'.join(out) + '\n'


BRIDGES = '''
.global growth_guard_bridge
.global allocation_guard_bridge
.global reclaim_bridge
growth_guard_bridge:
    mov r10,rdi
    mov r9,rsi
    mov rax,0x123456789abcdef0
    call r73_vriddhi_adi
    ret
allocation_guard_bridge:
    mov rax,rdi
    call r73_viniyog_adi
    ret
reclaim_bridge:
    mov r8,rdi
    mov r10,rsi
    mov r9,[r8-16]
    mov rax,r10
    mov rcx,0x1122334455667788
    mov rdi,0x1020304050607080
    mov rsi,0x8877665544332211
    mov r11,0x0123456789abcdef
    call r73_mukti_adi
    mov [rdx],rax
    mov [rdx+8],rcx
    mov [rdx+16],rdi
    mov [rdx+24],rsi
    mov [rdx+32],r11
    mov [rdx+40],r8
    mov [rdx+48],r9
    mov [rdx+56],r10
    ret
'''


class NativePayloadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.name != 'posix' or os.uname().machine != 'x86_64' or not shutil.which('gcc'):
            raise unittest.SkipTest('requires existing Linux x86-64/GCC; no installation attempted')
        cls.temp = tempfile.TemporaryDirectory(prefix='sutram-r71-reclaim-')
        cls.work = Path(cls.temp.name)
        source = '.intel_syntax noprefix\n.text\n' + ''.join(payload_gas(n) for n in ('growth_guard', 'allocation_guard', 'reclaim'))
        source += BRIDGES + '\n.section .note.GNU-stack,"",@progbits\n'
        asm = cls.work/'payload.S'
        asm.write_text(source)
        cls.probe = cls.work/'probe'
        result = subprocess.run(['gcc','-std=c11','-O2','-Wall','-Wextra','-Werror','-no-pie',
             str(Path(__file__).with_name('native_probe.c')),str(asm),'-o',str(cls.probe)],
             capture_output=True, timeout=30)
        if result.returncode:
            cls.temp.cleanup()
            raise AssertionError(result.stderr.decode('utf-8','replace'))

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def run_probe(self, *args):
        return subprocess.run([str(self.probe),*map(str,args)], capture_output=True, timeout=15)

    def cycle(self, cap, steps, floats=0):
        p = self.run_probe('cycle',cap,steps,floats)
        self.assertEqual(p.returncode, 0, (p.stdout,p.stderr))
        self.assertEqual(p.stderr, b'')
        data = json.loads(p.stdout)
        self.assertEqual(data['released'], steps)
        self.assertEqual(data['growths'], steps)
        self.assertGreaterEqual(data['old_pages_confirmed_unmapped'], steps)
        self.assertEqual(data['uid'], os.getuid())
        return data

    def test_zero_capacity_header_mapping(self): self.cycle(0, 8)
    def test_one_capacity_multiple_growths(self): self.cycle(1, 12)
    def test_non_power_two_capacity(self): self.cycle(3, 8)
    def test_default_capacity(self): self.cycle(4, 10)
    def test_exact_page_allocation(self): self.cycle(510, 3)
    def test_page_boundary_plus_qword(self): self.cycle(511, 3)
    def test_multiple_mapping_pages(self): self.cycle(4097, 4)
    def test_raw_binary64_including_nan_payloads(self): self.cycle(4, 12, 1)
    def test_repeated_independent_processes(self):
        for _ in range(5): self.cycle(1, 8)
    def test_many_growths_release_old_pages(self): self.cycle(4, 16)
    def test_growth_guard_preserves_rax(self):
        self.assertEqual(self.run_probe('guard',4,4).stdout,b'guard-returned\n')
    def test_largest_safe_capacity(self):
        p=self.run_probe('guard',hex(((1<<63)-17)//16),hex(((1<<63)-17)//16))
        self.assertEqual(p.returncode,0)
    def test_capacity_overflow_rejected(self):
        v=(((1<<63)-17)//16)+1
        p=self.run_probe('guard',v,v)
        self.assertEqual((p.returncode,p.stdout,p.stderr),(1,b'',CAPACITY_ERROR))
    def test_corrupt_length_over_capacity_rejected(self):
        p=self.run_probe('guard',4,5)
        self.assertEqual((p.returncode,p.stderr),(1,CAPACITY_ERROR))
    def test_growth_on_nonfull_header_rejected(self):
        p=self.run_probe('guard',4,3)
        self.assertEqual((p.returncode,p.stderr),(1,CAPACITY_ERROR))
    def test_null_allocation_rejected(self):
        p=self.run_probe('allocation',0)
        self.assertEqual((p.returncode,p.stdout,p.stderr),(1,b'',ALLOC_ERROR))
    def test_linux_raw_error_returns_rejected(self):
        for n in (-1,-12,-22,-4095):
            p=self.run_probe('allocation',hex(n & ((1<<64)-1)))
            self.assertEqual((p.returncode,p.stdout,p.stderr),(1,b'',ALLOC_ERROR))
    def test_nonerror_return_passes_without_modification(self):
        p=self.run_probe('allocation','0x12345000')
        self.assertEqual((p.returncode,p.stdout,p.stderr),(0,b'allocation-returned\n',b''))
    def test_real_munmap_failure_is_not_silent(self):
        p=self.run_probe('release-fail')
        self.assertEqual((p.returncode,p.stdout,p.stderr),(1,b'',RECLAIM_ERROR))


