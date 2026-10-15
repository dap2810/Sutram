"""Targeted guide regressions, not a whole-repository documentation audit."""
from pathlib import Path
import re
import unittest
ROOT=Path(__file__).resolve().parents[2]

class CurrentGuideTests(unittest.TestCase):
    def test_current_windows_guides_do_not_recommend_security_bypass(self):
        for name in ('INSTALL-WINDOWS.md','docs/WINDOWS-SETUP.md'):
            text=(ROOT/name).read_text('utf-8')
            with self.subTest(name=name):
                self.assertNotRegex(text,re.compile(r'-ExecutionPolicy\s+Bypass',re.I))
                self.assertNotIn('Allow it; the compiler',text)
                self.assertIn('INSTALLATION-ROUTES.md',text)

    def test_readme_book_path_and_example_count_are_not_stale(self):
        text=(ROOT/'README.md').read_text('utf-8')
        self.assertNotIn('| `books/` |',text)
        self.assertNotIn('in `books/`',text)
        self.assertIn('docs/sutram-book-*.html',text)
        self.assertNotRegex(text,r'\b178 programs\b')
        self.assertNotIn('`install.sh` installs',text)

    def test_setup_does_not_prescribe_program_files_default(self):
        text=(ROOT/'docs/WINDOWS-SETUP.md').read_text('utf-8')
        self.assertNotIn('default `C:\\Program Files\\Sutram`',text)
        self.assertIn('%LOCALAPPDATA%\\Programs\\Sutram',text)

    def test_archive_review_is_not_presented_as_windows_acceptance(self):
        text=(ROOT/'docs/INSTALLATION-ROUTES.md').read_text('utf-8')
        self.assertIn('no installer was executed',text)
        self.assertIn('remain blockers',text)
        self.assertIn('No Linux installer was produced',text)

    def test_six_exact_book_edition_names_documented(self):
        text=(ROOT/'docs/INSTALLATION-ROUTES.md').read_text('utf-8')
        names=set(re.findall(r'docs/sutram-book-([a-z]+)\.html',text))
        self.assertEqual(names,{'english','hindi','sanskrit','tamil','telugu','gujarati'})
        # Existence was checked against the pinned GitHub docs tree, not by
        # inventing placeholder book files in a partial local checkout.

if __name__=='__main__':unittest.main()
