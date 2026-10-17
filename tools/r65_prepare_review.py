#!/usr/bin/env python3
"""Prepare the corrected R65 compiler in a separate file; no native execution.

The input must be the exact compiler blob from PR #23 at 4f1dec7c.
This is a source-review delivery, not proof that NASM/runtime gates pass.
No network, package installation, Git mutation or source overwrite occurs.
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
from pathlib import Path
import re
import sys

EXPECTED_BLOB = "a14172c172ce7d1d714ca4efa0fb5bbdc67b5657"
SOURCE_PATH = "src/sutram_compiler.asm"


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise ValueError(f"{label}: expected exactly one anchor, found {count}")
    return source.replace(old, new, 1)


FIRST_ARG_OLD = """%ifdef SUTRAM_R65_PEEPHOLES
    ; Exactly one argument: no runtime instruction occurs between value
    ; evaluation and its transfer into RDI. Omit the push/pop pair.
    xor r8d,r8d
    cmp r14,1
    jne .r65_one_arg_flag_ready
    mov r8d,1
.r65_one_arg_flag_ready:
%endif
    call gen_typed_call_arg"""
FIRST_ARG_NEW = """%ifdef SUTRAM_R65_PEEPHOLES
    cmp r14,1
    jne .r65_normal_first_arg
    call r65_direct_typed_call_arg
    jmp .r65_first_arg_ready
.r65_normal_first_arg:
%endif
    call gen_typed_call_arg
%ifdef SUTRAM_R65_PEEPHOLES
.r65_first_arg_ready:
%endif"""
ARG_ENTRY_OLD = "gen_typed_call_arg:\n"
ARG_ENTRY_NEW = """%ifdef SUTRAM_R65_PEEPHOLES
; Only the single-argument EXPRESSION caller may omit its push. Statement
; calls and every other caller retain the historical push-by-default ABI.
r65_direct_typed_call_arg:
    mov r8d,1
    jmp gen_typed_call_arg.r65_explicit_push_mode
%endif
gen_typed_call_arg:
%ifdef SUTRAM_R65_PEEPHOLES
    xor r8d,r8d
.r65_explicit_push_mode:
%endif
"""
FOLD_OLD = """fold_const:
%ifdef SUTRAM_R65_TRAP_INT
    ; Parser literal folding could otherwise elide a runtime overflow trap.
    mov rax,rdi
    ret
%endif
"""
FOLD_NEW = """fold_const:
%ifdef SUTRAM_R65_TRAP_INT
    ; Keep safe constants and compile-time string concatenation. Preserve
    ; only a hazardous integer subtree for the runtime diagnostic path.
    push rdi
    call r65_can_fold_integer
    pop rdi
    test eax,eax
    jnz .r65_safe_constant_fold
    mov rax,rdi
    ret
.r65_safe_constant_fold:
%endif
"""
LINE_OLD = """%ifdef SUTRAM_R65_TRAP_INT
    push rcx                  ; unary-minus builder retains AST_NUM in RCX
    mov rcx,[rel cur_line]
    mov [rax+32],rcx          ; R65: parser-time BINOP source line
    pop rcx
%endif"""
LINE_NEW = """%ifdef SUTRAM_R65_TRAP_INT
    ; Saved before advancing the operator token; not the lexer's EOF line.
    pop qword [rax+32]
