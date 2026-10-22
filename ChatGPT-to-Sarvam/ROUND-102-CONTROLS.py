#!/usr/bin/env python3
"""R102 executable arithmetic and proposed-pointer-contract models.
No Sutram compiler is invoked; no foreign pointer is dereferenced or allocated.
Run: python3 -B ROUND-102-CONTROLS.py
"""
from __future__ import annotations
import random
import re
import struct

MAX = (1 << 63) - 1
MIN = -(1 << 63)
MASK = (1 << 64) - 1
HEADER = b'sutram-ffi-v3|windows-x86_64-msabi\n'  # PROPOSED, not implemented
KINDS = {b'i64': 0, b'f64': 1, b'ptr': 2, b'void': 3, b'cstr_ro': 4}


def wrap(n: int) -> int:
    return (n + (1 << 63)) % (1 << 64) - (1 << 63)


def truncdiv(a: int, b: int) -> int:
    if b == 0 or (a == MIN and b == -1):
        raise ArithmeticError('division would trap')
    q = abs(a) // abs(b)
    return -q if (a < 0) != (b < 0) else q


def checked_mul_model(a: int, b: int) -> tuple[int, int]:
    """Source-equivalent arithmetic of ganita_janchit_gun, not native execution."""
    if a == 0 or b == 0:
        return 0, 1
    if (a == MIN and b == -1) or (b == MIN and a == -1):
        return 0, 0
    m = wrap(a * b)
    return (0, 0) if truncdiv(m, a) != b else (m, 1)


def sized(count: int, stride: int, extra: int = 0) -> int:
    """Proposed allocation precondition. Arithmetic success is not allocation success."""
    if count < 0 or stride <= 0 or extra < 0 or extra > MAX:
        raise ValueError('invalid size domain')
    if count > (MAX - extra) // stride:
        raise ValueError('size overflow')
    return count * stride + extra


def parse_proposal(data: bytes) -> list[tuple[str, int, bytes, str]]:
    """Small model for R102 v3 proposal; does not change accepted v1/v2 semantics."""
    if len(data) > 8192 or not data.startswith(HEADER) or not data.endswith(b'\n'):
        raise ValueError('header/size/terminator')
    if any(b not in range(0x21, 0x7f) and b != 10 for b in data):
        raise ValueError('non-ASCII, space, CR or NUL')
    rows = data[len(HEADER):].split(b'\n')[:-1]
    if not 1 <= len(rows) <= 64:
        raise ValueError('record count')
    result, locals_seen, externals_seen = [], set(), set()
    for row in rows:
        fields = row.split(b'|')
        if len(fields) != 5:
            raise ValueError('field count')
        local, argc, args, ret, symbol = fields
        if not re.fullmatch(rb'[A-Za-z_][A-Za-z0-9_]{0,62}', local):
            raise ValueError('local identifier')
        if not re.fullmatch(rb'[A-Za-z_][A-Za-z0-9_]{0,126}', symbol):
            raise ValueError('external identifier')
        if not re.fullmatch(rb'[0-6]', argc):
            raise ValueError('arity')
        kinds = [] if args == b'' else args.split(b',')
        if len(kinds) != int(argc) or any(k not in KINDS or k == b'void' for k in kinds):
            raise ValueError('argument kinds')
        if ret not in (b'i64', b'f64', b'ptr', b'void'):
            raise ValueError('result kind')
        if local in locals_seen or symbol in externals_seen:
            raise ValueError('duplicate')
        locals_seen.add(local)
        externals_seen.add(symbol)
        packed = bytes([KINDS[k] for k in kinds] + [0] * (6 - len(kinds)) + [KINDS[ret], 0])
        result.append((local.decode(), int(argc), packed, symbol.decode()))
    return result


def literal_cstr(payload: bytes, provenance: str = 'literal') -> bytes:
    """Only a direct, compiler-known literal qualifies for the proposed first profile."""
    if provenance != 'literal':
        raise ValueError('unknown lifetime/extent')
    payload.decode('utf-8', 'strict')
    if b'\0' in payload:
        raise ValueError('embedded NUL')
    return payload + b'\0'


