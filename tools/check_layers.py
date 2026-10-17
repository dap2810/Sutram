#!/usr/bin/env python3
"""Check the library layer markers (R28 WS1).

Every module in lib/ carries a machine-readable marker in its header:
    # layer: core | alloc | std

  core  — no allocator, no OS. Must not call nirmmita and must not
          import (yoj) an alloc- or std-layer module.
  alloc — needs a heap (uses nirmmita, or imports an alloc module).
          Must not import a std-layer module.
  std   — OS services (files, network, clocks, ...). The ONLY layer
          allowed to call OS-service builtins (see OS_BUILTINS).
          file.smlib (R30) is the first std module.

The check fails on:
  - a module with no marker, or an unknown marker;
  - a core module that calls nirmmita( (allocator use);
  - a core module that imports an alloc/std module;
  - an alloc module that imports a std module;
  - a module missing from docs/LIBRARY-LAYERS.md.
  - a core/alloc module that calls an OS-service builtin (see
    OS_BUILTINS): such a module belongs in std. A std module
    calling one is correct, not an error.

Usage: python3 tools/check_layers.py   (exit 0 = all layers honour the rules)
"""
import os
import re
import sys

# Builtins that are OS services: console/file I/O and sockets. Any
# lib module calling one of these needs a heap-independent OS, i.e.
# it belongs in layer std. (nirmmita is the allocator, not an OS
# service: mmap is its implementation detail, and an alloc module
# needs A heap, not the OS. Raw memory ops likh/pad/likh8/pad8,
# kosh_*, char_*, smaran_* are language features, not OS services.)
OS_BUILTINS = ("likha", "likha_fmt", "likh", "paadh", "band",
               "dvaram",
               "netsock", "netbind", "netlisten", "netaccept")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB = os.path.join(REPO, "lib")
DOC = os.path.join(REPO, "docs", "LIBRARY-LAYERS.md")

LAYER_RE = re.compile(r"^\s*#\s*layer:\s*(core|alloc|std)\s*$", re.M)
AYOJAN_RE = re.compile(r"^\s*yoj\s+([a-z_][a-z0-9_]*)\s*$", re.M)
NIRMMITA_RE = re.compile(r"\bnirmmita\s*\(")
COMMENT_RE = re.compile(r"^\s*#")


def strip_comments(text):
    return "\n".join(
        line for line in text.splitlines() if not COMMENT_RE.match(line))


def main():
    errors = []
    layers = {}
    for name in sorted(os.listdir(LIB)):
        if not name.endswith(".smlib"):
            continue
        shesh = name[: -len(".smlib")]
        text = open(os.path.join(LIB, name), encoding="utf-8").read()
        m = LAYER_RE.search(text)
        if not m:
            errors.append(f"{shesh}: missing '# layer:' marker")
            continue
        layers[shesh] = m.group(1)
    if errors:
        print("\n".join(errors))
        return 1
    for shesh, layer in layers.items():
        text = open(os.path.join(LIB, f"{shesh}.smlib"), encoding="utf-8").read()
        code = strip_comments(text)
        imports = sorted(set(AYOJAN_RE.findall(code)))
        uses_alloc = bool(NIRMMITA_RE.search(code))
        # An OS-service builtin call means the module belongs in
        # std — an error only when the module is NOT marked std.
        if layer != "std":
            for builtin in OS_BUILTINS:
                if re.search(rf"\b{builtin}\s*\(", code):
                    errors.append(
                        f"{shesh}: marked {layer} but calls OS builtin {builtin}"
                        " (belongs in std)")
        if layer == "core":
            if uses_alloc:
                errors.append(f"{shesh}: marked core but calls nirmmita (allocator)")
            for dep in imports:
                if dep in layers and layers[dep] in ("alloc", "std"):
                    errors.append(
                        f"{shesh}: marked core but imports {dep} ({layers[dep]})")
        elif layer == "alloc":
            for dep in imports:
                if dep in layers and layers[dep] == "std":
                    errors.append(
                        f"{shesh}: marked alloc but imports {dep} (std)")
        for dep in imports:
            if dep not in layers:
                errors.append(f"{shesh}: imports unknown module {dep}")
    try:
        doc = open(DOC, encoding="utf-8").read()
    except FileNotFoundError:
        errors.append("docs/LIBRARY-LAYERS.md missing")
        doc = ""
    for shesh in layers:
        if shesh not in doc:
            errors.append(f"{shesh}: missing from docs/LIBRARY-LAYERS.md")
    if errors:
        print("LAYER CHECK FAILED:")
        print("\n".join(f"  - {e}" for e in errors))
        return 1
    core = sorted(m for m, l in layers.items() if l == "core")
    alloc = sorted(m for m, l in layers.items() if l == "alloc")
    std = sorted(m for m, l in layers.items() if l == "std")
    print(f"layers OK: {len(core)} core, {len(alloc)} alloc, {len(std)} std")
    return 0


if __name__ == "__main__":
    sys.exit(main())
