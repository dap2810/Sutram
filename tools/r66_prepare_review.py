#!/usr/bin/env python3
"""Stage R66 lexical changes on the accepted R65 compiler; never overwrites source.

No network, build or installation. Input is the exact Git blob read from main
9921cbf175b2fb7983e45305fdec963380532452. Requires src/r66_indic_lexer.inc.
Review the generated patch before compiling the staged source from repository root.
"""
from __future__ import annotations
import argparse
import difflib
import hashlib
import json
from pathlib import Path

INPUT_BLOB = "caee73735372cfd92f47ea18c9c1c6f8b70e9599"

OLD_DANDA = """    ; ---- slice 21: danda । / double danda ॥ as statement terminators ----
    ; MUST run before the is_alpha test: is_alpha claims the 0xE0 lead byte,
    ; so a danda would otherwise be absorbed into an identifier. Both forms
    ; are 3-byte UTF-8 (E0 A5 A4 / E0 A5 A5) and emit the same token as ';'.
    movzx rax, byte [r13]
    cmp al, 0xE0
    jne .not_danda
    movzx rax, byte [r13+1]
    cmp al, 0xA5
    jne .not_danda
    movzx rax, byte [r13+2]
    cmp al, 0xA4                    ; । DANDA
    je .emit_danda
    cmp al, 0xA5                    ; ॥ DOUBLE DANDA
    je .emit_danda
.not_danda:
"""
NEW_DANDA = """    ; R66: bounded shared danda recognition, before any Indic identifier.
    mov rdi, r13
    mov rsi, r14
    call r66_is_danda_at
    test eax, eax
    jnz .emit_danda
.not_danda:
    ; Native decimal digits also begin with E0. Recognize at token START,
    ; before is_alpha; do not rewrite bytes or original source positions.
    mov rdi, r13
    mov rsi, r14
    call r66_decimal_digit_at
    test edx, edx
    jnz .try_number
"""
OLD_ID_DANDA = """    ; ---- slice 21: a danda terminates an identifier, it does not extend it.
    ; is_alpha claims the 0xE0 lead byte, so without this check 'i।' would be
    ; lexed as a single identifier and the terminator would disappear.
    movzx rax, byte [r13]
    cmp al, 0xE0
    jne .cid_alpha
    movzx rax, byte [r13+1]
    cmp al, 0xA5
    jne .cid_alpha
    movzx rax, byte [r13+2]
    cmp al, 0xA4                    ; । DANDA
    je .id_done
    cmp al, 0xA5                    ; ॥ DOUBLE DANDA
    je .id_done
.cid_alpha:
"""
NEW_ID_DANDA = """    ; R66: a complete shared danda ends an identifier under every pack.
    push rsi                  ; preserve identifier string-pool write pointer
    mov rdi, r13
    mov rsi, r14
    call r66_is_danda_at
    pop rsi
    test eax, eax
    jnz .id_done
.cid_alpha:
"""
OLD_NUM = """.try_number:
    movzx rax, byte [r13]
    mov rdi, rax
    call is_digit
    test rax, rax
    jz .try_operator
"""
NEW_NUM = """.try_number:
    mov rdi, r13
    mov rsi, r14
    call r66_decimal_digit_at
    test edx, edx
    jz .try_operator
"""
OLD_HEX = """    cmp al, '0'
    jne .dec_loop
    movzx rax, byte [r13+1]
"""
NEW_HEX = """    cmp al, '0'
    jne .dec_loop
    lea rax, [r13+1]
    cmp rax, r14
    jae .dec_loop
    movzx rax, byte [r13+1]
"""
OLD_DEC = """.dec_loop:
    cmp r13, r14
    jae .num_done
    movzx rax, byte [r13]
    mov rdi, rax
    call is_digit
    test rax, rax
    jnz .dec_digit
    ; T12 decimal fraction: only treat '.' as numeric when followed by a digit.
    movzx rax, byte [r13]
    cmp al, '.'
    jne .num_done
    movzx rax, byte [r13+1]
    mov rdi, rax
    call is_digit
    test rax, rax
    jz .num_done
    inc r13                    ; consume '.'
    xor r9, r9                 ; fractional integer
    mov r10, 1                 ; decimal divisor
    xor ecx, ecx               ; kept precision digits
.float_frac_loop:
    cmp r13, r14
    jae .float_frac_done
    movzx rax, byte [r13]
    mov rdi, rax
    call is_digit
    test rax, rax
    jz .float_frac_done
    cmp ecx, 15                ; binary64 does not benefit from unbounded decimal accumulation
    jae .float_frac_consume
    imul r9, r9, 10
    movzx rax, byte [r13]
    sub rax, '0'
    add r9, rax
    imul r10, r10, 10
    inc ecx
.float_frac_consume:
    inc r13
    jmp .float_frac_loop
"""
NEW_DEC = """.dec_loop:
    cmp r13, r14
    jae .num_done
    mov rdi, r13
    mov rsi, r14
    call r66_decimal_digit_at
    test edx, edx
    jnz .dec_digit
    ; ASCII dot remains the decimal point. The next digit may be native.
    cmp byte [r13], '.'
    jne .num_done
    lea rdi, [r13+1]
    mov rsi, r14
    call r66_decimal_digit_at
    test edx, edx
    jz .num_done
    inc r13
    xor r9, r9
    mov r10, 1
    xor ecx, ecx
.float_frac_loop:
    cmp r13, r14
    jae .float_frac_done
    mov rdi, r13
    mov rsi, r14
    call r66_decimal_digit_at ; preserves fractional counter ECX and R8-R11
    test edx, edx
    jz .float_frac_done
    cmp ecx, 15
    jae .float_frac_consume
    imul r9, r9, 10
    add r9, rax              ; decoded numeric value, NOT UTF-8 byte value
    imul r10, r10, 10
    inc ecx
.float_frac_consume:
    add r13, rdx             ; 1 ASCII byte or the entire 3-byte native digit
    jmp .float_frac_loop
"""
OLD_ACC = """.dec_digit:
    imul r8, r8, 10
    movzx rax, byte [r13]
    sub rax, '0'
    add r8, rax
    inc r13
    jmp .dec_loop
"""
NEW_ACC = """.dec_digit:
    imul r8, r8, 10
    add r8, rax              ; baseline integer wrap semantics unchanged
    add r13, rdx
    jmp .dec_loop
"""
OLD_COPY = """.store_multibyte:
    ; UTF-8 3-byte sequence
"""
NEW_COPY = """.store_multibyte:
    ; Validate the whole E0 scalar before copying or advancing source bytes.
    push rsi
    mov rdi, r13
    mov rsi, r14
    call r66_indic_scalar_width
    pop rsi
    test eax, eax
    jnz .r66_copy_scalar
    lea rdi, [rel r66_msg_bad_utf8]
    jmp capacity_fail
.r66_copy_scalar:
    ; UTF-8 3-byte sequence
"""
REPLACEMENTS = (
    ("helper include", "lex:\n", '%include "src/r66_indic_lexer.inc"\n\nlex:\n'),
    ("token start", OLD_DANDA, NEW_DANDA),
    ("identifier danda", OLD_ID_DANDA, NEW_ID_DANDA),
    ("number start", OLD_NUM, NEW_NUM),
    ("hex lookahead", OLD_HEX, NEW_HEX),
    ("decimal/fraction", OLD_DEC, NEW_DEC),
    ("integer accumulation", OLD_ACC, NEW_ACC),
    ("bounded Indic scalar", OLD_COPY, NEW_COPY),
)


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def transform(text: str) -> str:
    """Exact source transformations; tests may use captured anchor fixtures."""
    if 'src/r66_indic_lexer.inc' in text:
        raise ValueError("R66 preparation already present; refuse reapplication")
    # Validate every anchor before changing anything.
    for label, old, _ in REPLACEMENTS:
        n = text.count(old)
        if n != 1:
            raise ValueError(f"{label}: expected exactly one anchor, found {n}")
    for _, old, new in REPLACEMENTS:
        text = text.replace(old, new, 1)
    return text


