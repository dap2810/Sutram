#!/usr/bin/env python3
"""R182 (Sarvam ROUND-182): a character the language does not know is refused where it stands.

Up to v320 the lexer skipped any character it did not recognise and carried on. So `vitti a = 5 <en dash> 2`
compiled and printed 5 - the subtraction silently gone - and `likha(<curly quote>hello<curly quote>)` was refused
for an unknown name `hello`, three characters away from what was wrong.

From v321:  file:line:col: Sutram truti [E_AGYAT_AKSHAR]: agyat akshar '<the character>' (U+XXXX)
then the source line with a caret under the character, and a Sanket line when the intention is plain (a curly
quote -> ", a dash -> -, a no-break space -> a space, an invisible character -> remove it, x -> *).
A character that cannot be shown (a control, a no-break or zero-width space) is named by its code point only.

Not refused, and checked here: anything inside a comment (#, //, /* */) or inside a string - that is prose; a
byte-order mark at the start of the file; Devanagari digits and names, which the language knows.

Usage: python3 tests/r182/test_unknown_character.py [--compiler PATH]
"""
import os, shutil, subprocess, sys, tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
checks = fails = 0
Q = '"'

# (name, source, line:col, the text after "agyat akshar ", the Sanket line or None)
REFUSED = [
    ('curly-quote', 'mukhya() {\n    likha(\u201chello\u201d)\n}\n', '2:11', "'\u201c' (U+201C)", f'Sanket: saral uddharana-chihnam {Q} (U+0022) likhyatam'),
    ('en-dash', 'mukhya() {\n    vitti a = 5 \u2013 2\n    likha(a, "\\n")\n}\n', '2:17', "'\u2013' (U+2013)", 'Sanket: vyavakalana-chihnam - (U+002D) likhyatam'),
    ('em-dash', 'mukhya() {\n    vitti a = 5 \u2014 2\n}\n', '2:17', "'\u2014' (U+2014)", 'Sanket: vyavakalana-chihnam - (U+002D) likhyatam'),
    ('minus-sign', 'mukhya() {\n    vitti a = 5 \u2212 2\n}\n', '2:17', "'\u2212' (U+2212)", 'Sanket: vyavakalana-chihnam - (U+002D) likhyatam'),
    ('no-break-space', 'mukhya() {\n    vitti a\u00a0= 5\n}\n', '2:12', '(U+00A0)', 'Sanket: sadharanah avakashah (U+0020) likhyatam'),
    ('zero-width-space', 'mukhya() {\n    vitti a\u200b = 5\n}\n', '2:12', '(U+200B)', 'Sanket: adrishyam aksharam etat - apaniyatam'),
    ('bom-in-a-line', 'mukhya() {\n    vitti a \ufeff= 5\n}\n', '2:13', '(U+FEFF)', 'Sanket: adrishyam aksharam etat - apaniyatam'),
    ('apostrophe', "mukhya() {\n    likha('hi')\n}\n", '2:11', "''' (U+0027)", f'Sanket: Sutram-bhashayam vakyam {Q} {Q} madhye likhyate - {Q} (U+0022) likhyatam'),
    ('curly-apostrophe', 'mukhya() {\n    likha(\u2018hi\u2019)\n}\n', '2:11', "'\u2018' (U+2018)", f'Sanket: Sutram-bhashayam vakyam {Q} {Q} madhye likhyate - {Q} (U+0022) likhyatam'),
    ('times', 'mukhya() {\n    likha(3 \u00d7 4)\n}\n', '2:13', "'\u00d7' (U+00D7)", 'Sanket: gunana-chihnam * (U+002A) likhyatam'),
    ('not-equal', 'mukhya() {\n    yadi (3 \u2260 4) {\n    }\n}\n', '2:13', "'\u2260' (U+2260)", 'Sanket: != likhyatam'),
    ('rupee', 'mukhya() {\n    likha(100 \u20b9)\n}\n', '2:15', "'\u20b9' (U+20B9)", None),
    ('dollar', 'mukhya() {\n    vitti a = 5 $ 3\n}\n', '2:17', "'$' (U+0024)", None),
    ('at-sign', 'mukhya() {\n    vitti a = @5\n}\n', '2:15', "'@' (U+0040)", None),
    ('form-feed', 'mukhya() {\n    likha(3)\x0c\n}\n', '2:13', '(U+000C)', None),
    ('emoji', 'mukhya() {\n    likha(3) \U0001F600\n}\n', '2:14', "'\U0001F600' (U+1F600)", None),
    ('first-of-two', 'mukhya() {\n    vitti a = 5 $ 3 \u2013 1\n}\n', '2:17', "'$' (U+0024)", None),
]

