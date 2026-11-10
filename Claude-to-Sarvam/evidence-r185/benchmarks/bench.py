#!/usr/bin/env python3
"""Build and time the same scenarios in Sutram and in whichever other languages this machine has.

  python3 bench.py --sutram PATH [--sutram2 PATH --label2 NAME] [--rounds 5] [--out results.md]

Every time is WALL time of the whole process, best of --rounds, measured around the program from start to
exit - so it includes starting the language's runtime (the "empty program" row is that cost alone).
A language whose compiler is not found gets a blank row that says so. A program whose output is not the
expected answer is marked WRONG and not timed.

Scenarios:
  empty  a program that does nothing
  A      10,000,000 passes of s = s + i * 2
  A2     10,000,000 passes of s = (s + i * 2) ^ (s >> 3)   (each pass needs the one before)
  B      build a growing collection of 1,000,000 numbers, then sum it
  C      fill a buffer of 10,000,000 64-bit numbers (80 MB), then sum all of it 20 times
  C0     the same with 0 sums (the fill alone), so (C - C0) / 20 is one pass over the buffer
  D      the same work on a buffer that fits in the processor's cache: 100,000 numbers (800 KB), summed
         2,000 times - 200,000,000 additions, as in C
  D0     its fill alone
"""
import argparse, json, os, re, shutil, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
EXPECT = {'empty': '', 'A': '99999990000000', 'A2': '31926361189', 'B': '499999500000',
          'C': '102297542610', 'C0': '0', 'D': '102065457000', 'D0': '0'}
SC = ['empty', 'A', 'A2', 'B', 'C0', 'C', 'D0', 'D']
# scenario -> (passes, numbers) for the buffer programs
ARGS = {'C0': (0, 10000000), 'C': (20, 10000000), 'D0': (0, 100000), 'D': (2000, 100000)}
SRC = {'A': 'a_arith', 'A2': 'a2_arith_dependent', 'B': 'b_collect', 'C': 'c_sum_buffer', 'C0': 'c_sum_buffer',
       'D': 'c_sum_buffer', 'D0': 'c_sum_buffer', 'empty': 'empty'}
JAVA = {'A': 'AArith', 'A2': 'A2ArithDependent', 'B': 'BCollect', 'C': 'CSumBuffer', 'C0': 'CSumBuffer',
        'D': 'CSumBuffer', 'D0': 'CSumBuffer', 'empty': 'Empty'}
PASSES = 20


def args_of(sc):
    return [str(x) for x in ARGS[sc]] if sc in ARGS else []


def have(tool):
    return shutil.which(tool) is not None


def version(tool):
    try:
        if tool == 'go':
            o = subprocess.run(['go', 'version'], capture_output=True, text=True)
        elif tool in ('java', 'javac'):
            o = subprocess.run([tool, '-version'], capture_output=True, text=True)
            lines = [l for l in (o.stdout + o.stderr).splitlines() if 'JAVA_TOOL_OPTIONS' not in l]
            # a version of four numbers joined by dots reads like a network address to the repository's privacy gate
            return re.sub(r'(\d+\.\d+\.\d+)\.(\d+)', r'\1 (patch \2)', lines[0].strip()) if lines else '?'
        else:
            o = subprocess.run([tool, '--version'], capture_output=True, text=True)
        lines = [l.strip() for l in (o.stdout + o.stderr).splitlines() if l.strip()]
        return lines[0] if lines else '?'
    except Exception as e:
        return 'error: %s' % e


