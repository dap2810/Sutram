#!/usr/bin/env python3
"""Verify every language pack accepts the current keyword set.

A pack that lists a word the compiler rejects is worse than one that omits it,
so this does not check that the words are *present* -- it compiles a real
program written in each pack's own native words and runs it.

Covers the four keywords that were missing from every pack until v81:
kosh (growable arrays), dasham (floats), kuru (do-while), nishkriya (inline asm).

Run: python3 tools/test_lang_packs.py
"""
import io, os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMPILER = os.environ.get("SUTRAM_COMPILER") or os.path.join(ROOT, "sutram_compiler")
LANGS = ["hindi", "bengali", "gujarati", "kannada", "malayalam",
         "marathi", "odia", "punjabi", "tamil", "telugu"]


def pack_words(name):
    """The pack as shipped: {sanskrit_keyword: native_word}."""
    d = {}
    with io.open(os.path.join(ROOT, "lang", f"{name}.lang"), encoding="utf-8") as f:
        for line in f:
            p = line.rsplit(None, 1)
            if len(p) == 2:
                d[p[1]] = p[0]
    return d


def compile_run(src, lang, tmpdir):
    sp = os.path.join(tmpdir, "t.sm")
    with io.open(sp, "w", encoding="utf-8") as f:
        f.write(src)
    out = os.path.join(tmpdir, "t.bin")
    r = subprocess.run([COMPILER, "--lang", lang, sp, out],
                       capture_output=True, text=True, timeout=60)
    if not os.path.exists(out):
        return None, (r.stdout + r.stderr).strip()[:100]
    os.chmod(out, 0o755)
    ex = subprocess.run([out], capture_output=True, text=True, timeout=30)
    return ex, None


CASES = [
    # name, builds source from the pack's words, expected stdout, expected exit
    ("kosh + dasham",
     lambda w: (f"{w['mukhya']}() {{\n"
                f"    {w['kosh']} xs[4]\n"
                f"    kosh_push(xs, 10)\n"
                f"    kosh_push(xs, 20)\n"
                f"    {w['dasham']} f = 1.5\n"
                f"    {w['likha']}(kosh_len(xs))\n"
                f"    {w['likha']}(f)\n"
                f"}}\n"),
     "2\n1.500000", 0),
    ("kuru (do-while)",
     lambda w: (f"{w['mukhya']}() {{\n"
                f"    vitti i = 0\n"
                f"    {w['kuru']} {{\n"
                f"        i = i + 1\n"
                f"        {w['likha']}(i)\n"
                f"    }} {w['yavat']} (i < 3)\n"
                f"}}\n"),
     "1\n2\n3", 0),
    ("nishkriya (inline asm)",
     lambda w: (f"{w['mukhya']}() {{\n"
                f"    {w['nishkriya']}(\"B8 3C 00 00 00\")\n"
                f"    {w['nishkriya']}(\"BF 2A 00 00 00\")\n"
                f"    {w['nishkriya']}(\"0F 05\")\n"
                f"}}\n"),
     "", 42),
]

if __name__ == "__main__":
    fails = 0
    for lang in LANGS:
        w = pack_words(lang)
        for name, build, want_out, want_exit in CASES:
            missing = [k for k in ("mukhya", "kosh", "dasham", "likha", "yavat",
                                   "kuru", "nishkriya") if k not in w]
            if missing:
                print(f"  FAIL  {lang:10s} {name:24s} pack missing {missing}")
                fails += 1
                continue
            tmp = tempfile.mkdtemp()
            ex, err = compile_run(build(w), lang, tmp)
            if ex is None:
                print(f"  FAIL  {lang:10s} {name:24s} compile error: {err}")
                fails += 1
            else:
                ok = ex.stdout.strip() == want_out.strip() and ex.returncode == want_exit
                if not ok:
                    fails += 1
                    print(f"  FAIL  {lang:10s} {name:24s} "
                          f"got {ex.stdout.strip()!r} exit={ex.returncode}, "
                          f"wanted {want_out.strip()!r} exit={want_exit}")
    total = len(LANGS) * len(CASES)
    print(f"\n  {total - fails}/{total} pack checks pass "
          f"({len(LANGS)} packs x {len(CASES)} keyword groups)")
    sys.exit(1 if fails else 0)
