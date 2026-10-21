#!/usr/bin/env python3
"""ROUND-29: separate compilation.  `sutram_build.py main.sm -o out`

Walks the module graph that `yoj` builds, compiles every module ONCE with
`sutram_compiler --separate`, and links the objects with sutram-link.

In a `--separate` compile a module that `yoj` brings in is still read, parsed
and checked - so a call into it is checked for its arity and gets the right
return type (dasham or not) - but its prakriyas generate no code there: the
calls become holes, and the module's code is in its own object, once.

The ordinary one-pass compile is untouched: `sutram_compiler in.sm out`
still inlines every module, exactly as before.  This tool is opt-in.

Module lookup is the compiler's own (B5), always relative to the ROOT program,
because an inlined module's text is compiled as if it were in the root file:
  1. <root's directory>/lib/<name>.smlib
  2. <the compiler's directory>/lib/<name>.smlib
  3. <current directory>/lib/<name>.smlib
`yoj` is found the way the compiler finds it: at any byte that is not inside a
`#` or `//` comment, the three bytes `yoj` followed by a space, tab or newline.

Version 1 refuses, plainly (exit 1):
  * a namespaced import (`yoj m@alias`), which rewrites the module's names;
  * a module that cannot be found.
A module's `vitti` is held once, in its own object (R30).
Exit status: 0 linked, 1 a refusal or a compile/link error, 2 usage.
"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)


def yoj_names(text: bytes):
    """The module names a source names with `yoj`, in order, as the compiler sees them."""
    names = []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c == 0x23 or (c == 0x2F and i + 1 < n and text[i + 1] == 0x2F):
            j = text.find(b"\n", i)
            i = n if j < 0 else j + 1
            continue
        if text[i:i + 3] == b"yoj" and i + 3 < n and text[i + 3] in b" \n\t\r":
            i += 3
            while i < n and text[i] in b" \n\t\r":
                i += 1
            j = i
            while j < n and text[j] not in b" \n\t\r":
                j += 1
            if j > i:
                names.append(text[i:j].decode("utf-8", "strict"))
            i = j
            continue
        i += 1
    return names


def resolve(name, root, compiler):
    for base in (os.path.dirname(os.path.abspath(root)),
                 os.path.dirname(os.path.abspath(compiler)),
                 os.getcwd()):
        p = os.path.join(base, "lib", name + ".smlib")
        if os.path.isfile(p):
            return os.path.realpath(p)
    return None


def module_graph(root, compiler):
    """[(path, [direct module paths])] for the root and every module it reaches, root first."""
    order, seen, todo = [], {os.path.realpath(root)}, [os.path.realpath(root)]
    while todo:
        path = todo.pop(0)
        with open(path, "rb") as f:
            names = yoj_names(f.read())
        deps = []
        for name in names:
            if "@" in name:
                raise SystemExit(f"sutram-build: {path}: yoj {name}: a namespaced yoj is not "
                                 f"separately compiled in this version")
            dep = resolve(name, root, compiler)
            if dep is None:
                raise SystemExit(f"sutram-build: {path}: yoj {name}: module not found")
            if dep not in deps:
                deps.append(dep)
            if dep not in seen:
                seen.add(dep)
                todo.append(dep)
        order.append((path, deps))
    return order


def main(argv):
    args = list(argv)
    compiler = os.path.join(REPO, "sutram_compiler")
    linker = os.path.join(REPO, "sutram-link")
    keep = None
    out = None
    show_graph = False
    while args and args[0].startswith("--"):
        flag = args.pop(0)
        if flag == "--graph":
            show_graph = True
        elif flag in ("--compiler", "--linker", "--keep") and args:
            val = args.pop(0)
            if flag == "--compiler":
                compiler = val
            elif flag == "--linker":
                linker = val
            else:
                keep = val
        else:
            args.insert(0, flag)
            break
    if len(args) == 3 and args[1] == "-o":
        root, out = args[0], args[2]
    elif len(args) == 1 and show_graph:
        root = args[0]
    else:
        print("usage: sutram_build.py [--compiler C] [--linker L] [--keep DIR] main.sm -o out\n"
              "       sutram_build.py --graph main.sm", file=sys.stderr)
        return 2
    try:
        graph = module_graph(root, compiler)
    except SystemExit as e:
        print(e, file=sys.stderr)
        return 1
    if show_graph:
        for path, deps in graph:
            print(os.path.relpath(path))
            for d in deps:
                print("  yoj", os.path.relpath(d))
        if out is None:
            return 0
    work = keep or tempfile.mkdtemp(prefix="sutram-build-")
    os.makedirs(work, exist_ok=True)
    objects = []
    for k, (path, _deps) in enumerate(graph):
        obj = os.path.join(work, f"{k:03d}-{os.path.basename(path)}.smo")
        r = subprocess.run([os.path.abspath(compiler), "--separate", path, os.path.abspath(obj),
                            os.path.abspath(root)],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if r.returncode != 0 or not os.path.isfile(obj):
            sys.stdout.write(r.stdout.decode("utf-8", "replace"))
            print(f"sutram-build: {path}: did not compile", file=sys.stderr)
            return 1
        objects.append(obj)
    r = subprocess.run([linker, out] + [os.path.abspath(o) for o in objects], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if r.returncode != 0:
        sys.stdout.write(r.stdout.decode("utf-8", "replace"))
        return 1
    print(f"sutram-build: {len(objects)} modules, each compiled once, linked to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
