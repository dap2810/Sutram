#!/usr/bin/env python3
"""Round54 exhaustive registered-builtin valid/invalid arity matrix and raw-memory execution."""
from pathlib import Path
import subprocess, tempfile
ROOT=Path(__file__).resolve().parents[1]
COMP=ROOT/"r48_after"
BASELINE=ROOT/"r54_before"
FIX=ROOT/"tests/r54_check"
SPECS=[["likh",2,2,"b, 300"],["sthagita",0,0,""],["pad",1,1,"b"],["dvaram",2,3,"\"missing\", 0"],["paadh",3,3,"0, b, 0"],["likha",1,3,"5"],["band",1,1,"0"],["netsock",0,0,""],["netbind",2,2,"0, 9000"],["netlisten",1,1,"0"],["netaccept",1,1,"0"],["nirmmita",1,1,"64"],["likh8",2,2,"b, 66"],["pad8",1,1,"b"],["vartani_len",1,1,"\"hi\""],["vartani_cmp",2,2,"\"hi\", \"hi\""],["vartani_cat",2,2,"b, \"hi\""],["sankhya_yog",3,3,"b, b, b"],["sankhya_gunan",3,3,"b, b, b"],["sankhya_dot",2,2,"b, b"],["likha_fmt",2,2,"\"x\", 1"],["char_at",2,2,"\"Hi\", 1"],["char_code",1,2,"\"Hi\""],["char_from",1,1,"65"],["char_upper",1,1,"97"],["char_lower",1,1,"65"],["likh8c",3,3,"b, 9, b + 128"],["pad8c",2,2,"b, b + 128"],["smaran",3,3,"b, 0, 16"],["smaran_cp",3,3,"b, \"AB\", 3"],["vartani_cp",2,2,"b, \"AB\""],["grahan",0,0,""],["lkhb",1,1,"7"],["shabda",1,1,"\"hi\""],["pankti_len",1,1,"b"],["kosh_push",2,2,"a, 3"],["kosh_pop",1,1,"a"],["kosh_len",1,1,"a"],["kosh_cap",1,1,"a"],["set_char",3,3,"b, 0, 65"]]
OPTIONAL={"dvaram":'"missing", 0, 384',"char_code":'"Hi", 1',"likha":"1, 2, 3"}
DIRECT={"likh","sthagita","likh8","likh8c","smaran","smaran_cp","vartani_cp","vartani_cat","kosh_push","shabda","likha","likha_fmt","lkhb"}
def execute(args,cwd):
    return subprocess.run([str(x) for x in args],cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=12)
def code(name,args):
    call=f"{name}({args})"
    if name not in DIRECT:
        call=f"likha({call})"
    return f"""mukhya() {{
    vitti gate = 0
    vitti b = nirmmita(128)
    kosh a[2]
    yadi (gate) {{
        {call}
    }}
    likha(54)
}}
"""
def case(name,kind,args,valid):
    with tempfile.TemporaryDirectory(prefix="r54-") as d:
        wd=Path(d); src=wd/"case.sm"; exe=wd/"out.elf"
        src.write_text(code(name,args))
        if valid:
            p=execute([COMP,src,exe],wd)
            assert p.returncode==0 and exe.is_file(),(name,kind,p.returncode,p.stdout,p.stderr)
            x=execute([exe],wd)
            print("R54_VALID",name,kind,"compile",p.returncode,"run",x.returncode,"stdout",repr(x.stdout),flush=True)
            assert x.returncode==0 and x.stdout=="54\n",(name,kind,x.returncode,repr(x.stdout))
        else:
            p=execute([COMP,"--check",src],wd)
            print("R54_INVALID",name,kind,"exit",p.returncode,"stdout",repr(p.stdout[:180]),flush=True)
            assert p.returncode!=0 and "Sutram Error" in p.stdout and not exe.exists(),(name,kind,p.returncode,p.stdout,p.stderr)
def main():
    assert len(SPECS)==40
    for name,lo,hi,args in SPECS:
        case(name,"valid",args,True)
        if name in OPTIONAL:
            case(name,"optional",OPTIONAL[name],True)
        case(name,"too_few",", ".join(["1"]*(lo-1)) if lo else "1",False)
        case(name,"too_many",", ".join(["1"]*(hi+1)),False)
    # Observe (do not normalize away) the pre-R54 copy defect on real ELF.
    with tempfile.TemporaryDirectory(prefix="r54-baseline-") as d:
        wd=Path(d)
        pre=execute([BASELINE,FIX/"raw_valid.sm",wd/"before"],wd)
        assert pre.returncode==0,(pre.returncode,pre.stdout,pre.stderr)
        prev=execute([wd/"before"],wd)
        print("R54_BEFORE_RAW_COPY",prev.returncode,"stdout",repr(prev.stdout),flush=True)
        assert prev.returncode==0 and prev.stdout.endswith("0\n1\n"),repr(prev.stdout)
    with tempfile.TemporaryDirectory(prefix="r54-raw-") as d:
        wd=Path(d)
        p=execute([COMP,FIX/"raw_valid.sm",wd/"raw"],wd)
        assert p.returncode==0,(p.returncode,p.stdout,p.stderr)
        x=execute([wd/"raw"],wd)
        print("R54_RAW_VALID",x.returncode,"stdout",repr(x.stdout),flush=True)
        assert x.returncode==0 and x.stdout=="258\n2\n66\n77\n0\n65\n65\n79\n75\n89\n4\n"
        n=execute([COMP,"--check",FIX/"raw_invalid.sm"],wd)
        print("R54_RAW_INVALID",n.returncode,"stdout",repr(n.stdout),flush=True)
        assert n.returncode!=0 and "Sutram Error" in n.stdout
    with tempfile.TemporaryDirectory(prefix="r54-seven-") as d:
        wd=Path(d);src=wd/"seven.sm"
        src.write_text(code("likha","1,2,3,4,5,6,7"))
        n=execute([COMP,"--check",src],wd)
        print("R54_SEVEN_ARGUMENT_GUARD",n.returncode,"stdout",repr(n.stdout[:200]),flush=True)
        assert n.returncode!=0 and "Sutram Error" in n.stdout
    print("R54_ACCEPTED builtin_ids=40 valid_arity=43 invalid_arity=80 raw_memory=1 arg_capacity=1",flush=True)
if __name__=="__main__":
    main()
