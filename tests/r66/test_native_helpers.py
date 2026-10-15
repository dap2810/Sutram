"""Execute the exact helper instructions on Linux via GNU as, NOT NASM/Windows.

A deliberately limited syntax adapter handles only these two simple NASM files;
it does not translate the Sutram compiler. GCC supplies a Win64-ABI bridge for
the cluster helper. No network, new packages, Windows GUI or compiler execution.
"""
from __future__ import annotations
import ctypes as C
import mmap
import os
from pathlib import Path
import random
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


def to_gas(text: str) -> str:
    out = ['.intel_syntax noprefix']
    scope = None
    for raw in text.splitlines():
        line = raw.split(';', 1)[0].strip()
        if not line:
            continue
        if line in ('bits 64', 'default rel') or line.startswith('global '):
            continue
        if line.startswith('section '):
            section = line.split()[1]
            if section not in ('.text', '.data'):
                raise ValueError('unsupported section ' + section)
            out.append(section)
            continue
        if line.endswith(':'):
            name = line[:-1]
            if not name.startswith('.'):
                if not re.fullmatch(r'[a-zA-Z_][a-zA-Z_0-9]*', name):
                    raise ValueError('unsupported symbol')
                scope = name
                out.append('.globl ' + name)
            else:
                if scope is None:
                    raise ValueError('unscoped local label')
                name = scope + '__' + name[1:]
            out.append(name + ':')
            continue
        if line.startswith('db '):
            # Only literal ASCII string / numeric bytes occur in these helpers.
            items = next(__import__('csv').reader([line[3:]], skipinitialspace=True))
            values = []
            for item in items:
                try:
                    values.append(int(item, 0))
                except ValueError:
                    values.extend(item.encode('utf-8'))
            out.append('.byte ' + ','.join(str(v) for v in values))
            continue
        if line.startswith('%'):
            raise ValueError('macros/includes are not accepted by this narrow adapter')
        line = re.sub(r'\b(byte|word|dword|qword)\s+\[',
                      lambda m: m[1].upper() + ' PTR [', line)
        if re.search(r'(?<![\w])\.[A-Za-z_]', line):
            if scope is None:
                raise ValueError('unscoped local reference')
            line = re.sub(r'(?<![\w])\.([A-Za-z_][\w]*)',
                          lambda m: scope + '__' + m[1], line)
        out.append(line)
    out.append('.section .note.GNU-stack,"",@progbits')
    return '\n'.join(out) + '\n'


