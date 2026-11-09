#!/usr/bin/env python3
"""R158 (Sarvam ROUND-158): doc currency is a gate, not a habit.

The owner's standing instruction: "The docs should be up to date as we progress." Six checks, each specific
enough to fail, over the documents a reader is told to use today (CURRENT, below). Historical records -
docs/CHANGELOG.md's older entries, docs/rounds/, the round folders, the paused-language books - may name old
versions; they are not read except where a check says so.

  1  versions   - each current document's status line names the compiler's version; no book heading or contents
                  entry names any other version ("14. New Features: v22"); each paused-language book says which
                  version it describes
  2  symbols    - every compiler-style symbol (`r142_gen_expr_body`) a current document cites in code is defined -
                  a label in src/, a file in the tree, or a prakriya in lib/ or examples/lib/ - and every E_ code it
                  names occurs in src/, lang/ or lib/
  3  examples   - every complete program (a <pre> containing mukhya) in the English and Sanskrit books compiles
                  on this compiler and runs to exit 0; one marked data-expect="E_CODE" must be refused with that
                  code, one marked data-exit="N" must exit N
  4  commands   - every compiler flag a current document shows on a compiler command line, or alone in code, is
                  one the compiler knows; the forms with a value (--analysis-steps=N, --lang X) are run as written
                  and must be accepted. Only the compiler is run - no other command from a document is executed
  5  memory     - the English and Sanskrit books have the memory chapter (id="memory") and it covers ROUND-157's
                  seven topics
  6  changelog  - docs/CHANGELOG.md has an entry for every version from its oldest kept entry to the current one,
                  each naming who and the round: "## vNNN (Who, RNNN)"

What it cannot check (ROUND-158 WS3): that a paragraph is still true. A version number and a symbol can be
found; a false sentence cannot. Read the narrative.

Each check is first run on fixtures made to fail (and on ones made to pass), so a check that cannot fail is
itself a failure (`self-test`).

Usage: python3 tests/r158/test_doc_currency.py [--compiler PATH] [--root DIR]
"""
import glob, html, os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))

CURRENT = ['README.md', 'PROJECT-MASTER.md', 'AGENTS.md', 'INSTALL-WINDOWS.md', 'ROADMAP.md',
           'docs/LANGUAGE-REFERENCE.md', 'docs/RELEASE-NOTES.md', 'docs/PATH-TO-COMPLETION.md',
           'docs/MEMORY-MODEL.md', 'docs/INSTALLER-REBUILD.md', 'docs/WINDOWS-SETUP.md',
           'docs/INSTALLATION-ROUTES.md', 'docs/BUILDING.md', 'docs/SANDESH.md', 'docs/ERROR-CONVENTION.md',
           'docs/LIBRARY-BOUNDARY.md', 'docs/NUMERIC-CONTRACT.md', 'docs/OVERFLOW-SAFETY.md',
           'docs/sutram-book-english.html', 'docs/sutram-book-sanskrit.html']
BOOKS = ['docs/sutram-book-english.html', 'docs/sutram-book-sanskrit.html']
PAUSED_BOOKS = ['docs/sutram-book-hindi.html', 'docs/sutram-book-tamil.html', 'docs/sutram-book-telugu.html',
                'docs/sutram-book-gujarati.html']
# the status lines that must name the current version: (document, the pattern whose group 1 is the version)
STATUS = [('PROJECT-MASTER.md', r'\*\*Status at compiler v(\d+)'),
          ('docs/PATH-TO-COMPLETION.md', r'\*\*Status at compiler v(\d+)'),
          ('docs/LANGUAGE-REFERENCE.md', r'\*\*Status at compiler v(\d+)'),
          ('docs/MEMORY-MODEL.md', r'\*\*Status at compiler v(\d+)'),
          ('docs/RELEASE-NOTES.md', r'^# Sutram \d+\.\d+ \(v(\d+)\)'),
          ('docs/sutram-book-english.html', r'class="footer">[^<]*\(compiler v(\d+)\)'),
          ('docs/sutram-book-sanskrit.html', r'class="footer">[^<]*\(compiler v(\d+)\)')]
