#!/usr/bin/env python3
"""R111: the vocabulary change, as aliases. Every old name still works and compiles to the same bytes as its
new name; the old name, written in the program's own file, prints one warning on stderr naming the
replacement; the new name prints none. `asti` / `nasti` (and अस्ति / नास्ति) are the tokens `==` / `!=`.

Checks, each against the compiler given (default ./sutram_compiler), ELF and PE:
  * sankhya_bindu / sankhya_dot (withdrawn, R115): refused with E_PRATYAHRITA, no warning, no output;
  * each of the other 21 builtin pairs: old-name program and new-name program -> byte-identical outputs;
    old -> exactly one "Sutram suchana: 'OLD' purana nama - 'NEW' likhatu"; new -> no warning;
  * asti / nasti / अस्ति / नास्ति -> the same bytes as == / !=, and they run true and false correctly;
  * an old name used twice warns once; an old name inside a yoj'd module does not warn;
  * a --lang gujarati word that maps to kosh_push does not warn, and no --lang run warns at all
    (a pack run prints only its pack's language - R11);
  * the shell (-i): tyaj leaves with no warning; exit, quit, help warn and still work.
Last line: "r111 vocabulary: N checks, M failed".
"""
import os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMPILER = os.path.abspath(sys.argv[sys.argv.index('--compiler') + 1]) if '--compiler' in sys.argv \
    else os.path.join(ROOT, 'sutram_compiler')

# (old, new, a statement using it; K is a kosh with 3 and 7 pushed, M a mala of 3, S a string, B 16 bytes)
PAIRS = [
    ('kosh_push', 'kosh_kship', 'kosh_push(K, 9)'),
    ('kosh_pop', 'kosh_hri', 'likha(kosh_pop(K))'),
    ('kosh_len', 'kosh_gan', 'likha(kosh_len(K))'),
    ('kosh_cap', 'kosh_ksham', 'likha(kosh_cap(K))'),
    ('kosh_peek', 'kosh_iksh', 'likha(kosh_peek(K))'),
    ('kosh_empty', 'kosh_rikt', 'likha(kosh_empty(K))'),
    ('kosh_clear', 'kosh_shodh', 'kosh_clear(K)'),
    ('kosh_enqueue', 'kosh_yuj', 'kosh_enqueue(K, 11)'),
    ('kosh_dequeue', 'kosh_apanay', 'likha(kosh_dequeue(K))'),
    ('pankti_len', 'pankti_gan', 'likha(pankti_len(M))'),
    ('netsock', 'jala', 'vitti s = netsock()'),
    ('netbind', 'jala_bandh', 'likha(netbind(0 - 1, 0))'),
    ('netlisten', 'jala_shru', 'likha(netlisten(0 - 1))'),
    ('netaccept', 'jala_grah', 'likha(netaccept(0 - 1))'),
    ('char_lower', 'akshar_laghu', 'likha(char_lower(65))'),
    ('char_upper', 'akshar_guru', 'likha(char_upper(97))'),
    ('char_from', 'anka_akshar', 'shabda(char_from(66))'),
    ('vartani_cat', 'vartani_sandhi', 'vitti c = vartani_cat(S, "!")'),
    ('lkhb', 'likha_santat', 'lkhb(7)'),
    ('likha_fmt', 'likha_rup', 'likha_fmt("x=", 42)'),
    ('smaran_cp', 'smaran_pratilip', 'smaran_cp(B, "OK", 3)'),
]
BODY = '''mukhya() {{
    kosh K[4]
    kosh_kship(K, 3)
    kosh_kship(K, 7)
    vitti M[3]
    vitti S = "ab"
    vitti B = nirmmita(16)
    {stmt}
}}
'''


def compile_(src, out, *flags, cwd=None):
    r = subprocess.run([COMPILER, *flags, src, out], capture_output=True, text=True, cwd=cwd or ROOT)
    return r.returncode, r.stdout, r.stderr


def warnings(err):
    return [l for l in err.splitlines() if l.startswith('Sutram suchana:')]


