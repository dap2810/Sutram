#!/usr/bin/env python3
"""Round 97 foreign-declaration sidecar model. TEST-ONLY reference, NOT native Sutram.

Usage: python3 ROUND-97-WS1-SIDECAR-ORACLE.py
The model is intentionally strict so that malformed inputs cannot produce
foreign stubs or reach the linker. Real compile-time checking needs NASM hooks.
"""
from __future__ import annotations
import re
from dataclasses import dataclass

HEADER = b"sutram-ffi-v1|linux-x86_64-sysv\n"
NAME = re.compile(rb"[A-Za-z_][A-Za-z0-9_]{0,62}\Z")
SYMBOL = re.compile(rb"[A-Za-z_][A-Za-z0-9_]{0,127}\Z")
MAX_FILE = 8192
MAX_RECORDS = 64

class ForeignError(ValueError):
    def __init__(self, code, detail):
        super().__init__(f"{code}: {detail}")
        self.code = code

@dataclass(frozen=True)
class Declaration:
    sutram_name: str
    arity: int
    arg_kinds: tuple[str, ...]
    return_kind: str
    external_symbol: str

def parse(data: bytes) -> dict[str, Declaration]:
    if len(data) > MAX_FILE or not data.startswith(HEADER) or b'\r' in data or b'\x00' in data:
        raise ForeignError('E_FFI_SIDECAR', 'wrong header, size or newline encoding')
    if not data.endswith(b'\n'):
        raise ForeignError('E_FFI_SIDECAR', 'missing final LF')
    table = {}
    rows = data[len(HEADER):].split(b'\n')[:-1]
    if not rows or len(rows) > MAX_RECORDS:
        raise ForeignError('E_FFI_SIDECAR', 'record count')
    externals=set()
    for line, row in enumerate(rows, 2):
        f = row.split(b'|')
        if len(f) != 5:
            raise ForeignError('E_FFI_SIDECAR', f'line {line}: exactly five fields required')
        local, arity_b, args_b, ret_b, sym = f
        if not NAME.fullmatch(local) or not SYMBOL.fullmatch(sym):
            raise ForeignError('E_FFI_SIDECAR', f'line {line}: invalid identifier/symbol')
        if not re.fullmatch(rb'[0-6]', arity_b):
            raise ForeignError('E_FFI_SIDECAR', f'line {line}: invalid arity')
        arity=int(arity_b)
        args = [] if not args_b else args_b.split(b',')
        if len(args) != arity or any(kind not in (b'i64',b'ptr',b'f64') for kind in args):
            raise ForeignError('E_FFI_SIDECAR', f'line {line}: argument-kinds/arity conflict')
        if ret_b not in (b'i64',b'ptr',b'f64',b'void'):
            raise ForeignError('E_FFI_SIDECAR', f'line {line}: invalid return kind')
        if any(a != b'i64' for a in args) or ret_b != b'i64':
            raise ForeignError('E_FFI_ABI_UNSUPPORTED', f'line {line}: first phase supports i64 only')
        key=local.decode('ascii')
        if key in table or sym in externals:
            raise ForeignError('E_FFI_DUPLICATE', f'line {line}: duplicate local or external symbol')
        table[key] = Declaration(key,arity,tuple(a.decode('ascii') for a in args),'i64',sym.decode('ascii'))
        externals.add(sym)
    return table

def check_call(table: dict[str,Declaration], name:str, argc:int, location='caller.sm:3:11') -> str:
    if name not in table:
        raise ForeignError('E_FFI_UNDECLARED',f'{location}: {name}')
    d=table[name]
    if argc != d.arity:
        raise ForeignError('E_ARITY', f'{location}: {name} takes {d.arity} arguments, got {argc}')
    # Simulated emitter ONLY: no fake function body, no SUTRAMO1 symbol definition.
    return d.external_symbol

GOOD = HEADER+b's_add|2|i64,i64|i64|sutram_ffi_add\n'

