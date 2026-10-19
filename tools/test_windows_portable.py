"""Portable/CWD and bounded argument regressions; no PATH mutation."""
from pathlib import Path
import os,subprocess,ctypes
ctypes.windll.kernel32.SetErrorMode(0x8003)
r=Path(__file__).resolve().parents[1];exe=r/'win/sutram.exe'
work=r/'build/windows/portable cwd';work.mkdir(parents=True,exist_ok=True)
for name,lang in [('01_hello',None),('79_ayojan_cwd',None),('218_sanskrit_devanagari','sanskrit')]:
    target=work/(name+'.bin')
    cmd=['sutram']+(['--lang',lang] if lang else [])+[str(r/'examples'/(name+'.sm')),str(target)]
    x=subprocess.run(cmd,executable=str(exe),cwd=work,capture_output=True,timeout=10)
    print('EXE',exe,'ARGV',cmd,'CWD',work,'EXIT',x.returncode)
    print((x.stdout+x.stderr).decode('utf8','replace'))
    assert x.returncode==0
    y=subprocess.run([str(target)],cwd=work,capture_output=True,timeout=5)
    print('RUN',target,'EXIT',y.returncode,'STDOUT',repr(y.stdout.decode('utf8')))
    assert y.returncode==0 and y.stdout.decode('utf8')==(r/'tests/expect'/(name+'.out')).read_text(encoding='utf8')
    assert target.read_bytes()[:2]==b'MZ'
for label,args in [('too many arguments',['x']*20),('oversized command',['x'*3000])]:
    x=subprocess.run([str(exe)]+args,cwd=work,capture_output=True,timeout=5)
    print(label,'EXIT',x.returncode)
    assert x.returncode==2
print('PORTABLE_PASS: external CWD, packs, imports, spaces, .bin PE and argument bounds')
