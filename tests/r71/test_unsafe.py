"""Execute the R71 token pass as machine code via GNU as; not a Sutram build."""
from __future__ import annotations
import ctypes as C
import importlib.util
import os
from pathlib import Path
import random
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('nasm_bridge',ROOT/'tests/r71/nasm_test_bridge.py')
bridge=importlib.util.module_from_spec(spec);spec.loader.exec_module(bridge)
class Token(C.Structure):
    _fields_=[('kind',C.c_uint64),('value',C.c_uint64),('semantic',C.c_uint64),('line',C.c_uint64),('origin',C.c_uint64)]

class UnsafePass(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix='r71-unsafe-')
        p=Path(cls.temp.name)
        (p/'helper.S').write_text(bridge.to_gas((ROOT/'src/r71_unsafe_tokens.inc').read_text()))
        (p/'bridge.S').write_text('''
.intel_syntax noprefix
.text
.globl test_unsafe
test_unsafe:
    push r12
    push r13
    sub rsp,8
    mov r12,rcx
    mov r13,r8
    call r71_check_unsafe
    mov [r12],rdx
    mov [r13],rcx
    add rsp,8
    pop r13
    pop r12
    ret
.section .note.GNU-stack,"",@progbits
''')
        result=subprocess.run(['gcc','-shared','-fPIC','-Wl,-Bsymbolic','-o',str(p/'test.so'),str(p/'helper.S'),str(p/'bridge.S')],capture_output=True,timeout=30)
        if result.returncode:raise RuntimeError(result.stderr.decode())
        cls.lib=C.CDLL(str(p/'test.so'))
        cls.fn=cls.lib.test_unsafe
        cls.fn.argtypes=[C.c_void_p,C.c_uint64,C.c_uint64,C.POINTER(C.c_uint64),C.POINTER(C.c_uint64)]
        cls.fn.restype=C.c_int64
    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()
    def run_pass(self,descriptors,capacity=None):
        names=[];records=[]
        for i,d in enumerate(descriptors):
            if isinstance(d,str):
                if len(d)==1 and d in '{}();':k,v,sem=5,ord(d),0
                else:
                    b=C.create_string_buffer(d.encode());names.append(b);k,v,sem=2,C.addressof(b),0
            else:k,v,sem=d
            records.append(Token(k,v,sem,i+1,1000+i))
        cap=capacity if capacity is not None else len(records)+50
        arr=(Token*max(cap,len(records),1))(*records)
        old=C.string_at(C.addressof(arr),len(records)*40)
        error,at=C.c_uint64(99),C.c_uint64(99)
        n=self.fn(arr,len(records),cap,C.byref(error),C.byref(at))
        if n<0:self.assertEqual(C.string_at(C.addressof(arr),len(records)*40),old,'failure mutated tokens')
        output=[(t.kind,t.value,t.semantic,t.line,t.origin) for t in arr[:max(0,n)]]
        return n,error.value,at.value,output
    def test_plain_program_unchanged(self):
        n,e,_,out=self.run_pass(['{',(3,8,0),'}',(0,0,0)])
        self.assertEqual((n,e),(4,0));self.assertEqual([x[3] for x in out],[1,2,3,4])
    def test_boundary_lowers_to_true_if_and_keeps_braces(self):
        n,e,_,o=self.run_pass(['{','asurakshit','{',(6,0,4),'}','}',(0,0,0)])
        self.assertEqual((n,e),(10,0));self.assertEqual([t[0] for t in o],[5,1,5,3,5,5,6,5,5,0])
        self.assertEqual(o[1][2],6);self.assertEqual(o[3][1],1)
        self.assertTrue(all(t[3:]==(2,1001) for t in o[1:5]))
        self.assertEqual([t[1] for t in o if t[0]==5],[123,40,41,123,125,125])
    def test_each_canonical_raw_builtin_rejected(self):
        for op in (1,4,14,15,28,29,30,31):
            with self.subTest(op=op):self.assertEqual(self.run_pass(['{',(6,0,op),'}'])[:3],(-1,1,1))
    def test_each_canonical_raw_builtin_inside_boundary(self):
        for op in (1,4,14,15,28,29,30,31):
            with self.subTest(op=op):self.assertEqual(self.run_pass(['{','asurakshit','{',(6,0,op),'}','}'])[:2],(9,0))
    def test_inline_assembly_requires_boundary(self):self.assertEqual(self.run_pass(['{',(1,0,27),'}'])[1],1)
    def test_inline_assembly_inside_boundary(self):self.assertEqual(self.run_pass(['{','asurakshit','{',(1,0,27),'}','}'])[1],0)
    def test_other_builtins_are_not_advertised_checked(self):self.assertEqual(self.run_pass(['{',(6,0,13),(6,0,7),'}'])[1],0)
    def test_nested_boundary(self):self.assertEqual(self.run_pass(['{','asurakshit','{','asurakshit','{',(6,0,4),'}','}','}'])[:2],(15,0))
    def test_boundary_ends_at_its_brace(self):self.assertEqual(self.run_pass(['{','asurakshit','{','}',(6,0,4),'}'])[1],1)
    def test_ordinary_inner_block_does_not_end_boundary(self):self.assertEqual(self.run_pass(['{','asurakshit','{','{','}',(6,0,4),'}','}'])[1],0)
    def test_top_level_marker_rejected(self):self.assertEqual(self.run_pass(['asurakshit','{','}'])[1],4)
    def test_missing_open_brace(self):self.assertEqual(self.run_pass(['{','asurakshit',';','}'])[1],2)
    def test_function_definition_inside_boundary_rejected(self):self.assertEqual(self.run_pass(['{','asurakshit','{',(1,0,12),'}','}'])[1],5)
    def test_unbalanced_braces(self):
        for inp in (['{'],['}'],['{','asurakshit','{','}']):self.assertEqual(self.run_pass(inp)[1],3)
    def test_depth_boundary(self):
        self.assertEqual(self.run_pass(['{']*256+['}']*256)[1],0)
        self.assertEqual(self.run_pass(['{']*257+['}']*257)[1],3)
    def test_expansion_capacity_checked_before_mutation(self):self.assertEqual(self.run_pass(['{','asurakshit','{','}','}'],5)[1],6)
    def test_exact_capacity(self):self.assertEqual(self.run_pass(['{','asurakshit','{','}','}'],8)[:2],(8,0))
    def test_nonmarker_identifiers(self):
        for name in ('','a','asur','asurakshitx','Asurakshit','safe'):
            self.assertEqual(self.run_pass(['{',name,'}'])[0],3)
    def test_string_is_not_marker(self):self.assertEqual(self.run_pass(['{',(7,0,0),'}'])[0],3)
    def test_invalid_capacity(self):self.assertEqual(self.run_pass(['{','}'],0)[1],6)
    def test_many_boundaries(self):
        body=['{']+['asurakshit','{','}']*100+['}']
        self.assertEqual(self.run_pass(body,700)[:2],(602,0))
    def test_seeded_balanced_inputs(self):
        rng=random.Random(71)
        for _ in range(200):
            body=['{'];markers=0
            for _ in range(rng.randrange(1,20)):
                if rng.randrange(2):body+=['asurakshit','{',(6,0,4),'}'];markers+=1
                else:body+=[(3,rng.randrange(100),0)]
            body+=['}']
            self.assertEqual(self.run_pass(body,1000)[:2],(len(body)+markers*3,0))

if __name__=='__main__':unittest.main()
