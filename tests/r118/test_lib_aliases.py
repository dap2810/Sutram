#!/usr/bin/env python3
"""R118: the library's English names, as aliases. The library defines the Sanskrit name; a call written with the
old name compiles to the same bytes as the new name and prints one warning naming the replacement; the new name
prints none.

Checks, each against the compiler given (default ./sutram_compiler):
  * each of the ten pairs, ELF and PE: old-name program and new-name program -> byte-identical outputs;
    old -> exactly one "Sutram suchana: 'OLD' purana nama - 'NEW' likhatu"; new -> no warning; the program runs
    and prints the expected value (ELF);
  * an old name called twice warns once; a space before `(` is still a call;
  * a prakriya the program defines with an old name is the program's own: it runs, no warning, with or
    without the module that has the new name;
  * a variable with an old name is not touched and not warned about;
  * an old name inside a yoj'd module is rewritten (it compiles) and not warned about;
  * a --lang hindi run is not warned (a pack run prints only its pack's language - R11);
  * an old name without its `yoj`: refused, the hint names the module of the new name;
  * the compiler's E_KOSH hints name kosh_gan, not kosh_len.
Last line: "r118 library names: N checks, M failed".
"""
import os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMPILER = os.path.abspath(sys.argv[sys.argv.index('--compiler') + 1]) if '--compiler' in sys.argv \
    else os.path.join(ROOT, 'sutram_compiler')

SETUP = {
    'ganit': '',
    'sangrah': ('    vitti s1 = rakh_srij(8)\n    vitti s2 = rakh_srij(8)\n    vitti s3 = rakh_srij(16)\n'
                '    rakh_yuj(s1, 8, "a", 1)\n    rakh_yuj(s1, 8, "b", 1)\n    rakh_yuj(s2, 8, "b", 1)\n'
                '    rakh_yuj(s2, 8, "c", 1)\n'),
    'roop': '    vitti out = nirmmita(128)\n',
    'vakyank': '    vitti buf = nirmmita(10 * 8)\n    ank_tak_varna(7, buf)\n',
    'shreni': '    mala a[4]\n    a[0] = 1\n    a[1] = 2\n    a[2] = 2\n    a[3] = 5\n',
    'suchi': '    vitti l = suchi_srij(8)\n    suchi_khip(l, 3)\n    suchi_khip(l, 9)\n',
}
# (old, new, module, the call, what it prints)
PAIRS = [
    ('bit_gan', 'ekanka_gan', 'ganit', 'bit_gan(255)', '8'),
    ('rakh_samroop_diff', 'rakh_ubhaya_bhed', 'sangrah', 'rakh_samroop_diff(s1, 8, s2, 8, s3)', '2'),
    ('roop_pad_vam', 'roop_purti_vam', 'roop', 'roop_pad_vam("ka", 2, 5, 46, out)', '5'),
    ('roop_pad_dakshin', 'roop_purti_dakshin', 'roop', 'roop_pad_dakshin("ka", 2, 5, 46, out)', '5'),
    ('roop_pad_madhya', 'roop_purti_madhya', 'roop', 'roop_pad_madhya("ka", 2, 5, 46, out)', '5'),
    ('pad_vam', 'purti_vam', 'vakyank', 'pad_vam(buf, 1, 3, 48)', '3'),
    ('roop_ank_pre', 'roop_ank_upasarga', 'roop', 'roop_ank_pre(255, 16, 0, out)', '4'),
    ('roop_sign_akshar', 'roop_chihna_akshar', 'roop', 'roop_sign_akshar(42, 43, out)', '3'),
    ('asti_sorted', 'asti_kramabaddha', 'shreni', 'asti_sorted(a, 4)', '1'),
    ('suchi_asti_sorted', 'suchi_asti_kramabaddha', 'suchi', 'suchi_asti_sorted(l)', '1'),
]


def prog(module, body):
    return f'yoj {module}\n\nmukhya() {{\n{SETUP[module]}{body}}}\n'


def compile_(d, src, out, *flags, cwd=None):
    p = os.path.join(d, 'p.sm')
    open(p, 'w', encoding='utf-8').write(src)
    if os.path.exists(out):
        os.remove(out)
    r = subprocess.run([COMPILER, *flags, p, out], capture_output=True, text=True, cwd=cwd or ROOT)
    return r.returncode, r.stdout, r.stderr


def warnings(err):
    return [l for l in err.splitlines() if l.startswith('Sutram suchana:')]


def run(path):
    return subprocess.run([path], capture_output=True, text=True, timeout=20).stdout.strip()


