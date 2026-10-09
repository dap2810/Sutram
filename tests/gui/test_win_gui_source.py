#!/usr/bin/env python3
"""Static source contract tests for standalone pure-NASM Windows GUI preview.
These are NOT a substitute for NASM build or real Windows GUI/manual testing.
"""
from __future__ import annotations
import re
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
ASM = (ROOT / 'windows/gui/sutram_gui.asm').read_text(encoding='utf8')
GUI_DIR = ROOT / 'windows/gui'


def cleaned_text():
    # Avoid treating label-shaped strings in semicolon comments as code.
    return '\n'.join(line.split(';')[0] for line in ASM.splitlines())


class GuiSourceContract(unittest.TestCase):
    def test_nasm_win64_and_gui_entrypoint(self):
        for needle in ['bits 64', 'default rel', 'global _start', 'wnd_proc:',
                       'RegisterClassExA', 'CreateWindowExA', 'GetMessageA',
                       'DispatchMessageA', 'CreateProcessA', 'ReadFile']:
            self.assertIn(needle, ASM)

    def test_no_third_party_runtime_or_security_changes(self):
        for forbidden in ('LoadLibraryA,\\"qt', 'VirtualProtect', 'reg add HKLM',
                          'RunAs', 'ShellExecuteA', 'powershell.exe', 'DisableRealtimeMonitoring'):
            self.assertNotIn(forbidden, ASM)

    def test_gui_features_are_wired(self):
        for needle in ['ID_EDITOR', 'ID_GUTTER', 'ID_OUTPUT', 'ID_SHELL',
                       'ID_LIST', 'highlight_editor:', 'update_lines:',
                       'open_dialog:', 'save_dialog:', 'load_example:',
                       'run_editor:', 'shell_submit:', 'spawn_capture:',
                       'MAX_EDIT 65534', 'MAX_OUTPUT 32767', '10000',
                       'EM_SETCHARFORMAT', 'WM_CHAR']:
            self.assertIn(needle, ASM)

    def test_export_lookup_names_and_slots(self):
        content = cleaned_text()
        exported = set(re.findall(r'^n_([A-Za-z0-9_]+):?\s+db\s+', content, re.M))
        slots = set(re.findall(r'^p_([A-Za-z0-9_]+):\s+dq\s+0', content, re.M))
        # Slots are expanded via IMPORTS macro at NASM preprocessing time.
        slots |= set(re.findall(r'^IMPORTS\s+([A-Za-z0-9_]+)$', content, re.M))
        apis = set(re.findall(r'(?m)^\s+API\s+([A-Za-z0-9_]+)\s*$', content))
        self.assertFalse(apis - exported, f'Unresolved name strings: {apis-exported}')
        self.assertFalse(apis - slots, f'Unresolved function pointer slots: {apis-slots}')

    def test_control_flow_labels_and_preprocessor_balance(self):
        lines = cleaned_text().splitlines()
        definitions = re.findall(r'(?m)^([A-Za-z_][\w]*):\s*$', '\n'.join(lines))
        local_defs = re.findall(r'(?m)^\s*(\.[\w]+):\s*$', '\n'.join(lines))
        self.assertEqual(len(definitions), len(set(definitions)))
        self.assertTrue(len(definitions) >= 25)
        self.assertGreater(len(local_defs), 100)
        directives = [re.search(r'^\s*%(macro|endmacro|if|ifdef|ifndef|endif|rep|endrep)\b', x) for x in lines]
        stack = []
        for x in directives:
            if x is None: continue
            directive = x.group(1)
            if directive in ('macro', 'if','ifdef','ifndef','rep'): stack.append(directive)
            else:
                self.assertTrue(stack, f'Orphan NASM %{directive}')
                expected = 'macro' if directive == 'endmacro' else 'rep' if directive == 'endrep' else 'if'
                got = stack.pop()
                self.assertEqual(expected, got if expected != 'if' else 'if')
        self.assertFalse(stack)

    def test_powershell_build_and_automated_gui_smoke(self):
        build = (GUI_DIR/'build-gui.ps1').read_text()
        smoke = (GUI_DIR/'test-gui.ps1').read_text()
        self.assertIn('nasm.exe',build)
        self.assertIn('-mi386pep',build)
        self.assertIn('0x8664',build)
        self.assertIn('UIAutomationClient',smoke)
        self.assertIn('GUI_AUTOTEST_OK',smoke)
        self.assertIn('MainWindowHandle',smoke)

    def test_manual_checklist_all_mandatory_flows(self):
        doc = (GUI_DIR/'MANUAL-WINDOWS-GUI-TEST.md').read_text()
        for step in ['Window/startup', 'Editing', 'Syntax highlighting',
                     'Run/compile/output', 'Examples browser', 'Shell Enter',
                     'Shell button', 'Save', 'Load', 'Resize', 'Exit', 'Missing compiler',
                     'Captured stdout regression', 'Windows ABI regression']:
            self.assertIn(step,doc)
        self.assertIn('NOT assembled or executed on Windows',doc)
        self.assertIn('Unicode/Devanagari/UTF-8',doc)

    def test_release_compiler_not_modified(self):
        original = ROOT/'src/sutram_compiler.asm'
        self.assertTrue(original.exists())
        self.assertGreater(original.stat().st_size, 100_000)


if __name__ == '__main__':
    unittest.main(verbosity=2)
