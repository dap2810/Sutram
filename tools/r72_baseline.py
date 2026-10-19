#!/usr/bin/env python3
"""R72: exact source/commit gate and reproducible build; no downloads/CI."""
import argparse, hashlib, json, pathlib, subprocess, tempfile
def git(root,*args):
 return subprocess.run(['git','-C',str(root),*args],capture_output=True,text=True,check=True,timeout=30).stdout.strip()
def blob(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def verify(root,manifest):
 assert git(root,'rev-parse','HEAD')==manifest['commit'],'commit drift'
 assert git(root,'status','--porcelain')=='','dirty checkout'
 for name,expected in manifest['pins'].items():
  p=pathlib.PurePosixPath(name)
  assert not p.is_absolute() and '..' not in p.parts,'unsafe input path'
  path=root/name
  assert path.is_file() and not path.is_symlink(),'missing/symlink: '+name
  assert blob(path.read_bytes())==expected,'blob mismatch: '+name
 return True
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--repo',type=pathlib.Path,required=True)
 ap.add_argument('--manifest',type=pathlib.Path,required=True)
 ap.add_argument('--verify-only',action='store_true')
 ap.add_argument('--output',type=pathlib.Path)
 args=ap.parse_args()
 m=json.loads(args.manifest.read_text('utf8'))
 try:
  verify(args.repo,m)
  if args.verify_only:print(json.dumps({'source':'PASS','build':'NOT_RUN'}));return 0
  if not args.output:raise ValueError('output required')
  if args.output.exists() or args.output.is_symlink():raise ValueError('output exists')
  with tempfile.TemporaryDirectory(prefix='r72-') as d:
   obj=pathlib.Path(d)/'c.o';exe=pathlib.Path(d)/'compiler'
   for cmd in [['nasm','-f','elf64','-I'+str(args.repo)+'/','src/r68_compiler_entry.asm','-o',str(obj)],['ld','-o',str(exe),str(obj)]]:
    p=subprocess.run(cmd,cwd=args.repo,capture_output=True,timeout=120)
    if p.returncode:raise RuntimeError(f'{cmd[0]} exit {p.returncode}: '+p.stderr.decode(errors='replace'))
   data=exe.read_bytes()
   if not data.startswith(b'\x7fELF'):raise RuntimeError('invalid ELF header')
   args.output.write_bytes(data)
   print(json.dumps({'source':'PASS','build':'PASS','binary_sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}))
  return 0
 except (AssertionError,ValueError,OSError,RuntimeError,subprocess.TimeoutExpired) as e:
  print(json.dumps({'status':'FAIL','reason':str(e)}));return 2
if __name__=='__main__':raise SystemExit(main())
