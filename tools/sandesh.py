#!/usr/bin/env python3
"""The compiler's messages, one set per language pack (ROUND-11, WS1).

The rule (the owner's): a message is in the language of the selected pack. Without
--lang it is the romanised Sanskrit default that the compiler source holds. With
--lang <pack> it is that pack's own text, from lang/<pack>.sandesh. There is no
English anywhere, not as a default and not as a fallback.

    python3 tools/sandesh.py --write      # lang/*.sandesh -> src/r11_sandesh.inc
    python3 tools/sandesh.py --check      # the .inc is current and every pack passes the checks
    python3 tools/sandesh.py --report     # counts per pack
    python3 tools/sandesh.py --show hindi r4_msg_undef

The same files hold the Windows IDE's status line and output-pane messages, under
`ide.<label>` keys; --write also writes windows/gui/r11_ide_sandesh.inc. The IDE shows
them in the language of the pack its next run passes with --lang (Auto: the detected
pack; Core: the default).

A pack file holds one line per message, `key<TAB>"text"`: the text is a JSON string
(\\n is a newline). A `#` line is a comment; each entry is preceded by the default
text as a comment, so a reviewer sees what the message says. The key is the
compiler's label for the message; the compiler looks a message up by its address
(r11_tr in src/sutram_compiler.asm), so no print site changes when a pack is added.

A pack that lacks a key prints the default for that message. --check refuses such a
pack, so a missing key cannot ship unnoticed: every one of the eleven packs is
complete or --check fails.

The checks, per entry:
  * the key is a known message;
  * `Sutram Error` and every `[E_CODE]` tag of the default are present, unchanged
    (identifiers, not prose: the owner's rule);
  * the punctuation the code relies on is kept: the leading newline / `: ` and the
    trailing newline or opening quote, since the compiler prints the name and the
    closing quote around the fragment;
  * every Latin word is code (a keyword, a builtin, a flag, a file name, an E_ tag)
    that the default also has, so no English can enter through a translation;
  * every other letter is in the pack's own script.
And on the defaults: none of the English words this round removed may return.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INC = ROOT / 'src/r11_sandesh.inc'
IDE_SRC = 'windows/gui/sutram_gui.asm'
IDE_INC = ROOT / 'windows/gui/r11_ide_sandesh.inc'
# the IDE's pack order (kw_pack_paths, r9_pack_names): its index + 1 is use_pack
IDE_PACKS = ['sanskrit', 'bengali', 'gujarati', 'hindi', 'kannada', 'malayalam', 'marathi', 'odia',
             'punjabi', 'tamil', 'telugu']
# each language's own name, in its own script, for the IDE's status line
NATIVE_NAME = {'sanskrit': 'संस्कृतम्', 'bengali': 'বাংলা', 'gujarati': 'ગુજરાતી', 'hindi': 'हिन्दी',
               'kannada': 'ಕನ್ನಡ', 'malayalam': 'മലയാളം', 'marathi': 'मराठी', 'odia': 'ଓଡ଼ିଆ',
               'punjabi': 'ਪੰਜਾਬੀ', 'tamil': 'தமிழ்', 'telugu': 'తెలుగు'}
# the status line (UTF-16 in the IDE) and the output-pane messages (UTF-8)
IDE_WIDE = ['st_pankti_w', 'st_stambh_w', 'st_bhasha_w', 'st_akshara_w', 'st_lipi_w', 'st_sanchit_w',
            'st_asanchit_w', 'st_notfound_w', 'lang_swayam_w', 'lang_swayam_sk_w', 'lang_mool_w']
IDE_NARROW = ['msg_ready', 'msg_compile_failed', 'msg_run_failed', 'msg_file_failed', 'msg_input_large',
              'msg_shell_limit', 'msg_timeout', 'msg_missing_compiler', 'msg_missing_lang',
              'msg_partial_lang', 'msg_pipe_fail', 'msg_more_output']
IDE_KEYS = IDE_WIDE + IDE_NARROW
SOURCES = ['src/sutram_compiler.asm', 'src/r66_indic_lexer.inc', 'src/r68_diagnostics.inc']

# compiler language id -> pack (the order of lang_names in sutram_compiler.asm)
PACK_IDS = {1: 'bengali', 2: 'gujarati', 3: 'hindi', 4: 'kannada', 5: 'malayalam', 6: 'marathi',
            7: 'odia', 8: 'punjabi', 9: 'tamil', 10: 'telugu', 11: 'sanskrit'}
# the order a reader is given them in: Sanskrit first (the canonical language), then Hindi
PACK_ORDER = ['sanskrit', 'hindi', 'marathi', 'gujarati', 'bengali', 'punjabi', 'odia',
              'tamil', 'telugu', 'kannada', 'malayalam']
SCRIPT = {'sanskrit': (0x0900, 0x097F), 'hindi': (0x0900, 0x097F), 'marathi': (0x0900, 0x097F),
          'bengali': (0x0980, 0x09FF), 'punjabi': (0x0A00, 0x0A7F), 'gujarati': (0x0A80, 0x0AFF),
          'odia': (0x0B00, 0x0B7F), 'tamil': (0x0B80, 0x0BFF), 'telugu': (0x0C00, 0x0C7F),
          'kannada': (0x0C80, 0x0CFF), 'malayalam': (0x0D00, 0x0D7F)}
SHARED_MARKS = {0x0964, 0x0965, 0x200C, 0x200D}   # danda, double danda, ZWNJ, ZWJ

# Every message the compiler prints, in source order. A key whose label lives in
# src/r68_diagnostics.inc exists only in the r68 entry build, so its row is wrapped
# in `%ifmacro call 1` (that entry defines a `call` macro; a bare build does not).
# Fragments that are only punctuation or an identifier ("'\n", ": Sutram Error [")
# are not listed: there is nothing in them to translate.
KEYS = [
    'msg_usage', 'msg_version', 'r48_msg_near', 'r48_msg_ok', 'r48_msg_errors', 'r48_msg_eof',
    'r50_msg_setchar_arity', 'r52_msg_dvaram_arity', 'r52_msg_charat_arity', 'r52_msg_charcode_arity',
    'r48_msg_undefined', 'r4_msg_undef', 'r4_msg_hint_decl', 'r4_msg_hint_old', 'r4_msg_hint_old2',
    'r5_msg_field', 'r7_msg_dup', 'r7_msg_dup_hint', 'r7_msg_field_amb', 'r7_msg_field_amb_hint',
    'r7_msg_field_dup_hint', 'r7_msg_arity2', 'r7_msg_arity3', 'r7_msg_arity_hint',
    'r7_msg_mod_missing', 'r7_msg_mod_missing2', 'r7_msg_hint_block', 'r5_msg_field_hint',
    'r5_msg_field_hint2',
    'msg_err_line', 'msg_err_near', 'msg_err_eof', 'msg_err_hint', 'msg_err_arg_limit',
    'msg_err_duplicate_func', 'msg_duplicate_func', 'msg_undefined_func', 'msg_array_oob',
    'msg_kosh_required',
    'r65_msg_add', 'r65_msg_sub', 'r65_msg_mul', 'r65_msg_div', 'r65_msg_mod', 'r65_msg_div_overflow',
    'r65_msg_mod_overflow',
    'msg_kosh_empty', 'msg_kosh_peek_empty', 'msg_kosh_dequeue_empty', 'msg_kosh_param_type',
    'msg_kosh_param_push',
    'msg_lang_ok', 'msg_lang_fail', 'msg_shell_banner', 'msg_shell_bye', 'msg_shell_help',
    'msg_open_err', 'msg_ok', 'msg_bytes',
    'msg_namespace_error', 'msg_namespace_module_missing', 'msg_namespace_alias_reuse',
    'r51_alias_conflict', 'msg_namespace_func_limit', 'msg_import_overflow',
    'graph_cycle_prefix', 'graph_missing_prefix', 'graph_invalid_prefix',
    'msg_ast_overflow', 'msg_func_params_overflow', 'msg_var_table_overflow', 'msg_func_table_overflow',
    'msg_patch_overflow', 'msg_func_defs_overflow', 'msg_r9_guna_overflow', 'msg_break_patch_overflow',
    'msg_continue_patch_overflow', 'msg_code_overflow', 'msg_rachana_overflow',
    'msg_rachana_fields_overflow', 'msg_block_nesting_overflow', 'msg_block_stmt_overflow',
    'r55_msg_proto_duplicate', 'r55_msg_proto_missing', 'r55_msg_proto_signature',
    'r55_msg_proto_capacity', 'r56_msg_global_capacity', 'r56_msg_global_duplicate',
    'r56_msg_patch_capacity',
    'mg_e_cycle', 'mg_e_noexp2', 'mg_e_noexp3', 'mg_e_dupexp1', 'mg_e_dupexp2', 'mg_e_undef1',
    'mg_e_undef2', 'mg_e_unknown1', 'mg_e_unknown2', 'mg_e_depth', 'mg_e_valias1', 'mg_e_valias2',
    'mg_e_limit',
    'r66_msg_bad_utf8', 'r68_utf8_tail', 'r68_value_tail',
]
R68_ONLY = {'r68_utf8_tail', 'r68_value_tail'}
R65_ONLY = {k for k in KEYS if k.startswith('r65_msg_')}

# Latin words a translation may keep: code the reader types or sees in the source.
CODE_WORDS = set('''
Sutram Error sutram check lang version i vitti akshar_rakh dvaram akshar aksharank kosh_pop
kosh_peek kosh_dequeue kosh_push v157 v1 v182 lib smlib sm bin UTF x86 yoj upanaam likha chakra tak
mala arr x n sarvam nirgat sahayata Namaste Enter F5 KiB win exe
'''.split())
KW = re.compile(r'\{kw:([A-Za-z_][A-Za-z0-9_]*)\}')


def pack_keywords(pack: str) -> dict[str, str]:
    """roman keyword -> the pack's own word for it (its first line for that keyword;
    abbreviations, written with the ॰ sign, are skipped)."""
    out: dict[str, str] = {}
    p = ROOT / 'lang' / f'{pack}.lang'
    for line in p.read_text(encoding='utf-8').splitlines():
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        parts = line.split()
        if len(parts) >= 2 and '\u0970' not in parts[0] and parts[1] not in out:
            out[parts[1]] = parts[0]
    return out


def roman_keywords() -> set[str]:
    return {k for f in (ROOT / 'lang').glob('*.lang') for k in pack_keywords(f.stem)}


def expand(pack: str, text: str) -> str:
    """{kw:likha} -> the pack's own word for likha, or likha when the pack has none."""
    kw = pack_keywords(pack)
    return KW.sub(lambda m: kw.get(m.group(1), m.group(1)), text)
