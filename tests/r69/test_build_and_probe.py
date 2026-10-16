"""R69 unit contracts. Mock build responses are NOT native Sutram execution."""
from pathlib import Path
import hashlib, importlib.util, json, os, struct, subprocess, sys, tempfile, unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
import r69_build as b
import r69_pair_probe as q
import r69_build_doc_migration as d

def elf():
    raw=bytearray(128);raw[:7]=b'\x7fELF\x02\x01\x01';struct.pack_into('<HH',raw,16,2,62)
    return bytes(raw)
def pe():
    raw=bytearray(256);raw[:2]=b'MZ';struct.pack_into('<I',raw,60,128)
    raw[128:132]=b'PE\0\0';struct.pack_into('<H',raw,132,0x8664);struct.pack_into('<H',raw,152,0x20b)
    return bytes(raw)
class BuildTests(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()
    def test_git_blob(self):self.assertEqual(b.git_blob(b''),'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391')
    def test_verify_exact_input(self):
        (self.root/'x.asm').write_bytes(b'nop\n');r=b.verify_files(self.root,{'x.asm':b.git_blob(b'nop\n')})
        self.assertEqual(r['x.asm']['bytes'],4)
    def test_drift(self):
        (self.root/'x').write_bytes(b'bad')
        with self.assertRaises(ValueError):b.verify_files(self.root,{'x':b.git_blob(b'good')})
    def test_invalid_pin(self):
        with self.assertRaises(ValueError):b.verify_files(self.root,{'x':'0'*39})
    def test_empty_lock(self):
        with self.assertRaises(ValueError):b.verify_files(self.root,{})
    def test_paths_fail_closed(self):
        for n in ('../x','/x','a//b','a/./b','a\\b','C:x'):
            with self.subTest(n=n),self.assertRaises(ValueError):b.regular_input(self.root,n)
    def test_input_symlink(self):
        (self.root/'x').write_bytes(b'x');(self.root/'y').symlink_to(self.root/'x')
        with self.assertRaises(ValueError):b.regular_input(self.root,'y')
    def test_source_directory_symlink(self):
        (self.root/'a').mkdir();(self.root/'a'/'x').touch();(self.root/'z').symlink_to(self.root/'a')
        with self.assertRaises(ValueError):b.regular_input(self.root,'z/x')
    def test_linux_entry_default(self):
        cmd=b.build_commands(self.root,self.root/'a.o',self.root/'a','linux','default','nasm','ld')
        self.assertIn(str(self.root/b.ENTRY),cmd[0]);self.assertFalse(any('TRAP' in x for x in cmd[0]))
        self.assertNotIn(str(self.root/b.COMPILER),cmd[0])
    def test_windows_entry(self):
        c=b.build_commands(self.root,Path('a'),Path('b'),'windows','default','n','l')
        self.assertIn('-DWINDOWS=1',c[0]);self.assertIn('-mi386pep',c[1])
    def test_all_modes(self):
        for mode,flags in b.MODES.items():
            c=b.build_commands(self.root,Path('o'),Path('e'),'linux',mode,'n','l')[0]
            self.assertEqual([x[2:] for x in c if x.startswith('-DSUTRAM_')],list(flags))
    def test_unknown_mode(self):
        with self.assertRaises(ValueError):b.build_commands(self.root,Path('o'),Path('e'),'linux','oops','n','l')
    def test_environment(self):
        with patch.dict(os.environ,{'SUTRAM_LANG':'hindi','sutram_bad':'1','KEEP_ME':'yes'}):
            e=b.clean_environment();self.assertNotIn('SUTRAM_LANG',e);self.assertNotIn('sutram_bad',e);self.assertEqual(e['KEEP_ME'],'yes')
    def test_format(self):b.validate_image(elf(),'linux');b.validate_image(pe(),'windows')
    def test_format_rejects_wrong_target(self):
        for raw,target in [(elf(),'windows'),(pe(),'linux'),(b'', 'linux'),(b'MZ','windows')]:
            with self.subTest(target=target),self.assertRaises(ValueError):b.validate_image(raw,target)
    def test_pe_bounds(self):
        x=bytearray(pe());struct.pack_into('<I',x,60,0xffffffff)
        with self.assertRaises(ValueError):b.validate_image(bytes(x),'windows')
    def test_output_stale(self):
        p=self.root/'old';p.touch()
        with self.assertRaises(ValueError):b.refuse_output(p)
    def test_output_dangling(self):
        p=self.root/'old';p.symlink_to(self.root/'missing')
        with self.assertRaises(ValueError):b.refuse_output(p,True)
    def test_output_hardlink(self):
        p=self.root/'a';p.touch();os.link(p,self.root/'b')
        with self.assertRaises(ValueError):b.refuse_output(p,True)
    def test_output_parent_required(self):
        with self.assertRaises(ValueError):b.refuse_output(self.root/'missing'/'x')
    def test_mock_build_publishes_after_checks(self):
        inputs={b.COMPILER:{'git_blob':b.COMPILER_BLOB},b.ENTRY:{'git_blob':b.ENTRY_BLOB}}
        def run(cmd,**kw):
            if cmd[0]=='ld':Path(cmd[cmd.index('-o')+1]).write_bytes(elf())
            return subprocess.CompletedProcess(cmd,0,b'',b'')
        with patch.object(b,'verify_release',return_value=inputs),patch.object(b.subprocess,'run',side_effect=run):
            r=b.build(self.root,self.root/'built','linux','default','nasm','ld')
        self.assertEqual(r['runtime_execution'],'NOT_RUN');self.assertEqual((self.root/'built').read_bytes(),elf())
    def test_mock_failed_build_no_artifact(self):
        with patch.object(b,'verify_release',return_value={}),patch.object(b.subprocess,'run',return_value=subprocess.CompletedProcess([],1,b'',b'fail')):
            with self.assertRaises(RuntimeError):b.build(self.root,self.root/'bad','linux','default','nasm','ld')
        self.assertFalse((self.root/'bad').exists())
class ProbeTests(unittest.TestCase):
    def test_fixtures_derive46(self):self.assertEqual(q.fixture_contract(ROOT)[1],46)
    def data(self):
        r={}
        for m in ('default','reference','pairs'):
            for n in q.NAMES:r[m,n]=(b'X'*46+b'Z') if n=='all_registers' and m!='pairs' else b'Z'
        return r
    def test_comparison(self):
        r=q.compare_generated(self.data(),46);self.assertEqual(r['measured_removed_bytes'],46);self.assertIsNone(r['speedup'])
    def test_reference_drift(self):
        r=self.data();r['reference','all_registers']=b'bad'
        with self.assertRaises(ValueError):q.compare_generated(r,46)
    def test_nonmatching_changes(self):
        r=self.data();r['pairs','nonmatching']=b'bad'
        with self.assertRaises(ValueError):q.compare_generated(r,46)
    def test_wrong_delta(self):
        with self.assertRaises(ValueError):q.compare_generated(self.data(),45)
    def test_no_pairs_changed(self):
        r=self.data();r['pairs','no_pairs']=b'bad'
        with self.assertRaises(ValueError):q.compare_generated(r,46)
    def test_control_is_never_executed_branch(self):
        s=(ROOT/'tools/r69_pair_probe.py').read_text();self.assertIn("if name == 'nonmatching':",s);self.assertIn('NOT_RUN_RAW_ASM_CONTROL',s)
class DocsAndWindows(unittest.TestCase):
    def test_migration_only_build_lines(self):
        x=b'nasm -f elf64 src/sutram_compiler.asm\nCore: src/sutram_compiler.asm\n'
        self.assertEqual(d.migrate(x),b'nasm -f elf64 src/r68_compiler_entry.asm\nCore: src/sutram_compiler.asm\n')
    def test_migration_backslash(self):self.assertIn(b'r68_compiler_entry',d.migrate(b'nasm.exe -f win64 src\\sutram_compiler.asm\n'))
    def test_migration_idempotent(self):
        x=d.migrate(b'nasm src/sutram_compiler.asm\n');self.assertEqual(d.migrate(x),x)
    def test_history_exclusion(self):
        for n in ('docs/CHANGELOG.md','ChatGPT-to-Sarvam/ROUND-69-HANDOFF.md','docs/R65-SOURCE-REVIEW.md'):self.assertFalse(d.current_document(n))
        for n in ('README.md','PROJECT-MASTER.md','docs/WINDOWS-SETUP.md'):self.assertTrue(d.current_document(n))
    def test_cmd_no_policy_override(self):self.assertNotIn('ExecutionPolicy',(ROOT/'windows/BUILD-WINDOWS-SETUP.cmd').read_text())
    def test_wrappers_actual_paths(self):
        s=(ROOT/'windows/build-windows-setup.ps1').read_text();self.assertIn('native-installer\\build-installer.ps1',s);self.assertNotIn('windows-installer-native',s)
    def test_wrappers_no_bypass(self):
        for n in ('build-windows-setup.ps1','build-windows-native.ps1','r69-build-common.ps1'):
            s=(ROOT/'windows'/n).read_text();self.assertNotIn('-ExecutionPolicy',s);self.assertNotIn('Set-ExecutionPolicy',s)
    def test_native_diagnostics_gate(self):
        s=(ROOT/'windows/build-windows-native.ps1').read_text();self.assertIn('E_UTF8',s);self.assertIn('r68_compiler_entry.asm',s)
    def test_staged_payload_hash_gate(self):
        s=(ROOT/'windows/build-windows-setup.ps1').read_text();self.assertIn('bin\\sutram.exe',s);self.assertIn('win\\sutram.exe',s);self.assertIn('Installer staged a different',s)
    def test_malayalam_named_gap(self):
        s=(ROOT/'docs/INDIC-COVERAGE.md').read_text();self.assertIn('Malayalam',s);self.assertIn('Not implemented',s)
if __name__=='__main__':unittest.main()
