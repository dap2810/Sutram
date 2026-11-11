#!/usr/bin/env python3
"""R189: run ChatGPT R233's four verification tests as one gate (they were added in R233 but not registered).

Prints one line the gate reads: 'r233 verification: N checks, F failed'.
Usage: python3 tests/r233/run_all.py [--compiler PATH]   (the compiler is passed on as SUTRAM_COMPILER)
"""
import os, sys, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
if '--compiler' in sys.argv:
    os.environ['SUTRAM_COMPILER'] = os.path.abspath(sys.argv[sys.argv.index('--compiler') + 1])
suite = unittest.defaultTestLoader.discover(HERE, pattern='test_*.py', top_level_dir=HERE)
result = unittest.TextTestRunner(stream=sys.stderr, verbosity=1).run(suite)
failed = len(result.failures) + len(result.errors)
for case, _ in result.failures + result.errors:
    print('FAIL  %s' % case.id())
print('r233 verification: %d checks, %d failed' % (result.testsRun, failed))
sys.exit(1 if failed else 0)