# English words that left the defaults in R11; none may come back
NOT_AGAIN = {'ok', 'binary', 'folder', 'module', 'ast', 'data', 'byte', 'bytes', 'code', 'parse',
             'error', 'token', 'run', 'type', 'help', 'for', 'at', 'the', 'not', 'found', 'file'}  # not 'is': Hindi इस

ROMAN_KW: set[str] = set()
LABEL = re.compile(r'^\s*([A-Za-z_][\w.]*):?\s+db\s+(.*)$')
CONT = re.compile(r'^\s+db\s+(.*)$')
LONE = re.compile(r'^\s*([A-Za-z_][\w.]*):\s*(;.*)?$')


def parse_db(arg: str) -> bytes:
    out = bytearray()
    i = 0
    while i < len(arg):
        c = arg[i]
        if c in '"\'`':
            j = arg.index(c, i + 1)
            body = arg[i + 1:j]
            if c == '`':
                body = body.encode('utf-8').decode('unicode_escape').encode('latin-1').decode('utf-8')
            out += body.encode('utf-8')
            i = j + 1
        elif c == ';':
            break
        elif c.isdigit():
            m = re.match(r'0x[0-9A-Fa-f]+|\d+', arg[i:])
            out.append(int(m.group(0), 0))
            i += len(m.group(0))
        else:
            i += 1
    return bytes(out)


