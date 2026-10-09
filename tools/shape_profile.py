#!/usr/bin/env python3
"""Static, reproducible Sutram assignment-shape census (NOT a runtime profiler).

Counts source-level assignments in library/modules/examples.  It deliberately does
not extrapolate dynamic execution frequency from source counts; a statement in a
400-iteration loop and an initialization statement each count once.  The parser
recognizes common Sutram assignment shapes, not a complete Sutram grammar.

Examples:
  python3 tools/shape_profile.py --scope lib
  python3 tools/shape_profile.py --scope all --json
  python3 tools/shape_profile.py --paths lib/sankhyiki.smlib lib/madhava.smlib examples/126_numeric_pipeline.sm
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IDENT = r"[^\W\d]\w*"  # Unicode-aware, includes Devanagari spelling
DECL = re.compile(rf"^(?P<type>vitti|dasham|वित्ति|दशम)\s+(?P<lhs>{IDENT})\s*=\s*(?P<rhs>.+)$")
ASSIGN = re.compile(rf"^(?P<lhs>{IDENT}(?:\[[^]]+\])?)\s*=(?!=)\s*(?P<rhs>.+)$")
BINARY = re.compile(rf"^(?P<left>{IDENT})\s*(?P<op>[+*\-])\s*(?P<right>{IDENT}|\d+)$")
LITERAL_LEFT = re.compile(rf"^(?P<value>\d+)\s*\+\s*(?P<right>{IDENT})$")
INDEX = re.compile(rf"{IDENT}\s*\[[^\]]+\]")
FLOAT = re.compile(r"(?<![\w.])\d+\.\d+(?!\w)")
FUNC = re.compile(rf"\bprakriya\s+{IDENT}\s*\(([^)]*)\)")
FLOAT_PARAM = re.compile(rf"\b(?:kosh\s+)?(?:dasham|दशम)\s+({IDENT})\b")
CALL = re.compile(rf"\b{IDENT}\s*\(")


def strip_comment(line: str) -> str:
    """Discard # outside single/double quotes; preserve source for shape matching."""
    result, quote, escaped = [], None, False
    for ch in line:
        if quote:
            result.append(ch)
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == quote:
                quote = None
        elif ch in ('"', "'"):
            quote = ch
            result.append(ch)
        elif ch == "#":
            break
        else:
            result.append(ch)
    return "".join(result)


def shape(lhs: str, rhs: str) -> str:
    """Disjoint assignment family (not a claim about generated machine code)."""
    if "[" in lhs:
        return "indexed_write"
    m = BINARY.fullmatch(rhs)
    if m and m['op'] in ('+', '-'):
        if m['right'].isdigit():
            imm = int(m['right'])
            if lhs == m['left']:
                return ("self_imm8" if imm <= 127 else
                        "self_imm32" if imm <= 2147483647 else "self_large_imm")
            return ("distinct_imm32" if imm <= 2147483647 else "distinct_large_imm")
        return "self_register_op" if lhs == m['left'] else "distinct_register_op"
    if m:
        return "self_multiply" if lhs == m['left'] else "distinct_multiply"
    m = LITERAL_LEFT.fullmatch(rhs)
    if m:
        return "literal_left_add"  # candidate only; no speed claim
    if re.fullmatch(IDENT, rhs):
        return "scalar_copy"
    if re.fullmatch(r"-?\d+", rhs):
        return "scalar_literal"
    return "complex_or_other"


def float_rhs_bucket(lhs: str, rhs: str) -> str:
    """Disjoint *syntactic* float assignment shapes; never runtime-weighted.

    Ordering is intentional: call expressions have highest priority, then
    indexed reads, then bare two-operand forms, and finally complex trees.
    The float-likely decision happens in classify_source() and is approximate.
    """
    if CALL.search(rhs):
        return "float_rhs_call"
    if INDEX.search(rhs):
        return "float_rhs_index"
    match = BINARY.fullmatch(rhs)
    if match:
        return ("float_rhs_simple_self" if lhs == match["left"]
                else "float_rhs_simple_distinct")
    if re.fullmatch(IDENT, rhs) or re.fullmatch(r"-?\d+(?:\.\d+)?", rhs):
        return "float_rhs_scalar"
    return "float_rhs_complex"