%endif"""

# This emitter uses rel32, not a signed one-byte branch over filename text.
LITERAL_NEW = """r65_emit_literal:
    push rbx
    push r12
    push r13
    mov r12,rdi
    call strlen
    mov r13,rax
    ; lea rsi,[rip+message], patched after the syscall and data-skip jump.
    mov dil,0x48
    call emit_byte
    mov dil,0x8D
    call emit_byte
    mov dil,0x35
    call emit_byte
    mov rbx,[rel code_sz]
    xor edi,edi
    call emit_u32
    mov dil,0xBA              ; mov edx,message length
    call emit_byte
    mov rdi,r13
    call emit_u32
    mov dil,0xBF              ; stdout (preserves existing trap contract)
    call emit_byte
    mov edi,1
    call emit_u32
    mov dil,0xB8              ; write
    call emit_byte
    mov edi,1
    call emit_u32
    call emit_syscall
    mov dil,0xE9              ; skip inline data with rel32
    call emit_byte
    mov rdi,r13
    call emit_u32
    mov rax,[rel code_sz]
    sub rax,rbx
    sub rax,4
    lea rcx,[rel code_buf]
    mov [rcx+rbx],eax
.r65_literal_loop:
    test r13,r13
    jz .r65_literal_done
    movzx edi,byte [r12]
    call emit_byte
    vardh r12
    dec r13
    jmp .r65_literal_loop
.r65_literal_done:
    pop r13
    pop r12
    pop rbx
    ret

"""
LONG_PATH_OLD = """    ; The literal-output path encodes short relative jumps over its bytes.
    ; Bound the embedded filename tak the last 95 bytes tak avoid overflow
    ; when a caller supplies a very long absolute input path.
    mov rdi,[rel source_path_ptr]
    push rdi
    call strlen
    pop rdi
    cmp rax,95
    jbe .r65_path_ready
    add rdi,rax
    sub rdi,95
.r65_path_ready:
"""

EXTRA_HELPERS = """
; R65 finishing corrections: inside the existing TRAP_INT guard.
; All temporaries below are compiler-side unless described as emitted bytes.
r65_can_fold_integer:
    cmp qword [rdi],AST_BINOP
    jne .yes
    mov r8,[rdi+16]
    mov r9,[rdi+24]
    cmp qword [r8],AST_NUM
    jne .yes
    cmp qword [r9],AST_NUM
    jne .yes
    mov r8,[r8+8]
    mov r9,[r9+8]
    mov rax,[rdi+8]
    cmp rax,OP_ADD
    je .add
    cmp rax,OP_SUB
    je .sub
    cmp rax,OP_MUL
    je .mul
    cmp rax,OP_DIV
    je .div
    cmp rax,OP_MOD
    je .div
    jmp .yes
.add:
    add r8,r9
    jo .no
    jmp .yes
.sub:
    sub r8,r9
    jo .no
    jmp .yes
.mul:
    imul r8,r9
    jo .no
    jmp .yes
.div:
    test r9,r9
    jz .no
    cmp r9,-1
    jne .yes
    mov rax,0x8000000000000000
    cmp r8,rax
    je .no
.yes:
    mov eax,1
    ret
.no:
    xor eax,eax
    ret

r65_emit_div_overflow_guard:
    ; Normal generic arithmetic holds lhs in runtime RAX, divisor in RCX.
    ; R10 is volatile scratch, not a named local or an active register tree.
    push rbx
    push r12
    push r13
    push r14
    mov r12,rdi
    ; cmp rcx,-1; jne success
    mov dil,0x48
    call emit_byte
    mov dil,0x83
    call emit_byte
    mov dil,0xF9
    call emit_byte
    mov dil,0xFF
    call emit_byte
    mov dil,0x0F
    call emit_byte
    mov dil,0x85
    call emit_byte
    mov r13,[rel code_sz]
    xor edi,edi
    call emit_u32
    ; mov r10,INT64_MIN; cmp rax,r10; jne success
    mov dil,0x49
    call emit_byte
    mov dil,0xBA
    call emit_byte
    mov rdi,0x8000000000000000
    call emit_u64
    mov dil,0x4C
    call emit_byte
    mov dil,0x39
    call emit_byte
    mov dil,0xD0
    call emit_byte
    mov dil,0x0F
    call emit_byte
    mov dil,0x85
    call emit_byte
    mov r14,[rel code_sz]
    xor edi,edi
    call emit_u32
    lea rax,[rel r65_msg_mod]
    cmp r12,rax
    lea rdi,[rel r65_msg_div_overflow]
    jne .message_ready
    lea rdi,[rel r65_msg_mod_overflow]
