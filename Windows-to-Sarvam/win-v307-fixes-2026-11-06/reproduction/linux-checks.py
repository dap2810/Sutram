from pathlib import Path
import subprocess,os,json,time
root=Path(__file__).resolve().parents[2]
base=root.parents[1]
out=root/'build/fixes/linux';out.mkdir(exist_ok=True)
results=[]
for label,source in [('baseline',base),('candidate',root)]:
    target=out/label;target.mkdir(exist_ok=True)
    for name in ['lib','lang']:
        if not (target/name).exists():(target/name).symlink_to(root/name,target_is_directory=True)
    compiler=target/'sutram_compiler';obj=target/'compiler.o'
    subprocess.run(['nasm','-f','elf64','-I.','src/r68_compiler_entry.asm','-o',str(obj)],cwd=source,check=True)
    subprocess.run(['ld','-o',str(compiler),str(obj)],check=True)
    commands=[['tests/run_tests.py'],['tools/codegen_gate.py',str(compiler)],['tools/test_lang_packs.py',str(compiler)],
              ['tools/proof_lib.py','--compiler',str(compiler)],['tools/proof_props.py','--compiler',str(compiler)],
              ['tools/check_layers.py'],['tests/r23/test_capabilities.py','--compiler',str(compiler)],
              ['tests/r126/test_kinds.py','--compiler',str(compiler)],['tests/r127/test_descriptor.py','--compiler',str(compiler)],
              ['tests/r133/test_indirect_slice.py','--compiler',str(compiler)]]
    for i,args in enumerate(commands):
        begin=time.monotonic();log=target/(str(i)+'-'+Path(args[0]).stem+'.log')
        with log.open('w') as f:
            try:p=subprocess.run(['python3',*args],cwd=root,env=dict(os.environ,SUTRAM_COMPILER=str(compiler)),stdout=f,stderr=subprocess.STDOUT,timeout=240);rc=p.returncode
            except subprocess.TimeoutExpired:rc='TIMEOUT'
        row=dict(label=label,command=args,exit=rc,seconds=time.monotonic()-begin,log=str(log),tail=log.read_text(errors='replace').splitlines()[-3:]);results.append(row)
        (out/'results.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(row),flush=True)