COMPILER_NAMES = ('sutram', 'sutram_compiler', './sutram_compiler', 'sutram.exe', r'win\sutram.exe',
                  'win/sutram.exe', r'.\sutram.exe', r'bin\sutram.exe')
MEMORY_TOPICS = [  # (topic, every one of these must occur in the chapter)
    ('1 kosh beside mala', ['mala', 'kosh', 'kosh_kship']),
    ('2 mandapa and its measured number', ['mandapa', 'nirmmita', 'KB']),
    ('3 parimana', ['parimana()']),
    ('4 mandapa parimita', ['parimita', 'E_PARIMITA']),
    ('5 a slice and its rule', ['vibhag', 'E_KOSH_VIBHAG', 'E_VIBHAG_ANKA']),
    ('6 running out of memory', ['kosh vardhayitum smritih na labdha']),
    ('7 what the language does not have', ['garbage collector', 'free', 'threads']),
]


def read(root, rel):
    try:
        return open(os.path.join(root, rel), encoding='utf-8').read()
    except FileNotFoundError:
        return None


def code_text(text, is_html):
    """The code in a document: `spans` and fenced blocks in Markdown; <code> and <pre> in HTML."""
    if is_html:
        parts = re.findall(r'<pre[^>]*>(.*?)</pre>', text, re.S) + re.findall(r'<code>(.*?)</code>', text, re.S)
        return [html.unescape(re.sub(r'<[^>]+>', '', p)) for p in parts]
    return re.findall(r'```[^\n]*\n(.*?)```', text, re.S) + re.findall(r'`([^`\n]+)`', text)


# ------------------------------------------------------------------------------------------------- 1 versions
def check_versions(root, docs, current):
    bad = []
    for rel, pat in STATUS:
        t = docs.get(rel)
        if t is None:
            bad.append(f'{rel}: missing')
            continue
        m = re.search(pat, t, re.M)
        if not m:
            bad.append(f'{rel}: no status line naming a version')
        elif int(m.group(1)) != current:
            bad.append(f'{rel}: status names v{m.group(1)}, the compiler is v{current}')
    for rel in BOOKS:
        t = docs.get(rel) or ''
        heads = re.findall(r'<h[23][^>]*>(.*?)</h[23]>', t, re.S)
        toc = re.findall(r'<li><a href="#[^"]*">(.*?)</a></li>', t, re.S)
        for h in heads + toc:
            plain = re.sub(r'<[^>]+>', '', h)
            for v in re.findall(r'\bv(\d+)\b', plain):
                if int(v) != current:
                    bad.append(f'{rel}: heading or contents entry names v{v}: {plain.strip()[:60]!r}')
    for rel in PAUSED_BOOKS:
        t = docs.get(rel)
        if t is not None and not re.search(r'data-archived="v\d+"', t):
            bad.append(f'{rel}: a paused-language book that does not say which version it describes')
    return bad


# ------------------------------------------------------------------------------------------------- 2 symbols
def defined_symbols(root):
    src = ''.join(open(f, encoding='utf-8', errors='replace').read()
                  for f in glob.glob(os.path.join(root, 'src', '*.asm')) + glob.glob(os.path.join(root, 'src', '*.inc')))
    labels = set(re.findall(r'(?m)^\s*([A-Za-z_.][\w.]*)\s*:', src))
    labels |= set(re.findall(r'(?m)^\s*([A-Za-z_]\w*)\s+(?:db|dw|dd|dq|equ|times|resb|resw|resd|resq)\b', src))
    labels |= set(re.findall(r'%(?:x?i?define|macro|assign)\s+(\w+)', src))
    libs = ''
    for f in glob.glob(os.path.join(root, 'lib', '*.smlib')) + glob.glob(os.path.join(root, 'examples', 'lib', '*.smlib')):
        libs += open(f, encoding='utf-8', errors='replace').read()
    labels |= set(re.findall(r'prakriya\s+(\w+)', libs))
    files = subprocess.run(['git', '-C', root, 'ls-files'], capture_output=True, text=True).stdout.split()
    labels |= {os.path.splitext(os.path.basename(f))[0] for f in files}
    lang = ''.join(open(f, encoding='utf-8', errors='replace').read() for f in glob.glob(os.path.join(root, 'lang', '*'))
                   if os.path.isfile(f))
    return labels, src + lang + libs


