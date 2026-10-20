#!/usr/bin/env python3
"""Traceable, conservative inventory of Sutram diagnostic message coverage.

An expected-output substring is evidence in a checked-in fixture, NOT proof
that a specific compiler label was executed in this session. New candidate
.sm programs remain unaccepted until compiled/run and independently reviewed.
Unmapped != unreachable. CLI/IDE messages are not source-program diagnostics.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
from pathlib import Path

DEFAULT_CASES = {
    'arity', 'duplicate', 'kosh_empty', 'missing_module',
    'ok', 'oob', 'parse', 'undefined_name', 'unknown_field'
}
SOURCE_ONLY_EXCLUSIONS = {
    'msg_usage': 'compiler CLI usage (invocation, not program source)',
    'msg_version': 'compiler --version CLI (invocation, not program source)',
    'msg_lang_ok': 'language pack loader status before compiling source',
    'msg_lang_fail': 'language pack loader failure before compiling source',
    'msg_shell_banner': 'interactive compiler shell startup',
    'msg_shell_bye': 'interactive compiler shell exit',
    'msg_shell_help': 'interactive shell help',
    'msg_open_err': 'CLI input-file opening failure',
}
# These existing files or new probes show a plausible path to a diagnostic.
# The script deliberately does NOT upgrade them to verified expected-output
# coverage merely because their filenames look right.
PROBE_CANDIDATES = {
    'r50_msg_setchar_arity': 'tests/r83/cases/setchar_bad_arity.sm',
    'r52_msg_dvaram_arity': 'tests/r52_check/dvaram_bad_arity.sm',
    'r52_msg_charat_arity': 'tests/r52_check/char_at_bad_arity.sm',
    'r52_msg_charcode_arity': 'tests/r52_check/char_code_bad_arity.sm',
    'r55_msg_proto_duplicate': 'tests/r55_check/prototype_duplicate.sm',
    'r56_msg_global_duplicate': 'tests/r56_check/duplicate_global.sm',
    'msg_undefined_func': 'examples/69_undefined_function.sm',
    'msg_kosh_peek_empty': 'tests/r83/cases/empty_kosh_peek.sm',
    'msg_kosh_dequeue_empty': 'tests/r83/cases/empty_kosh_dequeue.sm',
}


def extract_default_comments(text):
    """Comments immediately above each .sandesh entry contain default text."""
    result, previous = {}, None
    for line in text.splitlines():
        if line.startswith('# '):
            try:
                previous = json.loads(line[2:])
            except (ValueError, TypeError):
                previous = None
            continue
        if not line.strip():
            previous = None
            continue
        if line.lstrip().startswith('#'):
            continue
        key, sep, _ = line.partition('\t')
        if sep:
            if isinstance(previous, str):
                result[key] = previous
            previous = None
        else:
            previous = None
    return result


def build(keys, ide_keys, comments, expected_by_case, available_paths):
    entries = []
    for key in keys:
        text = comments.get(key, '')
        # Very short / generic fragments produce false attribution (e.g.
        # "Sanket: '"). Such hits remain CANDIDATE only.
        candidate_cases = sorted(
            case for case, output in expected_by_case.items()
            if len(text.strip()) >= 8 and text.strip() in output
        )
        if candidate_cases:
            status = 'CHECKED_IN_EXPECTATION_CANDIDATE'
            note = ('literal default-message fragment found in existing golden; '
                    'verify emitting callsite and native execution independently')
        elif key in SOURCE_ONLY_EXCLUSIONS:
            status = 'NON_SOURCE_CLI_OR_SHELL'
            note = SOURCE_ONLY_EXCLUSIONS[key]
        elif key in PROBE_CANDIDATES:
            status = 'PROBE_AVAILABLE_NOT_VERIFIED'
            note = ('existing source or R83 new candidate, no confirmed '
                    'per-label golden in this inventory')
        else:
            status = 'UNMAPPED_NEEDS_REPRO'
            note = 'no proven .sm test found; NOT a claim the diagnostic is unreachable'
        path = PROBE_CANDIDATES.get(key)
        if path and path not in available_paths:
            status = 'BROKEN_PROBE_PATH'
        entries.append({
            'key': key, 'status': status, 'context': note,
            'fixture': path,
            'expected_outputs': [
                'tests/sandesh/expect/default/' + c + '.out'
                for c in candidate_cases
            ],
            'candidate_sources': [
                'tests/sandesh/cases/' + c + '.sm' for c in candidate_cases
            ],
        })
    for key in ide_keys:
        entries.append({
            'key': 'ide.' + key, 'status': 'NON_SOURCE_IDE_MESSAGE',
            'context': 'IDE status/output UI, not emitted by a .sm program',
            'fixture': None, 'expected_outputs': [], 'candidate_sources': [],
        })
    counts = {}
    for e in entries:
        counts[e['status']] = counts.get(e['status'], 0) + 1
    return {
        'total_messages': len(entries),
        'compiler_messages': len(keys),
        'ide_messages': len(ide_keys),
        'expected_cases_considered': sorted(expected_by_case),
        'counts': counts,
        'native_execution': 'NOT_RUN',
        'all_diagnostics_covered': False,
        'entries': entries,
    }


def run(root):
    path = root / 'tools' / 'sandesh.py'
    spec = importlib.util.spec_from_file_location('r83_sandesh_schema', path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    comments = extract_default_comments(
        (root / 'lang/sanskrit.sandesh').read_text(encoding='utf8'))
    expected = {}
    for case in DEFAULT_CASES:
        path = root / f'tests/sandesh/expect/default/{case}.out'
        expected[case] = path.read_text(encoding='utf8')
    available = {path for path in PROBE_CANDIDATES.values()
                 if (root / path).is_file() and not (root / path).is_symlink()}
    return build(module.KEYS, module.IDE_KEYS, comments, expected, available)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--report', type=Path)
    a = parser.parse_args()
    try:
        result = run(a.repo)
    except (OSError, UnicodeError, ValueError) as exc:
        result = {'status': 'FAIL', 'reason': str(exc)}
    raw = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    print(raw, end='')
    if a.report:
        with a.report.open('x', encoding='utf8') as f:
            f.write(raw)
    return 2 if result.get('status') == 'FAIL' or \
        result.get('counts', {}).get('BROKEN_PROBE_PATH') else 0


if __name__ == '__main__':
    raise SystemExit(main())
