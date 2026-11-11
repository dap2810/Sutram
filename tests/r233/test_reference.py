"""Executable checks for the R233 reference corrections (Linux)."""
from pathlib import Path
import os
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
COMPILER = os.environ.get('SUTRAM_COMPILER', str(ROOT / 'sutram_compiler'))


class ReferenceTests(unittest.TestCase):
    def check_program(self, body, expected):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            (p / 'input.txt').write_bytes(b'ABC')
            (p / 'test.sm').write_text('mukhya() {\n' + body + '\n}\n')
            c = subprocess.run([COMPILER, str(p / 'test.sm'), str(p / 'test.bin')],
                               cwd=ROOT, capture_output=True, timeout=30)
            self.assertEqual(c.returncode, 0, c.stdout + c.stderr)
            r = subprocess.run([str(p / 'test.bin')], cwd=p, capture_output=True, timeout=5)
            self.assertEqual((r.returncode, r.stdout, r.stderr), (0, expected, b''))

    def test_qword_memory(self):
        self.check_program('vitti p = nirmmita(16)\nlikh8(p, 9223372036854775807)\nlikha(pad8(p))', b'9223372036854775807\n')

    def test_conditional_access_is_memory_and_start_address_only(self):
        self.check_program('vitti p = nirmmita(16)\nlikh8c(p, 123456789, p + 1)\nlikha(pad8c(p, p + 1))\nlikh8c(p, 7, p)\nlikha(pad8(p))\nlikha(pad8c(p, p))', b'123456789\n123456789\n0\n')

    def test_indexed_byte(self):
        self.check_program('likha(aksharank("AB", 1))\nlikha(aksharank("AB"))', b'66\n65\n')

    def test_equality_not_ordering(self):
        self.check_program('likha(vartani_tul("a", "a"))\nlikha(vartani_tul("a", "b"))\nlikha(vartani_tul("b", "a"))', b'0\n1\n1\n')

    def test_open_read_short_read_and_eof(self):
        self.check_program('vitti fd = dvaram("input.txt", 0)\nvitti p = nirmmita(16)\nlikha(fd >= 0)\nlikha(paadh(fd, p, 8))\nlikha(aksharank(p))\nlikha(paadh(fd, p, 8))\nband(fd)', b'1\n3\n65\n0\n')

    def test_open_failure_is_negative(self):
        self.check_program('likha(dvaram("missing-file", 0) < 0)', b'1\n')


if __name__ == '__main__':
    unittest.main()