def classify_source(source: str) -> Counter:
    results = Counter()
    float_names: set[str] = set()
    float_arrays: set[str] = set()
    for raw in source.splitlines():
        line = strip_comment(raw)
        if not line.strip():
            continue
        # A one-line yadi { assignment } is still an assignment.
        for chunk in re.split(r"[{}]", line):
            statement = chunk.strip()
            if not statement:
                continue
            fn = FUNC.search(statement)
            if fn:
                float_names.clear()
                float_arrays.clear()
                for param in FLOAT_PARAM.finditer(fn.group(1)):
                    float_names.add(param.group(1))
                for p in fn.group(1).split(','):
                    if re.search(r"\b(?:kosh|कोश)\s+(?:dasham|दशम)\b", p):
                        ids = re.findall(IDENT, p)
                        if ids:
                            float_arrays.add(ids[-1])
                results['function_declarations'] += 1
                continue
            if re.search(r"^(?:yavat|यावत|punaravartana|पुनरावर्तन)\b", statement):
                results['loop_statements'] += 1
            if re.search(r"^(?:yadi|यदि)\b", statement):
                results['conditional_statements'] += 1
            if re.search(r"^(?:kosh|कोश)\s+(?:dasham|दशम)\s+", statement):
                match = re.search(rf"\b(?:dasham|दशम)\s+({IDENT})", statement)
                if match:
                    float_arrays.add(match.group(1))
            declaration = DECL.fullmatch(statement)
            assignment = ASSIGN.fullmatch(statement) if not declaration else None
            match = declaration or assignment
            if match is None:
                continue
            lhs, rhs = match.group('lhs'), match.group('rhs').strip()
            if declaration and match.group('type') in ('dasham', 'दशम'):
                float_names.add(lhs)
            elif declaration:
                float_names.discard(lhs)
            results['assignments_total'] += 1
            results[shape(lhs, rhs)] += 1
            if INDEX.search(rhs):
                results['rhs_index_reads'] += 1
            if CALL.search(rhs):
                results['rhs_function_calls'] += 1
            if FLOAT.search(rhs) or lhs in float_names or any(
                    re.search(rf"(?<!\w){re.escape(n)}(?!\w)", rhs)
                    for n in float_names) or any(
                    re.search(rf"(?<!\w){re.escape(n)}\s*\[", rhs)
                    for n in float_arrays):
                results['float_likely_assignments'] += 1
                results[float_rhs_bucket(lhs, rhs)] += 1
    return results


def selected_files(scope: str, paths: list[str] | None) -> list[Path]:
    if paths:
        found = []
        for raw in paths:
            p = Path(raw)
            if not p.is_absolute():
                p = ROOT / p
            if p.is_dir():
                found.extend(sorted(p.rglob('*.sm')) + sorted(p.rglob('*.smlib')))
            else:
                found.append(p)
        return sorted(set(found))
    files = []
    if scope in ('lib', 'all'):
        files += sorted((ROOT / 'lib').glob('*.smlib'))
    if scope in ('examples', 'all'):
        files += sorted((ROOT / 'examples').glob('*.sm'))
    return files


def profile(files: list[Path]) -> dict:
    totals = Counter()
    per_file = {}
    for path in files:
        if not path.is_file():
            raise FileNotFoundError(path)
        counts = classify_source(path.read_text(encoding='utf-8'))
        totals.update(counts)
        try:
            name = str(path.relative_to(ROOT))
        except ValueError:
            name = str(path)
        per_file[name] = dict(sorted(counts.items()))
    return {'method': 'static source shapes; not execution-weighted or AST-exact',
            'files': len(files), 'totals': dict(sorted(totals.items())), 'per_file': per_file}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scope', choices=('lib', 'examples', 'all'), default='lib')
    parser.add_argument('--paths', nargs='+', help='Explicit files or folders (overrides --scope)')
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--top', type=int, default=14)
    args = parser.parse_args()
    try:
        report = profile(selected_files(args.scope, args.paths))
    except (OSError, UnicodeError) as error:
        parser.error(str(error))
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    print(f"STATIC source-pattern census: {report['files']} files (NOT runtime-weighted)")
    print('The categories are syntactic approximations; no dynamic hot-path claims.')
    totals = report['totals']
    for category, count in sorted(totals.items(), key=lambda x: (-x[1], x[0]))[:args.top]:
        print(f"{category:30s} {count:5d}")
    print('\nAssignment source locations (most first):')
    for name, row in sorted(report['per_file'].items(),
                            key=lambda x: -x[1].get('assignments_total', 0))[:8]:
        print(f"  {row.get('assignments_total', 0):4d}  {name}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