def defaults() -> dict[str, str]:
    """label -> the default text the compiler holds (up to its 0 byte)."""
    found: dict[str, bytes] = {}
    for f in SOURCES:
        cur = None
        pend = None
        for line in (ROOT / f).read_text(encoding='utf-8').split('\n'):
            m = LABEL.match(line)
            if m and m.group(1) not in ('db', 'dq', 'dw', 'dd'):
                cur = m.group(1)
                found[cur] = parse_db(m.group(2))
                pend = None
                continue
            m = LONE.match(line)
            if m:
                pend, cur = m.group(1), None
                continue
            m = CONT.match(line)
            if m and (cur or pend):
                if cur is None:
                    cur, pend = pend, None
                    found[cur] = b''
                found[cur] += parse_db(m.group(1))
                continue
            if line.strip() and not line.strip().startswith(';'):
                cur = pend = None
    out = {}
    for k in KEYS:
        if k not in found:
            raise SystemExit(f'sandesh: the compiler has no message labelled {k}')
        out[k] = found[k].split(b'\0')[0].decode('utf-8')
    return out


WIDE = re.compile(r'^\s*([A-Za-z_]\w*):\s+dw\s+__utf16__\("([^"]*)"\),0\s*$')


def ide_defaults() -> dict[str, str]:
    """'ide.<label>' -> the IDE's default text."""
    found = {}
    for line in (ROOT / IDE_SRC).read_text(encoding='utf-8').split('\n'):
        m = WIDE.match(line)
        if m:
            found[m.group(1)] = m.group(2)
            continue
        m = LABEL.match(line)
        if m:
            found.setdefault(m.group(1), parse_db(m.group(2)).split(b'\0')[0].decode('utf-8'))
    out = {}
    for k in IDE_KEYS:
        if k not in found:
            raise SystemExit(f'sandesh: the IDE has no message labelled {k}')
        out['ide.' + k] = found[k]
    return out


