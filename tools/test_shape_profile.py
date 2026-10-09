#!/usr/bin/env python3
"""Regression tests for the static Sutram shape census. No compiler required."""
import unittest
from shape_profile import classify_source, shape, strip_comment


class ShapeProfileTests(unittest.TestCase):
    def test_comment_and_string(self):
        self.assertEqual(strip_comment('x = "a#b" # comment'), 'x = "a#b" ')
        self.assertEqual(strip_comment('x = 1 # y = y + 500'), 'x = 1 ')

    def test_immediate_bounds(self):
        self.assertEqual(shape('x', 'x + 127'), 'self_imm8')
        self.assertEqual(shape('x', 'x - 128'), 'self_imm32')
        self.assertEqual(shape('x', 'x + 2147483647'), 'self_imm32')
        self.assertEqual(shape('x', 'x + 2147483648'), 'self_large_imm')
        self.assertEqual(shape('y', 'x + 1000'), 'distinct_imm32')
        self.assertEqual(shape('y', 'x + 4294967295'), 'distinct_large_imm')

    def test_distinct_and_candidate(self):
        self.assertEqual(shape('sum', 'sum + term'), 'self_register_op')
        self.assertEqual(shape('result', 'a + b'), 'distinct_register_op')
        self.assertEqual(shape('result', '25 + a'), 'literal_left_add')
        self.assertEqual(shape('a[0]', 'b'), 'indexed_write')

    def test_float_rhs_buckets_are_disjoint(self):
        src = """prakriya foo(dasham x) {
          dasham sum = 0.0
          sum = sum + x
          dasham value = sum + x
          value = value + bar(x)
          value = xs[0] + x
          value = (x + 2.0) * (sum + x)
          value = 2.0
        }
        """
        c = classify_source(src)
        bucket_keys = [k for k in c if k.startswith('float_rhs_')]
        self.assertEqual(sum(c[k] for k in bucket_keys), c['float_likely_assignments'])
        self.assertEqual(c['float_rhs_call'], 1)
        self.assertEqual(c['float_rhs_index'], 1)
        self.assertEqual(c['float_rhs_simple_self'], 1)
        self.assertEqual(c['float_rhs_simple_distinct'], 1)
        self.assertEqual(c['float_rhs_complex'], 1)
        self.assertEqual(c['float_rhs_scalar'], 2)

    def test_source_classification(self):
        src = '''# x = x + 1000
prakriya foo(kosh dasham xs) {
  dasham s = 0.0
  vitti i = 0
  yavat (i < 5) { s = s + xs[i] }
  i = i + 2147483648
  yadi (i > 0) { s = s + 1.5 }
  pratiyati s
}
'''
        c = classify_source(src)
        self.assertEqual(c['assignments_total'], 5)
        self.assertEqual(c['loop_statements'], 1)
        self.assertEqual(c['conditional_statements'], 1)
        self.assertEqual(c['rhs_index_reads'], 1)
        self.assertEqual(c['self_large_imm'], 1)
        self.assertGreaterEqual(c['float_likely_assignments'], 2)


if __name__ == '__main__':
    unittest.main()
