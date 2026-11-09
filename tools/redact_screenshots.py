#!/usr/bin/env python3
"""tools/redact_screenshots.py - R164/R165: the text gate cannot read an image, so read each tracked screenshot with
tesseract and cover the owner's account name, computer name, projects-folder name and an OS build number where they
appear (a destination folder, a prompt, an About box). Only those characters are covered - the rest of the path and
the picture stay, so the screenshot still shows what it was taken to show.

    python3 tools/redact_screenshots.py [--apply] [--record FILE.json] [PATH ...]

Without --apply it reports what it would cover. The names are matched by the SHA-256 of the word, from
tests/r159/test_no_personal_paths.py; they are not written here. OCR misses text it cannot read (small, faint, on a
coloured ground), so a screenshot this passes is not proven clean - it is the best a machine reading can do.
"""
import hashlib
import io
import json
import os
import re
import subprocess
import sys

from PIL import Image, ImageDraw

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.insert(0, os.path.join(ROOT, 'tests', 'r159'))
import test_no_personal_paths as gate  # noqa: E402

SCALE = 2
BUILD = re.compile(r'(?:(?<=build )|(?<=10\.0\.)|(?<=5\.1\.))2[0-9]{4}(?:\.[0-9]+)?')


def spans(word, prev):
    """Character spans of a word to cover."""
    out = []
    for m in re.finditer(r'[A-Za-z0-9_]+', word):
        if hashlib.sha256(m.group(0).lower().encode()).hexdigest() in gate.NAME_HASHES:
            out.append((m.start(), m.end()))
    for m in re.finditer(r'2[0-9]{4}(?:\.[0-9]+)?', word):
        before = word[:m.start()]
        if before.endswith(('10.0.', '5.1.')) or (before == '' and prev.lower() in ('build', 'build:')):
            out.append((m.start(), m.end()))
    return out


def ocr(img):
    big = img.convert('RGB').resize((img.width * SCALE, img.height * SCALE), Image.LANCZOS)
    buf = io.BytesIO()
    big.save(buf, format='PNG')
    r = subprocess.run(['tesseract', 'stdin', 'stdout', '--psm', '11', 'tsv'], input=buf.getvalue(),
                       capture_output=True, check=True)
    words = []
    for line in r.stdout.decode('utf-8', 'replace').splitlines()[1:]:
        f = line.split('\t')
        if len(f) == 12 and f[11].strip():
            words.append((int(f[6]) / SCALE, int(f[7]) / SCALE, int(f[8]) / SCALE, int(f[9]) / SCALE, f[11]))
    return words


def boxes_for(img):
    words = ocr(img)
    out = []
    prev = ''
    for x, y, w, h, t in words:
        for a, b in spans(t, prev):
            n = max(len(t), 1)
            cw = w / n                     # one character's width, roughly: the box is widened by one each side,
            x0 = x + cw * a - cw - 2       # because a proportional estimate inside a word can be a character off
            x1 = x + cw * b + cw + 2
            out.append((int(x0), int(y - 2), int(x1 + 0.999), int(y + h + 2.999), t[a:b]))
        prev = t
    return out


def main(argv):
    apply = '--apply' in argv
    record = argv[argv.index('--record') + 1] if '--record' in argv else None
    only = [a for a in argv if not a.startswith('--') and a != record]
    os.chdir(ROOT)
    files = subprocess.run(['git', 'ls-files', '-z'], capture_output=True, check=True).stdout.decode().split('\0')[:-1]
    imgs = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
    if only:
        imgs = [f for f in imgs if any(f == o or f.startswith(o.rstrip('/') + '/') for o in only)]
    rec, covered, kinds = [], 0, {}
    for f in imgs:
        try:
            img = Image.open(f)
            img.load()
        except Exception as e:  # an image PIL cannot read is reported, not skipped silently
            print(f'NOT READ  {f}: {e}')
            continue
        bx = boxes_for(img)
        if not bx:
            continue
        for *_, t in bx:
            k = gate.NAME_HASHES.get(hashlib.sha256(t.lower().encode()).hexdigest(), 'build')
            kinds[k] = kinds.get(k, 0) + 1
        covered += len(bx)
        print(f'{len(bx):3d}  {f}')
        if apply:
            before = open(f, 'rb').read()
            out = img.convert('RGBA') if img.mode in ('P', 'LA', 'RGBA') else img.convert('RGB')
            d = ImageDraw.Draw(out)
            for x0, y0, x1, y1, _ in bx:
                d.rectangle([x0, y0, x1, y1], fill=(128, 128, 128, 255) if out.mode == 'RGBA' else (128, 128, 128))
            fmt = 'PNG' if f.lower().endswith('.png') else None
            out.save(f, format=fmt) if fmt else out.save(f)
            rec.append({'path': f, 'covered': len(bx), 'before_sha256': hashlib.sha256(before).hexdigest(),
                        'after_sha256': hashlib.sha256(open(f, 'rb').read()).hexdigest()})
    print(f'{len(imgs)} images read; {sum(1 for _ in rec) if apply else "-"} changed; {covered} places covered: '
          + ', '.join(f'{k} {v}' for k, v in sorted(kinds.items())))
    if apply and record:
        json.dump({'scope': 'R164/R165: screenshots, the owner\'s names and OS build numbers covered where OCR read them',
                   'note': 'tesseract --psm 11 at 2x; only the matched characters are covered (grey); the history keeps '
                           'the original images', 'files': rec}, open(record, 'w'), indent=1)
        open(record, 'a').write('\n')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
