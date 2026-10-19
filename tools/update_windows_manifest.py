"""Maintainer operation: review sources before explicitly updating this manifest."""
from pathlib import Path
import hashlib
ROOT=Path(__file__).resolve().parents[1]
manifest=ROOT/'windows/windows-build-integrity.sha256'
files=set()
for directory in ('src','lib','lang','examples','docs','icons','windows'):
    files.update(f for f in (ROOT/directory).rglob('*') if f.is_file() and '__pycache__' not in f.parts)
files.update(f for f in (ROOT/'win').iterdir() if f.suffix in ('.asm','.inc'))
files.update(ROOT/name for name in ('LICENSE.txt','README.md','tools/build_windows_runtime.py','tools/update_windows_manifest.py'))
files.discard(manifest)
rows=[hashlib.sha256(f.read_bytes()).hexdigest()+' *'+f.relative_to(ROOT).as_posix() for f in sorted(files)]
manifest.write_text('\n'.join(rows)+'\n',encoding='utf8',newline='\n')
print(f'MANIFEST_UPDATED {len(rows)} reviewed build/payload inputs')
