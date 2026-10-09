#!/usr/bin/env python3
"""R39 independent language-pack and static source-contract tests.

The lexical oracle below is DEVELOPMENT-ONLY Python: it does NOT execute the
Win64 NASM highlighter or establish Windows GUI runtime acceptance.
"""
import re
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
ASM=(ROOT/'windows/gui/sutram_gui.asm').read_text(encoding='utf-8')
MANUAL=(ROOT/'windows/gui/MANUAL-WINDOWS-GUI-TEST.md').read_text(encoding='utf-8')
BUILD=(ROOT/'windows/native-installer/build-installer.ps1').read_text(encoding='utf-8')
PACKS=('bengali','gujarati','hindi','kannada','malayalam','marathi','odia','punjabi','tamil','telugu')


def keywords():
    mapping={}
    for lang in PACKS:
        text=(ROOT/'lang'/f'{lang}.lang').read_text(encoding='utf-8')
        words={}
        for line in text.splitlines():
            line=line.strip()
            if not line or line.startswith('#'): continue
            cols=line.split()
            if len(cols)<2: raise AssertionError((lang,line))
            native,latin=cols[:2]
            if native in words: raise AssertionError(('duplicate',lang,native))
            words[native]=latin
        mapping[lang]=words
    return mapping


def reference_lex(code,words):
    """Independent reference lexer for expected highlighting; no NASM calls."""
    identifiers=lambda c: c=='_' or c.isalpha() or c.isdigit() or c in '\u200c\u200d' or '\u0900' <= c <= '\u0dff'
    colored=[]
    i=0
    while i<len(code):
        ch=code[i]
        if ch in "\"'":
            quote=ch;i+=1
            while i<len(code):
                if code[i]=='\\': i+=min(2,len(code)-i)
                elif code[i]==quote: i+=1;break
                else: i+=1
            continue
        if ch=='#' or code.startswith('//',i):
            j=code.find('\n',i)
            i=len(code) if j<0 else j
            continue
        if identifiers(ch) and (i==0 or not identifiers(code[i-1])):
            found=None
            for keyword in words:
                end=i+len(keyword)
                if code.startswith(keyword,i) and (end>=len(code) or not identifiers(code[end])):
                    found=keyword
                    break
            if found:
                colored.append(found)
                i+=len(found)
                continue
        i+=1
    return colored


class NativeLanguagePackContract(unittest.TestCase):
    def test_all_ten_source_packs_have_native_tokens(self):
        packs=keywords()
        self.assertEqual(set(packs),set(PACKS))
        self.assertGreater(sum(len(x) for x in packs.values()),250)
        self.assertEqual(packs['hindi']['मुख्य'],'mukhya')
        self.assertEqual(packs['tamil']['முதன்மை'],'mukhya')
        self.assertEqual(packs['gujarati']['મુખ્ય'],'mukhya')

    def test_startup_loads_every_pack_using_unicode_api(self):
        for lang in PACKS:
            self.assertIn('kw_pack_'+lang+'_w:',ASM)
        self.assertIn('call load_native_keyword_packs\n    call gui_loop',ASM)
        self.assertIn('API CreateFileW',ASM)
        self.assertIn('API ReadFile',ASM)
        self.assertIn('call utf8_to_utf16',ASM)
        self.assertIn('native_keyword_storage resw MAX_NATIVE_KEYWORDS*NATIVE_KEYWORD_UNITS',ASM)
        self.assertIn('cmp ecx,254',ASM)
        self.assertIn('MAX_NATIVE_KEYWORDS 384',ASM)
        self.assertIn('MAX_LANG_FILE 8191',ASM)

    def test_script_lexer_scans_full_utf16_units_and_handles_boundaries(self):
        section=ASM[ASM.index('highlight_editor:'):ASM.index('is_ident_byte:')]
        self.assertIn('call native_keyword_match',section)
        self.assertIn('call is_ident_u16',section)
        self.assertIn('cmp dx,127',section)
        self.assertIn('test dx,dx',section)
        self.assertIn("cmp dx,'#'",section)
        self.assertIn("cmp dx,'/'",section)
        self.assertIn('cmp ax,[r10+rcx*2]',section)
        self.assertIn('EM_SETCHARFORMAT',section)
        self.assertIn('SCF_SELECTION',section)
        self.assertIn('ch_start',section)
        self.assertIn('ch_end',section)
        self.assertIn('kw_words',section)

    def test_hindi_tamil_and_latin_reference_lexer(self):
        packs=keywords()
        native=set(packs['hindi'])|set(packs['tamil'])
        native|={'mukhya','likha'}
        src='''मुख्य() { लिखो(1) }\nமுதன்மை() { எழுது(2) }\nmukhya() { likha(3) }\n"मुख्य लिखो முதன்மை எழுது"\n# मुख्य எழுது\n// முதன்மை लिखो\n'''
        self.assertEqual(reference_lex(src,native),['मुख्य','लिखो','முதன்மை','எழுது','mukhya','likha'])

    def test_reference_lex_prevents_substring_false_positives(self):
        packs=keywords()
        native=set(packs['hindi'])|set(packs['tamil'])
        native|={'mukhya'}
        self.assertEqual(reference_lex('मुख्यxyz abcஎழுது முதன்மைfoo mukhyaदेव',native),[])
        self.assertEqual(reference_lex('मुख्य; எழுது; mukhya',native),['मुख्य','எழுது','mukhya'])

    def test_installer_includes_lang_directory_and_missing_pack_warning(self):
        self.assertRegex(BUILD,r"\('lang','examples','docs'\)")
        self.assertIn('msg_missing_lang db',ASM)
        self.assertIn('msg_partial_lang db',ASM)
        self.assertIn('native_pack_errors',ASM)
        self.assertIn('native_pack_count',ASM)
        self.assertIn('MAX_NATIVE_KEYWORDS',ASM)

    def test_manual_windows_checklist_covers_real_script_cases(self):
        for needle in ['25. **Hindi/Devanagari pack**','26. **Tamil pack**',
                       '27. **Mixed-script/Latin boundary','28. **Missing pack diagnostics**',
                       '30. **Installed copy**','FAIL:', 'मुख्य', 'எழுது']:
            self.assertIn(needle,MANUAL)
        self.assertIn('not executed on Windows',MANUAL)

    def test_compiler_and_terminal_ide_paths_untouched(self):
        self.assertTrue((ROOT/'src/sutram_compiler.asm').is_file())
        self.assertTrue((ROOT/'ide/sutram_ide.asm').is_file())

if __name__=='__main__': unittest.main()
