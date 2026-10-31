"""Relative links in tracked .md/.html files (backups/ excluded): print every one whose target does not exist."""
import re, subprocess, sys, os
from urllib.parse import unquote
ROOT = sys.argv[1]
files = subprocess.run(['git','-C',ROOT,'ls-files'],capture_output=True,text=True).stdout.split('\n')
files = [f for f in files if f and not f.startswith('backups/') and f.endswith(('.md','.html'))]
LINK = re.compile(r'\]\(\s*<?([^)\s>]+)>?(?:\s+"[^"]*")?\s*\)|href="([^"]+)"')
def targets(text):
    for m in LINK.finditer(text):
        t = m.group(1) or m.group(2)
        if re.match(r'^[a-z][a-z0-9+.-]*:', t, re.I) or t.startswith(('#','//')): continue
        p = unquote(t.split('#')[0].split('?')[0])
        if p: yield t, p
n = 0; broken = []
for f in files:
    try: text = open(os.path.join(ROOT,f),encoding='utf-8',errors='replace').read()
    except FileNotFoundError: continue
    for t,p in targets(text):
        n += 1
        full = os.path.normpath(os.path.join(ROOT, p.lstrip('/')) if p.startswith('/') else os.path.join(ROOT, os.path.dirname(f), p))
        if not os.path.exists(full): broken.append((f,t))
for f,t in broken: print(f'BROKEN {f} -> {t}')
print(f'{len(files)} files, {n} relative links, {len(broken)} broken')