def read_pack(pack: str) -> dict[str, str]:
    p = ROOT / 'lang' / f'{pack}.sandesh'
    if not p.exists():
        return {}
    out = {}
    for n, line in enumerate(p.read_text(encoding='utf-8').split('\n'), 1):
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        key, _, val = line.partition('\t')
        if not val:
            raise SystemExit(f'{p.name}:{n}: expected key<TAB>"text"')
        if key in out:
            raise SystemExit(f'{p.name}:{n}: {key} twice')
        out[key] = json.loads(val)
    return out


EDGE_L = re.compile(r"^[\n:' ,\[]*")
EDGE_R = re.compile(r"[\r\n' \]]*$")
TAGS = re.compile(r'Sutram Error|\[E_[A-Z0-9_]+\]')
LATIN = re.compile(r'[A-Za-z][A-Za-z0-9_]*')


def check_entry(pack: str, key: str, text: str, default: str) -> list[str]:
    bad = []
    if TAGS.findall(text) != TAGS.findall(default):
        bad.append(f'identifiers differ: {TAGS.findall(default)} -> {TAGS.findall(text)}')
    if EDGE_L.match(text).group(0) != EDGE_L.match(default).group(0):
        bad.append(f'leading punctuation {EDGE_L.match(default).group(0)!r} changed to {EDGE_L.match(text).group(0)!r}')
    if EDGE_R.search(text).group(0) != EDGE_R.search(default).group(0):
        bad.append(f'trailing punctuation {EDGE_R.search(default).group(0)!r} changed to {EDGE_R.search(text).group(0)!r}')
    for m in KW.finditer(text):
        if m.group(1) not in ROMAN_KW and m.group(1) not in CODE_WORDS:
            bad.append(f'{{kw:{m.group(1)}}} is not a keyword')
    shown = expand(pack, text)
    if not bad and (EDGE_L.match(shown).group(0) != EDGE_L.match(default).group(0) or
                    EDGE_R.search(shown).group(0) != EDGE_R.search(default).group(0)):
        bad.append('a {kw:} at an edge changes the punctuation')
    # a keyword the pack has no word for is shown as its roman keyword: code, allowed
    plain = KW.sub(' ', TAGS.sub(' ', text))
    plain += ' ' + ' '.join(w for w in KW.findall(text) if w not in pack_keywords(pack))
    dwords = set(LATIN.findall(TAGS.sub(' ', default)))
    for w in LATIN.findall(plain):
        if w not in CODE_WORDS and not w.startswith('E_'):
            bad.append(f'Latin word {w!r} is not code')
        elif w not in dwords and w not in ('Sutram',) and w not in KW.findall(text):
            bad.append(f'code word {w!r} is not in the default')
    lo, hi = SCRIPT[pack]
    for ch in KW.sub(lambda m: pack_keywords(pack).get(m.group(1), ''), plain):
        cp = ord(ch)
        if cp < 128 or cp in SHARED_MARKS or lo <= cp <= hi:
            continue
        bad.append(f'{ch!r} U+{cp:04X} ({unicodedata.name(ch, "?")}) is not in the {pack} script')
        break
    return bad


