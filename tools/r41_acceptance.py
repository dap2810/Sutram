#!/usr/bin/env python3
"""R41 opt-in graph native acceptance; needs a rebuilt Sutram compiler.

Checks diagnostics, valid diamond, and exact byte identity of legacy and
opt-in diamond output. Python is test tooling only, NEVER in compiler runtime.
"""
from pathlib import Path
import subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
compiler=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT/'sutram_compiler'
if not compiler.exists():
    print('BLOCKED: native Sutram compiler missing; rebuild with NASM first')
    raise SystemExit(2)

def go(src,out):
    return subprocess.run([str(compiler),str(ROOT/'examples'/src),str(out)],
                          cwd=ROOT,capture_output=True,text=True,timeout=30)
with tempfile.TemporaryDirectory(prefix='sutram_r41_') as temp:
    path=Path(temp)
    for name,code in [('164_r41_cycle_reject.sm','E_MODULE_CYCLE'),('165_r41_missing_reject.sm','E_MODULE_MISSING')]:
        result=go(name,path/(name+'.bin'))
        expected=(ROOT/'tests'/'expect'/(name.removesuffix('.sm')+'.out')).read_text()
        assert result.returncode==1,(name,result.returncode,result.stdout,result.stderr)
        assert result.stdout==expected,(name,repr(result.stdout),repr(expected))
        assert code in result.stdout,(name,code)
        print('PASS',name,'file:line +',code)
    before=go('163_r40_transitive_diamond.sm',path/'legacy.bin')
    after=go('166_r41_optin_diamond.sm',path/'modern.bin')
    assert before.returncode==after.returncode==0,(before.stdout,after.stdout)
    legacy=(path/'legacy.bin').read_bytes()
    modern=(path/'modern.bin').read_bytes()
    assert legacy==modern,('program bytes differed',len(legacy),len(modern))
    execution=subprocess.run([str(path/'modern.bin')],capture_output=True,text=True,timeout=10)
    assert execution.returncode==0 and execution.stdout=='17\n7\n',(execution.returncode,execution.stdout)
    print('PASS opt-in diamond byte identity + native output 17\\n7')
print('R41 native acceptance 3/3 PASS')
