#!/usr/bin/env python3
"""R95 developer-only oracle for Claude R28's ACTUAL SUTRAMO1 format.

Python is only test infrastructure; not Sutram compiler, native NASM linker,
or a new shipping dependency. The two inputs contain SYNTHETIC machine code.
"""
import hashlib
import struct
import subprocess
import tempfile
from pathlib import Path

MAGIC = b'SUTRAMO1'
U64 = '<Q'


def encode(code, symbols, relocs):
    b = bytearray(MAGIC + struct.pack('<3Q', len(code), len(symbols), len(relocs)) + code)
    for table in (symbols, relocs):
        for off, name in table:
            raw = name.encode('utf-8')
            b += struct.pack('<2Q', off, len(raw)) + raw
    return bytes(b)


def read(b):
    if len(b) < 32 or b[:8] != MAGIC:
        raise ValueError('header/magic')
    c, ns, nr = struct.unpack_from('<3Q', b, 8)
    if not c or c > len(b)-32 or ns > 16384 or nr > 16384:
        raise ValueError('size/count')
    p = 32+c
    tables=[]
    for n in (ns, nr):
        a=[]
        for _ in range(n):
            if len(b)-p < 16:
                raise ValueError('short entry')
            off, ln = struct.unpack_from('<2Q', b, p)
            p+=16
            if not ln or ln > 4096 or ln > len(b)-p:
                raise ValueError('bad name length')
            name = b[p:p+ln].decode('utf-8', 'strict')
            if '\0' in name:
                raise ValueError('NUL name')
            p+=ln
            a.append((off, name))
        tables.append(a)
    if p != len(b):
        raise ValueError('trailing bytes')
    syms,rels=tables
    for off,_ in syms:
        if off>=c:
            raise ValueError('symbol out of code')
    occupied=set()
    code=b[32:32+c]
    for field,_ in rels:
        if field < 1 or field+4 > c:
            raise ValueError('relocation out of code')
        if code[field:field+4] != b'\0'*4:
            raise ValueError('field not blank')
        for i in range(field,field+4):
            if i in occupied:
                raise ValueError('overlapping relocation')
            occupied.add(i)
        if code[field-1] != 0xe8 and (field < 3 or code[field-3:field] != b'\x48\x8d\x05'):
            raise ValueError('unknown hole instruction')
    return {'code':code,'symbols':syms,'relocs':rels}


def link(objects):
    mains=[i for i,o in enumerate(objects) if ('mukhya' in (name for off,name in o['symbols']))]
    if len(mains)!=1:
        raise ValueError('one mukhya needed')
    units=[objects[mains[0]]] + [o for i,o in enumerate(objects) if i != mains[0]]
    image=bytearray()
    symbols={}
    for o in units:
        o['_base']=len(image)
        image+=o['code']
        for off,name in o['symbols']:
            if name in symbols:
                raise ValueError('duplicate symbol')
            if name=='mukhya' and off!=0:
                raise ValueError('mukhya not at zero')
            symbols[name]=o['_base']+off
    writes=[]
    for o in units:
        for field,name in o['relocs']:
            if name not in symbols:
                raise ValueError('unresolved')
            final=o['_base']+field
            disp=symbols[name]-(final+4)
            if not -(2**31) <= disp < 2**31:
                raise ValueError('rel32 overflow')
            writes.append((final,disp))
    for off,disp in writes:
        struct.pack_into('<i', image, off, disp)
    return bytes(image)


def elf(code):
    eh=b'\x7fELF\x02\x01\x01'+b'\0'*9
    entry=0x400000+120
    eh+=struct.pack('<HHIQQQIHHHHHH',2,62,1,entry,64,0,0,64,56,1,0,0,0)
    ph=struct.pack('<IIQQQQQQ',1,7,120,entry,entry,len(code),len(code)+65536,4096)
    assert len(eh)==64 and len(ph)==56
    return eh+ph+code


