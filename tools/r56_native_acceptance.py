#!/usr/bin/env python3
"""R56 native global-variable acceptance: real ELF execution and PE structure.

Use with r48_after built from the current NASM source. Negative cases must
return nonzero and leave no generated executable. This is NOT a Windows runtime
test: PE validation checks the image structure and protected writable section.
"""
from pathlib import Path
import os
import struct
import subprocess
import tempfile
ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "tests" / "r56_check"
COMPILER = ROOT / "r48_after"
POSITIVE = {
    "shared_rw.sm": "7\n9\n9\n9\n",
    "local_shadow.sm": "100\n31\n",
    "recursive_global.sm": "5\n7\n",
    "ordered_initializers.sm": "3\n7\n14\n0\n17\n17\n",
    "initializer_calls.sm": "17\n6\n",
    "global_for.sm": "1\n2\n3\n4\n",
    "global_pointer.sm": "44\n44\n",
}
NEGATIVE = ["bad_declaration.sm", "after_main.sm", "duplicate_global.sm",
            "global_array_unsupported.sm"]
def run(args, directory, timeout=25):
    return subprocess.run(list(map(str, args)), cwd=directory, text=True,
                          capture_output=True, timeout=timeout)
def compile_fixture(wd, filename, target):
    r = run([COMPILER, FIX / filename, target], wd)
    print("R56_NATIVE", filename, "compile", r.returncode,
          repr(r.stdout), repr(r.stderr), flush=True)
    return r
def validate_pe(path):
    data = path.read_bytes()
    assert data[:2] == b"MZ", "PE magic"
    pe = struct.unpack_from("<I", data, 0x3c)[0]
    assert data[pe:pe+4] == b"PE\\x00\\x00".replace(b"\\x00", b"\x00")
    assert struct.unpack_from("<H", data, pe+6)[0] == 2, "two PE sections"
    assert struct.unpack_from("<H", data, pe+24)[0] == 0x20b, "PE32+"
    oh_size = struct.unpack_from("<H", data, pe+20)[0]
    section_start = pe+24+oh_size
    secs = []
    for i in range(2):
        q=section_start+40*i
        name=data[q:q+8].split(b"\0",1)[0].decode()
        vsize,rva,raw,offset=struct.unpack_from("<IIII",data,q+8)
        flags=struct.unpack_from("<I",data,q+36)[0]
        secs.append((name,vsize,rva,raw,offset,flags))
    assert secs[0][0] == ".text" and secs[1][0] == ".data", secs
    assert secs[0][-1] & 0x80000000 == 0, "code must not be writable"
    assert secs[1][-1] & 0x80000000, "global data must be writable"
    assert secs[1][-1] & 0x40000000, "global data must be readable"
    assert secs[1][-1] & 0x20000000 == 0, "data must not execute"
    assert secs[1][3] > 0 and len(data) >= secs[1][4]+secs[1][3]
    assert set(data[secs[1][4]:secs[1][4]+secs[1][3]]) == {0}
    print("R56_PE_STRUCT",secs,flush=True)
def check():
    assert COMPILER.is_file(), "build r48_after first"
    with tempfile.TemporaryDirectory(prefix="sutram-r56-") as tmp:
        wd=Path(tmp)
        for name, expected in POSITIVE.items():
            output=wd/"r56_test.elf"
            output.unlink(missing_ok=True)
            r=compile_fixture(wd,name,output)
            assert r.returncode == 0 and output.is_file(),(name,r)
            p=run([output],wd)
            print("R56_NATIVE",name,"execute",p.returncode,repr(p.stdout),
                  repr(p.stderr),flush=True)
            assert p.returncode == 0 and p.stdout == expected, (
                name,p.returncode,repr(p.stdout),repr(expected))
        for name in NEGATIVE:
            output=wd/"r56_negative.elf"
            output.unlink(missing_ok=True)
            r=compile_fixture(wd,name,output)
            assert r.returncode != 0 and not output.exists(),(
                name,"negative accepted",r.returncode)
        pe_path=wd/"global_test.exe"
        r=compile_fixture(wd,"shared_rw.sm",pe_path)
        assert r.returncode == 0 and pe_path.is_file()
        validate_pe(pe_path)
    print("R56_GLOBAL_ACCEPTED scalar_read_write=1 shadowing=1 recursion=1 "
          "ordered_init=1 nonliteral_init=1 function_init=1 zero_default=1 "
          "global_for=1 pointer_index=1 bad_declarations=4 pe_data=1",
          flush=True)
if __name__ == "__main__":
    check()
