"""Every 'docs/NAME.md' path written in a tracked text file (backups/ excluded): print those that do not exist."""
import re, subprocess, sys, os
ROOT=sys.argv[1]; skip_ext=tuple(sys.argv[2].split(',')) if len(sys.argv)>2 else ()
files=[f for f in subprocess.run(['git','-C',ROOT,'ls-files'],capture_output=True,text=True).stdout.split('\n') if f and not f.startswith('backups/')]
pat=re.compile(r'(?<![\w/.-])docs/((?:[\w-]+/)*[\w.-]+\.md)\b')
miss={}; n=0
for f in files:
    if f.endswith(skip_ext): continue
    try: b=open(os.path.join(ROOT,f),'rb').read()
    except (FileNotFoundError, IsADirectoryError): continue
    if b'\0' in b[:4096]: continue
    for m in pat.finditer(b.decode('utf-8','replace')):
        n+=1
        if not os.path.exists(os.path.join(ROOT,'docs',m.group(1))): miss.setdefault(f,set()).add('docs/'+m.group(1))
for f in sorted(miss): print('MISSING', f, ' '.join(sorted(miss[f])))
print(f'{n} docs/*.md mentions, {sum(len(v) for v in miss.values())} distinct missing (file, path) pairs in {len(miss)} files')
