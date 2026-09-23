"""Exercise document coverage, local links, and strict parsing in isolated files."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from validation_common import ROOT, load_json
from validate_documents import REQUIRED_DOCUMENTS, validate_documents
from validate_language import validate_language


class DocumentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='java-doc-tests-', dir=ROOT.parent)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'repo'
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns('.git', '__pycache__'))

    def rules(self):
        return {e['rule_id'] for e in validate_documents(self.root)}

    def test_valid_repository_documents(self):
        self.assertEqual(validate_documents(self.root), [])

    def test_each_required_document_cannot_be_missing_or_empty(self):
        for relative in REQUIRED_DOCUMENTS:
            with self.subTest(relative=relative):
                path = self.root / relative
                original = path.read_text()
                path.unlink()
                self.assertIn('MISSING_DOCUMENT', self.rules())
                path.write_text(' \n')
                self.assertIn('EMPTY_DOCUMENT', self.rules())
                path.write_text(original)

    def test_nested_relative_links_and_heading_fragments(self):
        path = self.root / '.agents/teaching.md'
        path.write_text(path.read_text() + '\n[Entry](../AGENTS.md#save-protocol)\n')
        self.assertEqual(self.rules(), set())
        path.write_text(path.read_text() + '\n[Missing](../AGENTS.md#wrong-section)\n')
        self.assertIn('BROKEN_ANCHOR', self.rules())

    def test_broken_and_escaping_links(self):
        path = self.root / '.agents/teaching.md'
        original = path.read_text()
        for link in ('missing.json', '../../../outside.md', '%2e%2e/%2e%2e/outside.md'):
            with self.subTest(link=link):
                path.write_text(original + f'\n[Test]({link})\n')
                self.assertIn('BROKEN_LINK', self.rules())

    def test_reference_links_and_code_exclusion(self):
        path = self.root / '.agents/teaching.md'
        path.write_text(path.read_text() + '\n[Entry][main]\n\n[main]: ../AGENTS.md\n'
                        + '\n```md\n[Example](missing.md)\n```\n')
        self.assertEqual(self.rules(), set())
        path.write_text(path.read_text() + '\n[Undefined][unknown]\n')
        self.assertIn('BROKEN_LINK', self.rules())

    def test_markdown_language_coverage_includes_plan_and_instructions(self):
        for relative in REQUIRED_DOCUMENTS:
            with self.subTest(relative=relative):
                path = self.root / relative
                original = path.read_text()
                path.write_text(original + '\nGreat job.\n')
                report = validate_language(self.root)
                self.assertIn(relative, report['checked_files'])
                self.assertTrue(any(e['rule_id'] == 'STYLE-02' and e['file'] == relative for e in report['errors']))
                path.write_text(original)

    def test_polish_readme_skips_prose_but_keeps_link_validation(self):
        path = self.root / 'README.md'
        path.write_text('Great job.\n')
        report = validate_language(self.root)
        self.assertNotIn('README.md', report['checked_files'])
        self.assertIn('README.md', report['prose_exclusions'])
        self.assertFalse(any(e['rule_id'] == 'STYLE-02' and e['file'] == 'README.md' for e in report['errors']))
        path.write_text('[Brak](missing.md)\n')
        self.assertTrue(any(e['rule_id'] == 'BROKEN_LINK' and e['file'] == 'README.md'
                            for e in validate_language(self.root)['errors']))

    def test_language_check_rejects_missing_instructions(self):
        (self.root / '.agents/teaching.md').unlink()
        self.assertFalse(validate_language(self.root)['passed'])

    def test_linked_instruction_is_rejected(self):
        path = self.root / '.agents/teaching.md'
        path.unlink()
        path.symlink_to(self.root / 'AGENTS.md')
        self.assertIn('UNSAFE_FILE', self.rules())

    def test_strict_json_rejects_duplicates_and_non_finite_numbers(self):
        path = self.root / 'invalid.json'
        for content in ('{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}', '{"a":1e999}'):
            with self.subTest(content=content):
                path.write_text(content)
                with self.assertRaises(ValueError):
                    load_json(path)


if __name__ == '__main__':
    unittest.main()
