#!/usr/bin/env python3
"""Read-only R85 nine-identifier classification; NEVER runs compiled programs/sockets.

This is a source-structure check, not a native compilation or runtime test.
The nine names were raised in COVERAGE-AUDIT.md. The four kosh names
are compiler-private BSS state, NOT Sutram builtin functions.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

INTERNAL = ('kosh_var_cnt', 'kosh_vars', 'kosh_param_var_cnt', 'kosh_param_vars')
PUBLIC = ('sthagita', 'netsock', 'netbind', 'netlisten', 'netaccept')


def between(text: str, start: str, end: str) -> str:
    a = text.find(start)
    if a == -1:
        raise ValueError(f'missing source landmark: {start}')
    b = text.find(end, a + len(start))
    if b == -1:
        raise ValueError(f'missing source landmark: {end}')
    return text[a:b]


def inspect(source: str) -> dict:
    """Fail closed if lexer, parser, dispatch, or internal declarations drift."""
    table = between(source, 'bn_table:', 'bn_table_end:')
    bn_ids = dict(re.findall(r'^\s*BN_(\w+)\s+equ\s+(\d+)\b', source, re.M))
    declared = dict(re.findall(r'^\s*(bn_\w+)\s+db\s+"([^"]+)",\s*0', source, re.M))
    entries = re.findall(r'\bdq\s+(bn_\w+),\s*TOK_BUILTIN,\s*(BN_\w+)', table)
    dispatch = between(source, '.ge_call:', '.ge_call_nirm:')
    rows = []
    errors = []

    for word in PUBLIC:
        pairs = [(label, ident) for label, ident in entries if declared.get(label) == word]
        entry_ok = len(pairs) == 1 and pairs[0][1].removeprefix('BN_') in bn_ids
        symbol = pairs[0][1] if entry_ok else None
        # Special builtin sthagita goes straight to AST_HALT rather than .ge_call.
        if word == 'sthagita':
            parser_ok = bool(re.search(r'cmp\s+rbx,\s*BN_STHAGITA\s*\n\s*je\s+\.pp_halt', source))
            codegen_ok = '.gs_halt:' in source and '.ge_halt:' in source
        else:
            label = {'netsock': 'netsock', 'netbind': 'netbind',
                     'netlisten': 'netlist', 'netaccept': 'netacc'}[word]
            parser_ok = 'r54_builtin_arity_ok' in source
            codegen_ok = bool(re.search(r'cmp\s+r12,\s*BN_'+label.upper()+r'\s*\n\s*je\s+\.ge_call_'+label, dispatch))
        status = 'SOURCE_DISPATCH_TRACED' if entry_ok and parser_ok and codegen_ok else 'INCOMPLETE_MAPPING'
        if status == 'INCOMPLETE_MAPPING':
            errors.append(word + ': missing or ambiguous lexer/parser/codegen path')
        rows.append({'identifier': word, 'classification': 'source_builtin',
                     'status': status, 'builtin_id': bn_ids.get(symbol.removeprefix('BN_')) if symbol else None,
                     'lexer_entry': pairs[0] if entry_ok else None,
                     'parser_present': parser_ok, 'codegen_present': codegen_ok,
                     'native_test': 'NOT_RUN'})

    for word in INTERNAL:
        declaration = re.search(r'^\s*'+re.escape(word)+r'\s+resq\s+\w+', source, re.M)
        misuse = any(declared.get(label) == word for label, _ in entries)
        if not declaration or misuse:
            errors.append(word + ': expected compiler BSS-only symbol missing or exported')
        rows.append({'identifier': word, 'classification': 'compiler_private_bss',
                     'status': 'NOT_A_SOURCE_BUILTIN' if declaration and not misuse else 'REVIEW_REQUIRED',
                     'declaration_line': source[:declaration.start()].count('\n')+1 if declaration else None,
                     'name_in_builtin_table': misuse, 'native_test':'NOT_APPLICABLE'})

    # Check the current hazards without *ever* executing generated machine code.
    stmt = between(source, '.gs_halt:', '.gs_writemem:')
    expr = between(source, '.ge_halt:', '; emit_nirmmita_from_rax')
    privileged = bool(re.search(r'mov\s+dil,\s*0xF4\b', stmt, re.I)
                      and re.search(r'mov\s+dil,\s*0xF4\b', expr, re.I))
    bind = between(source, '.ge_call_netbind:', '.ge_call_netlist:')
    wildcard = bool(re.search(r'mov\s+dword\s+\[rsp\+4\],\s*0', bind))
    risks = {'sthagita_emits_privileged_hlt': privileged,
             'netbind_sets_ipv4_address_zero_INADDR_ANY': wildcard,
             'network_execution': 'NOT_RUN',
             'sthagita_execution': 'NOT_RUN'}
    if not privileged:
        risks['hlt_rule'] = 'HLT not found in both codegen handlers; review new semantics before running'
    if not wildcard:
        risks['bind_rule'] = 'Address assignment changed; review before assuming loopback'
    return {'status': 'PASS' if not errors else 'FAIL', 'compiler_proof': 'SOURCE_STRUCTURE_ONLY',
            'identifiers': rows, 'risks': risks, 'errors': errors}


def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[1])
    ap.add_argument('--report',type=Path)
    a=ap.parse_args()
    try:
        src=(a.repo/'src/sutram_compiler.asm').read_text('utf-8')
        result=inspect(src)
    except (OSError, ValueError, UnicodeError) as exc:
        result={'status':'BLOCKED','reason':str(exc)}
    print(json.dumps(result,indent=2))
    if a.report:
        a.report.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    return 0 if result['status']=='PASS' else 2

if __name__=='__main__':
    raise SystemExit(main())
