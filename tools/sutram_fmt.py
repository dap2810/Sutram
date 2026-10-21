#!/usr/bin/env python3
"""sutram-fmt: the Sutram source formatter (ROUND-17 WS3; asked for in ROUND-16).

    python3 -B tools/sutram_fmt.py FILE...            # print each file formatted
    python3 -B tools/sutram_fmt.py --write FILE...    # format in place
    python3 -B tools/sutram_fmt.py --check FILE...    # exit 1 and name the files that would change
    python3 -B tools/sutram_fmt.py --check --exclude-from tools/fmt-exclude.txt FILE...   # the gate
    python3 -B tools/sutram_fmt.py --diff FILE...     # show what would change
    python3 -B tools/sutram_fmt.py --verify FILE...   # prove: idempotent, and the same program
                                                      #   (compiles to the same bytes; --compiler C)

THE STYLE
  * four spaces per level of indentation; no tabs; no trailing spaces; one newline at
    the end; at most one blank line in a row, and none right after `{` or before `}`
  * K&R braces: `{` ends the line of its header (`yadi (x) {`, `prakriya f(a) {`,
    `mukhya() {`); `}` starts its own line; `} anya {` and `} yavat (c)` (after kuru)
    are one line
  * one space around binary operators and `=`, `+=` ...; none after unary `-` or `!`;
    none inside `( )` and `[ ]`; none before `,` `;` `।` `॥`; one after `,`
  * `yadi (`, `yavat (`, `prati (`: a keyword is followed by a space; a call (`f(x)`,
    `likha(x)`) and `mukhya()`, `abhava(...)`, `yantra(...)` have none
  * `.` and `?`/`:` of the ternary as in C; a `bhavana 1:` label keeps its colon tight
  * a line comment is indented like code; an inline comment gets two spaces before it;
    comment text, string text and block comments are never changed
  * a braceless body (`prakriya f(a)` then `prati a` on the next line; a braceless
    `mukhya()`) is indented one level; the braces are not added
  * everything else, in particular the order and the number of statements, line breaks
    between statements, and the words themselves, is kept exactly as written

WHY THIS STYLE
  It is the style the examples, the books and lib/ already use most, so formatting
  the tree moves the fewest lines; and it is C's, which every reader of a Sutram
  program has seen. The one choice that was open, braces on the header line or on
  their own, went to the header line because 660 of the tree's programs do that.

WHAT MAKES IT SAFE
  The formatter only moves whitespace and brace lines. The tokens of the program
  (names, numbers, strings, operators, comments) come out in the same order, so the
  compiler sees the same program. --verify proves it for a file: formatting twice
  gives the same bytes, and the compiled program is byte-for-byte the same binary.
  A file the formatter is unsure of (an unclosed string or block comment, mismatched
  braces) is left untouched and reported.

It needs Python 3 and nothing else. The compiler stays dependency-free; this is a
developer tool, like the test runners.
"""
from __future__ import annotations

import argparse
import difflib
import re
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]

# ------------------------------------------------------------------ the language
OPS3 = []
OPS2 = ['==', '!=', '<=', '>=', '<<', '>>', '&&', '||', '+=', '-=', '*=', '/=', '%=', '++', '--']
OPS1 = set('+-*/%<>=!&|^?:')
DELIMS = set('()[]{},;.')
DANDA = {'।', '॥'}        # । ॥ : statement terminators, like ;
CORE = {'mukhya', 'vitti', 'anka', 'yadi', 'yavat', 'prati', 'sankhya', 'anya', 'prakriya', 'yoj',
        'rachana', 'chakra', 'tak', 'sutra', 'abhava', 'krama', 'agrim', 'purna', 'shunya', 'satya',
        'ganana', 'guna', 'bhavana', 'mala', 'yantra', 'kuru', 'dasham', 'kosh', 'vibhag', 'siddhi', 'dosh', 'prasar'}
CALLLIKE_CORE = {'mukhya', 'yantra', 'abhava', 'siddhi', 'dosh'}   # R25: prati siddhi(v)     # keyword( ... ) written like a call
TOPLEVEL_CORE = {'prakriya', 'rachana', 'yoj', 'mukhya'}
HEADER_CORE = {'yadi', 'anya', 'yavat', 'chakra', 'kuru', 'guna', 'bhavana'}


