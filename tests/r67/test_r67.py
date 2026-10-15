"""R67 isolated machine-code and source tests; not full compiler/Windows tests."""
from __future__ import annotations
import ctypes as C
import importlib.util
import json
import os
from pathlib import Path
import random
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import r67_prepare_compiler as prep
spec=importlib.util.spec_from_file_location('r66helpers',ROOT/'tests/r66/test_native_helpers.py')
r66=importlib.util.module_from_spec(spec);spec.loader.exec_module(r66)

@unittest.skipUnless(shutil.which('gcc') and os.name=='posix','isolated Linux instruction harness')
class Helpers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory(prefix='r67-native-');p=Path(cls.tmp.name)
        paths=['src/r67_stack_pair.inc','windows/gui/r66_indic_clusters.asm','windows/gui/r67_cluster_count.asm']
        objects=[]
        for i,name in enumerate(paths):
            text=(ROOT/name).read_text()
            text='\n'.join(x for x in text.splitlines() if not x.startswith('extern '))
            gas=p/f'helper{i}.S';gas.write_text(r66.to_gas(text));objects.append(str(gas))
        bridge=p/'bridge.c'
        bridge.write_text('''
#include <stdint.h>
extern int64_t __attribute__((ms_abi)) r67_count_editor_clusters(const unsigned char*,const unsigned char*);
int64_t count_clusters(const unsigned char* p,const unsigned char* e) { return r67_count_editor_clusters(p,e); }
''')
        so=p/'r67.so'
        cp=subprocess.run(['gcc','-shared','-fPIC','-O2','-Wall','-Wextra','-Werror','-o',str(so),*objects,str(bridge)],capture_output=True,timeout=30)
        if cp.returncode: raise AssertionError(cp.stderr.decode())
        cls.lib=C.CDLL(str(so))
        for name in ('r67_is_pure_stack_pair','count_clusters'):
            fn=getattr(cls.lib,name);fn.argtypes=[C.c_void_p,C.c_void_p];fn.restype=C.c_int64
    @classmethod
    def tearDownClass(cls): cls.tmp.cleanup()
    def call(self,name,data):
        b=C.create_string_buffer(data);p=C.addressof(b)
        return getattr(self.lib,name)(p,p+len(data))
    def pair(self,s): return self.call('r67_is_pure_stack_pair',s.encode())
    def test_all_same_register_pairs(self):
        for reg in range(16):
            raw=bytes((0x50+reg,0x58+reg)) if reg<8 else bytes((0x41,0x50+reg-8,0x41,0x58+reg-8))
            self.assertEqual(self.pair(raw.hex(' ')),int(reg!=4))
    def test_all_different_register_pairs(self):
        for push in range(16):
            for pop in range(16):
                if push==pop: continue
                a=bytes([0x50+push]) if push<8 else bytes([0x41,0x50+push-8])
                b=bytes([0x58+pop]) if pop<8 else bytes([0x41,0x58+pop-8])
                self.assertEqual(self.pair((a+b).hex(' ')),0)
    def test_exact_instruction_boundaries_only(self):
        for s in ('b8 50 58 00 00','50 90 58','50 58 90','eb 00 50 58','48 50 48 58','66 50 66 58','50 58 50 58','54 5c'):
            self.assertEqual(self.pair(s),0,s)
    def test_hex_validation(self):
        for s in ('',' ', '5','50 5','5 0 58','50 gg','50\n58','50 58x','50\x0058','push rax; pop rax'):
            self.assertEqual(self.pair(s),0,s)
        for s in ('5058',' 50  58 ','41 53 41 5B','4153415b'):
            self.assertEqual(self.pair(s),1,s)
    def test_truncated_input_progress(self):
        raw=b'41 57 41 5f'
        for n in range(len(raw)):
            self.assertEqual(self.call('r67_is_pure_stack_pair',raw[:n]),0)
    def test_random_hex_rejected_unless_exact(self):
        rng=random.Random(67)
        for _ in range(1000):
            raw=bytes(rng.randrange(256) for _ in range(rng.randrange(0,12)))
            legal=(len(raw)==2 and raw[0] in (0x50,0x51,0x52,0x53,0x55,0x56,0x57) and raw[1]==raw[0]+8) or (len(raw)==4 and raw[0]==raw[2]==0x41 and 0x50<=raw[1]<=0x57 and raw[3]==raw[1]+8)
            self.assertEqual(self.pair(raw.hex(' ')),int(legal))
    def test_cluster_counter(self):
        for text,n in [('',0),('abc',3),('कि',1),('क्ष',1),('કિ',1),('ક્ષ',1),('a\r\nb',3),('😀',1),('।॥',2)]:
            self.assertEqual(self.call('count_clusters',text.encode()),n,(text,n))
    def test_counter_invalid_utf8_progress(self):
        self.assertEqual(self.call('count_clusters',b'\xff\xfe\xe0'),3)
    def test_counter_random_data_matches_iterator(self):
        # Native R66 iterator is independently called by the inherited tests.
        for data in (b'x'*65534,'કિ '.encode()*1000,'कि'.encode()*1000):
            expected=65534 if data[:1]==b'x' else (2000 if data.endswith(b' ') else 1000)
            self.assertEqual(self.call('count_clusters',data),expected)

