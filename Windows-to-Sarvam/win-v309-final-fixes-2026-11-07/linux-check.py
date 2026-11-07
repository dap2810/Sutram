"""Run on Ubuntu in the isolated LF checkout; preserve every argv and result."""
from pathlib import Path
import hashlib,json,subprocess,shutil
root=Path.cwd();out=Path(__file__).resolve().parent
review=out.parents[1]
work=root/'build/linux-final-validation';work.mkdir(parents=True,exist_ok=True)
rows=[]
def run(cmd,limit=180):
    p=subprocess.run(list(map(str,cmd)),cwd=root,capture_output=True,text=True,timeout=limit)
    row=dict(command=list(map(str,cmd)),exit=p.returncode,stdout=p.stdout,stderr=p.stderr)
    rows.append(row);(out/'linux-check.json').write_text(json.dumps(rows,indent=2)+'\n')
    print(p.stdout[-1400:],p.stderr[-600:],flush=True)
    assert p.returncode==0,row
run(['git','rev-parse','HEAD'])
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()=='664ff1889d23d37e10318a4c2d1950ce6cdb115e'
# Same reviewed PE input on both platforms; no Linux cross-linker is installed.
shutil.copyfile(review/'win/sutram.exe',root/'win/sutram.exe')
print('PE input SHA256',hashlib.sha256((root/'win/sutram.exe').read_bytes()).hexdigest(),flush=True)
run(['python3','tools/build_installer_linux.py','--payload-only','--work','build/linux-payload-final'])
# Review build of the canonical NASM entry. Frozen release pins are intentionally not promoted.
run(['nasm','-f','elf64','-I'+str(root)+'/', 'src/r68_compiler_entry.asm','-o',work/'compiler.o'])
run(['ld','-o',work/'sutram_compiler',work/'compiler.o'])
run([work/'sutram_compiler','--version'])
run(['python3','tests/r137/test_global_initializers.py','--compiler',work/'sutram_compiler','--report',out/'global-linux.json'])
run(['python3','tests/r137/test_slice_number.py','--compiler',work/'sutram_compiler'])
run(['python3','tests/r134/test_one_predicate.py','--compiler',work/'sutram_compiler'])
print('PASS Linux payload build, NASM host and all three regression gates',flush=True)