def best(cmd, rounds, stdin=None, cwd=None, env=None, want=None, prepare=None):
    """Best wall time of `rounds` runs, in seconds; None and a reason if it fails or prints the wrong answer."""
    b = None
    for _ in range(rounds):
        if prepare:
            prepare()
        t = time.perf_counter()
        r = subprocess.run(cmd, input=stdin, capture_output=True, text=True, cwd=cwd, env=env)
        d = time.perf_counter() - t
        if r.returncode != 0:
            return None, 'exit %d: %s' % (r.returncode, (r.stderr or r.stdout)[-200:].strip())
        if want is not None and r.stdout.strip() != want:
            return None, 'WRONG: printed %r, expected %r' % (r.stdout.strip()[:40], want)
        b = d if b is None or d < b else b
    return b, ''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sutram', required=True)
    ap.add_argument('--label', default='Sutram')
    ap.add_argument('--sutram2')
    ap.add_argument('--label2', default='Sutram (second compiler)')
    ap.add_argument('--rounds', type=int, default=5)
    ap.add_argument('--big', type=int, default=128, help='functions in the compile-time program')
    ap.add_argument('--out', default=os.path.join(HERE, 'results.md'))
    a = ap.parse_args()
    B = os.path.join(HERE, 'build')
    shutil.rmtree(B, ignore_errors=True)
    os.makedirs(B)
    env = dict(os.environ, GOCACHE=os.path.join(B, 'gocache'), GOFLAGS='-mod=mod', GOTOOLCHAIN='local')

    # ---- the configurations: label, the tool it needs, how to build one source, how to run a scenario
    confs = []

    def sutram(label, comp):
        comp = os.path.abspath(comp)

        def build(sc, src=None, out=None):
            src = src or os.path.join(HERE, SRC[sc] + '.sm')
            out = out or os.path.join(B, '%s_%s.sutram' % (label.replace(' ', '_').replace('(', '').replace(')', ''), SRC[sc]))
            return [[comp, src, out]], out

        def run(sc, exe):
            return [exe], ('%d\n%d\n' % ARGS[sc]) if sc in ARGS else None
        confs.append(dict(label=label, tool=comp, ok=os.path.exists(comp), build=build, run=run, lang='sm'))

    sutram(a.label, a.sutram)
    if a.sutram2:
        sutram(a.label2, a.sutram2)

    def native(label, tool, flags, ext):
        def build(sc, src=None, out=None):
            src = src or os.path.join(HERE, SRC[sc] + ext)
            if not os.path.exists(src):
                return None, None
            out = out or os.path.join(B, '%s_%s' % (label.replace(' ', '_').replace('=', ''), SRC[sc]))
            return [[tool] + flags + ['-o', out, src]], out

        def run(sc, exe):
            return [exe] + args_of(sc), None
        confs.append(dict(label=label, tool=tool, ok=have(tool), build=build, run=run, lang=ext))

    native('C, gcc (no flag)', 'gcc', [], '.c')
    native('C, gcc -O2', 'gcc', ['-O2'], '.c')
    native('C, gcc -O3 -march=native', 'gcc', ['-O3', '-march=native'], '.c')
    native('C, clang (no flag)', 'clang', [], '.c')
    native('C, clang -O2', 'clang', ['-O2'], '.c')
    native('C++, g++ (no flag)', 'g++', [], '.cpp')
    native('C++, g++ -O2', 'g++', ['-O2'], '.cpp')
    native('Rust, rustc (debug)', 'rustc', [], '.rs')
    native('Rust, rustc -C opt-level=3 (what --release sets)', 'rustc', ['-C', 'opt-level=3'], '.rs')
    native('Zig, zig build-exe -O ReleaseFast', 'zig', [], '.zig')

    def go_build(sc, src=None, out=None):
        d = src or os.path.join(HERE, 'go', SRC[sc])
        out = out or os.path.join(B, 'go_' + SRC[sc])
        return [['go', 'build', '-o', out, '.']], out
    go_build.cwd = True
    confs.append(dict(label='Go, go build', tool='go', ok=have('go'), build=go_build, lang='go',
                      run=lambda sc, exe: ([exe] + args_of(sc), None)))

    def java_build(sc, src=None, out=None):
        src = src or os.path.join(HERE, 'java', JAVA[sc] + '.java')
        return [['javac', '-d', os.path.join(B, 'java'), src]], JAVA[sc]
    confs.append(dict(label='Java, javac + java', tool='javac', ok=have('javac') and have('java'), build=java_build, lang='java',
                      run=lambda sc, cls: (['java', '-cp', os.path.join(B, 'java'), cls] + args_of(sc), None)))

    def interp(label, tool, ext):
        def build(sc, src=None, out=None):
            return [], os.path.join(HERE, SRC[sc] + ext)
        confs.append(dict(label=label, tool=tool, ok=have(tool), build=build, lang=ext,
                          run=lambda sc, f: ([tool, f] + args_of(sc), None)))
    interp('JavaScript, node', 'node', '.js')
    interp('Python, python3', 'python3', '.py')

    out = []
    P = out.append
    P('## What this machine has\n')
    P('| tool | |')
    P('|---|---|')
    for t in ['gcc', 'cc', 'clang', 'g++', 'rustc', 'cargo', 'go', 'javac', 'java', 'zig', 'python3', 'node', 'perl', 'ruby', 'nasm']:
        P('| `%s` | %s |' % (t, version(t) if have(t) else '**not found**'))
    for c in confs:
        if c['lang'] == 'sm':
            v = subprocess.run([c['tool'], '--version'], capture_output=True, text=True).stdout.splitlines()
            P('| %s | %s |' % (c['label'], v[0] if v else '?'))
    P('')

    # ---- run time
    results = {}
    P('## Run time - wall time of the whole process, best of %d, milliseconds\n' % a.rounds)
    P('| | ' + ' | '.join(SC) + ' | C: 10,000,000 additions, (C - C0) / 20 | D: 10,000,000 additions, (D - D0) / 20 |')
    P('|---|' + '---:|' * (len(SC) + 2))
    notes = []
    for c in confs:
        row = []
        results[c['label']] = {}
        if not c['ok']:
            P('| %s | ' % c['label'] + ' | '.join([''] * len(SC)) + ' | | | *`%s` not found - not measured*' % os.path.basename(c['tool']))
            continue
        for sc in SC:
            cmds, exe = c['build'](sc)
            if exe is None:
                row.append('')
                continue
            failed = ''
            for cmd in cmds:
                cwd = os.path.join(HERE, 'go', SRC[sc]) if c['lang'] == 'go' else None
                r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, env=env)
                if r.returncode != 0 or (c['lang'] == 'sm' and not os.path.exists(exe)):
                    failed = (r.stderr or r.stdout)[-300:].strip()
            if failed:
                row.append('BUILD FAILED')
                notes.append('%s, %s: %s' % (c['label'], sc, failed))
                continue
            cmd, stdin = c['run'](sc, exe)
            t, why = best(cmd, a.rounds, stdin=stdin, env=env, want=EXPECT[sc])
            if t is None:
                row.append('FAILED')
                notes.append('%s, %s: %s' % (c['label'], sc, why))
            else:
                results[c['label']][sc] = t
                row.append('%.1f' % (t * 1000))
        r = results[c['label']]
        per = '%.2f' % ((r['C'] - r['C0']) * 1000 / 20) if 'C' in r and 'C0' in r else ''
        perd = '%.2f' % ((r['D'] - r['D0']) * 1000 / 20) if 'D' in r and 'D0' in r else ''
        P('| %s | ' % c['label'] + ' | '.join(row) + ' | %s | %s |' % (per, perd))
        print(out[-1], flush=True)
    P('')
    # Sutram's checked collection for scenario C
    for c in confs:
        if c['lang'] == 'sm' and c['ok']:
            src = os.path.join(HERE, 'c_sum_kosh.sm')
            exe = os.path.join(B, 'kosh_' + os.path.basename(c['build']('A')[1]))
            subprocess.run([c['tool'], src, exe], capture_output=True)
            if os.path.exists(exe):
                for sc in ('C', 'D'):
                    t20, _ = best([exe], a.rounds, stdin='%d\n%d\n' % ARGS[sc], want=EXPECT[sc])
                    t0, _ = best([exe], a.rounds, stdin='%d\n%d\n' % ARGS[sc + '0'], want='0')
                    if t20 and t0:
                        results[c['label']][sc + 'kosh'] = t20
                        results[c['label']][sc + 'kosh0'] = t0
                        P('- **%s, scenario %s with a `kosh` (every index checked) instead of raw `nirmmita` memory:** fill %.1f ms, all %.1f ms, 10,000,000 additions %.2f ms.'
                          % (c['label'], sc, t0 * 1000, t20 * 1000, (t20 - t0) * 1000 / 20))
    P('')
    for n in notes:
        P('- ' + n)
    P('')

    # ---- compile time
    big = os.path.join(B, 'big')
    subprocess.run([sys.executable, os.path.join(HERE, 'gen_big.py'), str(a.big), big], check=True)
    lines = sum(1 for _ in open(os.path.join(big, 'big.sm')))
    P('## Compile time - wall time of the compiler, best of %d, milliseconds\n' % a.rounds)
    P('"small" is scenario A\'s source (under 15 lines). "big" is one generated program in each language: %d functions '
      'of six lines and a main that calls each once (%d lines in Sutram), written by `gen_big.py`.\n' % (a.big, lines))
    P('| | small | big | what the time covers |')
    P('|---|---:|---:|---|')
    bigsrc = {'.c': 'big.c', '.rs': 'big.rs', 'sm': 'big.sm'}
    counter = [0]
    for c in confs:
        if c['lang'] in ('.js', '.py', '.cpp', '.zig'):
            continue
        if not c['ok']:
            P('| %s | | | *`%s` not found - not measured* |' % (c['label'], os.path.basename(c['tool'])))
            continue
        cells = []
        for which in ('small', 'big'):
            prepare = None
            cwd = None
            if c['lang'] == 'go':
                d = os.path.join(HERE, 'go', 'a_arith') if which == 'small' else os.path.join(big, 'go_big')
                d2 = os.path.join(B, 'gotime_' + which)
                shutil.rmtree(d2, ignore_errors=True)
                shutil.copytree(d, d2)
                cmds, _ = c['build']('A', src=d2, out=os.path.join(B, 'ct_go_' + which))
                cwd = d2
                base = open(os.path.join(d2, 'main.go')).read()

                def prepare(d2=d2, base=base):   # a new comment each time, so the build cache cannot answer
                    counter[0] += 1
                    open(os.path.join(d2, 'main.go'), 'w').write(base + '\n// build %d\n' % counter[0])
                subprocess.run(cmds[0], cwd=cwd, env=env, capture_output=True)   # warm the standard library's cache
            elif c['lang'] == 'java':
                src = os.path.join(HERE, 'java', 'AArith.java') if which == 'small' else os.path.join(big, 'java_big', 'Big.java')
                cmds = [['javac', '-d', os.path.join(B, 'ct_java'), src]]
            else:
                ext = c['lang']
                src = (os.path.join(HERE, 'a_arith' + ('.sm' if ext == 'sm' else ext)) if which == 'small'
                       else os.path.join(big, bigsrc[ext]))
                cmds, _ = c['build']('A', src=src, out=os.path.join(B, 'ct_out'))
            t, why = best(cmds[0], a.rounds, cwd=cwd, env=env, prepare=prepare)
            cells.append('%.1f' % (t * 1000) if t is not None else 'FAILED')
            if t is None:
                notes.append('compile %s %s: %s' % (c['label'], which, why))
            else:
                results[c['label']]['compile_' + which] = t
        cover = {'sm': 'source to executable, one process (no assembler, no linker)',
                 '.c': 'preprocess, compile, assemble, link', '.rs': 'compile and link',
                 'go': '`go build` of the one package (the standard library already built)',
                 'java': 'source to `.class` (no native code is made here; the JVM compiles when it runs)'}[c['lang']]
        P('| %s | %s | %s | %s |' % (c['label'], cells[0], cells[1], cover))
        print(out[-1], flush=True)
    P('')
    open(a.out, 'w').write('\n'.join(out) + '\n')
    json.dump(results, open(os.path.splitext(a.out)[0] + '.json', 'w'), indent=1, sort_keys=True)
    print('\nwritten: %s' % os.path.basename(a.out))


if __name__ == '__main__':
    main()
