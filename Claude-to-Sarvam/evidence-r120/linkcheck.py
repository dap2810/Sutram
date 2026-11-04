#!/usr/bin/env python3
"""R120: every relative link in every tracked .md / .html file -> does its target exist in the working tree?
Markdown [text](target) and HTML href= / src= ; http(s), mailto, #anchors and javascript: are skipped; a link's
#fragment and ?query are dropped. Prints each broken link as  file: target  and a summary line."""
import os, re, subprocess, sys, urllib.parse
ROOT = sys.argv[1] if len(sys.argv) > 1 else '.'
os.chdir(ROOT)
files = [f for f in subprocess.run(['git', 'ls-files', '-z'], capture_output=True).stdout.decode().split('\0')
         if f.endswith(('.md', '.html')) and os.path.isfile(f)]
MD = re.compile(r'\[[^\]\n]*\]\(([^)\s]+)(?:\s+"[^"]*")?\)')
HT = re.compile(r'(?:href|src)\s*=\s*["\']([^"\']+)["\']', re.I)
links = broken = 0
for f in sorted(files):
    t = open(f, encoding='utf-8', errors='ignore').read()
    for m in list(MD.finditer(t)) + list(HT.finditer(t)):
        tgt = m.group(1).strip('<>')
        if re.match(r'^(https?:|mailto:|#|javascript:|data:|ftp:|file:|\{|\$)', tgt, re.I):
            continue
        path = urllib.parse.unquote(tgt.split('#')[0].split('?')[0])
        if not path:
            continue
        links += 1
        full = os.path.normpath(os.path.join(os.path.dirname(f), path)) if not path.startswith('/') else path.lstrip('/')
        if not os.path.exists(full):
            broken += 1
            print(f'{f}: {tgt}')
print(f'linkcheck: {len(files)} files, {links} relative links, {broken} broken')
