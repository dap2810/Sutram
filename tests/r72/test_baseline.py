import importlib.util,pathlib,tempfile,subprocess,unittest
P=pathlib.Path(__file__).resolve().parents[2]/'tools'/'r72_baseline.py'
s=importlib.util.spec_from_file_location('r72',P);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class TestBaseline(unittest.TestCase):
 def test_blob(self):self.assertEqual(m.blob(b'hello\n'),'ce013625030ba8dba906f756967f9e9ca394464a')
 def test_commit_and_drift(self):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d);subprocess.run(['git','init','-q',str(root)],check=True)
   subprocess.run(['git','-C',str(root),'config','user.name','Test'],check=True)
   subprocess.run(['git','-C',str(root),'config','user.email','test@example.invalid'],check=True)
   (root/'a.asm').write_text('hello\n')
   subprocess.run(['git','-C',str(root),'add','.'],check=True)
   subprocess.run(['git','-C',str(root),'commit','-qm','test'],check=True)
   manifest={'commit':m.git(root,'rev-parse','HEAD'),'pins':{'a.asm':m.blob(b'hello\n')}}
   self.assertTrue(m.verify(root,manifest))
   (root/'a.asm').write_text('changed\n')
   with self.assertRaises(AssertionError):m.verify(root,manifest)
 def test_path_traversal(self):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d);subprocess.run(['git','init','-q',str(root)],check=True)
   subprocess.run(['git','-C',str(root),'config','user.name','Test'],check=True)
   subprocess.run(['git','-C',str(root),'config','user.email','test@example.invalid'],check=True)
   (root/'a').write_text('x')
   subprocess.run(['git','-C',str(root),'add','.'],check=True)
   subprocess.run(['git','-C',str(root),'commit','-qm','test'],check=True)
   with self.assertRaises(AssertionError):m.verify(root,{'commit':m.git(root,'rev-parse','HEAD'),'pins':{'../a':'0'*40}})
if __name__=='__main__':unittest.main()
