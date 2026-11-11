#!/usr/bin/env python3
"""The guard, in the tree: compile every program the ordinary way with two (tree, compiler) pairs and compare bytes.

    python3 tools/guard_pair.py OLD_TREE OLD_COMPILER NEW_TREE NEW_COMPILER OUT_DIR [--pe]

The programs are every examples/*.sm, examples/*/*.sm, tests/stdlib/*.sm, tests/r*/*.sm and tests/r*/*/*.sm of
NEW_TREE. Each is compiled from OLD_TREE by OLD_COMPILER and from NEW_TREE by NEW_COMPILER, with the tree as the
working directory (so `yoj` finds that tree's lib/), and the two outputs are compared byte for byte:

    IDENTICAL     both exited 0 and wrote the same bytes
    REFUSED-SAME  both exited 1 without output, with matching normalized stdout/stderr
    DIFFER        anything else - the line that matters
    NEW           the program does not exist in OLD_TREE

The last line is the count, e.g. `577 programs: 486 byte-identical, 91 refused identically, 0 DIFFER, 0 new`.
--pe names the outputs .exe (the Linux compiler then writes PE; a Windows compiler run under Wine writes PE anyway).
A compiler can be any executable, so a one-line wrapper runs win/sutram.exe under Wine.

To check a change yourself: `git worktree add /tmp/old <commit before>`, build or copy each tree's compiler, run
this once per output format, and expect 0 DIFFER wherever the change was meant to leave programs alone.
R58: this is the script behind every guard line in Claude-to-Sarvam/ since R44, now kept with the code.
Writes only to OUT_DIR. No network.
"""
import glob
import os
import shutil
import subprocess
import sys

PATTERNS = ['examples/*.sm', 'examples/*/*.sm', 'tests/stdlib/*.sm', 'tests/r*/*.sm', 'tests/r*/*/*.sm']


def compile_one(compiler, root, rel, out):
    try:
        result = subprocess.run([compiler, os.path.join(root, rel), out], cwd=root, capture_output=True,
                                timeout=60)
    except subprocess.TimeoutExpired:
        return 'timeout', None, None
    # Only invocation-dependent paths are normalized; diagnostic bytes otherwise matter.
    def normalize(data):
        return data.replace(os.fsencode(out), b'<OUTPUT>').replace(os.fsencode(root), b'<ROOT>')
    diagnostics = (normalize(result.stdout), normalize(result.stderr))
    output = None
    if os.path.isfile(out):
        with open(out, 'rb') as f:
            output = f.read()
    return result.returncode, output, diagnostics


def main(argv):
    if len(argv) < 5:
        print(__doc__)
        return 2
    old_root, old_c, new_root, new_c, out = map(os.path.abspath, argv[:5])
    ext = '.exe' if '--pe' in argv else ''
    rels = sorted({os.path.relpath(p, new_root) for pat in PATTERNS for p in glob.glob(os.path.join(new_root, pat))})
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    ident = refused = new = changed_src = 0
    differ = []
    for i, rel in enumerate(rels):
        if not os.path.exists(os.path.join(old_root, rel)):
            new += 1
            print(f'NEW          {rel}')
            continue
        with open(os.path.join(old_root, rel), 'rb') as old_source, open(os.path.join(new_root, rel), 'rb') as new_source:
            same_src = old_source.read() == new_source.read()
        changed_src += not same_src
        tag = '' if same_src else ' (source changed)'
        orc, od, om = compile_one(old_c, old_root, rel, f'{out}/{i}.old{ext}')
        nrc, nd, nm = compile_one(new_c, new_root, rel, f'{out}/{i}.new{ext}')
        if od is None and nd is None and orc == nrc == 1 and om == nm:
            refused += 1
            print(f'REFUSED-SAME {rel}{tag}')
        elif od is not None and od == nd and orc == nrc == 0:
            ident += 1
            print(f'IDENTICAL    {rel}{tag}')
        else:
            differ.append(rel)
            print(f'DIFFER       {rel}{tag} old rc={orc} new rc={nrc}')
    print(f'source files whose text changed: {changed_src}')
    print(f'{len(rels)} programs: {ident} byte-identical, {refused} refused identically, {len(differ)} DIFFER, {new} new')
    return 1 if differ else 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