.message_ready:
    mov rsi,[rbx+32]
    call r65_emit_fatal
    mov rax,[rel code_sz]
    sub rax,r13
    sub rax,4
    lea rcx,[rel code_buf]
    mov [rcx+r13],eax
    mov rax,[rel code_sz]
    sub rax,r14
    sub rax,4
    mov [rcx+r14],eax
    pop r14
    pop r13
    pop r12
    pop rbx
    ret
"""


def transform(source: str) -> tuple[str, list[str]]:
    """Apply exact source anchors; no fuzzy matching or partial success."""
    log: list[str] = []

    def edit(old: str, new: str, name: str) -> None:
        nonlocal source
        source = replace_once(source, old, new, name)
        log.append(name)

    edit(FIRST_ARG_OLD, FIRST_ARG_NEW, "explicit-single-argument-entry")
    edit(ARG_ENTRY_OLD, ARG_ENTRY_NEW, "safe-push-default-for-all-other-callers")
    edit(FOLD_OLD, FOLD_NEW, "retain-safe-constant-and-string-folding")
    edit("    r65_candidate_name resq 1\n",
         "    r65_candidate_name resq 1\n    r65_last_store_end resq 1\n    r65_candidate_end resq 1\n",
         "peephole-emission-boundary-fields")
    edit("    mov [rel r65_candidate_name],rax\n",
         "    mov [rel r65_candidate_name],rax\n    mov rax,[rel r65_last_store_end]\n    mov [rel r65_candidate_end],rax\n",
         "capture-preceding-store-boundary")
    old_store = "    mov [rel r65_last_store_name],rax\n"
    if source.count(old_store) != 2:
        raise ValueError("expected exactly two generic scalar-store completion sites")
    source = source.replace(old_store, old_store +
                            "    mov rax,[rel code_sz]\n    mov [rel r65_last_store_end],rax\n")
    log.append("record-both-store-completion-offsets")
    edit("    mov rdi,[rel r65_candidate_name]\n",
         "    mov rdi,[rel code_sz]\n    cmp rdi,[rel r65_candidate_end]\n    jne .r65_emit_rhs\n    mov rdi,[rel r65_candidate_name]\n",
         "require-no-intervening-generated-instruction")
    # At .a_do/.m_do, RAX still addresses the operator token returned by cur_tok.
    # The operator's lexer-recorded line is token+24; cur_line itself is not
    # advanced by cur_tok and may still hold the lexer's final input line.
    for name, end, site in (("parse_add", "parse_mul", ".a_do:"),
                            ("parse_mul", "fold_const", ".m_do:")):
        begin = source.index(name + ":\n")
        finish = source.index(end + ":\n", begin + 1)
        segment = source[begin:finish]
        segment = replace_once(segment, site + "\n    call advance_tok\n",
                               site + "\n%ifdef SUTRAM_R65_TRAP_INT\n    push qword [rax+24]\n%endif\n    call advance_tok\n",
                               name + "-save-operator-line")
        segment = replace_once(segment, LINE_OLD, LINE_NEW, name + "-restore-operator-line")
        source = source[:begin] + segment + source[finish:]
        log.append(name + "-exact-operator-token-line")
    begin = source.index("r65_emit_literal:\n")
    finish = source.index("r65_emit_number:\n", begin)
    source = source[:begin] + LITERAL_NEW + source[finish:]
    log.append("rel32-literal-output-with-full-filename")
    edit(LONG_PATH_OLD, "    mov rdi,[rel source_path_ptr]\n", "remove-byte-truncation-of-filename")
    edit('    r65_msg_mod db ": remainder by zero",10,0\n',
         '    r65_msg_mod db ": remainder by zero",10,0\n'
         '    r65_msg_div_overflow db ": signed division overflow",10,0\n'
         '    r65_msg_mod_overflow db ": signed remainder overflow",10,0\n',
         "signed-idiv-overflow-diagnostics")
    begin = source.index("r65_emit_zero_guard:\n")
    finish = source.index("%endif", begin)
    segment = source[begin:finish]
    anchor = "    mov [rcx+r13],eax\n    pop r13\n"
    segment = replace_once(segment, anchor,
                           "    mov [rcx+r13],eax\n    mov rdi,r12\n    call r65_emit_div_overflow_guard\n    pop r13\n",
                           "idiv-minimum-divided-by-negative-one")
    source = source[:begin] + segment + EXTRA_HELPERS + "\n" + source[finish:]
    log.append("guard-int64-min-div-neg-one-and-preserve-normal-operands")
    return source, log


def default_projection(source: str) -> str:
    """Erase R65-only branches, not other NASM directives; ignore comments.

    This is a source comparison, not a NASM preprocessor or binary identity test.
    Both R65 defines are considered absent. Nested unrelated directives survive.
    """
    active = True
    stack: list[tuple[bool, bool, bool]] = []
    output: list[str] = []
    for line in source.splitlines():
        stripped = line.strip()
        m = re.fullmatch(r"%(ifdef|ifndef)\s+(SUTRAM_R65_[A-Z_]+)", stripped)
        if m:
            condition = m[1] == "ifndef"
            stack.append((active, True, condition))
            active = active and condition
            continue
        if re.match(r"%if(?:\w*)\b", stripped):
            stack.append((active, False, True))
        elif stripped == "%else":
            if not stack:
                raise ValueError("unbalanced %else")
            parent, ours, condition = stack[-1]
            if ours:
                stack[-1] = (parent, ours, not condition)
                active = parent and not condition
                continue
        elif stripped == "%endif":
            if not stack:
                raise ValueError("unbalanced %endif")
            parent, ours, _ = stack.pop()
            active = parent
            if ours:
                continue
        if active and stripped and not stripped.startswith(";"):
            output.append(line.rstrip())
    if stack:
        raise ValueError("unclosed NASM conditional")
    return "\n".join(output)


def prepare(data: bytes) -> tuple[bytes, list[str]]:
    actual = git_blob(data)
    if actual != EXPECTED_BLOB:
        raise ValueError(f"source drift: expected Git blob {EXPECTED_BLOB}, observed {actual}")
    text = data.decode("utf-8")
    result, log = transform(text)
    if default_projection(text) != default_projection(result):
        raise ValueError("finishing correction changed the default-mode source projection")
    return result.encode("utf-8"), log


def exclusive_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(data)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path(SOURCE_PATH))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--patch-output", type=Path)
    args = parser.parse_args(argv)
    if args.output.resolve() == args.source.resolve():
        parser.error("output must differ from source; this tool never edits the checkout")
    if args.output.exists() or (args.patch_output and args.patch_output.exists()):
        parser.error("output already exists; choose a fresh destination")
    try:
        data = args.source.read_bytes()
        result, log = prepare(data)
        if args.patch_output:
            diff = "".join(difflib.unified_diff(data.decode("utf-8").splitlines(True),
                           result.decode("utf-8").splitlines(True),
                           fromfile="a/" + SOURCE_PATH, tofile="b/" + SOURCE_PATH))
            exclusive_write(args.patch_output, diff.encode("utf-8"))
        exclusive_write(args.output, result)
        print(json.dumps({"status": "SOURCE_PREPARED_NOT_NATIVELY_TESTED",
                          "input_git_blob": EXPECTED_BLOB,
                          "output": str(args.output),
                          "output_sha256": hashlib.sha256(result).hexdigest(),
                          "corrections": log,
                          "default_source_projection_identical": True}, indent=2))
        return 0
    except (ValueError, UnicodeError, OSError) as exc:
        print(f"R65_PREPARE_FAILED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