def prepare(data: bytes) -> bytes:
    if git_blob(data) != INPUT_BLOB:
        raise ValueError("compiler source drift: required Git blob " + INPUT_BLOB)
    return transform(data.decode("utf-8")).encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("src/sutram_compiler.asm"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--patch-output", type=Path, required=True)
    args = parser.parse_args()
    source, output, patch = (p.resolve() for p in (args.source, args.output, args.patch_output))
    if len({source, output, patch}) != 3:
        parser.error("source, output and patch must be distinct paths")
    if output.exists() or patch.exists():
        parser.error("output already exists; use new paths, never overwrite source")
    # Compile includes are intentionally located in the caller's checkout.
    helper = Path(__file__).resolve().parents[1] / "src/r66_indic_lexer.inc"
    if not helper.is_file():
        parser.error("missing src/r66_indic_lexer.inc beside this tool's checkout")
    before = source.read_bytes()
    after = prepare(before)
    diff = ''.join(difflib.unified_diff(before.decode().splitlines(True), after.decode().splitlines(True),
                                      fromfile="a/src/sutram_compiler.asm", tofile="b/src/sutram_compiler.asm"))
    # Exclusive creation is race-safe. On a later failure remove only our own output.
    made = []
    try:
        with output.open("xb") as stream:
            made.append(output)
            stream.write(after)
        with patch.open("x", encoding="utf-8", newline="\n") as stream:
            made.append(patch)
            stream.write(diff)
    except BaseException:
        for name in made:
            name.unlink(missing_ok=True)
        raise
    print(json.dumps({"input_git_blob": git_blob(before), "output_git_blob": git_blob(after),
                      "output_sha256": hashlib.sha256(after).hexdigest(),
                      "output_bytes": len(after), "anchors_applied": len(REPLACEMENTS),
                      "native_execution": "not performed by preparation"}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
