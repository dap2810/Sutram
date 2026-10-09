"""Source checks, not a substitute for NASM/Windows runtime acceptance."""
from pathlib import Path
import unittest

R=Path(__file__).resolve().parents[2]
G=(R/'windows/gui/sutram_gui.asm').read_text(encoding='utf-8')
B=(R/'windows/native-installer/build-installer.ps1').read_text(encoding='utf-8')
I=(R/'windows/native-installer/install-core.ps1').read_text(encoding='utf-8')
U=(R/'windows/native-installer/uninstall-core.ps1').read_text(encoding='utf-8')

class UnicodeInstallerContract(unittest.TestCase):
    def test_strict_utf8_bridge(self):
        self.assertIn('utf8_to_utf16:',G)
        self.assertIn('utf16_to_utf8:',G)
        self.assertIn('MB_ERR_INVALID_CHARS',G)
        for marker in ['mov edx,8', 'mov edx,0x80','API MultiByteToWideChar','API WideCharToMultiByte']:
            self.assertIn(marker,G)

    def test_editor_wide_text_and_utf8_disk(self):
        self.assertIn('editor_read_utf8:',G)
        self.assertIn('editor_set_utf8:',G)
        for api in ['API GetWindowTextW','API SetWindowTextW','API CreateFileW']:
            self.assertIn(api,G)
        for method in ['load_file:','save_file:','run_editor:']:
            self.assertIn(method,G)
        self.assertIn('API GetOpenFileNameW',G)
        self.assertIn('API GetSaveFileNameW',G)
        self.assertIn('file_filter_w:',G)

    def test_unicode_temp_paths_and_program_launch(self):
        for api in ['API GetTempPathW','API GetTempFileNameW','API GetModuleFileNameW',
                    'API SetCurrentDirectoryW','API CreateProcessW','API DeleteFileW']:
            self.assertIn(api,G)
        self.assertIn('wide_command_concat:',G)
        self.assertIn('wide_string_copy:',G)
        self.assertIn('wide_string_concat:',G)

    def test_syntax_highlight_utf16_offsets(self):
        text=G[G.index('highlight_editor:'):G.index('utf8_to_utf16:')]
        self.assertIn('PTR r10,editor_utf16',text)
        self.assertIn('cmp ax,[r10+rcx*2]',text)
        self.assertIn('add qword [rbp-16],2',text)
        self.assertIn('EM_SETCHARFORMAT',text)
        self.assertNotIn('API GetWindowTextA',text)

    def test_shell_unicode_input_and_utf8_output(self):
        self.assertIn('PTR rdx,shell_input\n    mov r8d,4096\n    call utf16_to_utf8',G)
        self.assertIn('API SendMessageW',G)
        self.assertIn('output_utf16 resw 32768',G)

    def test_installer_packages_both_gui_and_compiler_layout(self):
        self.assertIn("Join-Path $Root 'sutram-ide-gui.exe'",B)
        self.assertIn(r"$PayloadStage 'win\sutram.exe'",B)
        self.assertIn("$PayloadStage 'sutram-ide-gui.exe'",B)
        self.assertIn('Assert-Pe64 $guiExe',B)
        self.assertIn(r"$stage 'win\sutram.exe'",I)

    def test_installer_user_shortcut_and_app_registry(self):
        self.assertIn('Sutram IDE.lnk',I)
        self.assertIn('Sutram IDE.lnk',U)
        self.assertIn('HKCU:',I)
        self.assertIn('HKCU:',U)
        self.assertIn('LOCALAPPDATA',I)
        self.assertNotIn('HKLM:',I)
        self.assertNotIn('HKLM:',U)

    def test_new_icon_selected_by_filename_not_hardcoded_old_pixels(self):
        self.assertIn('gui_icon_w:',G)
        self.assertIn('WM_SETICON',G)
        self.assertIn('LoadImageW',G)
        self.assertIn(r"$Here 'assets\sutram.ico'",B)

if __name__=='__main__': unittest.main()
