from pathlib import Path
import subprocess,json,hashlib,ctypes
root=Path(__file__).resolve().parents[2];out=root/'Windows-to-Sarvam/win-v307-fixes-2026-11-06/wrapper-comparison';out.mkdir(exist_ok=True)
ctypes.windll.kernel32.SetErrorMode(0x8003)
upstream=root/'build/fixes/upstream-v308.exe'
upstream.write_bytes(subprocess.check_output(['git','show','38751cee:win/sutram.exe'],cwd=root))
template='''prakriya keep(x) {
    nivartanam x
}
mukhya() {
    kosh k[1]
    kosh_kship(k, 7)
    vitti obstacle = nirmmita(16)
    vitti zero = 0
    vitti t = keep(k[0:1] OP zero)
    kosh_kship(k, 8)
    k[0] = 99
    vitti addr = t[0]
    likha(addr[0])
    likha(k[0])
}
'''
rows=[]
for op,label in [('+','add'),('^','xor')]:
    src=out/(label+'.sm');src.write_text(template.replace('OP',op),encoding='utf8')
    for version,compiler in [('baseline-v307',root/'build/fixes/baseline.exe'),('repair-v307',root/'build/fixes/candidate.exe'),('upstream-v308',upstream)]:
        exe=out/(label+'-'+version+'.exe')
        c=subprocess.run([str(compiler),str(src),str(exe)],capture_output=True,timeout=30)
        row=dict(label=label,version=version,compiler_sha256=hashlib.sha256(compiler.read_bytes()).hexdigest(),compile_exit=c.returncode,compile_stdout=c.stdout.decode('utf8','replace'),compile_stderr=c.stderr.decode('utf8','replace'))
        if c.returncode==0:
            p=subprocess.run([str(exe)],capture_output=True,timeout=10);row.update(exit=p.returncode,stdout=p.stdout.decode('utf8','replace'),stderr=p.stderr.decode('utf8','replace'))
        rows.append(row)
(out/'results.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2))
