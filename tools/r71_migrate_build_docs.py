#!/usr/bin/env python3
"""Complete R69's tracked-document migration, with a reviewed two-step plan/apply.
This tool changes current build instructions only. Historical handoffs stay historical.
The plan pins every scanned tracked document; --apply-plan refuses any intervening drift.
"""
from __future__ import annotations
import argparse, difflib, hashlib, importlib.util, json, os, re, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MIGRATOR_BLOB='4c40666f85e8ab87bbe073708ab2d2635a3a50cb'

def module(root):
 path=safe_file(root,'tools/r69_build_doc_migration.py')
 data=path.read_bytes()
 actual=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
 if actual!=MIGRATOR_BLOB:raise ValueError('R69 migration-tool drift')
 spec=importlib.util.spec_from_file_location('r69_migration',root/'tools/r69_build_doc_migration.py')
 if not spec or not spec.loader:raise ValueError('Round 69 migration tool missing')
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def digest(data):return hashlib.sha256(data).hexdigest()

def migrate_commands(data):
 text=data.decode('utf-8');out=[];continuation=False
 for line in text.splitlines(keepends=True):
  active=continuation or bool(re.search(r'(?i)\bnasm(?:\.exe)?\b',line))
  if active:
   line=line.replace('src/sutram_compiler.asm','src/r68_compiler_entry.asm')
   line=line.replace('src\\sutram_compiler.asm','src\\r68_compiler_entry.asm')
  continuation=active and line.rstrip().endswith(('\\','`'))
  out.append(line)
 return ''.join(out).encode('utf-8')


def safe_file(root,name):
 path=root/name
 if any((root/Path(*Path(name).parts[:i])).is_symlink() for i in range(1,len(Path(name).parts)+1)):raise ValueError('symlink document '+name)
 if not path.is_file() or path.stat().st_nlink!=1:raise ValueError('nonregular or hardlinked document '+name)
 return path

def plan(root):
 m=module(root)
 # Use current tracked documents, not just files known in the older R69 snapshot.
 proc=subprocess.run(['git','-C',str(root),'ls-files','-z'],capture_output=True,timeout=30,check=True)
 files=proc.stdout.decode().split('\0');scanned={};changes={}
 for name in files:
  if not name or not m.current_document(name):continue
  data=safe_file(root,name).read_bytes()
  try:after=migrate_commands(data)
  except UnicodeDecodeError:continue
  scanned[name]=digest(data)
  if after!=data:changes[name]={'before':digest(data),'after':digest(after),'text':after.decode()}
 return {'schema':1,'scanned':scanned,'changes':changes,'native_status':'NOT_RUN'}

def apply(root,record):
 if record.get('schema')!=1:raise ValueError('unrecognized plan')
 current=plan(root)
 if current!=record:raise ValueError('document inventory/content or transformation drift')
 patch=[]
 for name,item in record['changes'].items():
  before=safe_file(root,name).read_bytes().decode('utf-8');after=item['text']
  patch.extend(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+name,tofile='b/'+name))
 if patch:
  data=''.join(patch).encode()
  subprocess.run(['git','-C',str(root),'apply','--check','-'],input=data,capture_output=True,timeout=30,check=True)
  subprocess.run(['git','-C',str(root),'apply','-'],input=data,capture_output=True,timeout=30,check=True)
 after=plan(root)
 if after['changes']:raise ValueError('migration remains incomplete')
 return {'status':'CURRENT_BUILD_DOCS_MIGRATED','files_changed':len(record['changes']),'documents_scanned':len(after['scanned']),'native_status':'NOT_RUN'}

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 g=p.add_mutually_exclusive_group(required=True);g.add_argument('--plan',type=Path);g.add_argument('--apply-plan',type=Path);g.add_argument('--check',action='store_true')
 a=p.parse_args()
 try:
  if a.plan:
   r=plan(ROOT)
   with a.plan.open('x') as f:json.dump(r,f,indent=2)
   print(json.dumps({'status':'PLAN_WRITTEN','changes':list(r['changes']),'scanned':len(r['scanned'])}))
  elif a.apply_plan:print(json.dumps(apply(ROOT,json.loads(a.apply_plan.read_text())),indent=2))
  else:
   r=plan(ROOT);print(json.dumps({'remaining':list(r['changes']),'scanned':len(r['scanned'])},indent=2));raise SystemExit(bool(r['changes']))
 except (OSError,ValueError,subprocess.SubprocessError) as e:p.exit(2,'R71_DOC_MIGRATION_REFUSED: '+str(e)+'\n')
