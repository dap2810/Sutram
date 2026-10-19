from pathlib import Path
import subprocess,json,os,re,sys
# Process-local error mode inherited only by our test children.
import ctypes
ctypes.windll.kernel32.SetErrorMode(0x8003)
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'build/windows/acceptance';out.mkdir(parents=True,exist_ok=True)
exe=ROOT/'win/sutram.exe'
names=[]
skipped=[]
for source in sorted((ROOT/'examples').glob('*.sm')):
    if re.search(r'\b(nishkriya|dvaram|pad8?|likh8?|net\w*|system|unlink)\b',source.read_text(encoding='utf8')):
        skipped.append({'case':source.stem,'status':'SKIP_SIDE_EFFECT_OR_INLINE_ASM'})
    else:names.append(source.stem)
langs={'37_native_gujarati':'gujarati','38_native_hindi':'hindi','39_native_tamil':'tamil','218_sanskrit_devanagari':'sanskrit','219_sanskrit_kosh_aliases':'sanskrit'}
stdin={'23_grahan_input':'5\n','59_windows_grahan_runtime':'42\n','24_guess_game':'7\n','26_calculator':'20\n4\n','number_game':'3\n','46_language_reference':'7\n'}
rows=list(skipped)
for name in names:
    source=ROOT/'examples'/f'{name}.sm'
    if not source.exists():continue
    target=out/f'{name}.exe'
    cmd=[str(exe)]+(['--lang',langs[name]] if name in langs else [])+[str(source),str(target)]
    row={'case':name,'compile_command':cmd}
    try:
        compile_cwd=out if name=='79_ayojan_cwd' else ROOT
        row['compile_cwd']=str(compile_cwd)
        c=subprocess.run(cmd,cwd=compile_cwd,capture_output=True,timeout=15)
        row.update(compile_exit=c.returncode,compile_stdout=c.stdout.decode('utf8','replace'),compile_stderr=c.stderr.decode('utf8','replace'))
        fail=(ROOT/'tests/expect'/f'{name}.compile_fail').exists()
        if fail:
            actual=(c.stdout+c.stderr).decode('utf8','replace').replace('\r\n','\n').replace(str(ROOT),'<ROOT>').replace('\\','/')
            expected=(ROOT/'tests/expect'/f'{name}.out').read_text(encoding='utf8')
            ec=int((ROOT/'tests/expect'/f'{name}.exit').read_text())
            row['status']='PASS' if c.returncode==ec and actual==expected else 'FAIL'
            if row['status']=='FAIL':row.update(expected_stdout=expected,actual_normalized=actual,expected_exit=ec)
        elif c.returncode:
            row['status']='COMPILE_FAIL'
        else:
            r=subprocess.run([str(target)],cwd=out,input=stdin.get(name,'').encode(),capture_output=True,timeout=5)
            actual=r.stdout.decode('utf8','replace').replace('\r\n','\n')
            row.update(run_command=[str(target)],exit=r.returncode,stdout=actual,stderr=r.stderr.decode('utf8','replace'))
            expect=ROOT/'tests/expect'/f'{name}.out'
            if expect.exists():
                expected=expect.read_text(encoding='utf8')
                ec=int((expect.with_suffix('.exit')).read_text().strip())
                row['status']='PASS' if actual==expected and r.returncode==ec else 'FAIL'
                if row['status']=='FAIL':row.update(expected_stdout=expected,expected_exit=ec)
            else:row['status']='NO_EXPECTATION'
    except subprocess.TimeoutExpired:row['status']='TIMEOUT'
    rows.append(row)
    if row['status']!='PASS':print(name,row['status'],flush=True)
log=Path(os.environ.get('SUTRAM_EVIDENCE',str(ROOT/'build/windows/evidence')))/'native-cases.json'
log.parent.mkdir(parents=True,exist_ok=True)
log.write_text(json.dumps(rows,indent=2,ensure_ascii=True))
print({s:sum(r['status']==s for r in rows) for s in sorted({r['status'] for r in rows})})


sys.exit(any(r['status'] in ('FAIL','COMPILE_FAIL','TIMEOUT') for r in rows))
