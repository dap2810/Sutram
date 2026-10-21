"""Executable offline artifact tests; fixture PEs are not Windows runtime evidence."""
import hashlib
import importlib.util
import io
import json
import pathlib
import struct
import tempfile
import unittest
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('r80', ROOT/'tools/r80_payload_verify.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def pe(data=b'', symbols=False):
    """Construct bounded PE32+ fixture with real COFF section/symbol layout."""
    body = data + (hashlib.sha256(data).digest() if symbols else b'')
    raw_size = max(512, (len(body) + 511) & ~511)
    image = bytearray(512 + raw_size)
    image[:2] = b'MZ'
    struct.pack_into('<I', image, 60, 64)
    image[64:68] = b'PE\0\0'
    struct.pack_into('<HH', image, 68, 0x8664, 1)
    struct.pack_into('<H', image, 84, 240)
    struct.pack_into('<H', image, 88, 0x20b)
    image[328:333] = b'.data'
    struct.pack_into('<IIII', image, 336, len(body), 4096, raw_size, 512)
    image[512:512+len(body)] = body
    if symbols:
        table = bytearray()
        strings = bytearray(4)
        for name, value in (('blob_payload', 0), ('blob_payload_end', len(data)), ('hash_payload', len(data))):
            index = len(strings)
            strings += name.encode() + b'\0'
            table += struct.pack('<IIIhHBB', 0, index, value, 1, 0, 3, 0)
        struct.pack_into('<I', strings, 0, len(strings))
        struct.pack_into('<II', image, 76, len(image), 3)
        image += table + strings
    return bytes(image)


class PayloadChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        (self.root/'tools').mkdir()
        (self.root/'src').mkdir()
        self.core = self.root/m.CORE
        self.core.write_text('; same v182 banner even when code changes\n')
        (self.root/m.ENTRY).write_text('%include "src/sutram_compiler.asm"\n')
        pins = {n: m.blob((self.root/n).read_bytes()) for n in (m.CORE, m.ENTRY)}
        self.lock = self.root/'tools/r69_build.lock.json'
        self.lock.write_text(json.dumps({'schema': 1, 'entry': m.ENTRY, 'pins': pins}))
        self.compiler = self.root/'compiler.exe'
        self.compiler.write_bytes(pe(b'Sutram 1.0 (v182) new compiler'))
        self.report = self.root/'build.json'
        self.refresh_report()
        self.payload = self.root/'payload.zip'
        self.setup = self.root/'setup.exe'
        self.pack()

    def tearDown(self):
        self.tmp.cleanup()

    def refresh_report(self):
        inputs = m.source_inputs(self.root)
        inputs.pop('tools/r69_build.lock.json')
        self.report.write_text(json.dumps({'status': 'BUILT_FORMAT_CHECKED', 'target': 'windows',
            'mode': 'default', 'entry': m.ENTRY, 'inputs': inputs,
            'binary_sha256': m.sha(self.compiler.read_bytes())}))

    def pack(self, override=None, extra=None, omit=(), manifest_override=None):
        files = {'bin/sutram.exe': self.compiler.read_bytes(), 'win/sutram.exe': self.compiler.read_bytes(),
                 'lang/hindi.sandesh': 'अज्ञात नाम'.encode('utf-8')}
        files.update(override or {})
        for name in omit:
            files.pop(name)
        rows = [m.sha(content) + ' *' + name.replace('/', '\\') for name, content in files.items()]
        files['payload.manifest.sha256'] = (manifest_override if manifest_override is not None
                                            else ('\n'.join(rows) + '\n').encode())
        files.update(extra or {})
        with zipfile.ZipFile(self.payload, 'w', zipfile.ZIP_DEFLATED) as z:
            for name, content in files.items():
                z.writestr(name, content)
        self.setup.write_bytes(pe(self.payload.read_bytes(), True))

    def check(self, embedded=True):
        return m.verify(self.root, self.compiler, self.report, self.payload, self.setup if embedded else None)

    def test_matching_current_inputs_zip_and_pe_pass(self):
        out = self.check()
        self.assertEqual(out['status'], 'PASS')
        self.assertEqual(out['native_windows_acceptance'], 'NOT_RUN')
        self.assertEqual(out['payload_sha256'], m.sha(self.payload.read_bytes()))
        self.assertEqual(out['embedded_payload']['offset'], 512)
        self.assertEqual(out['installer_sha256'], m.sha(self.setup.read_bytes()))

    def test_preassembly_mode_does_not_claim_setup_hash(self):
        self.assertIsNone(self.check(False)['installer_sha256'])

    def test_same_version_different_compiler_payload_is_rejected(self):
        self.pack({'bin/sutram.exe': pe(b'Sutram 1.0 (v182) OLD compiler')})
        with self.assertRaisesRegex(ValueError, 'stale payload compiler'):
            self.check()

    def test_second_compiler_copy_is_also_checked(self):
        self.pack({'win/sutram.exe': pe(b'Sutram 1.0 (v182) OLD compiler')})
        with self.assertRaisesRegex(ValueError, 'stale payload compiler'):
            self.check()

    def test_source_change_is_rejected(self):
        self.core.write_text('; changed code, banner unchanged\n')
        with self.assertRaisesRegex(ValueError, 'source drift'):
            self.check()

    def test_report_for_previous_source_rejected_even_after_reviewed_repin(self):
        self.core.write_text('; legitimate new source\n')
        lock = json.loads(self.lock.read_text())
        lock['pins'][m.CORE] = m.blob(self.core.read_bytes())
        self.lock.write_text(json.dumps(lock))
        with self.assertRaisesRegex(ValueError, 'build report'):
            self.check()

    def test_build_report_compiler_hash_cannot_be_wrong(self):
        report = json.loads(self.report.read_text()); report['binary_sha256'] = '0'*64
        self.report.write_text(json.dumps(report))
        with self.assertRaisesRegex(ValueError, 'build report'):
            self.check()

    def test_unlocked_include_is_rejected(self):
        self.core.write_text('%include "src/not-locked.inc"\n')
        lock = json.loads(self.lock.read_text()); lock['pins'][m.CORE] = m.blob(self.core.read_bytes())
        self.lock.write_text(json.dumps(lock))
        with self.assertRaisesRegex(ValueError, 'unlocked'):
            self.check()

    def test_unmanifested_file_is_rejected(self):
        self.pack(extra={'surprise.txt': b'extra'})
        with self.assertRaisesRegex(ValueError, 'file sets differ'):
            self.check()

    def test_manifest_hash_corruption_is_rejected(self):
        with zipfile.ZipFile(self.payload) as z:
            manifest = z.read('payload.manifest.sha256')
        self.pack(manifest_override=b'0'*64 + manifest[64:])
        with self.assertRaisesRegex(ValueError, 'manifest hash mismatch'):
            self.check()

    def test_missing_compiler_copy_is_rejected(self):
        self.pack(omit=('win/sutram.exe',))
        with self.assertRaisesRegex(ValueError, 'both payload compiler'):
            self.check()

    def test_case_collisions_rejected(self):
        self.pack(extra={'BIN/SUTRAM.EXE': self.compiler.read_bytes()})
        with self.assertRaisesRegex(ValueError, 'case-colliding'):
            self.check()

    def test_zip_traversal_does_not_extract(self):
        self.pack(extra={'../escape.txt': b'unsafe'})
        with self.assertRaisesRegex(ValueError, 'unsafe'):
            self.check()
        self.assertFalse((self.root.parent/'escape.txt').exists())

    def test_windows_path_hazards(self):
        for name in ('C:/file', '/file', 'x:stream', 'a/../b', 'a/./b', 'a//b', 'a.', 'a ', 'CON.txt', 'a/COM1'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                m.normalized(name)

    def test_symlink_source_rejected(self):
        data = self.core.read_bytes(); self.core.unlink()
        target = self.root/'other.asm'; target.write_bytes(data)
        self.core.symlink_to(target)
        with self.assertRaisesRegex(ValueError, 'symlink'):
            self.check()

    def test_old_installer_with_new_zip_appended_is_rejected(self):
        self.setup.write_bytes(pe(b'old embedded archive', True) + self.payload.read_bytes())
        with self.assertRaisesRegex(ValueError, 'embedded payload span'):
            self.check()

    def test_wrong_embedded_hash_rejected(self):
        content = bytearray(self.setup.read_bytes())
        content[512 + len(self.payload.read_bytes())] ^= 1
        self.setup.write_bytes(content)
        with self.assertRaisesRegex(ValueError, 'hash constant'):
            self.check()

    def test_corrupt_embedded_zip_rejected(self):
        content = bytearray(self.setup.read_bytes()); content[530] ^= 1
        self.setup.write_bytes(content)
        with self.assertRaisesRegex(ValueError, 'payload bytes'):
            self.check()

    def test_stripped_pe_is_not_silently_accepted(self):
        self.setup.write_bytes(pe(self.payload.read_bytes()))
        with self.assertRaisesRegex(ValueError, 'COFF symbols'):
            self.check()

    def test_linux_binary_does_not_count_as_windows_compiler(self):
        self.compiler.write_bytes(b'\x7fELF' + b'\0'*100)
        with self.assertRaisesRegex(ValueError, 'not a PE'):
            self.check()

    def test_file_cannot_also_be_parent_directory(self):
        self.pack(extra={'bin': b'not a directory'})
        with self.assertRaisesRegex(ValueError, 'path conflict'):
            self.check()

    def test_zip_symlink_rejected_without_extraction(self):
        with zipfile.ZipFile(self.payload, 'a') as z:
            info = zipfile.ZipInfo('symlink')
            info.create_system = 3
            info.external_attr = 0o120777 << 16
            z.writestr(info, '/outside')
        with self.assertRaisesRegex(ValueError, 'nonregular'):
            self.check()

    def test_zip_bomb_budget(self):
        from unittest.mock import patch
        self.pack(override={'oversized.txt': b'x'*9000})
        with patch.object(m, 'MAX_FILE', 2048), self.assertRaisesRegex(ValueError, 'oversized ZIP'):
            self.check()

    def test_new_diagnostic_include_pin_is_supported(self):
        data = b'; diagnostics include\n'
        (self.root/'src/r11_sandesh.inc').write_bytes(data)
        lock = json.loads(self.lock.read_text())
        lock['pins']['src/r11_sandesh.inc'] = m.blob(data)
        self.lock.write_text(json.dumps(lock))
        self.refresh_report()
        result = self.check()
        self.assertEqual(len(result['source_inputs']), 3)
        self.assertIn('src/r11_sandesh.inc', result['source_inputs'])

    def test_actual_gnu_linked_pe_symbol_layout(self):
        import shutil
        import subprocess
        if not all(shutil.which(x) for x in ('as', 'objcopy', 'ld')):
            self.skipTest('GNU binutils unavailable')
        body = self.payload.read_bytes()
        assembly = ('.text\n.global _start\n_start:\n ret\n.data\nblob_payload:\n'
                    ' .incbin "payload.zip"\nblob_payload_end:\nhash_payload:\n .byte ' +
                    ','.join(str(x) for x in hashlib.sha256(body).digest()) + '\n')
        (self.root/'fixture.s').write_text(assembly)
        for command in (['as', '--64', 'fixture.s', '-o', 'elf.o'],
                        ['objcopy', '-O', 'pe-x86-64', 'elf.o', 'fixture.obj'],
                        ['ld', '-mi386pep', '--entry=_start', '--subsystem', 'windows',
                         '-o', str(self.setup), 'fixture.obj']):
            process = subprocess.run(command, cwd=self.root, capture_output=True, text=True, timeout=10)
            self.assertEqual(process.returncode, 0, process.stderr)
        result = self.check()
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['embedded_payload']['sha256'], m.sha(body))

    def test_source_and_outputs_unchanged_by_verifier(self):
        before = {p: p.read_bytes() for p in (self.core, self.compiler, self.payload, self.setup, self.report)}
        self.check()
        self.assertEqual(before, {p: p.read_bytes() for p in before})


if __name__ == '__main__':
    unittest.main()