def check_symbols(docs, labels, codes_text):
    bad = []
    for rel, t in docs.items():
        if rel not in CURRENT or t is None:
            continue
        code = ' '.join(code_text(t, rel.endswith('.html')))
        for s in sorted(set(re.findall(r'\b(r\d+[a-z]?_[a-z0-9_]+)\b', code))):
            if s not in labels:
                bad.append(f'{rel}: cites `{s}`, which is defined nowhere')
        for e in sorted(set(re.findall(r'\bE_[A-Z][A-Z0-9_]+\b', t))):
            if e not in codes_text:
                bad.append(f'{rel}: names {e}, which no compiler, pack or library has')
    return bad


# ------------------------------------------------------------------------------------------------- 3 examples
def book_programs(t):
    """(attributes, program text) for each <pre> in a book that is a complete program."""
    out = []
    for attrs, body in re.findall(r'<pre([^>]*)>(.*?)</pre>', t, re.S):
        prog = html.unescape(re.sub(r'<[^>]+>', '', body))
        if prog.lstrip().startswith('$ '):
            continue                         # a terminal transcript ("$ cat galat.sm"), not a program
        if re.search(r'^\s*mukhya\s*\(', prog, re.M):
            out.append((attrs, prog))
    return out


def run_program(compiler, root, prog, tmp):
    src, exe = os.path.join(tmp, 'p.sm'), os.path.join(tmp, 'p.bin')
    open(src, 'w', encoding='utf-8').write(prog)
    if os.path.exists(exe):
        os.remove(exe)
    c = subprocess.run([compiler, src, exe], capture_output=True, text=True, cwd=root, timeout=120)
    if c.returncode or not os.path.exists(exe):
        return False, c.stdout + c.stderr, None
    try:
        r = subprocess.run([exe], input='', capture_output=True, text=True, timeout=20, cwd=tmp)
        return True, r.stdout + r.stderr, r.returncode
    except subprocess.TimeoutExpired:
        return True, 'timed out', None


def check_examples(compiler, root, docs):
    bad, counted = [], 0
    with tempfile.TemporaryDirectory() as tmp:
        for rel in BOOKS:
            for i, (attrs, prog) in enumerate(book_programs(docs.get(rel) or ''), 1):
                counted += 1
                expect = re.search(r'data-expect="([A-Z_]+)"', attrs)
                want_exit = re.search(r'data-exit="(\d+)"', attrs)
                built, out, rc = run_program(compiler, root, prog, tmp)
                first = prog.strip().splitlines()[0][:50]
                if expect:
                    if built or expect.group(1) not in out:
                        bad.append(f'{rel} program {i} ({first!r}): should be refused with {expect.group(1)}; '
                                   f'{"it compiled" if built else "got: " + out.strip()[:120]}')
                elif not built:
                    bad.append(f'{rel} program {i} ({first!r}): does not compile: {out.strip()[:160]}')
                elif rc != int(want_exit.group(1) if want_exit else 0):
                    bad.append(f'{rel} program {i} ({first!r}): exit {rc}, want {want_exit.group(1) if want_exit else 0}: '
                               f'{out.strip()[-160:]}')
    return bad, counted


# ------------------------------------------------------------------------------------------------- 4 commands
def known_flags(root):
    src = ''.join(open(f, encoding='utf-8', errors='replace').read()
                  for f in glob.glob(os.path.join(root, 'src', '*.asm')) + glob.glob(os.path.join(root, 'src', '*.inc')))
    return set(re.findall(r'db\s+"(-{1,2}[a-z][a-z0-9-]*)', src))