@unittest.skipUnless(shutil.which('gcc') and os.name == 'posix', 'GCC/Linux helper test only')
class NativeHelpers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='r66-helpers-')
        p = Path(cls.tmp.name)
        for name, src in [('lex', ROOT / 'src/r66_indic_lexer.inc'),
                          ('clusters', ROOT / 'windows/gui/r66_indic_clusters.asm')]:
            (p / (name + '.S')).write_text(to_gas(src.read_text('utf-8')))
        (p / 'bridge.S').write_text('''
.intel_syntax noprefix
.text
.globl test_digit
test_digit:
    push rbx
    mov rbx, rdx
    call r66_decimal_digit_at
    mov DWORD PTR [rbx], edx
    pop rbx
    ret
.section .note.GNU-stack,"",@progbits
''')
        (p / 'bridge.c').write_text('''
#include <stdint.h>
extern const unsigned char* __attribute__((ms_abi))
    r66_next_indic_cluster(const unsigned char*, const unsigned char*);
const unsigned char* test_cluster(const unsigned char* p, const unsigned char* end) {
    return r66_next_indic_cluster(p, end);
}
''')
        so = p / 'helpers.so'
        built = subprocess.run(['gcc', '-shared', '-fPIC', '-O2', '-Wall', '-Wextra',
                                '-Werror', '-o', str(so), str(p / 'lex.S'),
                                str(p / 'clusters.S'), str(p / 'bridge.S'), str(p / 'bridge.c')],
                               capture_output=True, timeout=30)
        if built.returncode:
            raise RuntimeError(built.stderr.decode())
        cls.lib = C.CDLL(str(so))
        cls.lib.test_digit.argtypes = [C.c_void_p, C.c_void_p, C.POINTER(C.c_uint)]
        cls.lib.test_digit.restype = C.c_int64
        for function in ('r66_is_danda_at', 'r66_indic_scalar_width'):
            fn = getattr(cls.lib, function)
            fn.argtypes = [C.c_void_p, C.c_void_p]
            fn.restype = C.c_uint64
        cls.lib.test_cluster.argtypes = [C.c_void_p, C.c_void_p]
        cls.lib.test_cluster.restype = C.c_void_p

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def digit(self, data: bytes):
        buf = C.create_string_buffer(data)
        p = C.addressof(buf)
        width = C.c_uint(100)
        value = self.lib.test_digit(p, p + len(data), C.byref(width))
        return value, width.value

    def simple(self, name, data):
        buf = C.create_string_buffer(data)
        p = C.addressof(buf)
        return getattr(self.lib, name)(p, p + len(data))

    def cluster_bytes(self, data):
        buf = C.create_string_buffer(data)
        start = C.addressof(buf)
        end = start + len(data)
        cur = start
        parts = []
        while cur < end:
            nxt = self.lib.test_cluster(cur, end)
            self.assertTrue(cur < nxt <= end, (data, cur - start, nxt - start))
            parts.append(data[cur - start:nxt - start])
            cur = nxt
        self.assertEqual(self.lib.test_cluster(end, end), end)
        return parts

    def expect_clusters(self, s, expected):
        self.assertEqual(self.cluster_bytes(s.encode()), [x.encode() for x in expected])

    def test_all_30_decimal_digits(self):
        for zero, width in ((48, 1), (0x0966, 3), (0x0AE6, 3)):
            for i in range(10):
                with self.subTest(zero=zero, digit=i):
                    self.assertEqual(self.digit(chr(zero + i).encode()), (i, width))

    def test_every_single_byte(self):
        for b in range(256):
            self.assertEqual(self.digit(bytes([b])), (b - 48, 1) if 48 <= b <= 57 else (-1, 0))

    def test_exhaustive_indic_second_third_bytes(self):
        for second in range(256):
            for third in range(256):
                data = bytes((0xE0, second, third))
                wanted = (third - 0xA6, 3) if second in (0xA5, 0xAB) and 0xA6 <= third <= 0xAF else (-1, 0)
                self.assertEqual(self.digit(data), wanted)

    def test_empty_and_truncated_digits(self):
        for data in (b'', b'\xe0', b'\xe0\xa5', b'\xe0\xab'):
            self.assertEqual(self.digit(data), (-1, 0))

    def test_abbreviation_not_digit_or_danda(self):
        for s in ('॰', '૰'):
            self.assertEqual(self.digit(s.encode()), (-1, 0))
            self.assertEqual(self.simple('r66_is_danda_at', s.encode()), 0)

    def test_shared_danda_and_scalar_validation(self):
        for s in ('।', '॥'):
            self.assertEqual(self.simple('r66_is_danda_at', s.encode()), 1)
        for s in ('क', 'ક', '०', '૦', '॰', '૰'):
            self.assertEqual(self.simple('r66_indic_scalar_width', s.encode()), 3)
        for data in (b'', b'\xe0', b'\xe0\xa5', b'\xe0\x9f\xbf', b'\xe0\xa5A', b'A'):
            self.assertEqual(self.simple('r66_indic_scalar_width', data), 0)

    def test_devanagari_matras_and_nukta(self):
        for s in ('कि', 'की', 'क़', 'क़ि', 'कं', 'कः', 'कुँ'):
            self.expect_clusters(s, [s])
        self.expect_clusters('किख', ['कि', 'ख'])

    def test_devanagari_conjuncts(self):
        for s in ('क्ष', 'स्त्र', 'क्\u200dष', 'क़्\u200dषि'):
            self.expect_clusters(s, [s])

    def test_zwnj_and_nonlinking_zwj(self):
        self.expect_clusters('क्\u200cष', ['क्\u200c', 'ष'])
        self.expect_clusters('क\u200dष', ['क\u200d', 'ष'])

    def test_gujarati_matras_and_conjuncts(self):
        for s in ('કિ', 'કી', 'કં', 'ક્ષ', 'સ્ત્ર', 'ક્\u200dષ'):
            self.expect_clusters(s, [s])
        self.expect_clusters('ક્\u200cષ', ['ક્\u200c', 'ષ'])

    def test_cross_script_link_not_joined(self):
        self.expect_clusters('क्ક', ['क्', 'ક'])
        self.expect_clusters('ક्क', ['ક', '्', 'क'])

    def test_signs_and_digits_separate_clusters(self):
        self.expect_clusters('०१२।॥॰', list('०१२।॥॰'))
        self.expect_clusters('૦૧૨૰', list('૦૧૨૰'))

    def test_ascii_controls_and_crlf(self):
        self.expect_clusters('a\r\nb\nc\td', ['a', '\r\n', 'b', '\n', 'c', '\t', 'd'])
        self.expect_clusters('\nि', ['\n', 'ि'])

    def test_utf8_scalar_widths(self):
        self.expect_clusters('Aé😀ક', ['A', 'é', '😀', 'ક'])
        self.expect_clusters('e\u0301', ['e\u0301'])

    def test_invalid_utf8_one_byte_progress(self):
        for data in (b'\x80', b'\xc0\xaf', b'\xed\xa0\x80', b'\xf4\x90\x80\x80',
                     b'\xe0', b'\xe0\xa4', b'\xf0\x9f\x98', b'\xff'):
            self.assertEqual(self.cluster_bytes(data), [bytes([x]) for x in data])

    def test_random_bytes_always_progress(self):
        rng = random.Random(66)
        for _ in range(1000):
            data = bytes(rng.randrange(256) for _ in range(rng.randrange(1, 40)))
            self.assertEqual(b''.join(self.cluster_bytes(data)), data)

    @unittest.skipUnless(os.name == 'posix', 'mprotect guard-page test')
    def test_exclusive_end_no_read_into_guard_page(self):
        # Last readable bytes are followed immediately by PROT_NONE.
        page = mmap.PAGESIZE
        region = mmap.mmap(-1, page * 2, prot=mmap.PROT_READ | mmap.PROT_WRITE)
        base = C.addressof(C.c_char.from_buffer(region))
        libc = C.CDLL(None)
        libc.mprotect.argtypes = [C.c_void_p, C.c_size_t, C.c_int]
        self.assertEqual(libc.mprotect(base + page, page, 0), 0)
        try:
            for data in (b'', b'\xe0', b'\xe0\xa5', b'\xe0\xab', b'\xf0\x9f\x98',
                         '૧'.encode(), '।'.encode(), 'क्'.encode()):
                p = base + page - len(data)
                if data:
                    C.memmove(p, data, len(data))
                w = C.c_uint()
                self.lib.test_digit(p, base + page, C.byref(w))
                self.lib.r66_is_danda_at(p, base + page)
                self.lib.r66_indic_scalar_width(p, base + page)
                nxt = self.lib.test_cluster(p, base + page)
                self.assertTrue(p <= nxt <= base + page)
        finally:
            libc.mprotect(base + page, page, mmap.PROT_READ | mmap.PROT_WRITE)
            region.close()

if __name__ == '__main__':
    unittest.main()
