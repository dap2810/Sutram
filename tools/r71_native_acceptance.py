#!/usr/bin/env python3
"""Run proposed semantics/boundary cases against explicit, independently built compilers.
Does not compile the compiler, record goldens, execute rejected outputs or use a network.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, os, stat, struct, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('r71_prepare',ROOT/'tools/r71_prepare_review.py')
prep=importlib.util.module_from_spec(spec);spec.loader.exec_module(prep)
CASES=('associativity','evaluation_order','conversion')

def environment(extra=None):
 e={k:v for k,v in os.environ.items() if not k.upper().startswith('SUTRAM_')}
 if extra:e.update(extra)
 return e

def execute(args,cwd,env):
 return subprocess.run([str(v) for v in args],cwd=cwd,env=env,stdin=subprocess.DEVNULL,capture_output=True,timeout=12,check=False)

def build(compiler,source,output,cwd,env,lang=None):
 if os.path.lexists(output):raise ValueError('output already exists')
 command=[compiler]+(['--lang',lang] if lang else [])+[source,output]
 p=execute(command,cwd,env)
 if p.returncode!=0:raise AssertionError(f'compile exit={p.returncode}, stdout={p.stdout!r}, stderr={p.stderr!r}')
 if output.is_symlink() or not output.is_file() or output.stat().st_nlink!=1:raise AssertionError('missing or linked executable')
 b=output.read_bytes()
 if len(b)<64 or b[:7]!=b'\x7fELF\x02\x01\x01' or struct.unpack_from('<H',b,18)[0]!=62:raise AssertionError('not ELF64 AMD64')
 output.chmod(0o700)
 return p

def positive(compiler,source,expected,output,cwd,env,lang=None):
 build(compiler,source,output,cwd,env,lang)
 p=execute([output],cwd,env)
 if (p.returncode,p.stdout,p.stderr)!=(0,expected,b''):raise AssertionError(f'run exit={p.returncode}, actual={p.stdout!r}, expected={expected!r}, stderr={p.stderr!r}')
 return {'exit':p.returncode,'stdout_hex':p.stdout.hex(),'binary_sha256':hashlib.sha256(output.read_bytes()).hexdigest()}

def fixtures():
 result={}
 for n in CASES+('boundary_good',):
  result[n]={s:hashlib.sha256((ROOT/'examples/r71'/f'{n}.{s}').read_bytes()).hexdigest() for s in ('sm','out')}
 return result

def run(compiler,boundary):
 inputs=prep.verify(ROOT,prep.CORE_PINS)
 compiler=compiler.resolve(strict=True)
 if not compiler.is_file():raise ValueError('compiler must be a file')
 if boundary:
  boundary=boundary.resolve(strict=True)
  if os.path.samefile(compiler,boundary):raise ValueError('need distinct default and boundary compiler files')
  prep.reviewed_lock(ROOT)
  prep.verify(ROOT,prep.EXTENSION_PINS)
 results=[]
 def check(name,fn):
  try:results.append({'case':name,'status':'PASS',**fn()})
  except (OSError,ValueError,AssertionError,subprocess.TimeoutExpired) as e:results.append({'case':name,'status':'FAIL','detail':str(e)})
 with tempfile.TemporaryDirectory(prefix='sutram-r71-native-') as td:
  work=Path(td);env=environment();control=work/'control.sm';control.write_text('mukhya() { likha(42) }\n')
  # Failure of the positive control prevents attribution of generic tool failure
  # tak successful rejection of an invalid program.
  positive(compiler,control,b'42\n',work/'control.bin',ROOT,env)
  for n in CASES:
   check(n,lambda n=n:positive(compiler,ROOT/'examples/r71'/f'{n}.sm',(ROOT/'examples/r71'/f'{n}.out').read_bytes(),work/f'{n}.bin',ROOT,env))
  # Prove resolution with an isolated CWD and HOME, no user pack modifications.
  home=work/'home';fallback=home/'.local/share/sutram/lang';fallback.mkdir(parents=True)
  cwd=work/'resolution';local=cwd/'lang';local.mkdir(parents=True)
  src=cwd/'resolve.sm';src.write_text('shuru() { bol(42) }\n')
  (local/'probe.lang').write_text('shuru mukhya\nbol likha\n')
  (fallback/'probe.lang').write_text('shuru mukhya\nbol lkhb\n')
  penv=environment({'HOME':str(home)})
  check('pack_local_before_home',lambda:positive(compiler,src,b'42\n',work/'pack-local.bin',cwd,penv,'probe'))
  (local/'probe.lang').unlink()
  check('pack_home_fallback',lambda:positive(compiler,src,b'42',work/'pack-home.bin',cwd,penv,'probe'))
  (local/'cli.lang').write_text('shuru mukhya\nbol likha\n')
  (local/'environment.lang').write_text('shuru mukhya\nbol lkhb\n')
  check('cli_pack_before_environment',lambda:positive(compiler,src,b'42\n',work/'pack-cli.bin',cwd,environment({'HOME':str(home),'SUTRAM_LANG':'environment'}),'cli'))
  if boundary:
   positive(boundary,control,b'42\n',work/'boundary-control.bin',ROOT,env)
   check('boundary_positive',lambda:positive(boundary,ROOT/'examples/r71/boundary_good.sm',b'42\n',work/'boundary-good.bin',ROOT,env))
   def negative():
    src=ROOT/'examples/r71/boundary_bad.sm';out=work/'must-not-exist.bin'
    p=execute([boundary,src,out],ROOT,env)
    wanted=f'Sutram Error [E_UNSAFE_BOUNDARY]: {src}:3: unchecked operation requires asurakshit {{ ... }}\n'.encode()
    if p.returncode!=1 or p.stdout!=wanted or p.stderr!=b'' or os.path.lexists(out):raise AssertionError(f'bad rejection: exit={p.returncode}, stdout={p.stdout!r}, stderr={p.stderr!r}, output={os.path.lexists(out)}')
    return {'exit':p.returncode,'stdout_hex':p.stdout.hex(),'executable_created':False}
   check('boundary_negative',negative)
  else:results.append({'case':'boundary_profile','status':'NOT_RUN','detail':'provide --boundary-compiler'})
 return {'native_status':'FAIL' if any(x['status']=='FAIL' for x in results) else ('PARTIAL' if not boundary else 'PASS'),'compiler_executed':True,'compiler_sha256':hashlib.sha256(compiler.read_bytes()).hexdigest(),'boundary_compiler_sha256':hashlib.sha256(boundary.read_bytes()).hexdigest() if boundary else None,'source_pins':inputs,'results':results,'source_pin_is_build_provenance':False}

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--compiler',type=Path);p.add_argument('--boundary-compiler',type=Path);p.add_argument('--validate-only',action='store_true');p.add_argument('--report',type=Path);a=p.parse_args()
 try:
  if a.report and os.path.lexists(a.report):raise ValueError('report already exists')
  if a.validate_only:r={'native_status':'NOT_RUN','compiler_executed':False,'fixtures':fixtures(),'expectations':'candidate semantics pending native confirmation'}
  else:
   if not a.compiler:p.error('--compiler required')
   r=run(a.compiler,a.boundary_compiler)
  text=json.dumps(r,indent=2)+'\n'
  if a.report:
   with a.report.open('x') as f:f.write(text)
  print(text,end='');raise SystemExit(r['native_status']=='FAIL')
 except (OSError,ValueError,AssertionError,subprocess.SubprocessError) as e:p.exit(2,'R71_NATIVE_REFUSED: '+str(e)+'\n')