def _load_words():
    """Every spelling of every keyword: the core words, and each pack's native words
    (lang/*.lang: `native sanskrit` per line). Returns (keywords, meaning)."""
    kw, meaning = set(CORE), {w: w for w in CORE}
    for p in sorted((ROOT / 'lang').glob('*.lang')):
        for line in p.read_text(encoding='utf-8').split('\n'):
            s = line.strip()
            if not s or s.startswith('#'):
                continue
            parts = s.split()
            if len(parts) == 2 and parts[1] in CORE:
                kw.add(parts[0]); meaning[parts[0]] = parts[1]
    return kw, meaning


KEYWORDS, MEANING = _load_words()


def mean(word: str) -> str:
    return MEANING.get(word, '')


# ------------------------------------------------------------------- tokenizer
# token kinds: 'nl', 'word', 'str', 'op', 'delim', 'danda', 'comment', 'bcomment'
class Unsure(Exception):
    pass


def _gap(text, i):
    """How many spaces stood before position i on its line (0 at the line start)."""
    j = i
    while j > 0 and text[j - 1] in ' \t':
        j -= 1
    return i - j if j > 0 and text[j - 1] != '\n' else 0


def tokenize(text: str):
    toks, i, n = [], 0, len(text)
    while i < n:
        c = text[i]
        if c == '\n':
            toks.append(('nl', '\n')); i += 1; continue
        if c in ' \t\r':
            i += 1; continue
        if c == '#' or text.startswith('//', i):
            j = text.find('\n', i)
            j = n if j < 0 else j
            toks.append(('comment', text[i:j].rstrip(), _gap(text, i))); i = j; continue
        if text.startswith('/*', i):
            j = text.find('*/', i + 2)
            if j < 0:
                raise Unsure('unclosed block comment')
            toks.append(('bcomment', text[i:j + 2], _gap(text, i))); i = j + 2; continue
        if c == '"':
            j = i + 1
            while j < n and text[j] != '"':
                if text[j] == '\\':
                    j += 1
                if j < n and text[j] == '\n':
                    raise Unsure('a string runs past the end of its line')
                j += 1
            if j >= n:
                raise Unsure('unclosed string')
            toks.append(('str', text[i:j + 1])); i = j + 1; continue
        if c in DANDA:
            toks.append(('danda', c)); i += 1; continue
        two = text[i:i + 2]
        if two in OPS2:
            toks.append(('op', two)); i += 2; continue
        if c in OPS1:
            toks.append(('op', c)); i += 1; continue
        if c in DELIMS:
            toks.append(('delim', c)); i += 1; continue
        # a word: everything up to the next space, operator, delimiter, quote or danda
        j = i
        while j < n and text[j] not in ' \t\r\n"#' and text[j] not in OPS1 and text[j] not in DELIMS \
                and text[j] not in DANDA and not text.startswith('//', j) and not text.startswith('/*', j):
            j += 1
        if j == i:
            raise Unsure('cannot read the character %r' % c)
        toks.append(('word', text[i:j])); i = j
    return toks


# ------------------------------------------------------------------- one line
def is_unary_context(prev):
    if prev is None:
        return True
    k, v = prev
    if k == 'op':
        return v not in ('++', '--')
    if k == 'delim':
        return v in '([{,;:?'
    if k == 'danda':
        return True
    if k == 'word':
        return v in KEYWORDS
    return False


