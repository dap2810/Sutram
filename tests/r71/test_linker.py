"""Native linker-primitives tests. Objects here are assembly fixtures, NOT .sm output."""
from __future__ import annotations
import ctypes as C
import importlib.util
from pathlib import Path
import struct
import subprocess
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('bridge',ROOT/'tests/r71/nasm_test_bridge.py')
bridge=importlib.util.module_from_spec(spec);spec.loader.exec_module(bridge)

class Symbol(C.Structure):
    _fields_=[('ns',C.c_uint64),('ns_len',C.c_uint64),('name',C.c_uint64),('name_len',C.c_uint64),('offset',C.c_uint64),('arity',C.c_uint64),('public',C.c_uint64),('owner',C.c_uint64)]

class NativeLinker(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix='r71-link-');p=Path(cls.temp.name)
        (p/'link.S').write_text(bridge.to_gas((ROOT/'src/r71_module_link.inc').read_text()))
        (p/'bridge.S').write_text('''
.intel_syntax noprefix
.text
.globl test_resolve
test_resolve:
    push rbx
    mov rbx,rcx
    call r71_resolve_export
    mov [rbx],rdx
    pop rbx
    ret
.section .note.GNU-stack,"",@progbits
''')
        r=subprocess.run(['gcc','-shared','-fPIC','-Wl,-Bsymbolic','-o',str(p/'lib.so'),str(p/'link.S'),str(p/'bridge.S')],capture_output=True,timeout=30)
        if r.returncode:raise RuntimeError(r.stderr.decode())
        cls.lib=C.CDLL(str(p/'lib.so'))
        cls.lib.test_resolve.argtypes=[C.c_void_p,C.c_uint64,C.c_void_p,C.POINTER(C.c_uint64)]
        cls.lib.test_resolve.restype=C.c_int64
        cls.lib.r71_patch_rel32.argtypes=[C.c_void_p,C.c_uint64,C.c_uint64,C.c_uint64]
        cls.lib.r71_patch_rel32.restype=C.c_uint64
    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()
    def setUp(self):self.keep=[]
    def sym(self,ns,name,offset=0,arity=0,public=1,owner=0):
        a,b=C.create_string_buffer(ns.encode()),C.create_string_buffer(name.encode());self.keep.extend((a,b))
        return Symbol(C.addressof(a),len(ns.encode()),C.addressof(b),len(name.encode()),offset,arity,public,owner)
    def resolve(self,symbols,request):
        arr=(Symbol*len(symbols))(*symbols);err=C.c_uint64(99)
        off=self.lib.test_resolve(arr,len(arr),C.byref(request),C.byref(err))
        return off,err.value
    def test_same_leaf_in_two_namespaces(self):
        syms=[self.sym('left','init',12),self.sym('right','init',80)]
        self.assertEqual(self.resolve(syms,self.sym('left','init')),(12,0))
        self.assertEqual(self.resolve(syms,self.sym('right','init')),(80,0))
    def test_no_concatenation_collision(self):
        syms=[self.sym('a_b','c',17),self.sym('a','b_c',29)]
        self.assertEqual(self.resolve(syms,self.sym('a','b_c')),(29,0))
    def test_private_export_refused(self):self.assertEqual(self.resolve([self.sym('a','hidden',1,public=0)],self.sym('a','hidden')),(-1,2))
    def test_missing_module(self):self.assertEqual(self.resolve([self.sym('a','init')],self.sym('b','init')),(-1,1))
    def test_missing_export(self):self.assertEqual(self.resolve([self.sym('a','init')],self.sym('a','start')),(-1,1))
    def test_arity_mismatch(self):self.assertEqual(self.resolve([self.sym('a','init',arity=1)],self.sym('a','init')),(-1,4))
    def test_duplicate_rejected_not_first_wins(self):self.assertEqual(self.resolve([self.sym('a','init'),self.sym('a','init')],self.sym('a','init')),(-1,3))
    def test_utf8_names_are_exact_bytes(self):self.assertEqual(self.resolve([self.sym('મોડ્યુલ','આરંભ',33)],self.sym('મોડ્યુલ','આરંભ')),(33,0))
    def test_invalid_metadata(self):
        for s in [self.sym('','init'),self.sym('x'*64,'init'),self.sym('a','x'*129),self.sym('a','init',arity=7),self.sym('a','init',public=2)]:
            self.assertEqual(self.resolve([s],self.sym('a','init'))[1],5)
    def patch(self,data,field,target,length=None):
        buf=C.create_string_buffer(data,len(data));before=bytes(buf)
        ret=self.lib.r71_patch_rel32(buf,len(data) if length is None else length,field,target)
        if ret:self.assertEqual(bytes(buf),before)
        return ret,bytes(buf)
    def test_forward_rel32(self):
        r,b=self.patch(b'\xe8'+b'\0'*15,1,10);self.assertEqual(r,0);self.assertEqual(struct.unpack_from('<i',b,1)[0],5)
    def test_backward_rel32(self):
        r,b=self.patch(b'\x90'*8+b'\xe8'+b'\0'*7,9,0);self.assertEqual(r,0);self.assertEqual(struct.unpack_from('<i',b,9)[0],-13)
    def test_bad_opcode(self):self.assertEqual(self.patch(b'\x90'*10,1,8)[0],2)
    def test_bounds(self):
        for field,target in ((0,0),(7,1),(1,10),(2,2)):
            self.assertNotEqual(self.patch(b'\xe8'+b'\0'*9,field,target)[0],0)
    def test_rel32_overflow(self):self.assertEqual(self.patch(b'\xe8'+b'\0'*7,1,0x90000000,length=0xA0000000)[0],3)
    def test_two_fixture_units_link_and_execute(self):
        # Each unit has a separately defined init returning its own constant.
        # This is a native linking proof, not a claim of production .sm object emission.
        main=bytes.fromhex('e8 00000000 50 e8 00000000 5a 4801d0 89c7 b83c000000 0f05')
        left=bytes.fromhex('b811000000 c3');right=bytes.fromhex('b819000000 c3')
        image=C.create_string_buffer(main+left+right,len(main+left+right))
        syms=[self.sym('left','init',len(main)),self.sym('right','init',len(main)+len(left))]
        for field,namespace in ((1,'left'),(7,'right')):
            off,e=self.resolve(syms,self.sym(namespace,'init'));self.assertEqual(e,0)
            self.assertEqual(self.lib.r71_patch_rel32(image,len(image),field,off),0)
        code=bytes(image);base=0x400000;total=120+len(code)
        ident=b'\x7fELF\x02\x01\x01'+b'\0'*9
        eh=ident+struct.pack('<HHIQQQIHHHHHH',2,62,1,base+120,64,0,0,64,56,1,0,0,0)
        ph=struct.pack('<IIQQQQQQ',1,5,0,base,base,total,total,0x1000)
        exe=Path(self.temp.name)/'linked-two-units'
        exe.write_bytes(eh+ph+code);exe.chmod(0o700)
        p=subprocess.run([str(exe)],capture_output=True,timeout=3)
        self.assertEqual((p.returncode,p.stdout,p.stderr),(42,b'',b''))

if __name__=='__main__':unittest.main()
