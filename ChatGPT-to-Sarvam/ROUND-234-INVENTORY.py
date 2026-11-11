"""Read-only R234 inventories: source branch density and token-level input callers.
No assembly, compiler execution or repository mutation. Writes JSON to stdout.
Usage: python3 ChatGPT-to-Sarvam/ROUND-234-INVENTORY.py ROOT
"""
import collections
import glob
import json
from pathlib import Path
import re
import sys


def sm_tokens(text):
    # Keep line locations, excluding quoted strings and all three comment forms.
    pattern = r'/\*.*?\*/|//[^\n]*|\#[^\n]*|"(?:\\.|[^"\\])*"|\w+|[^\s]'
    result = []
    for m in re.finditer(pattern, text, re.S):
        token = m.group()
        if token.startswith(('/*', '//', '#', '"')):
            continue
        result.append((token, text.count('\n', 0, m.start()) + 1))
    return result


def inventory(root):
    root = Path(root)
    names = {'grahan'}
    for path in (root / 'lang').glob('*.lang'):
        for line in path.read_text().splitlines():
            parts = line.split()
            if len(parts) == 2 and parts[1] == 'grahan':
                names.add(parts[0])
    patterns = ['examples/*.sm', 'examples/*/*.sm', 'tests/stdlib/*.sm', 'tests/r*/*.sm', 'tests/r*/*/*.sm']
    paths = sorted({Path(p) for pat in patterns for p in glob.glob(str(root / pat))})
    callers = []
    for path in paths:
        tokens = sm_tokens(path.read_text())
        lines = [line for (name, line), (following, _) in zip(tokens, tokens[1:]) if name in names and following == '(']
        if lines:
            callers.append({'path':str(path.relative_to(root)), 'lines':lines})
    routines = []
    for path in sorted((root / 'src').rglob('*')):
        if path.suffix not in ('.asm', '.inc'):
            continue
        current = None
        def finish(end):
            if current and current['instructions']:
                current['end_line'] = end
                routines.append(dict(current))
        lines = path.read_text().splitlines()
        for no, line in enumerate(lines, 1):
            line = line.split(';', 1)[0].strip()
            m = re.match(r'^([A-Za-z_][\w$]*)\s*:\s*(.*)', line)
            if m:
                finish(no - 1)
                current = {'path':str(path.relative_to(root)), 'label':m[1], 'start_line':no,
                           'instructions':0,'conditional_jumps':0,'unconditional_jumps':0,'calls':0,'returns':0}
                line = m[2]
            if re.match(r'^(?:section|segment)\b', line, re.I):
                finish(no-1); current = None
            if not current:
                continue
            line = re.sub(r'^\.[\w.]+:\s*', '', line)
            op = line.split()[0].lower() if line else ''
            if re.fullmatch(r'j(?!mp)\w+|loop(?:e|ne|z|nz)?', op):
                current['conditional_jumps'] += 1
            if op == 'jmp': current['unconditional_jumps'] += 1
            if op == 'call': current['calls'] += 1
            if op in ('ret', 'retf'): current['returns'] += 1
            if re.fullmatch(r'mov\w*|lea|push|pop|call|ret|retf|j\w+|loop\w*|cmp|test|add|sub|imul|mul|idiv|div|xor|and|or|inc|dec|sh\w+|sa\w+|set\w+|cmov\w+|syscall|nop|cld|rep|repe|repne|stos\w*|lods\w*|leave|neg|not|cqo|cdq|xchg|bt|bts|btr', op):
                current['instructions'] += 1
        finish(len(lines))
    routines.sort(key=lambda r:(-r['conditional_jumps'],-r['unconditional_jumps'],r['path'],r['start_line']))
    return {'guard_programs':len(paths),'top_level_examples':len(list((root/'examples').glob('*.sm'))),
            'aliases':sorted(names),'input_callers':callers,'call_sites':sum(len(c['lines']) for c in callers),
            'routine_metric':'conditional jump instructions per non-local labelled source block; excludes macro expansion, includes conditional-assembly alternatives; not cyclomatic complexity',
            'routine_blocks':len(routines),'top_ten':routines[:10]}


if __name__ == '__main__':
    print(json.dumps(inventory(sys.argv[1]),ensure_ascii=False,indent=2))
