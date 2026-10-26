#!/usr/bin/env python3
"""Sutram stdlib signature *floor* (no NASM, no subprocesses).

Compare lib/*.smlib prakriya declarations with signatures in the FIRST
Function-column cells of docs/sutram-stdlib.html, keyed by module and name.
Names, arity, declared kinds, and parameter labels are compared; not behaviour.

Run from either location:
    python3 ChatGPT-to-Sarvam/tools/check_doc_signatures.py --repo-root .
    python3 tools/check_doc_signatures.py   # after tools-owner copies it
Exit 0 for matching signatures; 1 for drift/read/parse/duplicate problems.
"""
import argparse
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
import re
import sys

IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
DECL = re.compile(r"^\s*prakriya\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(([^)]*)\)")
START = re.compile(r"^\s*prakriya\b")
DOC_SIG = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*\(([^)]*)\)\s*$")


@dataclass(frozen=True)
class Signature:
    module: str
    name: str
    labels: tuple[str, ...]
    kinds: tuple[str, ...]
    where: str

    @property
    def arity(self):
        return len(self.labels)

    def brief(self):
        return f"{self.module}.{self.name}({', '.join(self.labels)})"


def signature(module, name, args, where):
    labels, kinds = [], []
    if args.strip():
        for chunk in args.split(","):
            words = chunk.strip().split()
            if not words or not all(IDENT.fullmatch(w) for w in words):
                raise ValueError(f"{where}: invalid parameter expression {chunk!r}")
            labels.append(words[-1])
            kinds.append(" ".join(words[:-1]) if len(words) > 1 else "untyped")
    return Signature(module, name, tuple(labels), tuple(kinds), where)


def read_source(lib_dir):
    out, errors, modules = [], [], []
    if not lib_dir.is_dir():
        return out, [f"missing library directory: {lib_dir}"], modules
    paths = sorted(lib_dir.glob("*.smlib"))
    if not paths:
        errors.append(f"no .smlib files found in {lib_dir}")
    for path in paths:
        module = path.stem
        modules.append(module)
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeError) as exc:
            errors.append(f"{path}: {exc}")
            continue
        for line_number, line in enumerate(lines, 1):
            if not START.match(line):
                continue
            where = f"{path.as_posix()}:{line_number}"
            m = DECL.match(line)
            if not m:
                errors.append(f"{where}: unparsed prakriya declaration: {line.strip()}")
                continue
            try:
                out.append(signature(module, m.group(1), m.group(2), where))
            except ValueError as exc:
                errors.append(str(exc))
    return out, errors, modules


class ReferenceParser(HTMLParser):
    """Only read <tr>'s FIRST <td><code>...</code></td> in module tables."""

    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.module = None
        self.modules = []
        self.row = False
        self.td_index = -1
        self.code = False
        self.code_fragments = []
        self.signatures = []
        self.errors = []
        self.table = False
        self.row_number = 0
        self.code_line = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "h2" and "id" in attrs:
            self.module = attrs["id"]
            self.modules.append(self.module)
        elif tag == "table":
            self.table = True
        elif tag == "tr" and self.table:
            self.row = True
            self.td_index = -1
            self.row_number += 1
        elif tag == "td" and self.row:
            self.td_index += 1
        elif tag == "code" and self.row and self.td_index == 0:
            self.code = True
            self.code_line = self.getpos()[0]
            self.code_fragments = []

    def handle_data(self, data):
        if self.code:
            self.code_fragments.append(data)

    def handle_endtag(self, tag):
        if tag == "code" and self.code:
            self.code = False
            text = "".join(self.code_fragments).strip()
            where = f"{self.path.as_posix()}:{self.code_line}"
            match = DOC_SIG.fullmatch(text)
            if not self.module:
                self.errors.append(f"{where}: signature without module heading: {text!r}")
            elif not match:
                self.errors.append(f"{where}: unparsed documented signature: {text!r}")
            else:
                try:
                    self.signatures.append(signature(self.module, match.group(1), match.group(2), where))
                except ValueError as exc:
                    self.errors.append(str(exc))
        elif tag == "tr":
            self.row = False
            self.td_index = -1
        elif tag == "table":
            self.table = False


