"""Check language findings and the exclusions needed by code exercises."""
import unittest

from validate_language import check_text, prose_fields, validate_language


class LanguageTests(unittest.TestCase):
    terms = [{"term": "JVM", "avoid_forms": ["JVM machine"]}]

    def rules(self, text):
        return {rule for rule, _ in check_text(text, self.terms)}

    def test_report_has_explicit_ste_limit(self):
        report = validate_language()
        self.assertEqual(report["ste_compliance"], "not_verified")
        self.assertEqual(report["manual_review"], "required")

    def test_detect_filler_contraction_alias_and_long_sentence(self):
        self.assertIn("STYLE-01", self.rules(" ".join(["word"] * 26) + "."))
        self.assertIn("STYLE-02", self.rules("Great job. You solved the task."))
        self.assertIn("STYLE-03", self.rules("It isn't complete."))
        self.assertIn("STYLE-03", self.rules("We’re ready."))
        self.assertIn("STYLE-04", self.rules("The JVM machine runs it."))

    def test_sentence_boundary_and_word_boundary(self):
        sentence = " ".join(["word"] * 25) + "."
        self.assertEqual(self.rules(sentence + " " + sentence), set())
        self.assertNotIn("STYLE-04", self.rules("JVM machinery"))

    def test_preserve_code_urls_and_exact_quotes(self):
        text = "Use `JVM machine`.\n```java\nString s = \"Great job\";\n```\n> It isn't complete.\nhttps://example.org/leverage"
        self.assertEqual(self.rules(text), set())

    def test_link_labels_are_checked(self):
        self.assertIn("STYLE-02", self.rules("[Great job](https://example.org)"))

    def test_prose_extraction_keeps_evidence_and_excludes_execution(self):
        fields = dict(prose_fields({
            "observations": [{"observed_result": "The result is zero.", "source": "learner_report"}],
            "execution": {"command": "java Main", "output": "It isn't complete."},
            "sources": [{"title": "Exact title", "url": "https://example.org"}],
            "term": "JVM", "avoid_forms": ["JVM machine"],
        }))
        self.assertEqual(fields, {"/observations/0/observed_result": "The result is zero."})

    def test_prose_prompts_remain_checked(self):
        fields = dict(prose_fields({"tasks": [{"prompt": "Great job."}]}))
        self.assertIn("STYLE-02", self.rules(fields["/tasks/0/prompt"]))


if __name__ == "__main__":
    unittest.main()
