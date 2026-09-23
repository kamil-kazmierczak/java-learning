"""Check that the plan validator rejects incorrect data."""
import copy
import tempfile
import unittest
from pathlib import Path

from validate_plan import ROOT, PLAN, SCHEMA, load_json, validate_plan, validate_entry_links


class PlanValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = load_json(ROOT / PLAN)
        cls.schema = load_json(ROOT / SCHEMA)

    def test_valid_plan(self):
        self.assertEqual(validate_plan(self.plan, self.schema), [])

    def test_unknown_nested_field(self):
        plan = copy.deepcopy(self.plan)
        plan["learner"]["assumed_skill"] = "expert"
        self.assertTrue(validate_plan(plan, self.schema))

    def test_missing_required_field(self):
        plan = copy.deepcopy(self.plan)
        del plan["language"]["approval_review"]
        self.assertTrue(validate_plan(plan, self.schema))

    def test_invalid_calendar_date(self):
        plan = copy.deepcopy(self.plan)
        plan["date"] = "2026-02-30"
        self.assertTrue(validate_plan(plan, self.schema))

    def test_duplicate_requirement(self):
        plan = copy.deepcopy(self.plan)
        plan["requirements"].append(copy.deepcopy(plan["requirements"][0]))
        errors = validate_plan(plan, self.schema)
        self.assertTrue(any(e["rule_id"] == "DUPLICATE_ID" for e in errors))

    def test_unknown_requirement_reference(self):
        plan = copy.deepcopy(self.plan)
        plan["acceptance_tests"][0]["requirement_ids"].append("UNKNOWN-99")
        errors = validate_plan(plan, self.schema)
        self.assertTrue(any(e["rule_id"] == "UNKNOWN_REQUIREMENT" for e in errors))

    def test_duplicate_key_and_non_json_number(self):
        for content in ('{"a": 1, "a": 2}', '{"a": NaN}'):
            with self.subTest(content=content), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "invalid.json"
                path.write_text(content, encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_json(path)

    def test_broken_entry_link(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "AGENTS.md").write_text("[Missing](missing.json)", encoding="utf-8")
            errors = validate_entry_links(root)
            self.assertTrue(any(e["rule_id"] == "BROKEN_LINK" for e in errors))

    def test_missing_record_schema(self):
        plan = copy.deepcopy(self.plan)
        plan["file_layout"][1]["schema"] = None
        errors = validate_plan(plan, self.schema)
        self.assertTrue(any(e["rule_id"] == "MISSING_SCHEMA" for e in errors))


if __name__ == "__main__":
    unittest.main()