def doc_flags(docs, flags):
    """(document, flag as written with its value if any) on compiler command lines, and lone code spans that are a
    compiler flag (a lone flag the compiler does not have is another tool's - `--work` - and is not read)."""
    found = set()
    for rel, t in docs.items():
        if rel not in CURRENT or t is None:
            continue
        for block in code_text(t, rel.endswith('.html')):
            for line in block.splitlines():
                s = line.strip().lstrip('$> ').strip()
                words = s.split()
                if not words:
                    continue
                lone = re.fullmatch(r'(--[a-z][a-z0-9-]*)(=\S+)?', s)
                if words[0] in COMPILER_NAMES or (lone and lone.group(1) in flags):
                    for m in re.finditer(r'(?<![\w-])(--[a-z][a-z0-9-]*|-i)(?=[\s=]|$)(=\S+|\s+(?!-)[A-Za-z0-9]+)?', s):
                        found.add((rel, m.group(1), (m.group(2) or '').strip()))
    return found


def check_commands(compiler, root, docs, flags):
    bad = []
    tmp = tempfile.mkdtemp()
    tiny = os.path.join(tmp, 't.sm')
    open(tiny, 'w').write('mukhya() {\n    likha(1)\n}\n')
    for rel, flag, value in sorted(doc_flags(docs, flags)):
        if flag not in flags:
            bad.append(f'{rel}: tells the reader to use {flag}, which the compiler does not know')
            continue
        if flag in ('--analysis-steps', '--lang') and value:
            v = value.replace('N', '1000') if flag == '--analysis-steps' else value
            argv = [compiler] + ([flag + v] if v.startswith('=') else [flag, v]) + [tiny, os.path.join(tmp, 'o')]
            r = subprocess.run(argv, capture_output=True, text=True, cwd=tmp, timeout=60)
            if r.returncode:
                bad.append(f'{rel}: `{flag}{value if value.startswith("=") else " " + value}` is refused by the compiler: '
                           f'{(r.stdout + r.stderr).strip()[:120]}')
    return bad


# ------------------------------------------------------------------------------------------------- 5 memory
def check_memory(docs):
    bad = []
    for rel in BOOKS:
        t = docs.get(rel) or ''
        m = re.search(r'<div class="ch" id="memory">(.*?)(?=<div class="ch"|<div class="footer")', t, re.S)
        if not m:
            bad.append(f'{rel}: no memory chapter (id="memory")')
            continue
        body = html.unescape(re.sub(r'<[^>]+>', ' ', m.group(1)))
        for topic, words in MEMORY_TOPICS:
            missing = [w for w in words if w not in body]
            if missing:
                bad.append(f'{rel}: memory chapter, topic {topic}: missing {missing}')
    return bad


# ------------------------------------------------------------------------------------------------- 6 changelog
def check_changelog(docs, current):
    t = docs.get('docs/CHANGELOG.md') or ''
    heads = re.findall(r'(?m)^## v(\d+)\b(.*)$', t)
    if not heads:
        return ['docs/CHANGELOG.md: no version entries']
    bad = []
    versions = [int(v) for v, _ in heads]
    if versions[0] != current:
        bad.append(f'docs/CHANGELOG.md: newest entry is v{versions[0]}, the compiler is v{current}')
    for v in range(min(versions), current + 1):
        if v not in versions:
            bad.append(f'docs/CHANGELOG.md: no entry for v{v}')
    for v, rest in heads:
        if not re.match(r'\s*\((?:[^()]*?),\s*R\d+', rest):
            bad.append(f'docs/CHANGELOG.md: v{v}\'s entry does not say who and which round: {rest.strip()[:60]!r}')
    return bad


# ------------------------------------------------------------------------------------------------- main
def load(root):
    rels = set(CURRENT) | set(BOOKS) | set(PAUSED_BOOKS) | {'docs/CHANGELOG.md'}
    return {rel: read(root, rel) for rel in rels}


def compiler_version(compiler):
    out = subprocess.run([compiler, '--version'], capture_output=True, text=True).stdout
    return int(re.search(r'\(v(\d+)\)', out).group(1))


