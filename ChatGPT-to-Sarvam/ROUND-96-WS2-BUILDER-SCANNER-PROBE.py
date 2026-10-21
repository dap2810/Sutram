#!/usr/bin/env python3
"""R96 source-equivalent copy of tools/sutram_build.py:yoj_names (v239).
It tests the builder scanner, NOT Sutram's native lexer/compiler.
"""
def yoj_names(text: bytes):
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

for label, source in [
    ('real import', b'yoj ganita\nmukhya() {}\n'),
    ('quoted string only', b'mukhya() { likha("yoj bogus") }\n'),
    ('hash comment only', b'# yoj bogus\nmukhya() {}\n'),
    ('slash comment only', b'// yoj bogus\nmukhya() {}\n'),
]:
    print(label, repr(yoj_names(source)))
