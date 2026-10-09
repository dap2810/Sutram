#!/usr/bin/env python3
"""Verify + merge a tree returned by the other AI (ChatGPT) into our working tree.

  python3 tools/merge_from_chatgpt.py <returned.zip> [--handoff <file>]          # verify only
  python3 tools/merge_from_chatgpt.py <returned.zip> [--handoff <file>] --apply  # merge

What it does, in order:
  1. unzip the returned tree (handles a wrapper folder OR a bare tree)
  2. if --handoff is given, check their claimed source SHA-256 against the real one
  3. build THEIR compiler (Linux) and run OUR suite against it
  4. also assemble the Windows host and confirm it is a PE32+ image
  5. diff their src against ours: code size, hunks, keyword/builtin adds AND removals,
     plus a philosophy guard (no English keyword aliases)
  6. --apply: take their src/, bring in any NEW examples/expectations, merge the test
     harness (taking theirs when it has features ours lacks, always keeping the
     SUTRAM_COMPILER override), then re-run the suite on the merged tree
  7. print a report ending in the single most useful next action

Ownership rule enforced here: docs/books belong to Sarvam, src/ belongs to whoever
holds the compiler this round.
"""
import glob, os, re, shutil, subprocess, sys, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = "/tmp/sutram_returned"
MINE = os.path.join(ROOT, "src", "sutram_compiler.asm")
NASM = shutil.which("nasm") or os.path.join(ROOT, "nasm", "usr", "bin", "nasm")


def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def find_tree(base):
    for root, dirs, files in os.walk(base):
        if os.path.basename(root) == "src" and "sutram_compiler.asm" in files:
            return os.path.dirname(root)
    return None