def join_tokens(toks, raw_line=''):
    """Render one logical line's tokens (no 'nl') with the spacing rules."""
    out = []
    prev = None            # the previous code token
    prev_unary = False     # ... and whether it was a unary - or !
    label = bool(toks) and toks[0][0] == 'word' and mean(toks[0][1]) in ('bhavana', 'anya')
    if toks and toks[0][0] == 'word' and mean(toks[0][1]) == 'yoj' and toks[0][1] == 'yoj':
        return raw_line          # a module path is kept exactly as written
    after_comment = False
    brackets = []          # R23: one entry per open '[' / '(': [char, pending '?' count]
    after_slice = False    # R23: the token after a slice colon a[lo:hi] is tight
    for t in toks:
        k, v = t[0], t[1]
        if k in ('comment', 'bcomment'):
            # an inline comment keeps its column (at least two spaces before it)
            out.append((' ' * max(2, t[2]) if out else '') + v)
            after_comment = True
            continue
        unary = k == 'op' and v in ('-', '!') and is_unary_context(prev)
        if prev is None:
            sp = ' ' if after_comment else ''
        elif after_comment:
            sp = ' '
        else:
            pk, pv = prev
            sp = ' '
            if prev_unary:
                sp = ''                                   # -x, !x, - -x stays `- -x` below
                if k == 'op' and v in ('-', '!'):
                    sp = ' ' if (pv == v) else ''         # `- -x` must not become `--x`
            elif k == 'delim' and (v in ')],;' or v == '.'):
                sp = ''
            elif k == 'danda':
                sp = ''
            elif pk == 'delim' and (pv in '([' or pv == '.'):
                sp = ''
            elif k == 'delim' and v == '(':
                if pk == 'word':      # a call is tight; a keyword is followed by a space
                    sp = '' if pv not in KEYWORDS or mean(pv) in CALLLIKE_CORE else ' '
                elif pk == 'delim' and pv in ')]':
                    sp = ''                               # f(x)(y) does not occur; keep tight
            elif k == 'delim' and v == '[':
                if pk == 'word' and pv not in KEYWORDS or (pk == 'delim' and pv in ')]'):
                    sp = ''
            elif k == 'op' and v in ('++', '--'):
                sp = ''
            elif k == 'op' and v == ':' and label:
                sp = ''
                label = False
            elif k == 'op' and v == ':' and brackets and brackets[-1][0] == '[' and brackets[-1][1] == 0:
                sp = ''                                   # R23: a[lo:hi] is tight
            elif after_slice:
                sp = ''
        after_slice = False
        if k == 'delim' and v in '([':
            brackets.append([v, 0])
        elif k == 'delim' and v in ')]' and brackets:
            brackets.pop()
        elif v == '?' and brackets:
            brackets[-1][1] += 1
        elif k == 'op' and v == ':' and brackets:
            if brackets[-1][1]:
                brackets[-1][1] -= 1                      # the ':' of a ternary
            elif brackets[-1][0] == '[':
                after_slice = True
        out.append(sp + v)
        prev, prev_unary, after_comment = t, unary, False
    return ''.join(out)