# (name, source, what it prints)
ACCEPTED = [
    ('in-comments-and-strings',
     '# \u201ccurly\u201d \u2013 dash \u20b9 $ @ in a hash comment\n// \u201ccurly\u201d \u00a0 in a slash comment\n/* \u2014 em dash\n   \u200b on two lines */\n'
     'mukhya() {\n    likha("\u201cquoted\u201d \u2013 \u20b9100 $ @ in a string\\n")   # and \u2019 after the code\n}\n',
     '\u201cquoted\u201d \u2013 \u20b9100 $ @ in a string'),
    ('byte-order-mark-first', '\ufeffmukhya() {\n    likha(7, "\\n")\n}\n', '7'),
    ('devanagari-digits', 'mukhya() {\n    vitti a = \u096b - \u0968\n    likha(a, "\\n")\n}\n', '3'),
    ('ascii-as-before', 'mukhya() {\n    vitti a = 5 - 2\n    likha(a, "\\n")\n}\n', '3'),
]


def check(ok, what):
    global checks, fails
    checks += 1
    print(('ok    ' if ok else 'FAIL  ') + what)
    fails += not ok


def run(cmd, cwd):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, timeout=120)
    return p.returncode, (p.stdout + p.stderr).decode('utf-8', 'replace')


def main():
    compiler = os.path.join(ROOT, 'sutram_compiler')
    if '--compiler' in sys.argv:
        compiler = os.path.abspath(sys.argv[sys.argv.index('--compiler') + 1])
    d = tempfile.mkdtemp(prefix='r182_')
    try:
        for name, src, pos, text, hint in REFUSED:
            open(os.path.join(d, name + '.sm'), 'w', encoding='utf-8').write(src)
            rc, out = run([compiler, name + '.sm', name + '.bin'], d)
            lines = out.split('\n')
            want = f'{name}.sm:{pos}: Sutram truti [E_AGYAT_AKSHAR]: agyat akshar {text}'
            sanket = [l for l in lines if l.startswith('Sanket:')]
            ok = (rc == 1 and lines[0] == want and not os.path.exists(os.path.join(d, name + '.bin'))
                  and (sanket == [hint] if hint else sanket == []) and len(lines) > 2 and lines[2].strip() == '^')
            check(ok, f'{name}: refused at {pos}, {text}' + (f' - {hint}' if hint else ' - no Sanket') + ('' if ok else f'  GOT {out[:160]!r}'))
        for name, src, prints in ACCEPTED:
            open(os.path.join(d, name + '.sm'), 'w', encoding='utf-8').write(src)
            rc, out = run([compiler, name + '.sm', name + '.bin'], d)
            rc2, out2 = run([os.path.join(d, name + '.bin')], d) if rc == 0 else (1, out)
            check(rc == 0 and rc2 == 0 and out2.strip() == prints, f'{name}: compiles and prints {prints!r}' + ('' if out2.strip() == prints else f'  GOT {out2[:120]!r}'))
    finally:
        shutil.rmtree(d, ignore_errors=True)
    print(f'r182 unknown character: {checks} checks, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