class Source(unittest.TestCase):
    def pack(self,name):
        return dict(line.split() for line in (ROOT/f'lang/{name}.lang').read_text().splitlines() if line and not line.startswith('#'))
    def test_gujarati_collision_removed(self):
        p=self.pack('gujarati');self.assertNotIn('સંખ્યા',p);self.assertEqual(len(p),44)
    def test_all_previous_words_preserved(self):
        base=json.loads((ROOT/'tests/r67/baseline_packs.json').read_text())
        for lang,words in base.items():
            for word,value in words.items(): self.assertEqual(self.pack(lang)[word],value)
    def test_new_abbreviations_exact(self):
        for lang,sign,count in [('bengali','\u09fd',34),('punjabi','\u0a76',34)]:
            p=self.pack(lang);self.assertEqual(len(p),count)
            self.assertEqual(sum(k.endswith(sign) for k in p),4)
            self.assertNotIn(sign,p)
    def test_word_and_table_capacity(self):
        for lang in ('gujarati','bengali','punjabi'):
            self.assertTrue(all(len(k.encode())<64 for k in self.pack(lang)))
    def test_staging_anchors_are_preemission(self):
        source=prep.OLD+'    push r12\n'+prep.INCLUDE_OLD+'    ret\n'
        result=prep.add_pair_site(source)
        self.assertLess(result.index('call r67_is_pure_stack_pair'),result.index('    push r12'))
        self.assertIn('%ifdef SUTRAM_R67_PURE_STACK_PAIRS',result)
        self.assertNotIn('[rel code_sz]',result)
    def test_missing_and_duplicate_anchor_rejected(self):
        for source in ('',prep.OLD,prep.INCLUDE_OLD,prep.OLD*2+prep.INCLUDE_OLD,prep.OLD+prep.INCLUDE_OLD*2):
            with self.assertRaises(ValueError): prep.add_pair_site(source)
    def test_reapply_and_source_drift_rejected(self):
        after=prep.add_pair_site(prep.OLD+prep.INCLUDE_OLD)
        with self.assertRaises(ValueError): prep.add_pair_site(after)
        with self.assertRaises(ValueError): prep.prepare(b'unreviewed source')
    def test_gui_build_links_objects(self):
        s=(ROOT/'windows/gui/build-gui.ps1').read_text()
        for name in ('r67_gui_entry.asm','r66_indic_clusters.asm','r67_cluster_count.asm'): self.assertIn(name,s)
        self.assertIn('@objects',s);self.assertNotIn('ExecutionPolicy Bypass',s)
    def test_gui_calls_real_counter_without_caret_override(self):
        s=(ROOT/'windows/gui/r67_gui_entry.asm').read_text()
        self.assertIn('call r67_count_editor_clusters',s)
        self.assertIn('API WideCharToMultiByte',s)
        self.assertIn('API SetWindowTextA',s)
        self.assertNotIn('EM_SETSEL',s);self.assertNotIn('COL_KEYWORD',s)
    def test_gui_single_call_redirect(self):
        s=(ROOT/'windows/gui/r67_gui_entry.asm').read_text()
        self.assertIn('%ifidni %1,highlight_editor',s)
        self.assertIn('%unmacro call 1',s)
        self.assertIn('%include "windows/gui/sutram_gui.asm"',s)
    def test_standalone_examples_have_expected_pairs(self):
        for lang in ('bengali','punjabi'):
            stem=ROOT/f'examples/r67/{lang}_native'
            txt=stem.with_suffix('.sm').read_text()
            self.assertIn('।',txt);self.assertIn('॥',txt)
            self.assertEqual(stem.with_suffix('.exit').read_text(),'0\n')
            self.assertEqual(stem.with_suffix('.out').read_text(),'15\n12.500000\n-7.250000\n123456789\n')
if __name__=='__main__': unittest.main()