# ------------------------------------------------------------------- the file
def format_text(text: str) -> str:
    toks = tokenize(text)
    raw = text.split('\n')
    # split into lines of tokens; each line remembers its source line (for yoj)
    lines, cur, ri = [], [], 0
    for t in toks:
        if t[0] == 'nl':
            lines.append((cur, raw[ri] if ri < len(raw) else '')); cur = []; ri += 1
        else:
            cur.append(t)
            if t[0] == 'bcomment':
                ri += t[1].count('\n')
    if cur:
        lines.append((cur, raw[ri] if ri < len(raw) else ''))
    rawof = {id(l): r for l, r in lines}
    lines = [l for l, _ in lines]

    # 1. brace lines: a lone `{` joins the previous code line; `}` + `anya ...` and
    #    `}` + `yavat (...)` closing a kuru join into one line
    merged = []
    stack = []            # the first word of each open block's header
    for ln in lines:
        code = [t for t in ln if t[0] not in ('comment', 'bcomment')]
        joined = False
        if code and code[0] == ('delim', '{') and len(code) == 1 and merged and \
                any(t[0] not in ('comment', 'bcomment') for t in merged[-1]) and \
                merged[-1][-1][0] not in ('comment', 'bcomment'):
            joined = True
        elif code and code[0][0] == 'word' and mean(code[0][1]) in ('anya', 'yavat') and merged and \
                merged[-1] and merged[-1][-1] == ('delim', '}') and \
                [t for t in merged[-1] if t[0] not in ('comment', 'bcomment')] == [('delim', '}')] and \
                (mean(code[0][1]) == 'anya' or (stack and stack[-1] == 'kuru-closed')):
            joined = True
        if stack and stack[-1] == 'kuru-closed':
            stack.pop()
        if joined:
            new = merged[-1] + ln
            rawof[id(new)] = rawof.get(id(merged[-1]), '')
            merged[-1] = new
        else:
            merged.append(ln)
        # track the open blocks, for the kuru ... } yavat rule
        head = [t for t in merged[-1] if t[0] not in ('comment', 'bcomment')]
        for t in code:
            if t == ('delim', '{'):
                stack.append(mean(head[0][1]) if head and head[0][0] == 'word' else '')
            elif t == ('delim', '}'):
                h = stack.pop() if stack else ''
                if h == 'kuru' and code == [('delim', '}')]:
                    stack.append('kuru-closed')
    lines = merged

    # 2. indentation
    out = []
    depth = 0
    paren = 0
    pending = 0           # braceless statement bodies waiting (yadi (c) \n stmt)
    body_mode = False     # inside a braceless mukhya / prakriya
    blank = 0
    last_was_open = False
    for ln in lines:
        code = [t for t in ln if t[0] not in ('comment', 'bcomment')]
        if not ln:
            blank += 1
            continue
        if ln[0][0] == 'bcomment' and '\n' in ln[0][1] and len(ln) == 1:
            # a multi-line block comment: keep it as written
            if blank and out and not last_was_open:
                out.append('')
            blank = 0
            out.append(ln[0][1]); last_was_open = False
            continue
        first = code[0] if code else None
        closes = first == ('delim', '}')
        top = first is not None and first[0] == 'word' and mean(first[1]) in TOPLEVEL_CORE
        if body_mode and top and depth == 0:
            body_mode = False
        d = depth - (1 if closes else 0)
        if body_mode and not top:
            d += 1
        if paren > 0:
            d += 1
        d += pending
        if blank and out and not last_was_open and not closes:
            out.append('')
        blank = 0
        if first is None:          # a comment-only line
            out.append('    ' * max(d, 0) + join_tokens(ln))
            last_was_open = False
            continue
        out.append('    ' * max(d, 0) + join_tokens(ln, rawof.get(id(ln), '').strip()))
        # update the state from this line's code
        for t in code:
            if t == ('delim', '{'): depth += 1
            elif t == ('delim', '}'): depth -= 1
            elif t[0] == 'delim' and t[1] in '([': paren += 1
            elif t[0] == 'delim' and t[1] in ')]': paren -= 1
        if depth < 0:
            raise Unsure('more } than {')
        ends_open = code[-1] == ('delim', '{')
        last_was_open = ends_open
        is_header = first[0] == 'word' and mean(first[1]) in HEADER_CORE
        is_func = first[0] == 'word' and mean(first[1]) in ('prakriya', 'mukhya')
        if ends_open or paren > 0:
            pending = 0
        elif is_func and not ends_open and depth == 0 and code[-1] != ('delim', ';'):
            body_mode = True; pending = 0
        elif is_header and ('delim', '{') not in code:
            pending += 1
        else:
            pending = 0
    if depth != 0:
        raise Unsure('more { than }')
    # 3. no blank line before a closing brace
    res = []
    for i, l in enumerate(out):
        if l == '' and i + 1 < len(out) and out[i + 1].lstrip().startswith('}'):
            continue
        res.append(l)
    return '\n'.join(res).rstrip('\n') + '\n'


# ------------------------------------------------------------------- commands
def fmt_file(path: Path):
    text = path.read_bytes().decode('utf-8')
    return text, format_text(text)


def _lang_map():
    """examples that need --lang, as tests/run_tests.py knows them."""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location('run_tests', ROOT / 'tests/run_tests.py')
        mod = importlib.util.module_from_spec(spec)
        saved, sys.argv = sys.argv, ['run_tests.py']
        try:
            spec.loader.exec_module(mod)
        finally:
            sys.argv = saved
        return getattr(mod, 'LANG', {})
    except Exception:
        return {}


def _compile(compiler, src: Path, cwd: Path, lang):
    exe = src.with_suffix('.fmtbin')
    exe.unlink(missing_ok=True)
    cmd = [compiler] + (['--lang', lang] if lang else []) + [str(src), str(exe)]
    r = subprocess.run(cmd, capture_output=True, cwd=str(cwd), timeout=60)
    data = exe.read_bytes() if exe.exists() else None
    exe.unlink(missing_ok=True)
    return r.returncode, data, r.stdout


