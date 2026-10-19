"""Verify the real staged payload without entering installation code."""
from pathlib import Path
import os,subprocess,ctypes,uuid
ctypes.windll.kernel32.SetErrorMode(0x8003)
ROOT=Path(__file__).resolve().parents[1]
work=ROOT/'build/windows'/('verify-'+uuid.uuid4().hex);work.mkdir(parents=True)
env=os.environ.copy();env['TEMP']=env['TMP']=str(work);env['LOCALAPPDATA']=str(work/'local')
install=work/'local/Programs/Sutram'
packages=sorted((ROOT/'build/windows').glob('setup-*/payload.zip'),key=lambda p:p.stat().st_mtime)
log=work/'verify-only.log'
cmd=['powershell.exe','-NoProfile','-File',str(ROOT/'windows/native-installer/install-core.ps1'),'-PayloadZip',str(packages[-1]),'-InstallDir',str(install),'-SetupExePath',str(ROOT/'Sutram-Setup.exe'),'-LogPath',str(log),'-VerifyOnly']
x=subprocess.run(cmd,env=env,cwd=ROOT,capture_output=True,timeout=90)
print('$ '+' '.join(cmd))
print((x.stdout+x.stderr).decode('utf8','replace'))
if log.exists():print(log.read_text(encoding='utf-8-sig'))
print('EXIT',x.returncode)
assert x.returncode==0
assert not install.exists()
assert not list(work.glob('Sutram-Payload-*'))
print('PAYLOAD_VERIFY_ONLY_PASS: no installation tree created; extraction stage cleaned')
