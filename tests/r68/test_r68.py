"""R68 isolated machine-code and source tests. NOT full compiler/Windows tests."""
from __future__ import annotations
import ctypes as C
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import r68_prepare_review as prep
spec = importlib.util.spec_from_file_location('r66adapter', ROOT/'tests/r66/test_native_helpers.py')
old = importlib.util.module_from_spec(spec); spec.loader.exec_module(old)

def gas(text: str) -> str:
    # Additional support is ONLY RIP-relative syntax in these supplied helpers.
    return old.to_gas(text.replace('[rel ', '[rip+'))

@unittest.skipUnless(shutil.which('gcc') and sys.platform.startswith('linux'), 'isolated Linux/GCC tests')
class HelperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='r68-test-');cls.work=Path(cls.temp.name)
        (cls.work/'helpers.S').write_text(gas((ROOT/'src/r68_unicode_helpers.inc').read_text()))
        (cls.work/'diag.S').write_text('.equ TOK_KEYWORD,1\n.equ KW_PURNA,21\n.equ KW_SHUNYA,22\n'+gas((ROOT/'src/r68_diagnostics.inc').read_text()))
        cls.so=cls.work/'helper.so'
        subprocess.run(['gcc','-shared','-fPIC','-Wl,-z,noexecstack','-o',str(cls.so),str(cls.work/'helpers.S')],check=True,capture_output=True)
        cls.lib=C.CDLL(str(cls.so))
        for n in ('r68_utf8_width','r68_ends_abbreviation'):
            f=getattr(cls.lib,n);f.argtypes=[C.c_void_p,C.c_void_p];f.restype=C.c_uint64
        (cls.work/'stub.c').write_text(r'''
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
unsigned char source_buf[65537];
uint64_t source_len;
const char *source_path_ptr;
uint64_t token[5];
void *cur_tok(void) { return token; }
void print_str_z(const char *s) { (void)write(1,s,strlen(s)); }
long os_write(uint64_t fd,const void *p,uint64_t n) { return write((int)fd,p,(size_t)n); }
void os_exit(uint64_t code) { _exit((int)code); }
extern void r68_prelex_validate(void);
extern void r68_guard_value_start(void);
int main(int argc,char **argv) {
    if(argc<3) return 90;
    if(!strcmp(argv[1],"lex")) {
        source_path_ptr=argv[2];FILE *f=fopen(argv[2],"rb");if(!f)return 91;
        source_len=fread(source_buf,1,65536,f);fclose(f);r68_prelex_validate();
    } else {
        if(argc!=7) return 92;
        source_path_ptr=argv[3];token[0]=strtoull(argv[5],0,10);
        token[1]=(uintptr_t)argv[2];token[2]=strtoull(argv[6],0,10);
        token[3]=strtoull(argv[4],0,10);r68_guard_value_start();
    }
    print_str_z("HOST_CHECK_OK\n");return 0;
}
''')
        cls.exe=cls.work/'diagnostic-host'
        cmd=['gcc','-O2','-Wall','-Wextra','-Werror','-no-pie','-o',str(cls.exe),str(cls.work/'stub.c'),str(cls.work/'helpers.S'),str(cls.work/'diag.S')]
        r=subprocess.run(cmd,capture_output=True,timeout=20)
        if r.returncode:raise RuntimeError(r.stderr.decode())
    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()
    def helper(self,name,data):
        b=C.create_string_buffer(data);p=C.addressof(b)
        return getattr(self.lib,name)(p,p+len(data))
    def host(self,data):
        p=self.work/'current.sm';p.write_bytes(data)
        return subprocess.run([str(self.exe),'lex',str(p)],capture_output=True,timeout=3),p
    def value(self,text,line=7,kind=1,keyword=2,path='root.sm'):
        return subprocess.run([str(self.exe),'value',text,path,str(line),str(kind),str(keyword)],capture_output=True,timeout=3)
    def test_manual_gui_fixture_counts_on_isolated_counter(self):
        spec = importlib.util.spec_from_file_location('r67counter_test', ROOT/'tests/r67/test_r67.py')
        mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        mod.Helpers.setUpClass()
        try:
            obj=mod.Helpers()
            for row in json.loads((ROOT/'tests/r68/gui_title_cases.json').read_text()):
                self.assertEqual(obj.call('count_clusters',row['text'].encode()),row['expected_scoped_count'])
                self.assertEqual(row['expected_title'],f"Sutram Shell 1.0 | scoped clusters: {row['expected_scoped_count']}")
        finally:
            mod.Helpers.tearDownClass()

    def test_scalar_widths_and_boundaries(self):
        for text in ('A','\x00','é','क','௧','😀','\U0010ffff'):
            raw=text.encode();self.assertEqual(self.helper('r68_utf8_width',raw),len(raw))
            for n in range(1,len(raw)):self.assertEqual(self.helper('r68_utf8_width',raw[:n]),0)
    def test_every_single_byte(self):
        for n in range(256):self.assertEqual(self.helper('r68_utf8_width',bytes([n])),int(n<128))
    def test_invalid_scalar_encodings(self):
        for b in (b'',b'\xc0\xaf',b'\xe0\x9f\xbf',b'\xed\xa0\x80',b'\xf4\x90\x80\x80',b'\xf5\x80\x80\x80',b'\xe0\xadA',b'\xe0\xb3\xff'):
            self.assertEqual(self.helper('r68_utf8_width',b),0,b)
    def test_random_scalar_reference(self):
        rng=random.Random(68)
        for _ in range(5000):
            n=rng.randrange(0x110000)
            if 0xD800<=n<=0xDFFF:continue
            b=chr(n).encode();self.assertEqual(self.helper('r68_utf8_width',b),len(b))
    def test_guard_page_bounded_access(self):
        code='''import ctypes as C,mmap,sys
lib=C.CDLL(sys.argv[1]);f=lib.r68_utf8_width;f.argtypes=[C.c_void_p,C.c_void_p];f.restype=C.c_uint64
p=mmap.mmap(-1,8192,prot=mmap.PROT_READ|mmap.PROT_WRITE);base=C.addressof(C.c_char.from_buffer(p));c=C.CDLL(None)
c.mprotect.argtypes=[C.c_void_p,C.c_size_t,C.c_int];assert c.mprotect(base+4096,4096,0)==0
for raw in (b"",b"\\xe0",b"\\xe0\\xad",b"\\xf0\\x90\\x80",b"A",b"\\xe0\\xad\\xa7"):
 start=base+4096-len(raw)
 if raw:C.memmove(start,raw,len(raw))
 want=len(raw) if raw in (b"A",b"\\xe0\\xad\\xa7") else 0
 assert f(start,base+4096)==want
assert c.mprotect(base+4096,4096,mmap.PROT_READ|mmap.PROT_WRITE)==0
'''
        r=subprocess.run([sys.executable,'-c',code,str(self.so)],capture_output=True,timeout=5)
        self.assertEqual(r.returncode,0,r.stderr)
    def test_exact_abbreviation_suffixes(self):
        for s in ('मु॰','મુ૰','মু৽','ਮੁ੶'):
            self.assertEqual(self.helper('r68_ends_abbreviation',s.encode()),1)
        for s in ('','म','मु।','मु॥','मु॰x','ମୁଖ୍ୟ','முதன்மை'):
            self.assertEqual(self.helper('r68_ends_abbreviation',s.encode()),0)
    def test_utf8_diagnostic_exact_line(self):
        r,p=self.host(b'mukhya() {\n vitti x = 1\n vitti y = \xe0\xad \n}\n')
        self.assertEqual(r.returncode,1)
        self.assertEqual(r.stdout,f'Sutram Error [E_UTF8]: {p}:3: invalid or truncated UTF-8 in source code\n'.encode())
    def test_orphan_continuation_is_not_ignored(self):
        r,p=self.host('mukhya() {\n vitti y = ୧'.encode()+b'\x80\n}\n')
        self.assertEqual(r.returncode,1);self.assertIn((str(p)+':2:').encode(),r.stdout)
    def test_comments_and_strings_retain_byte_semantics(self):
        for raw in (b'# \xff\xe0\n x=1',b'/* \xe0\n\xff */ x=1',b'likha("\xff\xe0")',b'likha("\\\"#\xe0")'):
            r,p=self.host(raw);self.assertEqual((r.returncode,r.stdout),(0,b'HOST_CHECK_OK\n'),raw)
    def test_line_after_comments(self):
        r,p=self.host(b'# one\r\n/* two\n three */\n\xe0\xb3')
        self.assertEqual(r.returncode,1);self.assertIn((str(p)+':4:').encode(),r.stdout)
    def test_long_utf8_filename_untruncated(self):
        d=self.work/('नाम'*16)/('ಪಥ'*16);d.mkdir(parents=True,exist_ok=True)
        p=d/'bad.sm';p.write_bytes(b'\n\xe0')
        r=subprocess.run([str(self.exe),'lex',str(p)],capture_output=True,timeout=3)
        self.assertEqual(r.stdout,f'Sutram Error [E_UTF8]: {p}:2: invalid or truncated UTF-8 in source code\n'.encode())
        self.assertEqual(r.returncode,1)
    def test_keyword_alias_value_error_exact(self):
        r=self.value('मु॰',line=37,path='C:\\Sutram files\\नमूना.sm')
        self.assertEqual(r.returncode,1)
        self.assertEqual(r.stdout,"Sutram Error [E_ABBREVIATION_VALUE]: C:\\Sutram files\\नमूना.sm:37: abbreviation keyword is not a value: 'मु॰'\n".encode())
    def test_all_reviewed_signs_report_alias(self):
        for a in ('मु॰','મુ૰','মু৽','ਮੁ੶'):
            r=self.value(a);self.assertEqual(r.returncode,1);self.assertTrue(r.stdout.endswith(("'"+a+"'\n").encode()))
    def test_boolean_and_nonkeyword_are_left_to_parser(self):
        for kw in (21,22):
            r=self.value('मु॰',keyword=kw);self.assertEqual(r.returncode,0)
        for kind in (2,3,6):
            r=self.value('मु॰',kind=kind);self.assertEqual(r.returncode,0)
        self.assertEqual(self.value('mukhya').returncode,0)