def ms_locations(kinds: list[str]) -> list[str]:
    gp = ('rcx', 'rdx', 'r8', 'r9')
    return [(f'xmm{i}' if kind == 'f64' else gp[i]) if i < 4
            else f'[rsp+{32+8*(i-4)}]' for i, kind in enumerate(kinds)]


def main() -> None:
    passed = 0
    def check(name: str, condition: bool) -> None:
        nonlocal passed
        if not condition:
            raise AssertionError(name)
        passed += 1
        print('PASS', name)
    def rejects(name: str, fn) -> None:
        try:
            fn()
        except (ValueError, UnicodeError):
            check(name + ' [expected rejection]', True)
            return
        raise AssertionError(name + ': unexpectedly accepted')

    edges = [MIN, MIN+1, -(1<<61)+1, -3, -1, 0, 1, 2, 8, (1<<59)+1,
             (1<<60)-1, 1<<60, (1<<61)+1, (1<<62)+1, MAX-1, MAX]
    rng = random.Random(102)
    pairs = [(a,b) for a in edges for b in edges]
    pairs += [(rng.randint(MIN, MAX), rng.randint(MIN, MAX)) for _ in range(20000)]
    for a,b in pairs:
        true = a*b
        expected = (true,1) if MIN <= true <= MAX else (0,0)
        if checked_mul_model(a,b) != expected:
            raise AssertionError((a,b,expected,checked_mul_model(a,b)))
    check(f'checked-multiply model matches bigint oracle for {len(pairs)} pairs', True)
    check('zero result requires ok flag', checked_mul_model(0, MAX)==(0,1)
          and checked_mul_model(MAX,2)==(0,0))
    check('signed helper does not validate size domain', checked_mul_model(-1,8)==(-8,1))
    rejects('negative count is not a valid allocation size', lambda:sized(-1,8))

    witnesses = [('count*8',(1<<61)+1,8,0), ('count*16',(1<<60)+1,16,0),
                 ('count*32',(1<<59)+1,32,0),
                 ('count*33+1',((1<<64)+32)//33,33,1)]
    for label,n,s,e in witnesses:
        product=n*s+e
        check(label+' wraps positive', product>MAX and 0<wrap(product)<=64)
        rejects(label+' precheck', lambda n=n,s=s,e=e:sized(n,s,e))
        print('WITNESS',label,'count',n,'mathematical',product,'wrapped',wrap(product))
    n=-(1<<61)+1
    check('mala negative count escapes current upper and sign checks',
          n<=MAX//8 and wrap(n*8)==8)
    print('WITNESS mala_negative',n,'wrapped_bytes',wrap(n*8))
    m=(1<<62)+1
    check('matrix dimensions can alias a four-cell loop', wrap(m*4)==4 and m*4>MAX)
    print('WITNESS matrix',m,4,'mathematical_cells',m*4,'wrapped_cells',wrap(m*4))
    check('index stride can alias byte offset eight',wrap(((1<<61)+1)*8)==8)
    mapcap=(MAX-16)//56
    check('R35 valid map bounds protect internal scratch arithmetic',
          16+56*mapcap<=MAX and 33*mapcap+1<=MAX)
    print('BOUND map_capacity',mapcap,'scratch_bytes',33*mapcap+1)
    check('cell-export expansion needs a stronger bound', (33*mapcap+1)*8>MAX)
    check('growth positive-wrap witness violates intact R35 constructor bound',
          (1<<60)+1>MAX//8 and wrap(((1<<60)+1)*16)==16)
    check('max valid constructor capacity can still overflow signed growth size',
          (MAX//8)*16>MAX and wrap((MAX//8)*16)<0)
    check('constant scratch products cannot wrap',22*8==176 and 70*8==560)
    check('FNV bounded product fits int64', ((1<<32)-1)*16777619<MAX)
    rejects('size addition checked too',lambda:sized(MAX//8,8,8))
    check('a valid zero-size calculation is not overflow',sized(0,8)==0)
    for stride,extra in [(8,0),(16,0),(32,0),(33,1),(56,16),(264,8)]:
        top=(MAX-extra)//stride
        check(f'bound stride={stride} extra={extra}',sized(top,stride,extra)<=MAX)
        rejects(f'bound+1 stride={stride} extra={extra}',lambda t=top,s=stride,e=extra:sized(t+1,s,e))

    good=HEADER+b's_len|1|cstr_ro|i64|sutram_w_cstrlen\n'
    parsed=parse_proposal(good)[0]
    check('proposed cstr signature retains five fields',parsed[1]==1 and parsed[3]=='sutram_w_cstrlen')
    check('internal kind word has id4, unused bytes zero',parsed[2]==bytes.fromhex('0400000000000000'))
    check('ASCII literal backing bytes',literal_cstr(b'abc')==b'abc\0')
    check('empty string is one NUL byte',literal_cstr(b'')==b'\0')
    utf8='नमस्ते'.encode('utf-8')
    check('UTF8 copied exactly plus one terminator',literal_cstr(utf8)==utf8+b'\0')
    rejects('embedded NUL literal',lambda:literal_cstr(b'a\0b'))
    rejects('malformed UTF8 literal',lambda:literal_cstr(b'\xff'))
    for p in ('integer','kosh','raw_ptr','variable'):
        rejects('cstr provenance '+p,lambda p=p:literal_cstr(b'abc',p))
    for label,data in [('old v2 header',good.replace(b'-v3|',b'-v2|')),
                       ('other ABI',good.replace(b'windows-x86_64-msabi',b'linux-x86_64-sysv')),
                       ('CRLF',good.replace(b'\n',b'\r\n')),
                       ('missing LF',good[:-1]),('BOM',b'\xef\xbb\xbf'+good),
                       ('bad kind',good.replace(b'cstr_ro',b'buf_ro@2')),
                       ('arity mismatch',good.replace(b'|1|',b'|2|')),
                       ('extra field',good[:-1]+b'|extra\n'),
                       ('cstr return',good.replace(b'|i64|sutram',b'|cstr_ro|sutram')),
                       ('duplicate',good+good[len(HEADER):]),
                       ('oversize',good+b'x'*8192)]:
        rejects('proposal '+label,lambda data=data:parse_proposal(data))
    for k in range(6):
        place=('rcx','rdx','r8','r9','[rsp+32]','[rsp+40]')[k]
        kinds = ['f64'] * 6
        kinds[k] = 'cstr_ro'
        check(f'MS pointer slot {k+1} = {place}',ms_locations(kinds)[k] == place)
    check('MS mixed arguments keep ordinal slots',
          ms_locations(['i64','f64','cstr_ro','f64']) == ['rcx','xmm1','r8','xmm3'])
    for old in (0x1000,0x1008,0x1018,0x1020):
        aligned=old&~15
        before_call=aligned-8-56
        check(f'shadow stack model from rsp={old:#x}',before_call%16==0
              and before_call+56==aligned-8 and before_call+40+8<=before_call+56)
    prefix=bytes.fromhex('4989e34883e4f041534883ec38')
    suffix=bytes.fromhex('4883c4385c')
    check('call-hole displacement uses next instruction',struct.pack('<i',100-(13+4))==b'S\0\0\0')
    print('BYTES proposed_header',len(HEADER),HEADER.hex())
    print('BYTES literal_utf8',literal_cstr(utf8).hex())
    print('BYTES win_call_prefix',prefix.hex(),'suffix',suffix.hex())
    print(f'RESULT {passed} PASS / 0 FAIL')
    print('SCOPE Python arithmetic and proposed-contract models only; no allocations, no native Sutram/Windows tests.')

if __name__=='__main__':
    main()