def check_all(defs: dict[str, str], strict: bool = True) -> tuple[list[str], dict]:
    problems = []
    for k, d in defs.items():
        words = {w.lower() for w in LATIN.findall(TAGS.sub(' ', d))}
        if words & NOT_AGAIN:
            problems.append(f'default {k}: English {sorted(words & NOT_AGAIN)}')
    counts = {}
    for pack in PACK_ORDER:
        tr = read_pack(pack)
        for k in tr:
            if k not in defs:
                problems.append(f'{pack}: unknown key {k}')
        missing = [k for k in list(KEYS) + ['ide.' + i for i in IDE_KEYS] if k not in tr]
        if missing and strict:
            problems.append(f'{pack}: {len(missing)} of {len(KEYS)} messages missing (first: {missing[0]})')
        for k, t in tr.items():
            if k in defs:
                for b in check_entry(pack, k, t, defs[k]):
                    problems.append(f'{pack} {k}: {b}')
        counts[pack] = {'compiler': len(KEYS), 'compiler_translated': sum(k in tr for k in KEYS),
                        'ide': len(IDE_KEYS), 'ide_translated': sum('ide.' + k in tr for k in IDE_KEYS),
                        'missing': missing}
    return problems, counts


def nasm_bytes(text: str) -> str:
    b = text.encode('utf-8') + b'\0'
    parts, run = [], ''
    for x in b:
        if 32 <= x < 127 and chr(x) not in '"\\`':
            run += chr(x)
        else:
            if run:
                parts.append(f'"{run}"')
                run = ''
            parts.append(str(x))
    if run:
        parts.append(f'"{run}"')
    return ','.join(parts)


def render(defs: dict[str, str]) -> str:
    packs = {p: read_pack(p) for p in PACK_IDS.values()}
    out = ['; GENERATED by tools/sandesh.py --write from lang/*.sandesh. Do not edit by hand.',
           '; R11 (WS1): every compiler message, per language pack. r11_keys lists the',
           "; default messages by address; each pack's column is parallel to it (0 = no copy:",
           '; the default is printed). r11_tr in sutram_compiler.asm does the lookup.',
           'R11_NPACKS equ 12', 'align 8', 'r11_keys:']

    def guard(k, line):
        if k in R68_ONLY:
            return ['%ifmacro call 1', line, '%endif']
        if k in R65_ONLY:
            return ['%ifdef SUTRAM_R65_TRAP_INT', line, '%endif']
        return [line]
    for k in KEYS:
        out += guard(k, f'    dq {k}')
    out += ['    dq 0', 'r11_packs:', '    dq 0' + ''.join(
        f', r11_col_{PACK_IDS[i]}' if packs[PACK_IDS[i]] else ', 0' for i in range(1, 12))]
    for i in range(1, 12):
        p = PACK_IDS[i]
        tr = packs[p]
        if not tr:
            continue
        out.append(f'r11_col_{p}:')
        for n, k in enumerate(KEYS):
            out += guard(k, f'    dq r11_{p}_{n}' if k in tr else '    dq 0')
    for i in range(1, 12):
        p = PACK_IDS[i]
        tr = packs[p]
        for n, k in enumerate(KEYS):
            if k in tr:
                out += guard(k, f'r11_{p}_{n} db {nasm_bytes(expand(p, tr[k]))}')
    return '\n'.join(out) + '\n'


def render_ide(defs: dict[str, str]) -> str:
    packs = {p: read_pack(p) for p in IDE_PACKS}
    out = ['; GENERATED by tools/sandesh.py --write from lang/*.sandesh. Do not edit by hand.',
           "; R11 (WS1): the IDE's status line and output-pane messages, per language pack.",
           '; r11_ide_keys lists the default strings by address; r11_ide_cols[use_pack] is',
           '; the column of the pack the next run passes (0 = the default). The status-line',
           '; strings are UTF-16, the output-pane ones UTF-8 (output_append converts them).',
           'section .data', 'align 8', 'r11_ide_keys:']
    out += [f'    dq {k}' for k in IDE_KEYS] + ['    dq 0', 'r11_ide_cols:', '    dq 0' + ''.join(
        f', r11_ide_col_{p}' for p in IDE_PACKS)]
    for p in IDE_PACKS:
        out.append(f'r11_ide_col_{p}:')
        out += [f'    dq r11_ide_{p}_{n}' if 'ide.' + k in packs[p] else '    dq 0'
                for n, k in enumerate(IDE_KEYS)]
    out.append('r11_pack_native_w:')
    out.append('    dq ' + ', '.join(f'r11_native_{p}' for p in IDE_PACKS))
    out.append('align 2')

    def wide(t):
        return 'dw ' + ','.join(f'0x{ord(c):04X}' for c in t) + ',0'
    for p in IDE_PACKS:
        out.append(f'r11_native_{p}: {wide(NATIVE_NAME[p])}')
        for n, k in enumerate(IDE_KEYS):
            t = packs[p].get('ide.' + k)
            if t is not None and k in IDE_WIDE:
                out.append(f'r11_ide_{p}_{n}: {wide(expand(p, t))}')
    for p in IDE_PACKS:
        for n, k in enumerate(IDE_KEYS):
            t = packs[p].get('ide.' + k)
            if t is not None and k in IDE_NARROW:
                out.append(f'r11_ide_{p}_{n}: db {nasm_bytes(expand(p, t))}')
    return '\n'.join(out) + '\n'


