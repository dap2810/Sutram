"""Tests of finishing source transformations, NOT Sutram/NASM execution."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("r65_prepare", ROOT / "tools/r65_prepare_review.py")
assert SPEC and SPEC.loader
p = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(p)


def snippet_source() -> str:
    """Minimal captured-anchor fixture, not the full production compiler."""
    return (
        "%ifdef SUTRAM_R65_PEEPHOLES\n"
        "    r65_candidate_name resq 1\n"
        "    mov [rel r65_candidate_name],rax\n"
        "    mov [rel r65_last_store_name],rax\n"
        "    mov [rel r65_last_store_name],rax\n"
        "    mov rdi,[rel r65_candidate_name]\n"
        "%endif\n"
        + p.FIRST_ARG_OLD + "\n" + p.ARG_ENTRY_OLD + "    ret\n"
        + "parse_add:\n.a_do:\n    call advance_tok\n" + p.LINE_OLD + "\n    ret\n"
        + "parse_mul:\n.m_do:\n    call advance_tok\n" + p.LINE_OLD + "\n    ret\n"
        + p.FOLD_OLD + "    ret\n"
        + "%ifdef SUTRAM_R65_TRAP_INT\n"
        '    r65_msg_mod db ": remainder by zero",10,0\n'
        "r65_emit_literal:\n    ret\n\nr65_emit_number:\n    ret\n"
        "r65_emit_fatal:\n" + p.LONG_PATH_OLD + "    call r65_emit_literal\n    ret\n"
        "r65_emit_zero_guard:\n    mov [rcx+r13],eax\n    pop r13\n    ret\n%endif\n"
    )


class PrepareTests(unittest.TestCase):
    def setUp(self):
        self.source = snippet_source()
        self.result, self.log = p.transform(self.source)

    def test_unmatched_source_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "source drift"):
            p.prepare(self.source.encode())

    def test_input_git_identity(self):
        self.assertEqual(p.git_blob(b"hello\n"), "ce013625030ba8dba906f756967f9e9ca394464a")

    def test_missing_anchor_fails(self):
        with self.assertRaisesRegex(ValueError, "exactly one"):
            p.replace_once("x", "absent", "y", "test")

    def test_duplicate_anchor_fails(self):
        with self.assertRaisesRegex(ValueError, "found 2"):
            p.replace_once("x x", "x", "y", "test")

    def test_default_source_projection_unchanged(self):
        self.assertEqual(p.default_projection(self.source), p.default_projection(self.result))

    def test_push_default_is_initialized(self):
        self.assertIn("gen_typed_call_arg:\n%ifdef SUTRAM_R65_PEEPHOLES\n    xor r8d,r8d", self.result)

    def test_direct_entry_is_explicit(self):
        self.assertIn("call r65_direct_typed_call_arg", self.result)
        self.assertIn("jmp gen_typed_call_arg.r65_explicit_push_mode", self.result)

    def test_store_reuse_requires_equal_emission_offset(self):
        self.assertIn("cmp rdi,[rel r65_candidate_end]\n    jne .r65_emit_rhs", self.result)
        self.assertEqual(self.result.count("mov [rel r65_last_store_end],rax"), 2)

    def test_operator_lines_saved_before_advance(self):
        for site in (".a_do:", ".m_do:"):
            self.assertIn(site + "\n%ifdef SUTRAM_R65_TRAP_INT\n    push qword [rax+24]\n%endif\n    call advance_tok", self.result)
        self.assertEqual(self.result.count("pop qword [rax+32]"), 2)

    def test_safe_constant_folding_has_guard_not_blanket_return(self):
        self.assertIn("call r65_can_fold_integer", self.result)
        self.assertNotIn(p.FOLD_OLD, self.result)
        self.assertIn("cmp rax,OP_MOD", self.result)
        self.assertIn("imul r8,r9\n    jo .no", self.result)

    def test_full_filename_no_95_byte_truncation(self):
        self.assertNotIn("sub rdi,95", self.result)
        self.assertIn("mov rdi,[rel source_path_ptr]\n    call r65_emit_literal", self.result)

    def test_literals_use_rel32_skip(self):
        self.assertIn("mov dil,0xE9              ; skip inline data with rel32", self.result)
        self.assertIn("mov [rcx+rbx],eax", self.result)

    def test_idiv_overflow_separate_from_zero(self):
        self.assertIn("call r65_emit_div_overflow_guard", self.result)
        self.assertIn("mov rdi,0x8000000000000000", self.result)
        self.assertIn("signed division overflow", self.result)
        self.assertIn("signed remainder overflow", self.result)

    def test_reapplication_fails_closed(self):
        with self.assertRaises(ValueError):
            p.transform(self.result)

    def test_missing_second_store_fails(self):
        changed = self.source.replace("    mov [rel r65_last_store_name],rax\n", "", 1)
        with self.assertRaisesRegex(ValueError, "two generic"):
            p.transform(changed)

    def test_writer_does_not_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "file.asm"
            p.exclusive_write(path, b"original")
            with self.assertRaises(FileExistsError):
                p.exclusive_write(path, b"replacement")
            self.assertEqual(path.read_bytes(), b"original")

    def test_conditional_balance_errors(self):
        for text in ("%else\n", "%endif\n", "%ifdef SUTRAM_R65_TRAP_INT\n"):
            with self.assertRaises(ValueError):
                p.default_projection(text)

    def test_unrelated_conditionals_preserved(self):
        text = "%ifdef WINDOWS\nhello\n%else\nworld\n%endif\n"
        self.assertEqual(p.default_projection(text), text.rstrip())


if __name__ == "__main__":
    unittest.main()