def main():
    checks = fails = 0

    def check(ok, what):
        nonlocal checks, fails
        checks += 1
        fails += not ok
        print(('PASS  ' if ok else 'FAIL  ') + what)

    with tempfile.TemporaryDirectory() as d:
        for old, new, module, call, want in PAIRS:
            for ext in ('bin', 'exe'):
                po, pn = os.path.join(d, 'o.' + ext), os.path.join(d, 'n.' + ext)
                flags = ()                   # the output's name chooses PE (.exe) or ELF
                ro, so, eo = compile_(d, prog(module, f'    likha({call})\n'), po, *flags)
                bo = open(po, 'rb').read() if ro == 0 else b''
                rn, sn, en = compile_(d, prog(module, f'    likha({call.replace(old, new, 1)})\n'), pn, *flags)
                bn = open(pn, 'rb').read() if rn == 0 else b''
                same = ro == 0 and rn == 0 and bo == bn
                wo = [f"Sutram suchana: '{old}' purana nama - '{new}' likhatu"]
                got = run(po) if ext == 'bin' and ro == 0 else want
                ok = same and warnings(eo) == wo and warnings(en) == [] and got == want
                check(ok, f'{old} -> {new} ({ext}): same bytes {same}, old warns {warnings(eo) == wo}, '
                          f'new silent {warnings(en) == []}, prints {got!r} (want {want!r})'
                          + ('' if ro == 0 and rn == 0 else f' (exit {ro}/{rn}: {(so + sn)[:120]})'))

        b = os.path.join(d, 'x.bin')
        # twice, and with a space before the parenthesis
        rc, _, err = compile_(d, prog('shreni', '    likha(asti_sorted(a, 4))\n    likha(asti_sorted (a, 4))\n'), b)
        check(rc == 0 and len(warnings(err)) == 1 and run(b).split() == ['1', '1'],
              f'asti_sorted twice, once with a space before "(": exit {rc}, {len(warnings(err))} warning (1)')

        # the program's own prakriya of an old name, without and with the module
        own = 'prakriya asti_sorted(x, n) {\n    nivartanam 77\n}\n\n'
        for mod in ('', 'yoj shreni\n\n'):
            rc, _, err = compile_(d, mod + own + 'mukhya() {\n    mala a[2]\n    likha(asti_sorted(a, 2))\n}\n', b)
            check(rc == 0 and warnings(err) == [] and run(b) == '77',
                  f'own prakriya asti_sorted{" beside yoj shreni" if mod else ""}: exit {rc}, '
                  f'warnings {warnings(err)}, prints {run(b) if rc == 0 else "-"!r} (77)')

        # a variable of an old name
        rc, _, err = compile_(d, 'yoj ganit\n\nmukhya() {\n    vitti bit_gan = 5\n    likha(bit_gan + ekanka_gan(3))\n}\n', b)
        check(rc == 0 and warnings(err) == [] and run(b) == '7',
              f'a variable named bit_gan: exit {rc}, warnings {warnings(err)} (none), prints 7')

        # an old name inside a yoj'd module: rewritten, not warned about
        os.makedirs(os.path.join(d, 'lib'), exist_ok=True)
        open(os.path.join(d, 'lib', 'r118mod.smlib'), 'w').write(
            'yoj ganit\n\nprakriya dvi_bit(n) {\n    nivartanam bit_gan(n) * 2\n}\n')
        rc, so, err = compile_(d, 'yoj r118mod\n\nmukhya() {\n    likha(dvi_bit(7))\n}\n', b, cwd=d)
        check(rc == 0 and warnings(err) == [] and run(b) == '6',
              f'bit_gan inside a yoj\'d module: exit {rc}, warnings {warnings(err)} (none), prints 6 {so[:80] if rc else ""}')

        # a pack run prints only its pack's language
        rc, _, err = compile_(d, prog('ganit', '    likha(bit_gan(255))\n'), b, '--lang', 'hindi')
        check(rc == 0 and warnings(err) == [] and run(b) == '8',
              f'--lang hindi with bit_gan: exit {rc}, warnings {warnings(err)} (none)')

        # without the yoj: refused, and the hint names the module
        rc, so, err = compile_(d, 'mukhya() {\n    mala a[2]\n    likha(asti_sorted(a, 2))\n}\n', b)
        check(rc != 0 and "yoj shreni" in so + err and not os.path.exists(b),
              f'asti_sorted without yoj shreni: exit {rc}, hint names yoj shreni {"yoj shreni" in so + err}')

        # the compiler's own hints name the new builtin
        rc, so, err = compile_(d, 'mukhya() {\n    kosh k[2]\n    kosh_kship(k, 1)\n    vitti x = k + 1\n}\n', b)
        check(rc != 0 and 'kosh_gan(k)' in so + err and 'kosh_len' not in so + err,
              f'E_KOSH hint: names kosh_gan(k) {"kosh_gan(k)" in so + err}, no kosh_len {"kosh_len" not in so + err}')
    print(f'r118 library names: {checks} checks, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
