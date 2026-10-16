"""Developer-only narrow NASM/GAS syntax bridge adapted from R66 helper tests.
Not a compiler backend, NASM substitute, or full Sutram translator.
"""
import re
def to_gas(text: str) -> str:
    out = ['.intel_syntax noprefix']
    scope = None
    for raw in text.splitlines():
        line = raw.split(';', 1)[0].strip()
        if not line:
            continue
        if line in ('bits 64', 'default rel') or line.startswith('global '):
            continue
        if line.startswith('section '):
            section = line.split()[1]
            if section not in ('.text', '.data'):
                raise ValueError('unsupported section ' + section)
            out.append(section)
            continue
        if line.endswith(':'):
            name = line[:-1]
            if not name.startswith('.'):
                if not re.fullmatch(r'[a-zA-Z_][a-zA-Z_0-9]*', name):
                    raise ValueError('unsupported symbol')
                scope = name
                out.append('.globl ' + name)
            else:
                if scope is None:
                    raise ValueError('unscoped local label')
                name = scope + '__' + name[1:]
            out.append(name + ':')
            continue
        if line.startswith('db '):
            # Only literal ASCII string / numeric bytes occur in these helpers.
            items = next(__import__('csv').reader([line[3:]], skipinitialspace=True))
            values = []
            for item in items:
                try:
                    values.append(int(item, 0))
                except ValueError:
                    values.extend(item.encode('utf-8'))
            out.append('.byte ' + ','.join(str(v) for v in values))
            continue
        if line.startswith('%'):
            raise ValueError('macros/includes are not accepted by this narrow adapter')
        line = re.sub(r'\b(byte|word|dword|qword)\s+\[',
                      lambda m: m[1].upper() + ' PTR [', line)
        if re.search(r'(?<![\w])\.[A-Za-z_]', line):
            if scope is None:
                raise ValueError('unscoped local reference')
            line = re.sub(r'(?<![\w])\.([A-Za-z_][\w]*)',
                          lambda m: scope + '__' + m[1], line)
        out.append(line)
    out.append('.section .note.GNU-stack,"",@progbits')
    return '\n'.join(out) + '\n'