def tests():
    checks=[]
    def ok(label, f):
        try: f()
        except Exception as e: raise AssertionError(label) from e
        checks.append(('PASS',label))
    def bad(label, f, code):
        try: f()
        except ForeignError as e:
            if e.code != code: raise AssertionError((label,e.code,code))
            checks.append(('PASS',label+' -> '+code))
            return
        raise AssertionError(label+' was erroneously accepted')
    d=parse(GOOD)
    ok('parse exact i64 signature', lambda: len(d)==1 and d['s_add'].arity==2 or (_ for _ in ()).throw(AssertionError()))
    ok('valid two-argument call resolves to foreign symbol', lambda: check_call(d,'s_add',2)=='sutram_ffi_add' or (_ for _ in ()).throw(AssertionError()))
    bad('one argument is compile error',lambda:check_call(d,'s_add',1),'E_ARITY')
    bad('three arguments is compile error',lambda:check_call(d,'s_add',3),'E_ARITY')
    bad('unbound foreign name compile error',lambda:check_call(d,'missing',2),'E_FFI_UNDECLARED')
    bad('header version rejected',lambda:parse(GOOD.replace(b'ffi-v1',b'ffi-v2')),'E_FFI_SIDECAR')
    bad('target ABI rejected',lambda:parse(GOOD.replace(b'linux-x86_64-sysv',b'windows-x64-sysv')),'E_FFI_SIDECAR')
    bad('byte order mark rejected',lambda:parse(b'\xef\xbb\xbf'+GOOD),'E_FFI_SIDECAR')
    bad('CRLF rejected',lambda:parse(GOOD.replace(b'\n',b'\r\n')),'E_FFI_SIDECAR')
    bad('trailing newline required',lambda:parse(GOOD.rstrip(b'\n')),'E_FFI_SIDECAR')
    bad('extra pipe rejected',lambda:parse(GOOD.rstrip(b'\n')+b'|extra\n'),'E_FFI_SIDECAR')
    bad('missing field rejected',lambda:parse(GOOD.replace(b'|i64,i64|',b'|')),'E_FFI_SIDECAR')
    bad('whitespace in name rejected',lambda:parse(GOOD.replace(b's_add|',b's add|')),'E_FFI_SIDECAR')
    bad('symbol name too long rejected',lambda:parse(GOOD.replace(b'sutram_ffi_add',b'x'*129)),'E_FFI_SIDECAR')
    bad('zero arity with arguments rejected',lambda:parse(GOOD.replace(b'|2|',b'|0|')),'E_FFI_SIDECAR')
    bad('mismatched argument kinds rejected',lambda:parse(GOOD.replace(b'|i64,i64|',b'|i64|')),'E_FFI_SIDECAR')
    bad('floating argument fails closed',lambda:parse(GOOD.replace(b'i64,i64',b'i64,f64')),'E_FFI_ABI_UNSUPPORTED')
    bad('pointer argument fails closed',lambda:parse(GOOD.replace(b'i64,i64',b'i64,ptr')),'E_FFI_ABI_UNSUPPORTED')
    bad('floating return fails closed',lambda:parse(GOOD.replace(b'|i64|sutram',b'|f64|sutram')),'E_FFI_ABI_UNSUPPORTED')
    bad('void return fails closed',lambda:parse(GOOD.replace(b'|i64|sutram',b'|void|sutram')),'E_FFI_ABI_UNSUPPORTED')
    bad('duplicate local rejected',lambda:parse(GOOD+GOOD[len(HEADER):]),'E_FFI_DUPLICATE')
    bad('duplicate external rejected',lambda:parse(GOOD+b'other|2|i64,i64|i64|sutram_ffi_add\n'),'E_FFI_DUPLICATE')
    bad('NUL byte rejected',lambda:parse(GOOD+b'\0'),'E_FFI_SIDECAR')
    bad('oversized file rejected',lambda:parse(GOOD + b'x'*MAX_FILE),'E_FFI_SIDECAR')
    bad('malformed invalid negative arity',lambda:parse(GOOD.replace(b'|2|',b'|-1|')),'E_FFI_SIDECAR')
    bad('missing all entries rejected',lambda:parse(HEADER),'E_FFI_SIDECAR')
    for result,label in checks: print(result,label)
    print('RESULT',len(checks),'PASS 0 FAIL; Python sidecar model only; native Sutram compiler NOT_RUN')
if __name__=='__main__':tests()
