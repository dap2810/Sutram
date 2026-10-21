import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('r76_modules',ROOT/'tools/r76_module_object_probe.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class ObjectProbe(unittest.TestCase):
    def test_et_rel_vs_et_exec(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'o';header=bytearray(64);header[:7]=b'\x7fELF\x02\x01\x01'
            struct.pack_into('<H',header,18,62)
            for code,want in ((1,'ET_REL'),(2,'ET_EXEC'),(3,'ET_DYN')):
                struct.pack_into('<H',header,16,code);f.write_bytes(header)
                self.assertEqual(m.kind(f),want)
    def test_missing_not_object(self):
        self.assertEqual(m.kind(Path('/definitely/not-existing/r76.bin')),'MISSING')
    def test_refuse_same_fixture(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'fixture.sm';p.write_text('dummy')
            with self.assertRaisesRegex(ValueError,'independent'):
                m.probe(p,p,p)
    def test_existing_elf_exec_does_not_count_as_module(self):
        import shutil
        binary=shutil.which('true')
        if binary:
            self.assertNotEqual(m.kind(Path(binary)),'ET_REL')

if __name__=='__main__':unittest.main()