def sha256(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def claimed_sha(handoff_path):
    txt = open(handoff_path, errors="replace").read()
    m = re.search(r"SHA-256[^`]*`([0-9a-fA-F]{64})`", txt)
    return m.group(1).lower() if m else None


def inventory(asm_path):
    src = open(asm_path, errors="replace").read()
    kw = set(re.findall(r'dq (kw_[a-z_]+),\s*TOK_KEYWORD', src))
    bn = set(re.findall(r'dq (bn_[a-z0-9_]+),\s*TOK_BUILTIN', src))
    return kw, bn, len(src)


def build_linux(tree):
    # build in-tree: the harness (and `ayojan`'s compiler-dir lookup) expects the
    # compiler to sit at the tree root, so an out-of-tree build gives false failures.
    obj, exe = os.path.join(tree, "mrg.o"), os.path.join(tree, "sutram_compiler")
    r = sh([NASM, "-f", "elf64", os.path.join(tree, "src", "sutram_compiler.asm"), "-o", obj])
    if r.returncode != 0:
        return None, f"LINUX BUILD FAILED\n{r.stderr[:1500]}"
    r = sh(["ld", "-o", exe, obj])
    if r.returncode != 0:
        return None, f"LINK FAILED\n{r.stderr[:800]}"
    return exe, None


def build_windows(tree):
    obj, exe = "/tmp/mrgw.obj", "/tmp/mrg_sutram.exe"
    r = sh([NASM, "-f", "win64", "-dWINDOWS", "-I.", os.path.join(tree, "src", "sutram_compiler.asm"), "-o", obj],
           cwd=tree)
    if r.returncode != 0:
        return f"WINDOWS BUILD FAILED\n{r.stderr[:1200]}"
    r = sh(["ld", "-mi386pep", "--entry=_start", "-o", exe, obj])
    if r.returncode != 0:
        return f"WINDOWS LINK FAILED\n{r.stderr[:800]}"
    magic = open(exe, "rb").read(2)
    return f"windows build OK · PE32+ {'yes' if magic == b'MZ' else 'NO (' + repr(magic) + ')'}"


def suite(exe, tree=ROOT):
    env = dict(os.environ, SUTRAM_COMPILER=exe)
    r = sh([sys.executable, os.path.join(tree, "tests", "run_tests.py")], env=env, cwd=tree)
    # note: tests that exercise module lookup rely on the compiler living at the tree
    # root; SUTRAM_COMPILER only overrides the path the harness invokes.
    tail = "\n".join(r.stdout.strip().splitlines()[-4:])
    return r.returncode, tail


def diff_summary(theirs, ours):
    kw_t, bn_t, sz_t = inventory(theirs)
    kw_o, bn_o, sz_o = inventory(ours)
    r = sh(["diff", "-u", ours, theirs])
    hunks = len(re.findall(r'^@@', r.stdout, re.M))
    out = [f"code size: ours {sz_o:,} B  ->  theirs {sz_t:,} B  ({sz_t - sz_o:+,})",
           f"diff hunks: {hunks}",
           f"new keywords:  {sorted(kw_t - kw_o) or 'none'}",
           f"new builtins:  {sorted(bn_t - bn_o) or 'none'}"]
    if kw_o - kw_t:
        out.append(f"!! keywords REMOVED: {sorted(kw_o - kw_t)}")
    if bn_o - bn_t:
        out.append(f"!! builtins REMOVED: {sorted(bn_o - bn_t)}")
    src = open(theirs, errors="replace").read()
    if re.search(r'\b(kw_english|kw_print|kw_var)\b', src):
        out.append("!! possible English keyword aliases added — check philosophy")
    # undefined-symbol guard: the Round-4 build break was an AST_* name with no equ
    defined = set(re.findall(r'^([A-Za-z_][A-Za-z0-9_]*)\s+equ\b', src, re.M))
    used = set(re.findall(r'\b(AST_[A-Z_]+|KW_[A-Z_]+|BN_[A-Z_]+)\b', src))
    missing = sorted(u for u in used if u not in defined and not re.search(r'\b%s\s+equ' % re.escape(u), src))
    if missing:
        out.append(f"!! symbols used but not defined (build risk): {missing}")
    return "\n".join(out), r.stdout


def merge_harness(tree):
    """Take their harness when it has features ours lacks; always keep the env override."""
    theirs = os.path.join(tree, "tests", "run_tests.py")
    ours = os.path.join(ROOT, "tests", "run_tests.py")
    if not os.path.exists(theirs):
        return "harness: theirs absent — kept ours"
    t = open(theirs, errors="replace").read()
    o = open(ours, errors="replace").read()
    take = ("compile_fail" in t and "compile_fail" not in o)
    if take:
        if "SUTRAM_COMPILER" not in t:
            t = t.replace('COMPILER = os.path.join(ROOT, "sutram_compiler")',
                          'COMPILER = os.environ.get("SUTRAM_COMPILER") or os.path.join(ROOT, "sutram_compiler")')
        open(ours, "w").write(t)
        return "harness: took theirs (it had features ours lacked)"
    return "harness: kept ours"


def main():
    if len(sys.argv) < 2:
        print(__doc__); return 2
    zpath = sys.argv[1]
    apply_ = "--apply" in sys.argv
    handoff = None
    if "--handoff" in sys.argv:
        handoff = sys.argv[sys.argv.index("--handoff") + 1]
    if not os.path.exists(zpath):
        print(f"no such zip: {zpath}"); return 2

    shutil.rmtree(WORK, ignore_errors=True)
    os.makedirs(WORK, exist_ok=True)
    with zipfile.ZipFile(zpath) as z:
        z.extractall(WORK)
    tree = find_tree(WORK)
    if not tree:
        print("could not find src/sutram_compiler.asm in the returned zip"); return 2
    theirs = os.path.join(tree, "src", "sutram_compiler.asm")
    print(f"returned tree: {tree}\n")

    print("=== 1. claimed source SHA-256")
    real = sha256(theirs)
    if handoff and os.path.exists(handoff):
        claim = claimed_sha(handoff)
        if claim:
            print(f"claimed {claim[:16]}…  real {real[:16]}…  {'MATCH' if claim == real else 'MISMATCH'}")
        else:
            print(f"no SHA found in {handoff}; real {real[:16]}…")
    else:
        print(f"real {real[:16]}…   (pass --handoff <file> to check their claim)")

    print("\n=== 2. build their compiler + run our suite against it")
    exe, err = build_linux(tree)
    print(err if err else f"linux build OK")
    if exe:
        rc, tail = suite(exe)
        print(f"suite exit={rc}\n{tail}")
    print(build_windows(tree))

    print("\n=== 3. source delta")
    summary, _ = diff_summary(theirs, MINE)
    print(summary)

    if apply_:
        print("\n=== 4. merge")
        shutil.copy(theirs, MINE)
        shutil.copy(theirs, os.path.join(ROOT, "sutram.asm"))
        print("took their src/ (and synced the working sutram.asm); kept our docs/")
        added = []
        for rel in ("examples", "tests/expect"):
            for src_f in glob.glob(os.path.join(tree, rel, "*")):
                name = os.path.basename(src_f)
                dst = os.path.join(ROOT, rel, name)
                if not os.path.exists(dst):
                    shutil.copy(src_f, dst); added.append(f"{rel}/{name}")
        print(f"new files taken: {added or 'none'}")
        print(merge_harness(tree))
        exe2, err2 = build_linux(ROOT)
        if exe2:
            rc, tail = suite(exe2)
            print(f"merged build OK · suite exit={rc}\n{tail}")
        else:
            print(err2)
        print("\nnext: fix any assembler error, then update books/docs and repackage")
    else:
        print("\n(dry run — nothing changed. re-run with --apply to merge)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