def write_template(pack: str, defs: dict[str, str], have: dict[str, str]) -> str:
    lines = [f'# Sutram compiler messages: {pack}. ROUND-11 (WS1).',
             '# One line per message: key<TAB>"text" (a JSON string; \\n is a newline).',
             '# The comment above each line is the romanised Sanskrit default. Keep `Sutram Error`,',
             '# the [E_CODE] tags, the code words (keywords, builtins, file names) and the',
             "# punctuation at both ends exactly as the default has them: the compiler prints the",
             '# name and the closing quote around the fragment. tools/sandesh.py --check verifies it.',
             '']
    def entry(k):
        lines.append('# ' + json.dumps(defs[k], ensure_ascii=False))
        if k in have:
            lines.append(f'{k}\t' + json.dumps(have[k], ensure_ascii=False))
        else:
            lines.append(f'# MISSING {k}')
    for k in KEYS:
        entry(k)
    lines += ['', '# ---- the Windows IDE: its status line and its output-pane messages ----', '']
    for k in IDE_KEYS:
        entry('ide.' + k)
    return '\n'.join(lines) + '\n'


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--write', action='store_true', help='write src/r11_sandesh.inc')
    ap.add_argument('--check', action='store_true', help='the .inc is current and every pack is complete and clean')
    ap.add_argument('--report', action='store_true', help='per-pack counts as JSON')
    ap.add_argument('--format', metavar='PACK', help='rewrite lang/PACK.sandesh in the canonical layout')
    ap.add_argument('--show', nargs=2, metavar=('PACK', 'KEY'))
    a = ap.parse_args(argv)
    ROMAN_KW.update(roman_keywords())
    defs = defaults()
    defs.update(ide_defaults())
    if a.format:
        p = ROOT / 'lang' / f'{a.format}.sandesh'
        p.write_text(write_template(a.format, defs, read_pack(a.format)), encoding='utf-8')
        print('wrote', p.relative_to(ROOT))
    if a.show:
        print(expand(a.show[0], read_pack(a.show[0]).get(a.show[1], defs[a.show[1]])), end='')
    problems, counts = check_all(defs, strict=a.check)
    if a.write:
        INC.write_text(render(defs), encoding='utf-8')
        IDE_INC.write_text(render_ide(defs), encoding='utf-8')
        print('wrote', INC.relative_to(ROOT), 'and', IDE_INC.relative_to(ROOT))
    if a.report:
        print(json.dumps({'compiler_messages': len(KEYS), 'ide_messages': len(IDE_KEYS), 'packs': {p: {k: v for k, v in c.items() if k != 'missing'}
                                                           for p, c in counts.items()}}, indent=1))
    if a.check:
        if INC.read_text(encoding='utf-8') != render(defs):
            problems.append('src/r11_sandesh.inc is stale: run tools/sandesh.py --write')
        if not IDE_INC.exists() or IDE_INC.read_text(encoding='utf-8') != render_ide(defs):
            problems.append('windows/gui/r11_ide_sandesh.inc is stale: run tools/sandesh.py --write')
        for p in problems:
            print('FAIL', p)
        print(f'sandesh: {len(KEYS)} compiler + {len(IDE_KEYS)} IDE messages x {len(PACK_ORDER)} packs: '
              + ('OK' if not problems else f'{len(problems)} problem(s)'))
        return 1 if problems else 0
    for p in problems:
        print('note:', p)
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