def main():
    checks = fails = 0

    def check(ok, what):
        nonlocal checks, fails
        checks += 1
        fails += not ok
        print(('PASS  ' if ok else 'FAIL  ') + what)

    with tempfile.TemporaryDirectory() as d:
        for old, new, stmt in PAIRS:
            for ext in ('bin', 'exe'):
                po, pn = os.path.join(d, 'o.sm'), os.path.join(d, 'n.sm')
                open(po, 'w').write(BODY.format(stmt=stmt))
                open(pn, 'w').write(BODY.format(stmt=stmt.replace(old, new, 1)))
                ro, so, eo = compile_(po, os.path.join(d, 'o.' + ext))
                rn, sn, en = compile_(pn, os.path.join(d, 'n.' + ext))
                same = ro == 0 and rn == 0 and \
                    open(os.path.join(d, 'o.' + ext), 'rb').read() == open(os.path.join(d, 'n.' + ext), 'rb').read()
                want = [f"Sutram suchana: '{old}' purana nama - '{new}' likhatu"]
                ok = same and warnings(eo) == want and warnings(en) == []
                check(ok, f'{old} -> {new} ({ext}): same bytes {same}, old warns {warnings(eo) == want}, '
                          f'new silent {warnings(en) == []}' + ('' if ro == 0 and rn == 0 else f' (exit {ro}/{rn}: {so or sn})'))

        # R115: sankhya_bindu and sankhya_dot are withdrawn - both refused, named, no output, no old-name warning
        for name in ('sankhya_bindu', 'sankhya_dot'):
            for ext in ('bin', 'exe'):
                p = os.path.join(d, 'w.sm')
                out = os.path.join(d, 'w.' + ext)
                if os.path.exists(out):
                    os.remove(out)
                open(p, 'w').write(BODY.format(stmt=f'vitti dp = {name}(B, B, 2)'))
                rc, so, err = compile_(p, out)
                ok = rc != 0 and '[E_PRATYAHRITA]' in so and warnings(err) == [] and not os.path.exists(out)
                check(ok, f'{name} ({ext}): withdrawn - exit {rc}, E_PRATYAHRITA {"[E_PRATYAHRITA]" in so}, '
                          f'no warning {warnings(err) == []}, no output {not os.path.exists(out)}')

        # asti / nasti: the same bytes as == / !=, and the right answers
        base = 'mukhya() {\n    vitti a = 4\n    likha(a OP1 4)\n    likha(a OP1 5)\n    likha(a OP2 5)\n    likha(a OP2 4)\n}\n'
        outs = {}
        for tag, e, n in (('sym', '==', '!='), ('lat', 'asti', 'nasti'), ('dev', 'अस्ति', 'नास्ति')):
            p = os.path.join(d, f'{tag}.sm')
            open(p, 'w', encoding='utf-8').write(base.replace('OP1', e).replace('OP2', n))
            rc, _, err = compile_(p, os.path.join(d, f'{tag}.bin'))
            outs[tag] = (rc, open(os.path.join(d, f'{tag}.bin'), 'rb').read() if rc == 0 else b'', err)
        check(outs['lat'][1] == outs['sym'][1] != b'' and outs['dev'][1] == outs['sym'][1],
              'asti / nasti / अस्ति / नास्ति compile to the bytes of == / !=')
        run = subprocess.run([os.path.join(d, 'lat.bin')], capture_output=True, text=True).stdout.split()
        check(run == ['1', '0', '1', '0'], f'asti true, asti false, nasti true, nasti false: {run}')
        check(warnings(outs['lat'][2]) == [], 'asti / nasti print no warning')

        # once per name
        p = os.path.join(d, 'twice.sm')
        open(p, 'w').write('mukhya() {\n    kosh k[2]\n    kosh_push(k, 1)\n    kosh_push(k, 2)\n    likha(kosh_len(k))\n}\n')
        rc, _, err = compile_(p, os.path.join(d, 'twice.bin'))
        check(rc == 0 and len(warnings(err)) == 2, f'kosh_push twice and kosh_len once: {len(warnings(err))} warnings (2)')

        # an old name in a yoj'd module is not the program's own text
        os.makedirs(os.path.join(d, 'lib'), exist_ok=True)
        open(os.path.join(d, 'lib', 'r111mod.smlib'), 'w').write(
            'prakriya ginti(kosh k) {\n    nivartanam kosh_len(k)\n}\n')
        open(os.path.join(d, 'usemod.sm'), 'w').write(
            'yoj r111mod\n\nmukhya() {\n    kosh k[2]\n    kosh_kship(k, 1)\n    likha(ginti(k))\n}\n')
        rc, _, err = compile_(os.path.join(d, 'usemod.sm'), os.path.join(d, 'usemod.bin'), cwd=d)
        check(rc == 0 and warnings(err) == [], f'an old name inside a yoj\'d module: no warning (exit {rc}, {warnings(err)})')

        # a pack word that maps to an old name is the pack's word, not the old spelling
        guj = [l.split()[0] for l in open(os.path.join(ROOT, 'lang', 'gujarati.lang'), encoding='utf-8')
               if l.strip().endswith(' kosh_push')]
        if guj:
            p = os.path.join(d, 'guj.sm')
            open(p, 'w', encoding='utf-8').write(f'mukhya() {{\n    kosh k[2]\n    {guj[0]}(k, 1)\n    likha(kosh_gan(k))\n}}\n')
            rc, _, err = compile_(p, os.path.join(d, 'guj.bin'), '--lang', 'gujarati')
            check(rc == 0 and warnings(err) == [], f'--lang gujarati {guj[0]} (kosh_push): no warning (exit {rc})')

        # a pack run prints only its pack's language, so the (romanised Sanskrit) warning is not printed there
        p = os.path.join(d, 'hindi.sm')
        open(p, 'w').write('mukhya() {\n    kosh k[2]\n    kosh_push(k, 1)\n    likha(kosh_gan(k))\n}\n')
        rc, _, err = compile_(p, os.path.join(d, 'hindi.bin'), '--lang', 'hindi')
        check(rc == 0 and warnings(err) == [], f'--lang hindi with the Latin kosh_push: no warning (exit {rc})')

        # the shell
        # one command a run: the shell reads stdin in chunks, so two piped lines arrive as one (v291 too)
        for word, warn in (('tyaj', None), ('exit', 'tyaj'), ('quit', 'tyaj'), ('help', 'sahayata')):
            r = subprocess.run([COMPILER, '-i'], input=word + '\n', capture_output=True, text=True, timeout=20)
            w = warnings(r.stderr)
            ok = r.returncode == 0 and (w == [] if warn is None else
                                        w == [f"Sutram suchana: '{word}' purana nama - '{warn}' likhatu"])
            check(ok, f'shell "{word}": exit {r.returncode}, warnings {w}')
    print(f'r111 vocabulary: {checks} checks, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
