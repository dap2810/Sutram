"""Run in a hidden dedicated console; changes only that test console's code page."""
from pathlib import Path
import ctypes,subprocess
k=ctypes.windll.kernel32
k.SetErrorMode(0x8003)
original=k.GetConsoleOutputCP()
if not original:raise RuntimeError('This test requires its own dedicated console')
r=Path(__file__).resolve().parents[1]
try:
    assert k.SetConsoleOutputCP(437)
    host=subprocess.run([str(r/'win/sutram.exe'),'--version'],capture_output=True,timeout=8)
    assert host.returncode==0 and b'\xe2\x80\x94' in host.stdout
    assert k.GetConsoleOutputCP()==437
    print('PASS compiler UTF-8 em dash; test console page restored to 437')
    app=subprocess.run([str(r/'build/windows/acceptance/218_sanskrit_devanagari.exe')],capture_output=True,timeout=8)
    expected=(r/'tests/expect/218_sanskrit_devanagari.out').read_text(encoding='utf8')
    assert app.returncode==0 and app.stdout.decode('utf8')==expected
    assert k.GetConsoleOutputCP()==437
    print('PASS generated Sanskrit UTF-8 output; test console page restored to 437')
finally:
    k.SetConsoleOutputCP(original)