def read_document(path):
    if not path.is_file():
        return [], [f"missing reference HTML: {path}"], []
    parser = ReferenceParser(path)
    try:
        parser.feed(path.read_text(encoding="utf-8"))
        parser.close()
    except (OSError, UnicodeError, ValueError) as exc:
        parser.errors.append(f"{path}: {exc}")
    if not parser.signatures:
        parser.errors.append(f"{path}: no documented signatures found")
    return parser.signatures, parser.errors, parser.modules


def index(items, side, errors):
    out = {}
    for item in items:
        key = (item.module, item.name)
        if key in out:
            errors.append(f"duplicate {side}: {item.brief()} at {out[key].where} and {item.where}")
        else:
            out[key] = item
    return out


def compare(source, document, source_modules, doc_modules):
    errors = []
    for m in sorted(set(doc_modules)):
        if doc_modules.count(m) != 1:
            errors.append(f"DUPLICATE HTML MODULE SECTION: {m} ({doc_modules.count(m)} occurrences)")
    src = index(source, "source declaration", errors)
    doc = index(document, "documented signature", errors)
    for module in sorted(set(source_modules) - set(doc_modules)):
        errors.append(f"SOURCE-ONLY MODULE: {module}")
    for module in sorted(set(doc_modules) - set(source_modules)):
        errors.append(f"DOCUMENT-ONLY MODULE: {module}")
    for key in sorted(set(src) - set(doc)):
        s = src[key]
        errors.append(f"SOURCE-ONLY: {s.brief()} at {s.where}")
    for key in sorted(set(doc) - set(src)):
        s = doc[key]
        errors.append(f"DOCUMENT-ONLY: {s.brief()} at {s.where}")
    for key in sorted(set(src) & set(doc)):
        a, b = src[key], doc[key]
        if a.arity != b.arity:
            errors.append(f"ARITY MISMATCH: {a.module}.{a.name}: source {a.arity} at {a.where}; doc {b.arity} at {b.where}")
        if a.kinds != b.kinds:
            errors.append(f"KIND MISMATCH: {a.module}.{a.name}: source {a.kinds} at {a.where}; doc {b.kinds} at {b.where}")
        if a.labels != b.labels:
            errors.append(f"PARAMETER LABEL MISMATCH: {a.module}.{a.name}: source {a.labels} at {a.where}; doc {b.labels} at {b.where}")
    return errors


def find_root(path):
    for parent in (path.parent, *path.parents):
        if (parent / "lib").is_dir() and (parent / "docs" / "sutram-stdlib.html").is_file():
            return parent
    return path.parent


def main(argv=None):
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--repo-root", type=Path, help="Repository root; otherwise discovered from script path")
    cli.add_argument("--lib-dir", type=Path, help="Optional fixture/source library directory")
    cli.add_argument("--html", type=Path, help="Optional fixture/reference HTML")
    args = cli.parse_args(argv)
    root = args.repo_root if args.repo_root else find_root(Path(__file__).resolve())
    lib_dir = args.lib_dir if args.lib_dir else root / "lib"
    html = args.html if args.html else root / "docs" / "sutram-stdlib.html"
    source, source_errors, src_modules = read_source(lib_dir)
    docs, doc_errors, doc_modules = read_document(html)
    issues = source_errors + doc_errors + compare(source, docs, src_modules, doc_modules)
    print("SUTRAM DOC SIGNATURE FLOOR — compares names, arity and declared parameter kinds, NOT behaviour.")
    print("NO NASM / NATIVE COMPILER / RUNTIME ACCEPTANCE IS RUN BY THIS CHECK.")
    print(f"Source: {len(src_modules)} modules, {len(source)} prakriya declarations")
    print(f"Document: {len(doc_modules)} modules, {len(docs)} function signatures")
    print(f"Issues: {len(issues)}")
    for item in issues:
        print("FAIL: " + item)
    print("RESULT: " + ("FAIL" if issues else "PASS (static signature floor only)"))
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