def self_test(compiler, root, flags, labels, codes_text, current):
    """Each check must reject a fixture made to fail and accept one made to pass."""
    ok = []
    good_book = ('<div class="ch" id="memory"><h2>19. Memory</h2><pre><code>mukhya() {\n    likha(1)\n}</code></pre>'
                 '<p>' + ' '.join(w for _, ws in MEMORY_TOPICS for w in ws) + '</p></div><div class="footer">x (compiler v'
                 + str(current) + ')</div>')
    bad_book = ('<div class="toc"><ol><li><a href="#ch14">New Features: v22</a></li></ol></div><h2>14. New Features: v22</h2>'
                '<pre><code>mukhya()\n    mala t[5]\n    chakra i = 0 tak 5 {\n        t[i] = i\n    }\n</code></pre>'
                '<pre data-expect="E_KOSH_VIBHAG"><code>mukhya() {\n    likha(1)\n}</code></pre>'
                '<p><code>r999_no_such_label</code> E_NO_SUCH_CODE_ANYWHERE</p>'
                '<pre><code>sutram --no-such-flag p.sm\nsutram --analysis-steps 1000 p.sm</code></pre>'
                '<div class="footer">x (compiler v22)</div>')
    for label, book, want_fail in (('a book made to fail', bad_book, True), ('a book made to pass', good_book, False)):
        docs = {rel: None for rel in load(root)}
        docs.update({'docs/sutram-book-english.html': book, 'docs/sutram-book-sanskrit.html': book})
        results = {
            'versions': [b for b in check_versions(root, docs, current) if 'sutram-book' in b and 'paused' not in b],
            'symbols': check_symbols(docs, labels, codes_text),
            'examples': check_examples(compiler, root, docs)[0],
            'commands': check_commands(compiler, root, docs, flags),
            'memory': check_memory(docs),
        }
        for name, found in results.items():
            ok.append((bool(found) == want_fail, f'self-test: {name} {"rejects" if want_fail else "accepts"} {label}'
                       + ('' if bool(found) == want_fail else f' -- got {found[:2]}')))
    bad_log = {'docs/CHANGELOG.md': '## v315 (Claude, R154) - x\n## v313 - no who\n'}
    found = check_changelog(bad_log, current)
    ok.append((any('v314' in f for f in found) and any('v313' in f for f in found),
               'self-test: changelog rejects a missing version and an entry without who and round'))
    return ok


def main():
    compiler = os.path.join(ROOT, 'sutram_compiler')
    root = ROOT
    a = sys.argv[1:]
    if '--compiler' in a:
        compiler = os.path.abspath(a[a.index('--compiler') + 1])
    if '--root' in a:
        root = os.path.abspath(a[a.index('--root') + 1])
    current = compiler_version(compiler)
    docs = load(root)
    flags = known_flags(root)
    labels, codes_text = defined_symbols(root)
    checks = fails = 0

    def report(ok, what):
        nonlocal checks, fails
        checks += 1
        fails += not ok
        print(('PASS  ' if ok else 'FAIL  ') + what)

    for ok, what in self_test(compiler, root, flags, labels, codes_text, current):
        report(ok, what)
    ex_bad, n_prog = check_examples(compiler, root, docs)
    for name, found, what in (
            ('versions', check_versions(root, docs, current), f'every current status line names v{current}; no book heading names another version; paused books say which version they describe'),
            ('symbols', check_symbols(docs, labels, codes_text), 'every symbol and E_ code a current document cites exists'),
            ('examples', ex_bad, f'every complete program in the English and Sanskrit books ({n_prog}) does what the book says on v{current}'),
            ('commands', check_commands(compiler, root, docs, flags), 'every compiler flag a current document shows is one the compiler accepts, in the form shown'),
            ('memory', check_memory(docs), 'the memory chapter is in both books and covers the seven topics'),
            ('changelog', check_changelog(docs, current), f'docs/CHANGELOG.md has every version to v{current}, each with who and the round')):
        report(not found, f'{name}: {what}')
        for f in found:
            print('      ' + f)
    print(f'r158 doc currency: {checks} checks, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
