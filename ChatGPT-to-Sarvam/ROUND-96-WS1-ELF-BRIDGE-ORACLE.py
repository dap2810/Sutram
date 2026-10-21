#!/usr/bin/env python3
"""R96 opt-in ELF64->SUTRAMO1 bridge oracle, developer TEST ONLY.
This script is NOT a production linker, Sutram compiler, or shipping tool.
"""
from __future__ import annotations
import hashlib
from pathlib import Path
import struct
import subprocess
import sys

S = struct.Struct('<IIQQQQIIQQ')       # ELF64 section header
SYM = struct.Struct('<IBBHQQ')         # ELF64 symbol table entry
ELF_H = struct.Struct('<16sHHIQQQIHHHHHH')


def bounded_slice(data: bytes, off: int, size: int) -> bytes:
    if off > len(data) or size > len(data) - off:
        raise ValueError('out-of-bounds file section')
    return data[off:off + size]


def name_from(tab: bytes, off: int) -> bytes:
    if off >= len(tab):
        raise ValueError('string offset outside strtab')
    end = tab.find(b'\0', off)
    if end == -1:
        raise ValueError('unterminated ELF string')
    return tab[off:end]


def elf_text_function(data: bytes, desired: bytes):
    if len(data) < ELF_H.size:
        raise ValueError('truncated ELF header')
    ident, e_type, machine, ver, _, _, shoff, _, _, _, _, shentsize, shnum, shstrndx = ELF_H.unpack_from(data)
    if ident[:7] != b'\x7fELF\x02\x01\x01' or e_type != 1 or machine != 62 or ver != 1:
        raise ValueError('not x86-64 little-endian ELF ET_REL')
    if shentsize != S.size or shnum < 1 or shnum > 64 or shstrndx >= shnum:
        raise ValueError('unsupported ELF section table')
    all_sh = bounded_slice(data, shoff, shnum * shentsize)
    headers = [S.unpack_from(all_sh, i * shentsize) for i in range(shnum)]
    sh_nameoff, sh_typ, _, _, sh_off, sh_size, _, _, _, _ = headers[shstrndx]
    sh_names = bounded_slice(data, sh_off, sh_size)
    sec_names = [name_from(sh_names, h[0]) for h in headers]
    if sec_names.count(b'.text') != 1:
        raise ValueError('not exactly one .text section')
    text_idx = sec_names.index(b'.text')
    h = headers[text_idx]
    if h[1] != 1 or h[5] < 1 or h[5] > 4096 or not (h[2] & 0x4):
        raise ValueError('unsupported .text flags/size')
    code = bounded_slice(data, h[4], h[5])
    # This first stage cannot process ANY relocation, even unwind metadata.
    for j, sh in enumerate(headers):
        name, typ, flags, _, off, size, _, _, _, _ = sh
        if typ in (4, 9) and size:
            raise ValueError('unsupported REL/RELA relocations')
        if j != text_idx and (flags & 0x2) and size:
            raise ValueError('additional allocated section unsupported')
    symbols = []
    for sh in headers:
        if sh[1] != 2:
            continue
        if sh[9] != SYM.size or sh[5] % SYM.size or sh[6] >= shnum:
            raise ValueError('malformed symbol table')
        strs = bounded_slice(data, headers[sh[6]][4], headers[sh[6]][5])
        sym_bytes = bounded_slice(data, sh[4], sh[5])
        for pos in range(0, len(sym_bytes), SYM.size):
            n, info, other, section, value, length = SYM.unpack_from(sym_bytes, pos)
            label = name_from(strs, n)
            if section == 0 and label:
                raise ValueError('undefined C helper: ' + label.decode('ascii', 'replace'))
            if label == desired:
                if section != text_idx or (info & 15) != 2 or (info >> 4) not in (1, 2) or other != 0:
                    raise ValueError('function symbol has unsupported binding')
                if value >= len(code) or (length and length > len(code)-value):
                    raise ValueError('symbol range outside CODE')
                symbols.append(int(value))
    if len(symbols) != 1:
        raise ValueError('one exact exported function needed')
    return code, symbols[0]


def smo(code: bytes, defs=(), relocs=()) -> bytes:
    out = bytearray(b'SUTRAMO1' + struct.pack('<3Q', len(code), len(defs), len(relocs)) + code)
    for group in (defs, relocs):
        for off, name in group:
            out += struct.pack('<2Q', off, len(name)) + name
    return bytes(out)


def read_smo(data: bytes):
    if len(data) < 32 or data[:8] != b'SUTRAMO1':
        raise ValueError('bad object header')
    ncode, ns, nr = struct.unpack_from('<3Q', data, 8)
    pos = 32 + ncode
    if pos > len(data) or ns > 1024 or nr > 1024:
        raise ValueError('malformed lengths')
    tables = []
    for n in (ns, nr):
        table = []
        for _ in range(n):
            if pos + 16 > len(data):
                raise ValueError('short entry')
            off, ln = struct.unpack_from('<2Q', data, pos)
            pos += 16
            if ln == 0 or ln > len(data) - pos:
                raise ValueError('bad name')
            table.append((off, data[pos:pos+ln]))
            pos += ln
        tables.append(table)
    if pos != len(data):
        raise ValueError('trailing bytes')
    return bytearray(data[32:32+ncode]), tables[0], tables[1]