def root_code():
    # Integer call, runtime check, stdout write, exit zero or failure one.
    x=bytearray(bytes.fromhex('bf11000000be19000000e800000000'))
    x+=bytes.fromhex('4883f82a7500b801000000bf01000000488d3500000000')
    lea_disp=len(x)-4
    x+=bytes.fromhex('ba030000000f0531ffb83c0000000f05')
    failure=len(x)
    x+=bytes.fromhex('bf01000000b83c0000000f05')
    msg=len(x)
    x+=b'42\n'
    x[20]=failure-21
    struct.pack_into('<i',x,lea_disp,msg-(lea_disp+4))
    return bytes(x)


def main():
    passed=0
    def check(label,func,bad=False):
        nonlocal passed
        try:
            func()
            if bad:
                raise AssertionError('invalid accepted: '+label)
        except ValueError:
            if not bad:
                raise
        passed+=1
        print('PASS', label)
    root=encode(root_code(), [(0,'mukhya')],[(11,'joda')])
    leaf=encode(bytes.fromhex('4889f84801f0c3'),[(0,'joda')],[])
    check('root_exact_format',lambda:read(root))
    check('leaf_exact_format',lambda:read(leaf))
    def mutate(at, raw, original=root):
        x=bytearray(original)
        x[at:at+len(raw)]=raw
        read(bytes(x))
    check('magic_reject',lambda:mutate(0,b'X'),True)
    check('header_truncation_reject',lambda:read(root[:30]),True)
    check('file_truncation_reject',lambda:read(root[:-1]),True)
    check('code_length_reject',lambda:mutate(8,struct.pack(U64,2**64-1)),True)
    check('symbol_count_reject',lambda:mutate(16,struct.pack(U64,2**64-1)),True)
    check('reloc_count_reject',lambda:mutate(24,struct.pack(U64,2**64-1)),True)
    check('symbol_offset_reject',lambda:mutate(32+len(root_code()),struct.pack(U64,99999)),True)
    check('name_length_reject',lambda:mutate(32+len(root_code())+8,struct.pack(U64,9000)),True)
    check('reloc_field_bounds_reject',lambda:mutate(len(root)-20,struct.pack(U64,99999)),True)
    check('nonzero_hole_reject',lambda:mutate(32+11,b'\x07'),True)
    check('wrong_opcode_reject',lambda:mutate(32+10,b'\x90'),True)
    check('trailing_bytes_reject',lambda:read(root+b'garbage'),True)
    check('missing_export_reject',lambda:link([read(root),read(encode(b'\xc3',[(0,'x')],[]))]),True)
    check('duplicate_export_reject',lambda:link([read(root),read(encode(b'\xc3',[(0,'mukhya')],[]))]),True)
    check('duplicate_main_reject',lambda:link([read(root),read(root)]),True)
    check('no_main_reject',lambda:link([read(leaf)]),True)
    linked=link([read(leaf),read(root)])  # argv reversed: main must still go first
    check('links_in_reverse_argument_order',lambda:link([read(leaf),read(root)]))
    assert struct.unpack_from('<i',linked,11)[0] == 54
    check('call_site_disp54',lambda:True)
    with tempfile.TemporaryDirectory() as td:
        exe=Path(td)/'r95_synthetic'
        body=elf(linked)
        exe.write_bytes(body)
        exe.chmod(0o700)
        p=subprocess.run([str(exe)],capture_output=True,timeout=4)
        print('synthetic_stdout_hex',p.stdout.hex())
        print('synthetic_exit',p.returncode)
        print('synthetic_stderr_bytes',len(p.stderr))
        assert (p.stdout,p.returncode,p.stderr)==(b'42\n',0,b'')
    check('synthetic_ELF_runtime_prints_42',lambda:True)
    print('root_bytes',len(root),'leaf_bytes',len(leaf),'linked_CODE_bytes',len(linked))
    print('root_SHA256',hashlib.sha256(root).hexdigest())
    print('leaf_SHA256',hashlib.sha256(leaf).hexdigest())
    print('ELF_SHA256',hashlib.sha256(body).hexdigest())
    print('RESULT',passed,'PASS 0 FAIL [synthetic host reference, NOT Sutram linker]')


if __name__=='__main__':
    main()
