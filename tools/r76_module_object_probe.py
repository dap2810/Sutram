#!/usr/bin/env python3
"""Smallest honest two-.sm native object/link probe: capture real failure point.

Existing Sutram compiler is the ONLY language frontend. No Python code emitter.
Success needs independently compiled ET_REL objects, an actual link, and stdout=42.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import os
import struct
import subprocess
import tempfile


def kind(path: Path):
    if not path.is_file() or path.is_symlink(): return 'MISSING'
    raw=path.read_bytes()
    if len(raw)<64 or raw[:7]!=b'\x7fELF\x02\x01\x01':return 'NOT_ELF64'
    e_type=struct.unpack_from('<H',raw,16)[0]
    machine=struct.unpack_from('<H',raw,18)[0]
    if machine!=62:return f'WRONG_ARCH_{machine}'
    return {1:'ET_REL',2:'ET_EXEC',3:'ET_DYN'}.get(e_type,'UNKNOWN_'+str(e_type))


def invoke(argv,timeout):
    r=subprocess.run([str(x) for x in argv],capture_output=True,
                     stdin=subprocess.DEVNULL,timeout=timeout,check=False)
    return {'command':[str(x) for x in argv],'exit':r.returncode,
            'stdout':r.stdout.decode('utf8','replace')[-4000:],
            'stderr':r.stderr.decode('utf8','replace')[-4000:]}


def probe(compiler:Path, helper:Path, main:Path, ld:str='ld',timeout=30):
    if not compiler.is_file() or not helper.is_file() or not main.is_file():
        raise ValueError('missing compiler or fixture')
    if helper.resolve()==main.resolve():raise ValueError('fixtures must be independent')
    compiled={'sha256':hashlib.sha256(compiler.read_bytes()).hexdigest()}
    with tempfile.TemporaryDirectory(prefix='sutram-r76-modules-') as d:
        d=Path(d);objects=[];steps=[]
        for path in (helper,main):
            o=d/(path.stem+'.o')
            step=invoke([compiler,path,o],timeout)
            step['object_kind']=kind(o)
            if o.is_file():step['output_sha256']=hashlib.sha256(o.read_bytes()).hexdigest()
            steps.append(step);objects.append(o)
            if step['exit'] or step['object_kind']!='ET_REL':
                return {'status':'FAIL','reason':('compiler returned nonzero' if step['exit'] else
                        'compiler did not produce relocatable ET_REL object'),
                        'compiler':compiled,'steps':steps,'link':'NOT_RUN'}
        executable=d/'linked.elf'
        link=invoke([ld,'-o',executable,*objects],timeout)
        link['output_kind']=kind(executable)
        if link['exit'] or not executable.is_file():
            return {'status':'FAIL','reason':'native linker rejected two objects',
                    'compiler':compiled,'steps':steps,'link':link}
        executable.chmod(0o700)
        run=invoke([executable],timeout)
        return {'status':'PASS' if run['exit']==0 and run['stdout']=='42\n' else 'FAIL',
                'compiler':compiled,'steps':steps,'link':link,'run':run,
                'expected_stdout':'42\n'}


def main_cli():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('--compiler',type=Path,required=True)
    a.add_argument('--helper',type=Path,default=Path('examples/r76/module_helper.sm'))
    a.add_argument('--main',type=Path,default=Path('examples/r76/module_main.sm'))
    a.add_argument('--ld',default='ld')
    a.add_argument('--report',type=Path)
    opts=a.parse_args()
    try:
        result=probe(opts.compiler.resolve(),opts.helper.resolve(),opts.main.resolve(),opts.ld)
    except (ValueError,OSError,subprocess.TimeoutExpired) as exc:
        result={'status':'FAIL','reason':str(exc)}
    out=json.dumps(result,indent=2)+'\n';print(out,end='')
    if opts.report:
        with opts.report.open('x',encoding='utf8') as f:f.write(out)
    return 0 if result['status']=='PASS' else 2

if __name__=='__main__':raise SystemExit(main_cli())