def link_smo(root: bytes, foreign: bytes) -> bytes:
    a, defs_a, rel_a = read_smo(root)
    b, defs_b, rel_b = read_smo(foreign)
    if rel_b:
        raise ValueError('foreign object has unhandled relocations')
    syms={}
    for base, defs in ((0,defs_a),(len(a),defs_b)):
        for off,name in defs:
            if name in syms or off >= (len(a) if base == 0 else len(b)):
                raise ValueError('duplicate or bad symbol')
            syms[name] = base + off
    if syms.get(b'mukhya') != 0:
        raise ValueError('no root')
    merged = a+b
    for off,name in rel_a:
        if name not in syms:
            raise ValueError('unresolved ' + name.decode('ascii','replace'))
        if off < 1 or off+4 > len(a) or a[off-1] != 0xe8 or a[off:off+4] != b'\0'*4:
            raise ValueError('unvalidated hole')
        disp=syms[name]-(off+4)
        if not -(1<<31) <= disp < (1<<31):
            raise ValueError('rel32 out of range')
        struct.pack_into('<i', merged, off, disp)
    return bytes(merged)


def root_code():
    # Standalone generated-machine-code *control*, not compiled Sutram source.
    # call a two-integer foreign C function, validate result 42, print "42\n", exit 0.
    code = bytearray(bytes.fromhex('bf11000000be19000000e800000000'))
    code += bytes.fromhex('4883f82a7500b801000000bf01000000488d3500000000')
    rip_site=len(code)-4
    code += bytes.fromhex('ba030000000f0531ffb83c0000000f05')
    failure=len(code)
    code += bytes.fromhex('bf01000000b83c0000000f05')
    msg=len(code)
    code += b'42\n'
    code[20] = failure - 21
    struct.pack_into('<i', code, rip_site, msg-(rip_site+4))
    return bytes(code)


def elf(code):
    ident=b'\x7fELF\x02\x01\x01'+b'\0'*9
    entry=0x400000+120
    hdr=ident+struct.pack('<HHIQQQIHHHHHH',2,62,1,entry,64,0,0,64,56,1,0,0,0)
    ph=struct.pack('<IIQQQQQQ',1,7,120,entry,entry,len(code),len(code)+65536,4096)
    return hdr+ph+code


def main():
    here=Path(__file__).resolve().parent
    flags=['-O2','-c','-ffreestanding','-fno-stack-protector','-fno-asynchronous-unwind-tables','-fno-unwind-tables','-fno-pic','-fno-pie']
    objects=[]
    for n in ('r96_ffi.c','r96_ffi_bad.c'):
        obj=here/(n+'.o')
        cmd=['gcc',*flags,str(here/n),'-o',str(obj)]
        p=subprocess.run(cmd,capture_output=True,text=True,timeout=25)
        print('CC',n,'exit',p.returncode)
        if p.returncode: raise RuntimeError(p.stderr)
        objects.append(obj)
    symbol=b'sutram_ffi_add'
    data=objects[0].read_bytes()
    code,offset=elf_text_function(data,symbol)
    foreign=smo(code,[(offset,symbol)])
    root=smo(root_code(),[(0,b'mukhya')],[(11,symbol)])
    (here/'r96_foreign.smo').write_bytes(foreign)
    (here/'r96_root.smo').write_bytes(root)
    complete=link_smo(root,foreign)
    executable=here/'r96_linked_control'
    exbytes=elf(complete)
    executable.write_bytes(exbytes)
    executable.chmod(0o700)
    p=subprocess.run([str(executable)],capture_output=True,timeout=5)
    print('runtime_stdout_hex',p.stdout.hex(),'runtime_exit',p.returncode,'runtime_stderr_bytes',len(p.stderr))
    assert (p.stdout,p.stderr,p.returncode)==(b'42\n',b'',0)
    failures=0
    try: link_smo(root,smo(b'\xc3',[(0,b'wrong_name')]))
    except ValueError as e:
        failures+=1
        print('PASS missing foreign symbol EXPECTED_ERROR',e)
    try: elf_text_function(objects[1].read_bytes(),symbol)
    except ValueError as e:
        failures+=1
        print('PASS C object with undefined helper EXPECTED_ERROR',e)
    assert failures==2
    for title,bytes_ in [('C_ELF',data),('foreign_SMO',foreign),('root_SMO',root),('linked_ELF',exbytes)]:
        print(title,'bytes',len(bytes_),'sha256',hashlib.sha256(bytes_).hexdigest())
    print('C_TEXT bytes',len(code),'offset',offset,'magic',foreign[:8], 'root_reloc',11)
    print('RESULT 6/6 PASS: 2 gcc builds, ELF extraction, linked runtime, 2 failure controls')
    print('EVIDENCE_LIMIT: synthetic root + PYTHON ELF converter/link oracle; NOT Sutram .sm output or native NASM linker')

if __name__=='__main__':
    main()
