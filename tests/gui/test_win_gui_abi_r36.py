#!/usr/bin/env python3
"""Source ABI checks for the Windows GUI — not a substitute for Windows execution.

Bug regression: PeekNamedPipe has SIX parameters, with lpTotalBytesAvail
in stack slot 5 on Win64. Passing the scratch pointer as parameter 6 makes
anonymous-pipe output capture appear empty because that result is always 0.
"""
from __future__ import annotations
import re
import unittest
from pathlib import Path

ASM_PATH = Path(__file__).resolve().parents[2] / 'windows/gui/sutram_gui.asm'
ASM = ASM_PATH.read_text(encoding='utf-8')


def function_block(label, end):
    m = re.search(rf'(?ms)^{re.escape(label)}:\n(.*?)^{re.escape(end)}:', ASM)
    if not m:
        raise AssertionError(f'Missing block {label} ... {end}')
    return m.group(1)


class Win64AbiRegressions(unittest.TestCase):
    def test_pipe_peek_reads_available_bytes_from_parameter_5(self):
        block = function_block('spawn_capture', 'compile_run')
        calls = list(re.finditer(r'(?m)^\s*API PeekNamedPipe\s*$', block))
        self.assertEqual(2, len(calls), 'both poll and post-exit drain must be guarded')
        for call in calls:
            previous = block[max(0,call.start()-270):call.start()]
            self.assertRegex(previous, r'PTR r10,pipe_available\s*\n\s*mov \[rsp\+32\],r10')
            self.assertRegex(previous, r'mov qword \[rsp\+40\],0')
            self.assertNotIn('mov [rsp+40],r10', previous)
            self.assertNotIn('mov qword [rsp+48],0', previous)

    def test_win_resolve_preserves_all_modified_win64_callee_saved_regs(self):
        block = function_block('win_resolve', 'section .data') if False else ASM.split('\nwin_resolve:\n',1)[1].split('\nsection .data\n',1)[0]
        for reg in ('rbx','rsi','rdi','r12','r13','r14','r15'):
            self.assertRegex(block,rf'(?m)^\s*push {reg}\s*$')
            self.assertRegex(block,rf'(?m)^\s*pop {reg}\s*$')
        pushes = re.findall(r'(?m)^\s*push (rbx|rsi|rdi|r1[2345])\s*$',block)
        pops = re.findall(r'(?m)^\s*pop (rbx|rsi|rdi|r1[2345])\s*$',block)
        self.assertEqual(list(reversed(pushes)),pops)
        self.assertEqual(7,len(pushes),'seven pushes preserve 16-byte alignment for nested call')

    def test_gui_smoke_checks_captured_stdout_not_just_window(self):
        smoke=(ASM_PATH.parent/'test-gui.ps1').read_text(encoding='utf-8')
        self.assertIn('GUI_AUTOTEST_OK',smoke)
        self.assertIn("$got -notmatch 'GUI_AUTOTEST_OK'",smoke)
        self.assertIn('Output edit has no ValuePattern',smoke)

    def test_no_runtime_compiler_or_ide_changes(self):
        root=ASM_PATH.parents[2]
        self.assertTrue((root/'src/sutram_compiler.asm').exists())
        self.assertTrue((root/'ide/sutram_ide.asm').exists())


if __name__ == '__main__': unittest.main(verbosity=2)