def verify(paths, compiler: str) -> int:
    """For each file: formatting twice gives the same bytes, and the program compiles
    to the same binary before and after. A .sm is compiled where it lives (so yoj
    finds its modules) with the --lang tests/run_tests.py uses for it; a .smlib is
    compiled through `yoj <module>` in a private copy of lib/."""
    import shutil
    bad = 0
    langs = _lang_map()
    with tempfile.TemporaryDirectory() as td:
        for p in paths:
            try:
                before, after = fmt_file(p)
                again = format_text(after)
            except Unsure as e:
                print('UNSURE   %s: %s (left as it is)' % (p, e)); continue
            if again != after:
                print('FAIL     %s: not idempotent' % p); bad += 1; continue
            outs = []
            if p.suffix == '.smlib':
                for k, text in enumerate((before, after)):
                    tree = Path(td, 'lib%d' % k)
                    lib = tree / 'lib'
                    shutil.rmtree(tree, ignore_errors=True)
                    lib.mkdir(parents=True)
                    for d in (ROOT / 'examples/lib', ROOT / 'lib'):
                        for q in d.glob('*.smlib'):
                            shutil.copyfile(q, lib / q.name)
                    (lib / p.name).write_text(text, encoding='utf-8')
                    prog = tree / 'p.sm'
                    prog.write_text('yoj %s\nmukhya() {\n    likha(1)\n}\n' % p.stem, encoding='utf-8')
                    outs.append(_compile(compiler, prog, tree, None))
            else:
                for k, text in enumerate((before, after)):
                    tmp = p.parent / ('.fmt-verify-%d-%s' % (k, p.name))
                    tmp.write_text(text, encoding='utf-8')
                    try:
                        outs.append(_compile(compiler, tmp, ROOT, langs.get(p.stem)))
                    finally:
                        tmp.unlink(missing_ok=True)
            if outs[0][0] != outs[1][0]:
                print('FAIL     %s: compile status %d -> %d' % (p, outs[0][0], outs[1][0])); bad += 1; continue
            if outs[0][0] != 0:
                print('SAME-ERR %s: does not compile before or after (%s)' % (
                    p, outs[0][2].decode('utf-8', 'replace').strip().split('\n')[0][:60]))
                continue
            if outs[0][1] != outs[1][1]:
                print('FAIL     %s: the compiled bytes differ' % p); bad += 1; continue
            print('%s %s' % ('UNCHANGED' if before == after else 'OK       ', p))
    return bad


def main(argv):
    ap = argparse.ArgumentParser(description='sutram-fmt')
    ap.add_argument('files', nargs='+')
    g = ap.add_mutually_exclusive_group()
    g.add_argument('--write', action='store_true')
    g.add_argument('--check', action='store_true')
    g.add_argument('--diff', action='store_true')
    g.add_argument('--verify', action='store_true')
    ap.add_argument('--compiler', default=str(ROOT / 'sutram_compiler'))
    ap.add_argument('--exclude-from', metavar='FILE',
                    help='skip the files listed there (one path per line, # comments); for the gate')
    a = ap.parse_args(argv)
    paths = [Path(f) for f in a.files]
    if a.exclude_from:
        skip = {l.strip() for l in Path(a.exclude_from).read_text(encoding='utf-8').split('\n')
                if l.strip() and not l.startswith('#')}
        paths = [p for p in paths if str(p) not in skip and p.as_posix() not in skip]
    if a.verify:
        bad = verify(paths, str(Path(a.compiler).resolve()))
        return 1 if bad else 0
    changed = 0
    for p in paths:
        try:
            before, after = fmt_file(p)
        except Unsure as e:
            print('%s: left as it is: %s' % (p, e), file=sys.stderr)
            changed += 1
            continue
        if a.check:
            if before != after:
                print('would change: %s' % p); changed += 1
        elif a.diff:
            sys.stdout.writelines(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                                                       str(p), str(p) + ' (formatted)'))
        elif a.write:
            if before != after:
                p.write_text(after, encoding='utf-8'); changed += 1
                print('formatted: %s' % p)
        else:
            sys.stdout.write(after)
    return 1 if (a.check and changed) else 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