class SourceTests(unittest.TestCase):
    def test_preserve_every_existing_pack_word(self):
        oldpacks=json.loads((ROOT/'tests/r68/baseline_packs.json').read_text())
        for name,base in oldpacks.items():
            now=(ROOT/'lang'/f'{name}.lang').read_text()
            for line in base['text'].splitlines():
                if line and not line.startswith('#'):self.assertIn(line+'\n',now)
            self.assertEqual(prep.git_blob(base['text'].encode()),base['git_blob'])
    def test_pack_aliases_and_no_invented_signs(self):
        for name in ('hindi','marathi'):
            s=(ROOT/'lang'/f'{name}.lang').read_text()
            for row in ('मु॰ mukhya','च॰ vitti','लि॰ likha','द॰ dasham'):self.assertIn(row,s)
        for name in ('odia','kannada','tamil','telugu'):
            base=json.loads((ROOT/'tests/r68/baseline_packs.json').read_text())[name]['text']
            get=lambda s:[x for x in s.splitlines() if x and not x.startswith('#')]
            self.assertEqual(get((ROOT/'lang'/f'{name}.lang').read_text()),get(base))
    def test_paired_new_examples(self):
        for name in ('odia','kannada','tamil','telugu','hindi','marathi'):
            p=ROOT/'examples/r68'/name;s=p.with_suffix('.sm').read_text()
            self.assertIn('।',s);self.assertIn('॥',s)
            self.assertEqual(p.with_suffix('.exit').read_bytes(),b'0\n')
            self.assertEqual(p.with_suffix('.out').read_bytes(),b'123456789\n2.500000\n')
    def test_pair_probe_exact_46_bytes(self):
        import re
        s=(ROOT/'examples/r68/pairs/all_registers.sm').read_text()
        b=[bytes.fromhex(v) for v in re.findall(r'nishkriya\("([^"]*)"\)',s)]
        self.assertEqual(len(b),15);self.assertEqual(sum(map(len,b)),46)
        self.assertNotIn(bytes.fromhex('54 5C'),b)
    def test_prepare_fixture_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);(root/'src').mkdir();(root/'src/sutram_compiler.asm').write_bytes(b'fixture, not real compiler')
            entry=(ROOT/'src/r68_compiler_entry.asm').read_bytes();(root/'src/r68_compiler_entry.asm').write_bytes(entry)
            pins={n:prep.git_blob((root/n).read_bytes()) for n in ('src/sutram_compiler.asm','src/r68_compiler_entry.asm')}
            out=root/'staged.asm';report=prep.stage(root,out,pins)
            self.assertEqual(out.read_bytes(),entry);self.assertIsNone(report['expanded_compiler_source_git_blob'])
            with self.assertRaises(FileExistsError):prep.stage(root,out,pins)
            with self.assertRaises(ValueError):prep.stage(root,root/'src/sutram_compiler.asm',pins)
    def test_unknown_pin_rejected_before_output(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);(root/'src').mkdir();(root/'src/sutram_compiler.asm').write_bytes(b'not real')
            with self.assertRaises(ValueError):prep.stage(root,root/'out',{'src/sutram_compiler.asm':prep.COMPILER_BLOB})
            self.assertFalse((root/'out').exists())
    def test_path_escape_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            for n in ('../outside','/etc/passwd'):
                with self.assertRaises(ValueError):prep.verify_inputs(Path(t),{n:'bad'})
    def test_wrapper_calls_only_compiler_host_checks(self):
        s=(ROOT/'src/r68_compiler_entry.asm').read_text()
        self.assertIn('%ifidni %1,lex',s);self.assertIn('%elifidni %1,parse_primary',s)
        self.assertIn('call r68_guard_value_start',s);self.assertIn('%unmacro call 1',s)
        self.assertNotIn('emit_byte',s)
    def test_lock_has_real_compiler_pin(self):
        pins=json.loads((ROOT/'tools/r68_review.lock.json').read_text())
        self.assertEqual(pins['src/sutram_compiler.asm'],prep.COMPILER_BLOB)
        for n,sha in pins.items():
            if n!='src/sutram_compiler.asm':self.assertEqual(prep.git_blob((ROOT/n).read_bytes()),sha,n)

if __name__=='__main__':unittest.main()
