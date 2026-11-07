from pathlib import Path
import hashlib,json,shutil,subprocess,sys,platform
root=Path(__file__).resolve().parents[2];work=root/'build/fixes';out=root/'Windows-to-Sarvam/win-v307-fixes-2026-11-06'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def copy(src,dst):
    dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
for source,dest in [('release-oom','oom'),('release-commit-oom','oom-controls'),('verified-slices','slices'),('linux-final','linux-final'),('linux','linux-first')]:
    for p in (work/source).rglob('*'):
        if p.is_file() and (p.suffix in ['.json','.log','.sm'] or p.name in ['stdout','stderr']):copy(p,out/dest/p.relative_to(work/source))
for source in ['installer-io.json','fixture-repair.json','payload-differences.json']:
    copy(work/source,out/source)
copy(work/'verified-native/native-cases.json',out/'native-cases.json')
for name in ['prepare-native.ps1','restore-native.ps1','retry-normalized.ps1','complete-native.ps1','linux-checks.py','linux-followup.py','check-payload-lines.py','collect-evidence.py']:
    copy(work/name,out/'reproduction'/name)
for args in [['tests/r133/test_installer_recovery.py'],['tests/r130/test_installer_engine.py'],['tools/check_installer_version.py']]:
    p=subprocess.run([sys.executable,*args],cwd=root,capture_output=True,timeout=40)
    (out/(Path(args[0]).stem+'.log')).write_bytes(p.stdout+p.stderr)
    assert p.returncode==0,(args,p.returncode)
stage=root/'build/windows/setup-b065f2d784f94c21adb7a03dd51645d6/payload'
copy(stage/'payload.manifest.sha256',out/'candidate-payload.manifest.sha256')
copy(root/'Sutram-Setup.exe',work/'review-Sutram-Setup.exe')
sources=['.gitattributes','src/sutram_compiler.asm','win/pe_layout.inc','win/pe_imports.inc','win/winrt_blob.asm','win/rtblob.inc','windows/native-installer/install-core.ps1','windows/native-installer/build-installer.ps1']
data=dict(base_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),python=sys.executable,python_version=sys.version,platform=platform.platform(),
          artifacts={str(p.relative_to(root)):sha(p) for p in [work/'candidate.exe',work/'baseline.exe',work/'review-Sutram-Setup.exe',work/'linux/candidate/sutram_compiler',work/'linux/baseline/sutram_compiler']},
          sources={name:sha(root/name) for name in sources},runtime_import_bytes=1024,release_version_unchanged='1.0 (v307)',frozen_goldens_changed=False)
(out/'build-identity.json').write_text(json.dumps(data,indent=2)+'\n')
# Preserve review artifacts in build/, then return tracked release binaries to
# their exact base commit bytes. No release binary or pin is updated by this PR.
for name in ['Sutram-Setup.exe','Sutram-Setup.sha256','sutram.exe','win/sutram.exe']:
    (root/name).write_bytes(subprocess.check_output(['git','show','HEAD:'+name],cwd=root))
print(json.dumps(data,indent=2))
