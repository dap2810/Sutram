#!/usr/bin/env python3
"""R167 WS5: what Claude-to-Sarvam/ holds, which files are byte-identical copies, and which no report cites.
Run from the repository root: python3 Claude-to-Sarvam/evidence-r167/footprint.py > .../footprint.txt
A file is CITED when a report (any tracked .md outside its own folder's listings) gives its path, or its
folder/name, or its name in a report that also names its folder. Else it is IN A CITED FOLDER when a report names
the folder (evidence-rN) as a whole. Else it is UNCITED. Lists of files (normalisation records, removal lists,
inventories) are not reports and do not count as citing."""
import collections, hashlib, os, re, subprocess, sys

CH = 'Claude-to-Sarvam/'
files = subprocess.run(['git', 'ls-files', '-z'], capture_output=True, check=True).stdout.decode().split('\0')[:-1]
size = {f: os.path.getsize(f) for f in files}
digest = {f: hashlib.sha256(open(f, 'rb').read()).hexdigest() for f in files}
reports = {f: open(f, encoding='utf-8', errors='replace').read() for f in files if f.endswith('.md')}
alltext = '\n'.join(reports.values())
mine = [f for f in files if f.startswith(CH)]
top = [f for f in mine if f.count('/') == 1]
ev = [f for f in mine if f.count('/') > 1]
by_digest = collections.defaultdict(list)
for f in files:
    by_digest[digest[f]].append(f)


def cited(f):
    folder, name = f.split('/')[1], os.path.basename(f)
    tail = '/'.join(f.split('/')[1:])
    if f in alltext or tail in alltext:
        return 'path'
    for t in reports.values():
        if name in t and folder in t:
            return 'name'
    return 'folder' if re.search(re.escape(folder) + r'(?![0-9A-Za-z])', alltext) else None


state = {f: cited(f) for f in ev}
print(f'Claude-to-Sarvam: {len(mine)} files, {sum(size[f] for f in mine)} bytes')
print(f'  reports at the top level: {len(top)} files, {sum(size[f] for f in top)} bytes')
print(f'  evidence: {len(ev)} files, {sum(size[f] for f in ev)} bytes')
for k, label in (('path', 'cited by path'), ('name', 'cited by name in a report that names its folder'),
                 ('folder', 'not named itself; its folder is named by a report'), (None, 'UNCITED: neither it nor its folder is named')):
    g = [f for f in ev if state[f] == k]
    print(f'    {label}: {len(g)} files, {sum(size[f] for f in g)} bytes')
copies_in = [f for f in ev if size[f] and any(o != f and o.startswith(CH) for o in by_digest[digest[f]])]
copies_out = [f for f in ev if size[f] and any(not o.startswith(CH) for o in by_digest[digest[f]])]
extra = sum(size[g[0]] * (len([x for x in g if x.startswith(CH)]) - 1) for g in by_digest.values()
            if size[g[0]] and len([x for x in g if x.startswith(CH)]) > 1)
print(f'byte-identical copies (empty files not counted):')
print(f'  evidence files sharing their bytes with another file in the channel: {len(copies_in)}; bytes in the extra copies: {extra}')
print(f'  evidence files sharing their bytes with a file outside the channel: {len(copies_out)}, {sum(size[f] for f in copies_out)} bytes')
for k, label in (('path', 'cited by path'), ('name', 'cited by name'), ('folder', 'only its folder is named'), (None, 'UNCITED')):
    g = [f for f in set(copies_in) | set(copies_out) if state[f] == k]
    print(f'    of the copies, {label}: {len(g)} files, {sum(size[f] for f in g)} bytes')
unc = [f for f in ev if state[f] is None]
print(f'UNCITED files ({len(unc)}):')
for f in sorted(unc):
    twin = [o for o in by_digest[digest[f]] if o != f]
    print(f'  {size[f]:8d}  {f}' + (f'   = {twin[0]}' if twin and size[f] else ''))
empty = [f for f in ev if size[f] == 0]
print(f'empty files: {len(empty)}')
