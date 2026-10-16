"""Developer-tool tests; real temporary git apply, not full repository migration."""
import importlib.util,json,hashlib,subprocess,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
def load(n,path):
 s=importlib.util.spec_from_file_location(n,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
prep=load('prep',ROOT/'tools/r71_prepare_review.py')
docs=load('docs_mig',ROOT/'tools/r71_migrate_build_docs.py')
boot=load('boot_probe',ROOT/'boot/r71/build_probe.py')

class SourceTools(unittest.TestCase):
 def test_git_blob_reference_vector(self):self.assertEqual(prep.blob(b''),'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391')
 def test_production_extension_pins(self):
  lock=json.loads((ROOT/'tools/r71_source.lock.json').read_text());self.assertEqual(len(prep.verify(ROOT,lock['extension_pins'])),3)
 def test_source_drift_refused(self):
  with tempfile.TemporaryDirectory() as t:
   r=Path(t);(r/'x').write_bytes(b'wrong')
   with self.assertRaises(ValueError):prep.verify(r,{'x':prep.blob(b'right')})
 def test_missing_input_refused(self):
  with tempfile.TemporaryDirectory() as t:
   with self.assertRaises(ValueError):prep.verify(Path(t),{'missing':prep.blob(b'')})
 def test_symlink_input_refused(self):
  with tempfile.TemporaryDirectory() as t:
   r=Path(t);(r/'real').write_bytes(b'a');(r/'alias').symlink_to('real')
   with self.assertRaises(ValueError):prep.verify(r,{'alias':prep.blob(b'a')})
 def test_parent_path_refused(self):
  with self.assertRaises(ValueError):prep.regular(ROOT,'../outside')
 def test_empty_pins_refused(self):
  with self.assertRaises(ValueError):prep.verify(ROOT,{})
 def test_invalid_pin_refused(self):
  with self.assertRaises(ValueError):prep.verify(ROOT,{'src/r71_compiler_entry.asm':'not-a-hash'})
 def test_colon_path_refused(self):
  with self.assertRaises(ValueError):prep.regular(ROOT,'file:stream')
 def test_reviewed_lock_matches_embedded_pins(self):
  self.assertEqual(prep.reviewed_lock(ROOT)['extension_pins'],prep.EXTENSION_PINS)
 def reject_lock(self,change):
  with tempfile.TemporaryDirectory() as td:
   r=Path(td);(r/'tools').mkdir();lock=json.loads((ROOT/'tools/r71_source.lock.json').read_text());change(lock)
   (r/'tools/r71_source.lock.json').write_text(json.dumps(lock))
   with self.assertRaises(ValueError):prep.reviewed_lock(r)
 def test_core_override_in_extension_lock_refused(self):
  self.reject_lock(lambda lock:lock['extension_pins'].update({'src/sutram_compiler.asm':'0'*40}))
 def test_missing_extension_lock_refused(self):
  self.reject_lock(lambda lock:lock.update({'extension_pins':{}}))
 def test_wrong_lock_schema_refused(self):
  self.reject_lock(lambda lock:lock.update({'schema':2}))
 def test_existing_semantics_capture_hashes(self):
  record=json.loads((ROOT/'tests/r71/existing_semantics.json').read_text())
  self.assertFalse(record['native_rerun']);self.assertEqual(len(record['files']),4)
  for name,item in record['files'].items():
   with self.subTest(path=name):
    raw=item['text'].encode('utf-8');self.assertEqual(prep.blob(raw),item['git_blob']);self.assertEqual(hashlib.sha256(raw).hexdigest(),item['sha256'])
 def test_entry_preserves_diagnostics(self):
  s=(ROOT/'src/r71_compiler_entry.asm').read_text()
  self.assertIn('call r68_prelex_validate',s);self.assertIn('call r68_guard_value_start',s)
  self.assertIn('%ifdef SUTRAM_R71_UNSAFE_BOUNDARY\n        call r71_after_lex',s)
 def test_default_canonical_entry_unchanged(self):
  self.assertEqual(prep.blob((ROOT/'src/r68_compiler_entry.asm').read_bytes()),prep.CORE_PINS['src/r68_compiler_entry.asm'])
 def test_boot_image_size_and_signature(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'boot.bin';boot.build(p);b=p.read_bytes()+bytes(1474560-512)
   self.assertEqual(len(b),1474560);self.assertEqual(b[510:512],b'\x55\xaa');self.assertFalse(any(b[512:]))
 def test_boot_rebuild_exact(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'boot.bin';report=boot.build(p)
   self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),'3b2a5aea3cef45ecfb376cacc9dbced796a1b4f524ba0ea7f468f71987d35073')
   self.assertEqual(report['boot_execution'],'NOT_RUN')
 def test_boot_overwrite_refused(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'boot.bin';p.write_bytes(b'KEEP')
   with self.assertRaises(ValueError):boot.build(p)
   self.assertEqual(p.read_bytes(),b'KEEP')

class DocumentationMigration(unittest.TestCase):
 # This small pinned fixture isolates planner/apply behavior. It is not the
 # production R69 migration file or evidence of a whole-repository sweep.
 DRIVER=b'''from pathlib import Path
import re
def current_document(name):
 return Path(name).suffix=='.md' and not name.startswith('ChatGPT-to-')
def migrate(data):
 return b''.join(line.replace(b'src/sutram_compiler.asm',b'src/r68_compiler_entry.asm') if b'nasm' in line else line for line in data.splitlines(True))
'''
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.r=Path(self.t.name);(self.r/'tools').mkdir();(self.r/'tools/r69_build_doc_migration.py').write_bytes(self.DRIVER)
  (self.r/'README.md').write_text('nasm -f elf64 src/sutram_compiler.asm -o s.o\n')
  subprocess.run(['git','init','-q',str(self.r)],check=True);subprocess.run(['git','-C',str(self.r),'add','.'],check=True)
  self.patcher=patch.object(docs,'MIGRATOR_BLOB',prep.blob(self.DRIVER));self.patcher.start()
 def tearDown(self):self.patcher.stop();self.t.cleanup()
 def test_multiline_shell_command(self):
  data=b'nasm -f elf64 \\\n  src/sutram_compiler.asm -o s.o\n'
  self.assertIn(b'src/r68_compiler_entry.asm',docs.migrate_commands(data))
 def test_multiline_powershell_command(self):
  data=b'nasm.exe -f win64 `\n src\\sutram_compiler.asm -o s.obj\n'
  self.assertIn(b'src\\r68_compiler_entry.asm',docs.migrate_commands(data))
 def test_prose_source_reference_not_rewritten(self):
  data=b'Implementation and hash: src/sutram_compiler.asm\n'
  self.assertEqual(docs.migrate_commands(data),data)
 def test_windows_single_line_command(self):
  data=b'nasm.exe src\\sutram_compiler.asm -o s.obj\n'
  self.assertIn(b'src\\r68_compiler_entry.asm',docs.migrate_commands(data))
 def test_plan_does_not_edit(self):
  p=docs.plan(self.r);self.assertEqual(list(p['changes']),['README.md']);self.assertIn('src/sutram_compiler.asm',(self.r/'README.md').read_text())
 def test_plan_apply_and_verify(self):
  p=docs.plan(self.r);r=docs.apply(self.r,p);self.assertEqual(r['files_changed'],1);self.assertIn('src/r68_compiler_entry.asm',(self.r/'README.md').read_text());self.assertFalse(docs.plan(self.r)['changes'])
 def test_document_drift_refused(self):
  p=docs.plan(self.r);(self.r/'README.md').write_text('changed\n')
  with self.assertRaises(ValueError):docs.apply(self.r,p)
 def test_inventory_drift_refused(self):
  p=docs.plan(self.r);(self.r/'new.md').write_text('hello\n');subprocess.run(['git','-C',str(self.r),'add','new.md'],check=True)
  with self.assertRaises(ValueError):docs.apply(self.r,p)
 def test_migrator_drift_refused(self):
  (self.r/'tools/r69_build_doc_migration.py').write_bytes(self.DRIVER+b'\n# drift')
  with self.assertRaises(ValueError):docs.plan(self.r)
 def test_untracked_docs_not_claimed_migrated(self):
  (self.r/'untracked.md').write_text('nasm src/sutram_compiler.asm\n');self.assertNotIn('untracked.md',docs.plan(self.r)['scanned'])

if __name__=='__main__':unittest.main()
